import os
from airtest.core.api import *
import logging
logger = logging.getLogger("airtest")
logger.setLevel(logging.WARN)

os_env = os.environ

DEV = device()
display_info = DEV.display_info
width = display_info['width']
height = display_info['height']
SCREENSIZE = (height, width) if os_env.get("screenRotation") == "vertical" else (width, height)
SCREENHALF = SCREENSIZE[0] // 2, SCREENSIZE[1] // 2
SCREENBOX = (0, 0), SCREENSIZE

from poco.drivers.android.uiautomation import AndroidUiautomationPoco
poco = AndroidUiautomationPoco(screenshot_each_action=False)

from track import MotionTrack

# pos归一化
pos_normalization = lambda pos: (pos[0] / SCREENSIZE[0], pos[1] / SCREENSIZE[1])

# Poco滑动
class SwipePoco:
    def __init__(self, start_point, delta_y=0.0, delta_x=0.0, end_point=None, hold_sec=0.5, sec=0.5):
        self.start_point = start_point
        self.end_point = end_point
        self.delta_y = delta_y
        self.delta_x = delta_x
        self.hold_sec = hold_sec
        self.sec = sec

    def processing(self, direction):
        if not self.end_point and any((self.delta_x, self.delta_y)):
            self.end_point = self.start_point[0] + self.delta_x, self.start_point[1] + self.delta_y

        if direction == "down":
            track = MotionTrack(speed=0.6, is_hold=True)
            track = track.start(pos_normalization(self.start_point))
            track = track.move(pos_normalization(self.end_point))
            track = track.hold(self.hold_sec)
        else:
            track = MotionTrack([pos_normalization(self.end_point)])
            track = track.hold(self.sec)
        poco.apply_motion_tracks([track], accuracy=0.04)

    def reset(self):
        self.delta_x = 0
        self.delta_y = 0
        self.end_point = None

    def down_swipe(self):
        self.processing("down")

    def up(self):
        self.processing("up")

    def __enter__(self):
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

def poco_swipe_fast(start_point, delta_y=0.0, delta_x=0.0, end_point=None, sec=1):
    if not end_point and any((delta_x, delta_y)):
        end_point = start_point[0] + delta_x, start_point[1] + delta_y
    poco.swipe(pos_normalization(start_point), pos_normalization(end_point), duration=0.5)
    sleep(sec)