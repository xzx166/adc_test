import time

from airtest.aircv import aircv
from airtest.core.android.touch_methods.base_touch import BaseTouch, DownEvent, SleepEvent, UpEvent, MoveEvent, \
    MotionEvent
from airtest.core.api import *
from airtest.core.helper import logwrap
from airtest.utils.logger import get_logger
from airtest.utils.snippet import on_method_ready, ready_method
from poco.utils.track import MotionTrack, track_sampling
LOGGING = get_logger(__name__)

# defualt_screen_method = "MINICAP"
# G.DEVICE.screen_proxy = "JAVACAP"
@logwrap
def snapshot(filename=None, msg="", quality=None, max_size=None, ensure_orientation=True):
    """自定义截图"""
    if not quality:
        quality = ST.SNAPSHOT_QUALITY
    if not max_size and ST.IMAGE_MAXSIZE:
        max_size = ST.IMAGE_MAXSIZE
    if filename:
        if not os.path.isabs(filename):
            logdir = ST.LOG_DIR or "."
            filename = os.path.join(logdir, filename)
        # print(ScreenProxy.SCREEN_METHODS)
        # 从self.SCREEN_METHODS中，逆序取出可用的方法
        curent_screen_method = G.DEVICE.screen_proxy.screen_method
        # print(f"当前截图模式: {G.DEVICE.screen_proxy.screen_method}")
        screen = G.DEVICE.snapshot(ensure_orientation=ensure_orientation)
        if screen is None or screen.size == 0:
            for screen_method, screen_proxy in reversed(G.DEVICE.screen_proxy.SCREEN_METHODS.items()):
                if isinstance(curent_screen_method, screen_proxy):
                    continue
                print(f"切换截图模式: {screen_method}, {screen_proxy}")
                G.DEVICE.screen_proxy = screen_method
                screen = G.DEVICE.snapshot(ensure_orientation=ensure_orientation)
                if screen is not None and screen.size != 0:
                    break
        if screen is None or screen.size == 0:
            raise RuntimeError("截图错误, 截图空")
        aircv.imwrite(filename, screen, quality, max_size=max_size)
        return try_log_screen(screen, quality=quality, max_size=max_size)
    else:
        return try_log_screen(quality=quality, max_size=max_size)

# defualt_screen_method = "MINICAP"
# G.DEVICE.screen_proxy = "JAVACAP"
# @logwrap
# def snapshot(filename=None, msg="", quality=None, max_size=None, ensure_orientation=True):
#     """自定义截图"""
#     print(f"当前截图模式: {G.DEVICE.screen_proxy.screen_method}")
#     if not quality:
#         quality = ST.SNAPSHOT_QUALITY
#     if not max_size and ST.IMAGE_MAXSIZE:
#         max_size = ST.IMAGE_MAXSIZE
#     if filename:
#         if not os.path.isabs(filename):
#             logdir = ST.LOG_DIR or "."
#             filename = os.path.join(logdir, filename)
#         # print(ScreenProxy.SCREEN_METHODS)
#         # 从self.SCREEN_METHODS中，逆序取出可用的方法
#         # curent_screen_method = G.DEVICE.screen_proxy.screen_method
#         # print(f"当前截图模式: {G.DEVICE.screen_proxy.screen_method}")
#         max_try = 3
#         while max_try > 0:
#             screen = G.DEVICE.snapshot(ensure_orientation=ensure_orientation)
#             if screen is None or screen.size == 0:
#                 print("截图错误, 截图空")
#                 continue
#             break
#         if screen is None or screen.size == 0:
#             raise RuntimeError("截图错误, 截图空")
#         aircv.imwrite(filename, screen, quality, max_size=max_size)
#         return try_log_screen(screen, quality=quality, max_size=max_size)
#     else:
#         return try_log_screen(quality=quality, max_size=max_size)


class CustomScreenshotEvent(MotionEvent):
    def __init__(self, filename):
        self.filename = filename

    def getcmd(self, transform=None):
        return None



class CustomEvent:
    def __init__(self, dev, default_pressure=50):
        self.dev = dev
        self.default_pressure = default_pressure


    def __swipe_move(self, tuple_from_xy, tuple_to_xy, duration=0.8, steps=5, screenshot=False):
        """
        Return a sequence of swipe motion events (only MoveEvent)
        Returns:
            [MoveEvent(from_x, from_y), ..., MoveEvent(to_x, to_y)]
        """
        from_x, from_y = tuple_from_xy
        to_x, to_y = tuple_to_xy

        ret = []
        interval = float(duration) / (steps + 1)

        for i in range(1, steps):
            ret.append(MoveEvent((from_x + (to_x - from_x) * i / steps,
                                  from_y + (to_y - from_y) * i / steps)))
            ret.append(SleepEvent(interval))
            if screenshot:
                if abs(to_x - from_x) > 10 or abs(to_y - from_y) > 10:
                    ret.append(CustomScreenshotEvent(f"swipe_step_{i}_{str(int(time.time() * 1000000))}.jpg"))
        ret += [MoveEvent((to_x, to_y), pressure=self.default_pressure), SleepEvent(interval)]
        return ret

    def install_and_setup(self):
        return self.dev.touch_proxy.install_and_setup()

    @on_method_ready('install_and_setup')
    def perform(self, motion_events, interval=0.01):
        """
        Perform a sequence of motion events including: UpEvent, DownEvent, MoveEvent, SleepEvent

        Args:
            motion_events: a list of MotionEvent instances
            interval: minimum interval between events

        Returns:
            None
        """
        for event in motion_events:
            if isinstance(event, SleepEvent):
                time.sleep(event.seconds)
            elif isinstance(event, CustomScreenshotEvent):
                snapshot(filename=event.filename, msg="swipe screenshot", quality=None, max_size=None)
            else:
                cmd = event.getcmd(transform=self.dev.touch_proxy.transform_xy)
                self.dev.touch_proxy.handle(cmd)
                time.sleep(interval)

    def swipe_along(self, coordinates_list, duration=0.8, steps=5, screenshot_name=None):
        """
        自定义滑动,截图
        :param coordinates_list:
        :param duration:
        :param steps:
        :param screenshot_name:
        :return:
        """
        tuple_from_xy = coordinates_list[0]
        swipe_events = [DownEvent(tuple_from_xy, pressure=self.default_pressure), SleepEvent(0.1)]
        for tuple_to_xy in coordinates_list[1:]:
            swipe_events += self.__swipe_move(tuple_from_xy, tuple_to_xy, duration=duration, steps=steps)
            tuple_from_xy = tuple_to_xy
        if screenshot_name:
            swipe_events.append(CustomScreenshotEvent(screenshot_name))
        swipe_events.append(UpEvent())
        self.perform(swipe_events)

    def swipe_along_return_screenshot(self, coordinates_list, duration=0.8, steps=5):
        """
        自定义滑动,截图
        :param coordinates_list:
        :param duration:
        :param steps:
        :param screenshot_name:
        :return:
        """
        tuple_from_xy = coordinates_list[0]
        swipe_events = [DownEvent(tuple_from_xy, pressure=self.default_pressure), SleepEvent(0.1)]
        swipe_events.append(CustomScreenshotEvent(f"swipe_step_start_{str(int(time.time() * 1000000))}.jpg"))
        for tuple_to_xy in coordinates_list[1:]:
            swipe_events += self.__swipe_move(tuple_from_xy, tuple_to_xy, duration=duration, steps=steps, screenshot=True)
            tuple_from_xy = tuple_to_xy
        swipe_events.append(UpEvent())
        swipe_events.append(CustomScreenshotEvent(f"swipe_step_end_{str(int(time.time() * 1000000))}.jpg"))
        self.perform(swipe_events)
        screenshot_name_list = []
        for item_event in swipe_events:
            if isinstance(item_event, CustomScreenshotEvent):
                screenshot_name_list.append(item_event.filename)
        return screenshot_name_list



class CustomMotionTrack(MotionTrack):
    def __init__(self, points=None, speed=0.4, up=True):
        super(CustomMotionTrack, self).__init__(points=points, speed=speed)
        self.up = up

    def discretize(self, contact_id=0, accuracy=0.004, dt=0.001):
        """
        Sample this motion track into discretized motion events.

        Args:
            contact_id: contact point id
            accuracy: motion minimum difference in space
            dt: sample time difference
        """

        if not self.event_points:
            return []

        events = []
        action_dt = accuracy / self.speed
        dt = dt or action_dt

        ep0 = self.event_points[0]
        for _ in range(int(ep0[0] / dt)):
            events.append(['s', dt])
        events.append(['d', ep0[1], contact_id])
        for i, ep in enumerate(self.event_points[1:]):
            prev_ts = self.event_points[i][0]
            curr_ts = ep[0]
            p0 = self.event_points[i][1]
            p1 = ep[1]
            if p0 == p1:
                # hold
                for _ in range(int((curr_ts - prev_ts) / dt)):
                    events.append(['s', dt])
            else:
                # move
                dpoints = track_sampling([p0, p1], accuracy)
                for p in dpoints:
                    events.append(['m', p, contact_id])
                    for _ in range(int(action_dt / dt)):
                        events.append(['s', dt])
        if self.up:
            events.append(['u', contact_id])
        return events


