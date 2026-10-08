
"""
换绑工具
"""
import random
import traceback
import socket


from airtest.core.api import shell,connect_device

from utility.base.adc_environment import AppEnv
from utility.base.adc_monitor import monitor_print, monitor_task_status_v2


PROVINCE_CODE_MAP = {
    "北京市": "11",
    "天津市": "12",
    "河北省": "13",
    "山西省": "14",          # 注意：这是山西（ShanXi_）
    "内蒙古自治区": "15",
    "辽宁省": "21",
    "吉林省": "22",
    "黑龙江省": "23",
    "上海市": "31",
    "江苏省": "32",
    "浙江省": "33",
    "安徽省": "34",
    "福建省": "35",
    "江西省": "36",
    "山东省": "37",
    "河南省": "41",
    "湖北省": "42",
    "湖南省": "43",
    "广东省": "44",
    "广西壮族自治区": "45",
    "海南省": "46",
    "重庆市": "50",
    "四川省": "51",
    "贵州省": "52",
    "云南省": "53",
    "西藏自治区": "54",
    "陕西省": "61",          # 注意：这是陕西（ShanXi）
    "甘肃省": "62",
    "青海省": "63",
    "宁夏回族自治区": "64",
    "新疆维吾尔自治区": "65"
}

def get_free_port():
    """
    获取电脑空闲端口
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # 绑定到任意地址，端口由系统分配
        s.listen(1)
        port = s.getsockname()[1]
    return port

def rebind_start_vpn(packages_name, **kwargs):
    """
    文档地址：https://alidocs.dingtalk.com/i/nodes/R1zknDm0WRboLg99UB7r4R2pWBQEx5rG?cid=62736594197&rnd=0.9608144020026473&utm_source=im&utm_scene=person_space&iframeQuery=utm_medium%3Dportal_main_colum_create%26utm_source%3Dportal&utm_medium=im_card&corpId=ding482919750e0d871724f2f5cc6abecb85
    换绑 启动vpn和切换vpn
    :param area_id: 指定地区名称 str
    :param packages_name: 指定包名
    :param port :指定端口
    :return: True 启动/切换成功 False: 启动/切换失败
    """
    area_id = kwargs.get("area_id", "")
    if area_id:
        area_id = PROVINCE_CODE_MAP.get(area_id, "")
        monitor_task_status_v2(f"ai换绑切换地区ip：{area_id}")
    period = kwargs.get("period", "3")
    port = kwargs.get("port","20818")
    sid = kwargs.get("sid", "")
    if not sid:
        sid = random.randint(0, 1000)
    if not area_id:
        # 省份代码列表
        province_codes = [11, 12, 13, 14, 15, 21, 22, 23, 31, 32, 33, 34, 35,
                          36, 37, 41, 42, 43, 44, 45, 46, 50, 51, 52, 53, 54,
                          61, 62, 63, 64, 65]
        area_id = random.choice(province_codes)
        monitor_task_status_v2(f"ai换绑切换地区ip：{area_id}")
    start_vpn_cmd = f"""
    am start-foreground-service -n com.jym.x.engine.app/com.ssrlive.socksdroid.VpnStarterService --es server "h384.kdltpspro.com" --ei port {port} --es username "t13065003207797-pool-q10-period-{period}-prov-{area_id}-sid-{sid}" --es password "5xpvdgua" --es allowed_apps "{packages_name}"
    """
    try:
        shell(start_vpn_cmd)

    except Exception as e:
        monitor_task_status_v2(f"启动vpn异常：{traceback.format_exc()}")
        return False
    monitor_task_status_v2(f"启动vpn成功,{packages_name},cmd:{start_vpn_cmd}")
    return True

def rebind_close_vpn():
    """
    关闭
    :param packages_name:
    :return:
    """
    try:

        close_vpn_cmd = """
        am start-foreground-service -a "stop" -n com.jym.x.engine.app/com.ssrlive.socksdroid.VpnStarterService
        """
        monitor_task_status_v2(f"关闭vpn：{close_vpn_cmd}")
        shell(close_vpn_cmd)

    except Exception as e:

        monitor_print(f"关闭vpn失败请重试：{traceback.format_exc()}")
        return False
    monitor_print("关闭vpn成功")
    return True


if __name__ == '__main__':
    device = connect_device("android:///")  # Android设备
    rebind_start_vpn("com.mmbox.xbrowser")



