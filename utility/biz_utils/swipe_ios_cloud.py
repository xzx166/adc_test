import logging

import requests
from airtest.core.api import *

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

__step_dict = lambda x, y, offset: {"x": float(x), "y": float(y), "offset": offset}
def __swipe_move(from_xy, to_xy, duration, steps=5, hold_sec=0.5):
    from_x, from_y = from_xy
    to_x, to_y = to_xy

    ret = []
    interval = duration / (steps + 1)
    delta_x, delta_y = to_x - from_x, to_y - from_y

    for i in range(1, steps):
        x = from_x + delta_x * i / steps
        y = from_y + delta_y * i / steps
        ret.append(__step_dict(x, y, interval * i))
    ret.append(__step_dict(to_x, to_y, duration))
    ret.append(__step_dict(to_x, to_y, duration + hold_sec))
    return ret

def __swipe_along(coordinates_list, duration, steps=5, hold_sec=0.5):
    from pprint import pprint

    from_xy = coordinates_list[0]
    swipe_events = [__step_dict(*from_xy, 0)]
    for to_xy in coordinates_list[1:]:
        swipe_events.extend(__swipe_move(
            from_xy,
            to_xy,
            duration=duration,
            steps=steps,
            hold_sec=hold_sec))
        from_xy = to_xy
    return swipe_events

def yunyou_ios_swipe(start_point, end_point, duration=1, steps=5, hold_sec=0.5, sec=0, dev=None):
    """
    滑动事件 iOS云机
    :param start_point: 开始点
    :param end_point: 结束点
    :param duration: 滑动持续时间
    :param sec: 滑动后等待
    :param steps: 滑动步数 (yunyou_ios)
    :return:
    """
    DEV = dev
    if DEV.uuid.startswith("http+usbmux"):
        swipe(start_point, end_point, duration=duration)
        sleep(sec)
        return

    deviceUrl = f"{DEV.uuid}/wda/ttg/swipe"
    swipe_events = __swipe_along(
        [start_point, end_point],
        duration=duration,
        steps=steps,
        hold_sec=hold_sec)
    display_info = DEV.display_info
    width = display_info['width']
    height = display_info['height']
    if display_info["orientation"] == "LANDSCAPE":
        width, height = height, width
    payload = {
        "path": swipe_events,
        "xRange": width,
        "yRange": height,
    }
    requests.post(deviceUrl, json=payload)
    sleep(sec)