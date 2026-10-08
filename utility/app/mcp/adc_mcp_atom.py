# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

from utility.base.adc_api import *
from utility.base.adc_environment import *
from utility.base.adc_monitor import *

def mcp_click(pos, sec=0, combo=1):
    """    点击
    :param pos: 坐标
    :param sec: 延迟
    :param combo: 连击
    """
    monitor_print(f"---mcp_click: {pos}, {sec}, {combo}")
    adc_touch(pos, sec, combo)

def mcp_swipe(start_pos, end_pos, duration=0.5):
    """    滑动
    :param start_pos: 开始坐标
    :param end_pos: 结束坐标
    :param sec: 延迟
    :param steps: 步数
    """
    monitor_print(f"---mcp_swipe: {start_pos}, {end_pos}, {duration}")
    adc_swipe(start_pos, end_pos, duration)


def mcp_snapshot(filename = "snapshot"):
    """    截图
    :param filename: 截图文件名
    """
    monitor_print(f"---mcp_snapshot: {filename}")
    adc_snapshot(filename)

def mcp_start_app(app_id):
    """    启动游戏
    :param app_id: 游戏id
    """
    monitor_print(f"---mcp_start_app: {app_id}")
    env = AppEnv.get_instance()
    monitor_task_status(env, "启动游戏", f"启动{app_id}")
    if env.system_type == "android":
        start_app(f"{app_id}")
    else:
        session_ctrl = env.iOS_session_connect
        session_ctrl.open_app(pkg=app_id)

def mcp_close_app(app_id):
    """    关闭游戏
    :param app_id: 游戏id
    """
    monitor_print(f"---mcp_close_app: {app_id}")
    env = AppEnv.get_instance()
    monitor_task_status(env, "关闭游戏", f"关闭{app_id}")
    if env.system_type == "android":
        stop_app(f"{app_id}")
    else:
        session_ctrl = env.iOS_session_connect
        session_ctrl.close_app(pkg=app_id)

def mcp_input(text):
    """    输入
    :param text: 输入文本
    """
    monitor_print(f"---mcp_input: {text}")
    adc_input(text)

def mcp_sleep(sec):
    """    等待
    :param sec: 等待时间
    """
    monitor_print(f"---mcp_sleep: {sec}")
    sleep(sec)


def mcp_home():
    """
    回到首页
    """
    monitor_print(f"---mcp_home")
    adc_home()

def mcp_session_end():
    """
    结束会话
    """
    monitor_print(f"---mcp_session_end")



