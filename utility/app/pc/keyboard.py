from airtest.core.api import *


"""
Keyevent
https://developer.android.com/reference/android/view/KeyEvent#constants_1
"""

def press_f12(sec=0):
    """F12"""
    keyevent("F12")
    sleep(sec)

def press_up(sec=0, combo=1):
    """UP"""
    for _ in range(combo):
        keyevent("DPAD_UP")
        sleep(sec)

def press_down(sec=0, combo=1):
    """DOWN"""
    for _ in range(combo):
        keyevent("DPAD_DOWN")
        sleep(sec)

def press_del(sec=0, combo=1, long_press=False):
    """DEL"""
    if long_press:
        shell("input keyevent --longpress KEYCODE_DEL")
        return

    for _ in range(combo):
        keyevent("KEYCODE_DEL")
        sleep(sec)

def press_space(sec=0, combo=1):
    """SPACE"""
    for _ in range(combo):
        keyevent("KEYCODE_SPACE")
        sleep(sec)

def press_enter(sec=0):
    """ENTER"""
    keyevent("KEYCODE_ENTER")
    sleep(sec)

def press_esc(sec=0):
    """ESC"""
    keyevent("KEYCODE_ESCAPE")
    sleep(sec)

def press_8(sec=0):
    """8"""
    keyevent("KEYCODE_8")
    sleep(sec)

def press_O(sec=0):
    """O"""
    keyevent("KEYCODE_O")
    sleep(sec)
