from typing import Union, Tuple, List, Optional
from pathlib import Path
import traceback

import cv2
import numpy as np
from airtest.core.api import *
from airtest.core.error import DeviceConnectionError, AdbShellError

from utility.base.adc_environment import AppEnv

# 异常组
exception_group = (ConnectionResetError, OSError, DeviceConnectionError, AdbShellError)
# 时间戳
timeStamp = lambda: str(int(time.time() * 10 ** 6))
# catch名称格式化
catch_name = lambda write_name: f"adc_catch_{write_name}_{timeStamp()}"

def __monitor_print(desc):
    taskId = os.environ.get('taskId')
    game_name = os.environ.get('game_name')
    game_id = os.environ.get('game_id')
    game_platfrom = os.environ.get('game_platfrom')

    info = 'adc-safe-log--> '+'desc:'+desc + '; '

    if taskId:
        info = 'adc-safe-log--> '+ 'taskId:' + taskId + '; '

    if game_id is not None and len(game_id) > 0:
        info = info + 'gameId:' + game_id + '; '

    if game_platfrom is not None and len(game_platfrom) > 0:
        info = info + 'gamePlatform:' + game_platfrom + '; '

    if game_name is not None and len(game_name) > 0:
        info = info + 'game_name:' + game_name + '; '

    info = info + 'print_timestamp:' + timeStamp() + '; '
    info = info + 'desc:'+desc+'; '

    print(info + '\n')

def lx_safe_connect():
    """
    安全连接
    """
    system = AppEnv.get_instance().system_type
    exception = None
    for i in range(1):
        try:
            sleep(1)
            ip_port = device().uuid
            __monitor_print(f"第{i + 1}次重连：{ip_port}")
            if system == "android":
                connect_device(f"Android:///{ip_port}")
            if system == "yunyou_ios":
                connect_device(f"iOS:///{ip_port}")
            __monitor_print("重连成功")
            break
        except Exception as e:
            exception = e
            __monitor_print(f"第{i + 1}次重连失败：{traceback.format_exc()}")
    else:
        if exception is not None:
            __monitor_print(f"重连失败：{type(exception)}-{str(exception)}")
            raise exception

def lx_safe_snapshot(filename="snapshot", msg="", quality=None, max_size=None):
    """
    获取屏幕快照
    :param filename: 快照名称或保存路径
    :param msg: 描述
    :param quality: 质量
    :param max_size: 最大尺寸
    :return: numpy array image object
    """
    filename = f"{filename}"
    if filename == "snapshot":
        filename = f"{filename}_{timeStamp()}"
    if os.path.splitext(filename)[-1] not in ('.png', '.jpg'):
        filename = f"{filename}.jpg"
    exception = None
    for _ in range(3):
        try:
            snapshot(filename, msg=msg, quality=quality, max_size=max_size)
            file_path = Path(ST.LOG_DIR).resolve() / filename
            if file_path.exists():
                return cv2.imread(str(file_path))
            elif Path(filename).resolve().exists():
                return cv2.imread(filename)
            break
        except AttributeError as e:
            __monitor_print(f"属性错误：{traceback.format_exc()}", )
            raise e
        except Exception as e:
            exception = e
            __monitor_print(f"截图失败, 尝试重连：{type(e)}-{traceback.format_exc()}")
            lx_safe_connect()
    else:
        if exception is not None:
            raise exception

def lx_safe_touch(pos: Union[List, Tuple], sec=0.1, printLog=False, touchFunc=None):
    """
    点击事件
    :param pos: 位置
    :param sec: 点击后等待
    :param printLog: 打印日志
    :param touchFunc: 点击函数
    :return: null
    """
    exception = None
    for _ in range(3):
        try:
            G.DEVICE.touch(pos) if not callable(touchFunc) else touchFunc()
            if printLog: __monitor_print(f"lx_safe_touch: {pos}")
            if sec > 0: sleep(sec)
            return
        except Exception as e:
            exception = e
            __monitor_print(f"点击失败, 尝试重连：{type(e)}-{traceback.format_exc()}")
            lx_safe_connect()
    else:
        if exception is not None:
            raise exception

def lx_safe_wait(filename: Template, timeout=2, interval=0.5, printLog=False) -> Optional[Tuple]:
    """
    等待目标匹配事件
    :param filename: 等待的目标对象
    :param timeout: 等待目标匹配的超时时间
    :param interval: 尝试查找匹配的时间间隔
    :param printLog: 打印日志
    :return: pos
    """
    exception = None
    for _ in range(3):
        try:
            pos = wait(filename, timeout, interval)
            if printLog: __monitor_print(f"lx_safe_wait: {pos} {filename}")
            return pos
        except TargetNotFoundError:
            return
        except Exception as e:
            exception = e
            __monitor_print(f"等待失败, 尝试重连：{type(e)}-{traceback.format_exc()}")
            lx_safe_connect()
    else:
        if exception is not None:
            raise exception

def lx_safe_exists(filename: Template, printLog=False) -> Optional[Tuple]:
    """
    检查目标是否存在
    :param filename: 待检查目标
    :param printLog: 打印日志
    :return: 目标位置
    """
    exception = None
    for _ in range(3):
        try:
            pos = exists(filename)
            if printLog: __monitor_print(f"lx_safe_exists: {pos} {filename}")
            return pos
        except TargetNotFoundError:
            return
        except Exception as e:
            exception = e
            __monitor_print(f"检查失败, 尝试重连：{type(e)}-{traceback.format_exc()}")
            lx_safe_connect()
    else:
        if exception is not None:
            raise exception

def lx_safe_wait_touch(filename: Template, alt_v: Union[Tuple, List]=None, timeout=2, interval=0.5, sec=1, printLog=False) -> Optional[Tuple]:
    """
    等待目标匹配并点击
    :param filename: 等待的目标对象
    :param alt_v: 匹配到目标后点击位置
    :param timeout: 等待目标匹配的超时时间
    :param interval: 尝试查找匹配的时间间隔
    :param sec: 点击后等待
    :param printLog: 打印日志
    :return: 目标位置
    """
    exception = None
    for _ in range(3):
        try:
            if pos := wait(filename, timeout, interval):
                touch(alt_v or pos)
                if printLog: __monitor_print(f"lx_safe_wait_touch: {pos} {filename}")
                if sec > 0: sleep(sec)
                return pos
        except TargetNotFoundError:
            return
        except Exception as e:
            exception = e
            __monitor_print(f"等待失败, 尝试重连：{type(e)}-{traceback.format_exc()}")
            lx_safe_connect()
    else:
        if exception is not None:
            raise exception

def lx_safe_exists_touch(filename: Template, alt_v: Union[Tuple, List]=None, sec=1, printLog=False) -> Optional[Tuple]:
    """
    检查目标是否存在并点击
    :param filename: 待检查目标
    :param alt_v: 匹配到目标后点击位置
    :param sec: 点击后等待
    :param printLog: 打印日志
    :return: 目标位置
    """
    exception = None
    for _ in range(3):
        try:
            if pos := exists(filename):
                touch(alt_v or pos)
                if printLog: __monitor_print(f"lx_safe_exists_touch: {pos} {filename}")
                if sec > 0: sleep(sec)
                return pos
        except TargetNotFoundError:
            return
        except Exception as e:
            exception = e
            __monitor_print(f"检查失败, 尝试重连：{type(e)}-{traceback.format_exc()}")
            lx_safe_connect()
    else:
        if exception is not None:
            raise exception
