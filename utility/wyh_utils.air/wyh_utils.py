from tempfile import template

from airtest.core.api import *

using("../utility/base")
from adc_api import lx_break_app, BreakMode
from adc_environment import AppEnv
from adc_request import upload_propreties_with_data

using("../utility/monitor.air")
from monitor import monitor_task_status_v2

using("../utility/biz_utils")
from biz_utils import gameId, platform, localRun, snapshot_write, monitor_catch, monitor_print

import os
import time
from PIL import Image, ImageDraw, ImageFont
import cv2
from typing import Any, Dict, List, Tuple, Callable, Union
import numpy as np
from functools import wraps


def template_match_cv2(img, tmp, threshold=0.8):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转灰度图
    result = cv2.matchTemplate(img, tmp, cv2.TM_CCOEFF_NORMED)
    _, max_val, *_ = cv2.minMaxLoc(result)
    return max_val > threshold


def template_match_cv2_v1(img, tmp, threshold=0.8):
    """
    模板匹配函数，自动判断输入图像和模板是否为灰度图，若不是则转为灰度图。

    参数:
        img: 输入图像 (numpy array)
        tmp: 模板图像 (numpy array)
        threshold: 匹配阈值，默认 0.8

    返回:
        bool: 最大匹配值是否超过阈值
    """

    def to_grayscale(image):
        if len(image.shape) == 2:
            # 已是灰度图
            return image
        elif len(image.shape) == 3 and image.shape[2] in [3, 4]:
            # 彩色图（BGR 或 BGRA），转灰度
            if image.shape[2] == 3:
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            raise ValueError(f"不支持的图像格式: shape={image.shape}")

    try:
        gray_img = to_grayscale(img)
        gray_tmp = to_grayscale(tmp)

        # 执行模板匹配
        result = cv2.matchTemplate(gray_img, gray_tmp, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        return max_val > threshold

    except cv2.error as e:
        print(f"OpenCV 错误: {e}")
        return False
    except Exception as e:
        print(f"其他错误: {e}")
        return False


def phase(name, kick_off_temp=None):
    def decorator(func):
        func._phase_name = name

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果提供了 kick_off_temp，则先做踢登检测
            if kick_off_temp is not None:
                if template_match_cv2_v1(snapshot_write(), kick_off_temp):
                    monitor_catch(
                        title=f"{name}",
                        desc="检测到账号被踢登",
                        break_mode="app",
                        status=10010
                    )
                    return None  # 不执行原函数

            # 否则正常执行原函数
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _invoke_handler(handler, phase_name) -> bool:
    """
    统一处理 handler 调用

    Args:
        handler: 处理
        phase_name: phase name

    Returns:
        bool: 是否中断当前phase的执行
    """
    if callable(handler):
        result = handler()
    elif isinstance(handler, tuple):
        # handler 是 (title, desc, break_mode, status, ...) 的形式
        monitor_catch(*handler)
        return True
    elif isinstance(handler, dict):
        monitor_catch(**handler)
        return True
    else:
        # 默认 fallback
        monitor_catch(
            title=phase_name,
            desc="检测到异常状态",
            break_mode="app",
            status=120007
        )
        return False

    return result is True


def phase_v1(
        name: str,
        pre_check_temps: List[Tuple[Any, Union[Callable, tuple, dict]]] = None,
        post_check_temps: List[Tuple[Any, Union[Callable, tuple, dict]]] = None
    ):
    """
    通用阶段装饰器，支持执行前/后模板检测

    Args:
        name: 阶段名称
        pre_check_temps: 执行前检测的模板列表 [(template, handler), ...]
        post_check_temps: 执行后检测的模板列表 [(template, handler), ...]
            handler 可以是：
                - callable：直接调用
                - tuple：作为 monitor_catch(*handler) 的参数
                - dict：作为 monitor_catch(**handler) 的参数
    """
    pre_check_temps = pre_check_temps or []
    post_check_temps = post_check_temps or []

    def decorator(func):
        func._phase_name = name

        @wraps(func)
        def wrapper(*args, **kwargs):
            # === 执行前检测 ===
            if pre_check_temps:
                screenshot = snapshot_write()
                for temp, handler in pre_check_temps:
                    if template_match_cv2_v1(screenshot, temp):
                        _invoke_handler(handler, name)
                        return None  # 中断执行

            # === 执行phase ===
            func(*args, **kwargs)

            # === 执行后检测 ===
            if post_check_temps:
                screenshot = snapshot_write()
                for temp, handler in post_check_temps:
                    if template_match_cv2_v1(screenshot, temp):
                        _invoke_handler(handler, name)
                        return None
            return None
        return wrapper
    return decorator


def properties_format(option_map: dict):
    option_list = []
    if option_map:
        for key, value in option_map.items():
            for item in value:
                option_list.append({
                    "propertyName": key,
                    "propertyValueName": item
                })
    return option_list


def create_blank_with_text_opencv(text: str="Not Equipped", width: int=700, height: int=650, bg_color: tuple=(80, 80, 80), font_scale=2):
    """
    使用 OpenCV 创建带英文文本的空白图像
    :param text: 要显示的文本
    :param width: 图像宽度
    :param height: 图像高度
    :param bg_color: 背景颜色 (BGR)
    :param font_scale: 字体缩放比例
    :return: OpenCV 图像 (numpy array)
    """
    # 创建空白图像
    img = np.full((height, width, 3), bg_color, dtype=np.uint8)

    # 设置字体
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 3

    # 获取文本大小，用于居中
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    # 计算居中位置
    x = (width - text_width) // 2
    y = (height + text_height) // 2  # y 是基线位置

    # 绘制文字（白色）
    cv2.putText(img, text, (x, y), font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)

    return img


def combine_template(
    template_img: str,
    text_pos_map: dict,
    img_list: list,
    output_name: str,
    template_img_region: tuple,
    font_name: str = "AlibabaPuHuiTi-3-85-Bold.ttf",
    font_size: int = 45,
    font_color: str = "white",
    spacing: int = 30,
    max_height_ratio: float = 0.95,
    align: str = "left",  # 'left', 'center', 'right'
) -> None:
    """
    通用模板图像合成函数：支持左/中/右对齐，内存操作，无需临时文件。

    :param template_img: 模板图片路径
    :param text_pos_map: {"文本": (x, y)}
    :param img_list: OpenCV 图像列表 (np.ndarray)
    :param output_name: 输出文件名前缀
    :param template_img_region: (x1, y1, x2, y2) 贴图区域
    :param font_name: 字体文件名（需与本文件同目录）
    :param font_size: 字体大小
    :param font_color: 字体颜色
    :param spacing: 垂直间距
    :param max_height_ratio: 可用高度比例
    :param align: 对齐方式 'left', 'center', 'right'
    """

    log_dir = ST.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)

    # === 1. 加载模板 ===
    if not os.path.exists(template_img):
        raise FileNotFoundError(f"模板图片不存在: {template_img}")

    try:
        template = Image.open(template_img).convert('RGBA')
    except Exception as e:
        raise IOError(f"无法打开模板图片: {e}")

    draw = ImageDraw.Draw(template)

    # === 2. 加载字体 ===
    try:
        current_dir = os.path.dirname(__file__)
        font_path = os.path.join(current_dir, font_name)
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"⚠️ 字体加载失败 ({font_name}): {e}，使用默认字体")
        font = ImageFont.load_default()

    # === 3. 绘制文字 ===
    for text, pos in text_pos_map.items():
        display_text = text.split("_")[0]
        print(f"📝 写入文字: '{display_text}' at {pos}")
        try:
            draw.text(pos, str(display_text), font=font, fill=font_color)
        except Exception as e:
            print(f"❌ 文字绘制失败: {e}")

    # === 4. 空图跳过 ===
    if not img_list:
        print("🟡 img_list 为空，仅保存文字结果")
        final_rgb = template.convert('RGB')
        timestamp = int(time.time() * 1000)
        output_path = os.path.join(log_dir, f"{output_name}_{timestamp}.jpg")
        final_rgb.save(output_path, "JPEG", quality=95)
        monitor_task_status_v2("提示", f"模版拼图完成：{output_name}")
        return

    # === 5. 区域计算 ===
    x1, y1, x2, y2 = template_img_region
    region_width = x2 - x1
    available_total_height = int((y2 - y1) * max_height_ratio)

    # === 6. 单图处理 ===
    if len(img_list) == 1:
        img = img_list[0]
        h, w = img.shape[:2]
        scale = min((region_width - 2 * spacing) / w, available_total_height / h)
        new_w, new_h = int(w * scale), int(h * scale)

        pil_img = cv2_to_pil(img).resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 计算水平位置
        if align == "left":
            paste_x = x1 + spacing
        elif align == "center":
            paste_x = x1 + (region_width - new_w) // 2
        elif align == "right":
            paste_x = x2 - new_w - spacing
        else:
            paste_x = x1 + (region_width - new_w) // 2  # 默认居中

        paste_y = y1 + (available_total_height - new_h) // 2

        if y1 <= paste_y < y2 and paste_y + new_h <= y2:
            template.paste(pil_img, (paste_x, paste_y), mask=pil_img if pil_img.mode == 'RGBA' else None)
        else:
            print("⚠️ 单图越界，跳过")

    # === 7. 多图垂直排列 ===
    else:
        n = len(img_list)
        total_spacing_height = (n - 1) * spacing
        individual_height = (available_total_height - total_spacing_height) // n

        current_y = y1
        for i, img in enumerate(img_list):
            h, w = img.shape[:2]
            scale = individual_height / h
            new_w = int(w * scale)
            new_h = individual_height

            # 宽度超限则压缩
            if new_w > region_width - 2 * spacing:
                scale = (region_width - 2 * spacing) / new_w
                new_w = int(new_w * scale)
                new_h = int(new_h * scale)

            pil_img = cv2_to_pil(img).resize((new_w, new_h), Image.Resampling.LANCZOS)

            # 水平对齐策略
            if align == "left":
                paste_x = x1 + spacing
            elif align == "center":
                paste_x = x1 + (region_width - new_w) // 2
            elif align == "right":
                paste_x = x2 - new_w - spacing
            else:
                paste_x = x1 + (region_width - new_w) // 2

            paste_y = current_y

            if paste_y + new_h <= y2:
                template.paste(pil_img, (paste_x, paste_y), mask=pil_img if pil_img.mode == 'RGBA' else None)
                print(f"✅ 图 {i} 贴在 ({paste_x}, {paste_y}), 尺寸: {new_w}x{new_h} ({align}对齐)")
            else:
                print(f"⚠️ 图 {i} 超出区域，跳过")

            current_y = paste_y + new_h + spacing  # 更新 Y

    # === 8. 保存===
    try:
        # 直接转 RGB 并保存
        final_img = template.convert('RGB')
        timestamp = int(time.time() * 1000)
        output_path = os.path.join(log_dir, f"{output_name}_{timestamp}.jpg")
        final_img.save(output_path, "JPEG", quality=95)
        print(f"✅ 合成完成: {output_path}")
        monitor_task_status_v2("提示", f"模版拼图完成：{output_name}")
    except Exception as e:
        print(f"❌ 图像保存失败: {e}")


def draw_chinese_text(
    image: np.ndarray,
    text: str,
    position: tuple,
    font_name: str = "AlibabaPuHuiTi-3-85-Bold.ttf",
    font_size: int = 40,
    color: tuple = (255, 255, 255),  # RGB 白色
    background_color: tuple = None   # 可选背景填充 (R,G,B)
) -> np.ndarray:
    """
    在 OpenCV 图像上绘制一行中文文本。

    :param image: 输入图像 (HxWxC, BGR, dtype=uint8)
    :param text: 要绘制的文本（支持中文）
    :param position: 文本左上角坐标 (x, y)
    :param font_name: 字体文件名（需与该 .py 文件同目录）
    :param font_size: 字体大小
    :param color: 字体颜色，RGB 元组，如 (255, 255, 255)
    :param background_color: 可选背景矩形颜色（用于增强可读性），RGB 元组

    :return: 绘制后的 OpenCV 图像 (BGR)
    """
    # 转为 PIL
    pil_image = cv2_to_pil(image)
    draw = ImageDraw.Draw(pil_image)

    # 加载字体
    try:
        current_dir = os.path.dirname(__file__)
        font_path = os.path.join(current_dir, font_name)
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"⚠️ 字体加载失败 ({font_name}): {e}，使用默认字体")
        font = ImageFont.load_default()

    x, y = position

    # 获取文本边界框
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        # 兼容旧版本 PIL
        text_w, text_h = draw.textsize(text, font=font)
        bbox = [0, 0, text_w, text_h]

    # 绘制背景（如果指定）
    if background_color is not None:
        bg_rect = [
            x + bbox[0], y + bbox[1],
            x + bbox[2], y + bbox[3]
        ]
        draw.rectangle(bg_rect, fill=background_color)

    # 绘制文字
    draw.text((x, y), text, font=font, fill=color)

    # 转回 OpenCV 格式
    return pil_to_cv(pil_image)


def generate_product_code_image(
    product_code: str,
    font_name: str = "AlibabaPuHuiTi-3-85-Bold.ttf",
    font_size: int = 40,
    text_color: tuple = (255, 255, 255),
    bg_color: tuple = (0, 0, 0),
    border_color: tuple = (255, 255, 255),
    padding: int = 5,
    corner_radius: int = 12
) -> np.ndarray:
    from PIL import Image, ImageDraw, ImageFont
    import os
    import numpy as np

    text = f"商品码 {product_code}"

    # === 1. 加载字体 ===
    try:
        current_dir = os.path.dirname(__file__)
        font_path = os.path.join(current_dir, font_name)
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"⚠️ 字体加载失败: {e}，使用默认字体")
        font = ImageFont.load_default()

    # === 2. 获取精确文本边界框 ===
    temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    try:
        # left, top, right, bottom = bbox
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_left, text_top, text_right, text_bottom = bbox
        text_w = text_right - text_left
        text_h = text_bottom - text_top
    except AttributeError:
        # 旧版 PIL 兼容（不推荐，精度差）
        text_w, text_h = temp_draw.textsize(text, font=font)
        text_left, text_top, text_right, text_bottom = 0, 0, text_w, text_h

    # === 3. 计算图像尺寸（严格四边 padding）===
    img_w = text_w + 2 * padding
    img_h = text_h + 2 * padding

    # 防止圆角过大
    corner_radius = min(corner_radius, min(img_w, img_h) // 2 - 1)

    # === 4. 创建图像并绘制背景和边框 ===
    pil_img = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pil_img)

    # 黑色背景
    draw.rounded_rectangle(
        [(0, 0), (img_w, img_h)],
        radius=corner_radius,
        fill=bg_color + (255,)
    )

    # 白色边框
    try:
        draw.rounded_rectangle(
            [(0, 0), (img_w, img_h)],
            radius=corner_radius,
            outline=border_color,
            width=2
        )
    except TypeError:
        # 旧版 Pillow 回退
        draw.rectangle([0, 0, img_w-1, img_h-1], outline=border_color, width=2)

    # === 5. 关键：计算文字绘制的正确起始点 ===
    # 我们希望：文字的 bbox 左上角 = (padding, padding)
    # 但 draw.text() 的坐标是 baseline，所以我们需要补偿 text_top
    # 实际绘制 x = padding - text_left
    # 实际绘制 y = padding - text_top
    text_draw_x = padding - text_left
    text_draw_y = padding - text_top

    draw.text((text_draw_x, text_draw_y), text, font=font, fill=text_color + (255,))

    # === 6. 转 OpenCV 格式 ===
    rgb_img = pil_img.convert('RGB')
    opencv_img = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)

    return opencv_img


def cv2_to_pil(cv_img: 'cv2.Mat') -> Image.Image:  # type: ignore
    """
    将 OpenCV (numpy.ndarray) 图像转换为 PIL.Image，支持 BGR/RGB/BGRA/RGBA。

    :param cv_img: OpenCV 格式的图像（numpy array）
    :return: 转换后的 PIL.Image 对象（RGBA 模式）
    """
    if cv_img.dtype != 'uint8':
        cv_img = cv_img.astype('uint8')

    if len(cv_img.shape) == 3:
        channels = cv_img.shape[2]
        if channels == 3:
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        elif channels == 4:
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)

    return Image.fromarray(cv_img).convert('RGBA')


def pil_to_cv(pil_img: Image.Image) -> np.ndarray:
    """
    将 PIL.Image 转换回 OpenCV 格式（BGR）
    """
    cv_img = np.array(pil_img.convert('RGB'))  # 去除 alpha
    return cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)


def map_property_value_to_ext(game_properties: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    将 gameProperties 列表转换为以 propertyValue 为键、propertyExt 为值的映射字典。

    :param game_properties: 包含 propertyValue 和 propertyExt 的属性项列表
    :return: 映射字典，格式为 {propertyValue: propertyExt}
    """
    return {
        item["propertyValue"]: item["propertyExt"]
        for item in game_properties
        if "propertyValue" in item and "propertyExt" in item
    }


def build_single_property_result(item: Dict[str, Any], data: Dict[str, Any], key: str) -> Dict[str, Any]:
    """
    构建单值属性的结果结构。

    :param item: 当前属性配置项，包含 propertyName、propertyId 等元信息
    :param data: 用户游戏数据字典
    :param key: 在 data 中对应的字段名
    :return: 格式化结果，包含 propertyName、propertyId 和 value
    """
    return {
        "propertyName": item["propertyName"],
        "propertyId": item["propertyId"],
        "value": data.get(key),
        "useGameProperty": item["useGameProperty"],
    }


def build_multi_property_result(item: Dict[str, Any], data: Dict[str, Any], key: str, feedback: bool=False) -> Dict[str, Any]:
    """
    构建多值嵌套属性的结果结构。

    :param item: 当前属性配置项，包含嵌套的 gameProperties
    :param data: 用户游戏数据字典
    :param key: 在 data 中对应的列表字段名
    :param feedback: 缺失属性是否进行属性回传
    :return: 包含 propertyName、propertyId 和 gameProperties 列表的结果
    """
    results = {
        "propertyName": item["propertyName"],
        "propertyId": item["propertyId"],
        "gameProperties": [],
        "useGameProperty": item["useGameProperty"]
    }

    # 提取 propertyValue -> propertyExt 映射
    prop_map = map_property_value_to_ext(item.get("gameProperties", []))

    name_list = data.get(key, [])
    for name in name_list:
        if isinstance(name, str):
            if name in prop_map:
                results["gameProperties"].append({
                    "propertyExt": prop_map[name],
                    "value": name
                })
            else:
                # 属性回填
                if feedback and not localRun:
                    option_map = properties_format({
                        results["propertyName"]: [name]
                    })
                    monitor_task_status_v2(title="属性回填", desc=f"回填属性{option_map}")
                    try:
                        upload_propreties_with_data(
                            game_id=gameId,
                            game_platform=platform,
                            data=option_map,
                            images=[],
                            addParams=True,
                            isFromCollectTask=True,
                            isNeedShenpi=True,
                            taskIdList=[AppEnv.get_instance().taskId]
                        )
                    except Exception as e:
                        monitor_task_status_v2(title="属性回填", desc=f"回填属性失败: {e}")
        elif not isinstance(name, str):
            monitor_print(f"⚠️ 多值属性 '{key}' 中包含非字符串项: {name}")

    return results


# 类型别名：处理器元组 (处理函数, 数据键名)
PropertyHandler = Tuple[Callable[[Dict[str, Any], Dict[str, Any], str], Dict[str, Any]], str]


def process_game_property_list(
    properties: List[Dict[str, Any]],
    game_data: Dict[str, Any],
    handlers: Dict[str, PropertyHandler]
) -> List[Dict[str, Any]]:
    """
    统一处理游戏属性列表，根据预定义处理器生成标准化输出。

    :param properties: 属性库
    :param game_data: 采集的游戏数据
    :param handlers: 处理器映射表，格式：
                     { propertyName: (handler_func, data_key) }
    :return: 处理后的属性结果列表
    """
    result_list: List[Dict[str, Any]] = []

    for item in properties:
        prop_name = item.get("propertyName")
        if not prop_name:
            monitor_print("属性项缺少 'propertyName' 字段")
            continue

        handler_pair = handlers.get(prop_name)
        if handler_pair is not None:
            handler_func, data_key, *feedback = handler_pair
            try:
                if feedback:
                    result = handler_func(item, game_data, data_key, feedback[0])
                else:
                    result = handler_func(item, game_data, data_key)
                result_list.append(result)
            except Exception as e:
                monitor_print(f"处理属性 '{prop_name}' 时出错: {e}")
                lx_break_app(ext_info="未知错误", e=e)
        else:
            monitor_print(f"未知属性类型，跳过: {prop_name}")

    return result_list