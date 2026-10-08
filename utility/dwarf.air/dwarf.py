import difflib
import json
import os
import random
import time
import urllib
from io import BytesIO

import cv2
import requests
import numpy as np
import logging
from airtest.core.api import *
from PIL import Image, ImageDraw, ImageFont, ImageStat

#####################导入项目依赖START#####################
from poco.utils.track import MotionTrack

using("../utility/api.air")
from api import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/monitor.air")
from monitor import *

using("../utility/upload.air")
from upload import *

using("../utility/ocr.air")
from ocr import *

using("../utility/mask.air")
from mask import *

using("../utility/image.air")
from image import *

using("../utility/upload.air")
from upload import *

using("../utility/swipe.air")
from swipe import *

using("../utility/phase.air")
from phase import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/dwarf.air")
from custom_airtest_api import *


#####################导入项目依赖END#####################
def lx_snapshot(env, name, mask_pos=[], crop_pos=(), path=False, rectangle_pos=(), save_return_img=False, quality=None):
    """
    截图+打码+剪切
    :param env
    :param name: 图片名 eg: adc_result_gerenxinxi
    :param mask_pos: [(x1, y1, x2, y2)]
    :param crop_pos: (x1, y1, x2, y2)
    :return:
    """
    name = name + "_" + str(int(time.time() * 1000000)) + '.jpg'
    snapshot(filename=name, msg="get a snapshot.", quality=quality)
    image_path = env.logPath + '/' + name
    for pos in mask_pos:
        mask_image_range_tosave(image_path, (pos[0], pos[1]), (pos[2], pos[3]))
    image_path = env.logPath + '/' + name
    image = cv2.imread(image_path)
    if crop_pos:
        image = image[crop_pos[1]: crop_pos[3], crop_pos[0]: crop_pos[2]]
    if rectangle_pos:
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        draw.rectangle(rectangle_pos, fill=None,
                       outline='red', width=5)
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        cv2.imwrite(image_path, image)
    if path:
        cv2.imwrite(image_path, image)
        return image_path
    if save_return_img:
        cv2.imwrite(image_path, image)
        return image
    return image

def ocr_keyword_return_pos(ocr_region, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}):
    """
    ocr返回内容+中心坐标
    :param ocr_region:
    :param remote_ocr_type:
    :return: [("文字", (x, y))...]
    """
    ocr_region = [int(item) for item in ocr_region]
    img_path = lx_snapshot(AppEnv.get_instance(), "ocr_temp_{}{}{}{}".format(*ocr_region), crop_pos=ocr_region, path=True)
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            ocr_res = [[item["txts"], ((item["box"][0][0]+item["box"][1][0])/2+ocr_region[0], (item["box"][0][1]+item["box"][2][1])/2
                                       + ocr_region[1])] for item in res]
            if ocr_res:
                for item in ocr_res:
                    if item[0] in fault_tolerant_map:
                        item[0] = fault_tolerant_map[item[0]]
                monitor_print(f"============ocr_keyword_return_pos: {ocr_res}")
                return ocr_res
    return []

def ocr_keyword_return_left_top_right_bottom_pos(ocr_region, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}):
    """
    ocr返回内容+左上右下坐标
    :param ocr_region:
    :param remote_ocr_type:
    :return: [("文字", (x, y))...]
    """
    img_path = lx_snapshot(AppEnv.get_instance(), "ocr_temp", crop_pos=ocr_region, path=True)
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            ocr_res = [[item["txts"], (((item["box"][0][0] + ocr_region[0], item["box"][0][1] + ocr_region[1])),
                        (item["box"][2][0] + ocr_region[0], item["box"][2][1] + ocr_region[1]))] for item in res]
            if ocr_res:
                for item in ocr_res:
                    if item[0] in fault_tolerant_map:
                        item[0] = fault_tolerant_map[item[0]]
                return ocr_res
    return []

def ocr_keyword_return_pos_with_image(img, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}, return_center_pos=False):
    """
    ocr返回内容+中心坐标
    :param ocr_region:
    :param remote_ocr_type:
    :return: [("文字", (x, y))...]
    """
    img_path = None
    if isinstance(img, str):
        if img.startswith("http"):
            # 从URL获取图像内容
            response = requests.get(img)
            img_path = os.path.join(ST.LOG_DIR, f"temp_{str(int(time.time() * 1000000))}.jpg")
            with open(img_path, "wb") as f:
                f.write(response.content)
        else:
            img_path = img
    elif isinstance(img, np.ndarray):
        img_path = os.path.join(ST.LOG_DIR, f"temp_{str(int(time.time() * 1000000))}.jpg")
        cv2.imwrite(img_path, img)
    elif isinstance(img, Image.Image):
        img_path = os.path.join(ST.LOG_DIR, f"temp_{str(int(time.time() * 1000000))}.jpg")
        img.save(img_path)
    if not img_path:
        return []
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            if return_center_pos:
                ocr_res = [[item["txts"], ((item["box"][0][0] + item["box"][1][0]) / 2, (item["box"][0][1] + item["box"][2][1]) / 2)] for item in res]
            else:
                ocr_res = [[item["txts"], item["box"]] for item in res]
            if ocr_res:
                for item in ocr_res:
                    if item[0] in fault_tolerant_map:
                        item[0] = fault_tolerant_map[item[0]]
                return ocr_res
    return []

def orc_return_number(ocr_region, remote_ocr_type=(3, 2, 1),  pattern=r"-?\d+", many=False, enhance_size=4):
    """
    ocr返回数字
    :param ocr_region:
    :param remote_ocr_type:
    :param pattern:
    :return:
    """
    img_path = lx_snapshot(AppEnv.get_instance(), "ocr_temp", crop_pos=ocr_region, path=True)
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            ocr_res = [int(re.findall(pattern, item["txts"])[0]) for item in res if re.findall(pattern, item["txts"])]
            if ocr_res:
                if many:
                    return ocr_res
                return ocr_res[0]
    result = enhanced_ocr_image(lx_snapshot(AppEnv.get_instance(), "ocr_temp", crop_pos=ocr_region),
                                enhance_size=(
                                    (ocr_region[2] - ocr_region[0])*enhance_size, (ocr_region[3] - ocr_region[1]) * enhance_size
                                ))
    for res in result:
        if len(res) > 0:
            return int(res[0]) if res[0].isdigit() else None
    return None


def orc_return_text(ocr_region, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}):
    """
    ocr返回文字
    :param ocr_region:
    :param remote_ocr_type:
    :return:
    """
    img_path = lx_snapshot(AppEnv.get_instance(), "ocr_temp", crop_pos=ocr_region, path=True)
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            ocr_res = [item["txts"] for item in res]
            if ocr_res:
                if ocr_res[0] in fault_tolerant_map:
                    return fault_tolerant_map[ocr_res[0]]
                return ocr_res[0]
    return None

def ocr_exists_text(ocr_region, remote_ocr_type=(2, 1, 3), text_list=[]):
    """
    ocr是否存在字符串
    :param ocr_region:
    :param remote_ocr_type:
    :param text_list:
    :return:
    """
    img_path = lx_snapshot(AppEnv.get_instance(), "ocr_temp", crop_pos=ocr_region, path=True)
    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            for item in res:
                if item["txts"] in text_list:
                    return True
    return False

# 工具方法
def lx_wait_pos(template, timeout=2, interval=0.5):
    """通常用于获取点击点"""
    return lx_wait(template, timeout=timeout, interval=interval, is_try=True)


def lx_wait_pos_touch(template, timeout=2, interval=0.5, touch_timeout=2):
    """通常用于获取点击点，然后点击"""
    pos = lx_wait(template, timeout=timeout, interval=interval, is_try=True)
    if not pos:
        return False
    lx_touch(pos, touch_timeout)
    return True

def save_image_to_path(image, image_path="temp"):
    """保存图片"""
    final_path = os.path.join(ST.LOG_DIR, f"{image_path}_{str(int(time.time()*1000000))}.jpg")
    cv2.imwrite(final_path, image)
    return final_path

def get_average_gray(img, region_pos=None, pos=None, thumb_size=40, MSE_cutoff=22, adjust_color_bias=True, type=0):
    # 加载图片
    image = None
    if isinstance(img, str):
        image = Image.open(img)
    elif isinstance(img, np.ndarray):
        cv2.imwrite(os.path.join(ST.LOG_DIR, "temp.jpg"), img)
        image = Image.open(os.path.join(ST.LOG_DIR, "temp.jpg"))
        # image = Image.fromarray(img)
    elif isinstance(img, Image.Image):
        image = img
    if not image:
        return -1
    if region_pos:
        image = image.crop(region_pos)
    # cv2.imwrite(img_path, image)
    if type == 0:
        # 将图片转换为灰度图像（"L"模式代表灰度图）
        gray_image = image.convert("L")
        # 使用ImageStat模块获取统计信息
        stat = ImageStat.Stat(gray_image)
        # 使用mean方法计算平均灰度值
        average_gray_value = stat.mean[0]
        # print(f"图片的平均灰度值是: {average_gray_value}")
        return average_gray_value
    if type == 1:
        # 将图片转换成RGB模式
        image = image.convert("RGB")
        # 生成颜色直方图，得到一个包含每种颜色出现次数的数组
        histogram = image.histogram()
        # 计算出现在直方图中的非零值的数量，即颜色数量
        # 注意：由于直方图是RGB三个通道连续排列的，所以要除以3计算实际的颜色数
        num_colors = sum(1 for i in histogram[::3] if i != 0)
        print(f"图片的颜色数量是: {num_colors}")
        return num_colors
    if type == 2:
        # 将Pillow图像转换为NumPy数组
        image_array = np.array(image)
        # 根据颜色通道分割数组：R, G 和 B
        r_channel = image_array[:, :, 0]
        g_channel = image_array[:, :, 1]
        b_channel = image_array[:, :, 2]
        # 计算每个通道的平均值
        r_mean = np.mean(r_channel)
        g_mean = np.mean(g_channel)
        b_mean = np.mean(b_channel)
        # 计算每个通道的方差
        r_variance = np.var(r_channel)
        g_variance = np.var(g_channel)
        b_variance = np.var(b_channel)
        # 计算每个通道的标准差
        r_stddev = np.std(r_channel)
        g_stddev = np.std(g_channel)
        b_stddev = np.std(b_channel)
        print(f"红色通道平均值: {r_mean}, 方差: {r_variance}, 标准差: {r_stddev}")
        print(f"绿色通道平均值: {g_mean}, 方差: {g_variance}, 标准差: {g_stddev}")
        print(f"蓝色通道平均值: {b_mean}, 方差: {b_variance}, 标准差: {b_stddev}")
        return r_mean

    if type == 3:
        # 将Pillow图像转换为NumPy数组
        image_array = np.array(image)
        # 根据颜色通道分割数组：R, G 和 B
        r_channel = image_array[:, :, 0]
        g_channel = image_array[:, :, 1]
        b_channel = image_array[:, :, 2]
        # 计算每个通道的平均值
        r_mean = np.mean(r_channel)
        g_mean = np.mean(g_channel)
        b_mean = np.mean(b_channel)
        monitor_print("rbg_mean : " + str(r_mean) + "," + str(g_mean) + "," + str(b_mean))
        return r_mean, g_mean, b_mean
    if type == 4:
        # 获取图像中特定点的颜色
        color = image.getpixel(pos)  # x, y是点的坐标
        print(f"=========坐标{pos}, 颜色: {color}")
        return color
    if type == 5:
        # 转换为RGB模式
        # img = image.convert('RGB')
        # 转换为NumPy数组
        image = image.convert("RGB")
        np_img = np.array(image)
        # 分离RGB通道
        r, g, b = np_img[:, :, 0], np_img[:, :, 1], np_img[:, :, 2]
        # 计算最大和最小RGB值
        max_rgb = np.maximum(np.maximum(r, g), b)
        min_rgb = np.minimum(np.minimum(r, g), b)
        # 计算饱和度
        saturation = np.mean((max_rgb - min_rgb) / max_rgb * 255)
        return saturation
    if type == 6:
        # 一晨
        pil_img = image
        bands = pil_img.getbands()
        if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
            thumb = pil_img.resize((thumb_size, thumb_size))
            SSE, bias = 0, [0, 0, 0]
            if adjust_color_bias:
                bias = ImageStat.Stat(thumb).mean[:3]
                bias = [b - sum(bias) / 3 for b in bias]
            for pixel in thumb.getdata():
                mu = sum(pixel) / 3
                SSE += sum((pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2])
            MSE = float(SSE) / (thumb_size * thumb_size)
            if MSE <= MSE_cutoff:
                print("grayscale")
                # 灰色
                return 1
            else:
                print("Color\t\t\t")
                return 0
            print(f"MSE:{MSE}")
        elif len(bands) == 1:
            print(f"Black and white:{bands}")
            # 黑白
            return 1
        else:
            print(f"Don't know...:{bands}")
            return 0

    # if type == 3:
    #     gray_image = image.convert('L')
    #     gray = gray_image.getpixel(pos)
    #     print(f"像素灰度值: {gray}")
    #     return gray

def upload_current_snapshot(desc):
    name = 'adc_catch_' + str(int(time.time() * 1000000)) + '.jpg'
    snapshot(filename=name, msg="get a snapshot.")
    image_path = AppEnv.get_instance().logPath + '/' + name
    _, cdn_url_list = upload_jym_oss_with_pathes([image_path])
    monitor_task_status(AppEnv.get_instance(), desc, f"{cdn_url_list}")
    return cdn_url_list

def dwarf_swipe(swipe_from_pos, swipe_to_pos, screenshot_name=None, screenshot_region=None, duration=0.8):
    """
    可以在滑动结束动手前截图
    :param swipe_from_pos: 滑动起始位置
    :param swipe_to_pos: 滑动终止位置
    :param screenshot_name: 截图名，可空，空则不截图
    :param screenshot_region: 截图区域
    :param duration:
    :return:
    :except:
        >>> dwarf_swipe((675, 1200), (675, 380), screenshot_name="测试截图" + "_" + str(int(time.time() * 1000000)) + '.jpg'
        >>>    , screenshot_region=(43, 1269, 540, 1342))
    """
    print(f"dwarf_swipe: {swipe_from_pos}->{swipe_to_pos}")
    device = AppEnv.get_instance().device
    custom_event = CustomEvent(device)
    from_x, from_y = swipe_from_pos
    to_x, to_y = swipe_to_pos
    coordinates_list = [(from_x, from_y), (to_x, to_y-2), (to_x, to_y)]
    coordinates_list = [device.touch_proxy.ori_transformer(xy) for xy in coordinates_list]
    custom_event.swipe_along(coordinates_list, duration=duration, screenshot_name=screenshot_name)
    if screenshot_name and screenshot_region:
        image_path = AppEnv.get_instance().logPath + '/' + screenshot_name
        image = cv2.imread(image_path)
        image = image[screenshot_region[1]: screenshot_region[3], screenshot_region[0]: screenshot_region[2]]
        cv2.imwrite(image_path, image)



def dwarf_swipe_bottom(swipe_from_pos, swipe_to_pos, bottom_region, bottom_img, degree=0.7):
    """
    滑动，带判底部，到底后松手前下面是空的
    :param swipe_from_pos: 滑动起始坐标
    :param swipe_to_pos: 滑动结束坐标
    :param bottom_region: 底部区域坐标
    :param bottom_img: 用于对比的底部区域图片路径
    :param degree: 相似度阀值
    :return: True 到底了 False没有到底
    :except:
        >>> is_bottom = dwarf_swipe_bottom((675, 1200), (675, 380), (43, 1269, 540, 1342), "底部判断图片_1720494779077168.jpg")
    """
    screenshot_name = "swipe_bottom" + "_" + str(int(time.time() * 1000000)) + '.jpg'
    dwarf_swipe(swipe_from_pos, swipe_to_pos, screenshot_name=screenshot_name, screenshot_region=bottom_region)
    if calculate(cv2.imread(AppEnv.get_instance().logPath + '/' + screenshot_name), cv2.imread(bottom_img)) > degree:
        return True
    return False

def dwarf_swipe_bottom_plus(swipe_from_pos, swipe_to_pos, check_region, degree=0.7):
    """
    滑动,带判底，松手前截一张松手后截一张判断一不一样，到底有回弹
    :param swipe_from_pos: 滑动起始坐标
    :param swipe_to_pos: 滑动结束坐标
    :param check_region: 判断相似度区域坐标
    :param degree:
    :return:
    """
    print(f"dwarf_swipe_bottom_plus开始滑动: {swipe_from_pos}->{swipe_to_pos}")
    screenshot_name = "swipe_before_up" + "_" + str(int(time.time() * 1000000)) + '.jpg'
    dwarf_swipe(swipe_from_pos, swipe_to_pos, screenshot_name=screenshot_name, screenshot_region=check_region)
    sleep(1)
    # 必须写进去再读出来不然相似度有问题
    after_up_img_path = lx_snapshot(AppEnv.get_instance(), f"swipe_after_up", crop_pos=check_region, path=True)
    # round_degree = calculate(cv2.imread(AppEnv.get_instance().logPath + '/' + screenshot_name), lx_snapshot(AppEnv.get_instance(), f"swipe_after_up", crop_pos=check_region))
    round_degree = calculate(cv2.imread(AppEnv.get_instance().logPath + '/' + screenshot_name), cv2.imread(after_up_img_path))
    print(f"dwarf_swipe_bottom_plus相似度: {round_degree}")
    if round_degree > degree:
        return False
    return True

from collections import defaultdict


def find_closest_group_average(numbers, abs_diff=5, rows=5):
    # 创建一个字典来存储数字之间的差值在5以内的情况
    close_numbers = defaultdict(list)
    # 找出相差5以内的数字
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            diff = abs(numbers[i] - numbers[j])
            if diff <= abs_diff:
                close_numbers[i].append(numbers[j])
                close_numbers[j].append(numbers[i])
    # 找出包含最多数字的组
    if not close_numbers:
        return 0
    max_group = max(close_numbers.values(), key=len)
    # 计算最多数字组的平均值
    avg = sum(max_group) / len(max_group) if max_group else 0
    return int(avg)


def group_and_calculate_averages(numbers, abs_diff, min_count):
    """
    适用场景，ocr整排去获取锚点的时候，有干扰项，但是目标识别内容一定是整排都有
    :param numbers:
    :param abs_diff: 相差阈值
    :param min_count: 单行最少几个
    :return:
    """
    # 首先对数字进行排序
    numbers.sort()

    groups = []
    current_group = [numbers[0]]

    # 分组过程
    for number in numbers[1:]:
        if number - current_group[-1] <= abs_diff:
            current_group.append(number)
        else:
            if len(current_group) >= min_count:
                groups.append(current_group)
            current_group = [number]

    # 检查最后一个分组
    if len(current_group) >= min_count:
        groups.append(current_group)
    # 计算每个组的平均值
    averages = [sum(group) / len(group) for group in groups]

    return averages


def swipe_screenshot_by_bottom(swipe_from_pos, swipe_to_pos, bottom_region, bottom_img, crop_data, combine_part_name, check_normal_image_func=None, check_normal_image_continue=True,  degree=0.7, max_swipe_count=20):
    """
    :param swipe_from_pos: 滑动开始
    :param swipe_to_pos: 滑动结束
    :param bottom_region: 拉到极限底部空白区域坐标
    :param bottom_img: 拉到极限底部空白对比图片
    :param crop_data: [前两排左上坐标(x,y)， 前两排右下坐标(x,y), 单个右下角坐标(x,y),  一排几个, 一次截几排, 拉到底最后一排y坐标]
    :param combine_part_name: 图片名
    :param check_normal_image_func: 检查图片是否正常
    :param check_normal_image_continue: 不正常是否继续
    :param degree: 拉到极限图片对比相似度阀值，默认0.7
    :param max_swipe_count: 超时方案
    :return:
    """
    # 滑动数据
    img_list = []
    buttom_imgs = []
    hori_count = crop_data[3]
    vert_count = crop_data[4]
    item_start_x, item_start_y = crop_data[0]
    item_width = crop_data[2][0] -crop_data[0][0]
    item_height = crop_data[2][1] -crop_data[0][1]
    item_interval_x = int(((crop_data[1][0]-item_start_x) - (item_width*hori_count))/(hori_count-1))
    item_interval_y = int((crop_data[1][1]-item_start_y) - (item_height*2))
    bottom_start_y= crop_data[5]
    print(f"单个元素，宽:{item_width}, 高: {item_height}, 水平间隔: {item_interval_x}, 垂直间隔: {item_interval_y}")
    last_img_path = None
    for swipe_round in range(max_swipe_count):
        swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_{swipe_round}", path=True)
        if swipe_round == 0:
            for item_crop_vert_index in range(vert_count):
                crop_y = item_crop_vert_index*(item_height+item_interval_y) + item_start_y
                for item_crop_hori_idex in range(hori_count):
                    item_img_name = f"cropped_image_{combine_part_name}_{swipe_round}_{(item_crop_vert_index+1)*(item_crop_hori_idex+1)}.jpg"
                    crop_x = item_crop_hori_idex * (item_width + item_interval_x) + item_start_x
                    item_img = crop_pos_image_from_snapshot(swipe_screenshot_source,
                                                              item_img_name,
                                                              (crop_x, crop_y),
                                                              (crop_x+item_width, crop_y+item_height))
                    if check_normal_image_func and not check_normal_image_func(item_img):
                        if not check_normal_image_continue:
                            return img_list
                        continue
                    last_img_path = os.path.join(AppEnv.get_instance().logPath, item_img_name)
                    img_list.append(item_img)

            continue
        is_bottom = dwarf_swipe_bottom(swipe_from_pos, swipe_to_pos, bottom_region, bottom_img, degree)
        if is_bottom:
            # 到底了的截图逻辑, 从下往上截图，对比相似度
            for item_crop_vert_index in range(vert_count):
                crop_y = bottom_start_y - (item_crop_vert_index * (item_height + item_interval_y))
                for item_crop_hori_idex in range(hori_count):
                    item_img_name = f"cropped_image_{combine_part_name}_{swipe_round}_{(item_crop_vert_index + 1) * (item_crop_hori_idex + 1)}.jpg"
                    crop_x = (hori_count-item_crop_hori_idex-1) * (item_width + item_interval_x) + item_start_x
                    item_img = crop_pos_image_from_snapshot(swipe_screenshot_source,
                                                            item_img_name,
                                                            (crop_x, crop_y),
                                                            (crop_x + item_width, crop_y + item_height))
                    if calculate(cv2.imread(last_img_path),
                                 item_img) > degree:
                        print("图片一样了,结束")
                        buttom_imgs.reverse()
                        img_list.extend(buttom_imgs)
                        return img_list
                    if check_normal_image_func and not check_normal_image_func(item_img):
                        if not check_normal_image_continue:
                            buttom_imgs.reverse()
                            img_list.extend(buttom_imgs)
                            return img_list
                        continue
                    buttom_imgs.append(item_img)
            break
        for item_crop_vert_index in range(vert_count):
            crop_y = item_crop_vert_index*(item_height+item_interval_y) + item_start_y
            for item_crop_hori_idex in range(hori_count):
                item_img_name = f"cropped_image_{combine_part_name}_{swipe_round}_{(item_crop_vert_index+1)*(item_crop_hori_idex+1)}.jpg"
                crop_x = item_crop_hori_idex * (item_width + item_interval_x) + item_start_x
                item_img = crop_pos_image_from_snapshot(swipe_screenshot_source,
                                                          item_img_name,
                                                          (crop_x, crop_y),
                                                          (crop_x+item_width, crop_y+item_height))
                if check_normal_image_func and not check_normal_image_func(item_img):
                    if not check_normal_image_continue:
                        return img_list
                    continue
                last_img_path = os.path.join(AppEnv.get_instance().logPath, item_img_name)
                img_list.append(item_img)
    buttom_imgs.reverse()
    img_list.extend(buttom_imgs)
    return img_list


def swipe_screenshot(swipe_from_pos, swipe_to_pos, check_region, crop_data, combine_part_name, check_normal_image_func=None, check_normal_image_continue=True,  degree=0.7, check_repeat_degree=0.7, max_swipe_count=20, swipe_fault_type=None, swipe_fault=None, swipe_fault_rows=4, poco=None, quality=None):
    """
    :param swipe_from_pos: 滑动开始
    :param swipe_to_pos: 滑动结束
    :param check_region: 检查是否到底的区域，拉到极限回弹前后的不一样的区域
    :param crop_data: [前两排左上坐标(x,y)， 前两排右下坐标(x,y), 单个右下角坐标(x,y),  一排几个, 一次截几排, 拉到底最后一排y坐标]
    :param combine_part_name: 图片名
    :param check_normal_image_func: 检查图片是否正常
    :param check_normal_image_continue: 不正常是否继续
    :param degree: 拉到极限图片对比相似度阀值，默认0.7
    :param max_swipe_count: 超时方案
    :param poco 是否使用poco
    :return:
    """
    # 滑动数据
    img_list = []
    buttom_imgs = []
    hori_count = crop_data[3]
    vert_count = crop_data[4]
    item_start_x, item_start_y = crop_data[0]
    item_width = crop_data[2][0] -crop_data[0][0]
    item_height = crop_data[2][1] -crop_data[0][1]
    item_interval_x = int(((crop_data[1][0]-item_start_x) - (item_width*hori_count))/(hori_count-1))
    item_interval_y = int((crop_data[1][1]-item_start_y) - (item_height*2))
    bottom_start_y = crop_data[5]
    max_rows = crop_data[6]
    print(f"单个元素，宽:{item_width}, 高: {item_height}, 水平间隔: {item_interval_x}, 垂直间隔: {item_interval_y}")
    last_img = None
    for swipe_round in range(max_swipe_count):
        print(id(item_start_y))
        print(f"当前Y: {item_start_y},  =====================\n")
        if swipe_round == 0:
            swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_{swipe_round}",
                                                  quality=quality)
            for item_crop_vert_index in range(vert_count):
                crop_y = item_crop_vert_index*(item_height+item_interval_y) + item_start_y
                for item_crop_hori_idex in range(hori_count):
                    # print(f"{item_crop_vert_index}排{item_crop_hori_idex}列: {crop_y}")
                    # item_img_name = f"cropped_image_{combine_part_name}_{swipe_round}_{item_crop_vert_index}_{item_crop_hori_idex}.jpg"
                    crop_x = item_crop_hori_idex * (item_width + item_interval_x) + item_start_x
                    item_img = crop_pos_from_image(swipe_screenshot_source,
                                                              (crop_x, crop_y),
                                                              (crop_x+item_width, crop_y+item_height))
                    if check_normal_image_func and not check_normal_image_func(item_img, crop_region_pos=(crop_x, crop_y, crop_x+item_width, crop_y+item_height)):
                        if not check_normal_image_continue:
                            buttom_imgs.reverse()
                            img_list.extend(buttom_imgs)
                            return img_list
                        continue
                    last_img = item_img
                    img_list.append(item_img)
            continue
        is_bottom = dwarf_swipe_bottom_plus(swipe_from_pos, swipe_to_pos, check_region, degree) if not poco\
            else dwarf_swipe_bottom_plus_poco(poco, swipe_from_pos, swipe_to_pos, check_region, degree)
        swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_{swipe_round}",
                                              quality=quality)
        if is_bottom:
            sleep(2)
            # 到底了的截图逻辑, 从下往上截图，对比相似度
            for item_crop_vert_index in range(max_rows):
                crop_y = bottom_start_y - (item_crop_vert_index * (item_height + item_interval_y))
                for item_crop_hori_idex in range(hori_count):
                    # item_img_name = f"cropped_image_bottom_{combine_part_name}_{swipe_round}_{item_crop_vert_index}_{item_crop_hori_idex}.jpg"
                    crop_x = (hori_count-item_crop_hori_idex-1) * (item_width + item_interval_x) + item_start_x
                    item_img = crop_pos_from_image(swipe_screenshot_source,
                                                            (crop_x, crop_y),
                                                            (crop_x + item_width, crop_y + item_height))
                    if item_crop_hori_idex == 0:
                        print(f"到底判断相似度： {check_repeat_degree}")
                        if calculate(last_img,
                                     item_img) > check_repeat_degree:
                            print("图片一样了,结束")
                            buttom_imgs.reverse()
                            img_list.extend(buttom_imgs)
                            return img_list
                    if check_normal_image_func and not check_normal_image_func(item_img, crop_region_pos=(crop_x, crop_y, crop_x+item_width, crop_y+item_height)):
                        # if not check_normal_image_continue:
                        #     buttom_imgs.reverse()
                        #     img_list.extend(buttom_imgs)
                        #     return img_list
                        continue
                    buttom_imgs.append(item_img)
            break
        if swipe_fault_type:
            print(f"==========================={swipe_fault_type}")
            if swipe_fault_type == 1:
                # 逻辑不动
                new_y = []
                res = ocr_keyword_return_pos((item_start_x, item_start_y, item_start_x + (item_width + item_interval_x)
                                              * hori_count, item_start_y + item_height + item_interval_y))
                print(res)
                for item in res:
                    if item[0][0].isdigit():
                        new_y.append(item[1][1])
                print(new_y)
                print("--------------->")
                if len(new_y) > 1:
                    abs_new_y = find_closest_group_average(new_y, abs_diff=5)
                    if abs_new_y > 0:
                        item_start_y = int(abs_new_y - swipe_fault)
                print(f"矫正后的y: {item_start_y}")
            elif swipe_fault_type == 2:
                # 小小蚂国的情况， 获取上面的数字, 可能获取两排获取下面的情况
                new_y = []
                res = ocr_keyword_return_pos((item_start_x, item_start_y, item_start_x + (item_width + item_interval_x)
                                              * hori_count, int(item_start_y + item_height/2)))
                print(res)
                for item in res:
                    new_y.append(item[1][1])
                print(new_y)
                print("--------------->")
                if len(new_y) > 0:
                    abs_new_y_list = group_and_calculate_averages(new_y, 20, swipe_fault_rows)
                    if abs_new_y_list:
                        item_start_y = int(abs_new_y_list[0] - swipe_fault)
                print(f"矫正后的y: {item_start_y}")
        for item_crop_vert_index in range(vert_count):
            crop_y = item_crop_vert_index*(item_height+item_interval_y) + item_start_y
            for item_crop_hori_idex in range(hori_count):
                # item_img_name = f"cropped_image_{combine_part_name}_{swipe_round}_{item_crop_vert_index}_{item_crop_hori_idex}.jpg"
                crop_x = item_crop_hori_idex * (item_width + item_interval_x) + item_start_x
                item_img = crop_pos_from_image(swipe_screenshot_source,
                                                          (crop_x, crop_y),
                                                          (crop_x+item_width, crop_y+item_height))
                if check_normal_image_func and not check_normal_image_func(item_img, crop_region_pos=(crop_x, crop_y, crop_x+item_width, crop_y+item_height)):
                    if not check_normal_image_continue:
                        return img_list
                    continue
                last_img = item_img
                img_list.append(item_img)
    buttom_imgs.reverse()
    img_list.extend(buttom_imgs)
    return img_list



def swipe_touch(swipe_from_pos, swipe_to_pos, check_bottom_region, check_repeat_region, touch_data, check_repeat_type=1, after_touch_fun=None, level=True,  degree=0.7, max_touch_count=None, max_swipe_count=50, poco=None, item_swipe_count=1):
    """
    :param swipe_from_pos: 滑动开始
    :param swipe_to_pos: 滑动结束
    :param check_bottom_region: 拉到极限底部空白区域坐标
    :param check_repeat_region: 判断重复的区域
    :param touch_data: [起始坐标(x,y)， 间隔, 到底后的y, 滑一次点击几个]
    :param degree: 拉到极限图片对比相似度阀值，默认0.7
    :param max_swipe_count: 超时方案
    :param poco 是否使用poco
    :return:
    """
    # 滑动数据
    img_list = []
    touch_count = 0
    touch_start_x, touch_start_y = touch_data[0]
    touch_interval = touch_data[1]
    bottom_start_y = touch_data[2]
    item_touch_count = touch_data[3]
    print(f"点击数据，起始坐标: {touch_start_x, touch_start_y}, 间隔：{touch_interval}")
    for swipe_round in range(max_swipe_count):
        last_check_repeat_img = lx_snapshot(AppEnv.get_instance(), f"check_repeat_img_{swipe_round}",
                                                 crop_pos=check_repeat_region)
        if swipe_round == 0:
            for touch_index in range(item_touch_count):
                touch_pos = (touch_start_x, touch_start_y + touch_index*touch_interval) if level \
                    else (touch_start_x + touch_index*touch_interval, touch_start_y)
                lx_touch(touch_pos, 1) if not poco else adb_touch(touch_pos, 1)
                touch_count += 1
                if max_touch_count and touch_count > max_touch_count:
                    return
                if after_touch_fun:
                    if not after_touch_fun():
                        return
            continue
        # is_bottom = dwarf_swipe_bottom_plus(swipe_from_pos, swipe_to_pos, check_bottom_region, degree)
        for _ in range(item_swipe_count):
            is_bottom = dwarf_swipe_bottom_plus(swipe_from_pos, swipe_to_pos, check_bottom_region, degree) if not poco\
                else dwarf_swipe_bottom_plus_poco(poco, swipe_from_pos, swipe_to_pos, check_bottom_region, degree)
            if is_bottom:
                break
        if is_bottom:
            # 到底了的截图逻辑, 从下往上截图，对比相似度
            if check_repeat_type == 2:
                last_round_text = ocr_keyword_return_pos_with_image(last_check_repeat_img)
            for touch_index in range(item_touch_count):
                touch_pos = (touch_start_x, bottom_start_y - touch_index * touch_interval) if level \
                    else (bottom_start_y - touch_index * touch_interval, touch_start_y)
                lx_touch(touch_pos, 1) if not poco else adb_touch(touch_pos, 1)
                if check_repeat_type == 1:
                    if calculate(lx_snapshot(AppEnv.get_instance(), f"check_repeat_img_bottom_{touch_index}", crop_pos=check_repeat_region),
                                 last_check_repeat_img) > degree:
                        print("重复了")
                        break
                elif check_repeat_type == 2:
                    current_text = ocr_keyword_return_pos_with_image(
                        lx_snapshot(AppEnv.get_instance(), f"check_repeat_img_bottom_{touch_index}",
                                    crop_pos=check_repeat_region))
                    if current_text and last_round_text:
                        if current_text[0][0] == last_round_text[0][0]:
                            print("重复了")
                            break
                    else:
                        print("判断失败")
                touch_count += 1
                if max_touch_count and touch_count > max_touch_count:
                    return
                if after_touch_fun:
                    if not after_touch_fun():
                        return
            break
        for touch_index in range(item_touch_count):
            touch_pos = (touch_start_x, touch_start_y + touch_index * touch_interval) if level \
                else (touch_start_x + touch_index * touch_interval, touch_start_y)
            lx_touch(touch_pos, 1) if not poco else adb_touch(touch_pos, 1)
            touch_count += 1
            if max_touch_count and touch_count > max_touch_count:
                return
            if after_touch_fun:
                if not after_touch_fun():
                    return


def adb_touch(pos, timeout=0.5):
    """原生点击"""
    shell("input tap {} {}".format(pos[0], pos[1]))
    sleep(timeout)

def adb_swipe(pos, timeout=1):
    """原生滑动"""
    shell("input swipe {} {} {} {} 1000".format(pos[0], pos[1], pos[2], pos[3]))
    sleep(timeout)

def poco_swipe(poco, swipe_from_pos, swipe_to_pos, screenshot_name=None, screenshot_region=None, hold=0.8,
               speed=0.6, accuracy=0.04):
    """poco滑动"""
    print("=====滑动")
    coordinate2normalized = lambda start_end_pos: [start_end_pos[0] / 2400, start_end_pos[1] / 1350]
    mt = CustomMotionTrack(speed=speed)
    if screenshot_name and screenshot_region:
        mt.up = False
        mt.start(coordinate2normalized(swipe_from_pos)).hold(hold).move(coordinate2normalized(swipe_to_pos)).hold(
            hold)
        poco.apply_motion_tracks([mt], accuracy=accuracy)
        image = lx_snapshot(AppEnv.get_instance(), screenshot_name, crop_pos=screenshot_region)
        cv2.imwrite(os.path.join(AppEnv.get_instance().logPath, screenshot_name), image)
        up_mt = CustomMotionTrack()
        up_mt.start(coordinate2normalized(swipe_to_pos))
        up_mt.hold(hold)
        poco.apply_motion_tracks([up_mt], accuracy=accuracy)
    else:
        mt.start(coordinate2normalized(swipe_from_pos)).hold(0.1).move(coordinate2normalized(swipe_to_pos)).hold(0.5)
        poco.apply_motion_tracks([mt], accuracy=accuracy)


def dwarf_swipe_bottom_plus_poco(poco, swipe_from_pos, swipe_to_pos, check_region, degree=0.7):
    """
    滑动,带判底，松手前截一张松手后截一张判断一不一样，到底有回弹, poco版本
    :param poco
    :param swipe_from_pos: 滑动起始坐标
    :param swipe_to_pos: 滑动结束坐标
    :param check_region: 判断相似度区域坐标
    :param degree:
    :return:
    """
    screenshot_name = "swipe_before_up" + "_" + str(int(time.time() * 1000000)) + '.jpg'
    print(f"开始滑动: {swipe_from_pos}, {swipe_to_pos}")
    poco_swipe(poco, swipe_from_pos, swipe_to_pos, screenshot_name=screenshot_name, screenshot_region=check_region)
    sleep(0.5)
    # 必须写进去再读出来不然相似度有问题
    after_up_img_path = lx_snapshot(AppEnv.get_instance(), f"swipe_after_up", crop_pos=check_region, path=True)
    round_degree = calculate(cv2.imread(os.path.join(AppEnv.get_instance().logPath, screenshot_name)), cv2.imread(after_up_img_path))
    print(f"滑动相似度： {round_degree}")
    if round_degree > degree:
        return False
    return True


def dwarf_swipe_return_screenshot(swipe_from_pos, swipe_to_pos, screenshot_region=None, duration=0.8):
    """
    滑动,滑动过程截一系列图片
    :param swipe_from_pos: 滑动起始位置
    :param swipe_to_pos: 滑动终止位置
    :param screenshot_region: 截图区域
    :param duration:
    :return:
    """
    device = AppEnv.get_instance().device
    custom_event = CustomEvent(device)
    from_x, from_y = swipe_from_pos
    to_x, to_y = swipe_to_pos
    screenshot_name_list = custom_event.swipe_along_return_screenshot([(from_x, from_y), (to_x, to_y-2), (to_x, to_y)],
                             duration=duration)
    image_list = []
    for item in screenshot_name_list:
        image_path = AppEnv.get_instance().logPath + '/' + item
        image = cv2.imread(image_path)
        image = image[screenshot_region[1]: screenshot_region[3], screenshot_region[0]: screenshot_region[2]]
        image_list.append(image)
    return image_list


def dwarf_swipe_bottom_without_resilience(swipe_from_pos, swipe_to_pos, check_region, degree=0.8):
    """
    滑动,带判底，滑动过程持续截图
    :param swipe_from_pos: 滑动起始坐标
    :param swipe_to_pos: 滑动结束坐标
    :param check_region: 判断相似度区域坐标
    :param degree:
    :return:
    """
    # screenshot_name = "swipe_before_up" + "_" + str(int(time.time() * 1000000)) + '.jpg'
    image_list = dwarf_swipe_return_screenshot(swipe_from_pos, swipe_to_pos, screenshot_region=check_region)
    # print(image_list)
    # 必须写进去再读出来不然相似度有问题
    # round_degree = calculate(cv2.imread(AppEnv.get_instance().logPath + '/' + screenshot_name), lx_snapshot(AppEnv.get_instance(), f"swipe_after_up", crop_pos=check_region))
    round_degree = calculate(image_list[-1], image_list[-2])
    print(f"相似度： {round_degree}")
    if round_degree > degree:
        return True
    return False

def upload_current_catch(name):
    name = f'adc_catch_{name}_' + str(int(time.time() * 1000000)) + '.jpg'
    snapshot(filename=name, msg="get a snapshot.")
    image_path = AppEnv.get_instance().logPath + '/' + name
    _, cdn_url_list = upload_jym_oss_with_pathes([image_path])
    monitor_print(f"upload_current_catch: {name}_{cdn_url_list}")


def upload_img_to_oss(img, filename=None):
    """
    上传图片到oss
    :param img:
    :param filename:
    :return:
    """
    # print("==================================")
    img_path = None
    if isinstance(img, str):
        if img.startswith("http"):
            # 从URL获取图像内容
            response = requests.get(img)
            img_path = os.path.join(ST.LOG_DIR, f"temp_{str(int(time.time() * 1000000))}.jpg")
            with open(img_path, "wb") as f:
                f.write(response.content)
        else:
            img_path = img
    elif isinstance(img, np.ndarray):
        img_path = os.path.join(ST.LOG_DIR, f"temp_{str(int(time.time() * 1000000))}.jpg")
        cv2.imwrite(img_path, img)
    elif isinstance(img, Image.Image):
        img_path = os.path.join(ST.LOG_DIR, f"temp_{str(int(time.time() * 1000000))}.jpg")
        img.save(img_path)
    if not img_path:
        return []
    # print(img_path)
    sig_result = get_jym_oss_signature()
    print(f"---upload_img_to_oss:{sig_result}")

    final_sig_result_object = None
    is_new_api = True
    if is_new_api:
        final_sig_result_object = sig_result
    else:
        final_sig_result_json = sig_result['data']
        final_sig_result_object = json.loads(final_sig_result_json)

    # final_sig_result_json = sig_result['data']
    # final_sig_result_object = json.loads(final_sig_result_json)
    final_sig_result = final_sig_result_object['result']
    if final_sig_result is None or len(final_sig_result) == 0:
        return None
    access_id = final_sig_result['accessId']
    policy = final_sig_result['policy']
    signature = final_sig_result['signature']
    host = final_sig_result['host']
    dir = final_sig_result['dir']
    # 构建OSS上传URL
    url = host
    oss_path_list = []
    cdn_url_list = []
    # 构建文件表单数据
    files = {
        'file': open(img_path, "rb"),
    }
    # 设置请求参数
    object_name = filename or f"{dir}{filename or img_path.split('/')[-1]}"
    params = {
        'OSSAccessKeyId': access_id,
        'policy': policy,
        'Signature': signature,
        'key': object_name,
        'success_action_status': '200',
    }
    response = requests.post(url, data=params, files=files)
    if response.status_code == 200:
        oss_path = '/' + object_name
        cdn_url = 'https://static.jiaoyimao.com' + oss_path
    else:
        retry_response = requests.post(url, data=params, files=files)
        if retry_response.status_code == 200:
            oss_path = '/' + object_name
            cdn_url = 'https://static.jiaoyimao.com' + oss_path
            return oss_path, cdn_url
        else:
            monitor_print(f"上传图片错误: {retry_response.status_code}")
            return None, None
    monitor_print(f"----upload_img_to_oss:{oss_path_list}, {cdn_url_list}")
    return oss_path, cdn_url


def clean_img_color_normalization(image, color=[255, 255, 255], scope=30, clean_type=0):
    # 将白色的像素值设为255，其他颜色设为0
    r, g, b = color
    white_lower = np.array([r-scope if r-scope > 0 else 0, g-scope if g-scope > 0 else 0, b-scope if b-scope > 0 else 0], dtype=np.uint8)
    white_upper = np.array([r+scope if r+scope < 255 else 255, g+scope if g+scope < 255 else 255, b+scope if b+scope < 255 else 255], dtype=np.uint8)
    mask = cv2.inRange(image, white_lower, white_upper)
    # 将非白色的像素改为黑色
    if clean_type == 0:
        # 不满足的都变成黑色
        image[mask != 255] = [0, 0, 0]
    else:
        # 满足的都变成白色
        image[mask > 0] = [255, 255, 255]
    return image



def image_match_in(template_img, current_img, threshold=0.7):
    template_img_height, template_img_width = template_img.shape[0:2]
    current_img_img_height, current_img_img_width = current_img.shape[0:2]
    print(template_img_height, current_img_img_height)
    if template_img_height > current_img_img_height or template_img_width > current_img_img_width:
        return None
    result = cv2.matchTemplate(template_img, current_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(min_val, max_val, min_loc, max_loc)
    top_left = max_loc
    bottom_right = (top_left[0] + template_img.shape[1], top_left[1] + template_img.shape[0])
    # print(bottom_right)
    print(f"top_left: {top_left}, bottom_right: {bottom_right}, threshold: {max_val}")
    if max_val > threshold:
        return [top_left, bottom_right]
    else:
        return None

def dwarf_wait_until(template_list, text_list=None, ocr_region=None, timeout=3, interval=0.5, is_fast=False):
    """
    超时等待页面加载完成
    :param template_list:
    :param text_list:
    :param ocr_region:
    :param timeout:
    :param interval:
    :return:
    """
    if is_fast:
        ST.CVSTRATEGY = ["tpl"]
    start_time = time.time()
    while time.time() - start_time < timeout:
        for template in template_list:
            if exists(template):
                if is_fast:
                    ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
                return True
        if text_list and ocr_region:
            if ocr_exists_text(ocr_region, text_list=text_list):
                if is_fast:
                    ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
                return True
        sleep(interval)
    if is_fast:
        ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
    return False

def dwarf_exists(template, timeout=1, interval=0.5, is_fast=False, match_region=None):
    """这个exists相比可以定义超时时间默认1秒，实际没什么卵用"""
    if is_fast:
        ST.CVSTRATEGY = ["tpl"]
    try:
        pos = loop_find(template, timeout=timeout, interval=interval)
    except TargetNotFoundError:
        monitor_print(f"dwarf_exists_notfound: {template}")
        if is_fast:
            ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
        return False
    else:
        if is_fast:
            ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
        if match_region and not (
                match_region[0] < pos[0] < match_region[2] and match_region[1] < pos[1] < match_region[3]):
            return False
        return pos


def dwarf_retry_phase(phase_name, max_try=2, before_retry_func=None, out_loop_func=None, is_pass=False):
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
                    func(*args, **kwargs)
                except Exception as e:
                    monitor_task_status_v2(phase_name, f"单流程重试: {current_loop},错误:{traceback.format_exc()}")
                    upload_current_catch(f'{phase_name}重试')
                    phase_error_snapshot_list.append(lx_snapshot(AppEnv.get_instance(), "break_app", path=True))
                    continue
                else:
                    break
            else:
                if out_loop_func:
                    phase_error_snapshot_list.reverse()
                    out_loop_func(phase_error_snapshot_list)
                # else:
                if is_pass:
                    monitor_task_status_v2(phase_name, f"{phase_name}内部重试{max_try}次失败,跳过")
                else:
                    lx_break_runloop(f"{phase_name}内部重试{max_try}次失败")
            monitor_task_status_v2(phase_name + "执行耗时", f"{time.strftime('%M:%S', time.gmtime(time.time()-start_time))}")
        return wrapper
    return decorator


def dwarf_img_sort(env, name_order):
    """
    通用图片排序
    :param env:
    :param name_order:
    :return:
    """
    img_list = []
    for file_name in os.listdir(env.logPath):
        if file_name.startswith("adc_result"):
            img_list.append(file_name)
    result = list(filter(lambda x: x.split("_")[2] in name_order, img_list))
    result.sort(key=lambda item: (name_order.index(item.split("_")[2]), item.split("_")[-1].split(".")[0]))
    for item in result:
        new_file_name = "_".join(item.split("_")[0:-1]) + "_" + str(int(time.time() * 1000000)) + "." + item.split(".")[
            -1]
        os.rename(os.path.join(env.logPath, item), os.path.join(env.logPath, new_file_name))


def dwarf_exists_with_img(target_template, source_img):
    """
    图片匹配
    :param target_template:
    :param source_img:
    :return:
    """
    match_pos = target_template.match_in(source_img)
    if match_pos:
        return match_pos
    return False

def dwarf_combin_template(template_img, text_pos_map, img_list, output_name,  row_count=1, template_img_region=(50, 635, 1075, 2199),
                          font_name="AlibabaPuHuiTi-3-85-Bold.ttf", right_text_pos_map={}, multiLine_text_region_map={},
                          font_arguments=(45, "white"), right_font_arguments=(45, "white"), multiline_font_arguments=(30, (109, 84, 66))):
    """
    通用模版拼图
    :param template_img:
    :param text_pos_map:
    :param img_list:
    :param output_name:
    :param row_count:
    :param template_img_region:
    :return:
    """
    font_size, font_color = font_arguments
    right_font_size, right_font_color = right_font_arguments
    multiline_font_size, multiline_font_color = multiline_font_arguments
    # path = os.path.dirname(os.path.abspath(__file__)) + "/"
    # 打开模版图片
    template = Image.open(template_img).convert('RGBA')
    draw = ImageDraw.Draw(template)
    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, font_name)
    font = ImageFont.truetype(font_path, font_size)
    # 设置图片文字，字体类型，以及字体大小
    for text, pos in text_pos_map.items():
        text = text.split("_")[0]
        print(f"写入文字: {text}")
        draw.text(pos, str(text), font=font, fill=font_color)
    font = ImageFont.truetype(font_path, right_font_size)
    for text, pos in right_text_pos_map.items():
        # Get the bounding box of the text
        bbox = draw.textbbox((0, 0), text, font=font)

        # Calculate width and height from the bounding box
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        draw.text((pos[0] - width, pos[1]), str(text), font=font, fill=right_font_color)
    font = ImageFont.truetype(font_path, multiline_font_size)
    for text, region in multiLine_text_region_map.items():
        region_width, region_height = region[2] - region[0], region[3] - region[1]
        # line_font_total = region_width//multiLine_font_size
        current_font_x, current_font_y = region[0], region[1]
        for item in text:
            # text_width, text_height = draw.textsize(item, font=font)
            if item == "\n":
                current_font_x = region[0]
                current_font_y += multiline_font_size
                continue
            if current_font_x + multiline_font_size > region_width:
                current_font_x = region[0]
                current_font_y += multiline_font_size
            draw.text((current_font_x, current_font_y), str(item), font=font, fill=multiline_font_color)
            current_font_x += multiline_font_size
    # 创建一个新的图片用于放置小图
    # 计算图片参数
    if not img_list:
        return
    template_valid_width = template_img_region[2] - template_img_region[0]
    template_valid_height = template_img_region[3] - template_img_region[1]
    if len(img_list) == 1:
        img = img_list[0]
        source_img_height, source_img_width = img_list[0].shape[0:2]
        # 计算宽高比
        if template_valid_width//template_valid_height > source_img_width//source_img_height:
            new_img_width = int(source_img_width * (template_valid_height / source_img_height))
            new_img_height = template_valid_height
        else:
            new_img_width = template_valid_width
            new_img_height = int(source_img_height*(template_valid_width/source_img_width))
        print(new_img_width, new_img_height)
        temp_img_path = os.path.join(ST.LOG_DIR, f"temp.png")
        cv2.imwrite(temp_img_path, img)
        img = Image.open(temp_img_path).convert('RGBA')
        img = img.resize((new_img_width, new_img_height))
        x = int(template_img_region[0] + (template_valid_width - new_img_width)//2)
        y = template_img_region[1]
        print(x, y)
        template.paste(img, (x, y))
    else:
        source_img_height, source_img_width = img_list[0].shape[0:2]
        spacing = 30
        item_image_width = int((template_valid_width - spacing)/row_count - spacing)
        # item_image_height = int(item_image_width*(source_img_height/source_img_width))
        # print(item_image_width, item_image_height)
        print(source_img_width, source_img_height)
        # 对图片进行缩放
        after_resize_imgs = []
        max_item_height = 0
        for img in img_list:
            img_height, img_width = img.shape[0:2]
            item_image_height = int(img_height*(item_image_width/img_width))
            if item_image_height > max_item_height:
                max_item_height = item_image_height
            temp_img_path = os.path.join(ST.LOG_DIR, f"temp.png")
            cv2.imwrite(temp_img_path, img)
            img = Image.open(temp_img_path).convert('RGBA')
            img = img.resize((item_image_width, item_image_height))
            after_resize_imgs.append(img)
        for i, img in enumerate(after_resize_imgs):
            x = template_img_region[0] + (i % row_count) * (item_image_width + spacing) + spacing
            y = template_img_region[1] + (i // row_count) * (max_item_height + spacing) + spacing
            if y + max_item_height > template_img_region[3]:
                break
            template.paste(img, (x, y))
    # 保存结果图片
    template.save(os.path.join(ST.LOG_DIR, f"temp.png"))
    png_image = Image.open(os.path.join(ST.LOG_DIR, f"temp.png")).convert('RGB')
    png_image.save(os.path.join(ST.LOG_DIR, f"{output_name}_{str(int(time.time() * 1000000))}.jpg"), "JPEG")
    monitor_task_status_v2("提示", f"模版拼图完成")


def dwarf_ocr_check(url, output_dir=None, file_name=None, remote_ocr_type=(2, 1, 3),  size=25):
    """
    对ocr识别结果进行原图标记
    :param url: 网络路径或本地路径
    :param output_dir: 输出文件夹
    :param file_name: 文件名
    :param size: 画框文字的大小
    :return:
    """
    ocr_result = []
    ocr_res = ocr_keyword_return_pos_with_image(url, remote_ocr_type=remote_ocr_type)
    if not ocr_res:
        print("ocr_res is None")
        return
    if url.startswith("http"):
        resp = urllib.request.urlopen(url)
        # 读取返回的字节数据
        image_data = resp.read()
        # 将字节数据转换为 NumPy 数组
        image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
        # 将 NumPy 数组解码为 OpenCV 图像格式
        result_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    else:
        result_img = cv2.imread(url)
    height, _ = result_img.shape[0:2]
    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, "AlibabaPuHuiTi-3-85-Bold.ttf")
    font = ImageFont.truetype(font=font_path, size=size)
    image_pil = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    for index, item in enumerate(ocr_res):
        ocr_result.append(item[0])
        draw.rectangle((tuple([int(i) for i in item[1][0]]), tuple([int(i) for i in item[1][2]])), fill=None,
                       outline='red', width=5)
        if item[1][3][1] + 2*size > height:
            draw.text([int(item[1][0][0]), int(item[1][0][1] - 1.5*size)], item[0], font=font,
                      fill=(255, 0, 0))
        else:
            draw.text([int(i) for i in item[1][3]], item[0], font=font,
                  fill=(255, 0, 0))
    result_img = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    file_name = file_name or url.split("/")[-1]
    output_dir = output_dir or ST.LOG_DIR
    cv2.imwrite(os.path.join(output_dir, f"{file_name}.jpg"), result_img)
    return list(set(ocr_result))


def dwarf_get_hsv(img):
    """"
    获取图片主色的hsv
    HSV颜色模型‌由三个参数组成：色相（Hue, H）、饱和度（Saturation, S）和亮度（Value, V）。
    ‌色相（H）‌：表示颜色的种类，取值范围为0°到360°，常见的色相与数值对应关系如下：
    红色：0°
    绿色：120°
    蓝色：240°
    黄色：60°
    青色：180°
    紫色：300°
    它们的补色相差180°‌12。
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

def is_current_screen_vertical():
    """
    判断当前屏幕是否为竖屏
    """
    if G.DEVICE.display_info["orientation"] in [1, 3]:
        return True
    return False

def dwarf_switch_screen_orientation(vertical=True):
    """
    切换屏幕方向
    """
    G.DEVICE.shell("settings put system accelerometer_rotation 0")
    if vertical:
        G.DEVICE.shell("settings put system user_rotation 1")
    else:
        G.DEVICE.shell("settings put system user_rotation 0")

def dwarf_match_text(source_text_list, target_text, degree=0.7):
    """
    相似度匹配文字, 返回匹配度最高的文字
    :param source_text_list:
    :param target_text:
    :param degree:
    :return:
    """
    result_text = None
    last_matcher_ratio = 0
    for item in source_text_list:
        matcher_ratio = difflib.SequenceMatcher(a=item, b=target_text).ratio()
        if matcher_ratio >= degree:
            if matcher_ratio > last_matcher_ratio:
                result_text = item
                last_matcher_ratio = matcher_ratio
    monitor_print(f"dwarf_match_text: {target_text}:{result_text}:{last_matcher_ratio}")
    return result_text

def dwarf_crop_image(img, crop_type="fixed", scale=0.5, crop_pos=None, text_pos=[]):
    """
    快速剪切图片，适用于取图片上下左右中某部分且不要求精准的情况
    :param img: 图片
    :param crop_type: top, bottom, left, right, center
    :param scale: 裁剪比例
    :param text_pos:  [{
            "text": "xxx",
            "pos": (x1, y1, x2, y2),
            "background_color": (r, g, b),
            "text_color": (r, g, b),
            "size": int
        },
        {
            "text": "xxx",
            "pos": (x1, y1, x2, y2),
            "background_color": (r, g, b),
            "text_color": (r, g, b),
            "size": int
        }
        ]
    """
    img_height, img_width = img.shape[0:2]
    p1, p2 = None, None
    if crop_type == "fixed":
        # if not crop_pos:
        #     print("crop_pos is None")
        #     return img
        p1 = (int(crop_pos[0]), int(crop_pos[1]))
        p2 = (int(crop_pos[2]), int(crop_pos[3]))
        # return img[int(crop_pos[1]):int(crop_pos[3]), int(crop_pos[0]):int(crop_pos[2])]
    elif crop_type == "top":
        p1 = (0, 0)
        p2 = (img_width, int(img_height * scale))
    elif crop_type == "bottom":
        p1 = (0, int(img_height * (1 - scale)))
        p2 = (img_width, img_height)
    elif crop_type == "left":
        p1 = (0, 0)
        p2 = (int(img_width * scale), img_height)
    elif crop_type == "right":
        p1 = (int(img_width * (1 - scale)), 0)
        p2 = (img_width, img_height)
    elif crop_type == "center":
        p1 = (int(img_width * (1-scale)/2), int(img_height * (1-scale)/2))
        p2 = (int(img_width * (1-(1-scale)/2)), int(img_height * (1-(1-scale)/2)))
    if p1 and p2:
        cropped_image = img[p1[1]:p2[1], p1[0]:p2[0]]
    else:
        cropped_image = img
    for item_text_pos in text_pos:
        print(item_text_pos)
        print("==============\n")
        size = item_text_pos["size"]
        text_start_x = item_text_pos["pos"][0] - p1[0]
        text_start_y = item_text_pos["pos"][1] - p1[1]
        text_end_x = item_text_pos["pos"][2] - p1[0]
        text_end_y = item_text_pos["pos"][3] - p1[1]
        background_color = item_text_pos["background_color"]
        text_color = item_text_pos["text_color"]
        font_path = os.path.join(os.path.dirname(__file__), "AlibabaPuHuiTi-3-85-Bold.ttf")
        font = ImageFont.truetype(font=font_path, size=size)
        image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        print((text_start_x, text_start_y, text_end_x, text_end_y))
        draw.rectangle((text_start_x, text_start_y, text_end_x, text_end_y), fill=background_color)
        draw.text((text_start_x, text_start_y), item_text_pos["text"], font=font, fill=text_color)
        cropped_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return cropped_image


def dwarf_clean_img(img, clean_region=[]):
    """
    将图片给定区域变成黑色
    :param img:
    :param clean_region:
    :return:
    """
    # 创建一个与图片大小相同的全黑色图片作为背景
    for region in clean_region:
        print(region)
        mask = 255 * np.ones(img.shape, dtype=img.dtype)
        # 定义选定区域的起始点和结束点
        x1, y1 = region[0], region[1]
        x2, y2 = region[2], region[3]
        # 将选定区域以外的区域设置成黑色
        cv2.rectangle(mask, (x1, y1), (x2, y2), (0, 0, 0), thickness=-1)
        # 将原始图片与mask进行按位与操作
        img = cv2.bitwise_and(img, mask)
    return img

def dwarf_exists_plus(template_list, cvstrategy=["tpl"], match_region=None):
    """
    一次match多张图片,返回匹配坐标，避免多次截图，速度更快
    :param template_list:
    :param cvstrategy:
    :return:
    """
    try:
        ST.CVSTRATEGY = cvstrategy
        screen = G.DEVICE.snapshot(filename=None, quality=ST.SNAPSHOT_QUALITY)
        if screen is None:
            G.LOGGING.warning("Screen is None, may be locked")
        else:
            for query in template_list:
                match_pos = query.match_in(screen)
                if match_pos:
                    if match_region and not (match_region[0] < match_pos[0] < match_region[2] and match_region[1] < match_pos[1] < match_region[3]):
                        continue
                    monitor_print(f"dwarf_exists_plus: {query}, {match_pos}")
                    try_log_screen(screen)
                    ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
                    return match_pos
    except TargetNotFoundError:
        monitor_print(f"dwarf_exists_notfound: {template_list}")
    ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
    monitor_print(f"dwarf_exists_notfound: {template_list}")
    return False

def dwarf_combine_images(crop_imgs, result_file_name="temp", one_row_count=4, max_rows_count=20,
                         spacing = 0, spacing_color = (125, 125, 125), is_adjust=True, title=None,
                         title_color=(0, 0, 0), text_size=30):
    """
    将图片合并保存
    :param crop_imgs:
    :param result_file_name:
    :param one_row_count:
    :param max_rows_count:
    """
    result_images = combine_images(crop_imgs, one_row_count=one_row_count, max_rows_count=max_rows_count,
                                   spacing=spacing, spacing_color=spacing_color, is_adjust=is_adjust, title=title,
                                   title_color=title_color, text_size=text_size)
    if result_images:
        for image in result_images:
            img_path = os.path.join(ST.LOG_DIR,
                                    f"{result_file_name}_{str(int(time.time() * 1000000))}.jpg")
            cv2.imwrite(img_path, image)
            time.sleep(0.1)
    return result_images


def dwarf_combine_images_generator(crop_imgs, result_file_name="temp", one_row_count=4, max_rows_count=20,
                         spacing = 0, spacing_color = (125, 125, 125), is_adjust=False, title=None,
                         title_color=(0, 0, 0), text_size=30):
    """
    将图片合并保存,生成器
    :param crop_imgs:
    :param result_file_name:
    :param one_row_count:
    :param max_rows_count:
    """
    result_images = combine_images(crop_imgs, one_row_count=one_row_count, max_rows_count=max_rows_count,
                                   spacing=spacing, spacing_color=spacing_color, is_adjust=is_adjust, title=title,
                                   title_color=title_color, text_size=text_size)
    if result_images:
        for image in result_images:
            img_path = os.path.join(ST.LOG_DIR,
                                    f"{result_file_name}_{str(int(time.time() * 1000000))}.jpg")
            cv2.imwrite(img_path, image)
            time.sleep(0.1)
            yield img_path


def swipe_screenshot_full(swipe_from_pos, swipe_to_pos, check_region=(), crop_pos=(), mask_pos=(), max_swipe_count=20, degree=0.9):
    """
    滑动截图，全屏
    :param swipe_from_pos:
    :param swipe_to_pos:
    :param check_region:
    :return:
    """
    imgs = [lx_snapshot(AppEnv.get_instance(), inspect.currentframe().f_back.f_code.co_name, crop_pos=crop_pos,
                        mask_pos=mask_pos)]
    for current_swipe_count in range(max_swipe_count):
        before_swipe_img = lx_snapshot(AppEnv.get_instance(), f"before_swipe_{current_swipe_count}",
                                       crop_pos=check_region) if check_region else None
        dwarf_swipe(swipe_from_pos, swipe_to_pos)
        sleep(2)
        if check_region:
            current_degree = calculate(lx_snapshot(AppEnv.get_instance(), f"after_swipe_{current_swipe_count}",
                                     crop_pos=check_region), before_swipe_img)
            if current_degree > degree:
                monitor_task_status_v2("swipe_screenshot_full", f"图片重复,相似度: {current_degree}, 阈值: {degree}")
                return imgs
        imgs.append(lx_snapshot(AppEnv.get_instance(), inspect.currentframe().f_back.f_code.co_name, crop_pos=crop_pos,
                                mask_pos=mask_pos))
    return imgs

def click_screenshot_full(click_pos_list, check_region=(), crop_pos=(), degree=0.9, abnormal_pass=True, mask_pos=()):
    """
    点击截图，全屏
    :param swipe_from_pos:
    :param swipe_to_pos:
    :param check_region:
    :return:
    """
    imgs = []
    before_click_img = None
    for idx, pos in enumerate(click_pos_list):
        adb_touch(pos)
        if check_region and before_click_img is not None:
            current_degree = calculate(lx_snapshot(AppEnv.get_instance(), f"after_swipe_{idx}",
                                                   crop_pos=check_region), before_click_img)
            if current_degree > degree:
                monitor_task_status_v2("click_screenshot_full", f"图片重复,相似度: {current_degree}, 阈值: {degree}")
                if abnormal_pass:
                    continue
                return imgs
        before_click_img = lx_snapshot(AppEnv.get_instance(), f"before_click_{idx}",
                                       crop_pos=check_region) if check_region else None
        imgs.append(lx_snapshot(AppEnv.get_instance(), inspect.currentframe().f_back.f_code.co_name, crop_pos=crop_pos, mask_pos=mask_pos))
    return imgs


def dwarf_calculate_plus(img1, img2):
    """
    计算图片相似度
    :param img1:
    :param img2:
    :return:
    """
    if abs(dwarf_get_hsv(img1)[0] - dwarf_get_hsv(img2)[0]) > 0.01:
        return 0
    center_img = dwarf_crop_image(img2, crop_type="center", scale=0.8)
    threshold = 1
    result = cv2.matchTemplate(dwarf_crop_image(center_img, crop_type="left", scale=0.4), img1,
                               cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    threshold = max_val if max_val < threshold else threshold
    result = cv2.matchTemplate(dwarf_crop_image(center_img, crop_type="right", scale=0.4), img1,
                               cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    threshold = max_val if max_val < threshold else threshold
    result = cv2.matchTemplate(dwarf_crop_image(center_img, crop_type="top", scale=0.4), img1, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    threshold = max_val if max_val < threshold else threshold
    result = cv2.matchTemplate(dwarf_crop_image(center_img, crop_type="bottom", scale=0.4), img1,
                               cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    threshold = max_val if max_val < threshold else threshold
    print(f"dwarf_calculate_plus: {threshold}")
    return threshold

def dwarf_write_to_img(img, text, pos=(0, 0), color=(255, 255, 255), font_size=30):
    """
    将文字写入图片
    :param img:
    :param text:
    :param pos:
    :param color:
    :param font_size:
    :return:
    """
    cv2_image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv2_image_rgb)
    draw = ImageDraw.Draw(pil_image)
    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, "AlibabaPuHuiTi-3-85-Bold.ttf")
    font = ImageFont.truetype(font=font_path, size=font_size)
    draw.text(pos, text, font=font, fill=color)
    opencv_image_with_text = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return opencv_image_with_text

def dwarf_show_img(img):
    """
    展示图片
    :param img:
    :return:
    """
    cv2.imshow("dwarf_show_img", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


class SwipeScreenshotGenerator:
    def __init__(self, swipe_from_pos, swipe_to_pos, check_region, crop_data, combine_part_name, degree=0.7, check_repeat_degree=0.7,
                 max_swipe_count=20, quality=None, poco=None):
        self.swipe_from_pos = swipe_from_pos
        self.swipe_to_pos = swipe_to_pos
        self.check_region = check_region
        self.combine_part_name = combine_part_name
        self.hori_count = crop_data[3]
        self.vert_count = crop_data[4]
        self.item_start_x, self.item_start_y = crop_data[0]
        self.item_width = crop_data[2][0] - crop_data[0][0]
        self.item_height = crop_data[2][1] - crop_data[0][1]
        self.item_interval_x = int(((crop_data[1][0] - self.item_start_x) - (self.item_width * self.hori_count)) / (self.hori_count - 1))
        self.item_interval_y = int((crop_data[1][1] - self.item_start_y) - (self.item_height * 2))
        self.bottom_start_y = crop_data[5]
        self.max_rows = crop_data[6]
        self.degree = degree
        self.check_repeat_degree = check_repeat_degree
        self.max_swipe_count = max_swipe_count
        self.quality = quality
        self.poco = poco
        print(f"单个元素，宽:{self.item_width}, 高: {self.item_height}, 水平间隔: {self.item_interval_x}, 垂直间隔: {self.item_interval_y}")

    def swipe_screenshot(self):
        last_img = None
        for swipe_round in range(self.max_swipe_count):
            if swipe_round == 0:
                swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_{swipe_round}",
                                                      quality=self.quality)
                for item_crop_vert_index in range(self.vert_count):
                    crop_y = item_crop_vert_index * (self.item_height + self.item_interval_y) + self.item_start_y
                    for item_crop_hori_idex in range(self.hori_count):
                        crop_x = item_crop_hori_idex * (self.item_width + self.item_interval_x) + self.item_start_x
                        item_img = crop_pos_from_image(swipe_screenshot_source,
                                                       (crop_x, crop_y),
                                                       (crop_x + self.item_width, crop_y + self.item_height))
                        yield item_img
                        last_img = item_img
                continue
            is_bottom = dwarf_swipe_bottom_plus(self.swipe_from_pos, self.swipe_to_pos, self.check_region, self.degree) if not self.poco \
                else dwarf_swipe_bottom_plus_poco(self.poco, self.swipe_from_pos, self.swipe_to_pos, self.check_region, self.degree)
            swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_{swipe_round}",
                                                  quality=self.quality)
            if is_bottom:
                sleep(2)
                # 到底了的截图逻辑, 从下往上截图，对比相似度
                for item_crop_vert_index in range(self.max_rows):
                    crop_y = self.bottom_start_y - (item_crop_vert_index * (self.item_height + self.item_interval_y))
                    for item_crop_hori_idex in range(self.hori_count):
                        crop_x = (self.hori_count - item_crop_hori_idex - 1) * (self.item_width + self.item_interval_x) + self.item_start_x
                        item_img = crop_pos_from_image(swipe_screenshot_source,
                                                       (crop_x, crop_y),
                                                       (crop_x + self.item_width, crop_y + self.item_height))
                        if item_crop_hori_idex == 0:
                            print(f"到底判断相似度： {self.check_repeat_degree}")
                            if calculate(last_img,
                                         item_img) > self.check_repeat_degree:
                                print("图片一样了,结束")
                                return
            for item_crop_vert_index in range(self.vert_count):
                crop_y = item_crop_vert_index * (self.item_height + self.item_interval_y) + self.item_start_y
                for item_crop_hori_idex in range(self.hori_count):
                    crop_x = item_crop_hori_idex * (self.item_width + self.item_interval_x) + self.item_start_x
                    item_img = crop_pos_from_image(swipe_screenshot_source,
                                                   (crop_x, crop_y),
                                                   (crop_x + self.item_width, crop_y + self.item_height))
                    yield item_img


def dwarf_create_blank_image(width, height, color=(0, 0, 0)):
    """
    创建一个指定背景颜色的空图片。

    参数:
    - width: 图片的宽度。
    - height: 图片的高度。
    - color: 图片背景颜色，格式为(B, G, R)。

    返回:
    - img: 创建的图片。
    """
    # 创建一个指定颜色的空白图像
    image = np.zeros((height, width, 3), dtype=np.uint8)
    # 设置背景颜色
    image[:] = color
    return image


def dwarf_parse_remote_properties(properties, property_name_list: list):
    """预解析多子属性"""
    results = {}
    for item in json.loads(properties):
        if item["propertyName"] in property_name_list:
            if item.get("optionList", []):
                results[item["propertyName"]] = item["optionList"]
            elif item.get("gameProperties", []):
                results[item["propertyName"]] = [i.get("propertyValue") for i in
                                                item.get("gameProperties", [])]
    return results

def dwarf_build_properties(remote_properties, information_map, result_data: list, key_list=[], type=0):
    """
    构建多子属性
    :param remote_properties: 远程拉下来的数据已经json.loads
    :param information_map: 本地保存的数据
    :param result_data: 源数据
    :param key_list:
    :param type: type=0: 单个属性(等级), type=1:  枚举不带图(角色) type=2: 多子带图片
    :return:
    """
    done_key_list = []
    for item_properties in remote_properties:
        if item_properties.get("propertyName", "") in key_list:
            key = item_properties.get("propertyName", "")
            if key not in information_map:
                monitor_print(f"dwarf_build_properties: {key} 不在information_map")
                continue
            done_key_list.append(key)
            if type == 0:
                result_data.append({
                    "propertyId": item_properties.get("propertyId", None),
                    "value": information_map[key]
                })
            elif type == 1:
                if option_list := item_properties.get("optionList", []):
                    if isinstance(information_map[key], str):
                        if information_map[key] in option_list:
                            result_data.append({
                                "propertyId": item_properties.get("propertyId", None),
                                "value": information_map[key]
                            })
                        else:
                            monitor_print(f"dwarf_build_properties: {information_map[key]} 不在属性库")
                        continue
                    elif isinstance(information_map[key], list) or \
                            isinstance(information_map[key], tuple) or \
                            isinstance(information_map[key], set):
                        result_match = []
                        for item_name in information_map[key]:
                            if item_name in option_list:
                                result_match.append(item_name)
                            else:
                                monitor_print(f"dwarf_build_properties: {item_name} 不在属性库")
                        result_data.append({
                            "propertyId": item_properties.get("propertyId", None),
                            "value": ",".join(result_match) if result_match else "无"
                        })
                    else:
                        raise Exception("information_map[key] is not str or list or tuple or set")
                elif gameProperties := item_properties.get("gameProperties", []):
                    item_results = {
                        "propertyId": item_properties.get("propertyId", None),
                        "useGameProperty": True,
                        "gameProperties": []
                    }
                    if isinstance(information_map[key], str):
                        for game_properties in gameProperties:
                            if game_properties.get("propertyValue") == information_map[key]:
                                item_results_game_properties = {
                                    "value": game_properties.get("propertyValue", ""),
                                    "propertyExt": game_properties.get("propertyExt", ""),
                                    "childProperties": []
                                }
                                for childProperties in game_properties.get("childProperties", []):
                                    item_results_game_properties["childProperties"].append({
                                        "propertyId": childProperties["propertyId"],
                                        "propertyExt": childProperties["propertyValues"][0]["propertyExt"],
                                        "value": childProperties["propertyValues"][0]["propertyValue"]
                                    })
                                item_results["gameProperties"].append(item_results_game_properties)
                                break
                    elif isinstance(information_map[key], list) or \
                            isinstance(information_map[key], tuple) or \
                                     isinstance(information_map[key], set):
                        for item_name in information_map[key]:
                            for game_properties in item_properties.get("gameProperties", []):
                                if game_properties.get("propertyValue") == item_name:
                                    item_results_game_properties = {
                                        "value": game_properties.get("propertyValue", ""),
                                        "propertyExt": game_properties.get("propertyExt", ""),
                                        "childProperties": []
                                   }
                                    for childProperties in game_properties.get("childProperties", []):
                                        item_results_game_properties["childProperties"].append({
                                            "propertyId": childProperties["propertyId"],
                                            "propertyExt": childProperties["propertyValues"][0]["propertyExt"],
                                            "value": childProperties["propertyValues"][0]["propertyValue"]
                                        })
                                    item_results["gameProperties"].append(item_results_game_properties)
                                    break
                    else:
                        raise Exception("information_map[key] is not str or list or tuple or set")
                    result_data.append(item_results)
            elif type == 2:
                    item_results = {
                        "propertyId": item_properties.get("propertyId", None),
                        "useGameProperty": True,
                        "gameProperties": []
                    }
                    if isinstance(information_map[key], list):
                        for item_resource_data in information_map[key]:
                            name = item_resource_data["name"]
                            oss_url = item_resource_data["oss"]
                            for game_properties in item_properties.get("gameProperties", []):
                                if game_properties.get("propertyValue") == name:
                                    item_result_data = {
                                        "value": game_properties.get("propertyValue", ""),
                                        "image": oss_url[0],
                                        "propertyExt": game_properties.get("propertyExt", ""),
                                        "childProperties": [],
                                    }
                                    for childProperties in game_properties.get("childProperties", []):
                                        item_result_data["childProperties"].append({
                                            "propertyId": childProperties["propertyId"],
                                            "propertyExt": childProperties["propertyValues"][0]["propertyExt"],
                                            "value": childProperties["propertyValues"][0]["propertyValue"]
                                        })
                                    item_results["gameProperties"].append(item_result_data)
                                    break
                    else:
                        raise Exception("information_map[key] is not list")
                    result_data.append(item_results)
    for key in key_list:
        if key not in done_key_list:
            monitor_print(f"dwarf_build_properties: {key} 不在属性库")


def dwarf_upload_propreties_with_data(game_id, platform, property_name, property_value, cdn_url_list=[], type=0):
    """
    属性回填
    :param game_id: 游戏ID eg:12697
    :param platform: 渠道 eg: giant
    :param property_name: eg: 六星角色
    :param property_value: eg: 李火旺
    :param cdn_url_list:
    :param type:
    :return:
    """
    try:
        if not cdn_url_list:
            name = property_name + '_' + property_value + "_" + str(int(time.time() * 1000000)) + '.jpg'
            snapshot(filename=name, msg="get a snapshot.")
            image_path = AppEnv.get_instance().logPath + '/' + name
            _, cdn_url_list = upload_jym_oss_with_pathes([image_path])
        if type == 0:
            upload_propreties_with_data(game_id, platform, [
                                {
                                    "childNodes": [],
                                    "propertyName": property_name,
                                    "propertyValueName": property_value
                                }
                            ], [cdn_url_list],
                                                    taskIdList=[str(AppEnv.get_instance().taskId)], addParams=True,
                                                    isFromCollectTask=True, isNeedShenpi=True)
    except Exception as e:
        monitor_print(f"dwarf_upload_propreties_with_data: {e}")


def generate_pos_list(start_x, start_y, interval_x, interval_y, count_x, count_y):
    """
    生成坐标列表
    :param start_x:
    :param start_y:
    :param interval_x:
    :param interval_y:
    :param count_x: 一排x个
    :param count_y: 一排y个
    :return:
    """
    pos_list = []
    for i in range(count_y):
        for j in range(count_x):
            pos_list.append((start_x + j * interval_x, start_y + i * interval_y))
    return pos_list


def swipe_screenshot_by_count(swipe_from_pos, swipe_to_pos, crop_data, count=0):
    """
    :param swipe_from_pos: 滑动开始
    :param swipe_to_pos: 滑动结束
    :param crop_data: [前两排左上坐标(x,y)， 前两排右下坐标(x,y), 单个右下角坐标(x,y),  一排几个, 一次截几排, 拉到底最后一排y坐标]
    :param combine_part_name: 图片名
    :param check_normal_image_func: 检查图片是否正常
    :param check_normal_image_continue: 不正常是否继续
    :param degree: 拉到极限图片对比相似度阀值，默认0.7
    :return:
    """
    # 滑动数据
    img_list = []
    hori_count = crop_data[3]
    vert_count = crop_data[4]
    item_start_x, item_start_y = crop_data[0]
    item_width = crop_data[2][0] -crop_data[0][0]
    item_height = crop_data[2][1] -crop_data[0][1]
    item_interval_x = int(((crop_data[1][0]-item_start_x) - (item_width*hori_count))/(hori_count-1))
    item_interval_y = int((crop_data[1][1]-item_start_y) - (item_height*2))
    bottom_start_y = crop_data[5]
    monitor_print(f"swipe_screenshot_by_count,单个元素,宽:{item_width}, 高: {item_height}, 水平间隔: {item_interval_x}, 垂直间隔: {item_interval_y}")
    # 计算滑动次数， 最后一次滑动参数
    swipe_count = int(count // (hori_count*vert_count)) - 1 if count % hori_count else int(count // (hori_count*vert_count))
    last_count = count % (hori_count*vert_count) if count % (hori_count*vert_count) else hori_count*vert_count
    bottom_start_y = bottom_start_y - (last_count//hori_count)*(item_height+item_interval_y) if last_count % hori_count != 0 else\
        bottom_start_y - ((last_count//hori_count)-1)*(item_height+item_interval_y)
    monitor_print(f"swipe_screenshot_by_count: count: {count} swipe_count: {swipe_count}, last_count: {last_count}, bottom_start_y: {bottom_start_y}")
    # 处理第一页
    swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_0", quality=99)
    if swipe_count < 1:
        for idx in range(count):
            crop_x = (idx % hori_count) * (item_width + item_interval_x) + item_start_x
            crop_y = (idx//hori_count) * (item_height + item_interval_y) + item_start_y
            item_img = dwarf_crop_image(swipe_screenshot_source, crop_type="fixed", crop_pos=(crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            img_list.append(item_img)
        return img_list
    else:
        for idx in range(hori_count*vert_count):
            crop_x = (idx % hori_count) * (item_width + item_interval_x) + item_start_x
            crop_y = (idx//hori_count) * (item_height + item_interval_y) + item_start_y
            print(f"crop_x: {crop_x}, crop_y: {crop_y}")
            item_img = dwarf_crop_image(swipe_screenshot_source, crop_type="fixed", crop_pos=(crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            img_list.append(item_img)
    for swipe_round in range(swipe_count):
        dwarf_swipe(swipe_from_pos, swipe_to_pos)
        sleep(1)
        swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_{swipe_round+1}", quality=99)
        for idx in range(hori_count*vert_count if swipe_round < swipe_count-1 else last_count):
            crop_x = (idx % hori_count) * (item_width + item_interval_x) + item_start_x
            crop_y = (idx//hori_count) * (item_height + item_interval_y) + item_start_y if swipe_round < swipe_count-1 \
                else (idx//hori_count) * (item_height + item_interval_y) + bottom_start_y
            item_img = dwarf_crop_image(swipe_screenshot_source, crop_type="fixed", crop_pos=(crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            img_list.append(item_img)
    return img_list


def dwarf_ocr_mack(url, output_dir=None, part_name=None, data=[], keys=[], is_upload=False, size=25):
    """
    easRequest 返回的数据进行原图标记
    :param data: ocr识别返回参数 ["message"]["imagePropertyValues"][0]["value"]
    :param url: 网络路径或本地路径
    :param output_dir: 输出文件夹
    :param part_name: 文件名
    :param keys: 响应数据中的属性
    :param size: 画框文字的大小
    :return:
    """
    # data = data["message"]["imagePropertyValues"][0]["value"]
    # 使用 urllib 打开 URL
    # launchType = AppEnv.get_instance().launchType
    # if launchType != 'localtest':
    #     return
    file_name = None
    if part_name:
        file_name = part_name + "_" + str(int(time.time() * 1000000)) + ".jpg"
    print(f"dwarf_ocr_mack, url: {file_name}, {part_name}")
    output_dir = output_dir if output_dir else ST.LOG_DIR
    if url.startswith("http"):
        resp = requests.get(url)
        # 读取返回的字节数据
        image_data = resp.content
        # 将字节数据转换为 NumPy 数组
        image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
        # 将 NumPy 数组解码为 OpenCV 图像格式
        result_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        file_name = file_name or url.split("/")[-1]
    else:
        result_img = cv2.imread(url)
        file_name = file_name or os.file.basename(url)
    print(f"dwarf_ocr_mack, file_name: {file_name}")
    font_path = os.path.join(os.path.dirname(__file__), "AlibabaPuHuiTi-3-85-Bold.ttf")
    font = ImageFont.truetype(font=font_path, size=size)
    image_pil = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    height, _ = result_img.shape[0:2]
    for index, item in enumerate(data):
        text = "_".join([str(item[i]) for i in keys])
        if "box" in item:
            draw.rectangle((tuple([int(i) for i in item["box"][0]]), tuple([int(i) for i in item["box"][2]])), fill=None,
                       outline='red', width=5)
            if item["box"][3][1] + 2 * size > height:
                draw.text([int(item["box"][0][0]), int(item["box"][0][1] - 1.5 * size)], text, font=font,
                          fill=(255, 0, 0))
            else:
                draw.text([int(i) for i in item["box"][3]], text, font=font,
                          fill=(255, 0, 0))
        else:
            draw.text((10 * (index + 1), 10), text, font=font,
                          fill=(255, 0, 0))
    result_img = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    local_path = os.path.join(output_dir, file_name)
    cv2.imwrite(local_path, result_img)
    cdn_url = None
    print(local_path)
    if is_upload:
        _, cdn_url = upload_img_to_oss(local_path)
    return cdn_url


def swipe_screenshot_by_count_generator(swipe_from_pos, swipe_to_pos, crop_data, count=0, duration=0.8):
    """
    :param swipe_from_pos: 滑动开始
    :param swipe_to_pos: 滑动结束
    :param crop_data: [前两排左上坐标(x,y)， 前两排右下坐标(x,y), 单个右下角坐标(x,y),  一排几个, 一次截几排, 拉到底最后一排y坐标]
    :param combine_part_name: 图片名
    :param check_normal_image_func: 检查图片是否正常
    :param check_normal_image_continue: 不正常是否继续
    :param degree: 拉到极限图片对比相似度阀值，默认0.7
    :return:
    """
    # 滑动数据
    hori_count = crop_data[3]
    vert_count = crop_data[4]
    item_start_x, item_start_y = crop_data[0]
    item_width = crop_data[2][0] -crop_data[0][0]
    item_height = crop_data[2][1] -crop_data[0][1]
    item_interval_x = int(((crop_data[1][0]-item_start_x) - (item_width*hori_count))/(hori_count-1))
    item_interval_y = int((crop_data[1][1]-item_start_y) - (item_height*2))
    bottom_start_y = crop_data[5]
    monitor_print(f"swipe_screenshot_by_count,单个元素,宽:{item_width}, 高: {item_height}, 水平间隔: {item_interval_x}, 垂直间隔: {item_interval_y}")
    # 计算滑动次数， 最后一次滑动参数
    swipe_count = int(count // (hori_count*vert_count)) - 1 if count % (hori_count*vert_count) == 0 else int(count // (hori_count*vert_count))
    last_count = count % (hori_count*vert_count) if count % (hori_count*vert_count) else hori_count*vert_count
    bottom_start_y = bottom_start_y - (last_count//hori_count)*(item_height+item_interval_y) if last_count % hori_count != 0 else\
        bottom_start_y - ((last_count//hori_count)-1)*(item_height+item_interval_y)
    monitor_print(f"swipe_screenshot_by_count: count: {count} swipe_count: {swipe_count}, last_count: {last_count}, bottom_start_y: {bottom_start_y}")
    # 处理第一页
    swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_0", quality=99)
    if swipe_count < 1:
        for idx in range(count):
            crop_x = (idx % hori_count) * (item_width + item_interval_x) + item_start_x
            crop_y = (idx//hori_count) * (item_height + item_interval_y) + item_start_y
            item_img = dwarf_crop_image(swipe_screenshot_source, crop_type="fixed", crop_pos=(crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            yield item_img
    else:
        for idx in range(hori_count*vert_count):
            crop_x = (idx % hori_count) * (item_width + item_interval_x) + item_start_x
            crop_y = (idx//hori_count) * (item_height + item_interval_y) + item_start_y
            item_img = dwarf_crop_image(swipe_screenshot_source, crop_type="fixed", crop_pos=(crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            yield item_img
    for swipe_round in range(swipe_count):
        dwarf_swipe(swipe_from_pos, swipe_to_pos, duration=duration)
        sleep(1)
        swipe_screenshot_source = lx_snapshot(AppEnv.get_instance(), f"swipe_screenshot_source_{swipe_round+1}", quality=99)
        for idx in range(hori_count*vert_count if swipe_round < swipe_count-1 else last_count):
            crop_x = (idx % hori_count) * (item_width + item_interval_x) + item_start_x
            crop_y = (idx//hori_count) * (item_height + item_interval_y) + item_start_y if swipe_round < swipe_count-1 \
                else (idx//hori_count) * (item_height + item_interval_y) + bottom_start_y
            item_img = dwarf_crop_image(swipe_screenshot_source, crop_type="fixed", crop_pos=(crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            yield item_img


def upload_flle_to_oss(file_path, filename=None):
    """
    上传文件到oss
    :param file_path:
    :param filename:
    :return:
    """
    # print("==================================")
    # print(img_path)
    sig_result = get_jym_oss_signature()
    print(f"---upload_img_to_oss:{sig_result}")

    final_sig_result_object = None
    is_new_api = True
    if is_new_api:
        final_sig_result_object = sig_result
    else:
        final_sig_result_json = sig_result['data']
        final_sig_result_object = json.loads(final_sig_result_json)

    # final_sig_result_json = sig_result['data']
    # final_sig_result_object = json.loads(final_sig_result_json)
    final_sig_result = final_sig_result_object['result']
    if final_sig_result is None or len(final_sig_result) == 0:
        return None
    access_id = final_sig_result['accessId']
    policy = final_sig_result['policy']
    signature = final_sig_result['signature']
    host = final_sig_result['host']
    dir = final_sig_result['dir']
    # 构建OSS上传URL
    url = host
    oss_path_list = []
    cdn_url_list = []
    # 构建文件表单数据
    files = {
        'file': open(file_path, "rb"),
    }
    # 设置请求参数
    object_name = filename or f"{dir}{filename or file_path.split('/')[-1]}"
    params = {
        'OSSAccessKeyId': access_id,
        'policy': policy,
        'Signature': signature,
        'key': object_name,
        'success_action_status': '200',
    }
    response = requests.post(url, data=params, files=files)
    if response.status_code == 200:
        oss_path = '/' + object_name
        cdn_url = 'https://static.jiaoyimao.com' + oss_path
    else:
        retry_response = requests.post(url, data=params, files=files)
        if retry_response.status_code == 200:
            oss_path = '/' + object_name
            cdn_url = 'https://static.jiaoyimao.com' + oss_path
            return oss_path, cdn_url
        else:
            monitor_print(f"上传图片错误: {retry_response.status_code}")
            return None, None
    monitor_print(f"----upload_img_to_oss:{oss_path_list}, {cdn_url_list}")
    return oss_path, cdn_url


class FreeDraw:
    def __init__(self, width, height, background_color, start_color=None, end_color=None, direction="horizontal"):
        self.empty_image = Image.new('RGBA', (width, height), background_color)
        self.draw = ImageDraw.Draw(self.empty_image)
        if start_color and end_color:
            if direction == "horizontal":
                for x in range(width):
                    ratio = x / (width - 1)
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                    a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio)
                    self.draw.line([(x, 0), (x, height)], fill=(r, g, b, a))
            elif direction == "vertical":
                for y in range(height):
                    ratio = y / (height - 1)
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                    a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio)
                    self.draw.line([(0, y), (width, y)], fill=(r, g, b, a))

            elif direction == "diagonal":
                for i in range(max(width, height)):
                    ratio = i / max(width, height)
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                    a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio)
                    self.draw.line([(i, 0), (width - i, height)], fill=(r, g, b, a))

    def get_text_size(self, text, font):
        """
        获取文字尺寸
        :param text:
        :param font:
        :return:
        """
        box = self.draw.textbbox((0, 0), text, font=font)
        return box[2] - box[0], box[3] - box[1]

    def text(self, xy, text, *args, **kwargs):
        """
        固定位置写文字
        :param start_pos:
        :param text:
        :param font:
        :param color:
        :return:
        """
        font = kwargs.get("font")
        x, y = xy
        if font.size % 5 == 0:
            y = y - font.size//5
        else:
            y = y - (font.size // 5) + 1
        self.draw.text((x, y), text, *args, **kwargs)

    def text_area(self, box_pos, text, justify_content="center", interval=15, background_color=None, *args,  **kwargs):
        """
        区域内写文字
        :param box_pos:
        :param text:
        :param justify_content:
        :param args:
        :param kwargs:
        :return:
        """
        box_center_x = (box_pos[2] - box_pos[0])//2 + box_pos[0]
        box_center_y = (box_pos[3] - box_pos[1])//2 + box_pos[1]
        if background_color is not None:
            self.draw.rectangle((box_pos[0], box_pos[1], box_pos[2], box_pos[3]), fill=background_color)
        font = kwargs.get("font")
        font_width, font_height = self.get_text_size(text, font)
        if justify_content == "center":
            self.text((box_center_x - (font_width//2), box_center_y - (font_height//2)), text, *args, **kwargs)
        elif justify_content == "left":
            self.text((box_pos[0] + interval, box_center_y - (font_height//2)), text, *args, **kwargs)
        elif justify_content == "right":
            self.text((box_pos[2] - interval - font_width, box_center_y - (font_height//2)), text, *args, **kwargs)

    def line_text_line(self, start_pos, end_pos, text, font, fill=(135, 105, 64), text_fill=(255, 255,255), interval=15):
        """
        横线分割线 文字
        :param start_pos:
        :param end_pos:
        :param text:
        :param font:
        :param interval:
        :return:
        """
        font_width, font_height = self.get_text_size(text, font)
        line_width = (end_pos[0] - start_pos[0] - interval*4 - font_width)//2
        self.draw.line([(start_pos[0] + interval, start_pos[1]), (start_pos[0] + interval + line_width, start_pos[1])], fill=fill, width=2)
        self.draw.line([(end_pos[0] - interval - line_width, end_pos[1]), (end_pos[0] - interval, end_pos[1])], fill=fill, width=2)
        self.text(((end_pos[0] - start_pos[0])//2 - font_width//2 + start_pos[0], start_pos[1] - font_height//2), text, font=font, fill=text_fill)
        # print((end_pos[0] - start_pos[0])//2 - font_width//2, start_pos[1] - font_height//2)
        # print(self.draw.textbbox(((end_pos[0] - start_pos[0])//2 - font_width//2, start_pos[1] - font_height//2), text, font=font))

    def paste_img(self, img_path, box_pos, interval=0):
        """
        粘贴图片
        :param img_path:
        :param box_pos:
        :param interval:
        :return:
        """
        print(img_path)
        if isinstance(img_path, str):
            if img_path.startswith("http"):
                response = requests.get(img_path)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(img_path)
        elif isinstance(img_path, Image.Image):
            img = img_path
        box_width, box_height = box_pos[2] - box_pos[0], box_pos[3] - box_pos[1]
        img = img.resize((box_width-2*interval, box_height-2*interval))
        self.empty_image.paste(img, (box_pos[0] + interval, box_pos[1] + interval))

    def paste_imgs(self, img_path_list, box_pos, interval=0):
        """
        粘贴图片
        :param img_path:
        :param box_pos:
        :param interval:
        :return:
        """
        box_width, box_height = box_pos[2] - box_pos[0], box_pos[3] - box_pos[1]
        item_img_width = (box_width - len(img_path_list) * interval - interval) // len(img_path_list)
        start_x, start_y = box_pos[0] + interval, box_pos[1] + interval
        max_img_height = 0
        for img_path in img_path_list:
            # print(img_path)
            if isinstance(img_path, numpy.ndarray):
                # 将 BGR 转换为 RGB
                rgb_image = cv2.cvtColor(img_path, cv2.COLOR_BGR2RGB)
                # 转换为 PIL 的 Image 对象
                img = Image.fromarray(rgb_image)
            elif isinstance(img_path, str):
                if img_path.startswith("http"):
                    response = requests.get(img_path)
                    img = Image.open(BytesIO(response.content))
                else:
                    img = Image.open(img_path)
            elif isinstance(img_path, Image.Image):
                img = img_path
            else:
                start_x += item_img_width + interval
                if item_img_height > max_img_height:
                    max_img_height = item_img_height

            source_img_width, source_img_height = img.size
            item_img_height = item_img_width * source_img_height // source_img_width
            img = img.resize((item_img_width, item_img_height))
            self.empty_image.paste(img, (start_x, start_y))
            start_x += item_img_width + interval
            if item_img_height > max_img_height:
                max_img_height = item_img_height
        return max_img_height

    def add_full_text_watermark(self, text="Sample Watermark",
                                interval=100, angle=45, font_size=70,
                                color=(255, 255, 255, 100), font_name="AlibabaPuHuiTi-3-85-Bold.ttf"):
        # 打开图片
        width, height = self.empty_image.size

        # 创建透明水印层
        watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)

        # 加载字体
        try:
            current_dir = os.path.dirname(__file__)
            font_path = os.path.join(current_dir, font_name)
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # 计算文字尺寸
        box = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = box[2] - box[0], box[3] - box[1]
        text_height += text_height//3
        text_box = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_box)
        text_draw.text((0, 0), text, font=font, fill=color)
        text_box = text_box.rotate(angle, expand=1)  # 旋转文字

        # 铺满水印
        for x in range(0, width, text_box.width + interval):
            for y in range(0, height, text_box.height // 2 + interval):
                pos = (x - text_box.width // 2, y - text_box.height // 2)
                print(pos)
                watermark_layer.paste(text_box, pos, text_box)

        # 合并原图和水印层
        self.empty_image = Image.alpha_composite(self.empty_image, watermark_layer)
        self.draw = ImageDraw.Draw(self.empty_image)
        # 转换为 RGB 模式并保存为 JPEG
        # combined.save("output.jpg")
        # self.empty_image = self.empty_image.convert("RGB")
        # combined.convert("RGB").save(output_path, "JPEG")

    def add_image_to_image(self, image_path, position=(50, 50), size=100):
        img = Image.open(image_path).convert("RGBA")
        img = img.resize((size, size))
        self.empty_image.paste(img, position)



    def save(self, width=None, height=None, output_path=None):
        if output_path is None:
            output_path = "output.png"
        if width and height:
            self.empty_image = self.empty_image.crop((0, 0, width, height))
        self.empty_image.convert("RGB").save(output_path)



def get_clipboard_with_clipper(current_package_name, check_template=None, timeout=5):
    data_content = ""
    start_app("ca.zgrs.clipper")
    sleep(2)
    text = shell('am broadcast -a clipper.get')
    print(text)
    match = re.search(r'data="(.*)"', text)
    if match:
        data_content = match.group(1)
    # start_app(current_package_name)
    # shell(f"am start -n {current_package_name}")
    shell("input keyevent KEYCODE_BACK")
    if check_template:
        if dwarf_exists(check_template, timeout=timeout):
            return data_content
        raise Exception("返回应用超时")
    return data_content


def dwarf_qufu_backcall(qufu_img, qufu_name, max_count=5):
    """区服回填"""
    if not qufu_name:
        return {}
    from airtest.core.helper import using
    using("../utility/biz_foundation.air")
    from biz_foundation import DomainServerModel, get_domain_and_server_info
    _, url = upload_img_to_oss(qufu_img)
    monitor_print(f'---dwarf_qufu_backcall: {qufu_name}')
    model = DomainServerModel(qufu_name, '', max_count=max_count, image_list=[url])
    seller_info = get_domain_and_server_info(model)
    return seller_info


from PIL import Image, ImageDraw, ImageFont

def add_full_text_watermark(image_path, output_path, text="Sample Watermark",
                            interval=100, angle=45, font_size=40,
                            color=(255, 255, 255, 100), font_name="AlibabaPuHuiTi-3-85-Bold.ttf"):
    # 打开图片
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    # 创建透明水印层
    watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    # 加载字体
    try:
        current_dir = os.path.dirname(__file__)
        font_path = os.path.join(current_dir, font_name)
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 计算文字尺寸
    text_width, text_height = draw.textsize(text, font=font)
    text_box = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_box)
    text_draw.text((0, 0), text, font=font, fill=color)
    text_box = text_box.rotate(angle, expand=1)  # 旋转文字

    # 铺满水印
    for x in range(0, width, interval):
        for y in range(0, height, interval):
            pos = (x - text_box.width // 2, y - text_box.height // 2)
            watermark_layer.paste(text_box, pos, text_box)

    # 合并原图和水印层
    combined = Image.alpha_composite(img, watermark_layer)
    combined.convert("RGB").save(output_path, "JPEG")


def crop_line_imgs_from_current_screen(crop_region_pos, row_count=1, col_count=1):
    """
    从当前屏幕裁剪出行
    :param crop_region_pos:
    :param row_count:
    :param col_count:
    :return:
    """
    start_x, start_y = crop_region_pos[0], crop_region_pos[1]
    end_x, end_y = crop_region_pos[2], crop_region_pos[3]
    # 单个width, 单个height
    item_width, item_height = (end_x - start_x) / row_count, (end_y - start_y) / col_count
    imgs = []
    current_screen = lx_snapshot(AppEnv.get_instance().scriptEnv, "crop_line_imgs_from_current_screen")
    for i in range(row_count):
        for j in range(col_count):
            img = dwarf_crop_image(current_screen, crop_type="fixed",
                                   crop_pos=(start_x + item_width * i, start_y + item_height * j,
                                             start_x + item_width * (i + 1), start_y + item_height * (j + 1)))
            imgs.append(img)
    return imgs



def crop_img_from_fullimg(source_img, crop_data, check_normal_image_func=None, check_normal_image_continue=False):
    """
    :param start_pos:
    :param end_pos:
    :param crop_data: [前两排左上坐标(x,y)， 前两排右下坐标(x,y), 单个右下角坐标(x,y),  一排几个, 一次截几排]
    :return:
    """
    # 滑动数据
    img_list = []
    hori_count = crop_data[3]
    vert_count = crop_data[4]
    item_start_x, item_start_y = crop_data[0]
    item_width = crop_data[2][0] -crop_data[0][0]
    item_height = crop_data[2][1] -crop_data[0][1]
    item_interval_x = int(((crop_data[1][0]-item_start_x) - (item_width*hori_count))/(hori_count-1))
    item_interval_y = int((crop_data[1][1]-item_start_y) - (item_height*2))
    print(f"单个元素，宽:{item_width}, 高: {item_height}, 水平间隔: {item_interval_x}, 垂直间隔: {item_interval_y}")
    for item_crop_vert_index in range(vert_count):
        crop_y = item_crop_vert_index * (item_height + item_interval_y) + item_start_y
        for item_crop_hori_idex in range(hori_count):
            crop_x = item_crop_hori_idex * (item_width + item_interval_x) + item_start_x
            print((crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            item_img = dwarf_crop_image(source_img, crop_type="fixed", crop_pos=(crop_x, crop_y, crop_x + item_width, crop_y + item_height))
            if check_normal_image_func and not check_normal_image_func(item_img):
                if not check_normal_image_continue:
                    return img_list
                continue
            img_list.append(item_img)
    return img_list


def captcha_ai(crop_pos, reco_type="图形验证码", captcha_type="默认"):
    """
    基于文斌接口的验证码
    :param crop_pos:
    :param reco_type:拼图验证码 文字验证码 图形验证码
    :param captcha_type:
    :return:
    """
    env = AppEnv.get_instance()
    _, cdn_url = upload_img_to_oss(lx_snapshot(env, "captcha_ai", crop_pos=crop_pos))

    params = {}
    params['requestId'] = str(int(time.time() * 1000000))
    params['imageUrl'] = cdn_url
    params['recoType'] = reco_type
    params['captchaType'] = captcha_type

    url = "/api/predict/lingxialgo_ocr_service_pre"
    if env.scriptEnv == 'local':
        url = "/api/predict/lingxialgo_ocr_service_pre"
    elif env.scriptEnv == 'prod':
        url = "/api/predict/lingxialgo_vision_ocr"

    response = enhanced_easrequest(url, params, type=2)
    monitor_print(f"---captcha_ai_response: {response}, url: {cdn_url}")
    if response.get("code") != 200:
        monitor_print(f"---captcha_ai_error_response: {response.get('message')}")
        return []
    data = response.get("message", {})
    if data.get("status", 0) != 1:
        monitor_print(f"---captcha_ai_error_response: {data.get('failReason')}")
        return []
    for item in data.get("data", []):
        box = item.get("box")
        item["center_pos"] = (int((box[0][0] + box[1][0]) / 2 + crop_pos[0]), int((box[0][1] + box[3][1]) / 2 + crop_pos[1]))
    return data.get("data")

def captcha_agent_ai(crop_pos, reco_type="agent", task="米哈游物品验证码"):
    """
    基于文斌接口的验证码 特殊
    :param crop_pos:
    :param reco_type:
    :param task:
    :return:
    """
    env = AppEnv.get_instance()
    _, cdn_url = upload_img_to_oss(lx_snapshot(env, "captcha_ai", crop_pos=crop_pos))
    params = {}
    params['requestId'] = str(int(time.time() * 1000000))
    params['recoType'] = reco_type
    params['task'] = task
    params['imageUrl'] = cdn_url


    url = "/api/predict/lingxialgo_vision_agent_pre"
    if env.scriptEnv == 'local':
        url = "/api/predict/lingxialgo_vision_agent_pre"
    elif env.scriptEnv == 'prod':
        url = "/api/predict/lingxialgo_vision_agent"

    response = enhanced_easrequest(url, params, type=2)
    monitor_print(f"---captcha_agent_ai: {response}, url: {cdn_url}")
    if response.get("code") != 200:
        monitor_print(f"---captcha_ai_error_response: {response.get('message')}")
        return []
    data = response.get("message", {})
    if data.get("status", 0) != 1:
        monitor_print(f"---captcha_ai_error_response: {data.get('failReason')}")
        return []
    for item in data.get("data", []):
        box = item.get("box")
        item["center_pos"] = (int((box[0][0] + box[1][0]) / 2 + crop_pos[0]), int((box[0][1] + box[3][1]) / 2 + crop_pos[1]))
    return data.get("data")

def captcha_slider_ai(crop_pos, swipe_start_pos, offset=1, propertyId="验证码", recoType="拼图验证码"):
    """
    验证码识别，基于文斌接口, 滑块
    :param crop_pos:
    :param swipe_start_pos:
    :param offset:
    :param propertyId:
    :param recoType:
    :return:
    """
    scriptEnv = AppEnv.get_instance().scriptEnv
    risk_path = '/api/predict/lingxialgo_vision_adc_pre'
    if scriptEnv == 'local':
        risk_path = '/api/predict/lingxialgo_vision_adc_pre'
    elif scriptEnv == 'pre':
        risk_path = '/api/predict/lingxialgo_vision_adc '
    elif scriptEnv == 'prod':
        risk_path = '/api/predict/lingxialgo_vision_adc '

    _, cnd_url = upload_img_to_oss(
        lx_snapshot(AppEnv.get_instance(), "adc_catch_验证码", crop_pos=crop_pos))
    resData = {
        'imageProperties': [{"propertyId": propertyId}],
        'requestId': str(int(time.time() * 1000000)),
        'imageUrl': cnd_url,
        'recoType': recoType
    }
    data = easRequest(risk_path, resData)
    monitor_print(f"---captcha_agent_ai: {data}, url: {cnd_url}")
    if not data or not data["message"]["imagePropertyValues"]:
        return None
    res_data = data["message"]["imagePropertyValues"][0]
    box = res_data["box"]
    swipe_end_x = int(
        (offset * ((box[1][0] + box[0][0]) // 2 + crop_pos[0] - swipe_start_pos[0])) + swipe_start_pos[0])
    res_data["swipe_start_pos"] = swipe_start_pos
    res_data["swipe_end_pos"] = (swipe_end_x, swipe_start_pos[1])
    return res_data

def fast_touch_snapshot(pos, crop_pos=None, timeout=0.5):
    """点击后迅速截图"""
    shell("input tap {} {}".format(pos[0], pos[1]))
    print("---点击后截图---")
    print("====================\n")
    print("====================\n")
    print("====================\n")
    print("====================\n")
    print("====================\n")
    # after_touch_img = G.DEVICE.snapshot(ensure_orientation=True)
    after_touch_img = lx_snapshot(AppEnv.get_instance(), "fast_touch_snapshot", crop_pos=crop_pos)
    print("---截图完成---")
    sleep(timeout)
    return after_touch_img


def dwarf_upload_property(property_name, property_value_name, img_url=None, child_nodes=[]):
    """
    属性回填
    :param property_name:
    :param property_value_name:
    :param img_url:
    :param child_nodes:
    :return:
    """
    if not img_url:
        _, img_url = upload_img_to_oss(lx_snapshot(AppEnv.get_instance(), "temp"))
    upload_propreties_with_data( AppEnv.get_instance().game_id, AppEnv.get_instance().get_common_property_with_key('gamePlatform'), [
                {
                    "childNodes": child_nodes,
                    "propertyName": property_name,
                    "propertyValueName": property_value_name
                }
            ], [img_url],
            taskIdList=[str(AppEnv.get_instance().taskId)], addParams=True,
            isFromCollectTask=True, isNeedShenpi=True)