# -*- encoding=utf8 -*-
from airtest.core.api import *
import time
import sys
import cv2
import json
from pathlib import Path

from utility.biz_utils.track import MotionTrackSuper

using("../utility/monitor.air")
from monitor import *

using("../utility/api.air")
from api import *

using("../utility/phase.air")
from phase import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/mask.air")
from mask import *

using("../utility/swipe.air")
from swipe import *

using("../utility/image.air")
from image import *

using("../utility/ocr.air")
from ocr import *

using("./utility/security.air")
from security import *


using("../utility/upload.air")
from upload import *

using("../utility/dwarf.air")
from dwarf import *

from airtest.core.api import connect_device, device

oppoENV = AppEnv.get_instance()
oppoLocalRun = oppoENV.launchType == "localtest"

def launchPoco():
    """
    # 启动POCO
    :return: poco object
    """
    from poco.drivers.android.uiautomation import AndroidUiautomationPoco
    for _ in range(3):
        try:
            androidPoco = AndroidUiautomationPoco(screenshot_each_action=False)
            sleep(2)
            return androidPoco
        except Exception:
            monitor_task_status_v2("OPPO_POCO启动失败", traceback.format_exc())
            sleep(3)

oppoPoco = launchPoco()

def loginTaskOppo(env, preLoginFunc=None, afterLoginFunc=None, skipCheckDialog=False):
    if AppDynamicInfo.get_instance().getHasLogin():

        if preLoginFunc is not None:
            preLoginFunc(env)

        sleep(3)

        if afterLoginFunc is not None:
            afterLoginFunc(env)
        monitor_task_status(env, "登录", "getHasLogin已登录")
        lx_break_phase(desc='已登录')
    else:
        ##########preOppoInstall()

        ##oppo游戏 未登录check逻辑需要交给
        sleep(3)
        name = 'adc_catch_oppoPreLogin_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=name, msg="get a snapshot.")
        pos = lx_wait(Template(r"tpl1723690099424.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
                      timeout=12,
                      is_try=True)
        if pos is None:
            #####有的游戏需要在oppo登录页前判断
            if preLoginFunc is not None:
                preLoginFunc(env)

        preOppoXieyi()

        ##oppo游戏 未登录check逻辑需要交给
        if preLoginFunc is not None:
            preLoginFunc(env)

        preLogin(env)
        processLogin(env, preLoginFunc, afterLoginFunc, skipCheckDialog)
        if afterLoginFunc is not None:
            afterLoginFunc(env)

def preOppoXieyi():
    start_time = time.time()
    while time.time() - start_time < 300:
        if dwarf_exists(Template(r"tpl1723690099424.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
                        timeout=30, interval=2):
            lx_touch((1229, 949), 2)
            break
        oss_path, cdn_url = upload_img_to_oss(lx_snapshot(AppEnv.get_instance(), "temp", path=True))
        monitor_task_status_v2("未正常游戏", f"当前屏幕: {cdn_url}, 剩余时间: {int(300 - (time.time() - start_time))}")
    else:
        lx_break_runloop(desc='未正常进入游戏')

def preOppoInstall():
    pos = lx_wait(Template(r"tpl1723632000022.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)), timeout=35,
                  is_try=False)
    if pos is not None:
        # 下载插件
        lx_touch((1488, 818), 1)

    pos = lx_wait(Template(r"tpl1723632222795.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
                  timeout=35,
                  is_try=False)
    if pos is not None:
        # 安装
        lx_touch((1687, 833), 3)
        if lx_wait(Template(r"tpl1723632345053.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
                  timeout=20,
                  is_try=False):
            # 安装完成
            lx_touch((1506, 826), 5)
            # 同意
            lx_touch((1217, 961), 8)



def preLogin(env):
    monitor_task_status(env, "登录", "start")
    for i in range(3):
        if lx_safe_wait_touch(Template(r"tpl1750300918997.png", record_pos=(-0.106, 0.115), resolution=(2400, 1350)), timeout=1):
            monitor_task_status(env, "登录阶段", "取消更新")
        if lx_safe_wait_touch(Template(r"tpl20250822143208.png", resolution=(2400, 1350))) or \
            lx_safe_wait_touch(Template(r"tpl20250829120503.png", resolution=(2400, 1350))):
            monitor_task_status(env, "登录阶段", "点击同意并使用")
        if lx_wait(Template(r"tpl1723531799876.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)), timeout=10,is_try=True):
            monitor_task_status(env, "登录阶段", "检测到-oppo登录入口")
            break
    else:
        if lx_wait(Template(r"tpl1723534184470.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)), timeout=10, is_try=True):
            monitor_task_status(env, "登录阶段", "检查登录 一下阶段")

        else:
            monitor_task_status(env, "登录阶段", "未成功检测到-oppo登录入口")
            lx_safe_snapshot(f"adc_catch_未成功检测到-oppo登录入口_{timeStamp()}.jpg")
            lx_break_runloop(desc="登录阶段，未成功检测到-oppo登录入口")
    sleep(1)

def safe_snapshot(max_retries=3,name='111'):
    retries = 0
    current_device = device()
    # device_url = current_device.get_uri()  # 获取设备连接地址（如 "Android://127.0.0.1:5555"）
    monitor_task_status(AppEnv.get_instance(), f"adc-uuid-sss {current_device.uuid}", "")

    while retries <= max_retries:
        try:
            snapshot(filename=name, msg="get a snapshot.")

            monitor_task_status(AppEnv.get_instance(),"截图成功！","")
            break
        except (OSError, ConnectionResetError) as e:

            monitor_task_status(AppEnv.get_instance(), f"错误：{e}, 尝试重连... ({retries}/{max_retries})", "")
            try:
                # 关闭旧连接并重新连接
                # current_device.disconnect()
                connect_device(f"Android:///{current_device.uuid}")
                retries += 1
            except Exception as reconnect_err:
                monitor_task_status(AppEnv.get_instance(), f"重连失败: {reconnect_err}", "")
                raise
        except AttributeError as ae:  # 处理其他潜在属性错误
            monitor_task_status(AppEnv.get_instance(), f"属性错误: {ae}", "")
            break
    else:
        raise RuntimeError("所有重试均失败！")


def processLogin(env, preLoginFunc=None, afterLoginFunc=None, skipCheckDialog=False):
        mode = env.mode
        taskId = env.taskId
        taskStatus = env.taskStatus
        scriptEnv = env.scriptEnv
        username = env.username
        password = env.password
        transferAccountInfo = env.transfer_account_info
        transferAccountInfoJson = json.loads(transferAccountInfo)
        transferAccountName = transferAccountInfoJson["transferAccountName"].strip()

        gameNickName = None
        if AppEnv.get_instance().account_attr is not None and len(AppEnv.get_instance().account_attr) > 0:
            gameNickName = json.loads(AppEnv.get_instance().account_attr).get("GAME_NICK_NAME")
            if gameNickName: gameNickName = gameNickName.strip()

        name = 'adc_catch_oppo_processLogin_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=name, msg="get a snapshot.")

        # 某些场景下手机号 键盘会出来，点击【对号】位置 - 目前也是安全位置
        lx_touch((2212, 1299), 1)
        #协议
        lx_touch((801, 1307), 1)
        #切换账密
        lx_touch((935, 1268), 1)

        name = 'adc_catch_oppo_processLogin0_' + str(int(time.time() * 1000000)) + '.jpg'
        safe_snapshot(max_retries=3,name=name)

        #输入手机号
        lx_touch((363, 555), 1, is_try=True)
        name = 'adc_catch_oppo_processLogin1_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=name, msg="get a snapshot.")

        shell("input text {}".format(username))
        monitor_task_status(env, "登录阶段", f"账号:{username}")
        sleep(AppEnv.get_instance().sleepTime * 1)

        # 输入手机号
        lx_touch((363, 717), 1)
        shell("input text {}".format(password))
        monitor_task_status(env, "登录阶段", "password")
        sleep(AppEnv.get_instance().sleepTime * 1)
        keyevent("BACK")
        sleep(AppEnv.get_instance().sleepTime * 2)

        # 点击 登录
        lx_touch((1055, 1165), 2)

        # 永劫无间手游oppo验证等待
        # sleep(10)

        oppoLoginClicked(env, transferAccountName, checkNickName=gameNickName)

#================
#登录点击后  子账号逻辑
#================
def oppoLoginClicked(env, transferAccountName, checkNickName=None):
    gameID = env.gameDir.split("_")[0]
    accountNameMapPath = (Path(__file__).parent / "accountNameMap.json").resolve()
    accountNameMap = {}
    if accountNameMapPath.exists():
        accountNameMap.update(json.loads(accountNameMapPath.read_text()))

    checkedQiehuan = False
    check_risk_status = 0
    for retry_num in range(5):
        monitor_task_status_v2("oppo登录", f"开始连续点击（{retry_num}）")
        # 点击切换账号
        for i in range(5 if oppoLocalRun else 20):
            if i <= 4:
                lx_touch((1492, 161), sec=0.5)
            else:
                lx_touch((1492, 161), sec=0.2)
                lx_touch((1492, 161), sec=0.2)
                lx_touch((1524, 650), sec=0.2)
                lx_touch((1480, 450), sec=0.2)

        monitor_task_status_v2("oppo登录", f"开始识别是否进入切换小号界面（{retry_num}）")
        if lx_safe_wait(Template(r"tpl1749454110428.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=2, interval=0.5):
            monitor_task_status_v2("oppo登录", f"识别到切换小号1（{retry_num}）")
            checkedQiehuan = True
        elif lx_safe_wait(Template(r"tpl1723539101959.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=2, interval=0.5):
            monitor_task_status_v2("oppo登录", f"识别到切换小号2（{retry_num}）")
            checkedQiehuan = True
        ####做一次识别的信息补偿
        if not checkedQiehuan:
            if lx_safe_wait(Template(r"tpl1723603806460.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=2, interval=0.5):
                monitor_task_status_v2("oppo登录", f"识别到暂不切换（{retry_num}）")
                checkedQiehuan = True

        if checkedQiehuan:
            break
        else:
            check_risk_control.RETRY_NUM = retry_num
            if check_risk_status := check_risk_control():
                continue
            else:
                monitor_task_status_v2("oppo登录", f"未识别到暂不切换（{retry_num}）", status=10199)
                lx_break_runloop("未识别到暂不切换")

    else:
        if check_risk_status > 0:
            monitor_task_status_v2("风控检测", f"风控未通过", status=10102)
            lx_break_runloop("风控未通过")
        else:
            monitor_task_status_v2("oppo登录", f"未识别到暂不切换", status=10199)
            lx_break_runloop("未识别到暂不切换")

    newLoginButton = None
    if checkedQiehuan:
        monitor_task_status_v2(f"检测到oppo组件", "开始")
        lx_touch((1517, 162), 0.5)
        sleep(1)

        ##点击暂不切换
        if lx_wait(Template(r"tpl1723603806460.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=2,
                   interval=1, is_try=True):
            lx_touch((909, 1184), 1)

    #切换账号识别 或者点击失败 二次checked trcatch来保障
    if not lx_wait(Template(r"tpl1723539101959.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=5,
               interval=0.5, is_try=True):
        if lx_wait(Template(r"tpl1731401942795.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=5,
                   interval=0.5, is_try=False):
            monitor_task_status_v2(f"检测到oppo组件", "开始check账号")

    pos = lx_wait(Template(r"tpl1753783424071.png", record_pos=(-0.014, 0.196), resolution=(2400, 1350)), is_try=True)
    if pos:
        newLoginButton = pos
        monitor_task_status_v2("选择子账号", f"识别到新界面 {pos}")

    # 特殊字符
    special_pattern = re.compile(r"[丿\-_乀灬丨|｜\s]")
    checked = False
    for page in range(15):
        name = f'adc_catch_oppo_sun_account_area_{page}_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=name, msg="get a snapshot.")

        if newLoginButton:
            ocrResult = getOppoImageCropPosForEASPro(name, (720, 250), (1630, 1172))
        else:
            ocrResult = getOppoImageCropPosForEASPro(name, (758, 250), (1527, 1172))

        checked = False
        if ocrResult is not None:
            for i in range(len(ocrResult)):
                val = ocrResult[i]['txts']
                monitor_task_status_v2(f"Account name match", f"{val}: {transferAccountName}")
                if val == transferAccountName or \
                    (len(val) > 5 and val.startswith("0") and f"O{val[1:]}" == transferAccountName) or \
                    ((len(val) >= 2 or len(transferAccountName) >= 2) and accountNameMap.get(gameID, {}).get(val) == transferAccountName) or \
                    (special_pattern.sub("", transferAccountName) == special_pattern.sub("", val)) or \
                    (len(transferAccountName) >= 5 and transferAccountName == f"l{val[1:]}") or \
                    (len(transferAccountName) >= 5 and transferAccountName == f"I{val[1:]}"):
                    checked = True
                    boxY = int(ocrResult[i]['box'][0][1])
                    touch_pos = (1566, 250 + boxY + 8)
                    monitor_task_status_v2("oppo选择子账号", f"{transferAccountName}: {touch_pos}")
                    name = 'adc_catch_oppo_select_start_' + str(int(time.time() * 1000000)) + '.jpg'
                    lx_safe_snapshot(filename=name, msg="get a snapshot.")
                    lx_touch(touch_pos)
                    name = 'adc_catch_oppo_selected_end_' + str(int(time.time() * 1000000)) + '.jpg'
                    lx_safe_snapshot(filename=name, msg="get a snapshot.")
                    sleep(1)
                    name = 'adc_catch_oppo_selected_end2_' + str(int(time.time() * 1000000)) + '.jpg'
                    lx_safe_snapshot(filename=name, msg="get a snapshot.")
                    if newLoginButton:
                        lx_touch(newLoginButton, sec=1)
                        monitor_task_status_v2("选择子账号", f"点击登录游戏（新界面）{newLoginButton}")
                    break

            if not checked and checkNickName is not None and len(checkNickName) > 2:
                for i in range(len(ocrResult)):
                    val = ocrResult[i]['txts']
                    # if len(val) > len(checkNickName):
                    #     total_length = len(checkNickName)
                    #     val = val[:total_length]
                    checkNickName = checkNickName.replace('丨', '').replace('、', '').replace('|', '').replace('丶', '')
                    val = val.replace('丨', '').replace('、', '').replace('|', '').replace('丶', '')

                    # monitor_task_status_v2(f"名称check兼容逻辑", f"checkNickName = {checkNickName}   val = {val}")
                    if len(checkNickName) > 2 and (val == checkNickName or val.startswith(checkNickName)):
                        checked = True
                        boxY = int(ocrResult[i]['box'][0][1])
                        lx_touch((1566, 250 + boxY + 8))
                        name = 'adc_catch_oppo_selected_nick_end_' + str(int(time.time() * 1000000)) + '.jpg'
                        lx_safe_snapshot(filename=name, msg="get a snapshot.")
                        sleep(1)
                        name = 'adc_catch_oppo_selected_nick_end2_' + str(int(time.time() * 1000000)) + '.jpg'
                        lx_safe_snapshot(filename=name, msg="get a snapshot.")
                        if newLoginButton:
                            lx_touch(newLoginButton, sec=1)
                            monitor_task_status_v2("选择子账号", f"点击登录游戏（新界面）{newLoginButton}")
                        break

        if checked:
            sleep(3.5)
            if lx_wait(Template(r"tpl1723539101959.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=2,
                       interval=0.5, is_try=True) or lx_wait(Template(r"tpl1731401942795.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)), timeout=5,
                   interval=0.5, is_try=True):
                name = 'adc_catch_oppo_selected_buchang_' + str(int(time.time() * 1000000)) + '.jpg'
                lx_safe_snapshot(filename=name, msg="get a snapshot.")
                lx_touch((2378, 352), 1)
                monitor_task_status_v2(f"检测到oppo组件", "补偿点击")
            break
        else:
            if newLoginButton:
                swipe_only((1200, 990), (1200, 990 - 400))
            else:
                swipe_only((1218, 735), (1218, 320))
            sleep(1)

    if not checked:
        monitor_task_status_v2("账号ocr不匹配", f"{transferAccountName}", 10112)
        lx_break_runloop(desc="登录阶段, 未成功登录后检测-oppo登录入口2")
    else:
        AppDynamicInfo.get_instance().setHasLogin(True)

# ================= eas 2.0 信息 ===========================
def getOppoImageCropPosForEASPro(filename, crop_start, crop_end, check_type=2):
    data = []

    cropFileName = f'crop_oppo_eas_pro_' + str(int(time.time() * 1000000)) + '.jpg'

    crop_pos_img = crop_pos_image_from_snapshot(filename, cropFileName, crop_start, crop_end, need_snapshot=False)

    name_crop_image_path = os.path.join(ST.LOG_DIR, cropFileName)

    data.extend(ocr_image_by_eas(name_crop_image_path, type=check_type))
    data.extend(ocr_image_by_eas(name_crop_image_path, type=1))

    return data

class OppoRiskControl:
    def __init__(self, **kwds):
        """
        处理风控
        :param kwds: 不定长参数
        """
        self.IDENTIFY = kwds.get("IDENTIFY")          # 滑动验证码标识
        self.REFRESH_POS = kwds.get("REFRESH_POS")    # 刷新按钮位置
        self.RETRY_NUM = kwds.get("RETRY_NUM")        # 重试次数
        self.NOT_REFRESH = kwds.get("NOT_REFRESH")    # 每次循环不要刷新
        self.START_POINT = kwds.get("START_POINT")    # 开始滑动接触点
        self.VER_LT = kwds.get("VER_LT")              # 验证码图片区域左上
        self.VER_RB = kwds.get("VER_RB")              # 验证码图片区域右下
        self.SLIDE_OFFSET = kwds.get("SLIDE_OFFSET")  # 偏移量

    def __call__(self):
        # 0表示未遇到风控；1表示遇到风控；2表示风控未通过;
        if START_POINT := lx_safe_wait(self.IDENTIFY, timeout=2):
            monitor_task_status_v2("风控检测", f"识别到风控，需要处理（{self.RETRY_NUM}）")
            if self.REFRESH_POS and isinstance(self.RETRY_NUM, int) and self.RETRY_NUM > 0:
                lx_safe_touch(self.REFRESH_POS, sec=1)

            filename1 = f"snap_risk_control.jpg"
            filename2 = f"adc_catch_risk_control_{self.RETRY_NUM}_{timeStamp()}.jpg"
            crop_pos_image_from_snapshot(filename1, filename2, self.VER_LT, self.VER_RB)
            risk_crop_path = os.path.join(ST.LOG_DIR, filename2)
            localFileList = [risk_crop_path]
            _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
            risk_control_url = cdn_url_list[0]
            data = easRequest(self.get_env_path(), self.getRequestDataWithURL(risk_control_url))
            monitor_print(f'processing_risk_control:{risk_control_url} result:{data}_{self.RETRY_NUM}')
            match_point = self.getEasCommonResult(data)
            monitor_print(f'processing_risk_control_match_point: {match_point[0]}_retry_num: {self.RETRY_NUM}')
            # 滑动距离为零
            if not match_point[0]:
                return 2
            finalEndPoint = (START_POINT[0] + self.SLIDE_OFFSET + match_point[0], START_POINT[1])
            # adc_swipe(START_POINT, finalEndPoint, sec=2, duration=5)
            SwipePoco(START_POINT, end_point=finalEndPoint, sec=2, hold_sec=1, speed=0.2)()
            return 1

        else:
            monitor_task_status_v2("风控检测", "无风控")
            return 0

    def get_env_path(self):
        scriptEnv = AppEnv.get_instance().scriptEnv
        monitor_print(f"scriptEnv: {scriptEnv}")
        if scriptEnv in ['local', 'daily', 'pre']:
            return '/api/predict/lingxialgo_adc_ocr_pre'
        else:
            return '/api/predict/lingxialgo_vision_adc'

    def getRequestDataWithURL(self, url):
        resData = {
            'imageProperties': [{"propertyId": "验证码"}],
            'requestId': str(int(time.time() * 1000000)),
            'imageUrl': url,
            'recoType': "拼图验证码"
        }
        return resData

    def getEasCommonResult(self, res):
        if res is not None and 'message' in res and ('imagePropertyValues' in res['message']):
            values = res['message']['imagePropertyValues']
            for value in values:
                if value['propertyId'] == "验证码" and value['value'] == "阴影拼图":
                    startPoint = value['box'][0]
                    return startPoint
        return 0, 0

# 检查风控
check_risk_control = OppoRiskControl(
    IDENTIFY=Template("tpl20250816184657.png", resolution=(2400, 1350)),
    REFRESH_POS=(1545, 815),
    VER_LT=(796, 463),
    VER_RB=(1607, 869),
    SLIDE_OFFSET=-120
)

# pos归一化
oppoSCREENSIZE = (2400, 1350)
oppo_pos_normal = lambda pos: (pos[0] / oppoSCREENSIZE[0], pos[1] / oppoSCREENSIZE[1])
class SwipePoco:
    def __init__(self, start_point, delta_y=0.0, delta_x=0.0, end_point=None, hold_sec=0.5, sec=0.5, speed=None):
        """
        Poco滑动
        :param start_point:
        :param delta_y:
        :param delta_x:
        :param end_point:
        :param hold_sec:
        :param sec:
        :param speed:
        """
        self.start_point = start_point
        self.end_point = end_point
        self.delta_y = delta_y
        self.delta_x = delta_x
        self.hold_sec = hold_sec
        self.sec = sec
        self.speed = speed

    def processing(self, direction):
        if not self.end_point and any((self.delta_x, self.delta_y)):
            self.end_point = self.start_point[0] + self.delta_x, self.start_point[1] + self.delta_y

        if direction == "down":
            track = MotionTrackSuper(speed=self.speed or 0.6, is_hold=True)
            track = track.start(oppo_pos_normal(self.start_point))
            track = track.move(oppo_pos_normal(self.end_point))
            track = track.hold(self.hold_sec)
        else:
            track = MotionTrackSuper([oppo_pos_normal(self.end_point)])
            track = track.hold(self.sec)
        oppoPoco.apply_motion_tracks([track], accuracy=0.04)

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
