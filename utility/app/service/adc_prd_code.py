from airtest.core.api import *

import os
import cv2
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

using("../utility/base")
from utility.base.adc_monitor import monitor_task_status_v2, monitor_print
from typing import Optional


def create_banner_image(
        product_code: str,
        banner_width: int,
        font_size: int = 36
) -> Optional[np.ndarray]:
    """
    创建横幅图像（黑色背景 + 白色文字）
    - 商品码使用粗体
    - 其他文字使用细体

    :param product_code: 商品码
    :param banner_width: 横幅宽度（与原图相同）
    :param font_size: 字体大小
    :return: 横幅图像 (BGR)
    """
    # 获取当前脚本目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 构建字体路径
    bold_font_path = os.path.normpath(
        os.path.join(current_dir, "..", "..", "wyh_utils.air", "Alibaba-PuHuiTi-Bold.otf")
    )
    light_font_path = os.path.normpath(
        os.path.join(current_dir, "..", "..", "wyh_utils.air", "Alibaba-PuHuiTi-Light.otf")
    )

    # 检查文件是否存在
    if not os.path.exists(bold_font_path):
        monitor_print(f"粗体字体文件不存在: {bold_font_path}")
        return None
    if not os.path.exists(light_font_path):
        monitor_print(f"细体字体文件不存在: {light_font_path}")
        return None

    # 加载粗体字体（商品码）
    try:
        bold_font = ImageFont.truetype(bold_font_path, font_size)
    except Exception as e:
        monitor_print(f"粗体字体加载失败: {e}")
        return None

    # 加载细体字体（其他文字）
    try:
        light_font = ImageFont.truetype(light_font_path, font_size)
    except Exception as e:
        monitor_print(f"细体字体加载失败: {e}")
        return None

    # 三段文本
    prefix = "上交易猫搜 "
    code = product_code
    suffix = "找到本商品"

    # 计算各段文本尺寸
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    try:
        # 使用 textbbox 计算精确尺寸
        prefix_bbox = temp_draw.textbbox((0, 0), prefix, font=light_font)
        code_bbox = temp_draw.textbbox((0, 0), code, font=bold_font)
        suffix_bbox = temp_draw.textbbox((0, 0), suffix, font=light_font)

        prefix_w = prefix_bbox[2] - prefix_bbox[0]
        code_w = code_bbox[2] - code_bbox[0]
        suffix_w = suffix_bbox[2] - suffix_bbox[0]

        # 取最大高度（确保对齐）
        prefix_h = prefix_bbox[3] - prefix_bbox[1]
        code_h = code_bbox[3] - code_bbox[1]
        suffix_h = suffix_bbox[3] - suffix_bbox[1]
        text_h = max(prefix_h, code_h, suffix_h)

    except AttributeError:
        # 兼容旧版本 PIL
        prefix_w, prefix_h = temp_draw.textsize(prefix, font=light_font)
        code_w, code_h = temp_draw.textsize(code, font=bold_font)
        suffix_w, suffix_h = temp_draw.textsize(suffix, font=light_font)
        text_h = max(prefix_h, code_h, suffix_h)

    total_text_w = prefix_w + code_w + suffix_w

    # 设置横幅高度（文本高度 + 上下内边距）
    padding_vertical = 20
    banner_height = text_h + 2 * padding_vertical

    # 如果文本太宽，需要调整字体大小
    if total_text_w > banner_width - 40:  # 保留左右20px边距
        scale_factor = (banner_width - 40) / total_text_w
        new_font_size = max(16, int(font_size * scale_factor))

        # 重新加载调整后的字体
        try:
            bold_font = ImageFont.truetype(bold_font_path, new_font_size)
            light_font = ImageFont.truetype(light_font_path, new_font_size)

            # 重新计算尺寸
            prefix_bbox = temp_draw.textbbox((0, 0), prefix, font=light_font)
            code_bbox = temp_draw.textbbox((0, 0), code, font=bold_font)
            suffix_bbox = temp_draw.textbbox((0, 0), suffix, font=light_font)

            prefix_w = prefix_bbox[2] - prefix_bbox[0]
            code_w = code_bbox[2] - code_bbox[0]
            suffix_w = suffix_bbox[2] - suffix_bbox[0]
            total_text_w = prefix_w + code_w + suffix_w

        except Exception as e:
            print(f"调整字体大小时出错: {e}")
            # 继续使用原始字体大小

    # 创建黑色背景的横幅图像
    banner_pil = Image.new('RGB', (banner_width, banner_height), (0, 0, 0))
    draw = ImageDraw.Draw(banner_pil)

    # 计算起始位置（整体居中）
    start_x = (banner_width - total_text_w) // 2
    y_pos = padding_vertical

    # 分别绘制三段文字
    # 前缀（细体）
    draw.text((start_x, y_pos), prefix, font=light_font, fill=(255, 255, 255))
    # 商品码（粗体）
    draw.text((start_x + prefix_w, y_pos), code, font=bold_font, fill=(255, 255, 255))
    # 后缀（细体）
    draw.text((start_x + prefix_w + code_w, y_pos), suffix, font=light_font, fill=(255, 255, 255))

    # 转换为 OpenCV BGR 格式
    banner_cv = cv2.cvtColor(np.array(banner_pil), cv2.COLOR_RGB2BGR)
    return banner_cv


def add_banner_to_image(image: np.ndarray, product_code: str = None) -> np.ndarray:
    """
    在图片下方添加横幅

    :param image: 原始图像
    :param product_code: 商品码
    :return: 添加横幅后的图像
    """
    if image is None or image.size == 0:
        return image

    h, w = image.shape[:2]

    banner = create_banner_image(product_code, w, font_size=36)
    if banner is None:
        monitor_task_status_v2("商品码合图", "创建横幅水印失败")
        return image
    banner_h = banner.shape[0]

    # 创建新的输出图像（原图高度 + 横幅高度）
    output_height = h + banner_h
    output = np.zeros((output_height, w, 3), dtype=np.uint8)

    # 复制原图到顶部
    output[:h, :, :] = image

    # 复制横幅到底部
    output[h:h + banner_h, :, :] = banner

    return output


def phase_composite_image(env):
    """
    批量处理指定目录中的图片，添加横幅
    """
    try:
        #. 无尽冬日、部落冲突需要增加商品码，其他游戏默认首图不增加商品码
        _filter_game_list = [
            "23047",
            "2582"
        ]
        input_dir = env.logPath
        account_attr = json.loads(env.account_attr or "{}")
        product_code = account_attr.get("ITEM_SHARE_CODE", "")
        if not product_code:
            monitor_task_status_v2("商品码合图", "获取商品码失败")
            return
        else:
            monitor_task_status_v2("商品码合图", f"获取商品码 {product_code}")

        # 支持的图片格式
        supported_extensions = ('.jpg')

        # 获取所有包含 "adc_result" 的图片文件
        image_files = []
        for filename in os.listdir(input_dir):

            if filename.lower().endswith(supported_extensions) and "adc_result" in filename.lower():
                image_files.append(filename)

        if not image_files:
            monitor_print(f"在目录 '{input_dir}' 中未找到包含 'adc_result' 的图片文件")
            return
        try:
            image_files = sorted(image_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        except Exception as e:
            pass
        # 处理每张图片
        game_id = env.game_id or env.internal_common_properties.get("game_id", "")
        if game_id not in _filter_game_list:
            monitor_task_status_v2("商品码合图",
                                   f"游戏{game_id}不在列表内：{_filter_game_list},首图跳过，不需要合并商品码")
            if len(image_files) > 0:
                image_files.pop(0)
        processed_count = 0
        for index, filename in enumerate(image_files):
            input_path = os.path.join(input_dir, filename)
            output_filename = f"{filename}"
            output_path = os.path.join(input_dir, output_filename)

            try:
                # 读取原图
                image = cv2.imread(input_path)
                if image is None:
                    monitor_task_status_v2("商品码合图", f"无法读取图片 {filename}")
                    continue

                # 添加横幅
                monitor_print(f"正在处理 {filename}")
                image_with_banner = add_banner_to_image(image, product_code)

                # 检查是否处理成功
                if image_with_banner.shape[0] <= image.shape[0]:  # 高度没增加，说明失败
                    monitor_print(f"跳过 {filename}（横幅创建失败）")
                    continue

                # 保存结果
                success = cv2.imwrite(output_path, image_with_banner)
                if success:
                    monitor_print(f"{filename} 处理完成")
                    processed_count += 1
                else:
                    monitor_print(f"保存失败: {output_filename}")

            except Exception as e:
                monitor_task_status_v2("商品码合图", f"处理 {filename} 时出错， {e}")

        monitor_task_status_v2("商品码合图", f"处理完成, 成功处理 {processed_count}/{len(image_files)} 张图片")
    except Exception as e:
        monitor_task_status_v2("商品码合图", f"处理失败, 异常: {e}")

if __name__ == "__main__":
    class ENV:
        logPath = ""
        account_attr = ""
    env = ENV()
    env.logPath = "/Users/wuchimedes/androidLogResult/"
    env.account_attr = "{\"ITEM_SHARE_CODE\": \"JYM345267365\"}"
    phase_composite_image(env)
