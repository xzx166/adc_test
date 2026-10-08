#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lc
# @Date: 2026/4/7


import time
from airtest.core.api import *
from utility.base.adc_security import decrypt, encrypt
from utility.base.adc_api import adc_input
from utility.app.rebind.rebind_tools import *
from utility.tool_kit.kit_rebind import *
from functools import partial, wraps
import json
import re
from typing import Callable, Any

using('../utility/swipe.air')
from swipe import swipe_only

using("../utility/dwarf.air")
from imports import *
from pathlib import Path

using("../utility/lxplatform_start.air")
from lxplatform_start import *

os.environ.update(
    indexDir=str(Path(__file__).resolve().parent),
    screenRotation="H",
    poco_enable="true"
)
using("../utility/api.air")
from api import *

ENV = AppEnv.get_instance()
using("../utility/biz_utils.air")
from biz_utils import *

using("../utility/biz_utils")
from biz_utils import (monitor_task_status_v2, monitor_catch, snapshot_write, monitor_print, image_upload,
                       get_jiuyou_all_servers, push_jiuyou_server_incremental, ImageOcrRemote)
from LLM import get_name_large_model_copy

from poco.drivers.android.uiautomation import AndroidUiautomationPoco

poco = AndroidUiautomationPoco(use_airtest_input=False, screenshot_each_action=False)
game_name = "QQ"
package_name = ENV.get_common_property_with_key('jymPackageName')
package_name = package_name if package_name else "com.tencent.mobileqq"

# 本地
localRun = ENV.launchType == "localtest"
# 设置截图模式
tool_kit_set_env(snapshot_mode="auto")


def check_account_logged_in() -> bool:
    """
    检查账户是否被踢
    """
    logout_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770873017705.png", record_pos=(0.019, -0.067),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770873029174.png", record_pos=(0.077, 0.041),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770882190386.png", record_pos=(0.007, -0.186),
                 resolution=(1350, 2400))
    ]
    if kit_wait_find_plus(logout_list):
        return False
    return True


def handle_account_logout():
    """
    处理账户被踢下线的情况
    """
    snapshotImg('account_logout', catch_file_name)
    monitor_task_status_v2('账户被踢下线')
    return {'success': False, 'message': '账户被踢下线', 'code': 'account_kicked_offline_error'}


def check_login_status(func: Callable) -> Callable:
    """
    在函数执行前检查账户是否被踢下线
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if not check_account_logged_in():
            handle_account_logout()
            return None

        result = func(*args, **kwargs)
        return result

    return wrapper


def login_qq_by_password(qq, password):
    """
    登陆
    1.正常登陆
    2.触发下行短信验证-发送验证码》check_qq_login_downstream_captcha
    3.触发上行短信验证-返回发送内容》upstream_qq_login_sms
    4.密码错误重试
    """
    monitor_task_status_v2("登陆qq账号", "")
    if not qq or not password:
        return {"success": False, "message": "QQ号或密码为空", 'code': 'account_error'}
    gamePackage = shell(f"pm list packages | grep {package_name}")
    monitor_task_status_v2(f"{game_name}APP", f"{gamePackage}")
    if not gamePackage:
        return {"success": False, "message": "QQAPP不存在", 'code': 'application_error'}
    snapshotImg('device_init', catch_file_name)
    check_login_page_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768809492721.png", record_pos=(-0.23, 0.691),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768809500857.png", record_pos=(-0.004, -0.076),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768809749352.png", record_pos=(-0.004, 0.105),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768810505465.png", record_pos=(0.022, 0.139),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768810384776.png", record_pos=(0.001, -0.624),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770191010992.png", record_pos=(0.001, -0.076),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770882833042.png", record_pos=(0.001, 0.118),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770882190386.png", record_pos=(0.007, -0.186),
                 resolution=(1350, 2400)),
    ]
    sleep(10)
    # 可能处于密码错误状态，多次错误弹窗略有区别
    is_pwd_error_page = ocrText(ENV, "is_pwd_error_page", (390, 1160, 940, 1215))
    is_pwd_error_words = ''
    for word in is_pwd_error_page:
        is_pwd_error_words += word[0]
    if '错误' in is_pwd_error_words:
        monitor_task_status_v2(f"账密错误，重试")
        adc_touch((550, 1370), 0.5)
        sleep(0.5)
    is_pwd_error_page2 = ocrText(ENV, "is_pwd_error_page2", (315, 1120, 1000, 1180))
    is_pwd_error_words2 = ''
    for word in is_pwd_error_page2:
        is_pwd_error_words2 += word[0]
    if '错误' in is_pwd_error_words2 or '密码' in is_pwd_error_words2:
        monitor_task_status_v2(f"账密错误")
        adc_touch((550, 1370), 0.5)
    check_login_page = kit_wait_find_plus(check_login_page_list, threshold=0.9)
    # 可能是验证码输入超时页面，需要点击返回重新登陆
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817882452.png", record_pos=(0.003, -0.676),
                     resolution=(1350, 2400))):
        monitor_task_status_v2('验证码超时，重新登陆')
        adc_touch((50, 120), 2)
    if not check_login_page:
        kit_rebind_game_action(
            clean_game_func=None,
            package_name=package_name,
            stop_game=False,
            start_game=True
        )
        sleep(5)
    login_again()
    try:
        # 偶发点不到同意按钮，暂时重试尝试，猜测可能是设备卡顿
        for i in range(5):
            agree_button_check = ocrText(ENV, "agree_check", (1350, 1010, 1465, 1065))[0][0]
            if '同意' in agree_button_check:
                adc_touch((1400, 1040), 0.5)
                sleep(5)
                break
            sleep(1)
    except Exception as e:
        snapshotImg('touch_agree', catch_file_name)
        monitor_task_status_v2('')
    version_update_tips()
    # 初始页面需要点击登陆按钮
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768809492721.png", record_pos=(-0.23, 0.691),
                     resolution=(1350, 2400)), timeout=5):
        adc_touch((1000, 2120), 0.5)
        sleep(2)
    # 点击切换为QQ号登陆
    snapshotImg('check_change_qq_button', catch_file_name, LT=(550, 1325), RB=(810, 1370))
    check_change = kit_wait_find(
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769486764773.png", record_pos=(0.002, 0.107),
                 resolution=(1350, 2400)),
        timeout=5)
    if check_change:
        # QQ号登陆切换按钮有时点击一次无法跳转,检测一下额外点击一次
        adc_touch((200, 2100), 0.5, printLog=True)
        sleep(1)
        check_change = kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769486764773.png", record_pos=(0.002, 0.107),
                     resolution=(1350, 2400)),
            timeout=5)
        if check_change:
            adc_touch((200, 2100), 0.5, printLog=True)
            sleep(1)
    # 确认当前处于QQ号密码登陆页面
    login_by_pwd_page_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768810505465.png", record_pos=(0.022, 0.139),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768810394340.png", record_pos=(-0.009, -0.321),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768810384776.png", record_pos=(0.001, -0.624),
                 resolution=(1350, 2400))
    ]
    login_by_pwd_page_check = kit_wait_find_plus(login_by_pwd_page_list, threshold=0.9)
    if not login_by_pwd_page_check:
        return {"success": False, "message": "QQ登陆页面异常", 'code': 'page_error'}
    # 输入qq号
    adc_touch((1100, 750), 0.5, printLog=True)
    snapshotImg('enter_qq', catch_file_name)
    for j in range(15): shell("input keyevent 67")
    shell("input text {}".format(f'{qq}'))
    # 偶发账号输入未生效，这里加一层校验,发现没点击，再执行一次输入账号操作
    check_touch_account = ocrText(ENV, "check_change", (550, 730, 800, 800))[0][0]
    if '输入' in check_touch_account:
        adc_touch((1100, 750), 0.5, printLog=True)
        snapshotImg('enter_qq', catch_file_name)
        for j in range(15): shell("input keyevent 67")
        shell("input text {}".format(f'{qq}'))
    # 输入密码
    adc_touch((1100, 1000), 0.5)
    sleep(1)
    snapshotImg('enter_pwd', catch_file_name)
    for j in range(20): shell("input keyevent 67")
    shell("input text {}".format(f'{password}'))
    # 点击密码明文
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768811618831.png", record_pos=(-0.352, -0.159),
                     resolution=(1350, 2400))):
        adc_touch((200, 1000), 0.5)
    snapshotImg('enter_qq_and_pwd_after', catch_file_name)

    # 勾选用户协议
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768813428722.png", record_pos=(-0.214, 0.141),
                     resolution=(1350, 2400))):
        adc_touch((310, 1390), 0.5)
    # 点击登陆
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768811951898.png", record_pos=(0.009, 0.03),
                     resolution=(1350, 2400))):
        adc_touch((670, 1250), 0.5)
    else:
        snapshotImg('tobe_login_error', catch_file_name)
        return {"success": False, "message": "登陆按钮异常", 'code': 'page_error'}
    snapshotImg('login_after', catch_file_name)
    # 通过轮询方式处理点击登陆后可能出现的各种场景
    result = login_with_scene_handling()
    return result


def trigger_qq_login_downstream_captcha(seller_mobile):
    """
    身份验证后接收卖家手机号
    可能会出现下行短信验证码用户未接受到的情况，需要重发短信
    判断当前页面即可
    """
    # 判断是否为重发短信
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817882452.png", record_pos=(0.003, -0.676),
                     resolution=(1350, 2400))):
        resend_message = ocrText(ENV, "resend_message", (200, 810, 450, 855))
        resend_words = ''
        for word in resend_message:
            resend_words += word[0]
        print(resend_words)
        nums = list(map(int, re.findall(r"\d+", resend_words)))
        if nums:
            sleep(int(nums[0]) + 1)
        adc_touch((280, 830), 0.5)
        snapshotImg('resend_message', catch_file_name)
        send_result = ocrText(ENV, "send_result", (459, 1188, 976, 1268))
        sned_result_words = ''
        for word in send_result:
            sned_result_words += word[0]
        if '重新登录' in sned_result_words or '请求已失效' in sned_result_words:
            return {"success": False, "message": "验证超时", 'code': 'exit_retry_error'}
        return {"success": False, "message": "需要验证", 'code': 'need_verify', 'need_seller_mobile': False,
                "verify_type": 'downstream'}

    if not seller_mobile:
        return {"success": False, "message": "手机号错误", 'code': 'seller_mobile_error'}
    check_is_enter_phone_page_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768900664057.png", record_pos=(-0.223, -0.668),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768900681170.png", record_pos=(-0.004, -0.275),
                 resolution=(1350, 2400))
    ]
    if kit_wait_find_plus(check_is_enter_phone_page_list, threshold=0.9):
        adc_touch((1100, 620), 0.5)
        snapshotImg('enter_seller_mobile', catch_file_name)
        for j in range(20): shell("input keyevent 67")
        shell("input text {}".format(f'{seller_mobile}'))
        sleep(1)
        adc_touch((680, 820), 0.5, printLog=True)
        snapshotImg('next_step_touch', catch_file_name)
        # 如果手机号输入间隔较长，点击下一步会提示账号错误，请重新输入，这种情况需要重新登陆
        interval_too_long_check = ocrText(ENV, "interval_too_long_check", (456, 367, 935, 430))
        check_words = ''
        for word in interval_too_long_check:
            check_words += word[0]
        if '账号错误' in check_words or '错误' in check_words:
            return {"success": False, "message": "验证超时", 'code': 'exit_retry_error'}
        sleep(1)
        check_in_upstream_captcha_page = [
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768988637699.png", record_pos=(-0.292, -0.636),
                     resolution=(1350, 2400)),
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768988646316.png", record_pos=(0.341, -0.418),
                     resolution=(1350, 2400))
        ]
        if kit_wait_find_plus(check_in_upstream_captcha_page, threshold=0.9):
            # 截取当前上行短信页面
            upstream_image = snapshotImg('upstream_image', catch_file_name, path=True)
            upstream_oss_pathes, upstream_oss_urls = upload_jym_oss_with_pathes([upstream_image])
            # 截取短信内容
            upstream_content = ocrText(ENV, "message_content", (270, 600, 330, 670))[0][0]
            upstream_mobile = ocrText(ENV, "message_content", (270, 770, 750, 840))[0][0]
            return {"success": False, "message": "需要验证", 'code': 'need_verify', 'need_seller_mobile': False,
                    "verify_type": 'upstream', 'upstream_mobile': upstream_mobile, 'upstream_content': upstream_content,
                    'upstream_image': str(upstream_oss_urls[0])}
        else:
            if kit_wait_find_plus(check_is_enter_phone_page_list, threshold=0.9):
                return {"success": False, "message": "未知异常", 'code': 'seller_mobile_error'}
            return {"success": False, "message": "页面异常，未知错误", 'code': 'login_error'}


def upstream_qq_login_sms():
    """
    上行短信验证
    """
    is_sending = kit_wait_find(
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768989514579.png", record_pos=(-0.003, -0.064),
                 resolution=(1350, 2400)))
    if is_sending:
        adc_touch(is_sending, 0.5)
        for i in range(60):
            click_to_login = kit_wait_find(
                Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768901341707.png", record_pos=(0.002, 0.602),
                         resolution=(1350, 2400)))
            if click_to_login:
                adc_touch(click_to_login, 0.5)
                sleep(1)
            is_login_page = kit_wait_find(
                Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768811951898.png", record_pos=(0.009, 0.03),
                         resolution=(1350, 2400)))
            if is_login_page:
                # 点击登陆后，进入轮询判定逻辑
                adc_touch(is_login_page, 0.5)
                result = login_with_scene_handling()
                return result
            send_check_word = ocrText(ENV, "message_content", (40, 930, 1320, 1100))[0][0]
            if '未收到' in send_check_word or '不正确' in send_check_word:
                # 截取当前上行短信页面
                upstream_image = snapshotImg('upstream_image', catch_file_name, path=True)
                upstream_oss_pathes, upstream_oss_urls = upload_jym_oss_with_pathes([upstream_image])
                # 截取短信内容
                upstream_content = ocrText(ENV, "message_content", (270, 600, 330, 670))[0][0]
                upstream_mobile = ocrText(ENV, "message_content", (270, 770, 750, 840))[0][0]
                return {"success": False, "message": "用户未发送短信", 'code': 'upstream_sms_error',
                        'need_seller_mobile': False, 'upstream_mobile': upstream_mobile,
                        'upstream_content': upstream_content, 'upstream_image': str(upstream_oss_urls[0])}
            if '账号错误' in send_check_word or '错误' in send_check_word:
                return {"success": False, "message": "验证超时", 'code': 'exit_retry_error'}
            sleep(1)
        else:
            return {"success": False, "message": "未知错误", 'code': 'login_error'}
    else:
        return {"success": False, "message": "未知错误", 'code': 'login_error'}


def check_qq_login_downstream_captcha(captcha):
    """
    下行短信输入短信验证码
    """
    if not captcha:
        return {"success": False, "message": "验证码为空", 'code': 'check_captcha_error'}
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817882452.png", record_pos=(0.003, -0.676),
                     resolution=(1350, 2400))):
        adc_touch((250, 650), 0.5)
        shell("input text {}".format(captcha))
        snapshotImg('enter_captcha', catch_file_name)
        for i in range(5):
            monitor_task_status_v2('检查登陆结果')
            captcha_content = ocrText(ENV, "message_content", (465, 1200, 990, 1270))[0][0]
            if '重新登陆' in captcha_content or '请求已失效' in captcha_content:
                return {"success": False, "message": "请求已失效，请重新登录", 'code': 'exit_retry_error'}
            if '不正确' in captcha_content or '已过期' in captcha_content:
                return {"success": False, "message": "验证码错误或过期", 'code': 'check_captcha_error'}
            if '部分功能暂时使用受限' in captcha_content or '使用受限' in captcha_content:
                return {"success": True, "message": "执行成功", 'code': 'success', "social_limit": True}
            sleep(1)

        # 短信输入正确后，如未登陆成功则进入轮询判定逻辑
        result = login_with_scene_handling()
        return result
    else:
        return {"success": False, "message": "页面异常，未知错误", 'code': 'login_error'}

def login_again():
    """
    账户被踢下线，调用此脚本重新登陆
    默认当前设备处于被踢下线状态，其余页面均为异常页面
    """
    monitor_task_status_v2('检测是否为账户踢登页面')
    logout_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770873017705.png", record_pos=(0.019, -0.067),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770873029174.png", record_pos=(0.077, 0.041),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770882190386.png", record_pos=(0.007, -0.186),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770882833042.png", record_pos=(0.001, 0.118),
                 resolution=(1350, 2400))
    ]
    if kit_wait_find_plus(logout_list, threshold=0.9):
        monitor_task_status_v2('账户踢登，重新登陆')
        if kit_wait_find(
                Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770882190386.png", record_pos=(0.007, -0.186),
                         resolution=(1350, 2400))):
            # 点击关闭踢蹬弹窗
            adc_touch((660, 1500), random.uniform(1, 2), printLog=True)
        # 勾选用户协议
        # if kit_wait_find(Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768813428722.png", record_pos=(-0.214, 0.141), resolution=(1350, 2400))):
        adc_touch((360, 1500), random.uniform(1, 2), printLog=True)
        adc_touch((670, 1350), random.uniform(1, 2), printLog=True)
        sleep(5)
        # 重新登陆后，再次丢到循环里去处理社交限制等问题
        # login_with_scene_handling()


def login_with_scene_handling(timeout=310, interval=2):
    """
    处理点登陆后可能出现的各种场景
    """
    scenes = {
        # 验证码页面
        'verify_captcha': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768875320611.png",
                                   record_pos=(0.007, -0.147), resolution=(1350, 2400)),
        # 验证码页面
        'verify_captcha_2': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817786611.png",
                                     record_pos=(-0.228, -0.15), resolution=(1350, 2400)),
        # 触发下行短信验证页面
        'downstream_captcha': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817858382.png",
                                       record_pos=(0.004, -0.207), resolution=(1350, 2400)),
        # 登陆成功触发社交限制页面
        'social_limit': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768813939074.png",
                                 record_pos=(-0.005, -0.005), resolution=(1350, 2400)),
        'social_limit_2': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770608244958.png",
                                   record_pos=(-0.047, -0.093), resolution=(1350, 2400)),
        'social_limit_3': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770608256225.png",
                                   record_pos=(0.038, 0.01), resolution=(1350, 2400)),
        'social_limit_4': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770608346336.png",
                                   record_pos=(-0.033, -0.089), resolution=(1350, 2400)),
        'social_limit_5': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1770608353239.png",
                                   record_pos=(0.036, 0.013), resolution=(1350, 2400)),
        # 登陆频繁页面
        'account_frequent': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768875442526.png",
                                     record_pos=(0.002, -0.013), resolution=(1350, 2400)),
        # 登陆频繁手机验证页面
        'account_frequent_mobile_check': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768900444521.png",
                                                  record_pos=(-0.23, -0.446),
                                                  resolution=(1350, 2400)),
        # 风控页面
        'account_risk': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769395310249.png",
                                 record_pos=(-0.141, -0.416), resolution=(1350, 2400)),
        # 风控页面
        'account_risk_2': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1772008643425.png",
                                   record_pos=(-0.132, -0.356), resolution=(1350, 2400)),
        # 登陆频繁无法登陆
        'unable_to_login': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769672018649.png",
                                    record_pos=(-0.001, -0.039), resolution=(1350, 2400)),
        # 账号密码错误
        'account_error': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768899210762.png",
                                  record_pos=(-0.003, -0.011), resolution=(1350, 2400)),
        'version_update_tips': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769580346501.png",
                                        record_pos=(0.007, 0.41), resolution=(1350, 2400)),
        'version_update_tips_2': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1772604834260.png",
                                          record_pos=(-0.119, -0.288),
                                          resolution=(1350, 2400)),
        # 登陆成功页面
        'login_success': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768814336671.png",
                                  record_pos=(0.132, 0.833), resolution=(1350, 2400)),
        # 登陆成功页面2
        'login_success_two': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769580725862.png",
                                      record_pos=(0.128, 0.835), resolution=(1350, 2400)),
        # 登陆成功弹窗
        'login_success_show_dialog': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1772091008250.png",
                                              record_pos=(0.004, 0.612),
                                              resolution=(1350, 2400)),
        'login_success_show_dialog_2': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1772783712340.png",
                                                record_pos=(-0.005, 0.605),
                                                resolution=(1350, 2400)),
        'login_success_show_dialog_3': Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1774601382833.png",
                                                record_pos=(-0.001, 0.001),
                                                resolution=(1350, 2400))
    }
    failures_scenes = [
        "account_error"
    ]

    scene_handler = {
        'verify_captcha': verify_captcha,
        'verify_captcha_2': verify_captcha,
        'downstream_captcha': downstream_captcha,
        'social_limit': login_success,
        'social_limit_2': login_success,
        'social_limit_3': login_success,
        'social_limit_4': login_success,
        'social_limit_5': login_success,
        'account_frequent': account_frequent,
        'account_risk': login_error,
        'account_risk_2': login_error,
        'account_frequent_mobile_check': account_frequent_mobile_check,
        'version_update_tips': login_success,
        'version_update_tips_2': login_success,
        'login_success_show_dialog': login_success,
        'login_success_show_dialog_2': login_success,
        'login_success_show_dialog_3': login_success
    }

    start_time = time.time()
    no_match_count = 0
    account_risk_failed = False
    param_providers = {
        "social_limit": lambda: {"deep_risk": account_risk_failed},
        'social_limit_2': lambda: {"deep_risk": account_risk_failed},
        'social_limit_3': lambda: {"deep_risk": account_risk_failed},
        'social_limit_4': lambda: {"deep_risk": account_risk_failed},
        'social_limit_5': lambda: {"deep_risk": account_risk_failed},
        'downstream_captcha': lambda: {"deep_risk": account_risk_failed},
        'account_frequent_mobile_check': lambda: {"deep_risk": account_risk_failed},
    }

    while time.time() - start_time < timeout:
        matched = False
        # 用ocr识别账号密码错误界面，密码错误多次，弹窗会变，识别区域也略有区别
        is_pwd_error_page = ocrText(ENV, "is_pwd_error_page", (390, 1160, 940, 1215))
        is_pwd_error_page2 = ocrText(ENV, "is_pwd_error_page2", (315, 1120, 1000, 1180))
        is_pwd_error_words = ''
        is_pwd_error_words2 = ''
        for word in is_pwd_error_page:
            is_pwd_error_words += word[0]
        for word in is_pwd_error_page2:
            is_pwd_error_words2 += word[0]
        if '错误' in is_pwd_error_words or '密码' in is_pwd_error_words:
            monitor_task_status_v2(f"账密错误")
            return {'success': False, 'message': '登陆异常，账号密码错误', 'code': 'account_error'}
        if '错误' in is_pwd_error_words2 or '密码' in is_pwd_error_words2:
            monitor_task_status_v2(f"账密错误")
            return {'success': False, 'message': '登陆异常，账号密码错误', 'code': 'account_error'}
        if '网络' in is_pwd_error_words2:
            # 网络不稳定
            adc_touch((880, 1380), 0.5)
        if '版本过低' in is_pwd_error_words2:
            return {'success': False, 'message': 'QQ客户端版本过低，无法登陆', 'code': 'login_error'}
        if '全新回归' in is_pwd_error_words:
            monitor_task_status_v2('关闭弹窗')
            adc_touch((1255, 1200), 1, printLog=True)
        # 检查是否进入可直接返回页面，比如账号密码错误
        for scene_name in failures_scenes:
            template = scenes.get(scene_name)
            if kit_wait_find(template):
                return {'success': False, 'message': '登陆异常，账号密码错误', 'code': 'account_error'}
        if kit_wait_find(scenes['unable_to_login']):
            monitor_task_status_v2('登陆频繁登陆失败')
            return {'success': False, 'message': '登陆频繁，登陆失败', 'code': 'unable_to_login'}
        # 检查是否登陆成功
        if kit_wait_find(scenes['login_success']) or kit_wait_find(scenes['login_success_two']) or poco_qq_main():
            monitor_task_status_v2('登陆成功')
            return {'success': True, 'message': '登陆成功', 'code': 'success'}
        # 检查其他可能出现的场景并处理
        for scene_name, template in scenes.items():
            if kit_wait_find(template):
                if scene_name == 'account_risk' or scene_name == 'account_risk_2':
                    account_risk_failed = True
                handler = scene_handler.get(scene_name)
                if handler:
                    provider = param_providers.get(scene_name)
                    kwargs = provider() if provider else {}
                    try:
                        result = handler(**kwargs)
                        if result is not None:
                            return result
                    except Exception as e:
                        print(e)
                matched = True
                no_match_count = 0
                break
        if not matched:
            no_match_count += 1
            monitor_task_status_v2("登陆中", "")
        sleep(interval)
    if kit_wait_find(scenes['login_success']) or kit_wait_find(scenes['login_success_two']) or poco_qq_main():
        monitor_task_status_v2('登陆成功')
        return {'success': True, 'message': '登陆成功', 'code': 'success'}
    else:
        snapshotImg('login_error', catch_file_name)
        if account_risk_failed:
            return {'success': False, 'message': '深度风控登陆失败', 'code': 'deep_risk_control_login_failed'}
        else:
            return {'success': False, 'message': '登陆异常，登陆失败', 'code': 'login_error'}


def login_success():
    """
    不做处理，只返回登陆成功
    """
    return {'success': True, 'message': '登陆成功', 'code': 'success'}


def login_error():
    """
    不做处理，只返回登陆失败
    """
    return {'success': False, 'message': '登陆失败', 'code': 'login_error', }


def poco_qq_main():
    """
    通过poco元素定位首页
    """
    msg = poco(type="android.widget.TextView",
               text="消息").exists()
    contacts = poco(type="android.widget.TextView",
                    text="联系人").exists()
    if msg and contacts:
        monitor_task_status_v2('当前为QQ主页面')
        return True
    else:
        return False


def account_frequent():
    """
    账号操作频繁处理
    """
    monitor_task_status_v2('开始处理登陆频繁')
    login_freq_check_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768875442526.png", record_pos=(0.002, -0.013),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768875452251.png", record_pos=(0.007, -0.135),
                 resolution=(1350, 2400))
    ]
    login_freq_check = kit_wait_find_plus(login_freq_check_list, threshold=0.9)
    if login_freq_check:
        login_auth = kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768875466054.png", record_pos=(-0.149, 0.159),
                     resolution=(1350, 2400)))
        if login_auth:
            # 点击身份验证
            adc_touch(login_auth, 0.5)


def account_frequent_mobile_check(deep_risk=False):
    """
    身份验证点击手机验证
    """

    phone_captcha_page_check = kit_wait_find(
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768900444521.png", record_pos=(-0.23, -0.446),
                 resolution=(1350, 2400)))
    if phone_captcha_page_check:
        adc_touch(phone_captcha_page_check, 0.5)
        sleep(1)
        is_captcha_check_list = [
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817786611.png", record_pos=(-0.228, -0.15),
                     resolution=(1350, 2400)),
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768875320611.png", record_pos=(0.007, -0.147),
                     resolution=(1350, 2400))
        ]
        if kit_wait_find_plus(is_captcha_check_list, threshold=0.9):
            return
        for i in range(30):
            input_phone_check = kit_wait_find(
                Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768900664057.png",
                         record_pos=(-0.223, -0.668), resolution=(1350, 2400)))
            if input_phone_check:
                # 上行短信页面截图
                upstream_image = snapshotImg('upstream_image', catch_file_name, path=True)
                upstream_oss_pathes, upstream_oss_urls = upload_jym_oss_with_pathes([upstream_image])
                # 卖家手机截图
                seller_phone_img = snapshotImg('seller_phone_img', catch_file_name, path=True, LT=(12, 200),
                                               RB=(1350, 700))
                oss_pathes, oss_urls = upload_jym_oss_with_pathes([seller_phone_img])
                # 拼接手机号,llm和ocr双重验证
                seller_phone_content = get_seller_mobile()
                if not seller_phone_content:
                    continue
                return {'success': False, 'message': '需要验证', 'code': 'need_verify', 'need_seller_mobile': True,
                        'upstream_image': str(upstream_oss_urls[0]), 'seller_mobile_image': str(oss_urls[0]),
                        'seller_mobile_content': seller_phone_content}
            sleep(1)


def get_seller_mobile():
    """
    通过ocr和llm双重验证获取模糊的卖家手机号
    """
    user_prompt = '''
                请将图片中的数字提取出来， 并以json的格式将数字整理给我，
                注意：
                    1.返回json格式时，不要带有```json```的markdown的内容；
                    2.返回格式内容严格按照以下json格式,只用返回区服的名称，其他任何多余字符都不用返回，空格也不需要返回，示例如下：
                        {
                            "name": '180'
                        }
                    3.如果未识别到内容，返回结果如下
                        {
                            "name": ""
                        }
                    4.严格遵守以上要求
            '''
    llm_content1_img = snapshot_write(
        f"llm_content1",
        LT=(450, 400),
        RB=(520, 480)
    )
    llm_content2_img = snapshot_write(
        f"llm_content2",
        LT=(610, 400),
        RB=(670, 480)
    )

    _, llm_content1_img_url = image_upload(image=llm_content1_img)
    _, llm_content2_img_url = image_upload(image=llm_content2_img)
    llm_content1 = get_name_large_model_copy(llm_content1_img_url, prompt=user_prompt)
    llm_content2 = get_name_large_model_copy(llm_content2_img_url, prompt=user_prompt)

    if llm_content1 and llm_content2:
        seller_phone_content = f'{llm_content1}******{llm_content2}'
        monitor_task_status_v2(f'seller_mobile_{seller_phone_content}')
        return seller_phone_content
    else:
        return ''


def downstream_captcha(deep_risk=False):
    """
    账号下行短信返回处理
    """
    monitor_task_status_v2('开始处理下行短信')
    is_downstream_page = kit_wait_find(
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817858382.png", record_pos=(0.004, -0.207),
                 resolution=(1350, 2400)))
    # 490 980 870 1040
    is_downstream = ocrText(ENV, 'is_downstream', (490, 980, 870, 1040))
    is_downstream_words = ''
    for word in is_downstream:
        is_downstream_words += word[0]
    monitor_task_status_v2(is_downstream_words)
    if '发送' in is_downstream_words or '短信验证码' in is_downstream_words or is_downstream_page:
        # if is_downstream:
        adc_touch((650, 980), 0.5, printLog=True)
        sleep(1)
        snapshotImg('downstream_send', catch_file_name)
        if kit_wait_find(
                Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817882452.png", record_pos=(0.003, -0.676),
                         resolution=(1350, 2400))):
            return {'success': False, 'message': '需要验证', "verify_type": 'downstream', 'code': 'need_verify',
                    'need_seller_mobile': False}


def verify_captcha():
    """
    确认是否触发了验证码并处理
    """
    monitor_task_status_v2('开始检查图形验证码')
    is_captcha_check_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817786611.png", record_pos=(-0.228, -0.15),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768875320611.png", record_pos=(0.007, -0.147),
                 resolution=(1350, 2400))
    ]
    for try_count in range(5):
        is_captcha_check = kit_wait_find_plus(is_captcha_check_list)
        if is_captcha_check:
            code_img = snapshotImg(f'code_img_{try_count}', catch_file_name, path=True, LT=(280, 214), RB=(1081, 1039))
            url, res = ocr_image_by_check(code_img)
            if res:
                # 多种风控图，需要分开处理
                # 290 250
                captcha_type = check_captcha_type()
                monitor_task_status_v2(f'风控类型{captcha_type}')
                if captcha_type == 1:
                    box = res[0]["box"]
                    target_touch = (box[0][0] + 300, box[0][1] + 300)
                    adc_touch(target_touch, 0.5)
                    sleep(1)
                    snapshotImg(f'select_after_{try_count}', catch_file_name)
                    adc_touch((1000, 1000), 0.5)
                    # 点击确定后可能会有一定时间的延迟，需要重新设计验证码处理逻辑
                    sleep(0.5)
                if captcha_type == 2:
                    if try_count >= 3:
                        # 点击我不会尝试跳过风控
                        skip_verify()
                    else:
                        # 该情况点击验证时间比较长
                        for box in res:
                            target_box = (box['box'][0][0] + 300, box['box'][0][1] + 300)
                            adc_touch(target_box, 0.5, printLog=True)
                            sleep(random.uniform(1, 2))
                        snapshotImg(f'type_2_captcha{try_count}', catch_file_name)
                        adc_touch((1000, 1000), 0.5)
                        sleep(random.randint(10, 15))
                if captcha_type == 3:
                    monitor_task_status_v2('尝试跳过验证码')
                    skip_verify()
                snapshotImg(f'captcha_after_{try_count}', catch_file_name)
                captcha_succes_check_list = [
                    Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768810384776.png",
                             record_pos=(0.001, -0.624), resolution=(1350, 2400)),
                    Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768898269107.png",
                             record_pos=(-0.013, -0.219), resolution=(1350, 2400))
                ]
                if kit_wait_find_plus(captcha_succes_check_list):
                    sleep(3)
                    break
            else:
                if try_count >= 3:
                    # 点击我不会尝试跳过风控
                    skip_verify()
                # 验证失败会自动变更验证码图片，暂时屏蔽点击动作
                # adc_touch((660, 1000), 0.5)
                sleep(1)
                continue
        else:
            return
    else:
        return {'success': False, 'message': '登陆异常，图形验证码处理异常'}


def skip_verify():
    """
    点击我不会尝试跳过风控
    """
    if kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768817786611.png", record_pos=(-0.228, -0.15),
                     resolution=(1350, 2400))):
        adc_touch((380, 1010), 0.5)
        snapshotImg(f'no_captcha_page', catch_file_name)
        sleep(0.5)
        no_captcha_timeout = ocrText(ENV, "no_captcha_timeout", (500, 530, 840, 800))[0][0]
        try:
            sleep(int(no_captcha_timeout))
            captcha_succes_check_list = [
                Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768810384776.png", record_pos=(0.001, -0.624),
                         resolution=(1350, 2400)),
                Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1768898269107.png",
                         record_pos=(-0.013, -0.219), resolution=(1350, 2400))
            ]
            if kit_wait_find_plus(captcha_succes_check_list):
                sleep(3)
        except Exception as e:
            # 跳过失败，尝试点击回常规风控后，重新进入登陆循环逻辑
            sleep(0.5)
            adc_touch((380, 1010), 0.5)


def check_captcha_type():
    """
    检查当前风控类型
    """
    captcha_type = ocrText(ENV, "captcha_type", (290, 250, 740, 300))
    captcha_type_words = ''
    for word in captcha_type:
        captcha_type_words += word[0]
    if '最' in captcha_type_words:
        return 1
    if '所有' in captcha_type_words:
        return 2
    if '安全' in captcha_type_words or '验证' in captcha_type_words:
        return 3


def ocr_image_by_check(crop_pos_img_path):
    """
    验证码处理接口请求
    """
    monitor_print(f'---ocr_image_by_check: {crop_pos_img_path}')
    env = AppEnv.get_instance()

    if not crop_pos_img_path.startswith("http"):
        localFileList = []
        localFileList.append(crop_pos_img_path)
        _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
        if cdn_url_list:
            qufu_crop_img_url = cdn_url_list[0]
    else:
        qufu_crop_img_url = crop_pos_img_path

    resData = {}
    resData['requestId'] = str(int(time.time() * 1000000))
    resData['imageUrl'] = qufu_crop_img_url
    resData['recoType'] = "agent"
    resData['task'] = "腾讯物品验证码"
    risk_path = '/api/predict/lingxialgo_vision_agent_pre'
    scriptEnv = env.scriptEnv
    if (scriptEnv == 'local'):
        risk_path = "/api/predict/lingxialgo_vision_agent_pre"
    elif (scriptEnv == 'pre'):
        risk_path = "/api/predict/lingxialgo_vision_agent_pre"
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_agent'

    monitor_print(f'get_env_ocr_path: {risk_path}, env:{scriptEnv}')
    data = enhanced_easrequest(risk_path, resData, type=2)
    print('==============================', data)
    if data is not None and 'message' in data and ('status' in data['message']) and ('data' in data['message']):
        ocrResult = data['message']['data']
        status = data['message']['status']
        monitor_print(f'ocr_image_by_check_result:{status},{qufu_crop_img_url},{ocrResult}')
        return qufu_crop_img_url, ocrResult
    else:
        return qufu_crop_img_url, None


def version_update_tips():
    """
    检测QQ升级弹窗并关闭
    """
    tips_list = [
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1772604834260.png", record_pos=(-0.119, -0.288),
                 resolution=(1350, 2400)),
        Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769580346501.png", record_pos=(0.007, 0.41),
                 resolution=(1350, 2400))
    ]
    if kit_wait_find_plus(tips_list, threshold=0.9):
        monitor_task_status_v2('监测到升级弹窗，准备关闭')
        adc_touch((705, 1911), 0.5, printLog=True)
        close_button_check = kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769580468509.png", record_pos=(0.001, 0.638),
                     resolution=(1350, 2400)))
        if close_button_check:
            qq_touch(close_button_check, 1,
                     template=Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1769580468509.png",
                                       record_pos=(0.001, 0.638), resolution=(1350, 2400)))
        b_close_button = kit_wait_find(
            Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1772604906079.png", record_pos=(-0.002, 0.678),
                     resolution=(1350, 2400)))
        if b_close_button:
            qq_touch(b_close_button, 1,
                     template=Template(r"../../777724729_qq/777724729_qq_rebind.air/tpl1772604906079.png",
                                       record_pos=(-0.002, 0.678)))


def qq_touch(
        pos: Union[List, Tuple],
        sec=0.5,
        template=None,
        wait_after_first=2,
) -> None:
    """
    点击一次；若提供 template，则判断是否需要补点
    应对可能出现的点击失效
    """
    if wait_after_first is None:
        wait_after_first = sec

    adc_touch(pos, sec, printLog=True)

    if template is None:
        return

    # 给 UI 刷新一点时间，避免过快匹配误判
    if wait_after_first and wait_after_first > 0:
        sleep(wait_after_first)

    found = kit_wait_find(template)
    if found:
        adc_touch(pos, sec, printLog=True)


def ocrText(env, Name="", Region=(), returnState=True):
    try:
        textArr = ocr_keyword_return_pos(Region)
        lx_snapshot(env, f"adc_catch_ocr{Name}", crop_pos=Region, path=True)
        monitor_task_status_v2(f"ocr{Name}", f"{textArr}")
        if not textArr and returnState:
            monitor_task_status_v2("ocr识别为空", f"ocr识别{Name}为空", 10127)
            return [['']]
        return textArr
    except Exception as e:
        monitor_task_status_v2(f'ocr 识别异常-{e}')
        return [['']]
