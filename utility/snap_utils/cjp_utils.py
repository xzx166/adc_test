
import cv2
import os
import numpy as np
from PIL import Image
# from utility.biz_utils.biz_utils import *
# from .biz_utils import *
# from biz_utils import *

from utility.biz_utils.biz_utils import monitor_print, monitor_task_status_v2, lx_break_runloop
from airtest.core.api import Template,ST, using
from utility.base.adc_environment import AppEnv
from utility.app.service.adc_ocr import ocr_image_by_eas


import time


using("utility/dwarf.air")
from dwarf import lx_snapshot, upload_current_catch

#正规马赛克打码操作
def apply_mosaic(image_path, x1, y1, x2, y2, block_size=15):
    """
    对指定区域加马赛克（正宗方块像素化）
    :param image_path: 图片路径
    :param x1, y1: 区域左上角坐标
    :param x2, y2: 区域右下角坐标
    :param block_size: 方块大小（越大越粗糙）
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")

    # 自动修正坐标（防止传反）
    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])

    # 确保坐标在图片范围内
    h_img, w_img = img.shape[:2]
    x1 = max(0, min(x1, w_img))
    x2 = max(0, min(x2, w_img))
    y1 = max(0, min(y1, h_img))
    y2 = max(0, min(y2, h_img))

    # 宽高
    w = x2 - x1
    h = y2 - y1

    if w == 0 or h == 0:
        raise ValueError("选区宽高不能为0")
    # 取 ROI 区域
    roi = img[y1:y2, x1:x2]
    # 缩小
    roi_small = cv2.resize(roi, (max(1, w // block_size), max(1, h // block_size)),
                           interpolation=cv2.INTER_LINEAR)
    # 放大回原始
    roi_mosaic = cv2.resize(roi_small, (w, h), interpolation=cv2.INTER_NEAREST)
    # 放回原图
    img[y1:y2, x1:x2] = roi_mosaic

    # 保存
    cv2.imwrite(image_path, img)
    monitor_print(f"-----马赛克已完成，保存到: {image_path}")

# ssim结构相似度指数
def compare_ssim_func(img1_path, img2_path, threshold = 0.9):
    from skimage.metrics import structural_similarity as compare_ssim
    # 确保图片已经正确读取
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    # gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    # gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # 计算SSIM
    score_color = compare_ssim(img1, img2, channel_axis=2)
    monitor_print(f"-----RGB图像的ssim为: {score_color}")
    if score_color > threshold:
        return True
    else:
        return False




def dwarf_get_hsv(img):
    """
    获取图片主色的hsv
    HSV颜色模型‌由三个参数组成：色相（Hue, H）、饱和度（Saturation, S）和亮度（Value, V）。
    ‌饱和度（S）‌：表示颜色的纯度，取值范围为0.0到1.0。饱和度越高，颜色越鲜艳；饱和度越低，颜色越黯淡‌12。
    ‌亮度（V）‌：表示颜色的明亮程度，取值范围为0.0（黑色）到1.0（白色）。亮度越高，颜色越亮；亮度越低，颜色越暗‌
    """
    import colorsys
    from colorthief import ColorThief
    # 加载图片
    # image = None
    img_path = None
    if isinstance(img, str):
        img_path = img
    elif isinstance(img, np.ndarray):
        img_path = os.path.join(ST.LOG_DIR, "temp.jpg")
        cv2.imwrite(img_path, img)
    elif isinstance(img, Image.Image):
        img_path = os.path.join(ST.LOG_DIR, "temp.jpg")
        img.save(img_path)
    color_thief = ColorThief(img_path)
    # 获取主颜色
    dominant_color = color_thief.get_color(quality=1)
    # 获取调色板
    palette = color_thief.get_palette(color_count=6)
    # 将 RGB 从 0-255 范围转换到 0-1 范围
    r, g, b = [x / 255.0 for x in dominant_color]
    # 使用 colorsys 转换 RGB 到 HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    monitor_print(f"dwarf_get_hsv: h: {h} s: {s} v: {v}")
    return h, s, v



def hue_map(h):
    # 定义区间和名称
    COLOR_RANGES = [
        ((0, 10), "红色"),
        ((11, 23), "橙色"),
        ((24, 34), "黄色"),
        ((35, 77), "绿色"),
        ((78, 99), "青色"),
        ((100, 124), "蓝色"),
        ((125, 155), "紫色"),
        ((156, 180), "红色")
    ]
    for (low, high), name in COLOR_RANGES:
        if low <= h <= high:
            return name
    return "未知"


def ocr_return_text_write(ocr_region, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}):
    """
    ocr返回文字
    :param ocr_region:
    :param remote_ocr_type:
    :return:
    """
    timtStamp = str(int(time.time() * 10 ** 6))
    img_path = lx_snapshot(AppEnv.get_instance(), f"adc_catch_ocr_temp_{timtStamp}", crop_pos=ocr_region, path=True)
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            ocr_res = [item["txts"] for item in res]
            if ocr_res:
                if ocr_res[0] in fault_tolerant_map:
                    return fault_tolerant_map[ocr_res[0]]
                return ocr_res[0]
    return None

def ocr_return_text_all_write(ocr_region, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}):
    """
    ocr返回文字
    :param ocr_region:
    :param remote_ocr_type:
    :return:
    """
    timtStamp = str(int(time.time() * 10 ** 6))
    img_path = lx_snapshot(AppEnv.get_instance(), f"adc_catch_ocr_temp_{timtStamp}", crop_pos=ocr_region, path=True)
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            ocr_res = [item["txts"] for item in res]
            if ocr_res:
                return "".join(ocr_res)
    return None



def retry_phase(phase_name, max_try=2, before_retry_func=None, go_home = None, out_loop_func=None, is_pass=False):
    """
    此装饰器作用是异常后重启游戏，重试phase
    :param phase_name:
    :param max_try: 重试次数，默认2次, 第一次失败后重启游戏再试一次
    :param before_retry_func: 重试phase前需要做的操作, 清理全局变量，清理图片，重启游戏，进入phase执行前的页面
    :param out_loop_func: 重试phase后需要做的操作
    :param is_pass: 是否跳过
    :return:
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            phase_error_snapshot_list = []
            for current_loop in range(max_try):
                try:
                    if current_loop != 0:
                        if before_retry_func:
                            before_retry_func()
                    if go_home:
                        if go_home():
                            func(*args, **kwargs)
                        else:
                            before_retry_func()
                            func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)
                    if out_loop_func:
                        out_loop_func(phase_error_snapshot_list)
                except Exception as e:
                    monitor_task_status_v2(phase_name, f"单流程重试: {current_loop},错误:{e}")
                    upload_current_catch(f'{phase_name}重试')
                    phase_error_snapshot_list.append(lx_snapshot(AppEnv.get_instance(), "break_app", path=True))
                    continue
                else:
                    break
            else:
                # if out_loop_func:
                #     phase_error_snapshot_list.reverse()
                #     out_loop_func(phase_error_snapshot_list)
                # else:
                # 两次都失败，任务直接失败
                if is_pass:
                    monitor_task_status_v2(phase_name, f"{phase_name}内部重试{max_try}次失败,跳过")
                else:
                    lx_break_runloop(f"{phase_name}内部重试{max_try}次失败")
            monitor_task_status_v2(phase_name + "执行耗时", f"{time.strftime('%M:%S', time.gmtime(time.time()-start_time))}")
        return wrapper
    return decorator


# # 点击回调函数
# def pick_color(event, x, y, flags, param):
#     # 识别鼠标左键按下
#     if event == cv2.EVENT_LBUTTONDOWN:
#         bgr_color = img[y, x]
#         hsv_color = cv2.cvtColor(bgr_color.reshape(1, 1, 3), cv2.COLOR_BGR2HSV)
#         h, s, v = hsv_color[0][0]
#         print(f"坐标: ({x}, {y})")
#         print(f"BGR: {tuple(int(c) for c in bgr_color)}")
#         print(f"HSV: (H={h}, S={s}, V={v})")
#         result = hue_map(h)
#         print(f"结果: {result}")

# # 读取图片
# img_path = "./image.png"  # 这里换成你的图片路径
# img = cv2.imread(img_path)

# # 显示窗口
# cv2.namedWindow("Image")
# cv2.setMouseCallback("Image", pick_color)

# while True:
#     cv2.imshow("Image", img)
#     if cv2.waitKey(1) & 0xFF == 27:  # 按 ESC 退出
#         break

# cv2.destroyAllWindows()