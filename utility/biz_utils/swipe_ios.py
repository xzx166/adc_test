import datetime
import os
import time
import traceback
from time import sleep
from pathlib import Path

from civita import Client, SessionEvent
from civita.exceptions import *
import concurrent.futures
import requests


class ENV:
    iOSDeviceId = ""

class AppDynamicInfo:
    __instance = None

    def __init__(self):
        self.iosHasKicked = False
        self.iosClient = None
        self.iosCb = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

class Application:
    def init_mds(self):
        mds_client_token = "8r0864y6y8g"
        client = Client(mds_client_token)
        print("---iOS设备_init_client", "iOS设备_init_client")

        AppDynamicInfo.get_instance().iosClient = client
        AppDynamicInfo.get_instance().iosHasKicked = False

        # 启动civita-client-agent, 只有需要使用ADB或者WDA时，才需要调用此方法
        # civita-client-agent是全局共享的，不需要反复启动
        print("---iOS设备_setup_device_agent_start", "iOS设备_setup_device_agent_start")

        def retry_setup_device_agent(cur_client):
            agent_response = False
            for i in range(4):
                try:
                    cur_client.setup_device_agent()
                    print(f"---iOS设备_setup_device_agent", f"")
                    print(f"---iOS设备_setup_device_agent")

                    print("---iOS设备_setup_device_agent成功", f"")
                    agent_response = True
                    break
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    print("---iOS设备_setup_device_agent_Except", f"{str(e)}_{error_traceback}")
                    sleep(15)

            return agent_response

        real_agent_response = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(retry_setup_device_agent, client)
            try:
                real_agent_response = future.result(timeout=60)  # 设置超时时间
            except concurrent.futures.TimeoutError:
                future.cancel()
                print(f"------iOS设备_setup_device_agent_timeout")
                print("------iOS设备_setup_device_agent_timeout", "---iOS设备_setup_device_agent超时")
                exit()

        if real_agent_response is False:
            print("---iOS设备_setup_device_agent失败", f"")
            exit()

        def cb(evt: SessionEvent, *args):
            print("---iOS设备_cb_start", f"")
            if SessionEvent.EVENT_DEV_ADBDISCONNECTED == evt:
                print("---iOS设备_adb_disconnected", f"")
            elif SessionEvent.EVENT_DEV_WDAPORTCLOSED == evt:
                print("---iOS设备_wda_disconnected", f"")
            elif SessionEvent.EVENT_DEV_KICKED == evt:
                AppDynamicInfo.get_instance().iosHasKicked = True

        print("---iOS设备_setup_cb", "iOS设备_setup_cb")
        AppDynamicInfo.get_instance().iosCb = cb

    def connect_mds(self):
        client = AppDynamicInfo.get_instance().iosClient

        AppDynamicInfo.get_instance().iosHasKicked = False

        print("---连接iOS设备_start", "连接iOS设备")
        # 请求获取一台设备，并建立会话连接
        session_connect = None
        session_connect = self.connect_mds_session(client)

        if session_connect is None:
            print("---iOS设备session连接失败", f"")
            exit()

        self.config_mds_session(session_connect, AppDynamicInfo.get_instance().iosCb)

    def connect_mds_session(self, client):
        # 请求获取一台设备，并建立会话连接
        session_connect = None
        def retry_connect(client):
            cur_session_connect = None
            for i in range(8):
                try:
                    print(f"---连接iOS设备_连接_{i}", f"---")
                    cur_session_connect = client.request_device_session(selector={'deviceid': ENV.iOSDeviceId})
                    if cur_session_connect is not None:
                        print("---连接iOS设备_连接成功", f"")
                        break
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    print(f"---连接iOS设备_连接失败_{str(e)}", f"{error_traceback}")
                    sleep(15*i)

            return cur_session_connect

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(retry_connect, client)
            try:
                session_connect = future.result(timeout=60*5)  # 设置超时时间
            except concurrent.futures.TimeoutError:
                future.cancel()
                print(f"---连接iOS设备_session_timeout")
                print("---连接iOS设备_session_timeout", "连接iOS设备超时")
                exit()

        if session_connect is None:
            print("---iOS设备session连接失败", f"")
            exit()

        return session_connect

    def config_mds_session(self, session_connect, cb):
        # 设置会话事件回调
        session_connect.set_event_listener(cb)
        print("---iOS设备_set_event_listener", f"")
        print(f"---iOS设备_set_event_listener")

        # 这个代码， 会导致进程无法结束，另外需要确定到底是什么功能
        # session_connect.setup_display_touch_channel()

        self.config_mds_wda(session_connect)

        ENV.iOS_session_connect = session_connect
        device_info = session_connect.device
        display_width = device_info["display_width"]
        screen_width = device_info["deviceModel"]["screen_width"]
        screen_height = device_info["deviceModel"]["screen_height"]
        if os.environ.get("screenRotation", "").lower().startswith("h"):
            os.environ.update(screenWidth=str(screen_height), screenHeight=str(screen_width))
        else:
            os.environ.update(screenWidth=str(screen_width), screenHeight=str(screen_height))
        os.environ.update(posDivisor=str(screen_width // display_width))
        print(f"---iOS_session_id: {session_connect.sessionid}")

    def config_mds_wda(self, session_connect):
        # 连接远程ADB，连接成功以后，才能通过ADB使用远程设备
        # 成功连接adb的返回形如 {'success': True, 'adbdPort': 65235, 'adbHostPort': '5037'}
        conn = session_connect.setup_wda_proxy()
        print("---iOS设备_setup_wda_proxy", f"")
        print(f"---iOS设备_setup_wda_proxy: {conn}")

        if conn.get('success') is False:
            raise Exception("setup_wda_proxy failed")

        wda_port = conn.get('wdaPort')
        if wda_port is None:
            raise Exception("wda_port is None")

        ENV.iOS_wda_port = wda_port

    def start(self):
        self.init_mds()
        self.connect_mds()

# 强制释放设备
def force_release_device():
    client = AppDynamicInfo.get_instance().iosClient
    AppDynamicInfo.get_instance().iosHasKicked = False
    # 本地调试的情况下，不用强制释放设备
    print("---强制释放iOS设备_start", "强制释放iOS设备_start")
    for i in range(3):
        try:
            release_response = client.release_device(ENV.iOSDeviceId)
            print("---强制释放iOS设备", f"---")
            if release_response is not None:
                print("---强制释放iOS设备成功", f"")
                break
        except Exception as e:
            error_traceback = traceback.format_exc()
            print("---强制释放iOS设备_Except", f"{str(e)}_{error_traceback}")
            sleep(2)

def modaoshi_action_swipe(wda_port, data):
    url = f"http://127.0.0.1:{wda_port}/mds/multiPathGesture"  # 替换为你实际的端点
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)

def ios_swipe(start_point, end_point, sec=0, duration=1.0, offset=0.5):
    is_accurate_swipe = True
    screenWidth = int(os.environ.get("screenWidth", "0"))
    screenHeight = int(os.environ.get("screenHeight", "0"))
    posDivisor = int(os.environ.get("posDivisor"))
    if screenWidth > screenHeight:
        start_point = screenHeight - start_point[1], start_point[0]
        end_point = screenHeight - end_point[1], end_point[0]
    if is_accurate_swipe:
        swipe_list = [
            {"x": start_point[0] / posDivisor, "y": start_point[1] / posDivisor, "offset": 0},
            {"x": end_point[0] / posDivisor, "y": end_point[1] / posDivisor, "offset": duration},
            {"x": end_point[0] / posDivisor, "y": end_point[1] / posDivisor, "offset": duration + offset}
        ]
        modaoshi_action_swipe(wda_port=ENV.iOS_wda_port, data={'path': swipe_list})
        sleep(sec)

def ios_screenshot(save_path):
    """
    获取屏幕快照 ios
    """
    filename = f"{datetime.datetime.now().strftime('tpl%Y%m%d%H%M%S')}.png"
    filepath = Path(save_path) / filename

    session_ctrl = ENV.iOS_session_connect
    data = session_ctrl.screenshot()
    if image_url := data.get("full_url"):
        response = requests.get(image_url)
        content = response.content
        filepath.write_bytes(content)
        print(f"Save to {filepath}")
