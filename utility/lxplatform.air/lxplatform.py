# -*- encoding=utf8 -*-
from airtest.core.api import *
import time
import sys
import cv2
import json
import traceback
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

catch_file_name = 'adc_catch'

def getOCRRequestDataWithURL(url):
    resData = {}
    resId = str(int(time.time()*1000000))
    resData['requestId'] = resId
    resData['imageUrl'] = url
    resData['recoType'] = "ocr"
    return resData
def getRequestDataWithURL(url):
    resData = {}
    resData['imageProperties'] = [
        {
            "propertyId": "验证码"
        }
    ]
    resId = str(int(time.time()*1000000))
    resData['requestId'] = resId
    resData['imageUrl'] = url
    resData['recoType'] = "拼图验证码"
    return resData
def getEasCommonResult(res):
    if res is not None and 'message' in res and ('imagePropertyValues' in res['message']):
        values = res['message']['imagePropertyValues']
        for value in values:
            if value['propertyId'] == "验证码" and  value['value'] == "阴影拼图":
                startPoint = value['box'][0]
                return startPoint
    return (0,0)

def getEasCommonResultOCR(res):
    if res is not None and 'message' in res and ('status' in res['message']) and ('data' in res['message']):
        data = res['message']['data']
        status = res['message']['status']
        return data
    return None
# ============================================
def loginTaskJiuyou(env, preLoginFunc=None, afterLoginFunc=None, skipCheckDialog=False):

    try:
        monitor_task_status_v2(
            "锁定键盘：am broadcast -a UPDATE_KEYBOARD --es VALUE '0.0001' com.alibaba.cgs.ime")
        shell(
            "am broadcast -a UPDATE_KEYBOARD --es VALUE '0.0001' com.alibaba.cgs.ime")
    except Exception as e:
        monitor_print(f"锁定键盘失败:{traceback.format_exc()}")
        monitor_task_status_v2("jiuyou登录",f"锁定键盘失败：{e}")



    if AppDynamicInfo.get_instance().getHasLogin():

        if preLoginFunc is not None:
            preLoginFunc(env)
        else:
            preLogin(env)
        sleep(3)

        if afterLoginFunc is not None:
            afterLoginFunc(env)
        monitor_task_status(env, "登录", "getHasLogin已登录")
        lx_break_phase(desc='已登录')
    else:
        processLogin(env, preLoginFunc, afterLoginFunc, skipCheckDialog)

def streamSnapshot(filename = None, msg = None, is_try = True):
    if filename is None:
        filename = f'record_{str(int(time.time() * 1000000))}.jpg'
    path = os.path.join(ST.LOG_DIR, filename)
    lx_safe_snapshot(filename, msg)
    img_np = cv2.imread(path)
    return img_np

def kit_match_in(small_img_np, main_img_np = None, threshold=0.57, print_str = ''):
    small_img_gray = cv2.cvtColor(small_img_np, cv2.COLOR_BGR2GRAY)
    if main_img_np is not None:
        main_img_gray = cv2.cvtColor(main_img_np, cv2.COLOR_BGR2GRAY)
    else:
        file_name = f'{catch_file_name}_kit_match_in_{str(int(time.time()*1000000))}.jpg'
        snapshot(filename=file_name, msg="get a snapshot.")
        img_path = os.path.join(ST.LOG_DIR, file_name)
        main_img_gray = cv2.imread(img_path, 0)
    # 进行模板匹配
    res = cv2.matchTemplate(main_img_gray, small_img_gray, cv2.TM_CCOEFF_NORMED)

    # 找到最大和最小值及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # 使用最大值位置作为匹配结果
    top_left = max_loc
    h, w = small_img_gray.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    pos = (top_left[0] + int(w / 2), top_left[1] + int(h / 2))
    if print_str:
        monitor_print(f'{print_str}, max_val: {max_val}')
    if max_val > threshold:
        return pos
    else:
        return None
    
def kit_wait_find(v, timeout=None, interval=0.5, threshold=0.7, area_pos = None):
    try:
        monitor_print(f'---kit_wait_finding: {v}')
        start_time = time.time()
        while True:
            screen = streamSnapshot()
            if screen is None:
                monitor_print(f'---kit_wait_error: Screen is None, may be locked')
                if timeout is None:
                    return None
            else:
                file_path = v._filepath
                file_np = cv2.imread(file_path)
                if area_pos is not None:
                    screen = screen[area_pos[1]:area_pos[3], area_pos[0]:area_pos[2]]
                pos = kit_match_in(file_np, screen, threshold, print_str = f'---kit_wait {v}')
                if pos:
                    if area_pos is not None:
                        pos = (pos[0] + area_pos[0], pos[1] + area_pos[1])
                    monitor_print(f'---kit_wait_finding: {v} pos: {pos}')
                    return pos
                if timeout is None:
                    return None
                if (time.time() - start_time) > timeout:
                    return None
                else:
                    time.sleep(interval)
    except:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit_wait_find_exception: {error_traceback}')
        return None
    

def getJiuyouAccountId():
    sleep(2)
    monitor_print("九游-截图唯一id")
    targetPos=None
    pos = exists(Template(r"tpl1715737772905.png", record_pos=(-0.38, -0.275), resolution=(2400, 1350)))
    if pos:
        monitor_print("检测到九游悬浮入口-上")
        targetPos=pos

    if targetPos is None:
        pos = exists(Template(r"tpl1715737908207.png", record_pos=(-0.496, -0.033), resolution=(2400, 1350)))
        if pos:
            monitor_print("检测到九游悬浮入口-左")
            targetPos=pos

    if targetPos is None:
        pos = exists(Template(r"tpl1715737996609.png", record_pos=(0.495, -0.015), resolution=(2400, 1350)))
        if pos:
            monitor_print("检测到九游悬浮入口-右")
            targetPos=pos

    monitor_print(f"检测九游悬浮入口-targetPos={targetPos}")
    if targetPos:
        lx_touch(targetPos, 2)
        # lx_touch((95,95),2)
        pos = exists(Template(r"tpl1715738336209.png", record_pos=(-0.464, -0.183), resolution=(2400, 1350)))
        if pos:
            monitor_print("检测到九游悬浮入口-设置")
            lx_touch(pos, 2)

            snapFileName=f'jiuyou_settings_snap_' + str(int(time.time()*1000000)) + '.jpg'
            cropFileName=f'jiuyou_settings_crop_' + str(int(time.time()*1000000)) + '.jpg'

            crop_start=(1251,194)
            crop_end=(1490,247)
            crop_pos_img = crop_pos_image_from_snapshot(snapFileName, cropFileName, crop_start,crop_end)

            item_full_path = os.path.join(ST.LOG_DIR, cropFileName)

            localFileList = []
            localFileList.append(item_full_path)
            _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
            if cdn_url_list:
                qufu_crop_img_url = cdn_url_list[0]

            data = easRequest(get_env_ocr_path(env), getOCRRequestDataWithURL(qufu_crop_img_url))
            print(f'九游账号, ocr result:{data}')

            if data is not None and 'message' in data and ('status' in data['message']) and ('data' in data['message']):
                ocrResult = data['message']['data']
                status = data['message']['status']

                for item in ocrResult:
                    # monitor_print(f"ocr result 区服 {item}")
                    accountId=item['txts']
                    monitor_print(f"ocr result accountId {accountId}")
                    if accountId.isdigit():
                        break



def preLogin(env):
    from poco.drivers.android.uiautomation import AndroidUiautomationPoco
    poco = AndroidUiautomationPoco(
        use_airtest_input=True, screenshot_each_action=False)

    monitor_task_status(env, "登录阶段", "开始")

    lx_wait_touch(Template(r"tpl1704788787130.png", record_pos=(0.128, 0.114), resolution=(2400, 1350)), timeout=20, is_try=True)
    timeOut = 50
    if (lx_wait(Template(r"tpl1701671312516.png", record_pos=(-0.47, 0.163), resolution=(2400, 1350)), timeout=12, interval=2, is_try=True)):
        sleep(1)
    lx_exists_touch(Template(r"tpl1701671300103.png", record_pos=(-0.0, -0.233), resolution=(2400, 1350)))

    start_time = time.time()
    while time.time() - start_time < timeOut:
        if exists(Template(r"tpl1726307290136.png", record_pos=(0.456, 0.188), resolution=(2400, 1350))) or\
            exists(Template(r"tpl1742461805192.png", record_pos=(0.457, 0.186), resolution=(2400, 1350))) or\
            exists(Template(r"tpl1699499196274.png", record_pos=(-0.47, 0.163), resolution=(2400, 1350))):
            if exists(Template(r"tpl1699498568338.png", record_pos=(-0.0, -0.233), resolution=(2400, 1350))):
               # exists(Template(r"tpl1699500995660.png", record_pos=(-0.0, -0.233), resolution=(2400, 1350))):
                lx_while(lambda: exists(Template(r"tpl1699498568338.png", record_pos=(-0.0, -0.233), resolution=(2400, 1350))),lambda: (touch((200, 200)),
                                  monitor_task_status(env, "登录阶段", "关闭弹窗")))
            break
    else:
        lx_break_runloop("未正常进入游戏")
    sleep(1)
    #如果存在弹窗的话去掉登录弹窗
    touch((200, 200))
    sleep(0.5)


    #拉起弹窗
    # 点击进入游戏(1210,1046)
    touch((2000, 700),3)
    monitor_task_status(env, "登录阶段", "点击进入游戏")

    # if (exists(Template(r"tpl1699500425576.png", record_pos=(-0.0, 0.013), resolution=(2400, 1350)))):
    #     monitor_task_status(env, "登录阶段", "账密出错,三国杀不支持手机号登录", 10008)
    #     lx_break_app(desc='账密出错,账号非手机号', hold_game=False,ext_info={'key':'10008'})



def get_env_risk_path(env):
    scriptEnv = env.scriptEnv
    risk_path=""
    if (scriptEnv == 'local'):
        risk_path='/api/predict/lingxialgo_adc_ocr_pre'
    elif(scriptEnv == 'pre'):
        risk_path = '/api/predict/lingxialgo_vision_adc'
    elif(scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_adc'
    else:
        risk_path = '/api/predict/lingxialgo_adc_ocr_pre'

    return risk_path

def get_env_ocr_path(env):
    scriptEnv = env.scriptEnv
    risk_path=""
    if (scriptEnv == 'local'):
        risk_path='/api/predict/lingxialgo_adc_ocr_pre'
    elif(scriptEnv == 'pre'):
        risk_path = '/api/predict/lingxialgo_vision_adc'
    elif(scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_adc'
    else:
        risk_path = '/api/predict/lingxialgo_adc_ocr_pre'

    return risk_path

def process_risk_control(env):
    # 0表示未遇到风控；1表示风控通过；2表示风控未通过
    risk_control_status = 0
    count = 0
    for i in range(5):
        if (exists(Template(r"tpl1703663214268.png", record_pos=(-0.164, 0.197), resolution=(2400, 1350)))):
            if i != 0:
                # 刷新
                lx_touch((853,927),sec=2)

            filename=f"adc_upload_snap_risk_control-{i}.jpg"
            # 识别到风控，需要处理
            lx_safe_snapshot(filename=filename , msg="get a snapshot.", quality=99)
            # 滑动结束后，如果账密错误，则依然在登录界面，如果账密正确，则进入游戏
            risk_snap_path = os.path.join(ST.LOG_DIR, filename)
            # current_file_path = os.path.abspath(__file__)

            # If you want to get the directory containing the current file, use os.path.dirname
            # current_file_directory = os.path.dirname(current_file_path)
            # sliderFileName =  os.path.join(current_file_directory, "swipe-slider-jiuyou5.png")

            # cropStart=(953,320)
            # cropEnd=(1630,760)
            # points = crop_and_calculate_slide_distance(risk_snap_path, sliderFileName, cropStart, cropEnd,slide_offset=140,finalStartPoint = (877,826))
            # start_point, end_point = points

            risk_crop_path =  os.path.join(ST.LOG_DIR, f"adc_upload_snap_risk_control_cropped-{i}.jpg")

            cropImg=cv2.imread(risk_snap_path,1)
        #     print(f"图片文件大小: {cropImg.shape[0]},{cropImg.shape[1]}")
            # (919,136)  (1731,777)
            if (cropImg.shape[0] != 1350 or cropImg.shape[1]!= 2400):
                cropImg=cv2.resize(cropImg,(2400,1350))

        #     cropImg= cropImg[147:343,431:727]  # small (431,147)  (727,343)
            cropImg= cropImg[320:760,953:1630]  # airtest (953,320)  (1630,760)
            cv2.imwrite(risk_crop_path, cropImg)

            localFileList = []
            localFileList.append(risk_crop_path)
            _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
            if cdn_url_list:
                risk_control_url = cdn_url_list[0]

            data = easRequest(get_env_risk_path(env), getRequestDataWithURL(risk_control_url))
            print(f'process_risk_control:{risk_control_url}   result:{data}')

            slide_offset = 150  # for jiuyou
            match_point = getEasCommonResult(data)
            finalStartPoint = (877,826)
            finalEndPoint = (finalStartPoint[0]+slide_offset + match_point[0], finalStartPoint[1])
            swipe_only(finalStartPoint, finalEndPoint)
            sleep(4)
            count = count + 1
        else:
            break

    if count > 0:
        # 触发风控
        monitor_task_flow_status_info(1003, '触发风控')

    if count == 0:
        risk_control_status = 0
    elif count > 0 and count < 3:
        risk_control_status = 1
    else:
        if (exists(Template(r"tpl1703663214268.png", record_pos=(-0.164, 0.197), resolution=(2400, 1350)))):
            risk_control_status = 2
        else:
            risk_control_status = 1

    if risk_control_status == 1:
        # 风控通过
        monitor_task_flow_status_info(1004, '风控通过')

    return risk_control_status

def processLogin(env, preLoginFunc=None, afterLoginFunc=None, skipCheckDialog=False):
    mode = env.mode
    taskId = env.taskId
    taskStatus = env.taskStatus
    scriptEnv = env.scriptEnv
    username = env.username
    password = env.password
    smsCode = env.smsCode
    orientation = G.DEVICE.display_info["orientation"]
    # 是否竖屏
    is_portrait_screen = False
    resolution = (2400, 1350)
    if orientation in (1, 3):
        monitor_task_status(env, "登录阶段-检测屏幕方向", "竖屏")
        is_portrait_screen = True
        resolution = (1350, 2400)
    else:
        monitor_task_status(env, "登录阶段-检测屏幕方向", "横屏")
    if mode == 'submit_ext_info':
        monitor_task_status(env, "登录阶段", f"校验前验证码{smsCode}")
        monitor_task_status(env, "登录阶段", f"输入验证码{smsCode}")
        # smsCode_string = smsCode.encode('unicode_escape')
        if tool_contains_chinese(smsCode):
            monitor_task_status(env, "登录阶段", "验证码失败", 10007)
            lx_break_app(desc='验证码校验失败',hold_game= True,ext_info={'key':'10007'})

        # 点击验证码输入框
        lx_touch((867, 752), 2)

        #点击清理
        lx_touch((1275,743),1)

        shell("input text {}".format(smsCode))
        # touch_number_keyboard(smsCode)
        monitor_task_status(env, "登录阶段", "输入验证码结束")
        sleep(2)

        # 点击提交
        lx_touch((1210,966), 5)
        # keyevent("BACK")
        # sleep(2)

        # lx_touch((1209, 945), 6)

        if exists(Template(r"tpl1704872708786.png", record_pos=(-0.001, 0.111), resolution=resolution)):
            monitor_task_status(env, "登录阶段", "验证码失败", 10007)
            lx_break_app(desc='验证码失败', hold_game= True,ext_info={'key':'10007'})
        else:
            env.mode = 'normal_start'
            afterLogin(env)
        return

    # 三国杀仅有账号登录，无其他方式
    if preLoginFunc is not None:
        preLoginFunc(env)
    else:
        preLogin(env)



    #检测九游登录入口
    monitor_task_status(env, "登录阶段", "检测-九游登录入口")

    if kit_wait_find(Template("tpl20251113164048.png", resolution=resolution)):
        monitor_task_status(env, "登录阶段", "识别到九游APP快速登录")
        lx_safe_touch((1200, 775), 1)

    # ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
    pos = kit_wait_find(Template(r"tpl1725613119079.png", record_pos=(-0.024, -0.156), resolution=resolution), timeout = 5)
    # ST.CVSTRATEGY = ['mstpl', 'tpl']
    if (pos is not None ):
        # 检测到九游登录入口
        monitor_task_status(env, "登录阶段", "检测到-九游登录入口1")
        lx_touch(pos, 2)
    else:
        ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
        pos = lx_wait(Template(r"tpl1706752840153.png", record_pos=(-0.04, -0.149), resolution=resolution), timeout = 2, is_try=True)
        ST.CVSTRATEGY = ['mstpl', 'tpl']
        if (pos is not None ):
            # 检测到九游登录入口
            monitor_task_status(env, "登录阶段", "检测到-九游登录入口2")
            lx_touch(pos, 2)
        else:
            ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
            pos2 = lx_wait(Template(r"tpl1709105253027.png", record_pos=(-0.022, -0.155), resolution=resolution), timeout = 2, is_try=True)
            ST.CVSTRATEGY = ['mstpl', 'tpl']
            if (pos2 is not None):
                # 检测到九游登录入口
                monitor_task_status(env, "登录阶段", "检测到-九游登录入口3")
                lx_touch(pos2, 2)
            else:
                lx_break_runloop(desc="登录阶段, 未成功检测到-九游登录入口4")
                return

    isNewSdk = True
    isThirdLogin = False
    # if (exists(Template(r"tpl1709866169683.png", record_pos=(0.138, -0.155), resolution=(2400, 1350))) or exists(Template(r"tpl1723186188467.png", record_pos=(0.138, -0.137), resolution=(2400, 1350)))):
    #     isNewSdk = True
    lx_snapshot(env, f"adc_catch_判断九游新老版本_{str(int(time.time() * 1000000))}.jpg",path=True)
    if exists(Template(r"tpl1728630401022.png", record_pos=(0.163, -0.157), resolution=resolution, threshold=0.9)) or\
        exists(Template(r"tpl1728981159353.png", record_pos=(-0.001, -0.091), resolution=resolution, threshold=0.85)):
        isNewSdk = False
    if exists(Template(r"tpl1736240455820.png", record_pos=(-0.03, 0.142), resolution=(2400, 1350), threshold=0.9)) or\
        exists(Template(r"tpl1736240463448.png", record_pos=(0.091, 0.143), resolution=(2400, 1350), threshold=0.9)):
        isThirdLogin = True

    monitor_task_status(env, "登录阶段", f"检测到-九游三方登陆入口{'出现' if isThirdLogin else '未出现'}")
    monitor_task_status(env, "登录阶段", f"检测到-九游sdk{'新版' if isNewSdk else '旧版'}")
    monitor_task_status(env, "登录阶段", "输入账号")
    sleep(AppEnv.get_instance().sleepTime*2)
    # lx_touch((1097,304), 2)
    # 同意隐私协议 竖屏 340 1400
    if is_portrait_screen:
        lx_touch((340,1400), 1)
    else:
        if isThirdLogin:
            lx_touch((861, 867), 1)
            lx_touch((1134, 308), 1)
        else:
            lx_touch((869,879), 1)
            lx_touch((807,901), 1)
            lx_touch((862,913), 1)
    # if isThirdLogin:

    # 点击手机号输入框
    # lx_touch((912,547), 1)
    if is_portrait_screen:
        lx_touch((415,1085), 1)
    else:
        if isThirdLogin:
            lx_touch((1044, 526), 1)
        else:
            lx_touch((1166,583), 1)


    if (isNewSdk):
        account_attr = env.account_attr
        accountAttr = json.loads(account_attr)
        username = accountAttr["GRAY_ACCOUNT"]
        secret_password = accountAttr["GRAY_PASSWORD"]

        decrypt_key = os.getenv('SECRTET_DECRYPT_PASSWORD')

        monitor_print(f"secret_password:{secret_password}")

        scriptEnv = env.scriptEnv
        if (scriptEnv == 'local'):
            password = secret_password
        else:
            if secret_password and len(secret_password)>0 and decrypt_key and len(decrypt_key)>0:
                password = decrypt(secret_password, decrypt_key)

    if tool_contains_chinese(username):
        monitor_task_status(env, "登录阶段", "账密出错,账号非手机号", 10008)
        lx_break_app(desc='账密出错,账号非手机号', hold_game=False,ext_info={'key':'10008'})
    deleteInputText()
    shell("input text {}".format(username))
    monitor_task_status(env, "登录阶段", f"账号:{username}")
    sleep(AppEnv.get_instance().sleepTime*2)
    if is_portrait_screen:
        lx_touch((1209, 2276), 1)
    else:
        lx_touch((2222, 1284), 1) # 点击键盘右下键

    ##########################
    # 点击密码输入框[1113,501]
    ##########################
    monitor_task_status(env, "登录阶段", "输入密码")
    # 点击密码输入框[1113,627]
    # lx_touch((1107, 625), AppEnv.get_instance().sleepTime)
    if is_portrait_screen:
        lx_touch((415,1202), 2)
    else:
        if isThirdLogin:
            lx_touch((1166, 681), 2) # 密码范围兼容，坐标相同
        else:
            lx_touch((1166,681), 2)


    # monitor_print(f"final password:{password}")
    if tool_contains_chinese(password):
        monitor_task_status(env, "登录阶段", "账密出错,账号非手机号", 10008)
        lx_break_app(desc='账密出错,账号非手机号', hold_game=False,ext_info={'key':'10008'})
    deleteInputText()
    shell("input text {}".format(password))
    sleep(AppEnv.get_instance().sleepTime)
    if is_portrait_screen:
        lx_touch((1252, 2285), 2)
    else:
        lx_touch((2222, 1284), 2) # 点击键盘右下键


    ##########################
    # 点击登录
    ##########################
    monitor_task_status(env, "登录阶段", "点击登录")
    # lx_touch((1206, 788), 5)
    if is_portrait_screen:
        loginButtonPos = (680, 1280)
    else:
        loginButtonPos = (1206, 829)
    if (isNewSdk):
        if is_portrait_screen:
            loginButtonPos = (680, 1304)
        else:
            loginButtonPos = (1200,785)
    # lx_touch((1206, 829), 5)
    print(f'process_jiuyou_sdk, loginButtonPos:{loginButtonPos}')
    lx_touch(loginButtonPos)

    for i in range(4):
        monitor_task_status(env, "登录", "点击登录页面")
        huanqu_snap_name = f'adc_catch_snap_denglu_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=huanqu_snap_name, msg="get a snapshot.")
        sleep(0.5)

    sleep(4)

    if not skipCheckDialog:
        if (isNewSdk):
            pos = exists(Template(r"tpl1709881469184.png", record_pos=(0.106, 0.186), resolution=resolution))

            if (pos):
                print(f'process_jiuyou_sdk, pos:{pos}')
                monitor_task_status(env, "登录阶段", "新版sdk-11隐私协议")
                lx_touch(pos, 2)
                lx_touch(loginButtonPos, 5)
                pos = exists(Template(r"tpl1709881469184.png", record_pos=(0.106, 0.186), resolution=resolution))
                if (pos):
                    monitor_task_status(env, "登录阶段", "新版sdk-22账号服务协议")
                    lx_touch(pos, 2)
                    lx_touch(loginButtonPos, 5)
        else:
            lx_wait_touch(Template(r"tpl1704788787130.png", record_pos=(0.128, 0.114), resolution=resolution), timeout=5, is_try=True)

        if lx_exists_touch(Template(r"tpl1709108013837.png", record_pos=(-0.102, 0.12), resolution=resolution)):
            monitor_task_status(env, "同意协议", "-")
            sleep(5)

    # status = process_risk_control(env)
    # if status == 2:
    #     monitor_task_status(env, "登录阶段", "风控未通过")
    #     lx_break_runloop(desc='风控未通过')
    # elif status == 1:
    #     monitor_task_status(env, "登录阶段", "风控通过")

    if (isNewSdk):
        # 截图判断 是历史页面还是 选择账号页面
        # 判断有几个账号
        isHistory = exists(Template(r"tpl1709867769179.png", record_pos=(0.121, -0.055), resolution=resolution))
        print(f'process_jiuyou_sdk, isHistory:{isHistory}')
        if (isHistory):
            lx_touch((1177,705), 5)

        else:
            if isNewSelect := exists(Template(r"tpl1709866910193.png", record_pos=(-0.0, 0.165), resolution=resolution)):
                print(f'process_jiuyou_sdk, isNewSelect:{isNewSelect}')
            elif isNewSelect := exists(Template(r"tpl1743586639947.png", record_pos=(-0.001, 0.405), resolution=resolution)):
                print(f'process_jiuyou_sdk, isNewSelect:{isNewSelect}')
            if (isNewSelect):

                shouldSwipe = False
                isFirst = True
                lastSwipeGameItem=None
                while(isFirst or shouldSwipe):
                    isFirst = False
                    file_name = 'jiuyou_sdk_' + str(int(time.time()*1000000)) + '.jpg'
                    if is_portrait_screen:
                        crop_start=(282,748)
                        crop_end=(1071,1656)
                    else:
                        crop_start=(795,202)
                        crop_end=(1607,1135)
                    crop_pos_img = crop_pos_image_from_snapshot(f"temp.jpg", file_name, crop_start,crop_end)

                    imagePath = AppEnv.get_instance().logPath + '/' + file_name

                    localFileList = []
                    localFileList.append(imagePath)
                    _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
                    if cdn_url_list:
                        jiuyou_sdk_img_url = cdn_url_list[0]

                    data = easRequest(get_env_ocr_path(env), getOCRRequestDataWithURL(jiuyou_sdk_img_url))
                    print(f'process_jiuyou_sdk, result:{data}')

                    if data is not None and 'message' in data and ('status' in data['message']) and ('data' in data['message']):
                        ocrResult = data['message']['data']
                        status = data['message']['status']

                        accountCount = 0
                        firstAccountBox = None
                        targetAccountBox = None
                        hasCharacterName = False
                        accountBoxes=[]
                        # transferName="297870080"
                        # transferName="507400139"
                        taskContentType = env.task_contenttype

                        transfer_account_info = env.transfer_account_info
                        print(f'process_jiuyou_sdk, transfer_account_info:{transfer_account_info}')
                        accountInfo = json.loads(transfer_account_info)

                        transferName = accountInfo["transferAccountName"]
                        print(f'process_jiuyou_sdk, transferName:{transferName}')

                        # 根据 box 中的第二个元素（y值）对 data 列表进行排序
                        sorted_data = sorted(ocrResult, key=lambda x: x['box'][0][1])
                        print(f'process_jiuyou_sdk, sorted_data:{sorted_data}')
                        lastGameItem=None

                        for item in sorted_data:
                            if item['txts'].startswith("游戏号"):
                                lastGameItem = item
                                text = item['txts']
                                print(f'process_jiuyou_sdk, accountItem:{text}')

                                accountCount = accountCount + 1
                                accountBoxes.append(item['box'])
                                if firstAccountBox is None:
                                    firstAccountBox = item['box'][3]
                            if item['txts'].startswith("游戏角色"):
                                hasCharacterName = True

                            if transferName in item['txts']:
                                targetAccountBox = item['box'][3]
                        print(f'process_jiuyou_sdk, accountCount:{accountCount} firstAccountBox:{firstAccountBox}, hasCharacterName:{hasCharacterName}, targetAccountBox:{targetAccountBox}')
                        if (accountCount ==1):
                            targetPos = (firstAccountBox[0]+crop_start[0], firstAccountBox[1]+crop_start[1])
                            print(f"process_jiuyou_sdk, 单账号, targetPos:{targetPos}")
                            lx_touch(targetPos, 5)
                        else:
                            if targetAccountBox:
                                targetPos = (targetAccountBox[0]+crop_start[0], targetAccountBox[1]+crop_start[1])
                                print(f"process_jiuyou_sdk, 找到:{transferName}, targetAccountBox:{targetAccountBox}, targetPos:{targetPos}")
                                lx_touch(targetPos, 5)

                                shouldSwipe = False
                                break
                            else:
                                print(f"process_jiuyou_sdk, 没有找到:{transferName}")
                                shouldSwipe = True

                            if lastSwipeGameItem is None:
                                lastSwipeGameItem = lastGameItem
                            else:
                                print(f"process_jiuyou_sdk, lastSwipeGameItem:{lastSwipeGameItem}, lastGameItem:{lastGameItem}")
                                if lastSwipeGameItem['txts'] == lastGameItem['txts'] and abs(lastGameItem['box'][0][1] - lastSwipeGameItem['box'][0][1]) < 10:
                                    shouldSwipe = False
                                else:
                                    shouldSwipe = True
                                    lastSwipeGameItem = lastGameItem

                    if (shouldSwipe):
                        swipe_start=(832,955)
                        swipe_end=(832,742)
                        if (hasCharacterName):
                            swipe_end=(832,742-50)
                        swipe_only(swipe_start, swipe_end)
                        sleep(1)
        if afterLoginFunc is not None:
            afterLoginFunc(env)
        else:
            afterLogin(env, isNewSdk)
    else:

        lx_wait_touch(Template(r"tpl1709887324825.png", record_pos=(0.115, 0.172), resolution=resolution), timeout=5, is_try=True)

        # 触发手机验证码风控
        if (lx_wait(Template(r"tpl1704872708786.png", record_pos=(0.38, -0.109), resolution=resolution), timeout=5, interval=0.5, is_try=True)):

            monitor_task_status(env, "登录阶段", "需要验证码", 10001)
            lx_break_app(desc='需要验证码',hold_game=True, ext_info={'key':'10001'})

        if exists(Template(r"tpl1710315541881.png", record_pos=(-0.002, 0.043), resolution=resolution)):
            print("检测到-九游-youka-新登录")
            monitor_task_status(env, "登录阶段", "账密出错,账号非手机号", 10008)
            lx_break_app(desc='账密出错,账号非手机号', hold_game=False,ext_info={'key':'10008'})

        if exists(Template(r"tpl1710315840124.png", record_pos=(0.001, 0.061), resolution=resolution)):
            print("检测到-九游-youka-旧登录")
            monitor_task_status(env, "登录阶段", "账密出错,账号非手机号", 10008)
            lx_break_app(desc='账密出错,账号非手机号', hold_game=False,ext_info={'key':'10008'})
        else:
            monitor_task_status(env, "登录阶段", "登录框已消失")

            if afterLoginFunc is not None:
                afterLoginFunc(env)
            else:
                afterLogin(env, isNewSdk)

def deleteInputText():
    monitor_task_status_v2("九游登录", "删除输入框内容")
    for _ in range(30):
        shell("input keyevent 67")
    sleep(1)

def afterLogin(env, isNewSdk=False):

    if (isNewSdk):
        sleep(5)
        lx_wait_touch(Template(r"tpl1709887324825.png", record_pos=(0.115, 0.172), resolution=(2400, 1350)), timeout=5, is_try=True)
        sleep(2)
        lx_wait_touch(Template(r"tpl1709887324825.png", record_pos=(0.115, 0.172), resolution=(2400, 1350)), timeout=2, is_try=True)
        sleep(3)
        name = 'adc_catch_to_enter_check_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=name, msg="get a snapshot.")
        # 点击进入游戏
        if exists(Template(r"tpl1699499196274.png", record_pos=(-0.47, 0.163), resolution=(2400, 1350))):
            # 点击进入游戏(1210,1046)
            touch((2000, 700))
            sleep(8)
            monitor_task_status(env, "登录阶段jiuyou", "点击进入游戏")
    # 登录成功的
    name = 'adc_catch_login_done_check_' + str(int(time.time() * 1000000)) + '.jpg'
    lx_safe_snapshot(filename=name, msg="get a snapshot.")
    monitor_task_status(env, "登录后", "进入首页")
    #无互踢逻辑等