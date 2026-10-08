# -*- encoding=utf8 -*-
__author__ = "yangxiao"

import importlib
import sys

from airtest.core.api import *
from airtest.core.helper import G
from airtest.core.cv import *
from airtest.core.error import TargetNotFoundError, InvalidMatchingMethodError
from airtest.core.android.android import *
from enum import Enum

auto_setup(__file__)

import cv2
import time
import json

# parent_dir = os.path.dirname(os.path.abspath(__file__))  # /project/src
# base_dir = os.path.join(parent_dir, 'base')
# sys.path.append(base_dir)
from utility.base.adc_environment import *

using("../utility/adc_safe_framework.air")
from adc_safe_base import *

from utility.base.adc_api import *


def lx_exists(v, timeout=None):
    if timeout is None:
        ST.FIND_TIMEOUT_TMP = 3
    else:
        ST.FIND_TIMEOUT_TMP = timeout

    try:
        pos = loop_find(v, timeout=ST.FIND_TIMEOUT_TMP)
    except TargetNotFoundError:
        print(f"---lx_exists_TargetNotFoundError:{TargetNotFoundError}")
        return False
    else:
        return pos


def lx_snapshot_api(filename=None, msg="", quality=None, max_size=None):
    return lx_safe_snapshot(filename=filename, msg=msg, quality=quality, max_size=max_size)


def lx_snapshot_image(filename=None, msg="", quality=None, max_size=None):
    lx_snapshot_api(filename=filename, msg=msg, quality=quality, max_size=max_size)
    image_path = os.path.join(ST.LOG_DIR, filename)
    image = cv2.imread(image_path)
    return image

# return_type标识返回的是图片，还是图片路径
def lx_crop_image(p1, p2, image=None, write_name=None, return_type=0):
    real_image = None
    if image is None:
        real_image = lx_snapshot_image(filename=f"lx_crop_image_{str(int(time.time() * 1000000))}.jpg")
    else:
        real_image = image

    cropped_image = real_image[p1[1]:p2[1], p1[0]:p2[0]]

    write_name_path = os.path.join(ST.LOG_DIR, write_name)
    cv2.imwrite(write_name_path, cropped_image)

    if return_type == 0:
        return cropped_image
    elif return_type == 1:
        return write_name_path

# is_try参数标识是否需要捕获wait指令的异常情况
# break_mode用于标识当捕获到wait异常后，中断处理哪种级别（phase，runloop，app）
def lx_wait(v, timeout=None, interval=0.5, intervalfunc=None, is_try=False, break_mode=BreakMode.StopRunloop):
    try:
        return wait(v, timeout, interval, intervalfunc)
    except Exception as e:
        print(f'---lx_wait_Exception:{e}, is_try:{is_try}, break_mode:{break_mode}')
        if is_try:
            return None
        if break_mode == BreakMode.StopRunloop:
            lx_break_runloop(e)
        elif break_mode == BreakMode.StartNextPhase:
            lx_break_phase(e)
        else:
            lx_break_app(ext_info={'key': '120002'}, e=e, desc='lx_wait exception')


# sec标识touch之后需要sleep多少秒        
def lx_touch(v, sec: float = 0, is_try=False, break_mode=BreakMode.StopRunloop):
    try:
        pos = touch(v)
        if sec:
            sleep(sec)
        return pos
    except Exception as e:
        if False == is_try:
            if break_mode == BreakMode.StopRunloop:
                lx_break_runloop(e)
            elif break_mode == BreakMode.StartNextPhase:
                lx_break_phase(e)
            else:
                lx_break_app(ext_info={'key': '120003'}, e=e, desc='lx_touch exception')


# sec标识touch之后需要sleep多少秒 
# pos 标识需要touch的位置
# is_try参数标识是否需要捕获wait指令的异常情况 
# break_mode用于标识当捕获到wait异常后，中断处理哪种级别（phase，runloop，app） 
def lx_wait_touch(v, timeout=None, interval=0.5, intervalfunc=None, sec=None, alt_v=None, is_try=False,
                  break_mode=BreakMode.StopRunloop):
    p = lx_wait(v, timeout, interval, intervalfunc, is_try, break_mode)
    if alt_v:
        lx_touch(alt_v, sec)
    elif p:
        lx_touch(p, sec)
    return p


# sec标识touch之后需要sleep多少秒  
# alv_v参数是需要touch的位置或者图片   
def lx_exists_touch(v, alt_v=None, sec=None):
    pos = exists(v)
    print(f"---lx_exists_touch:{pos}")
    if pos:
        if alt_v:
            lx_touch(alt_v, sec)
        else:
            lx_touch(pos, sec)
    return pos


# sec标识touch之后需要sleep多少秒  
# alv_v参数是需要touch的位置或者图片     
def lx_not_exists_touch(v, alt_v, sec=None):
    pos = exists(v)
    if not pos:
        lx_touch(alt_v, sec)
    return pos


# condition是前置条件执行函数
# do_task是在前置条件执行函数正常的情况下执行具体任务的函数
# repeat是重复执行的次数上限 
def lx_while(condition, do_task, repeat=10):
    for index in range(repeat):
        result = condition()
        if result:
            do_task()
        else:
            break


def lx_exists_with_file(v, snapshot_path, threshold=None, timeout=None):
    try:
        real_timeout = ST.FIND_TIMEOUT_TMP
        if timeout is not None:
            real_timeout = timeout
        pos = lx_loop_find(v, snapshot_path, timeout=real_timeout, threshold=threshold)
    except TargetNotFoundError:
        return False
    else:
        return pos


def lx_exists_image_in_largeimage(image, large_image, shuping=False):
    image_name = f"lx_exists_image_in_largeimage_image_{str(int(time.time() * 1000000))}.jpg"
    image_path = os.path.join(ST.LOG_DIR, image_name)
    cv2.imwrite(image_path, image)

    template = Template(f"{image_path}")
    if shuping == True:
        template = Template(f"{image_path}", record_pos=(-0.102, 0.12), resolution=(1350, 2400))

    pos = template.match_in(large_image)
    print(f"lx_exists_image_in_largeimage: {pos}")

    return pos


def lx_loop_find(query, snapshot_path=None, timeout=ST.FIND_TIMEOUT, threshold=None, interval=0.5, intervalfunc=None):
    start_time = time.time()
    while True:
        screen = None
        if snapshot_path != None and len(snapshot_path) > 0:
            screen = cv2.imread(snapshot_path)
        else:
            screen = lx_safe_snapshot(filename=None, quality=ST.SNAPSHOT_QUALITY)

        if screen is None:
            G.LOGGING.warning("Screen is None, may be locked")
        else:
            if threshold:
                query.threshold = threshold
            match_pos = query.match_in(screen)
            if match_pos:
                try_log_screen(screen)
                return match_pos

        if intervalfunc is not None:
            intervalfunc()

        # 超时则raise，未超时则进行下次循环:
        if (time.time() - start_time) > timeout:
            try_log_screen(screen)
            raise TargetNotFoundError('Picture %s not found in screen' % query)
        else:
            time.sleep(interval)


# 注意match_all_in这个方法很消耗内存，要谨慎使用
def lx_find_all(v, match_bg_image):
    return v.match_all_in(match_bg_image)


def get_escape_text(input_text):
    # ADB needs a backslash to be sent as a double backslash.
    # Shell also interprets some characters like * and ! which need to be escaped with a backslash.
    # Add other characters to escape as needed.
    characters_to_escape = ['\\', '*', '!', '(', ')', '"', "'", '`', '|', ';', '<', '>', '&', '$', ' ', '%', '~', '?',
                            '^', '{', '}', '[', ']', '@', '#']
    for char in characters_to_escape:
        input_text = input_text.replace(char, '\\' + char)
    return input_text


# 使用的是clipper
def lx_input(text: str):
    """
    输入支持中英文
    :param text:
    :return:
    """
    new_input_text = get_escape_text(text)
    if new_input_text is not None:
        shell('am startservice ca.zgrs.clipper/.ClipboardService')
        shell(f'am broadcast -a clipper.set --es text "{new_input_text}"')
        shell('input keyevent KEYCODE_PASTE')


def lx_shell_input(input_text):
    new_input_text = get_escape_text(input_text)
    if new_input_text is not None:
        shell("input text {}".format(new_input_text))


class INTERNAL_PRINT_LEVEL(Enum):
    INFO = 1
    DEBUG = 2
    WARN = 3
    ERROR = 4


def internal_print(desc, timestamp=None, level=INTERNAL_PRINT_LEVEL.DEBUG):
    GRAY = "\033[37m"  # 浅灰色
    BLUE = "\033[94m"  # 蓝色
    YELLOW = "\033[93m"  # 黄色
    RED = "\033[91m"  # 红色
    GREEN = "\033[92m"  # 绿色

    RESET = "\033[0m"  # 重置颜色

    env = AppEnv.get_instance()
    taskId = env.taskId
    game_dir = env.gameDir
    game_name = env.game_name
    launchType = env.launchType
    info = ' adc-sc-log-->  ' + 'desc:' + desc + ';  '

    if taskId:
        info = 'adc-sc-log-->  ' + 'taskId:' + taskId + ';  ' + 'desc:' + desc + ';  '

    if game_dir is not None and len(game_dir) > 0:
        info = info + 'game_dir:' + game_dir + ';  '

    if game_name is not None and len(game_name) > 0:
        info = info + 'game_name:' + game_name + ';  '

    if timestamp is not None:
        info = info + 'print_timestamp:' + str(int(timestamp)) + ';  '
    else:
        info = info + 'print_timestamp:' + str(int(time.time() * 1000000)) + ';  '

    real_color = GRAY
    if level == INTERNAL_PRINT_LEVEL.ERROR:
        real_color = RED
    elif level == INTERNAL_PRINT_LEVEL.WARN:
        real_color = YELLOW
    elif level == INTERNAL_PRINT_LEVEL.DEBUG:
        real_color = GREEN
    elif level == INTERNAL_PRINT_LEVEL.INFO:
        real_color = BLUE

    print(real_color + info + RESET)
