# -*- encoding=utf8 -*-
from airtest.core.api import *
import time
import sys
import cv2
import json


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

g_compatable_account_func = None

# 10台设备是用于小米渠道的
# 584 xiaomituoguan11@lingxigames.com
# 585 xiaomituoguan12@lingxigames.com
# 533-540  (xiaomituoguan13@lingxigames.com -> xiaomituoguan20@lingxigames.com)

def test_xiaomi():
    zizhanghao_page_pos = lx_wait(
        Template(r"tpl1732260315561.png", record_pos=(-0.04, -0.149), resolution=(1350, 2400)),
        timeout=5, is_try=True)
    if zizhanghao_page_pos is None:
        print('未成功检测到-xiaomi切换子账号页面')
    else:
        print(f'成功检测到-xiaomi切换子账号页面:{zizhanghao_page_pos}')
    return

    # xiaomi_denglu_pos = lx_wait(Template(r"tpl1729764113818.png",threshold=0.85, record_pos=(0.0, -0.211), resolution=(2400, 1350)),
    #                             timeout=8, interval=1, is_try=True)
    # if xiaomi_denglu_pos is None:
    #     print('未成功检测到-xiaomi切换子账号页面')
    # else:
    #     print(f'成功检测到-xiaomi切换子账号页面:{xiaomi_denglu_pos}')
    # return

def loginTaskXiaomi(env, preLoginFunc=None, afterLoginFunc=None, direct_enter=False, login_shuping=False, compatable_account_func=None):
    lx_snapshot_api(filename=f"adc_catch_xiaomi_start_login_{str(int(time.time() * 1000000))}.jpg")

    global g_compatable_account_func
    g_compatable_account_func = compatable_account_func
    # test_xiaomi()
    # return

    # if AppDynamicInfo.get_instance().getHasLogin():
    #     if preLoginFunc is not None:
    #         preLoginFunc(env)
    #
    #     sleep(3)
    #
    #     afterXiaomiLogin(env)
    #
    #     if afterLoginFunc is not None:
    #         afterLoginFunc(env)
    #     monitor_task_status(env, "登录", "getHasLogin已登录")
    #     lx_break_phase(desc='已登录')
    # else:

    ##未登录check逻辑需要交给
    if direct_enter == False:
        if preLoginFunc is not None:
            preLoginFunc(env)

        # lx_snapshot_api(filename=f"adc_catch_xiaomi_after_preLoginFunc_{str(int(time.time() * 1000000))}.jpg")
        monitor_print(f"---登录阶段,开始小米检测登录态")

        qiehuan_pos = None
        final_resolution = (2400, 1350)
        if login_shuping == True:
            monitor_task_status_v2("小米登录阶段", f"当前登录是竖屏")
            final_resolution = (1350, 2400)

        qiehuan_pos = wait_xiaomi_qiehuan_xiaohao(resolution=final_resolution)

        if qiehuan_pos is not None:
            # #这里优先点击处理，不然担心后续的流程切换按钮消失
            # change_qiehuan_zizhanghao_pos = (qiehuan_pos[0] + 20, qiehuan_pos[1] + 4)
            # lx_touch(change_qiehuan_zizhanghao_pos, 2)

            processXiaomiLogin(env, preLoginFunc, afterLoginFunc, qiehuan_pos=qiehuan_pos, resolution=final_resolution)
        else:
            preXiaomiLogin(env)
            processXiaomiLogin(env, preLoginFunc, afterLoginFunc, resolution=final_resolution)
    else:
        monitor_print(f"---登录阶段,开始小米检测登录态")

        qiehuan_pos = None
        final_resolution = (2400, 1350)
        if login_shuping == True:
            monitor_task_status_v2("小米登录阶段", f"当前登录是竖屏")
            final_resolution = (1350, 2400)

        qiehuan_pos = wait_xiaomi_qiehuan_xiaohao(resolution=final_resolution)

        if qiehuan_pos is not None:
            # #这里优先点击处理，不然担心后续的流程切换按钮消失
            # change_qiehuan_zizhanghao_pos = (qiehuan_pos[0] + 20, qiehuan_pos[1] + 4)
            # lx_touch(change_qiehuan_zizhanghao_pos, 2)

            processXiaomiLogin(env, preLoginFunc, afterLoginFunc, qiehuan_pos=qiehuan_pos, resolution=final_resolution)
        else:
            preXiaomiLogin(env)

            if preLoginFunc is not None:
                preLoginFunc(env)

            processXiaomiLogin(env, preLoginFunc, afterLoginFunc, resolution=final_resolution)


    afterXiaomiLogin(env)

    if afterLoginFunc is not None:
        afterLoginFunc(env)

def preXiaomiLogin(env):
    xieyi_pos = lx_wait(
        Template(r"tpl1729582429575.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
        timeout=3, is_try=True)
    if xieyi_pos is not None:
        lx_touch((1422, 977), 1)

    banben_gengxin_pos = lx_wait(
        Template(r"tpl1731049827014.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
        timeout=3, is_try=True)
    if banben_gengxin_pos is not None:
        lx_touch((981, 1129), 1)

def afterXiaomiLogin(env):
    # 处理可能的协议
    lx_snapshot_api(filename=f"adc_catch_xiaomi_before_xiaomixieyi_{str(int(time.time() * 1000000))}.jpg")

    tongyi_xieyi_pos = lx_wait(
        Template(r"tpl1729572126579.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
        timeout=8, is_try=True)
    if tongyi_xieyi_pos is not None:
        lx_touch((1478, 1081), 1)

    youhui_fuceng_pos = lx_wait(
        Template(r"tpl1729737127402.png", record_pos=(-0.04, -0.149), resolution=(2400, 1350)),
        timeout=8, is_try=True)
    if youhui_fuceng_pos is not None:
        lx_touch((1841, 162), 1)


def process_denglutai_miss(username, password, resolution=(2400, 1350)):
    env = AppEnv.get_instance()

    is_denglutai_miss = False
    # 兼容登录态丢失
    lx_snapshot_api(filename=f"adc_catch_xiaomi_denglutai_miss_{str(int(time.time() * 1000000))}.jpg")
    xiaomi_denglu_pos = lx_wait(
        Template(r"tpl1729764113818.png", threshold=0.85, record_pos=(0.0, -0.211), resolution=resolution),
        timeout=8, interval=1, is_try=True)
    if xiaomi_denglu_pos is None:
        monitor_task_status_v2("登录阶段", "未检测到小米登录入口")
        return is_denglutai_miss


    is_denglutai_miss = True
    # 检测到xiaomi登录
    lx_touch(xiaomi_denglu_pos, 1)

    # 检测小米登录页面
    lx_snapshot_api(filename=f"adc_catch_xiaomi_denglutai_miss_page_{str(int(time.time() * 1000000))}.jpg")
    xiaomi_denglu_page_pos = lx_wait(Template(r"tpl1729764474184.png", record_pos=(0.0, -0.211), resolution=(1350, 2400)),
                                timeout=5, interval=1, is_try=True)
    if xiaomi_denglu_page_pos is None:
        lx_break_runloop(desc="---登录阶段,未成功检测到登录页面")

    # 点击密码登录
    lx_touch((687, 1350), 2)

    # 点击同意协议
    lx_touch((246,1175), 1)

    # 点击输入账号
    lx_touch((343, 812), 1)

    shell("input text {}".format(username))
    monitor_task_status(env, "登录阶段", f"账号:{username}")
    sleep(AppEnv.get_instance().sleepTime * 1)

    # 点击输入密码
    lx_touch((396, 691), 1)

    shell("input text {}".format(password))
    monitor_task_status(env, "登录阶段", "password")
    sleep(AppEnv.get_instance().sleepTime * 1)

    lx_snapshot_api(filename=f"adc_catch_xiaomi_denglutai_miss_dengluwan_{str(int(time.time() * 1000000))}.jpg")

    # # 判断忘记密码的位置，推算同意位置
    # wangjimima_pos = lx_wait(Template(r"tpl1729064423575.png", record_pos=(0.0, -0.211), resolution=(2400, 1350)),
    #                          timeout=3,
    #                          interval=1, is_try=True)
    # if wangjimima_pos is None:
    #     lx_break_runloop(desc="登录阶段, 未成功检测到-忘记密码")
    #
    # xieyi_agree_pos = (wangjimima_pos[0] - 75, wangjimima_pos[1] + 125)
    # lx_touch(xieyi_agree_pos, 1)
    #
    # tongyi_anniu_pos = (xieyi_agree_pos[0], xieyi_agree_pos[1] - 152)
    # lx_touch(tongyi_anniu_pos, 1)

    # 点击登录
    lx_touch((691, 1045))
    return is_denglutai_miss

# 小米渠道比较特殊，要预先判断是否直接进入了切换子账号的页面，如果是的话，就可以直接走
def wait_xiaomi_qiehuan_xiaohao(resolution=(2400, 1350)):
    # 切换子账号
    if qiehuan_zizhanghao_pos := lx_wait(Template(r"tpl1729566341102.png", record_pos=(-0.04, -0.149), threshold=0.85, resolution=resolution), timeout=20, interval=0.1, is_try=True):
        # change_qiehuan_zizhanghao_pos = (qiehuan_zizhanghao_pos[0] + 20, qiehuan_zizhanghao_pos[1] + 4)
        lx_touch(qiehuan_zizhanghao_pos)
        for _ in range(5):
            if not lx_wait_touch(Template(r"tpl1729566341102.png", record_pos=(-0.04, -0.149), resolution=resolution), timeout=0.5, interval=0.1, is_try=True):
                sleep(2)
                break
        monitor_task_status_v2("登录阶段", f"切换小号按钮位置：{qiehuan_zizhanghao_pos}")
        return qiehuan_zizhanghao_pos

def processXiaomiLogin(env, preLoginFunc=None, afterLoginFunc=None, qiehuan_pos = None, resolution=(2400, 1350)):
    print('processXiaomiLoginprocessXiaomiLogin')
    password = env.password
    transferAccountName= AppEnv.get_instance().get_transfer_accountInfo_with_key("transferAccountName")

    gameNickName = None
    login_account = None
    if AppEnv.get_instance().account_attr is not None and len(AppEnv.get_instance().account_attr) > 0:
        gameNickName = AppEnv.get_instance().get_account_attr_with_key("GAME_NICK_NAME")
        login_account = AppEnv.get_instance().get_account_attr_with_key("XIAOMI_LOGIN_MOBILE")

    # 子账号状态：0标识需要识别子账号，1标识只有1个子账号直接进入游戏
    zizhanghao_check_status = 0

    # 切换子账号
    if qiehuan_pos is not None:
        qiehuan_zizhanghao_pos = qiehuan_pos
    elif qiehuan_zizhanghao_pos := lx_wait(Template(r"tpl1729566341102.png", record_pos=(-0.04, -0.149), threshold=0.85, resolution=resolution), timeout=5, interval=0.1, is_try=True):
        change_qiehuan_zizhanghao_pos = (qiehuan_zizhanghao_pos[0] + 20, qiehuan_zizhanghao_pos[1] + 4)
        lx_touch(change_qiehuan_zizhanghao_pos)
        for _ in range(5):
            if not lx_wait_touch(Template(r"tpl1729566341102.png", record_pos=(-0.04, -0.149), resolution=resolution), timeout=0.5, interval=0.1, is_try=True):
                sleep(2)
                break
        monitor_task_status_v2("登录阶段", f"点击切换小号按钮：{change_qiehuan_zizhanghao_pos}")

    if not qiehuan_zizhanghao_pos:
        monitor_task_status_v2("登录阶段", "没有探测到切换小号按钮")
        # 没有找到切换小号，可能有两种情况，一种是没有子账号，直接进入游戏，一种是登录态丢失，需要处理登录
        # lx_break_runloop(desc="登录阶段, 未成功检测到-xiaomi切换子账号入口")
        # 未找到切换小号的情况下，处理登录态丢失问题
        if process_denglutai_miss(login_account, password, resolution=resolution):
            # 处理登录态丢失后，要重新判断切换小号
            if qiehuan_zizhanghao_pos := lx_wait(Template(r"tpl1729566341102.png", record_pos=(-0.04, -0.149), resolution=resolution), timeout=8, interval=0.1, is_try=True):
                change_qiehuan_zizhanghao_pos = (qiehuan_zizhanghao_pos[0] + 20, qiehuan_zizhanghao_pos[1] + 4)
                lx_touch(change_qiehuan_zizhanghao_pos)
                for _ in range(5):
                    if not lx_wait_touch(Template(r"tpl1729566341102.png", record_pos=(-0.04, -0.149), resolution=resolution), timeout=0.5, interval=0.1, is_try=True):
                        sleep(2)
                        break
                monitor_task_status_v2("登录阶段", f"登录态丢失，重登后，探测到切换小号按钮：{change_qiehuan_zizhanghao_pos}")
            else:
                monitor_task_status_v2("登录阶段", "登录态丢失，重登后，没有探测到切换小号按钮，直接进入游戏")
                zizhanghao_check_status = 1
        else:
            monitor_task_status_v2("登录阶段", "登录态保持，直接进入游戏")
            zizhanghao_check_status = 1

    if zizhanghao_check_status == 1:
        monitor_task_status_v2("登录阶段", f"未找到切换小号", status=10199)
        lx_break_runloop(desc=f"---登录阶段_重新登录子账号未成功检测: {transferAccountName}")

    # 这个之前不要做任何事情，不然可能会影响对切换小号的相应
    # lx_snapshot_api(filename=f"adc_catch_xiaomi_before_qiehuanxiaohao_{str(int(time.time() * 1000000))}.jpg")

    lx_snapshot_api(filename=f"adc_catch_xiaomi_after_qiehuanxiaohao_{str(int(time.time() * 1000000))}.jpg")

    if resolution[0] == 2400:
        zizhanghao_page_pos = lx_wait(Template(r"tpl1729569672509.png", record_pos=(-0.04, -0.149), resolution=resolution), timeout=5, is_try=True)
    else:
        zizhanghao_page_pos = lx_wait(Template(r"tpl1732260315561.png", record_pos=(-0.04, -0.149), resolution=resolution), timeout=5, is_try=True)

    if zizhanghao_page_pos is None:
        monitor_task_status_v2("登录阶段", f"未找到切换小号", status=10199)
        lx_break_runloop(desc=f"---登录阶段_子账号未成功检测: {transferAccountName}")
    else:
        xiaomiLoginClicked(env, transferAccountName, checkNickName=gameNickName, resolution=resolution)

#================
#登录点击后  子账号逻辑
#================
def xiaomiLoginClicked(env, transferAccountName, checkNickName=None, resolution=(2400, 1350)):
    gameID = env.gameDir.split("_")[0]
    accountNameMapPath = (Path(__file__).parent / "accountNameMap.json").resolve()
    accountNameMap = {}
    if accountNameMapPath.exists():
        accountNameMap.update(json.loads(accountNameMapPath.read_text()))

    checked = False

    global g_compatable_account_func

    def find_longest_string_index(strings):
        if not strings:  # 如果数组为空
            return -1

        longest_index = 0  # 假设第一个字符串是最长的
        longest_length = len(strings[0])  # 第一字符串的长度

        for index in range(1, len(strings)):
            current_length = len(strings[index])
            if current_length > longest_length:
                longest_length = current_length
                longest_index = index

        return longest_index

    def compatible_transferAccountName(transferAccountName):
        global g_compatable_account_func
        new_account_name = transferAccountName.rstrip('.')
        if g_compatable_account_func is not None:
            new_account_name = g_compatable_account_func(new_account_name)
        # 上面的代码不要动，自定义的兼容在这个处理完后再处理

        # 处理双下划线
        if "__" in new_account_name:
            new_account_name = new_account_name.replace("__", "_")
            monitor_print(f"---xiaomi_compatible_transferAccountName:{new_account_name},{transferAccountName}")
        return new_account_name


    checked = False

    start_x_offset = 727
    start_y_offset = 328

    crop_eas_pos_start = (start_x_offset, start_y_offset)
    crop_eas_pos_end = (1480, 1290)

    touch_y_offset = 123

    if resolution == (1350, 2400):
        start_x_offset = 198
        start_y_offset = 803
        crop_eas_pos_start = (start_x_offset, start_y_offset)
        crop_eas_pos_end = (985, 1679)

        touch_y_offset = 110

    transferAccountName_split = transferAccountName.split("_", 1)[0]
    # 特殊字符
    special_pattern = re.compile(r"[丿\-_乀灬丨|｜\s]")
    for try_index in range(3):
        name = f'adc_catch_xiaomi_zizhanghao_account_area_{try_index}_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=name, msg="get a snapshot.")

        ocrResult = getXiaomiImageCropPosForEASPro(name, crop_eas_pos_start, crop_eas_pos_end)
        monitor_print(f"---xiaomi_ocr_ocrResult: {ocrResult}")

        if ocrResult is not None:
            match_all_results = []
            match_all_string = []

            for i in range(len(ocrResult)):
                val = ocrResult[i]['txts']
                strip_val = val.rstrip('.')
                strip_transferAccountName = compatible_transferAccountName(transferAccountName)
                strip_val_split = strip_val.split("_", 1)[0]
                # monitor_task_status_v2(f"Account name match", f"{strip_val}: {strip_transferAccountName}")
                monitor_task_status_v2(f"Account name match", f"{strip_val_split}: {transferAccountName_split}")

                if strip_val in strip_transferAccountName:
                    if strip_val == '默认帐号' or strip_val == '默认账号':
                        pass
                    else:
                        match_all_results.append(ocrResult[i])
                        match_all_string.append(val)
                else:
                    if special_pattern.sub("", strip_val) in special_pattern.sub("", strip_transferAccountName):
                        if strip_val == '默认帐号' or strip_val == '默认账号':
                            pass
                        else:
                            match_all_results.append(ocrResult[i])
                            match_all_string.append(val)

                    elif accountNameMap.get(gameID, {}).get(strip_val_split) == transferAccountName_split:
                        monitor_task_status_v2(f"xiaomi匹配成功", f"{strip_val_split}: {transferAccountName_split}")
                        if strip_val == '默认帐号' or strip_val == '默认账号':
                            pass
                        else:
                            match_all_results.append(ocrResult[i])
                            match_all_string.append(val)

                    elif '默认帐号' in strip_val:
                        strip_val = strip_val.replace("默认帐号", "默认账号")
                        if strip_val in strip_transferAccountName:
                            if strip_val == '默认帐号' or strip_val == '默认账号':
                                pass
                            else:
                                match_all_results.append(ocrResult[i])
                                match_all_string.append(val)

            monitor_print(f"---xiaomi_check_match_all_results:{match_all_results}")
            monitor_print(f"---xiaomi_check_match_all_string:{match_all_string}")

            if len(match_all_string) >= 1:

                longest_index = find_longest_string_index(match_all_string)
                cur_result = match_all_results[longest_index]

                checked = True

                monitor_print(f"---xiaomi_right_transferAccountName:{match_all_string[longest_index]},{transferAccountName}")
                monitor_task_status_v2("登录阶段", f"成功登录的子账号信息:{match_all_string[longest_index]}, {transferAccountName}")

                name = 'adc_catch_xiaomi_selected_before_' + str(int(time.time() * 1000000)) + '.jpg'
                lx_safe_snapshot(filename=name, msg="get a snapshot.")

                boxY = cur_result['box'][0][1]

                lx_touch((start_x_offset + 147, start_y_offset + boxY + touch_y_offset))
                monitor_task_status_v2("登录阶段", f"子账号信息点击位置：{(start_x_offset + 147, start_y_offset + boxY + touch_y_offset)}")
                sleep(1)

                name = 'adc_catch_xiaomi_selected_end_' + str(int(time.time() * 1000000)) + '.jpg'
                lx_safe_snapshot(filename=name, msg="get a snapshot.")


        if checked == True:
            sleep(2)
            break
        else:
            break
            # swipe_only((849, 722), (849, 516))
            # sleep(1)

    if checked == False:
        monitor_task_status_v2("登录阶段", f"未找到切换小号", status=10199)
        lx_break_runloop(desc=f"登录阶段_子账号未成功检测_{transferAccountName}")
    else:
        AppDynamicInfo.get_instance().setHasLogin(True)



# ================= eas 2.0 信息 ===========================
def getXiaomiImageCropPosForEASPro(filename, crop_start, crop_end):
    cropFileName = f'crop_xiaomi_eas_pro_' + str(int(time.time() * 1000000)) + '.jpg'

    crop_pos_img = crop_pos_image_from_snapshot(filename, cropFileName, crop_start, crop_end, need_snapshot=False)

    name_crop_image_path = os.path.join(ST.LOG_DIR, cropFileName)

    data = []
    data.extend(ocr_image_by_eas(name_crop_image_path, type=2))
    data.extend(ocr_image_by_eas(name_crop_image_path, type=1))

    return data






