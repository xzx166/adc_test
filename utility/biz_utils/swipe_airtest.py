from airtest.core.api import *
from airtest.core.android.touch_methods.base_touch import DownEvent, MoveEvent, SleepEvent, UpEvent
import logging
logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

DEV = device()
display_info = DEV.display_info
width = display_info['width']
height = display_info['height']
screen_vertical = lambda: DEV.display_info["orientation"] in (1, 3)
SCREENSIZE = (height, width) if screen_vertical() else (width, height)
SCREENHALF = SCREENSIZE[0] // 2, SCREENSIZE[1] // 2
SCREENBOX = (0, 0), SCREENSIZE

# Airtest滑动
class SwipeAirtest:
    def __init__(self, start_point, delta_y=0.0, delta_x=0.0, end_point=None, offset=None, duration=None, hold_sec=0.5, sec=0.5, steps=5):
        self.start_point = start_point
        self.end_point = end_point
        self.delta_y = delta_y
        self.delta_x = delta_x
        self.hold_sec = hold_sec
        self.sec = sec
        self.offset = offset
        self.duration = duration
        self.start_point_ = None
        self.steps = steps
        self.screen_vertical = screen_vertical()

    def processing(self):
        # 竖屏
        if self.screen_vertical:
            self.start_point_ = self.start_point[1], SCREENHALF[0] - self.start_point[0] + SCREENHALF[0]
            if not self.end_point:
                self.end_point = self.start_point_[0] + self.delta_y, self.start_point_[1] - self.delta_x
        # 横屏
        else:
            if not self.end_point and any((self.delta_x, self.delta_y)):
                self.end_point = self.start_point[0] + self.delta_x, self.start_point[1] + self.delta_y

    @staticmethod
    def __swipe_move(from_xy, to_xy, duration, steps=5):
        from_x, from_y = from_xy
        to_x, to_y = to_xy

        ret = []
        interval = duration / (steps + 1)
        delta_x, delta_y = to_x - from_x, to_y - from_y

        for i in range(1, steps):
            ret.append(MoveEvent((from_x + delta_x * i / steps, from_y + delta_y * i / steps)))
            ret.append(SleepEvent(interval))
        ret.extend([MoveEvent((to_x, to_y)), SleepEvent(interval)])
        return ret

    def __swipe_along(self, coordinates_list, duration, steps=5):
        from_xy = coordinates_list[0]
        swipe_events = [DownEvent(from_xy), SleepEvent(0.1)]
        for to_xy in coordinates_list[1:]:
            swipe_events.extend(self.__swipe_move(from_xy, to_xy, duration=duration, steps=steps))
            from_xy = to_xy
        swipe_events.append(SleepEvent(self.hold_sec))
        DEV.touch_proxy.perform(swipe_events)

    # 按下并滑动
    def down_swipe(self):
        self.processing()
        to_x, to_y = self.end_point

        if self.offset and isinstance(self.offset, int):
            offset = self.end_point
            # 横屏向上滑动
            if not self.screen_vertical and self.delta_y < 0: offset = (to_x, to_y + self.offset)
            # 横屏向下滑动
            elif not self.screen_vertical and self.delta_y > 0: offset = (to_x, to_y - self.offset)
            # 横屏向左滑动
            elif not self.screen_vertical and self.delta_x < 0: offset = (to_x + self.offset, to_y)
            # 横屏向右滑动
            elif not self.screen_vertical and self.delta_x > 0: offset = (to_x - self.offset, to_y)

            # 竖屏向上滑动
            elif self.screen_vertical and self.delta_y < 0: offset = (to_x + self.offset, to_y)
            # 竖屏向下滑动
            elif self.screen_vertical and self.delta_y > 0: offset = (to_x - self.offset, to_y)
            # 竖屏向左滑动
            elif self.screen_vertical and self.delta_x < 0: offset = (to_x, to_y - self.offset)
            # 竖屏向右滑动
            elif self.screen_vertical and self.delta_x > 0: offset = (to_x, to_y + self.offset)

            self.__swipe_along([self.start_point_ or self.start_point, offset, (to_x, to_y)], duration=self.duration or 0.5, steps=self.steps)
        else:
            self.__swipe_along([self.start_point_ or self.start_point, self.end_point], duration=self.duration or 0.5, steps=self.steps)

    # 放开
    def up(self):
        DEV.touch_proxy.perform([UpEvent(0), SleepEvent(self.sec)])

    def reset(self):
        self.delta_x = 0
        self.delta_y = 0
        self.end_point = None

    def __enter__(self):
        print(323232)
        self.down_swipe()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.up()

    def __call__(self, start_point=None, end_point=None, delta_y=0.0, delta_x=0.0, hold_sec=None, sec=None):
        if start_point: self.start_point = start_point
        if end_point: self.end_point = end_point
        if delta_y:
            self.reset()
            self.delta_y = delta_y
        if delta_x:
            self.reset()
            self.delta_x = delta_x
        if hold_sec: self.hold_sec = hold_sec
        if sec: self.sec = sec
        self.down_swipe()
        self.up()

def air_swipe_fast(start_point, delta_y=0.0, delta_x=0.0, end_point=None, offset=None, duration=None, hold_sec=0.5, sec=0.5):
    SwipeAirtest(
        start_point,
        delta_y=delta_y,
        delta_x=delta_x,
        end_point=end_point,
        offset=offset,
        duration=duration,
        hold_sec=hold_sec,
        sec=sec)()