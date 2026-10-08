from utility.utility_header import *

import itertools
import math
from typing import Union, Iterable, Tuple, List, Set, Dict, Callable
from glob import glob
from pathlib import Path
import json
import yaml
import re
import shelve
from pprint import pprint
import os
import traceback
from functools import wraps, partial
from enum import Enum
from copy import deepcopy
import difflib
OPJ = os.path.join
OP = os.path
os_env = os.environ
from subprocess import run, Popen, call, PIPE
p_args = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf8')

import cv2
import numpy as np
try:
    from paddleocr import PaddleOCR
except Exception as e:
    ...
from airtest.core.android.touch_methods.base_touch import DownEvent, MoveEvent, SleepEvent, UpEvent
from airtest.core.api import *
from airtest import aircv
import requests
from civita.session import ControlSession

logging.getLogger('session').setLevel(logging.CRITICAL)
logging.getLogger("airtest").setLevel(logging.CRITICAL)
logging.getLogger('ppocr').setLevel(logging.CRITICAL)

# 图片输出路径
logDir = Path(ST.LOG_DIR).resolve()

# 图片拼接
def combine_images_base(combine_images_arr, one_row_count=1, max_rows_count=10, spacing=0, spacing_x=0, spacing_y=0, spacing_color=(255, 255, 255)):
    spacing_color = spacing_color[2], spacing_color[1], spacing_color[0]
    if spacing: spacing_x = spacing_y = spacing
    final_count = len(combine_images_arr)
    if not final_count: return []
    spaceing_color_1, spaceing_color_2, spaceing_color_3 = spacing_color
    item_height, item_width = combine_images_arr[0].shape[:2]
    whole_width = item_width * one_row_count + spacing_x * (one_row_count - 1)
    row_imgs = []
    colomn_imgs = []
    for i in range(final_count):
        img = combine_images_arr[i]
        if (i + 1) % one_row_count > 0:
            img = cv2.copyMakeBorder(img, 0, 0, 0, spacing_x, cv2.BORDER_CONSTANT, value=(spaceing_color_1, spaceing_color_2, spaceing_color_3))
        row_imgs.append(img)
        if (i + 1) % one_row_count == 0:
            final_img = cv2.hconcat(row_imgs)
            colomn_imgs.append(final_img)
            row_imgs = []
        elif i == final_count - 1:
            final_img = cv2.hconcat(row_imgs)
            # color = (1, 1, 1)
            padding_height, padding_width = final_img.shape[:2]
            # 生成指定尺寸和颜色的背景图像
            background = np.zeros((item_height, whole_width - padding_width, 3), dtype=np.uint8)
            background[:] = spacing_color
            final_img = cv2.hconcat([final_img, background])
            colomn_imgs.append(final_img)
            row_imgs = []
    item_imgs = []
    result_imgs = []
    size_width = None

    for i in range(len(colomn_imgs)):
        img = colomn_imgs[i]
        if i != len(colomn_imgs) - 1 and (i + 1) % max_rows_count > 0:
            img = cv2.copyMakeBorder(img, 0, spacing_y, 0, 0, cv2.BORDER_CONSTANT, value=(spaceing_color_1, spaceing_color_2, spaceing_color_3))
        if size_width is None:
            size_width = img.shape[1]
        if img is not None:
            new_size = (size_width, img.shape[0])
            img = cv2.resize(img, new_size)
            item_imgs.append(img)
        if (i + 1) % max_rows_count == 0 or i == len(colomn_imgs) - 1:
            concat_img = cv2.vconcat(item_imgs)
            result_imgs.append(concat_img)
            item_imgs = []
    return result_imgs

def create_ocr(lang):
    try:
        #默认使用旧版本
        return PaddleOCR(lang=lang, use_gpu = False, use_angle_cls=False)
    except ValueError as e:
        print("paddle实例化错误，报错原因：",e)
        monitor_task_status_v2("本地PaddleOCR实例化错误——传入参数错误，需重重新创建实例", "开始")
        return PaddleOCR(lang=lang, device = "cpu", use_angle_cls=False)

# OCR识别

# ocr_ch_func = lambda: PaddleOCR(lang='ch', use_gpu=False, use_angle_cls=False)
# ocr_en_func = lambda: PaddleOCR(lang='en', use_gpu=False, use_angle_cls=False)

ocr_ch_func = lambda: create_ocr(lang='ch')
ocr_en_func = lambda: create_ocr(lang='en')
def ocr_image_base(img, en_ocr=False):
    array = []
    if en_ocr: result = ocr_en_func().ocr(img)
    else: result = ocr_ch_func().ocr(img)
    if result and len(result):
        for line in result:
            if line and len(line):
                for word in line:
                    array.append(word[1][0])
    return array

def match_in_base(match_image, whole_image, target_pos=None, threshold=0.7):
    match_image_width = match_image.shape[1]
    match_image_height = match_image.shape[0]
    whole_image_width = whole_image.shape[1]
    whole_image_height = whole_image.shape[0]
    if (match_image_width > whole_image_width) or \
        (match_image_height > whole_image_height):
        return None, 0

    result = cv2.matchTemplate(whole_image, match_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if isinstance(target_pos, Enum):
        target_pos = target_pos.value
    if max_val >= threshold:
        if target_pos == "lt":
            return max_loc, max_val
        elif target_pos == "rt":
            x = max_loc[0] + match_image_width
            y = max_loc[1]
            return (x, y), max_val
        elif target_pos == "lb":
            x = max_loc[0]
            y = max_loc[1] + match_image_height
            return (x, y), max_val
        elif target_pos == "rb":
            x = max_loc[0] + match_image_width
            y = max_loc[1] + match_image_height
            return (x, y), max_val
        elif target_pos == "center":
            x = max_loc[0] + int(match_image_width / 2)
            y = max_loc[1] + int(match_image_height / 2)
            return (x, y), max_val
        else:
            x = max_loc[0]
            y = max_loc[1] + match_image_height
            return (x, y), max_val
    else:
        return None, max_val

def match_in_all_base(match_image, whole_image, threshold=0.7):
    result = cv2.matchTemplate(whole_image, match_image, cv2.TM_CCOEFF_NORMED)
    # 获取匹配程度大于阈值的位置
    loc = np.where(result >= threshold)
    # 遍历这些位置
    location_list = []
    for pt in zip(*loc[::-1]):
        location_list.append((pt, (pt[0] + match_image.shape[1], pt[1] + match_image.shape[0])))
    return location_list

# (0, 127) 像素点的灰度值范围是从0到255。其中，0表示黑色，255表示白色。因此，(0, 127)表示灰度值从黑色到中灰色的范围。
def detect_color_image_base(pil_img, thumb_size=40, MSE_cutoff=22, adjust_color_bias=True):
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
            # 灰色
            return True
        else:
            return False
    elif len(bands) == 1:
        return True
    else:
        return False

def is_in_gray_range_by_image_base(image):
    base_image = image.copy()
    image_pil = Image.fromarray(cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB))
    return detect_color_image_base(image_pil)