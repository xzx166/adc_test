import subprocess

import logging

from airtest.core.api import *
import cv2
import numpy as np
from PIL import Image


def get_window_titles_applescript():
    script = '''
    tell application "System Events"
        set windowTitles to {}
        set appProcesses to every process whose background only is false
        repeat with proc in appProcesses
            try
                set procName to name of proc
                set windowNames to name of every window of proc
                repeat with wName in windowNames
                    set end of windowTitles to procName & " - " & wName
                end repeat
            end try
        end repeat
        return windowTitles
    end tell
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode == 0:
        titles = result.stdout.strip().split(', ')
        return [t for t in titles if t]
    else:
        print("AppleScript Error:", result.stderr)
        return []

def cv2_2_pil(cv2_image):
    cv2_im = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im)
    return pil_im

def pngstring_2_image(pngstr):
    nparr = np.frombuffer(pngstr, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

DEV = device()
def streamSnapshot(filepath=None, quality=99):
    data = DEV.screen_proxy.get_frame_from_stream()
    frame = pngstring_2_image(data)  # type: ignore
    if filepath:
        # pil_img = cv2_2_pil(frame)
        # pil_img.save(filepath, quality=quality, optimize=True)
        cv2.imwrite(filepath, frame)
    return frame