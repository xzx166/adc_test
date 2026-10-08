import traceback

from airtest.core.api import *

using("../utility/biz_utils.air")
from biz_utils import platform, monitor_task_status_v2,os_env, snapshot_write

from poco.drivers.android.uiautomation import AndroidUiautomationPoco


if "com.netease.open.pocoservice" in shell("pm list package -d"):
    shell("pm enable com.netease.open.pocoservice")
    monitor_task_status_v2("启用POCOService")

try:
    androidPoco = AndroidUiautomationPoco(screenshot_each_action=False)
except Exception:
    monitor_task_status_v2(f"POCO启动失败", traceback.format_exc())
    androidPoco = None

def get_vivo_vip(drag_ball=False, write_image=True, mask_pos=None):
    """
    vivo乐享等级
    :param drag_ball: 是否拖拽悬浮球
    :param write_image: 是否保存截图
    :param mask_pos: 打码区域 格式要求[(1,2,3,4),(5,6,7,8)]
    :return Numpy array image
    """
    mask = []
    if mask_pos:
        mask.extend(mask_pos)

    if platform == "vivo":
        if androidPoco is None:
            return
        ball = androidPoco(nameMatches="^.+:id/float_view_append")
        if ball.exists():
            monitor_task_status_v2("vivo乐享等级截图")
            screen_size = androidPoco.get_screen_size()
            ball.click()
            # 获取元素的中心位置
            pos_center = ball.get_position()
            # 从元素中心向下开始滑动，这里我们假设向下滑动元素高度的一半
            pos_after_swipe = (pos_center[0], pos_center[1] + 0.3)

            if drag_ball:
                ball.swipe(pos_after_swipe)

            ball.click(sleep_interval=1)
            ball.click()
            # child_ball = androidPoco("com.vivo.unionsdk:id/vivo_page_content").offspring("com.vivo.unionsdk:id/vivo_union_display_area").offspring("com.vivo.unionsdk:id/vivo_float_window_nick_name")
            child_ball = androidPoco("com.vivo.unionsdk:id/vivo_float_window_nick_name")
            vivo_image = None
            if child_ball.exists():
                center_pos = child_ball.get_position()
                print(f"{center_pos[0]*screen_size[0]}, {center_pos[1]*screen_size[1]}")
                left_x = int(center_pos[0]*screen_size[0] - 161)
                left_y = int(center_pos[1]*screen_size[1] - 30)
                right_x = int(center_pos[0]*screen_size[0] + 125)
                right_y = int(center_pos[1]*screen_size[1] + 30)
                mask.append((left_x,left_y,right_x,right_y))
                vivo_image = snapshot_write(write_name='adc_result_vivo_4102416000000000.jpg' if write_image else None, mask=mask)
            # vip_level = poco("com.vivo.unionsdk:id/vivo_page_content").offspring("com.vivo.unionsdk:id/vivo_union_display_area").offspring("com.vivo.unionsdk:id/vivo_float_window_vip_level").get_text()
            ball.click()
            return vivo_image
        else:
            monitor_task_status_v2("vivo悬浮球未找到")
