# -*- encoding=utf8 -*-
__author__ = "zhuhaoshuang"
import traceback
from airtest.core.api import *
import time
import sys
import cv2
import json

import numpy as np

using("../utility/monitor.air")
from monitor import *

using("../utility/api.air")
from api import *

using("../utility/phase.air")
from phase import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/mask.air")
from mask import *

using("../utility/swipe.air")
from swipe import *

using("../utility/image.air")
from image import *

using("../utility/ocr.air")
from ocr import *

using("./utility/security.air")
from security import *


using("../utility/upload.air")
from upload import *

from airtest import aircv

png_file_name = 'adc_result'
catch_file_name = 'adc_catch'
tmp_file_name = 'tmp'
ENV = AppEnv.get_instance()

def loginTaskLingXi(env, preLoginFunc=None, afterLoginFunc=None, skipCheckDialog=False):
    if AppDynamicInfo.get_instance().getHasLogin():
        
        if preLoginFunc is not None:
            preLoginFunc(env)
        sleep(3)
        
        if afterLoginFunc is not None:
            afterLoginFunc(env)
        monitor_task_status(env, "登录", "getHasLogin已登录")
        lx_break_phase(desc='已登录')
    else:
        processLogin(env, preLoginFunc, afterLoginFunc, skipCheckDialog)

def kit_wait(v, timeout=None, interval=0.5, intervalfunc=None, is_try = False):
    try:
        monitor_print(f'---kit_wait_finding: {v}')
        start_time = time.time()
        while True:
            screen = streamSnapshot()
            if screen is None:
                monitor_print(f'---kit_wait_error: Screen is None, may be locked')
                if timeout is None:
                    return None
            else:
                pos = v.match_in(screen)
                if pos:
                    return pos
                if timeout is None:
                    return None
                if (time.time() - start_time) > timeout:
                    return None
                else:
                    time.sleep(interval)
    except:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit_wait_exception: {error_traceback}')
        if is_try:
            return None
def snapshotImg(name, type_name = tmp_file_name, mask = None, LT = None, RB = None, path=False):
    """
        截图
    """
    img_filename = f'{type_name}_{name}_{str(int(time.time() * 1000000))}.jpg'
    streamSnapshot(filename = img_filename, msg="get a snapshot.")
    image_path = os.path.join(ST.LOG_DIR, img_filename)
    if mask is not None:
        for mask_one in mask:
            mask_image_range_tosave(image_path, mask_one[0], mask_one[1])
    image_np = cv2.imread(image_path)
    if LT is not None and RB is not None:
        image_np = image_np[LT[1]:RB[1], LT[0]:RB[0]]
        cv2.imwrite(image_path, image_np)
    if path:
        return image_path
    else:
        return image_np
    
def kit_wait_find(v, timeout=None, interval=0.5, threshold=0.7, area_pos = None):
    try:
        monitor_print(f'---kit_wait_finding: {v}')
        start_time = time.time()
        while True:
            screen = streamSnapshot()
            if screen is None:
                monitor_print(f'---kit_wait_error: Screen is None, may be locked')
                if timeout is None:
                    return None
            else:
                file_path = v._filepath
                file_np = cv2.imread(file_path)
                if area_pos is not None:
                    screen = screen[area_pos[1]:area_pos[3], area_pos[0]:area_pos[2]]
                pos = kit_match_in(file_np, screen, threshold)
                if pos:
                    if area_pos is not None:
                        pos = (pos[0] + area_pos[0], pos[1] + area_pos[1])
                    return pos
                if timeout is None:
                    return None
                if (time.time() - start_time) > timeout:
                    return None
                else:
                    time.sleep(interval)
    except:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit_wait_find_exception: {error_traceback}')
        return None
def kit_match_in(small_img_np, main_img_np = None, threshold=0.57):
    small_img_gray = cv2.cvtColor(small_img_np, cv2.COLOR_BGR2GRAY)
    if main_img_np is not None:
        main_img_gray = cv2.cvtColor(main_img_np, cv2.COLOR_BGR2GRAY)
    else:
        file_name = f'{catch_file_name}_kit_match_in_{str(int(time.time()*1000000))}.jpg'
        lx_safe_snapshot(filename=file_name, msg="get a snapshot.")
        img_path = os.path.join(ST.LOG_DIR, file_name)
        main_img_gray = cv2.imread(img_path, 0)
    # 进行模板匹配
    res = cv2.matchTemplate(main_img_gray, small_img_gray, cv2.TM_CCOEFF_NORMED)

    # 找到最大和最小值及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # 使用最大值位置作为匹配结果
    top_left = max_loc
    h, w = small_img_gray.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    pos = (top_left[0] + int(w / 2), top_left[1] + int(h / 2))
    print(max_val)
    if max_val > threshold:
        return pos
    else:
        return None     
        
def streamSnapshot(filename = None, msg = None, is_try = True):
    try:
        device = ENV.device
        data = device.screen_proxy.get_frame_from_stream()
        frame = aircv.utils.string_2_img(data)
        
        frame = resize_by_max(frame, 2400)
        if filename is not None:
            path = os.path.join(ST.LOG_DIR, filename)
            cv2.imwrite(path, frame)
        return frame
    except Exception as e:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit stream snapshot error({ENV.gameDir}): {error_traceback}')
        if is_try:
            lx_break_app(desc='截图失败', hold_game=True,ext_info={'key':'10163'})
        return None
    
def resize_by_max(img, max_size=800):
    if img is None:
        return np.zeros((max_size, max_size, 3), dtype=np.uint8)
    max_len = max(img.shape[0], img.shape[1])
    if max_len > max_size:
        scale = max_size / max_len
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
    return img

def processLogin(env, preLoginFunc=None, afterLoginFunc=None, skipCheckDialog=False, login_check_time_out = 120):
    mode = env.mode
    taskId = env.taskId
    taskStatus = env.taskStatus
    scriptEnv = env.scriptEnv
    username = env.username
    password = env.password
    smsCode = env.smsCode
    orientation = G.DEVICE.display_info["orientation"]
    # 是否竖屏
    is_portrait_screen = False
    resolution = (2400, 1350)
    if orientation in (1, 3):
        monitor_task_status(env, "登录阶段-检测屏幕方向", "竖屏")
        is_portrait_screen = True
        resolution = (1350, 2400)
    else:
        monitor_task_status(env, "登录阶段-检测屏幕方向", "横屏")
    if preLoginFunc is not None:
        preLoginFunc(env)
    #检测灵犀登录入口
    monitor_task_status(env, "登录阶段", "检测-灵犀登录入口")
    pos = kit_wait(Template(r"tpl1733136142632.png", record_pos=(-0.001, -0.105), resolution = resolution), timeout = 5, is_try=True)
    if pos:
        monitor_task_status(env, "登录阶段", "检测到-灵犀登录入口")
        for try_touch in range(3):
            # 隐私政策勾选
            yszc_button = kit_wait_find(Template(r"tpl1733192053835.png", record_pos=(-0.137, 0.118), resolution = resolution), threshold=0.98)
            yszc_button2 = kit_wait_find(Template(r"tpl1747376475034.png", record_pos=(-0.137, 0.118), resolution = resolution), threshold=0.98)
            if yszc_button:
                monitor_task_status(env, "登录阶段", "检测到-隐私政策未勾选")
                lx_touch(yszc_button, 0.2)
                touch_after = kit_wait_find(Template(r"tpl1733192060064.png", record_pos=(-0.137, 0.119), resolution = resolution), threshold=0.98)
                if touch_after:
                    monitor_task_status(env, "登录阶段", "隐私政策勾选成功")
                    break
            elif yszc_button2:
                monitor_task_status(env, "登录阶段", "检测到-隐私政策未勾选")
                lx_touch(yszc_button2, 0.2)
                touch_after = kit_wait_find(Template(r"tpl1747376542336.png", record_pos=(-0.137, 0.119), resolution = resolution), threshold=0.98)

                if touch_after:
                    monitor_task_status(env, "登录阶段", "隐私政策勾选成功")
                    break

            else:
                monitor_task_status(env, "登录阶段", "未检测到隐私政策勾选框")
        else:
            snapshotImg('yszc_button_error', catch_file_name)
    else:
        lx_break_runloop(desc="登录阶段, 未成功检测到-灵犀登录入口")
        return
    monitor_task_status(env, "登录阶段", "输入账号")
    sleep(ENV.sleepTime*2)
    # 点击手机号输入框
    phone_input_pos = (pos[0], pos[1] + 150)
    lx_touch(phone_input_pos, 1)
    # 清理手机号输入框内容
    shell("input keyevent 67")
    sleep(1)
    # 输入手机号
    shell(f"input text {username}")
    sleep(ENV.sleepTime)
    # 消除键盘
    for try_count in range(3):
        ok_button = kit_wait_find(Template(r"tpl1733192991625.png", record_pos=(0.319, 0.255), resolution = resolution), threshold=0.9)
        if ok_button:
            lx_touch(ok_button, 1)
            break
    monitor_task_status(env, "登录阶段", "点击下一步")
    next_button = kit_wait_find(Template(r"tpl1733193110067.png", record_pos=(0.001, 0.012), resolution = resolution), threshold=0.8, timeout=3)
    if next_button:
        lx_touch(next_button, 1)
    for i in range(4):
        monitor_task_status(env, "登录", "点击登录页面后")
        snapshotImg('denglu_after', catch_file_name)
        sleep(0.5)
    sleep(2)
    password_login_button = kit_wait_find(Template(r"tpl1733193289063.png", record_pos=(-0.044, 0.038), resolution = resolution), threshold=0.9, timeout=5)
    password_login_button2 = kit_wait_find(Template(r"tpl1747375566606.png", record_pos=(-0.044, 0.038), resolution = resolution), threshold=0.9, timeout=5)

    if password_login_button:
        monitor_task_status(env, "检测到-密码登录按钮", "点击密码登录")
        lx_touch(password_login_button, 1)
    elif password_login_button2:
        monitor_task_status(env, "检测到-密码登录按钮2", "点击密码登录2")
        lx_touch(password_login_button2, 1)

    else:
        monitor_task_status(env, "未检测到-密码登录按钮", "未检测到")
    # 登录按钮
    login_button_pos = kit_wait_find(Template(r"tpl1733193486949.png", record_pos=(0.005, 0.032), resolution = resolution), threshold=0.9)
    if login_button_pos:
        monitor_task_status(env, "密码输入框坐标确认-检测到登录按钮", f"登录按钮坐标: {login_button_pos}")
        # 点击密码输入框
        password_input_pos = (login_button_pos[0], login_button_pos[1] - 150)
    else:
        monitor_task_status(env, "未检测到登录按钮", "密码输入框采用固定坐标点击")
        # 默认横屏坐标
        password_input_pos = (1109,623)
    monitor_task_status(env, "点击密码输入框", f"{password_input_pos}")
    lx_touch(password_input_pos, 1)
    # 输入密码
    shell("input text {}".format(password))
    # 消除键盘
    for try_count in range(3):
        ok_button = kit_wait_find(Template(r"tpl1733192991625.png", record_pos=(0.319, 0.255), resolution = resolution), threshold=0.9)
        if ok_button:
            lx_touch(ok_button, 1)
            break
        ok_button2 = kit_wait_find(Template(r"tpl1747376165090.png", record_pos=(0.319, 0.255), resolution = resolution), threshold=0.9)
        if ok_button2:
            monitor_task_status(env,"检测到键盘2","消除键盘2")
            lx_touch((1991,641), 5)
            break
    login_button_pos2 = kit_wait_find(Template(r"tpl1747375722887.png", record_pos=(0.005, 0.032), resolution = resolution), threshold=0.9, timeout=5)

    # 点击登录
    if login_button_pos:
        lx_touch(login_button_pos, 1)
    elif login_button_pos2:
        monitor_task_status(env, "检测到登录按钮2",f"检测到登录按钮2:{login_button_pos}")
        lx_touch(login_button_pos2, 1)
        zhengxe_button = lx_exists(Template(r"tpl1747385176344.png", record_pos=(0.084, 0.058), resolution=(2400, 1350)))
        if zhengxe_button:
            monitor_task_status(env,"检测到政策按钮", "检测到政策按钮")
            lx_touch(zhengxe_button, 2)
    else:
        # 默认横屏坐标
        lx_touch((1200, 755), 1)
    yszc_check = kit_wait_find(Template(r"tpl1733195115890.png", record_pos=(0.107, 0.195), resolution = resolution), threshold=0.9, timeout=3)
    if yszc_check:
        monitor_task_status(env, "检测到-隐私政策提示", "点击接受隐私政策")
        lx_touch(yszc_check, 1)
    # 选择登录账号
    select_id = kit_wait_find(Template(r"tpl1733195766874.png", record_pos=(-0.077, -0.026), resolution = resolution), threshold=0.9)
    if select_id:
        monitor_task_status(env, "检测到-选择登录账号", "选择登录账号")
        lx_touch(select_id, 0.2)
    # 等待登录结束
    sleep(5)
    monitor_task_status(env, "登录流程", "完成")
    if afterLoginFunc is not None:
        afterLoginFunc(env)