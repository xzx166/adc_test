# -*- encoding=utf8 -*-
from airtest.core.api import *

from utility.biz_utils.biz_tools import *

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


ENV = AppEnv.get_instance()
DEV = ENV.device
localRun = ENV.launchType == "localtest"

# 查找图片路径
add_image_basedir = lambda path: G.BASEDIR.append(path) if path not in G.BASEDIR else None
baseDir = Path(__file__).resolve().parent
add_image_basedir(str(baseDir))

# 获取分辨率
get_resolution = lambda: DEV.get_current_resolution()
# 竖屏
screen_vertical = lambda: DEV.display_info["orientation"] in (1, 3)

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
            monitor_task_status_v2("XIAOMI_POCO启动失败", traceback.format_exc())
            sleep(3)

# xiaomiPoco = launchPoco()

def activityApps():
    """
    正在活动app
    :return: applist
    """
    try:
        # 前台应用
        activityComponent = shell("dumpsys window | grep mCurrentFocus")
        applist = re.findall(r"mCurrentFocus.*u0\s(.*?)/", activityComponent)

    except Exception as e:
        monitor_print(f"---activityAppsError: {e}")
        return []
    return applist

# 小米渠道比较特殊，要预先判断是否直接进入了切换子账号的页面，如果是的话，就可以直接走
def check_qiehuan_pos(timeout=30, login_shuping=False):
    w, h = DEV.display_info["width"], DEV.display_info["height"]
    if login_shuping:
        resolution = (h, w)
        monitor_task_status_v2("识别切换小号", f"竖屏识别切换小号：{resolution}")
    else:
        resolution = (w, h)
        monitor_task_status_v2("识别切换小号", f"横屏识别切换小号：{resolution}")

    if localRun:
        timeout = 5
    # 切换子账号
    if qiehuan_zizhanghao_pos := lx_safe_wait_touch(Template(r"tpl20250825162015.png", threshold=0.85, resolution=resolution), timeout=timeout):
        monitor_task_status_v2("登录阶段", f"切换小号按钮位置：{qiehuan_zizhanghao_pos}")
        if lx_safe_wait(Template(r"tpl20250825162539.png", resolution=resolution), timeout=3):
            return True

# 开始
def loginTaskXiaomi(
        env,
        preLoginFunc=None,
        afterLoginFunc=None,
        direct_enter=False,
        login_shuping=False,
        first_check_qiehuan_timeout=30,
        save_login_state=True,
        **kwgs):
    """
    小米登录SDK
    :param env: 环境变量
    :param preLoginFunc: 登录前处理
    :param afterLoginFunc: 登录后处理
    :param direct_enter: 是否直接进入, 识别切换小号前不做处理
    :param login_shuping: 登录界面是竖屏
    :param first_check_qiehuan_timeout: 首次识别切换小号超时
    :param save_login_state: 保存登录态
    :param kwgs: 额外参数
    :return:
    """
    lx_safe_snapshot(f"adc_catch_小米登录开始_{str(int(time.time() * 1000000))}.jpg")

    # 识别切换小号前调用preLoginFunc
    if not direct_enter and callable(preLoginFunc):
        preLoginFunc(env)

    monitor_task_status_v2(f"登录阶段", "开始检测小米登录态")
    for i in range(3):
        if i == 0:
            timeout = first_check_qiehuan_timeout
        else:
            timeout = 20

        if check_qiehuan_pos(timeout=timeout, login_shuping=login_shuping):
            xiaomiChildAccountOCR(env, save_login_state)
            break
        else:
            if preXiaomiLogin():
                continue
            # 识别切换小号后调用preLoginFunc
            if direct_enter and callable(preLoginFunc):
                preLoginFunc(env)
            xiaomiLogin()
    else:
        monitor_task_status_v2("登录阶段", f"未找到切换小号", status=10199)
        lx_break_runloop(desc=f"未找到切换小号")

    # 登录完成后处理
    afterXiaomiLogin()
    if callable(afterLoginFunc):
        afterLoginFunc(env)

def preXiaomiLogin():
    if lx_safe_wait(Template(r"tpl20250828165838.png", threshold=0.85, resolution=get_resolution()), timeout=2):
        monitor_task_status_v2("登录阶段", "识别到新版本弹窗")
        if lx_safe_wait_touch(Template(r"tpl20250828165032.png", threshold=0.85, resolution=get_resolution()), timeout=2):
            monitor_task_status_v2("登录阶段", "点击取消")
            return True

def afterXiaomiLogin():
    for _ in range(2):
        activityApp = activityApps()
        if "com.xiaomi.gamecenter.sdk.service" in activityApp:
            monitor_task_status_v2("小米登录", f"未进入游戏：{format_print(activityApp)}")
            lx_safe_snapshot(filename=f"adc_catch_小米未进入游戏_{str(int(time.time() * 1000000))}.jpg")
            if lx_safe_wait_touch(Template(r"tpl1730125767904.png", record_pos=(0.264, -0.197), resolution=(2400, 1350)), timeout=1, sec=1):
                monitor_task_status_v2("小米登录", "关闭弹窗1")

            if lx_safe_wait_touch(Template(r"tpl1747730871234.png", record_pos=(0.182, -0.149), resolution=(2400, 1350)), timeout=1, sec=1):
                monitor_task_status_v2("小米登录", "关闭弹窗2")

            if lx_safe_wait_touch(Template(r"tpl1746700607881.png", record_pos=(0.264, -0.212), resolution=(2400, 1350)), timeout=1, sec=1) or \
                lx_safe_wait_touch(Template(r"tpl1746700618493.png", record_pos=(0.264, -0.213), resolution=(2400, 1350)), timeout=1, sec=1):
                monitor_task_status_v2("小米登录", "关闭弹窗3")

            if lx_safe_wait_touch(Template(r"tpl1747734634107.png", record_pos=(0.26, -0.188), resolution=(2400, 1350)), timeout=1, sec=1):
                monitor_task_status_v2("小米登录", "关闭弹窗4")

        else:
            monitor_task_status_v2("小米登录", f"正在运行：{format_print(activityApp)}")
            break

def back(n=1, sec=1.5):
    """
    返回键
    :param n: 执行次数
    :param sec: 执行后等待
    :return: 无
    """
    for _ in range(n):
        keyevent("BACK")
        sleep(sec)

# 小米登录
def xiaomiLogin():
    # 兼容登录态丢失
    username = AppEnv.get_instance().get_account_attr_with_key("XIAOMI_LOGIN_MOBILE")
    password = ENV.password

    # if localRun:
    #     username = ""
    #     password = ""

    if lx_safe_wait_touch(Template(r"tpl20250824194903.png", threshold=0.85, resolution=get_resolution()), timeout=5, sec=2):
        lx_safe_snapshot(filename=f"adc_catch_小米登录开始_{str(int(time.time() * 1000000))}.jpg")
        monitor_task_status_v2("登录阶段", "小米登录开始")
        # 检测小米登录页面
        lx_safe_snapshot(filename=f"adc_catch_小米登录页_{str(int(time.time() * 1000000))}.jpg")
        if not lx_safe_wait(Template(r"tpl1756040358116.png", record_pos=(-0.002, -0.635), resolution=(1350, 2400)), timeout=5):
            lx_break_runloop(desc="登录阶段，未成功检测到登录页面")

        # 点击密码登录
        lx_safe_touch((675, 1010), 1)
        # 点击同意协议
        lx_safe_touch((340, 890), 1)
        # 输入账号
        lx_safe_touch((675, 620), 1)
        adc_input(username)
        back()
        monitor_task_status_v2("登录阶段", f"输入账号完成：{username}")
        # 输入密码
        lx_safe_touch((675, 780), 1)
        adc_input(password)
        back()
        monitor_task_status_v2("登录阶段", f"输入密码完成")
        lx_safe_snapshot(filename=f"adc_catch_账密输入完成_{str(int(time.time() * 1000000))}.jpg")
        # 点击登录
        lx_safe_touch((675, 1040), 1)

# 选择子账号
def xiaomiChildAccountOCR(env, save_login_state):
    transferAccountName = AppEnv.get_instance().get_transfer_accountInfo_with_key("transferAccountName")
    # gameNickName = AppEnv.get_instance().get_account_attr_with_key("GAME_NICK_NAME")

    # if localRun:
    #     transferAccountName = "jymtg"

    gameID = env.gameDir.split("_")[0]
    accountNameMapPath = (Path(__file__).parent / "accountNameMap.json").resolve()
    accountNameMap = {}
    if accountNameMapPath.exists():
        accountNameMap.update(json.loads(accountNameMapPath.read_text()))

    resolution = get_resolution()

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
        new_account_name = transferAccountName.rstrip('.')
        # 处理双下划线
        if "__" in new_account_name:
            new_account_name = new_account_name.replace("__", "_")
            monitor_print(f"---xiaomi_compatible_transferAccountName:{new_account_name},{transferAccountName}")
        return new_account_name

    checked = False

    # 横屏
    if resolution[0] > resolution[1]:
        start_x_offset = 780
        start_y_offset = 200
        crop_eas_pos_start = (start_x_offset, start_y_offset)
        crop_eas_pos_end = (1330, 1350)
        touch_x = 1490
        touch_y_offset = 45
    # 竖屏
    else:
        start_x_offset = 0
        start_y_offset = 1315
        crop_eas_pos_start = (start_x_offset, start_y_offset)
        crop_eas_pos_end = (1350, 2400)
        touch_x = 1220
        touch_y_offset = 45

    transferAccountName_split = transferAccountName.split("_", 1)[0]
    # 特殊字符
    special_pattern = re.compile(r"[丿\-_乀灬丨|｜\s]")
    for try_index in range(3):
        name = f'adc_catch_小米子账号_{try_index}_' + str(int(time.time() * 1000000)) + '.jpg'
        lx_safe_snapshot(filename=name, msg="get a snapshot.")
        ocrResult = getXiaomiImageCropPosForEASPro(name, crop_eas_pos_start, crop_eas_pos_end)
        monitor_print(f"---xiaomi_ocr_ocrResult: {ocrResult}")

        if ocrResult is not None:
            match_all_results = []
            match_all_string = []

            for i in range(len(ocrResult)):
                val: str = ocrResult[i]['txts']
                strip_val = val.rstrip('.').strip("，").strip(",")
                strip_transferAccountName: str = compatible_transferAccountName(transferAccountName)
                strip_val_split = strip_val.split("_", 1)[0]
                monitor_task_status_v2(f"Account name match", f"{strip_val}: {strip_transferAccountName}")

                # 默认帐号
                if strip_val == '默认帐号':
                    continue

                # 普通字符
                if strip_val in strip_transferAccountName:
                    match_all_results.append(ocrResult[i])
                    match_all_string.append(val)
                    break

                # 特殊字符
                elif special_pattern.sub("", strip_val) in special_pattern.sub("", strip_transferAccountName):
                    match_all_results.append(ocrResult[i])
                    match_all_string.append(val)
                    break

                # 账号映射1
                accountName = accountNameMap.get(gameID, {}).get(strip_val_split, "")
                if len(accountName) > 0 and accountName == transferAccountName_split:
                    match_all_results.append(ocrResult[i])
                    match_all_string.append(val)
                    break

                # 账号映射2
                accountName = accountNameMap.get(gameID, {}).get(strip_val, "")
                if len(accountName) > 0 and strip_transferAccountName.startswith(accountName):
                    match_all_results.append(ocrResult[i])
                    match_all_string.append(val)
                    break

            monitor_print(f"---xiaomi_check_match_all_results:{match_all_results}")
            monitor_print(f"---xiaomi_check_match_all_string:{match_all_string}")

            if len(match_all_string) >= 1:
                longest_index = find_longest_string_index(match_all_string)
                cur_result = match_all_results[longest_index]

                checked = True

                monitor_print(f"---xiaomi_right_transferAccountName:{match_all_string[longest_index]},{transferAccountName}")
                monitor_task_status_v2("登录阶段", f"成功登录的子账号信息:{match_all_string[longest_index]}, {transferAccountName}")

                name = 'adc_catch_子账号选择前_' + str(int(time.time() * 1000000)) + '.jpg'
                lx_safe_snapshot(filename=name, msg="get a snapshot.")

                boxY = int(cur_result['box'][0][1])

                pos = (touch_x, start_y_offset + boxY + touch_y_offset)
                lx_safe_touch(pos, 1)
                monitor_task_status_v2("登录阶段", f"子账号信息点击位置：{pos}")

                name = 'adc_catch_子账号选择后_' + str(int(time.time() * 1000000)) + '.jpg'
                lx_safe_snapshot(filename=name, msg="get a snapshot.")

        if checked:
            sleep(2)
            break
        else:
            start_point = resolution[0] // 2, resolution[1] - 300
            end_point = start_point[0], start_point[1] - 300
            adc_swipe(start_point, end_point, sec=1)
            sleep(1)

    if not checked:
        monitor_task_status_v2("登录阶段", f"子账号未成功检测", status=10199)
        lx_break_runloop(desc=f"登录阶段_子账号未成功检测_{transferAccountName}")
    elif save_login_state:
        AppDynamicInfo.get_instance().setHasLogin(True)


# ================= eas 2.0 信息 ===========================
def getXiaomiImageCropPosForEASPro(filename, crop_start, crop_end):
    cropFileName = f'crop_xiaomi_eas_pro_' + str(int(time.time() * 1000000)) + '.jpg'
    crop_pos_image_from_snapshot(filename, cropFileName, crop_start, crop_end, need_snapshot=False)
    name_crop_image_path = os.path.join(ST.LOG_DIR, cropFileName)

    data = []
    data.extend(ocr_image_by_eas(name_crop_image_path, type=2))
    data.extend(ocr_image_by_eas(name_crop_image_path, type=1))
    monitor_print(f"---cropFileNameOCR: {filename}-{data}")

    return data
