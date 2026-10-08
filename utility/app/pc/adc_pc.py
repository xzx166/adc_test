from airtest.core.api import *

from utility.app.pc.keyboard import *
from utility.utility_header import *
from utility.base.adc_api import *
from utility.base.adc_monitor import *


def setPCScreenOrientation():
    """设置屏幕方向"""
    shell("settings put system accelerometer_rotation 0")
    shell("settings put system user_rotation 0")
    shell("settings put system accelerometer_rotation 1")
    sleep(2)

def connectPCDeviceByQQBrowser(url, sec=20):
    """
    连接PC设备(QQ浏览器), 仅限本地测试使用
    :param url: pc url
    :param sec: 连接后等待
    """
    packageName = "com.tencent.mtt"
    setPCScreenOrientation()
    # 输入url
    monitor_task_status_v2("连接PC设备 - QQ Browser", url)
    shell(f"am start -S -a android.intent.action.VIEW -d \"{url}\" -p \"{packageName}\"")
    sleep(sec)
    monitor_task_status_v2("连接PC设备 - QQ Browser", "按F12切换全屏")
    press_f12()
    sleep(2)
    # 10217 无可用PC设备

def connectPCDevice(url, sec=12):
    """
    连接PC设备
    :param url: pc url
    :param sec: 连接后等待
    """
    monitor_task_status_v2("连接PC设备 - Android Demo", url)
    shell(f"am start -a com.ttg.demoh5.view --es action \"load\" --es url \"{url}\"")
    monitor_task_status_v2("连接PC设备 - Android Demo", "android demo 生产环境 gameid：2009267")
    sleep(sec)
    if adc_wait("tpl20260408165913.png", timeout=1, is_try=True):
        monitor_task_status_v2("连接PC设备 - Android Demo", "无可用PC设备", 10217)
        lx_break_app(desc='无可用PC设备', ext_info={'key':'10217'})

def disconnectPCDevice():
    """
    断开PC设备
    """
    monitor_task_status_v2("断开PC设备")
    shell("am start -a com.ttg.demoh5.view --es action \"stop\"")
