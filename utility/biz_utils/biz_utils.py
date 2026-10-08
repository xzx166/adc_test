"""
╔═════════════════════════════╗
║   ______ _     _   _ _      ║
║   | ___ (_)   | | | | |     ║
║   | |_/ /_ ___| | | | |_    ║
║   | ___ \ |_  / | | | __|   ║
║   | |_/ / |/ /| |_| | |_    ║
║   \____/|_/___|\___/ \__|   ║
║  -------------------------  ║
║  请在导入本模块前配置好环境变量  ║
╚═════════════════════════════╝
import os
from pathlib import Path

os.environ.update(
    # 主程序/资源目录
    mainDir=str(Path(__file__).resolve().parent),
    # 游戏/应用运行时屏幕方向, portrait 或 landscape
    screenOrientation="landscape",
    # 是否启用POCO, 非必要不启用
    # poco_enable="true",
    # 是否启用子线程, 非必要不启用
    # thread_status="run",
    # 游戏/应用名称
    gameName="第五人格",
    # 游戏/应用包名, 仅适用非 common 运行时
    # packageName="com.netease.dwrg.aligames",
    # 本地测试游戏包名
    packageName_test="com.netease.dwrg",
    # 本地测试游戏渠道
    platform_test="netease",
)
from utility.biz_utils.biz_utils import *
"""
from utility.biz_utils.base_module import *
from utility.biz_utils.biz_tools import *
from utility.biz_utils.LLM import *
from utility.biz_utils.OCR import *
from utility.biz_utils.track import MotionTrackSuper
from utility.biz_utils.properties_tools import (
    properties_organize,
    properties_organize_simple,
    properties_organize_simple_v2
)
monitor_task_status_v2("Welcome To Use Biz Utils")

jym_oss_url = "https://static-cdn.jiaoyimao.com"
ENV = AppEnv.get_instance()
DEV = ENV.device
ENV_ATTR = json.loads(ENV.account_attr) if hasattr(ENV, "account_attr") and ENV.account_attr else {}

# 操作系统
system_type = ENV.system_type
isAndroid = system_type == 'android'
isiOS = system_type == 'ios'
isiOSCloud = system_type == 'yunyou_ios'

# 主程序/资源目录
mainDir = os_env.get("mainDir", "") or os_env.get("indexDir", "")
if mainDir:
    mainDir = Path(mainDir).resolve()
    gameDir = mainDir.parent
else:
    gameDir = Path(ENV.scriptHome).resolve()
    if (gameDir / f"{ENV.gameDir}_index.air").exists():
        mainDir = gameDir / f"{ENV.gameDir}_index.air"
    elif (gameDir / f"{ENV.gameDir}_index").exists():
        mainDir = gameDir / f"{ENV.gameDir}.air"
indexDir = mainDir

# 查找图片路径
add_image_basedir = lambda path: G.BASEDIR.append(path) if path not in G.BASEDIR else None
add_image_basedir(str(mainDir))

# 本地运行
localRun = ENV.launchType == "localtest"
# 预发环境
isPre = ENV.scriptEnv == 'pre' and not localRun
# 生产环境
isProd = ENV.scriptEnv == 'prod' and not localRun

# 脚本路径
launchGameDir = Path(ENV.scriptHome).resolve()
# 真实游戏目录
realGameDir = ENV.gameDir
# 任务类型
taskType = ENV.taskType
# 任务来源: 5-客服托管
taskSource = ENV.taskSource
# 任务ID
taskId = ENV.taskId
# 游戏ID
gameId = extract_digit(realGameDir)

# 普通发布和验证码发布
isFabu = taskType in (2, 20)
# 验号
isYanhao = taskType == 3
# 云游
isCloudGame = "common" in realGameDir and not localRun

# 游戏包名
if isCloudGame:
    packageName = ENV.get_common_property_with_key('jymPackageName')
    monitor_task_status_v2(f"云游采集包名", packageName)
elif localRun and os_env.get("packageName_test"):
    packageName = os_env.get("packageName_test")
    monitor_task_status_v2(f"本地测试包名", packageName)
elif packageName := os_env.get("packageName"):
    monitor_task_status_v2(f"智能采集包名", packageName)

# 游戏名
gameName = os_env.get("gameName") or os_env.get('game_name')
# 渠道
platform = ENV.get_common_property_with_key('gamePlatform') or realGameDir.split("_")[-1]
platform = os_env.get("platform_test") if localRun and os_env.get("platform_test") else platform

# 服务器
gameArea = ENV.game_area or "未知"

# 本地运行不保存时间戳图片
if localRun:
    ST.SAVE_IMAGE = False

# 本地识别属性数据
properties_path = str(gameDir / "properties_data")
for i in glob(OPJ(gameDir, "properties_data*")):
    if ".json" in i: continue
    os.remove(i)

# 屏幕信息
if isiOS:
    device_info = ENV.iOS_session_connect.device
    monitor_task_status_v2("MDS iOS Device 屏幕信息", device_info)
    os_version = device_info["os_version"]
    device_name = device_info["deviceModel"]["market_name"]
    screen_width = device_info["deviceModel"]["screen_width"]
    screen_height = device_info["deviceModel"]["screen_height"]
    desc = f"{device_name} - iOS {os_version} - resolution ({screen_width}x{screen_height})"
    monitor_task_status_v2("iOS device info", desc)
    display_info = {"width": screen_width, "height": screen_height}
else:
    if isAndroid:
        device_name = "Android 设备"
    elif isiOSCloud:
        device_name = "iOS 设备"
    else:
        device_name = ""
    display_info = DEV.display_info
    display_info.update(connected=DEV.uuid)
    monitor_task_status_v2(f"{device_name}信息".strip(), display_info)

"""
SCREENSIZE
仅作为坐标计算使用, 由环境变量 screenRotation 或 screenOrientation 决定
获取当前分辨率 请使用 get_resolution() 或 ScreenDynamic.SCREENSIZE() 方法
"""

__width = display_info['width']
__height = display_info['height']
__orientation = os_env.get("screenRotation", "").lower() or \
            os_env.get("screenOrientation", "").lower()
if isAndroid:
    SCREENSIZE = (__width, __height)
    if __orientation.startswith("v") or \
        __orientation == "portrait":
        SCREENSIZE = (__height, __width)
else:
    SCREENSIZE = (__width, __height)
    if __orientation.startswith("h") or \
        __orientation == "landscape":
        SCREENSIZE = (__height, __width)

SCREEN_WIDTH = SCREENSIZE[0]
SCREEN_HEIGHT = SCREENSIZE[1]
os_env.update(screenWidth=str(SCREEN_WIDTH), screenHeight=str(SCREEN_HEIGHT))
# 屏幕中心SCREENCENTER, 原SCREENHALF废弃
SCREENCENTER = SCREENHALF = int(SCREENSIZE[0] / 2), int(SCREENSIZE[1] / 2)
# 屏幕边界
SCREENBOX = (0, 0), SCREENSIZE
# 长截图长度限制
LIMITPIXEL = 12000

# 屏幕区域
area_lt = (*SCREENBOX[0], *SCREENCENTER)
area_rt = (SCREENCENTER[0], 0, SCREEN_WIDTH, SCREENCENTER[1])
area_rb = (*SCREENCENTER, *SCREENSIZE)
area_lb = (0, SCREENCENTER[1], SCREENCENTER[0], SCREEN_HEIGHT)
area_top = (0, 0, SCREEN_WIDTH, SCREENCENTER[1])
area_bottom = (0, SCREENCENTER[1], SCREEN_WIDTH, SCREEN_HEIGHT)
area_left = (0, 0, SCREENCENTER[0], SCREEN_HEIGHT)
area_right = (SCREENCENTER[0], 0, SCREEN_WIDTH, SCREEN_HEIGHT)

# 开始时间
__bizStartTime = time.time()

class ScreenDynamic:
    """
    屏幕区域
    支持动态获取屏幕尺寸
    不创建实例, 直接使用类方法
    """
    @classmethod
    def __get_screen_resolution(cls):
        """获取屏幕分辨率"""
        cls.__screen_size = DEV.get_current_resolution()
        cls.__screen_width = cls.__screen_size[0]
        cls.__screen_height = cls.__screen_size[1]
        cls.__screen_width_half = int(cls.__screen_width / 2)
        cls.__screen_height_half = int(cls.__screen_height / 2)
        cls.__screen_box = (0, 0), cls.__screen_size
        cls.__screen_center = cls.__screen_width_half, cls.__screen_height_half

    @classmethod
    def SCREENSIZE(cls):
        """屏幕分辨率"""
        cls.__get_screen_resolution()
        return cls.__screen_size

    @classmethod
    def SCREENBOX(cls):
        """全屏幕区域"""
        cls.__get_screen_resolution()
        return cls.__screen_box

    @classmethod
    def SCREENCENTER(cls):
        """屏幕中心"""
        cls.__get_screen_resolution()
        return cls.__screen_center

    @classmethod
    def SCREEN_WIDTH(cls):
        """屏幕宽度"""
        cls.__get_screen_resolution()
        return cls.__screen_width

    @classmethod
    def SCREEN_HEIGHT(cls):
        """屏幕高度"""
        cls.__get_screen_resolution()
        return cls.__screen_height

    @classmethod
    def SCREEN_WIDTH_HALF(cls):
        """屏幕宽度一半"""
        cls.__get_screen_resolution()
        return cls.__screen_width_half

    @classmethod
    def SCREEN_HEIGHT_HALF(cls):
        """屏幕高度一半"""
        cls.__get_screen_resolution()
        return cls.__screen_height_half

    @classmethod
    def area_lt(cls):
        """左上区域"""
        cls.__get_screen_resolution()
        lt = (*cls.__screen_box[0], *cls.__screen_center)
        return lt

    @classmethod
    def area_rt(cls):
        """右上区域"""
        cls.__get_screen_resolution()
        rt = (cls.__screen_center[0], 0, cls.__screen_width, cls.__screen_center[1])
        return rt

    @classmethod
    def area_rb(cls):
        """右下区域"""
        cls.__get_screen_resolution()
        rb = (*cls.__screen_center, *cls.__screen_size)
        return rb

    @classmethod
    def area_lb(cls):
        """左下区域"""
        cls.__get_screen_resolution()
        lb = (0, cls.__screen_center[1], cls.__screen_center[0], cls.__screen_height)
        return lb

    @classmethod
    def area_top(cls):
        """上半区域"""
        cls.__get_screen_resolution()
        top = (0, 0, cls.__screen_width, cls.__screen_center[1])
        return top

    @classmethod
    def area_bottom(cls):
        """下半区域"""
        cls.__get_screen_resolution()
        bottom = (0, cls.__screen_center[1], cls.__screen_width, cls.__screen_height)
        return bottom

    @classmethod
    def area_left(cls):
        """左半区域"""
        cls.__get_screen_resolution()
        left = (0, 0, cls.__screen_center[0], cls.__screen_height)
        return left

    @classmethod
    def area_right(cls):
        """右半区域"""
        cls.__get_screen_resolution()
        right = (cls.__screen_center[0], 0, cls.__screen_width, cls.__screen_center[1])
        return right

# 当前DPI
def current_dpi():
    if dpi := re.search(r"Override density: (\d+)", shell("wm density")):
        return int(dpi.group(1))
dpi_eq_450 = lambda: current_dpi() == 450

# 当前屏幕方向
screen_isportrait = screen_vertical = lambda: DEV.display_info["orientation"] in (1, 3, "PORTRAIT")
screen_islandscape = lambda: not screen_isportrait()
# 获取当前分辨率
get_resolution = lambda: DEV.get_current_resolution()
# 获取当前屏幕中心点坐标
def get_screen_center():
    __screen_size = get_resolution()
    return int(__screen_size[0] / 2), int(__screen_size[1] / 2)
screen_half = get_screen_center

def pos_conver(pos, mode=None):
    """坐标转换"""
    resolution = get_resolution()
    # 转绝对位置
    if mode == "abs":
        return int(pos[0] * resolution[0]), int(pos[1] * resolution[1])
    # 转相对位置
    elif mode == "rel":
        return pos[0] / resolution[0], pos[1] / resolution[1]
    # 转绝对位置-自适应
    elif isinstance(pos[0], float) and isinstance(pos[1], float) and \
        0 < pos[0] <= 1 and 0 < pos[1] <= 1:
        return int(pos[0] * resolution[0]), int(pos[1] * resolution[1])
    # 转相对位置-自适应
    else:
        return pos[0] / resolution[0], pos[1] / resolution[1]

def launchPoco():
    """
    启动POCO
    :return: poco object
    """
    Poco = None
    if isAndroid:
        from poco.drivers.android.uiautomation import AndroidUiautomationPoco as Poco

        if "com.netease.open.pocoservice" in shell("pm list package -d"):
            shell("pm enable com.netease.open.pocoservice")
            monitor_task_status_v2("启用POCOService")

    elif isiOSCloud:
        from poco.drivers.ios import iosPoco as Poco

    if Poco is not None:
        t0 = time.time()
        try:
            poco_instance = Poco(
                use_airtest_input=os_env.get("poco_use_airtest"),
                screenshot_each_action=False)
            monitor_task_status_v2(f"POCO启动成功", f"time: {time.time() - t0:.2f}s")
            poco_instance()
            return poco_instance
        except Exception:
            monitor_task_status_v2(f"POCO启动失败", traceback.format_exc())

poco = launchPoco() if os_env.get("poco_enable") and (isAndroid or isiOSCloud) else None

def activitiesApps(is_front=True):
    """
    正在活动app
    :return: applist
    """
    try:
        # 前台活动
        if is_front:
            activitiesComponent = shell("dumpsys window | grep mCurrentFocus")
            appslist = re.findall(r"mCurrentFocus.*u0\s(.*?)/", activitiesComponent)

        # 全部活动
        else:
            activitiesComponent = shell("dumpsys activity top | grep ACTIVITY")
            appslist = re.findall(r"ACTIVITY\s(.*?)/", activitiesComponent)

    except Exception as e:
        monitor_print(f"---activitiesAppsError: {e}")
        return
    return appslist

def all_activities_running(packageName, catch=True):
    """全部活动"""
    activitiesAppsList = activitiesApps(is_front=False)
    if activitiesAppsList is None or not len(activitiesAppsList): return -1

    if activitiesAppsList[-1] == packageName:
        monitor_catch(f"应用正在运行", format_print(activitiesAppsList[-1:]), catch=catch)
        return 1

    elif activitiesAppsList[-1] in ["com.android.launcher3", "com.teslacoilsw.launcher", "com.alibaba.cgs"]:
        monitor_catch("当前在桌面", format_print(activitiesAppsList))

    elif packageName in activitiesAppsList:
        monitor_catch("应用正在后台运行", format_print(activitiesAppsList))
        return 1

    else:
        monitor_catch(f"应用未在运行", format_print(activitiesAppsList))
        return 1

def kill_all_activities(closeVpn=True):
    """关闭全部活动"""
    exclude = [
        "com.teslacoilsw.launcher",
        "com.android.launcher3",
        "com.alibaba.cgs",
        "com.jym.x.engine.app",
        "com.alibaba.android.security.activity",
    ]
    activitiesAppsList = list(filter(lambda x: x not in exclude, activitiesApps(is_front=False) or []))
    for activityApp in activitiesAppsList:
        stop_app(activityApp)
    if activitiesAppsList:
        monitor_task_status_v2("已关闭以下应用", format_print(activitiesAppsList))
    if closeVpn and not os_env.get("closedVpn"):
        try:
            shell('am start-foreground-service -a "stop" -n com.jym.x.engine.app/com.ssrlive.socksdroid.VpnStarterService')
            monitor_task_status_v2("关闭VPN", "已关闭")
        except Exception as e:
            monitor_task_status_v2("关闭VPN", e)
        os_env.update(closedVpn="true")

activityApps = activitiesApps
all_activity_running = all_activities_running
kill_all_activity = kill_all_activities

def fix_black_edge(packageName=None):
    """
    修复设备黑边, 启动游戏后使用
    :param packageName: 包名(可选)
    """
    if not packageName:
        if activitiesAppsList := activitiesApps():
            packageName = activitiesAppsList[-1]

    has_black_edge = False
    for i in range(5):
        image = snapshot_write()
        size = image_size(image)
        if size[0] > size[1]:
            color: Dict = snapshot_color(area=(120, 1130, 1200, 1300), desc="黑边检测1", image=image)
            color: Dict = snapshot_color(area=(1980, 50, 2350, 1080), desc="黑边检测2", image=image)
            if color["b"] == 0 and color["b"] == 0:
                if i == 0:
                    monitor_catch("修复设备黑边", "开始修复")
                    has_black_edge = True
                start_app("com.android.settings")
                sleep(1)
                switch_screen_portrait()
                sleep(1)
                switch_screen_landscape()
                sleep(1)
                start_app(packageName)
                sleep(1)
                if not all_activities_running(packageName, False):
                    start_app(packageName)
            else:
                if has_black_edge:
                    monitor_catch("修复设备黑边", "修复完成")
                break
        else:
            monitor_task_status_v2("修复设备黑边", "暂不支持竖屏")
            break

def launchGame(gameName: str=gameName, packageName: str=packageName, sec=8, printLog=True, catch=True):
    """
    启动应用/游戏
    :param gameName: 应用/游戏名称
    :param packageName: 包名
    :param sec: 启动后等待
    :param printLog: 打印日志
    :param catch: 启动后留图
    :return:
    """
    if printLog:
        if packageName in gameName:
            monitor_task_status_v2("启动应用", gameName)
        else:
            monitor_task_status_v2("启动应用", f"{gameName} ({platform}) [{packageName}]")

    # Android
    if isAndroid:
        if packageName in shell("pm list package -d"):
            shell(f"pm enable \"{packageName}\"")
            monitor_task_status_v2("启用应用", packageName)

        for _ in range(5):
            # 检查应用是否在运行
            if localRun:
                if activitiesAppsList := activitiesApps():
                    if packageName == activitiesAppsList[-1]:
                        monitor_catch(f"应用正在运行，无需启动", format_print(activitiesAppsList), catch=catch)
                        break

            start_app(packageName)
            # 启动后等待
            if isinstance(sec, (int, float)) and sec > 0:
                sleep(sec)
            else:
                sleep(2.5)

            if all_activities_running(packageName, catch):
                if platform != "vivo" and gameId in [
                    "8788",
                    "15574",
                    "6586",
                    "10025",
                    "2717",
                    "25115",
                    "2480",
                    "23399"
                ]:
                    fix_black_edge(packageName)
                break

    # iOS
    elif isiOS:
        ex = None
        ex_traceback = ""
        for _ in range(6):
            try:
                start_result = ENV.iOS_session_connect.open_app(pkg=packageName)
                monitor_print(f"启动应用结果: {start_result}")
                if start_result:
                    break
                else:
                    sleep(15)
                    continue
            except Exception as e:
                ex_traceback = traceback.format_exc()
                ex = e
        else:
            monitor_task_status_v2("启动应用失败", ex_traceback)
            raise ex
        # 启动后等待
        if isinstance(sec, (int, float)) and sec > 0:
            sleep(sec)

    # iOSCloud
    elif isiOSCloud:
        start_app(packageName)
        # 启动后等待
        if isinstance(sec, (int, float)) and sec > 0:
            sleep(sec)

def closeGame(gameName: str=gameName, packageName: str=packageName, closeVpn=True):
    """
    关闭应用/游戏
    :param gameName: 应用/游戏名称
    :param packageName: 包名
    :param closeVpn: 关闭VPN
    :return: 无
    """
    if packageName in gameName:
        monitor_task_status_v2("关闭应用", gameName)
    else:
        monitor_task_status_v2("关闭应用", f"{gameName} ({platform}) [{packageName}]")

    # Android
    if isAndroid:
        if activitiesAppsList := activitiesApps(is_front=False):
            monitor_catch("关闭应用前正在运行", format_print(activitiesAppsList))
        stop_app(packageName)

        if closeVpn and not os_env.get("closedVpn"):
            try:
                shell('am start-foreground-service -a "stop" -n com.jym.x.engine.app/com.ssrlive.socksdroid.VpnStarterService')
                monitor_task_status_v2("关闭VPN", "已关闭")
            except Exception as e:
                monitor_task_status_v2("关闭VPN", e)
            os_env.update(closedVpn="true")

        if activitiesAppsList := activitiesApps(is_front=False):
            monitor_task_status_v2("关闭应用后正在运行", format_print(activitiesAppsList))

    # iOS
    elif isiOS:
        ex = None
        ex_traceback = ""
        for _ in range(3):
            try:
                ENV.iOS_session_connect.close_app(pkg=packageName)
                break
            except Exception as e:
                ex_traceback = traceback.format_exc()
                ex = e
        else:
            monitor_task_status_v2("关闭应用失败", ex_traceback)
            raise ex

    # iOSCloud
    elif isiOSCloud:
        stop_app(packageName)

    sleep(1)

def restartGame(gameName: str=gameName, packageName: str=packageName, sec=8):
    """
    重启应用/游戏
    :param gameName: 游戏名称
    :param packageName: 包名
    :param sec: 启动后等待
    :return: 无
    """
    if packageName in gameName:
        monitor_task_status_v2("重启应用", gameName)
    else:
        monitor_task_status_v2("重启应用", f"{gameName} ({platform}) [{packageName}]")

    # Android
    if isAndroid:
        if activitiesAppsList := activitiesApps(is_front=False):
            monitor_catch("重启应用前正在运行", format_print(activitiesAppsList))
        stop_app(packageName)
        sleep(1)
        for _ in range(5):
            start_app(packageName)
            # 启动后等待
            if isinstance(sec, (int, float)) and sec > 0:
                sleep(sec)
            else:
                sleep(2.3)

            if all_activities_running(packageName):
                break

    # iOS
    elif isiOS:
        ex = None
        ex_traceback = ""
        for _ in range(6):
            try:
                ENV.iOS_session_connect.close_app(pkg=packageName)
                sleep(1)
                start_result = ENV.iOS_session_connect.open_app(pkg=packageName)
                monitor_print(f"启动应用结果: {start_result}")
                if start_result:
                    break
                else:
                    sleep(15)
                    continue
            except Exception as e:
                ex_traceback = traceback.format_exc()
                ex = e
        else:
            monitor_task_status_v2("启动应用失败", ex_traceback)
            raise ex
        # 启动后等待
        if isinstance(sec, (int, float)) and sec > 0:
            sleep(sec)

    # iOSCloud
    elif isiOSCloud:
        stop_app(packageName)
        sleep(1)
        start_app(packageName)

        # 启动后等待
        if isinstance(sec, (int, float)) and sec > 0:
            sleep(sec)

def screen_rotation_diff(image=None):
    """
    屏幕方向和预设旋转方向有差异返回True
    """
    if isAndroid or isiOSCloud:
        monitor_task_status_v2("screen orientation", str(DEV.display_info["orientation"]))
        if (__orientation.startswith("v") or __orientation == "portrait") and screen_islandscape():
            return True
        elif (__orientation.startswith("h") or __orientation == "landscape") and screen_isportrait():
            return True
        else:
            return False

    elif isiOS:
        if not isinstance(image, np.ndarray):
            image = snapshot_write()
        if image_size(image) != SCREENSIZE:
            return True
        else:
            return False

def switch_screen_portrait(packageName=None):
    """
    切换竖屏
    :param packageName: 包名
    :return: 无
    """
    if packageName:
        keyevent("HOME")
        sleep(1)

    for _ in range(3):
        DEV.shell("settings put system accelerometer_rotation 0")
        DEV.shell("settings put system user_rotation 1")
        DEV.shell("settings put system accelerometer_rotation 1")
        sleep(1)
        if screen_isportrait():
            monitor_task_status_v2("旋转屏幕", "切换竖屏成功")
            break
    else:
        monitor_task_status_v2("旋转屏幕", "切换竖屏失败")
    if packageName:
        start_app(packageName)
        sleep(0.5)
switch_screen_vertical = switch_screen_portrait

def switch_screen_landscape(packageName=None):
    """
    切换横屏
    :param packageName: 包名
    :return: 无
    """
    if packageName:
        keyevent("HOME")
        sleep(1)

    for _ in range(3):
        DEV.shell("settings put system accelerometer_rotation 0")
        DEV.shell("settings put system user_rotation 0")
        DEV.shell("settings put system accelerometer_rotation 1")
        sleep(1)
        if not screen_isportrait():
            monitor_task_status_v2("旋转屏幕", "切换横屏成功")
            break
    else:
        monitor_task_status_v2("旋转屏幕", "切换横屏失败")
    if packageName:
        start_app(packageName)
        sleep(1)
switch_screen_horizontal = switch_screen_landscape

def switch_screen_rotation(packageName=None):
    """
    自适应切换横竖屏
    :param packageName: 包名
    """
    if os_env.get("screenRotation", "").lower().startswith("v") and not screen_isportrait():
        switch_screen_vertical(packageName)
    elif os_env.get("screenRotation", "").lower().startswith("h") and screen_isportrait():
        switch_screen_horizontal(packageName)

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

def check_username(username, phone_number=True):
    """
    校验账号
    :param username: 用户名
    :param phone_number: 手机号
    :return: 通过校验的用户名
    """
    username_strip = username.strip()
    if username_strip != username: monitor_task_status_v2("登录阶段", f"账号前后包含空格，已处理")

    if phone_number and not is_valid_phone_number(username_strip):
        monitor_task_status_v2("登录阶段", "账号格式错误", 10008)
        lx_break_app(ext_info={'key': '10008'}, desc='账号非手机号', hold_game=False)

    if tool_contains_chinese(username_strip):
        monitor_task_status_v2("登录阶段", "账号格式错误", 10008)
        lx_break_app(ext_info={'key': '10008'}, desc='账号包含中文', hold_game=False)

    elif len(username_strip) == 0:
        monitor_task_status_v2("登录阶段", "账号格式错误", 10008)
        lx_break_app(ext_info={'key': '10008'}, desc='账号为空', hold_game=False)

    return username_strip

def check_password(password):
    """
    校验密码
    :param password: 密码
    :return: 通过校验的密码
    """
    if tool_contains_chinese(password):
        monitor_task_status_v2("登录阶段", "密码格式错误", 10008)
        lx_break_app(ext_info={'key': '10008'}, desc='密码包含中文', hold_game=False)

    elif len(password) == 0:
        monitor_task_status_v2("登录阶段", "密码格式错误", 10008)
        lx_break_app(ext_info={'key': '10008'}, desc='密码为空', hold_game=False)

    return password

def check_smsCode(smsCode):
    """
    校验验证码
    :param smsCode: 短信验证码
    :return: 通过验证的短信验证码
    """
    if not smsCode.isdigit():
        monitor_task_status_v2("登录阶段", "验证码校验失败", 10007)
        lx_break_app(ext_info={'key': '10007'}, desc='验证码非数字', hold_game=False)

    return smsCode

def image_save_to_path(save_path, image, desc=""):
    """
    将图片保存到指定路径
    :param save_path: 写入路径
    :param image: 一张图片
    :param desc: 描述
    :return: image path
    """
    desc = f"[{desc}] " if desc else ""
    save_path_px = Path(save_path).resolve()

    # 校验扩展名
    ext = save_path_px.suffix
    if not ext:
        monitor_print(f"---imageSaveFailed: {desc}save_path_not_contains_ext ({save_path})")
        return ""

    # 校验目录
    image_path = save_path_px.parent
    if not str(image_path).startswith(str(logDir)):
        monitor_print(f"---imageSaveFailed: {desc}save_path_not_in_logDir ({save_path})")
        return ""

    # 校验图片
    if isinstance(image, np.ndarray):
        if not image.size > 0:
            monitor_print(f"---imageSaveFailed: {desc}image_is_empty {image_size(image)} ({save_path}) ")
            return ""
    else:
        monitor_print(f"---imageSaveFailed: {desc}image_is_not_nparray_type")
        return ""

    # 创建目录
    for _ in range(10):
        if image_path.is_dir():
            break
        else:
            image_path.mkdir(parents=True)
    else:
        monitor_print(f"---imageSaveFailed: {desc}create_failed {image_path}")
        return ""

    # 保存图片
    for _ in range(10):
        cv2.imwrite(str(save_path_px), image)
        if save_path_px.is_file():
            if desc:
                monitor_print(f"---imageSaveComplete: {desc}{save_path_px}")
            return str(save_path_px)
    else:
        monitor_print(f"---imageSaveFailed: {desc}{save_path}")
        return ""

def image_upload(write_name="image", image: np.ndarray=None, LT: Union[Tuple, List]=None, RB: Union[Tuple, List]=None, local_save=False):
    """
    上传图片对象
    :param write_name: 写入名称
    :param image: 图片对象
    :param LT: 左上裁剪
    :param RB: 右下裁剪
    :param local_save: 本地测试时不上传oss
    :return: [0]：不含http；[1]：含http
    """
    filepath = ""
    if isinstance(image, np.ndarray):
        path, name, ext = SnapshotFunctionGroup.filename_split(write_name)
        name = f"upload_{name}_{timeStamp()}"
        filepath = SnapshotFunctionGroup.join_path(path, name, ext)
        image = EditImage(image)(LT, RB)
        image_save_to_path(filepath, image, desc="IMGUP")
    else:
        lx_break_runloop(desc="image upload empty")

    for i in range(3):
        try:
            if not (local_save and localRun):
                oss_pathes, cdn_url_list = upload_jym_oss_with_pathes([filepath])
                return oss_pathes[0], cdn_url_list[0]
            else:
                return filepath, filepath
        except Exception:
            if i == 2:
                monitor_task_status_v2("Image upload failed", f"{traceback.format_exc()} - {write_name}", status=10011)
                lx_break_runloop(desc="Image upload failed")
            else:
                sleep(2)

def image_path_upload(image_path="", local_save=False):
    """
    上传图片路径
    :param image_path: 图片全路径或LOG_DIR中图片文件名
    :param local_save: 本地测试时不上传oss
    :return: [0]：不含http；[1]：含http
    """
    if image_path and isinstance(image_path, str):
        # 分割目录和文件名.扩展名
        file_dir, file_name_ext = OP.split(image_path)
        file_dir = file_dir or ST.LOG_DIR
        # 分割文件名和扩展名
        file_name, ext = OP.splitext(file_name_ext)
        ext = ext or ".jpg"

        image_path = f"{OPJ(file_dir, file_name)}{ext}"
        timeStamp_pattern = re.compile(r"\d{16}")
        for _ in range(2):
            # 文件存在
            if OP.isfile(image_path):
                # 添加时间戳
                if not timeStamp_pattern.match(file_name.split("_")[-1]):
                    file_name = f"upload_{file_name}_{timeStamp()}"
                    image_path_new = f"{OPJ(file_dir, file_name)}{ext}"
                    # 文件重命名
                    os.rename(image_path, image_path_new)
                    image_path = image_path_new
            else:
                monitor_print(f"---image_path_upload: image_path_not_exists ({image_path}) ")
                return "", ""
        else:
            for i in range(3):
                try:
                    if local_save and localRun:
                        return image_path, image_path
                    else:
                        oss_pathes, cdn_url_list = upload_jym_oss_with_pathes([image_path])
                        return oss_pathes[0], cdn_url_list[0]
                except Exception:
                    if i == 2:
                        monitor_task_status_v2("Image upload failed", f"{traceback.format_exc()} - {image_path}")
                    else:
                        sleep(3)
    else:
        return "", ""

class CaptchaType(Enum):
    SLIDER_SINGLE_IMAGE = "验证码"
    SLIDER_MULTI_PIECE_PUZZLE = "多拼图验证码"

class SwipeCode:
    def __init__(self, **kwds):
        """
        滑动验证码
        :param kwds: 不定长参数
        """
        self.IDENTIFY = kwds.get("IDENTIFY")          # 滑动验证码标识
        self.REFRESH = kwds.get("REFRESH")            # 刷新按钮
        self.NOT_REFRESH = kwds.get("NOT_REFRESH")    # 每次循环不要刷新
        self.START_POINT = kwds.get("START_POINT")    # 开始滑动接触点
        self.VER_LT = kwds.get("VER_LT")              # 验证码图片区域左上
        self.VER_RB = kwds.get("VER_RB")              # 验证码图片区域右下
        self.SLIDE_OFFSET = kwds.get("SLIDE_OFFSET")  # 偏移量
        self.RAISE_EXCEPTION = kwds.get("RAISE_EXCEPTION", True)  # 抛异常
        self.CAPTCHA_TYPE = kwds.get("CAPTCHA", CaptchaType.SLIDER_SINGLE_IMAGE.value) #

    def __call__(self):
        # 0表示未遇到风控；1表示风控通过；2表示风控未通过
        risk_control_status = 0
        count = 0
        monitor_task_status_v2("风控检测", f"开始检测")
        for i in range(15):
            if START_POINT := air_exists(self.IDENTIFY, timeout=1):
                if self.START_POINT: START_POINT = self.START_POINT
                # 识别到风控，需要处理
                risk_control_status = 2
                monitor_task_status_v2("风控检测", f"触发风控, 尝试次数{i + 1}")
                # 刷新
                if i > 0 and self.REFRESH and not self.NOT_REFRESH:
                    air_exists_touch(self.REFRESH, sec=3)
                # filename1 = f"adc_upload_snap_risk_control.jpg"
                filename2 = f"adc_upload_snap_risk_control_cropped_{timeStamp()}.jpg"
                # crop_pos_image_from_snapshot(filename1, filename2, self.VER_LT, self.VER_RB)
                snapshot_write(filename2, self.VER_LT, self.VER_RB)
                risk_crop_path = OPJ(ST.LOG_DIR, filename2)
                localFileList = [risk_crop_path]
                _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
                if cdn_url_list: risk_control_url = cdn_url_list[0]
                else: break
                data = easRequest(self.get_env_path(), self.getRequestDataWithURL(risk_control_url, property_id=self.CAPTCHA_TYPE))
                monitor_print(f'---processing_risk_control:{risk_control_url} result:{data}')
                match_point = self.getEasCommonResult(data)
                # 滑动距离为零，刷新
                if not match_point[0] and self.REFRESH: air_exists_touch(self.REFRESH, sec=3); continue
                finalEndPoint = (START_POINT[0] + self.SLIDE_OFFSET + match_point[0], START_POINT[1])
                adc_swipe(START_POINT, finalEndPoint, sec=1)
                count += 1
            else:
                risk_control_status = 1
                break
        if risk_control_status == 1 and count:
            monitor_task_status_v2("风控检测", "风控通过")
            return True
        elif risk_control_status == 2:
            if self.RAISE_EXCEPTION:
                monitor_catch("风控检测", "风控未通过", status=10102, break_mode=BreakModeEnum.runloop)
            else:
                monitor_catch("风控检测", "风控未通过")
            return False
        else:
            monitor_task_status_v2("风控检测", "无风控")
            return True

    def get_env_path(self):
        scriptEnv = ENV.scriptEnv
        monitor_print(f"scriptEnv: {scriptEnv}")
        if scriptEnv in ['local', 'daily', 'pre']:
            return '/api/predict/lingxialgo_adc_ocr_pre'
        else:
            return '/api/predict/lingxialgo_vision_adc'

    def getRequestDataWithURL(self, url, property_id):
        resData = {
            'imageProperties': [{"propertyId": property_id}],
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

def combine_images_write(
        write_name="",
        images=None,
        mask=None,
        area=None,
        cols=1,
        rows=99,
        spacing=0,
        spacing_x=0,
        spacing_y=0,
        spacing_color=(255, 255, 255),
        border=None,
        sn=None):
    """
    合并保存截图
    :param write_name: 写入名称
    :param images: 一组图片np.array或完整路径
    :param mask: 为每张图片同一位置打码
    :param area: 裁剪区域
    :param cols: 列数
    :param rows: 行数
    :param spacing: 全局间距
    :param spacing_x: 内横间距
    :param spacing_y: 内纵间距
    :param spacing_color: 间距背景颜色
    :param border: 外边框TRBL
    :param sn: 序号
    :return: 合并后的一组图片
    """
    if isinstance(images, (np.ndarray, str)):
        images = [images]
    write_name = str(write_name)
    # 临时图片列表
    images_tmp = []
    # 合并图片结果
    combine_images_result = []
    for image in iter(images or []):
        if isinstance(image, np.ndarray):
            images_tmp.append(image)
        elif OP.isfile(str(image)):
            images_tmp.append(cv2.imread(str(image)))

    if images_tmp:
        # 补全截图
        # fill_image_path = OPJ(mainDir, "fill_image.jpg")
        # if OP.isfile(fill_image_path):
        #     fill_image = cv2.imread(fill_image_path)
        #     lenth = len(images)
        #     diff = math.ceil(lenth / cols) * cols - lenth
        #     fill_image_list = [fill_image for _ in range(diff)]
        # else:
        #     fill_image_list = []

        # 图片打码
        if mask:
            for i in range(len(images_tmp)):
                images_tmp[i] = EditImage(images_tmp[i]).mask(mask)

        # 图片裁剪
        if area:
            for i in range(len(images_tmp)):
                images_tmp[i] = EditImage(images_tmp[i]).crop(area[:2], area[2:])

        # 合并截图
        combine_images_result.extend(combine_images_base(
            images_tmp,
            one_row_count=cols,
            max_rows_count=rows,
            spacing=spacing,
            spacing_x=spacing_x,
            spacing_y=spacing_y,
            spacing_color=spacing_color
        ))

        # 添加边框
        if border:
            combine_images_result = list(map(lambda image: image_extend(image, border, spacing_color), combine_images_result))

        # 保存合并后图片
        if write_name:
            images_batch_write(write_name, combine_images_result, sn=sn)
    else:
        monitor_task_status_v2("Combine images", f"{write_name.split('_')[-1] if write_name else ''} Images empty")

    return combine_images_result

def images_batch_write(write_name, images, sn=None):
    """
    图片批量保存
    :param write_name: 写入名称
    :param images: 一组图片
    :param sn: 序号
    :return: 无
    """
    write_path, write_name, ext = SnapshotFunctionGroup.filename_split(write_name)
    images_paths = []
    if isinstance(images, (np.ndarray, str)):
        images = [images]
    for index, image in enumerate(images, 1):
        if write_name.startswith("$_"):
            # 以正式名称保存
            write_name_list = [
                f"adc_result_{write_name.strip('$_')}",
                str(index),
                f"${sn}" if isinstance(sn, int) else timeStamp()
            ]
        elif write_name.startswith("adc_catch"):
            write_name = re.sub(r"_\d{16}", "", write_name)
            write_name = re.sub(r"\.jpg|\.png", "", write_name)
            write_name_list = [
                write_name,
                str(index),
                timeStamp()
            ]
        else:
            write_name_list = [write_name, str(index)]

        images_paths.append(image_path := SnapshotFunctionGroup.join_path(write_path, "_".join(write_name_list), ext))
        if isinstance(image, np.ndarray):
            image_save_to_path(image_path, image, "IMGBW")
        elif OP.isfile(str(image)):
            shutil.copy2(image, image_path)

    return images_paths

def images_batch_read(images_path, glob_pattern):
    """
    图片批量读取
    :param images_path: 图片路径
    :param glob_pattern: 图片名称模式
    :return: images
    """
    images = []
    images_paths = Path(images_path).resolve().glob(glob_pattern)
    images_paths = sorted(map(str, images_paths), key=select_numbers)
    for image_path in images_paths:
        images.append(cv2.imread(str(image_path)))

    return images

def image_size(image):
    """
    图片尺寸
    :param image: 一张图片
    :return: 图片尺寸
    """
    image_shape = image.shape[:2]
    return image_shape[1], image_shape[0]

def image_extend(image, border, color=(255, 255, 255)):
    """
    扩图
    :param image: 一张图片
    :param border: 外边距
    :param color: 边距背景颜色
    :return:
    """
    top = bottom = left = right = 0
    if isinstance(border, int): top = bottom = left = right = border
    elif isinstance(border, Tuple):
        if len(border) == 1: top = bottom = left = right = border[0]
        elif len(border) == 2: top = bottom = border[0]; left = right = border[1]
        elif len(border) == 3: top = border[0]; left = right = border[1]; bottom = border[2]
        elif len(border) == 4: top = border[0]; right = border[1]; bottom = border[2]; left = border[3]

    if any((top, bottom, left, right)):
        border_color = color[2], color[1], color[0]
        image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=border_color)

    return image

def image_add_title(image, title_images, color=(255, 255, 255)):
    """
    添加标题
    :param image: 一张图片
    :param title_images: 标题图片
    :param color: 空白处背景颜色
    :return: 添加标题后的图片
    """
    def add_title(image, title_image):
        image_width = image_size(image)[0]
        title_image_width = image_size(title_image)[0]
        abs_diff = abs(image_width - title_image_width)
        if image_width > title_image_width:
            title_image = image_extend(title_image, (0, abs_diff, 0, 0), color)
        elif image_width < title_image_width:
            title_image = snapshot_write(TRBL=(0, abs_diff, 0, 0), image=title_image)
        return combine_images_write(images=[title_image, image])[0]

    if isinstance(title_images, np.ndarray):
        return add_title(image, title_images)
    else:
        for title_image in title_images[::-1]:
            image = add_title(image, title_image)
        else:
            return image

def gaussian_blur(image, p1, p2):
    """
    高斯模糊
    :param image:
    :param p1:
    :param p2:
    :return:
    """
    x1, y1 = p1; x2, y2 = p2
    # 从原始图像中裁剪出想要模糊的区域，对该区域应用高斯模糊
    blurred_roi = cv2.GaussianBlur(image[y1:y2, x1:x2], (99, 99), 0)
    # 将模糊后的区域替换回原始图像
    image[y1:y2, x1:x2] = blurred_roi
    return image

def add_alpha_channel(img):
    """
    为图像添加alpha通道
    :param img:
    :return:
    """
    b_channel, g_channel, r_channel = cv2.split(img)  # 剥离jpg图像通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255  # 创建Alpha通道
    img_new = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))  # 融合通道
    return img_new

def image_multiline_text(
        base_image,
        text,
        text_color="#fff",
        font_size=50,
        textPoint=(0, 0),
        text_bg_color=None,
        area_width=None,
        area_height=None,
        line_height=None,
        shadow=None,
        center_alignment=False,
        font_path=None):
    """
    多行文字
    :param base_image: 基础图片
    :param text: 文字
    :param text_color: 文字颜色
    :param font_size: 文字大小
    :param textPoint: 文字位置
    :param text_bg_color: 文字背景颜色
    :param area_width: 区域宽度
    :param area_height: 区域高度
    :param line_height: 行高
    :param shadow: 阴影
    :param center_alignment: 居中对齐
    :param font_path: 字体路径
    :return:
    """
    if not line_height or line_height < font_size:
        line_height = font_size + font_size * 0.25

    assert base_image is not None, "merge_text_in_image base_image is None"
    # 将图像转换为PIL格式
    base_image = base_image.copy()
    image_pil = Image.fromarray(cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB))
    # 创建绘图对象
    draw = ImageDraw.Draw(image_pil)

    if font_path and OP.isfile(font_path):
        ttf_path = font_path
    else:
        ttf_path = AppEnv.get_instance().rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'

    the_font_size = 60
    if font_size is not None:
        the_font_size = font_size
    font = ImageFont.truetype(ttf_path, size=the_font_size)

    size = image_size(base_image)
    area_width = area_width or int(size[0] * 0.95) - textPoint[0]
    area_height = area_height or size[1] - textPoint[1] - line_height

    text_list = []
    for text_item in str(text).split(r"\n"):
        text_temp_list = []
        for word in text_item:
            text_temp = "".join(text_temp_list)
            text_lenth = draw.textlength(text_temp, font=font)
            if text_lenth > area_width:
                text_list.append(text_temp.strip())
                text_temp_list.clear()
            text_temp_list.append(word)
        else:
            text_list.append("".join(text_temp_list).strip())

    text_list = list(filter(bool, text_list))
    poses = create_poses(textPoint, T2T=line_height, rows=len(text_list))
    loop_break = False
    for text_position, text_j in zip(poses, text_list):
        if center_alignment:
            text_lenth = draw.textlength(text_j, font=font)
            text_position = text_position[0] - int(text_lenth / 2), text_position[1]

        if text_bg_color:
            small_bg_image = Image.new('RGBA', (len(text_j) * the_font_size, line_height), color=text_bg_color)
            small_bg_draw = ImageDraw.Draw(small_bg_image)
            small_bg_draw.text((5, -5), text_j, font=font, fill=text_color)
            image_pil.paste(small_bg_image, text_position)

        if text_position[1] + the_font_size >= textPoint[1] + area_height:
            if draw.textlength(text_j, font=font) > area_width:
                text_j = text_j[:-1] + "..."
            loop_break = True

        if shadow:
            shadow = 1
            for x_offset, y_offset in itertools.product(range(-shadow, shadow + 1), range(-shadow, shadow + 1)):
                if x_offset == 0 and y_offset == 0:
                    continue
                draw.text((text_position[0] + x_offset, text_position[1] + y_offset), text_j, font=font, fill="#111")

        draw.text(text_position, text_j, font=font, fill=text_color)
        if loop_break:
            break

    # 将PIL图像转换回OpenCV格式
    base_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return base_image

def image_fill(image, pos, small_image):
    """
    填充图片
    :param image:
    :param pos:
    :param small_image:
    :return:
    """
    if isinstance(pos, (str, Enum)):
        pos = image_fill_pos(image, small_image, pos)

    # 确定小图片的宽度和高度
    small_width, small_height = image_size(small_image)
    # 确定大图片的宽度和高度
    big_width, big_height = image_size(image)

    if small_width > big_width or small_height > big_height:
        monitor_task_status_v2("填充图片", f"小图片尺寸超过大图片{small_width=}, {big_width=}, {small_height=}, {big_height=}")
        return image

    # 将小图片复制到大图片的指定位置
    image[pos[1]:pos[1] + small_height, pos[0]:pos[0] + small_width] = small_image
    return image

def image_fill_alpha(image, pos, small_image):
    """
    填充透明图片
    :param image:
    :param pos:
    :param small_image:
    :return:
    """
    if isinstance(pos, (str, Enum)):
        pos = image_fill_pos(image, small_image, pos)
    # 确定小图片的宽度和高度
    small_width, small_height = image_size(small_image)
    # 确定大图片的宽度和高度
    big_width, big_height = image_size(image)
    x1, x2 = pos[0], pos[0] + small_width
    y1, y2 = pos[1], pos[1] + small_height

    if small_width > big_width or small_height > big_height:
        monitor_task_status_v2("填充图片", f"小图片尺寸超过大图片{small_width=}, {big_width=}, {small_height=}, {big_height=}")
        return image

    # 判断jpg图像是否已经为4通道
    if image.shape[2] == 3:
        image = add_alpha_channel(image)

    # 获取要覆盖图像的alpha值，将像素值除以255，使值保持在0-1之间
    alpha_png = small_image[..., 3] / 255.0
    alpha_jpg = 1 - alpha_png

    # 开始叠加
    for c in range(0, 3):
        image[y1:y2, x1:x2, c] = (alpha_jpg * image[y1:y2, x1:x2, c]) + (alpha_png * small_image[..., c])

    return image

# 创建空白图片
def create_blank_image(width: int, height: int, color=(0, 0, 0)):
    """返回空白图片"""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:, :, :] = color[2], color[1], color[0]
    return image

class TargetPosEnum(Enum):
    center = "center"
    lt = "lt"
    rt = "rt"
    lb = "lb"
    rb = "rb"
    top = "top"
    left = "left"
    right = "right"
    bottom = "bottom"

def image_fill_pos(big_image: np.ndarray, small_image: np.ndarray, target_pos: Union[Enum, str]):
    """
    填充图片位置
    :param big_image:
    :param small_image:
    :param target_pos:
    :return: image
    """
    # 确定小图片的宽度和高度
    small_width, small_height = image_size(small_image)
    # 确定大图片的宽度和高度
    big_width, big_height = image_size(big_image)

    if small_width > big_width or small_height > big_height:
        monitor_task_status_v2("填充图片位置", f"小图片尺寸超过大图片{small_width=}, {big_width=}, {small_height=}, {big_height=}")
        return

    if isinstance(target_pos, Enum):
        target_pos = target_pos.value

    if target_pos == "center":
        pos = (big_width - small_width) // 2, (big_height - small_height) // 2
    elif target_pos == "lt":
        pos = 0, 0
    elif target_pos == "rt":
        pos = big_width - small_width, 0
    elif target_pos == "lb":
        pos = 0, big_height - small_height
    elif target_pos == "rb":
        pos = big_width - small_width, big_height - small_height
    elif target_pos == "top":
        pos = (big_width - small_width) // 2, 0
    elif target_pos == "left":
        pos = 0, (big_height - small_height) // 2
    elif target_pos == "right":
        pos = big_width - small_width, (big_height - small_height) // 2
    elif target_pos == "bottom":
        pos = (big_width - small_width) // 2, big_height - small_height
    else:
        pos = 0, 0

    return pos

def color_fill(image, pos, width, height, color):
    """
    填充颜色
    :param image:
    :param pos:
    :param width:
    :param height:
    :param color:
    :return:
    """
    # 确定大图片的宽度和高度
    big_width, big_height = image_size(image)
    if width > big_width or height > height:
        monitor_print("---颜色区域超过图片")
        return image

    color_image = np.zeros((height, width, 3), dtype=np.uint8)
    color_image[:] = color[2], color[1], color[0]
    image[pos[1]:pos[1] + height, pos[0]:pos[0] + width] = color_image
    return image

class EditImage:
    """
    编辑图片
    :param image:
    """
    def __init__(self, image):
        self.image = image.copy()
        self.operation_record = []

    def crop(self, LT, RB):
        """裁剪图片"""
        lt = LT or SCREENBOX[0]; rb = RB or SCREENBOX[1]
        if lt[0] > rb[0] or lt[1] > rb[1]:
            monitor_print(f"---image_crop_error: {lt=}, {rb=}")
        self.image = self.image[lt[1]:rb[1], lt[0]:rb[0]]
        return self.image

    def mask(self, boxes):
        """图片打码"""
        if len(boxes) == 4 and all(map(lambda x: isinstance(x, int), boxes)):
            p1, p2 = (boxes[0], boxes[1]), (boxes[2], boxes[3])
            try: self.image = gaussian_blur(self.image, p1, p2)
            except Exception:...

        elif len(boxes) == 2 and all(map(lambda x: isinstance(x, int), boxes[0])) and all(map(lambda x: len(x) == 2, boxes)):
            p1, p2 = boxes[0], boxes[1]
            try: self.image = gaussian_blur(self.image, p1, p2)
            except Exception:...

        else:
            for box in boxes:
                if len(box) == 4 and all(map(lambda x: isinstance(x, int), box)):
                    p1, p2 = (box[0], box[1]), (box[2], box[3])
                    try: self.image = gaussian_blur(self.image, p1, p2)
                    except Exception:...

                elif len(box) == 2 and all(map(lambda x: isinstance(x, int), box[0])) and all(map(lambda x: len(x) == 2, box)):
                    p1, p2 = box[0], box[1]
                    try: self.image = gaussian_blur(self.image, p1, p2)
                    except Exception:...

        return self.image

    def images_fill(self, value):
        """填充图片"""
        if isinstance(value[0], (Iterable, Enum)):
            if isinstance(value[0], Enum):
                self.image = image_fill(self.image, *value)
            # 多图 ((pos1, image1), (pos2, image1),...)
            elif isinstance(value[0][0], (List, Tuple, Enum)):
                for pos, small_image in value:
                    try: self.image = image_fill(self.image, pos, small_image)
                    except Exception:...
            # 单图 (pos, image)
            else:
                self.image = image_fill(self.image, *value)
        else:
            monitor_print("---obj_isnot_Iterable")
        return self.image

    def images_fill_alpha(self, value):
        """填充透明图片"""
        if isinstance(value[0], (Iterable, Enum)):
            if isinstance(value[0], Enum):
                self.image = image_fill_alpha(self.image, *value)
            # 多图 ((pos1, image1), (pos2, image1),...)
            elif isinstance(value[0][0], (List, Tuple, Enum)):
                for pos, small_image in value:
                    try: self.image = image_fill_alpha(self.image, pos, small_image)
                    except Exception:...
            # 单图 (pos, image)
            else:
                self.image = image_fill_alpha(self.image, *value)
        else:
            monitor_print("---obj_is_not_Iterable")
        return self.image

    def colors_fill(self, value):
        """填充颜色"""
        if isinstance(value[0], Iterable):
            # 多色 ((pos1, width1, height1, color1), (pos2, width2, height2, color1),...)
            if isinstance(value[0][0], Iterable):
                monitor_print(value)
                for pos, width, height, color in value:
                    try: self.image = color_fill(self.image, pos, width, height, color)
                    except Exception:...
            # 单色 (pos, width, height, color)
            else:
                self.image = color_fill(self.image, *value)
        else:
            monitor_print("---obj_is_not_Iterable")
        return self.image

    def alpha_beta(self, contrast=1, brightness=1):
        """亮度和对比度"""
        self.image = cv2.convertScaleAbs(self.image, alpha=contrast, beta=brightness)
        self.operation_record.append("alpha_beta")
        return self.image

    def gamma(self, value):
        """伽马"""
        self.image = np.power(self.image / 255, value) * 255
        return self.image

    def zoom(self, value):
        """等比缩放"""
        width, height = image_size(self.image)
        self.image = cv2.resize(self.image, (int(width * value), int(height * value)))
        return self.image

    def resize(self, value):
        """按宽高等比缩放"""
        """
        先根据宽来啊<等比>缩放，宽传了None，再根据高来等比缩放
        :param value:
        :return:
        """
        width, height = image_size(self.image)
        if new_width := value[0]:
            new_height = value[0] * height // width
        elif new_height := value[1]:
            new_width = value[1] * width // height
        if all((new_width, new_height)):
            self.image = cv2.resize(self.image, (new_width, new_height))
            return self.image

    def red2blue(self):
        """红蓝分量交换"""
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        return self.image

    def gray(self):
        """灰度"""
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return self.image

    def median_blur(self, value):
        """中值模糊"""
        self.image = cv2.medianBlur(self.image, value)
        return self.image

    def __call__(self, LT=None, RB=None, **kwds):
        if LT or RB: self.crop(LT, RB)
        for operation, value in kwds.items():
            if operation == "mask": self.mask(value)
            elif operation == "images_fill": self.images_fill(value)
            elif operation == "images_fill_alpha": self.images_fill_alpha(value)
            elif operation == "colors_fill": self.colors_fill(value)
            elif operation == "zoom": self.zoom(value)
            elif operation == "resize": self.resize(value)
            elif operation == "r2b": self.red2blue()
            elif operation == "gray": self.gray()
            elif operation == "blur": self.median_blur(value)
            elif operation == "gamma": self.gamma(value)
            elif operation == "contrast" and  "alpha_beta" not in self.operation_record:
                self.alpha_beta(value, kwds.get("brightness", 1))
            elif operation == "brightness" and  "alpha_beta" not in self.operation_record:
                self.alpha_beta(kwds.get("contrast", 1), value)
        else:
            return self.image

# 图片处理-转灰度
edit_image_gray = lambda image_: EditImage(image_)(r2b=True, gray=True)
# 图片处理-转灰度并扩大4倍
edit_image_gray_x4 = lambda image_: EditImage(image_)(zoom=4, r2b=True, gray=True)
# 图片处理-扩大4倍
edit_image_x4 = lambda image_: EditImage(image_)(zoom=4)

# 描述信息格式化
desc_format = lambda desc: f" | {desc}" if desc != "" and desc is not None else ""
desc_format2 = lambda desc: f"-{desc}" if desc != "" and desc is not None else ""

def get_current_screen():
    """
    获取当前屏幕
    :return: screen
    """
    global __bizStartTime
    for i in range(5):
        try:
            screen = DEV.snapshot()
            if screen is None or screen.size == 0:
                monitor_task_status_v2("截图失败", str(screen))
                if i == 2 and os_env.get("SCREEN_PROXY") != "JAVACAP":
                    DEV.screen_proxy = "JAVACAP"
                    os_env.update({"SCREEN_PROXY": "JAVACAP"})
                    monitor_task_status_v2("切换截图代理", "JAVACAP")

            else:
                resolution = get_resolution()
                if image_size(screen) != resolution:
                    screen = cv2.resize(screen, resolution)

                if ST.SAVE_IMAGE:
                    # 清理时间戳图片
                    currentTime = time.time()
                    if currentTime - __bizStartTime > 60 * 2:
                        clean_old_timestamp_files()
                        __bizStartTime = currentTime
                    filename_ = "%(time)d.jpg" % {'time': time.time() * 1000}
                else:
                    filename_ = "current_screen.jpg"
                filepath = str(logDir / filename_)
                image_save_to_path(filepath, screen)
                return screen

            sleep(2)
        except Exception:
            lx_safe_connect()
    else:
        monitor_catch("截图失败", status=10163, break_mode=BreakModeEnum.runloop, catch=False)

def screenshot(filename=None, hq_func=None):
    """
    获取屏幕截图
    :param filename: 文件名
    :param hq_func: 处理图像的方法
    :return:
    """
    image = None
    for _ in range(5):
        if isAndroid or isiOSCloud:
            image = get_current_screen()
        else:
            image = adc_snapshot(filename=None)

        if callable(hq_func):
            obj = hq_func(image)
            if isinstance(obj, np.ndarray):
                image = obj
                break
            elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
                if obj > 0: sleep(obj)
            elif obj:
                break
            else:
                sleep(2)
        else:
            break

    if filename:
        name, ext = OP.splitext(filename)
        if not ext: ext = ".jpg"
        if name.startswith("$_"):
            name = catch_name(name.strip("$_"))
        filename = filename_special_char_pattern.sub("", f"{name}") + ext

        filepath = str(logDir / filename)
        image_save_to_path(filepath, image, desc="SCREENSHOT")

    return image

class SnapshotFunctionGroup:
    """SNAPSHOT功能组"""
    def __init__(self, **kwds):
        # 图片保存名称（$_名称：保存为 adc_result）
        self.WRITE_NAME = kwds.get("write_name")
        # 图片全路径或 INDEX_DIR, LOG_DIR 中图片文件名
        self.READ_NAME = kwds.get("read_name")
        # 需要返回路径
        self.needPath = kwds.get("needPath")
        # 图片 numpy.array
        self.IMAGE = kwds.get("image")
        # 打码
        self.MASK = kwds.get("mask")
        # 左上/右下
        self.LT = kwds.get("LT")
        self.RB = kwds.get("RB")
        # 宽/高
        self.WIDTH = kwds.get("width")
        self.HEIGHT = kwds.get("height")
        # 边缘重置
        self.edge_reset = kwds.get("edge_reset")
        # 相对裁剪
        self.TRBL = kwds.get("TRBL")
        # 图片序列号
        self.SN = kwds.get("sn")
        # 描述信息
        self.DESC = desc_format(kwds.get('desc'))
        # 描述信息（原始）
        self.desc_original = kwds.get('desc')
        # 内部定义临时图片名称
        self.SNAPSHOT_NAME = kwds.get("snapshot_name")
        # 高品质回调函数
        self.HQ_FUNC = kwds.get("hq_func")
        self.full_write_path = ""
        self.kwds = kwds
        self.processing()

    def processing(self):
        if all((self.LT, self.RB)) and self.LT == self.RB:
            lx_break_runloop(desc=f"CROP LT=RB {self.RB}")

        # image未传入
        if not isinstance(self.IMAGE, np.ndarray):
            self.IMAGE = self.read_image(self.READ_NAME)

        # 图片尺寸
        if isinstance(self.IMAGE, np.ndarray):
            size = image_size(self.IMAGE)
        else:
            monitor_task_status_v2("图片错误", f"{self.READ_NAME}-{self.IMAGE}")
            size = (0, 0)

        # 使用宽高计算右下角
        if not self.RB and any((self.WIDTH, self.HEIGHT)):
            if not self.LT: self.LT = (0, 0)
            if self.WIDTH and self.WIDTH > size[0]: self.WIDTH = size[0]
            if self.HEIGHT and self.HEIGHT > size[1]: self.HEIGHT = size[1]
            self.RB = (
                self.LT[0] + (self.WIDTH or size[0]),
                self.LT[1] + (self.HEIGHT or size[1])
            )

        # 边缘重置
        if self.LT and self.edge_reset:
            lt = list(self.LT)
            if lt[0] < 0: lt[0] = 0
            if lt[1] < 0: lt[1] = 0
            if tuple(self.LT) != tuple(lt):
                monitor_task_status_v2("CROP边缘重置", f"超出边缘: LT={self.LT}, IMAGE_SIZE={size}")
                self.LT = tuple(lt)

        if self.RB and self.edge_reset:
            rb = list(self.RB)
            if rb[0] > size[0]: rb[0] = size[0]
            if rb[1] > size[1]: rb[1] = size[1]
            if tuple(self.RB) != tuple(rb):
                monitor_task_status_v2("CROP边缘重置", f"超出边缘: RB={self.RB}, IMAGE_SIZE={size}")
                self.RB = tuple(rb)

        # 图片打码
        if self.MASK:
            self.IMAGE = EditImage(self.IMAGE)(mask=self.MASK)

        # 图片裁剪
        if self.LT or self.RB:
            if self.IMAGE is None: return
            self.IMAGE = EditImage(self.IMAGE)(self.LT or SCREENBOX[0], self.RB or size)

        # 相对位置裁剪
        if isinstance(self.TRBL, int): self.IMAGE = EditImage(self.IMAGE)((self.TRBL, self.TRBL), (size[0] - self.TRBL, size[1] - self.TRBL))
        elif isinstance(self.TRBL, Tuple):
            if len(self.TRBL) == 1: self.IMAGE = EditImage(self.IMAGE)((self.TRBL[0], self.TRBL[0]), (size[0] - self.TRBL[0], size[1] - self.TRBL[0]))
            elif len(self.TRBL) == 2: self.IMAGE = EditImage(self.IMAGE)((self.TRBL[1], self.TRBL[0]), (size[0] - self.TRBL[1], size[1] - self.TRBL[0]))
            elif len(self.TRBL) == 3: self.IMAGE = EditImage(self.IMAGE)((self.TRBL[1], self.TRBL[0]), (size[0] - self.TRBL[1], size[1] - self.TRBL[2]))
            elif len(self.TRBL) == 4: self.IMAGE = EditImage(self.IMAGE)((self.TRBL[3], self.TRBL[0]), (size[0] - self.TRBL[1], size[1] - self.TRBL[2]))

        # image需要保存
        if self.WRITE_NAME != "" and self.WRITE_NAME is not None:
            self.write_image(str(self.WRITE_NAME), self.IMAGE)

    def write_image(self, write_name, image):
        write_path, write_name, ext = self.filename_split(write_name)
        write_name = filename_special_char_pattern.sub("", write_name)
        write_name = write_name.replace(".", "")
        # 以正式名称保存
        if write_name.startswith("$_"):
            write_name = f"adc_result_{write_name.strip('$_')}"
            write_name += f"_${self.SN}" if isinstance(self.SN, int) else f"_{timeStamp()}"
        self.full_write_path = self.join_path(write_path, write_name, ext)
        image_save_to_path(self.full_write_path, image, desc=f"SFG")

    def read_image(self, read_name):
        # 如果传入的read_name是Template，获取Template的路径，读入文件，返回cv2的文件
        if isinstance(read_name, Template) and OP.isfile(filepath := read_name.filepath):
            return cv2.imread(str(filepath))
        # 如果传入的是字符串类型，并且不是空串，以http为开头的，就发请求获取，保存图片到本地，并返回cv2格式
        elif isinstance(read_name, (str, Path)) and len(str(read_name)) > 0:
            if str(read_name).startswith("http"):
                response = requests.get(read_name, verify=False)
                content = response.content
                if isinstance(content, ByteString):
                    save_path = logDir / OP.split(read_name)[1]
                    save_path.write_bytes(content)
                    image = cv2.imread(str(save_path))
                    return image
            else:
                # 本地文件存在
                if OP.isfile(filepath := self.join_path(*self.filename_split(read_name))):
                    return cv2.imread(str(filepath))
                elif OP.isfile(filepath := self.join_path(*self.filename_split_v2(read_name))):
                    return cv2.imread(str(filepath))
                else:
                    monitor_task_status_v2("文件不存在", read_name)
        # 其他，传入的为None之类的，就直接走截屏处理
        else:
            # 从屏幕中采集image
            screen_crop_image = screenshot(self.SNAPSHOT_NAME, self.HQ_FUNC)
            # 长安幻想全局打码专用
            if "13765" in str(gameDir):
                screen_crop_image = EditImage(screen_crop_image)(mask=((0, -60), image_size(screen_crop_image)))
            return screen_crop_image

    @staticmethod
    def filename_split(name):
        path, name = OP.split(str(name))
        if not OP.isdir(path):
            path = logDir / path
            for _ in range(3):
                if path.exists():
                    break
                path.mkdir(parents=True)
        name, ext = OP.splitext(name)
        if not ext:
            ext = ".jpg"
        elif ext not in (".jpg", ".png"):
            name += ext.replace(".jpg", "").replace(".png", "")
            ext = ".jpg"
        return path, name, ext

    @staticmethod
    def filename_split_v2(name):
        path, name = OP.split(str(name))
        if not OP.isdir(path): path = mainDir
        name, ext = OP.splitext(name)
        if not ext:
            ext = ".jpg"
        elif ext not in (".jpg", ".png"):
            name += ext.replace(".jpg", "").replace(".png", "")
            ext = ".jpg"
        return path, name, ext

    @staticmethod
    def join_path(write_path, write_name, ext):
        if ext not in (".jpg", ".png"): ext = ".jpg"
        return OPJ(write_path, f"{write_name}{ext}")

    def __call__(self, *args, **kwds):
        if self.needPath:
            return self.IMAGE, self.full_write_path
        return self.IMAGE

    def rename(self, result):
        if self.full_write_path and "$_" not in self.full_write_path and "adc_" not in self.full_write_path:
            filepath, ext = OP.splitext(self.full_write_path)
            new_filename = f"{filepath} {result}{ext}"
            os.renames(self.full_write_path, new_filename)
            self.full_write_path = new_filename

    def ocr(self, en_ocr, mode="r", model=None, enhance_func=None):
        local_ocr = lambda: "".join(ocr_image_base(self.IMAGE, en_ocr=en_ocr)).strip()
        remote_ocr = lambda: "".join(map(lambda x: x[0], ImageOcrRemote(image=self.IMAGE, en_ocr=en_ocr, model=model)())).strip()
        # write_enhance_image = lambda write_image, image: self.write_image(write_image, image)

        # 图片增强
        if callable(enhance_func):
            self.IMAGE = enhance_func(self.IMAGE)

        if mode == "l":
            if callable(enhance_func):
                filename = str(OPJ(ST.LOG_DIR, "enhance_image.png"))
                image_save_to_path(filename, self.IMAGE)
                self.IMAGE = cv2.imread(str(filename))
            local_ocr_result = local_ocr()
            font_color = font_yellow if local_ocr_result else font_red
            output_str = f"<LOCAL_OCR: {local_ocr_result if local_ocr_result else 'null'}{self.DESC}>"
            monitor_print(font_color + output_str.center(70, "-") + font_reset)
            if self.WRITE_NAME != "" and self.WRITE_NAME is not None:
                add_write_name = f"LOCAL_OCR={local_ocr_result.replace('/', '|')}{self.DESC}"
                if callable(enhance_func):
                    self.rename(f"{add_write_name}")
                    # write_enhance_image(f"{self.WRITE_NAME} {add_write_name} B-ENHANCE", image=self.IMAGE)
                else:
                    self.rename(add_write_name)
            return local_ocr_result

        elif mode == "r":
            remote_ocr_result = remote_ocr()
            font_color = font_yellow if remote_ocr_result else font_red
            output_str = f"<REMOTE_OCR: {remote_ocr_result if remote_ocr_result else 'null'}{self.DESC}>"
            monitor_print(font_color + output_str.center(70, "-") + font_reset)
            if self.WRITE_NAME != "" and self.WRITE_NAME is not None:
                add_write_name = f"REMOTE_OCR={remote_ocr_result.replace('/', '|')}{self.DESC}"
                if callable(enhance_func):
                    self.rename(f"{add_write_name}")
                    # write_enhance_image(f"{self.WRITE_NAME} {add_write_name} B-ENHANCE", image=self.IMAGE)
                else:
                    self.rename(add_write_name)
            return remote_ocr_result

        elif mode == "lr":
            if callable(enhance_func):
                filename = str(OPJ(ST.LOG_DIR, "enhance_image.png"))
                image_save_to_path(filename, self.IMAGE)
                self.IMAGE = cv2.imread(str(filename))
            remote_ocr_result, local_ocr_result = remote_ocr(), local_ocr()
            font_color = font_yellow if any((local_ocr_result, remote_ocr_result)) else font_red
            if local_ocr_result == remote_ocr_result:
                output_str = f"<L+R_OCR: {local_ocr_result if local_ocr_result else 'null'}{self.DESC}>"
                monitor_print(font_color + output_str.center(70, "-") + font_reset)
                if self.WRITE_NAME != "" and self.WRITE_NAME is not None:
                    add_write_name = f"L+R_OCR={remote_ocr_result.replace('/', '|')}{self.DESC}"
                    if callable(enhance_func):
                        self.rename(f"{add_write_name}")
                        # write_enhance_image(f"{self.WRITE_NAME} {add_write_name} B-ENHANCE", image=self.IMAGE)
                    else:
                        self.rename(add_write_name)
                return local_ocr_result
            else:
                output_str = f"<LOCAL_OCR: {local_ocr_result if local_ocr_result else 'null'} REMOTE_OCR: {remote_ocr_result if remote_ocr_result else 'null'}{self.DESC}>"
                monitor_print(font_color + output_str.center(70, "-") + font_reset)
                if self.WRITE_NAME != "" and self.WRITE_NAME is not None:
                    add_write_name = f"LOCAL_OCR={local_ocr_result.replace('/', '|')} REMOTE_OCR={remote_ocr_result.replace('/', '|')}{self.DESC}"
                    if callable(enhance_func):
                        self.rename(f"{add_write_name}")
                        # write_enhance_image(f"{self.WRITE_NAME} {add_write_name} B-ENHANCE", image=self.IMAGE)
                    else:
                        self.rename(add_write_name)
                return f"{local_ocr_result} {remote_ocr_result}"

    def match_execute(self, match_image, absolute_pos, target_pos, threshold):
        match_result, score = match_in_base(match_image, self.IMAGE, target_pos, threshold)
        os_env.update(match_score=str(score))
        # 返回绝对位置
        if absolute_pos and match_result and self.LT:
            match_result = match_result[0] + self.LT[0], match_result[1] + self.LT[1]

        self.rename(f"MATCH={match_result if match_result else 'null'}{self.DESC}")
        if "printLog" not in self.kwds or self.kwds.get("printLog"):
            font_color = font_magenta if match_result else font_red
            output_str = f"<Match: {match_result if match_result else 'null'} - score: {score:.2f}{self.DESC}>"
            monitor_print(font_color + output_str.center(70, "-") + font_reset)

        return match_result

    def matchAll_execute(self, match_image, absolute_pos, target_pos, threshold):
        match_result = []
        for box1 in match_in_all_base(match_image, self.IMAGE, threshold):
            for box2 in match_result:
                if box2[0][0] < box1[1][0] and box2[1][0] > box1[0][0] and box2[0][1] < box1[1][1] and box2[1][1] > box1[0][1]:
                    break
            else:
                match_result.append(box1)

        match_result_lenth = len(match_result)
        self.rename(f"MATCHALL={match_result_lenth if match_result_lenth else 'null'}{self.DESC}")
        font_color = font_magenta if match_result else font_red
        output_str = f"<MatchAll: {match_result_lenth if match_result_lenth else 'null'}{self.DESC}>"
        monitor_print(font_color + output_str.center(70, "-") + font_reset)

        if absolute_pos:
            matchAll_result = list(map(lambda x: (int(x[0][0]) + self.LT[0], int(x[1][1]) + self.LT[1]), match_result))
        else:
            matchAll_result = list(map(lambda x: (int(x[0][0]), int(x[1][1])), match_result))

        if isinstance(target_pos, Enum):
            target_pos = target_pos.value
        if target_pos == "center":
            size = image_size(match_image)
            width_half, height_half = int(size[0] / 2), int(size[1] / 2)
            matchAll_result = list(map(lambda x: (x[0] + width_half, x[1] - height_half), matchAll_result))

        if matchAll_result:
            monitor_print(f"{font_color}{matchAll_result}{font_reset}")
        return matchAll_result

    def match(self, match_image, matchAll=False, absolute_pos=False, target_pos=None, threshold=0.7):
        if isinstance(match_image, np.ndarray):
            if matchAll:
                return self.matchAll_execute(match_image, absolute_pos=absolute_pos, target_pos=target_pos, threshold=threshold)
            else:
                return self.match_execute(match_image, absolute_pos=absolute_pos, target_pos=target_pos, threshold=threshold)

        elif isinstance(match_image, Template):
            match_image_path = match_image.filepath
            if OP.isfile(match_image_path):
                if matchAll:
                    return self.matchAll_execute(
                        cv2.imread(str(match_image_path)),
                        absolute_pos=absolute_pos,
                        target_pos=target_pos,
                        threshold=threshold
                    )
                else:
                    return self.match_execute(
                        cv2.imread(str(match_image_path)),
                        absolute_pos=absolute_pos,
                        target_pos=target_pos,
                        threshold=threshold
                    )

        elif isinstance(match_image, (str, Path)):
            match_image = str(match_image)
            match_name = f"{match_image}.png" if not OP.splitext(match_image)[1] else match_image
            match_image_path = ""
            if OP.isfile(match_name):
                match_image_path = match_name
            else:
                image_dirs = [mainDir, logDir, *G.BASEDIR]
                for i in image_dirs:
                    if OP.isfile(OPJ(i, match_name)):
                        match_image_path = OPJ(i, match_name)
                        break

            if match_image_path:
                if matchAll:
                    return self.matchAll_execute(
                        cv2.imread(str(match_image_path)),
                        absolute_pos=absolute_pos,
                        target_pos=target_pos,
                        threshold=threshold
                    )
                else:
                    return self.match_execute(
                        cv2.imread(str(match_image_path)),
                        absolute_pos=absolute_pos,
                        target_pos=target_pos,
                        threshold=threshold
                    )

        else:
            monitor_task_status_v2("Match images", "Match images empty")

    def color_select(self, version=1, printLog=True):
        if version == 1:
            return self.color_v1(printLog=printLog)
        elif version == 2:
            return self.color_v2(printLog=printLog)

    def color_v1(self, printLog=True):
        try:
            image_hsb = cv2.cvtColor(self.IMAGE, cv2.COLOR_BGR2HSV)
            h = int(image_hsb[..., 0].mean() * 2)          # Hue 色相
            s = int(image_hsb[..., 1].mean() / 255 * 100)  # Saturation 饱和度
            b = int(image_hsb[..., 2].mean() / 255 * 100)  # Brightness 亮度
            R = int(self.IMAGE[..., 2].mean())             # 红
            G = int(self.IMAGE[..., 1].mean())             # 绿
            B = int(self.IMAGE[..., 0].mean())             # 蓝
            if printLog:
                self.rename(f"H={h} S={s} B={b} RGB={(R, G, B)}{self.DESC}")
                output_str = f"<Hue: {h}, Stn: {s}, Brs: {b}, RGB: {(R, G, B)}{self.DESC}>"
                monitor_print(font_cyan + output_str.center(70, "-") + font_reset)
            return dict(h=h, s=s, b=b, R=R, G=G, B=B)
        except Exception:
            monitor_task_status_v2("snapshot_color Error", f"{traceback.format_exc()}")
            lx_break_runloop(desc="snapshot_color_v1 Error")

    def color_v2(self, printLog=True):
        try:
            import colorsys
            from colorthief import ColorThief
            # 加载图片
            img_path = ""
            if isinstance(self.IMAGE, np.ndarray):
                img_path = OPJ(ST.LOG_DIR, "color_v2_temp.jpg")
                image_save_to_path(img_path, self.IMAGE)
            elif isinstance(self.IMAGE, Image.Image):
                img_path = OPJ(ST.LOG_DIR, "color_v2_temp.jpg")
                self.IMAGE.save(img_path)

            color_thief = ColorThief(img_path)
            # 获取主颜色
            R, G, B = color_thief.get_color(quality=1)
            # 获取调色板
            # palette = color_thief.get_palette(color_count=6)
            # 使用 colorsys 转换 RGB 到 HSV
            h, s, v = colorsys.rgb_to_hsv(*map(lambda x: x / 255, [R, G, B]))
            h = int(h * 360)  # Hue 色相
            s = int(s * 100)  # Saturation 饱和度
            b = int(v * 100)  # Brightness 亮度
            if printLog:
                self.rename(f"H={h} S={s} B={b} RGB={(R, G, B)}{self.DESC}")
                output_str = f"<Hue: {h}, Stn: {s}, Brs: {b}, RGB: {(R, G, B)}{self.DESC}>"
                monitor_print(font_cyan + output_str.center(70, "-") + font_reset)
            return dict(h=h, s=s, b=b, R=R, G=G, B=B)
        except Exception:
            monitor_task_status_v2("snapshot_color_v2 Error", f"{traceback.format_exc()}")
            lx_break_runloop(desc="snapshot_color_v2 Error")

    def gray(self, printLog=True):
        gray = is_in_gray_range_by_image_base(self.IMAGE)
        if printLog:
            self.rename(f"Gray={'Yes' if gray else 'No'}{self.DESC}")
            output_str = f"<Gray: {'Yes' if gray else 'No'}{self.DESC}>"
            monitor_print(font_gray + output_str.center(70, "-") + font_reset)
        return gray

    def color_gray(self, version=1):
        cg = dict(**self.color_select(version=version, printLog=False), gray=self.gray(printLog=False))
        self.rename(f"H={cg['h']} S={cg['s']} B={cg['b']} RGB={(cg['R'], cg['G'], cg['B'])} Gray={'Yes' if cg['gray'] else 'No'}{self.DESC}")
        output_str = f"<Hue: {cg['h']}, Stn: {cg['s']}, Brs: {cg['b']}, RGB: {(cg['R'], cg['G'], cg['B'])} Gray: {'Yes' if cg['gray'] else 'No'}{self.DESC}>"
        monitor_print(font_cyan + output_str.center(70, "-") + font_reset)
        return cg

def snapshot_write(
        write_name=None,
        LT: Union[Tuple, List]=None,
        RB: Union[Tuple, List]=None,
        width: int=None,
        height: int=None,
        area: Union[Tuple, List]=None,
        edge_reset: bool=None,
        TRBL: Union[Tuple, List, int]=None,
        image: np.ndarray=None,
        mask: Union[Tuple, List]=None,
        sn: int=None,
        read_name: Union[str, Path, Template]=None,
        needPath=False,
        snapshot_name: str=None,
        hq_func: Callable=None,
        **kwds):
    """
    方法处理图片优先级：read_name，image，截屏
    :param write_name: 图片保存名称 ($_名称: 保存为 adc_result), 支持按文件夹保存 (文件夹/文件)
    :param LT: 截图文件裁剪的左上角
    :param RB: 截图文件裁剪的右下角
    :param width: 如果没有传RB，就根据width计算x
    :param height: 如果没有传RB，就根据height计算y
    :param area: 相当于一唯的LTRB）
    :param edge_reset: 超出边界，返回图片最大值
    :param TRBL: 相对位置裁剪，上右下左，和前端的格式一样，一个参数代表上下左右都一样，两个参数代表上下一样，左右一样
    :param image: 待处理图片，如果提供了，就不会走上面截图
    :param mask: 打码区域，多种格式
    :param sn: 序列号
    :param read_name: 读取图片的路径名，全路径或者log下的或者index下的
    :param needPath: True/False，如果为True，返回 nparray 和全路径
    :param snapshot_name: 保存原始图文件名，不用传，会覆盖
    :param hq_func: 高品质图片回调方法
    :return: nparray格式 / nparray格式，path
    """

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    # 实例化
    snapshot_group = SnapshotFunctionGroup(
        write_name=write_name,
        read_name=read_name,
        needPath=needPath,
        snapshot_name=snapshot_name,
        hq_func=hq_func,
        LT=LT,
        RB=RB,
        width=width,
        height=height,
        edge_reset=edge_reset,
        TRBL=TRBL,
        image=image,
        mask=mask,
        sn=sn)

    # 获取图片
    image = snapshot_group()

    # 删除实例
    try:
        del snapshot_group
    except NameError:
        pass

    return image

def snapshot_ocr(
        LT: Union[Tuple, List]=None,
        RB: Union[Tuple, List]=None,
        width: int=None,
        height: int=None,
        area: Union[Tuple, List]=None,
        edge_reset: bool=None,
        TRBL: Union[Tuple, List, int]=None,
        image: np.ndarray=None,
        write_name: str=None,
        read_name: Union[str, Path, Template]=None,
        snapshot_name: str=None,
        hq_func: Callable=None,
        is_digit: bool=None,
        is_chinese: bool=None,
        is_chinese_search: bool=None,
        en_ocr: bool=False,
        mode: str="r",
        model: int=None,
        enhance_func: Callable=None,
        desc: str="",
        **kwds):
    """
    SNAPSHOT功能组OCR
    :param LT: 左上角
    :param RB: 右下角
    :param width: 裁剪宽度
    :param height: 裁剪高度
    :param area: 区域
    :param edge_reset: 裁剪图片不超过图片边界
    :param TRBL: 相对位置裁剪，上右下左
    :param image: 默认图
    :param write_name: 写入图片，$_开头输出result图
    :param read_name: 读取本地图片
    :param snapshot_name: 保存原始图文件名，$_开头输出catch图
    :param is_digit: 使用正则search方法匹配数字
    :param is_chinese: 使用正则findall方法匹配中文
    :param is_chinese_search: 使用正则search方法匹配中文
    :param en_ocr: 使用英文OCR模型
    :param mode: 本地或远程模式
    :param model: 识别模型
    :param enhance_func: 图片增强回调方法
    :param hq_func: 高品质图片回调方法
    :param desc: 描述信息
    :return: ocr结果
    """

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    # 实例化
    snapshot_group = SnapshotFunctionGroup(
        LT=LT,
        RB=RB,
        width=width,
        height=height,
        edge_reset=edge_reset,
        TRBL=TRBL,
        image=image,
        write_name=write_name,
        read_name=read_name,
        snapshot_name=snapshot_name,
        hq_func=hq_func,
        desc=desc)

    # ocr识别结果
    ocr_result = snapshot_group.ocr(en_ocr, mode, model, enhance_func).strip()

    # 删除实例
    try:
        del snapshot_group
    except NameError:
        pass

    if is_digit:
        return extract_digit(ocr_result)

    elif is_chinese_search:
        if regex_result := chinese_pattern.search(ocr_result):
            return regex_result.group()
        return ""

    elif is_chinese:
        return "".join(chinese_pattern.findall(ocr_result))

    return ocr_result

def snapshot_match(
        LT: Union[Tuple, List]=None,
        RB: Union[Tuple, List]=None,
        width: int=None,
        height: int=None,
        area: Union[Tuple, List]=None,
        edge_reset: bool=None,
        TRBL: Union[Tuple, List, int]=None,
        image: np.ndarray=None,
        write_name: str=None,
        read_name: Union[str, Path, Template]=None,
        snapshot_name: str=None,
        hq_func: Callable=None,
        match_image: Union[str, Template, np.array, Path]=None,
        filename: Union[str, Template, np.array, Path]=None,
        threshold: float=0.7,
        target_pos: Union[Enum, str]=None,
        absolute_pos: bool=False,
        is_abs_pos: bool=False,
        desc: str="",
        **kwds):
    """
    图像匹配
    :param LT: (左, 上)
    :param RB: (右, 下)
    :param width: 宽度
    :param height: 高度
    :param area: (左, 上, 右, 下)
    :param edge_reset: 重置边缘
    :param TRBL: 相对位置裁剪
    :param image: 数组对象
    :param write_name: 写入图片名称
    :param read_name: 读取图片名称
    :param snapshot_name: 弃用
    :param hq_func: 截图中间件
    :param match_image: 判断的第二张图
    :param filename: 同上
    :param threshold: 相似度阈值
    :param absolute_pos: 返回绝对坐标
    :param is_abs_pos: 同上
    :param target_pos: 匹配目标位置
    :param desc: 描述信息
    :return:
    """
    match_image = match_image if match_image is not None else filename
    absolute_pos = absolute_pos or is_abs_pos

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    # 实例化
    snapshot_group = SnapshotFunctionGroup(
        LT=LT,
        RB=RB,
        width=width,
        height=height,
        edge_reset=edge_reset,
        TRBL=TRBL,
        image=image,
        write_name=write_name,
        read_name=read_name,
        snapshot_name=snapshot_name,
        hq_func=hq_func,
        desc=desc,
        **kwds)

    # match识别结果
    match_result = snapshot_group.match(
        match_image,
        threshold=threshold,
        absolute_pos=absolute_pos,
        target_pos=target_pos)

    # 删除实例
    try:
        del snapshot_group
    except NameError:
        pass

    return match_result

def snapshot_matchAll(
        LT: Union[Tuple, List]=None,
        RB: Union[Tuple, List]=None,
        width: int=None,
        height: int=None,
        area: Union[Tuple, List]=None,
        edge_reset: bool=None,
        TRBL: Union[Tuple, List, int]=None,
        image: np.ndarray=None,
        write_name: str=None,
        read_name: Union[str, Path, Template]=None,
        snapshot_name: str=None,
        hq_func: Callable=None,
        match_image: Union[str, Template]=None,
        filename: str=None,
        threshold: float=0.7,
        absolute_pos: bool=None,
        is_abs_pos: bool=None,
        target_pos: Union[Enum, str]=None,
        desc: str="",
        **kwds):
    """
    图像匹配全部
    :param LT: (左, 上)
    :param RB: (右, 下)
    :param width: 宽度
    :param height: 高度
    :param area: (左, 上, 右, 下)
    :param edge_reset: 重置边缘
    :param TRBL: 相对位置裁剪
    :param image: 数组对象
    :param write_name: 写入图片名称
    :param read_name: 读取图片名称
    :param snapshot_name: 弃用
    :param hq_func: 截图中间件
    :param match_image: 判断的第二张图
    :param filename: 同上
    :param threshold: 相似度阈值
    :param absolute_pos: 返回绝对坐标
    :param is_abs_pos: 同上
    :param target_pos: 匹配目标位置
    :param desc: 描述信息
    :return:
    """
    match_image = match_image if match_image is not None else filename
    absolute_pos = absolute_pos or is_abs_pos

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    # 实例化
    snapshot_group = SnapshotFunctionGroup(
        LT=LT,
        RB=RB,
        width=width,
        height=height,
        edge_reset=edge_reset,
        TRBL=TRBL,
        image=image,
        write_name=write_name,
        read_name=read_name,
        snapshot_name=snapshot_name,
        hq_func=hq_func,
        desc=desc)

    # match all识别结果
    matchAll_result = snapshot_group.match(
        match_image,
        threshold=threshold,
        matchAll=True,
        absolute_pos=absolute_pos,
        target_pos=target_pos)

    # 删除实例
    try:
        del snapshot_group
    except NameError:
        pass

    return matchAll_result

def snapshot_color(
        LT: Union[Tuple, List]=None,
        RB: Union[Tuple, List]=None,
        width: int=None,
        height: int=None,
        area: Union[Tuple, List]=None,
        edge_reset: bool=None,
        TRBL: Union[Tuple, List, int]=None,
        image: np.ndarray=None,
        write_name: str=None,
        read_name: Union[str, Path, Template]=None,
        snapshot_name: str=None,
        hq_func: Callable=None,
        version=1,
        desc: str="",
        **kwds):
    """

    :param LT:
    :param RB:
    :param width:
    :param height:
    :param area:
    :param edge_reset:
    :param TRBL:
    :param image:
    :param write_name:
    :param read_name:
    :param snapshot_name:
    :param hq_func:
    :param version:
    :param desc:
    :return:
    """

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    if LT and not RB and not any((width, height)):
        RB = (LT[0] + 1, LT[1] + 1)

    # 实例化
    snapshot_group = SnapshotFunctionGroup(
        LT=LT,
        RB=RB,
        width=width,
        height=height,
        edge_reset=edge_reset,
        TRBL=TRBL,
        image=image,
        write_name=write_name,
        read_name=read_name,
        snapshot_name=snapshot_name,
        hq_func=hq_func,
        desc=desc)

    # 颜色识别结果
    color_result = snapshot_group.color_select(version=version)

    # 删除实例
    try:
        del snapshot_group
    except NameError:
        pass

    return color_result

def snapshot_gray(
        LT: Union[Tuple, List]=None,
        RB: Union[Tuple, List]=None,
        width: int=None,
        height: int=None,
        area: Union[Tuple, List]=None,
        edge_reset: bool=None,
        TRBL: Union[Tuple, List, int]=None,
        image: np.ndarray=None,
        write_name: str=None,
        read_name: Union[str, Path, Template]=None,
        snapshot_name: str=None,
        hq_func: Callable=None,
        desc: str="",
        **kwds):
    """
    :param LT:不传的话，就直接判断图，不抠图
    :param RB:不传的话，就直接判断图，不抠图
    :param width:
    :param height:
    :param area:
    :param edge_reset:
    :param TRBL:
    :param image:
    :param write_name:
    :param read_name:
    :param snapshot_name:
    :param hq_func:
    :param desc:
    :return: bool类型，灰的是true，非灰的是false
    """

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    # 实例化
    snapshot_group = SnapshotFunctionGroup(
        LT=LT,
        RB=RB,
        width=width,
        height=height,
        edge_reset=edge_reset,
        TRBL=TRBL,
        image=image,
        write_name=write_name,
        read_name=read_name,
        snapshot_name=snapshot_name,
        hq_func=hq_func,
        desc=desc)

    # 灰度识别结果
    gray_result = snapshot_group.gray()

    # 删除实例
    try:
        del snapshot_group
    except NameError:
        pass

    return gray_result

def snapshot_color_gray(
        LT: Union[Tuple, List]=None,
        RB: Union[Tuple, List]=None,
        width: int=None,
        height: int=None,
        area: Union[Tuple, List]=None,
        edge_reset: bool=None,
        TRBL: Union[Tuple, List, int]=None,
        image: np.ndarray=None,
        write_name: str=None,
        read_name: Union[str, Path, Template]=None,
        snapshot_name: str=None,
        hq_func: Callable=None,
        version=1,
        desc: str="",
        **kwds):
    """

    :param LT:
    :param RB:
    :param width:
    :param height:
    :param area:
    :param edge_reset:
    :param TRBL:
    :param image:
    :param write_name:
    :param read_name:
    :param snapshot_name:
    :param hq_func:
    :param version:
    :param desc:
    :return:
    """

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    # 实例化
    snapshot_group = SnapshotFunctionGroup(
        LT=LT,
        RB=RB,
        width=width,
        height=height,
        edge_reset=edge_reset,
        TRBL=TRBL,
        image=image,
        write_name=write_name,
        read_name=read_name,
        snapshot_name=snapshot_name,
        hq_func=hq_func,
        desc=desc)

    # 颜色灰度识别结果
    color_gray_result = snapshot_group.color_gray(version=version)

    # 删除实例
    try:
        del snapshot_group
    except NameError:
        pass

    return color_gray_result

def snapshot_userID(
        LT=None,
        RB=None,
        width=None,
        height=None,
        area=None,
        is_digit=True,
        en_ocr=False,
        enhance_func=None,
        hq_func=None,
        image=None):
    """
    识别用户ID
    :param LT:
    :param RB:
    :param height:
    :param width:
    :param area:
    :param is_digit:
    :param en_ocr:
    :param hq_func:
    :param enhance_func:
    :param image:
    :return:
    """
    for i in glob(OPJ(ST.LOG_DIR, "adc_seller_*")): os.remove(i)

    if not isinstance(image, np.ndarray):
        image = snapshot_write(f"adc_seller_UID_{timeStamp()}", hq_func=hq_func)
    else:
        snapshot_write(f"adc_seller_UID_{timeStamp()}", image=image)

    if not (LT or RB) and area:
        LT = area[0], area[1]
        RB = area[2], area[3]

    userID = snapshot_ocr(
        LT,
        RB,
        width=width,
        height=height,
        is_digit=is_digit,
        enhance_func=enhance_func,
        image=image,
        en_ocr=en_ocr,
        desc="识别UID")
    if userID:
        userID = chinese_pattern.sub("", userID)
        monitor_task_status_v2("USER_ID", f"UID: {userID}")
        try: property_write("userID", userID)
        except Exception:...
    else:
        monitor_task_status_v2("USER_ID", "识别失败")

    return userID

def snapshot_hq(qc_func, snapshot_name=None):
    """
    高品质截图
    :param qc_func:
    :param snapshot_name:
    :return:
    """
    image = snapshot_write(snapshot_name=snapshot_name)
    if callable(qc_func):
        for _ in range(5):
            qc_image = qc_func(image)
            if isinstance(qc_image, np.ndarray): return qc_image
            elif qc_image: return image
            else: sleep(5)
            image = snapshot_write(snapshot_name=snapshot_name)
        else:
            return image
    else:
        return image

def image_split_generator(
        LT=(0, 0),
        L2L=0,
        T2T=0,
        width=1,
        height=1,
        image: np.ndarray=None,
        need_pos=False,
        limit=0,
        mode="col",
        top_offset_func=None,
        left_offset_func=None,
        need_path=False):
    """
    图片分割生成器（不指定行、列数）
    :param LT:
    :param L2L:
    :param T2T:
    :param width:
    :param height:
    :param image:
    :param need_pos:
    :param limit:
    :param mode: col:先行后列，row先列后行
    :param top_offset_func: top偏移函数
    :param left_offset_func: top偏移函数
    :param need_path: 是否需要路径
    :return:
    """
    save_path = ""
    if need_path:
        save_path = logDir / f"ISG_TEMP_{timeStamp()}"
        for _ in range(5):
            save_path.mkdir()
            if save_path.exists():
                break
        else:
            monitor_print(f"---ISG创建目录失败: {save_path}")

    image_counter = CounterBase()
    if not isinstance(image, np.ndarray): image = snapshot_write()
    size = image_size(image)
    runloop_break = False
    # 先行后列
    if mode == "col":
        for row_index in itertools.count():
            top = LT[1] + T2T * row_index
            if callable(top_offset_func):
                top += top_offset_func(row_index)
            if top > size[1]: break
            for col_index in itertools.count():
                left = LT[0] + L2L * col_index
                if callable(left_offset_func):
                    left += left_offset_func(col_index)
                if left > size[0]: break
                lt = (left, top)
                rb = (lt[0] + width, lt[1] + height)
                if rb[0] <= size[0] and rb[1] <= size[1]:
                    croped_image = snapshot_write(LT=lt, RB=rb, image=image)
                    index = image_counter()
                    if save_path:
                        image_path = str(save_path / f"ISG_{index}.jpg")
                        image_save_to_path(image_path, croped_image, desc="ISG")
                        croped_image = image_path
                    if need_pos:
                        yield croped_image, box2pos(lt, rb)
                    else:
                        yield croped_image
                    if index == limit: runloop_break = True; break
                else: break
                if not L2L: break
            if not T2T: break
            if runloop_break: break
    # 先列后行
    else:
        for col_index in itertools.count():
            left = LT[0] + L2L * col_index
            if callable(left_offset_func):
                left += left_offset_func(col_index)
            if left > size[0]: break
            for row_index in itertools.count():
                top = LT[1] + T2T * row_index
                if callable(top_offset_func):
                    top += top_offset_func(row_index)
                if top > size[1]: break
                lt = (left, top)
                rb = (lt[0] + width, lt[1] + height)
                if rb[0] <= size[0] and rb[1] <= size[1]:
                    croped_image = snapshot_write(LT=lt, RB=rb, image=image)
                    index = image_counter()
                    if save_path:
                        image_path = str(save_path / f"ISG_{index}.jpg")
                        image_save_to_path(image_path, croped_image, desc="ISG")
                        croped_image = image_path
                    if need_pos:
                        yield croped_image, box2pos(lt, rb)
                    else:
                        yield croped_image
                    if index == limit: runloop_break = True; break
                else: break
                if not L2L: break
            if not T2T: break
            if runloop_break: break

def image_splitCR_generator(
        LT=(0, 0),
        L2L=0,
        T2T=0,
        width=0,
        height=0,
        cols=1,
        rows=1,
        image: np.ndarray=None,
        need_pos=False,
        limit=0):
    """
    图片分割生成器（指定行、列数）
    :param LT:
    :param L2L:
    :param T2T:
    :param width:
    :param height:
    :param cols:
    :param rows:
    :param image:
    :param need_pos:
    :param limit:
    :param need_path:
    :return:
    """
    size = image_size(image)
    width = size[0] if not width else width
    height = size[1] if not height else height
    image_counter = CounterBase()
    if not isinstance(image, np.ndarray): image = snapshot_write()
    for row, col in itertools.product(range(rows), range(cols)):
        lt = (LT[0] + L2L * col, LT[1] + T2T * row)
        rb = (lt[0] + width, lt[1] + height)
        if need_pos:
            yield snapshot_write(LT=lt, RB=rb, image=image), box2pos(lt, rb)
        else:
            yield snapshot_write(LT=lt, RB=rb, image=image)
        if image_counter() == limit: break

def image_splitWH_generator(
        LT=(0, 0),
        width=0,
        height=0,
        image=None,
        need_pos=False,
        need_path=False,
        limit=0,
        all_split=True):
    """
    图片分割生成器（指定宽、高）
    :param LT:
    :param width:
    :param height:
    :param image:
    :param need_pos:
    :param need_path:
    :param limit:
    :param all_split:
    :return:
    """
    save_path = ""
    if need_path:
        save_path = logDir / f"ISWHG_TEMP_{timeStamp()}"
        for _ in range(5):
            save_path.mkdir()
            if save_path.exists():
                break
        else:
            monitor_print(f"---ISG创建目录失败: {save_path}")

    image_counter = CounterBase()
    if not isinstance(image, np.ndarray): image = snapshot_write()
    image = snapshot_write(LT=LT, image=image)
    size = image_size(image)
    width = width or size[0]
    height = height or size[1]
    if all_split:
        rows = math.ceil(size[1] / height)
        cols = math.ceil(size[0] / width)
    else:
        rows = size[1] // height
        cols = size[0] // width

    for row, col in itertools.product(range(rows), range(cols)):
        lt = (col * width, row * height)
        rb = (lt[0] + width, lt[1] + height)
        rb = (rb[0] if rb[0] <= size[0] else size[0], rb[1] if rb[1] <= size[1] else size[1])
        croped_image = snapshot_write(LT=lt, RB=rb, image=image)
        index = image_counter()
        if save_path:
            image_path = str(save_path / f"ISG_{index}.jpg")
            image_save_to_path(image_path, croped_image, desc="ISG")
            croped_image = image_path
        if need_pos:
            yield croped_image, box2pos(lt, rb)
        else:
            yield croped_image
        if index == limit:
            break

class ImageOcrRemote:
    def __init__(self, LT=None, RB=None, area=None, image=None, en_ocr=False, model=None):
        """
        OCR识别Remote
        :param LT:
        :param RB:
        :param image:
        :param en_ocr:
        """
        self.LT = LT
        self.RB = RB
        self.area = area
        self.IMAGE = image
        self.EN_OCR = en_ocr
        self.model = model
        save_path = logDir / f'ImageOcrRemote'
        for _ in range(3):
            if save_path.exists():
                break
            save_path.mkdir(parents=True)
        self.wirte_path = str(save_path / f'image_ocr_remote_{timeStamp()}.jpg')

        if not (self.LT or self.RB) and self.area:
            self.LT = self.area[0], self.area[1]
            self.RB = self.area[2], self.area[3]

    def image_ocr_remote(self):
        for i in range(3):
            try:
                if self.EN_OCR:
                    ocrResult = ocr_num_by_eas(self.wirte_path)
                elif self.model:
                    ocrResult = ocr_image_by_eas(self.wirte_path, self.model)
                else:
                    ocrResult = ocr_chinese_by_eas(self.wirte_path)
                result = []
                LT = self.LT or (0, 0)
                for j in ocrResult or []:
                    pos = box2pos(j["box"][0], j["box"][2])
                    result.append((j["txts"], (pos[0] + LT[0], pos[1] + LT[1])))
                # os.remove(self.wirte_path)
                return result
            except Exception:
                if i == 2:
                    monitor_task_status_v2("Remote ocr failed", f"{traceback.format_exc()}", status=10127)
                    lx_break_runloop(desc="Remote ocr failed")
                else:
                    sleep(2)

    def __call__(self):
        if self.LT and self.RB:
            if isinstance(self.IMAGE, np.ndarray) and image_size(self.IMAGE) == get_resolution():
                image = self.IMAGE
            else:
                image = screenshot()
            cropped_image = EditImage(image)(self.LT, self.RB)
            image_save_to_path(self.wirte_path, cropped_image)
            return self.image_ocr_remote()

        elif isinstance(self.IMAGE, np.ndarray):
            image_save_to_path(self.wirte_path, self.IMAGE)
            return self.image_ocr_remote()

def images_match_crop(images, overlap_x=0, overlap_width=0, overlap_hight=100, threshold=0.8):
    """
    图片匹配裁剪
    :param images: 一组相似图片数组或路径
    :param overlap_x: 开始点X坐标
    :param overlap_width: 重叠区域宽度
    :param overlap_hight: 重叠区域高度
    :param threshold: 相似度阈值
    """
    prev_image = image = images.pop(0)
    if not isinstance(image, np.ndarray) and OP.isfile(image):
        prev_image = cv2.imread(str(image))
    croped_images = [image]

    for image in images:
        image_path = ""
        if not isinstance(image, np.ndarray) and OP.isfile(image):
            image_path = image
            image = cv2.imread(str(image))

        prev_image_size = image_size(prev_image)
        left = overlap_x
        top = prev_image_size[1] - overlap_hight
        right = left + overlap_width if overlap_width else prev_image_size[0]
        bottom = prev_image_size[1]
        area = (left, top, right, bottom)
        overlap_image = snapshot_write(area=area, image=prev_image)
        prev_image = image
        if top_offset_pos := snapshot_match(match_image=overlap_image, image=image, threshold=threshold):
            if top_offset_pos[1] >= image_size(image)[1]:
                continue
            croped_image = snapshot_write(TRBL=(top_offset_pos[1], 0, 0, 0), image=image)
            size = image_size(croped_image)
            if size[0] > 0 and size[1] > 0:
                if image_path:
                    image_save_to_path(image_path, croped_image, "IMGMC")
                    croped_images.append(image_path)
                else:
                    croped_images.append(croped_image)

    return croped_images

class LongScreenshotOfTotal:
    def __init__(self, **kwds):
        """
        长截图内容总数模式
        :param kwds:
        """
        # 截图区域
        self.top = kwds.get("top")
        self.left = kwds.get("left")
        self.right = kwds.get("right")
        self.bottom = kwds.get("bottom")
        # 内容区域
        self.content_top = kwds.get("content_top")
        self.content_bottom = kwds.get("content_bottom")
        # 质量控制函数
        self.qc_func = kwds.get("qc_func")
        # 内容总数
        self.content_total = kwds.get("content_total")
        # 最大内容总数
        self.content_total_max = kwds.get("content_total_max", 0)
        # 正常页行、列数
        self.normal_cols = kwds.get("normal_cols")
        self.normal_rows = kwds.get("normal_rows")
        self.normal_count = self.normal_cols * self.normal_rows
        # 最后一页最后一行
        self.lastpage_lastrow_top = kwds.get("lastpage_lastrow_top")
        self.lastpage_lastrow_bottom = kwds.get("lastpage_lastrow_bottom")
        self.lastpage_is_normal = kwds.get("lastpage_is_normal")
        # 滑动接触点和滑动距离
        self.swipe_start_point = kwds.get("swipe_start_point")
        self.swipe_delta_y = kwds.get("swipe_delta_y")
        self.swipe_offset = kwds.get("swipe_offset")
        self.swipe_duration = kwds.get("swipe_duration")
        self.swipe_hold_sec = kwds.get("swipe_hold_sec", 0.5)
        self.swipe_sec = kwds.get("swipe_sec", 0.5)
        self.swipe_mode = kwds.get("swipe_mode")
        self.swipe_func = kwds.get("swipe_func")
        # 最后一页等待回落
        self.lastpage_fall_back = kwds.get("lastpage_fall_back")
        # 保存名称
        self.write_name = kwds.get("write_name")
        self.sn = kwds.get("sn")
        # 打码
        self.top_mask = kwds.get("top_mask")
        self.mask = kwds.get("mask")
        # 暂存区
        self.images = []

    def __call__(self, *args, **kwds):
        # 滑动方式
        if self.swipe_mode == "poco":
            sp = lambda: SwipePoco(self.swipe_start_point, delta_y=swipe_delta_from_env(self.swipe_delta_y), sec=self.swipe_sec)
        else:
            sp = lambda: SwipeAirtest(
                self.swipe_start_point,
                delta_y=swipe_delta_from_env(self.swipe_delta_y),
                offset=self.swipe_offset,
                duration=self.swipe_duration,
                hold_sec=self.swipe_hold_sec,
                sec=self.swipe_sec
            )
        self.images.clear()
        # 标题栏
        if self.content_top > self.top:
            self.images.append(snapshot_write(LT=(self.left, self.top), RB=(self.right, self.content_top), mask=self.top_mask, image=snapshot_hq(self.qc_func)))

        # 内容区域截图
        swipe_count, mod = divmod(self.content_total, self.normal_count)
        if not mod: swipe_count -= 1

        for sc in range(1, swipe_count + 1):
            self.images.append(snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func)))
            sp()()
            if callable(self.swipe_func):
                self.swipe_func(self, sc)

        else:
            # 等待回落
            if isinstance(self.lastpage_fall_back, (int, float)):
                sleep(self.lastpage_fall_back)
            # 最后一页截图
            lastpage_top = 0
            if all((self.lastpage_lastrow_top, self.lastpage_lastrow_bottom, self.bottom)):
                bottom_rows = math.ceil(mod / self.normal_cols) or self.normal_rows
                lastpage_top = self.lastpage_lastrow_bottom - bottom_rows * (self.lastpage_lastrow_bottom - self.lastpage_lastrow_top)
                self.images.append(snapshot_write(LT=(self.left, lastpage_top), RB=(self.right, self.bottom), image=snapshot_hq(self.qc_func)))

            # bottom_rows = self.content_total % self.normal_cols
            # if bottom_rows == 0:
            #     lastpage_top = self.content_top
            # else:
            #     lastpage_top = self.lastpage_lastrow_bottom - bottom_rows * (self.swipe_delta_y / self.normal_cols)
            # print(f"lastpage_top: {int(lastpage_top)}")
            # yield snapshot_write(LT=(self.left, int(lastpage_top)), RB=(self.right, self.lastpage_lastrow_bottom), image=snapshot_hq(self.qc_func))

            # 打码
            if self.mask:
                for index in [*range(len(self.images))][:-1]:
                    if isinstance(self.top, int) and not index: continue
                    self.images[index] = EditImage(self.images[index])(mask=self.mask)
                else:
                    self.images[-1] = EditImage(self.images[-1])(mask=self.mask[:mod or self.normal_count])

            # 保存截图
            if self.write_name:
                header_height = self.content_top - self.top
                body_height = self.content_bottom - self.content_top
                footer_height = self.lastpage_lastrow_bottom - lastpage_top
                rows = math.ceil((LIMITPIXEL - header_height - footer_height) / body_height)
                combine_images_write(self.write_name, images=self.images, rows=rows, sn=self.sn)

        return self.images

class LongScreenshotPrecisionSwipe:
    def __init__(self, **kwds):
        """
        长截图精准滑动
        适用场景：内容区域上下间隔一致
        :param kwds:
        """
        # 截图区域
        self.top = kwds.get("top")
        self.left = kwds.get("left")
        self.right = kwds.get("right")
        self.bottom = kwds.get("bottom")
        # 判底函数
        self.checkBottom_func = kwds.get("checkBottom_func")
        # 质量控制函数
        self.qc_func = kwds.get("qc_func")
        # 内容区域
        self.content_top = kwds.get("content_top")
        self.content_bottom = kwds.get("content_bottom")
        # 内容重叠区域
        self.content_overlap_top = kwds.get("content_overlap_top")
        self.content_overlap_bottom = kwds.get("content_overlap_bottom")
        # 最后一页内容区域
        self.lastpage_content_top = kwds.get("lastpage_content_top")
        # 最后一页内容项目间隔、行数
        self.lastpage_content_items_T2T = kwds.get("lastpage_content_items_T2T")
        self.lastpage_content_items_rows = kwds.get("lastpage_content_items_rows")
        # 滑动参数
        self.swipe_start_point = kwds.get("swipe_start_point")
        self.swipe_delta_y = kwds.get("swipe_delta_y")
        self.swipe_offset = kwds.get("swipe_offset")
        self.swipe_duration = kwds.get("swipe_duration")
        self.swipe_hold_sec = kwds.get("swipe_hold_sec", 0.3)
        self.swipe_sec = kwds.get("swipe_sec", 0.3)
        self.swipe_mode = kwds.get("swipe_mode")
        self.swipe_count = kwds.get("swipe_count")
        self.swipe_func = kwds.get("swipe_func")
        self.swipe_raise_ex = kwds.get("swipe_raise_ex", True)
        # 滑动悬停
        self.is_hold = kwds.get("is_hold")
        self.lastpage_fall_back = kwds.get("lastpage_fall_back")
        # 合并保存参数
        self.write_name = kwds.get("write_name")
        self.max_rows = kwds.get("max_rows")
        self.sn = kwds.get("sn")
        # 打码
        self.top_mask = kwds.get("top_mask")
        self.mask = kwds.get("mask")
        # 图片暂存
        self.images = []

    def __call__(self, *args, **kwargs):
        self.images.clear()
        swipe_before_image = snapshot_hq(self.qc_func)
        # 只有一页
        if self.checkBottom_func(swipe_before_image):
            self.images.append(snapshot_write(self.write_name, image=swipe_before_image, LT=(self.left, self.top), RB=(self.right, self.bottom), mask=self.mask, sn=self.sn))
        # 存在多页
        else:
            # 标题栏
            if self.content_top > self.top:
                self.images.append(snapshot_write(LT=(self.left, self.top), RB=(self.right, self.content_top), image=swipe_before_image, mask=self.top_mask))
            # 滑动悬停
            if self.swipe_mode == "poco":
                sp = lambda: SwipePoco(self.swipe_start_point, delta_y=self.swipe_delta_y, sec=self.swipe_sec)
            else:
                sp = lambda: SwipeAirtest(
                    self.swipe_start_point,
                    delta_y=self.swipe_delta_y,
                    offset=self.swipe_offset,
                    duration=self.swipe_duration,
                    hold_sec=self.swipe_hold_sec,
                    sec=self.swipe_sec
                )
            # 内容
            for i in range(1, self.swipe_count + 1 if isinstance(self.swipe_count, int) else 80):
                if self.is_hold:
                    with sp():
                        checkBottom_image = snapshot_write()
                    swipe_after_image = snapshot_hq(self.qc_func)
                else:
                    spins = sp()
                    if callable(spins): spins()
                    checkBottom_image = swipe_after_image = snapshot_hq(self.qc_func)
                self.images.append(snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), mask=self.mask, image=swipe_before_image))

                if not self.checkBottom_func(checkBottom_image):
                    swipe_before_image = swipe_after_image
                # 最后一页
                else:
                    match_image = snapshot_write(LT=(self.left, self.content_overlap_top), RB=(self.right, self.content_overlap_bottom), image=swipe_before_image)
                    if pos := snapshot_match((self.left, self.lastpage_content_top), (self.right, self.bottom), image=swipe_after_image, match_image=match_image):
                        pair_result, check_height = digit_pair([self.lastpage_content_top + self.lastpage_content_items_T2T * i for i in range(self.lastpage_content_items_rows + 1)]), pos[1] + self.lastpage_content_top
                        index = find_range_index(pair_result, check_height)
                        monitor_print(f"{pair_result=}, {check_height=}, {index=}")
                        top = self.lastpage_content_top + self.lastpage_content_items_T2T * index
                        self.images.append(snapshot_write(LT=(self.left, top), RB=(self.right, self.bottom), mask=self.mask, image=swipe_after_image))
                    else:
                        self.images.append(snapshot_write(LT=(self.left, self.lastpage_content_top), RB=(self.right, self.bottom), mask=self.mask, image=swipe_after_image))
                    monitor_task_status_v2("LongScreenshotPrecisionSwipe 结束", f"滑动{i}次")
                    break
            else:
                if self.swipe_raise_ex:
                    monitor_catch("超过滑动次数", status=10134, break_mode=BreakModeEnum.runloop)

            # 合并保存截图
            if self.write_name:
                max_rows = self.max_rows or (LIMITPIXEL - (self.content_top - self.top)) // (self.content_bottom - self.content_top)
                combine_images_write(self.write_name, images=self.images, rows=max_rows, sn=self.sn)

        return self.images

class LongScreenshotSingleRow:
    def __init__(self, **kwds):
        """
        长截图单行精准滑动
        适用场景：内容区域为单行上下间隔一致，最后一页无需 match 拼接
        :param kwds:
        """
        # 截图区域
        self.top = kwds.get("top")
        self.left = kwds.get("left")
        self.right = kwds.get("right")
        self.bottom = kwds.get("bottom")
        # 判底函数
        self.checkBottom_func = kwds.get("checkBottom_func")
        self.is_hold = kwds.get("is_hold")
        # 质量控制函数
        self.qc_func = kwds.get("qc_func")
        # 内容区域
        self.content_top = kwds.get("content_top")
        self.content_bottom = kwds.get("content_bottom")
        # 最后一页内容区域
        self.lastpage_content_top = kwds.get("lastpage_content_top")
        # 滑动参数
        self.swipe_start_point = kwds.get("swipe_start_point")
        self.swipe_delta_y = kwds.get("swipe_delta_y")
        self.swipe_offset = kwds.get("swipe_offset")
        self.swipe_duration = kwds.get("swipe_duration")
        self.swipe_hold_sec = kwds.get("swipe_hold_sec", 0.5)
        self.swipe_sec = kwds.get("swipe_sec", 0.5)
        self.swipe_mode = kwds.get("swipe_mode")
        self.swipe_count = kwds.get("swipe_count")
        self.swipe_func = kwds.get("swipe_func")
        self.swipe_raise_ex = kwds.get("swipe_raise_ex", True)
        # 合并保存参数
        self.write_name = kwds.get("write_name")
        self.sn = kwds.get("sn")
        self.max_rows = kwds.get("max_rows")
        # 打码
        self.top_mask = kwds.get("top_mask")
        self.mask = kwds.get("mask")
        self.lastpage_mask = kwds.get("lastpage_mask")
        # 图片暂存
        self.images = []

    def __call__(self, *args, **kwargs):
        self.images.clear()
        swipe_before_image = snapshot_hq(self.qc_func)
        # 只有一页
        if self.checkBottom_func(swipe_before_image):
            self.images.append(snapshot_write(self.write_name, image=swipe_before_image, LT=(self.left, self.top), RB=(self.right, self.bottom), mask=self.mask, sn=self.sn))
        # 存在多页
        else:
            # 标题栏
            if self.content_top > self.top:
                self.images.append(snapshot_write(LT=(self.left, self.top), RB=(self.right, self.content_top), image=swipe_before_image, mask=self.top_mask))
            # 滑动悬停
            if self.swipe_mode == "poco":
                sp = lambda: SwipePoco(self.swipe_start_point, delta_y=self.swipe_delta_y, sec=self.swipe_sec)
            else:
                sp = lambda: SwipeAirtest(
                    self.swipe_start_point,
                    delta_y=self.swipe_delta_y,
                    offset=self.swipe_offset,
                    duration=self.swipe_duration,
                    hold_sec=self.swipe_hold_sec,
                    sec=self.swipe_sec
                )
            # 内容
            for i in range(1, self.swipe_count + 1 if isinstance(self.swipe_count, int) else 80):
                if self.is_hold:
                    with sp():
                        checkBottom_image = snapshot_write()
                    swipe_after_image = snapshot_hq(self.qc_func)
                else:
                    spins = sp()
                    if callable(spins): spins()
                    checkBottom_image = swipe_after_image = snapshot_hq(self.qc_func)
                self.images.append(snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), mask=self.mask, image=swipe_before_image))

                if not self.checkBottom_func(checkBottom_image):
                    swipe_before_image = swipe_after_image
                # 最后一页
                else:
                    self.images.append(snapshot_write(LT=(self.left, self.lastpage_content_top), RB=(self.right, self.bottom), mask=self.lastpage_mask, image=swipe_after_image))
                    monitor_task_status_v2("LongScreenshotSingleRow 结束", f"滑动{i}次")
                    break
            else:
                if self.swipe_raise_ex:
                    monitor_catch("超过滑动次数", status=10134, break_mode=BreakModeEnum.runloop)

            # 合并保存截图
            if self.write_name:
                max_rows = self.max_rows or (LIMITPIXEL - (self.content_top - self.top)) // (self.content_bottom - self.content_top)
                combine_images_write(self.write_name, images=self.images, rows=max_rows, sn=self.sn)

        return self.images

class LongScreenshotLite:
    def __init__(self, **kwds):
        """
        长截图有限次数精准滑动
        适用场景：滑动页数确定，最后一页无需 match 拼接
        :param kwds:
        """
        # 截图区域
        self.top = kwds.get("top")
        self.left = kwds.get("left")
        self.right = kwds.get("right")
        self.bottom = kwds.get("bottom")
        # 质量控制函数
        self.qc_func = kwds.get("qc_func")
        # 内容区域
        self.content_top = kwds.get("content_top")
        self.content_bottom = kwds.get("content_bottom")
        # 最后一页内容区域
        self.lastpage_content_top = kwds.get("lastpage_content_top")
        # 滑动参数
        self.swipe_start_point = kwds.get("swipe_start_point")
        self.swipe_delta_y = kwds.get("swipe_delta_y")
        self.swipe_count = kwds.get("swipe_count")
        self.swipe_offset = kwds.get("swipe_offset")
        self.swipe_duration = kwds.get("swipe_duration")
        self.swipe_hold_sec = kwds.get("swipe_hold_sec", 0.5)
        self.swipe_sec = kwds.get("swipe_sec", 0.5)
        self.swipe_mode = kwds.get("swipe_mode")
        # 合并保存参数
        self.write_name = kwds.get("write_name")
        self.sn = kwds.get("sn")
        self.max_rows = kwds.get("max_rows")
        self.top_mask = kwds.get("top_mask")
        # 图片暂存
        self.images = []

    def __call__(self, *args, **kwargs):
        self.images.clear()
        # 标题栏
        if self.content_top > self.top:
            self.images.append(snapshot_write(LT=(self.left, self.top), RB=(self.right, self.content_top), mask=self.top_mask, image=snapshot_hq(self.qc_func)))
        # 滑动悬停
        if self.swipe_mode == "poco":
            sp = SwipePoco(self.swipe_start_point, delta_y=self.swipe_delta_y, sec=self.swipe_sec)
        else:
            sp = SwipeAirtest(
                self.swipe_start_point,
                delta_y=self.swipe_delta_y,
                offset=self.swipe_offset,
                duration=self.swipe_duration,
                hold_sec=self.swipe_hold_sec,
                sec=self.swipe_sec
            )
        # 内容
        for _ in range(self.swipe_count):
            self.images.append(snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func)))
            sp()
        else:
            # 最后一页
            self.images.append(snapshot_write(LT=(self.left, self.lastpage_content_top), RB=(self.right, self.bottom), image=snapshot_hq(self.qc_func)))

        # 合并保存截图
        if self.write_name:
            max_rows = self.max_rows or (LIMITPIXEL - (self.content_top - self.top)) // (self.content_bottom - self.content_top)
            combine_images_write(self.write_name, images=self.images, rows=max_rows, sn=self.sn)

        return self.images

class LongScreenshotNonprecisionSwipe:
    def __init__(self, **kwds):
        """
        长截图非精准滑动
        适用场景：内容区域上下间隔不一致
        :param kwds:
        """
        # 截图区域
        self.top = kwds.get("top")
        self.left = kwds.get("left")
        self.right = kwds.get("right")
        self.bottom = kwds.get("bottom")
        # 判底函数
        self.checkBottom_func = kwds.get("checkBottom_func")
        self.checkBottom_count = kwds.get("checkBottom_count", 1)
        # 质量控制函数
        self.qc_func = kwds.get("qc_func")
        # 内容区域
        self.content_top = kwds.get("content_top")
        self.content_bottom = kwds.get("content_bottom")
        self.lastpage_content_bottom = kwds.get("lastpage_content_bottom")
        # 内容重叠区域
        self.content_overlap_top = kwds.get("content_overlap_top")
        self.content_overlap_bottom = kwds.get("content_overlap_bottom")
        # 滑动参数
        self.swipe_start_point = kwds.get("swipe_start_point")
        self.swipe_delta_y = kwds.get("swipe_delta_y")
        self.swipe_offset = kwds.get("swipe_offset")
        self.swipe_duration = kwds.get("swipe_duration")
        self.swipe_hold_sec = kwds.get("swipe_hold_sec", 0.5)
        self.swipe_sec = kwds.get("swipe_sec", 0.5)
        self.swipe_mode = kwds.get("swipe_mode")
        self.swipe_count = kwds.get("swipe_count")
        self.swipe_func = kwds.get("swipe_func")
        self.swipe_raise_ex = kwds.get("swipe_raise_ex", True)
        # 合并保存参数
        self.write_name = kwds.get("write_name")
        self.sn = kwds.get("sn")
        self.max_rows = kwds.get("max_rows")
        self.top_mask = kwds.get("top_mask")
        self.images = []

    def images_match(self, overlap_image, swipe_after_image, sc):
        if top_offset_pos := snapshot_match(match_image=overlap_image, image=swipe_after_image):
            image = snapshot_write(TRBL=(top_offset_pos[1], 0, 0, 0), image=swipe_after_image)
            size = image_size(image)
            if size[0] > 0 and size[1] > 0:
                snapshot_write(f"lsnp part {sc}", image=image)
                self.images.append(image)
                return top_offset_pos
        else:
            swipe_after_image_url = image_upload("swipe_after_image", swipe_after_image, local_save=True)[1]
            overlap_image_url = image_upload("overlap_image", overlap_image, local_save=True)[1]
            monitor_task_status_v2("ScrNonpreSwiGen match failed", f"{swipe_after_image_url}, {overlap_image_url}")

    def __call__(self, *args, **kwargs):
        self.images.clear()
        first_image = snapshot_hq(self.qc_func)
        # 只有一页
        if self.checkBottom_func(first_image):
            self.images.append(snapshot_write(self.write_name, image=first_image, LT=(self.left, self.top), RB=(self.right, self.bottom), mask=self.top_mask, sn=self.sn))
        # 存在多页
        else:
            # 标题栏
            if self.content_top > self.top:
                self.images.append(snapshot_write(LT=(self.left, self.top), RB=(self.right, self.content_top), image=first_image))
            # 滑动悬停
            if self.swipe_mode == "poco":
                sp = lambda: SwipePoco(self.swipe_start_point, delta_y=self.swipe_delta_y, sec=self.swipe_sec)
            else:
                sp = lambda: SwipeAirtest(
                    self.swipe_start_point,
                    delta_y=self.swipe_delta_y,
                    offset=self.swipe_offset,
                    duration=self.swipe_duration,
                    hold_sec=self.swipe_hold_sec,
                    sec=self.swipe_sec
                )
            # 内容
            self.images.append(snapshot_write("lsnp part 0", LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=first_image))
            checkBottom_counter = CounterBase()
            for sc in range(1, self.swipe_count + 1 if isinstance(self.swipe_count, int) else 100):
                overlap_image = snapshot_write(LT=(self.left, self.content_overlap_top), RB=(self.right, self.content_overlap_bottom or self.content_bottom), image=first_image)
                first_image = None
                with sp():
                    checkBottom_image = snapshot_write()

                swipe_after_image = snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func))
                self.images_match(overlap_image, swipe_after_image, sc)

                # 多次判底
                if self.checkBottom_func(checkBottom_image):
                    if checkBottom_counter() == self.checkBottom_count:
                        break
                else:
                    checkBottom_counter = CounterBase()
            else:
                if self.swipe_raise_ex:
                    monitor_catch("超过滑动次数", status=10134, break_mode=BreakModeEnum.runloop)

            # 底栏
            if self.bottom > self.content_bottom:
                self.images.append(snapshot_write(LT=(self.left, self.content_bottom), RB=(self.right, self.bottom), image=snapshot_hq(self.qc_func)))

            # 合并保存截图
            if self.write_name:
                max_rows = self.max_rows or (LIMITPIXEL - (self.content_top - self.top)) // (self.content_bottom - self.content_top)
                combine_images_write(self.write_name, images=self.images, rows=max_rows, sn=self.sn)

        return self.images

class LongScreenshotNonprecisionSwipeVer2(LongScreenshotNonprecisionSwipe):
    def __init__(self, **kwds):
        """
        长截图非精准滑动V2
        适用场景：内容区域上下间隔不一致
        :param left
        :param right
        :param checkBottom_func
        :param checkBottom_count
        :param qc_func
        :param content_top
        :param content_bottom
        :param lastpage_content_bottom: 最后一页截图区域补充底图
        :param content_overlap_top
        :param content_overlap_bottom
        :param swipe_start_point
        :param swipe_delta_y
        :param swipe_offset
        :param swipe_duration
        :param swipe_hold_sec
        :param swipe_sec
        :param swipe_mode
        :param swipe_count
        :param swipe_raise_ex: 超过滑动次数后抛异常
        """
        super().__init__(**kwds)

    def __call__(self, *args, **kwargs):
        self.images.clear()
        first_image = snapshot_hq(self.qc_func)
        # 只有一页
        if self.checkBottom_func(first_image):
            self.images.append(snapshot_write("lsnp part 0", LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=first_image))
        # 存在多页
        else:
            # 滑动悬停
            if self.swipe_mode == "poco":
                sp = lambda: SwipePoco(self.swipe_start_point, delta_y=self.swipe_delta_y, sec=self.swipe_sec)
            else:
                sp = lambda: SwipeAirtest(
                    self.swipe_start_point,
                    delta_y=self.swipe_delta_y,
                    offset=self.swipe_offset,
                    duration=self.swipe_duration,
                    hold_sec=self.swipe_hold_sec,
                    sec=self.swipe_sec
                )
            # 内容
            self.images.append(snapshot_write("lsnp part 0", LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=first_image))
            checkBottom_counter = CounterBase()
            for sc in range(1, self.swipe_count + 1 if isinstance(self.swipe_count, int) else 100):
                overlap_image = snapshot_write(LT=(self.left, self.content_overlap_top), RB=(self.right, self.content_overlap_bottom or self.content_bottom), image=first_image)
                first_image = None
                with sp():
                    checkBottom_image = snapshot_write()
                if callable(self.swipe_func):
                    self.swipe_func(self, sc)

                swipe_after_image = snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func))
                self.images_match(overlap_image, swipe_after_image, sc)

                # 多次判底
                if self.checkBottom_func(checkBottom_image):
                    if checkBottom_counter() == self.checkBottom_count:
                        # 最后一页补充底图
                        if self.lastpage_content_bottom and self.lastpage_content_bottom > self.content_bottom:
                            self.images.append(snapshot_write(LT=(self.left, self.content_bottom), RB=(self.right, self.lastpage_content_bottom), image=snapshot_hq(self.qc_func)))
                        break
                else:
                    checkBottom_counter = CounterBase()
            else:
                if self.swipe_raise_ex:
                    monitor_catch("超过滑动次数", status=10134, break_mode=BreakModeEnum.runloop)

        return combine_images_write(images=self.images, rows=len(self.images))[0]

class LongScreenshotNonprecisionSwipeVer3:
    def __init__(self, **kwds):
        """
        长截图非精准滑动V3
        """
        # 截图区域
        self.left = kwds.get("left")
        self.right = kwds.get("right")
        self.width = self.right - self.left
        self.content_top = kwds.get("content_top")
        self.content_bottom = kwds.get("content_bottom")
        self.height = self.content_bottom - self.content_top
        self.lastpage_content_bottom = kwds.get("lastpage_content_bottom")
        # 内容重叠区域开始点X
        self.content_overlap_x = kwds.get("content_overlap_x", 0)
        # 内容重叠区域宽度, 包含开始宽度
        self.content_overlap_width = kwds.get("content_overlap_width", 0)
        # 内容重叠区域高度
        self.content_overlap_height = kwds.get("content_overlap_height", 100)
        # 拼图相似度阈值
        self.threshold = kwds.get("threshold", 0.8)
        # 判底函数
        self.checkBottom_func = kwds.get("checkBottom_func")
        # 判底次数
        self.checkBottom_count = kwds.get("checkBottom_count", 1)
        # 质量控制函数
        self.qc_func = kwds.get("qc_func")
        # 滑动方法
        self.swipe_func = kwds.get("swipe_func")
        # 滑动次数
        self.swipe_count = kwds.get("swipe_count", 100)
        # 保存名称
        self.write_name = kwds.get("write_name")
        self.sn = kwds.get("sn")

    def __call__(self, *args, **kwargs):
        images_croped_paths = []
        prev_image = image = bottom_image = None
        checkBottom_counter = CounterBase()
        save_path = logDir / f"LSNP3_TEMP_{timeStamp()}"
        for sc in range(1, self.swipe_count + 1):
            image = snapshot_hq(self.qc_func)
            image_croped = EditImage(image).crop((self.left, self.content_top), (self.right, self.content_bottom))
            image_path = save_path / f"LSNP3_{sc}.jpg"
            image_save_to_path(image_path, image_croped, "LSNP3")
            images_croped_paths.append(str(image_path))

            # 多次判底
            if sc > 1:
                checkBottom_value = 0
                if callable(self.checkBottom_func):
                    checkBottom_value = self.checkBottom_func(prev_image, image)
                if checkBottom_value == 1 and checkBottom_counter() == self.checkBottom_count:
                    break
                elif checkBottom_value == 2:
                    break
                elif checkBottom_value == 0:
                    checkBottom_counter.reset()

            # 滑动方法返回True结束
            if self.swipe_func(sc):
                break

            prev_image = image

        # 图片分割
        images_match_crop_result = images_match_crop(
            images_croped_paths,
            overlap_x=self.content_overlap_x,
            overlap_width=self.content_overlap_width,
            overlap_hight=self.content_overlap_height,
            threshold=self.threshold)

        # 最后一页补充底图
        if self.lastpage_content_bottom and self.lastpage_content_bottom > self.content_bottom:
            image_croped = EditImage(image).crop((self.left, self.content_bottom), (self.right, self.lastpage_content_bottom))
            image_path = save_path / f"LSNP3_Bottom.jpg"
            image_save_to_path(image_path, image_croped, "LSNP3")
            bottom_image = image_path

        # 图片合并
        if bottom_image is not None:
            images_match_crop_result.append(bottom_image)
        long_image = combine_images_write(images=images_match_crop_result, rows=len(images_match_crop_result))[0]

        if self.write_name:
            images_batch_write(self.write_name, list(image_splitWH_generator(height=LIMITPIXEL, image=long_image)), sn=self.sn)

        # 清空图片
        delete_path(save_path)
        return long_image

# 从环境变量中获取滑动距离
def swipe_delta_from_env(swipe_delta_y):
    if swipe_delta_y_str := os_env.get("swipe_delta_y"):
        os_env.pop("swipe_delta_y")
        if swipe_delta_y_str.isdigit() or swipe_delta_y_str[0] == "-" and swipe_delta_y_str[1:].isdigit():
            swipe_delta_y = int(swipe_delta_y_str)
    return swipe_delta_y

class LongScreenshotOfTotalGenerator(LongScreenshotOfTotal):
    def __init__(self, **kwds):
        """
        长截图内容总数模式生成器
        :param left：识别内容左边界
        :param right：识别内容右边界
        :param content_top：识别内容上边界
        :param content_bottom：识别内容下边界
        :param content_total：识别内容全部区域总数
        :param content_total_max：识别内容最大数，游戏固定的
        :param normal_cols：正常列
        :param normal_rows：正常行
        :param normal_count：正常页的数量，不需要传
        :param lastpage_lastrow_top：最后一页最后一行的顶部值
        :param lastpage_lastrow_bottom：最后一页最后一行的底部值
        :param lastpage_is_normal：最后一次滑动是否正常页
        :param swipe_start_point：滑动开始点
        :param swipe_delta_y：滑动y轴距离
        :param swipe_duration：滑动持续时长，几秒滑动完
        :param swipe_hold_sec：滑动到终点保持几秒
        :param swipe_offset=1：滑动到最后拉回来一点，传递一般是负数
        :param swipe_sec：滑动松开之后等待几秒
        :param swipe_mode：滑动模式，用poco滑动，还是airtest滑动
        :param swipe_func：滑动的函数，滑动过程中动态调整，比如说滑动的第几次，单独处理
        :param swipe_raise_ex: 超过滑动次数后抛异常
        :param qc_func：质量控制函数，在每次截图的时候给图片判断质量，有没有弹窗之类的
        """
        super().__init__(**kwds)

    def __call__(self, *args, **kwds):
        # 内容区域截图
        swipe_count, mod = divmod(self.content_total, self.normal_count)
        if not mod: swipe_count -= 1
        # 仅一页
        if not swipe_count:
            yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func))
        # 存在多页
        else:
            # 滑动方式
            if self.swipe_mode == "poco":
                sp = lambda: SwipePoco(self.swipe_start_point, delta_y=swipe_delta_from_env(self.swipe_delta_y), sec=self.swipe_sec)
            else:
                sp = lambda: SwipeAirtest(
                    self.swipe_start_point,
                    delta_y=swipe_delta_from_env(self.swipe_delta_y),
                    offset=self.swipe_offset,
                    duration=self.swipe_duration,
                    hold_sec=self.swipe_hold_sec,
                    sec=self.swipe_sec
                )

            for sc in range(1, swipe_count + 1):
                yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func))
                sp()()
                if callable(self.swipe_func):
                    self.swipe_func(self, sc)

            else:
                # 等待回落
                if isinstance(self.lastpage_fall_back, (int, float)):
                    sleep(self.lastpage_fall_back)
                # 最后一页截图
                if self.lastpage_is_normal or int(self.content_total_max / self.normal_count) > swipe_count:
                    yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func))
                else:
                    bottom_rows = math.ceil(mod / self.normal_cols) or self.normal_rows
                    lastpage_top = self.lastpage_lastrow_bottom - bottom_rows * (self.lastpage_lastrow_bottom - self.lastpage_lastrow_top)
                    yield snapshot_write(LT=(self.left, lastpage_top), RB=(self.right, self.lastpage_lastrow_bottom), image=snapshot_hq(self.qc_func))

                # bottom_rows = self.content_total % self.normal_cols
                # if bottom_rows == 0:
                #     lastpage_top = self.content_top
                # else:
                #     lastpage_top = self.lastpage_lastrow_bottom - bottom_rows * (self.swipe_delta_y / self.normal_cols)
                # print(f"lastpage_top: {int(lastpage_top)}")
                # yield snapshot_write(LT=(self.left, int(lastpage_top)), RB=(self.right, self.lastpage_lastrow_bottom), image=snapshot_hq(self.qc_func))

class LongScreenshotPrecisionSwipeGenerator(LongScreenshotPrecisionSwipe):
    def __init__(self, **kwds):
        """
        长截图精准滑动生成器
        适用场景：内容区域上下间隔一致
        :param left: 整体左边
        :param right: 整体右边
        :param checkBottom_func: 判底函数------snapshot_gray
        :param qc_func: 质量控制函数
        :param content_top: 内容区域顶部
        :param content_bottom: 内容区域底部
        :param content_overlap_top: 重叠区域顶部
        :param content_overlap_bottom: 重叠区域底部
        :param lastpage_content_top: 最后一页顶部
        :param lastpage_content_bottom: 最后一页底部
        :param lastpage_content_items_T2T: 最后一页T2T间隔
        :param lastpage_content_items_rows: 最后一页内容行数
        :param swipe_start_point: 滑动起点
        :param swipe_delta_y: 滑动距离
        :param swipe_mode: 滑动方式
        :param swipe_func: 滑动过程控制，返回true会停止滑动
        :param swipe_raise_ex: 超过滑动次数后抛异常
        :param is_hold: 保持悬停
        :param lastpage_fall_back: 最后一页等待回落
        :param desc: 任务描述
        """
        self.lastpage_content_bottom = kwds.get("lastpage_content_bottom")
        self.desc = desc_format2(kwds.get("desc"))
        super().__init__(**kwds)

    def __call__(self, *args, **kwargs):
        # 滑动方式
        # 是iOS系统
        if isiOS:
            sp = lambda: air_swipe_fast(self.swipe_start_point, delta_y=swipe_delta_from_env(self.swipe_delta_y), duration=self.swipe_duration, sec=self.swipe_sec)
        # 是Android系统，poco模式
        elif self.swipe_mode == "poco":
            sp = lambda: SwipePoco(self.swipe_start_point, delta_y=swipe_delta_from_env(self.swipe_delta_y), sec=self.swipe_sec)
        # 是Android系统，airtest模式
        else:
            sp = lambda: SwipeAirtest(
                self.swipe_start_point,
                delta_y=swipe_delta_from_env(self.swipe_delta_y),
                offset=self.swipe_offset,
                duration=self.swipe_duration,
                hold_sec=self.swipe_hold_sec,
                sec=self.swipe_sec
            )
        swipe_before_image = snapshot_hq(self.qc_func)
        checkBottom_match_image = None
        loop_break = False
        for sc in range(1, self.swipe_count + 1 if isinstance(self.swipe_count, int) else 80):
            # 滑动判底截图
            if self.is_hold:
                with sp():
                    checkBottom_image = snapshot_write()
                if callable(self.swipe_func):
                    loop_break = self.swipe_func(self, sc)
                swipe_after_image = snapshot_hq(self.qc_func)
            else:
                spins = sp()
                if callable(spins): spins()
                if callable(self.swipe_func):
                    loop_break = self.swipe_func(self, sc)
                checkBottom_image = swipe_after_image = snapshot_hq(self.qc_func)

            # 停止滑动
            if loop_break:
                break

            checkBottom_value = self.checkBottom_func(swipe_before_image, checkBottom_image)
            if not checkBottom_value:
                yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=swipe_before_image)
                checkBottom_match_image = swipe_before_image
                swipe_before_image = swipe_after_image
            # 最后一页
            else:
                # 仅在match判底方法使用
                if checkBottom_value != 2:
                    yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=swipe_before_image)

                # 等待回落
                if isinstance(self.lastpage_fall_back, (int, float)):
                    sleep(self.lastpage_fall_back)
                    swipe_after_image = snapshot_hq(self.qc_func)
                else:
                    snapshot_write(f"ScrPreSwiGen_lastpage{self.desc}", image=swipe_after_image)
                lastpage_content_bottom = self.lastpage_content_bottom or (self.content_bottom - self.content_top + self.lastpage_content_top)

                if checkBottom_value == 2 and checkBottom_match_image is not None:
                    match_image = snapshot_write(LT=(self.left, self.content_overlap_top), RB=(self.right, self.content_overlap_bottom), image=checkBottom_match_image)
                else:
                    match_image = snapshot_write(LT=(self.left, self.content_overlap_top), RB=(self.right, self.content_overlap_bottom), image=swipe_before_image)

                if localRun:
                    snapshot_write(write_name=f"match_image{single_counter()}", image=match_image)
                if pos := snapshot_match((self.left, self.lastpage_content_top), (self.right, self.content_bottom), image=swipe_after_image, match_image=match_image):
                    pair_result, check_height = digit_pair([self.lastpage_content_top + self.lastpage_content_items_T2T * sc for sc in range(self.lastpage_content_items_rows + 1)]), pos[1] + self.lastpage_content_top
                    index = find_range_index(pair_result, check_height)
                    monitor_print(f"{pair_result=}, {check_height=}, {index=}")

                    lastpage_content_top = self.lastpage_content_top + self.lastpage_content_items_T2T * index
                    yield snapshot_write(LT=(self.left, lastpage_content_top), RB=(self.right, lastpage_content_bottom), image=swipe_after_image)
                else:
                    swipe_after_image_url = image_upload("swipe_after_image", swipe_after_image)[1]
                    match_image_url = image_upload("match_image", match_image)[1]
                    monitor_task_status_v2("ScrPreSwiGen match failed", f"{swipe_after_image_url}, {match_image_url}")
                    yield snapshot_write(LT=(self.left, self.lastpage_content_top), RB=(self.right, lastpage_content_bottom), image=swipe_after_image)
                monitor_task_status_v2("LongScreenshotPrecisionSwipeGenerator 结束", f"滑动{sc}次")
                break
        else:
            if self.swipe_raise_ex:
                monitor_catch("超过滑动次数", status=10134, break_mode=BreakModeEnum.runloop)

class LongScreenshotSingleRowGenerator(LongScreenshotSingleRow):
    def __init__(self, **kwds):
        """
        长截图单行精准滑动生成器
        适用场景：一次滑一整行，内容区域为单行上下间隔一致，最后一页无需 match 拼接
        :param left
        :param right
        :param checkBottom_func
        :param qc_func
        :param content_top
        :param content_bottom
        :param lastpage_content_top
        :param lastpage_content_bottom
        :param swipe_start_point
        :param swipe_delta_y
        :param swipe_offset
        :param swipe_raise_ex: 超过滑动次数后抛异常
        :param is_hold
        """
        self.lastpage_content_bottom = kwds.get("lastpage_content_bottom")
        self.is_bottom = kwds.get("is_bottom")  # match判底方法专用
        self.desc = desc_format2(kwds.get("desc"))
        self.current_sc = 0  # 当前滑动次数
        super().__init__(**kwds)

    def __call__(self, *args, **kwargs):
        # 滑动方式
        if isiOS:
            sp = lambda: air_swipe_fast(self.swipe_start_point, delta_y=swipe_delta_from_env(self.swipe_delta_y), duration=self.swipe_duration, sec=self.swipe_sec)
        elif self.swipe_mode == "poco":
            sp = lambda: SwipePoco(self.swipe_start_point, delta_y=swipe_delta_from_env(self.swipe_delta_y), sec=self.swipe_sec)
        else:
            sp = lambda: SwipeAirtest(
                self.swipe_start_point,
                delta_y=swipe_delta_from_env(self.swipe_delta_y),
                offset=self.swipe_offset,
                duration=self.swipe_duration,
                hold_sec=self.swipe_hold_sec,
                sec=self.swipe_sec
            )
        swipe_before_image = snapshot_hq(self.qc_func)
        loop_break = False
        for sc in range(1, self.swipe_count + 1 if isinstance(self.swipe_count, int) else 80):
            self.current_sc = sc
            # 滑动判底截图
            if self.is_hold:
                with sp():
                    checkBottom_image = snapshot_write()
                if callable(self.swipe_func):
                    loop_break = self.swipe_func(self, sc)
                swipe_after_image = snapshot_hq(self.qc_func)
            else:
                spins = sp()
                if callable(spins): spins()
                if callable(self.swipe_func):
                    loop_break = self.swipe_func(self, sc)
                checkBottom_image = swipe_after_image = snapshot_hq(self.qc_func)

            # 停止滑动
            if loop_break:
                break

            checkBottom_value = self.checkBottom_func(swipe_before_image, checkBottom_image)
            if not checkBottom_value:
                yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=swipe_before_image)
                swipe_before_image = swipe_after_image
            # 最后一页
            else:
                # 仅在match判底方法使用
                if checkBottom_value != 2:
                    self.is_bottom = True
                    yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=swipe_before_image)

                lastpage_content_bottom = self.lastpage_content_bottom or (self.content_bottom - self.content_top + self.lastpage_content_top)
                yield snapshot_write(LT=(self.left, self.lastpage_content_top), RB=(self.right, lastpage_content_bottom), image=swipe_after_image)
                monitor_task_status_v2("LongScreenshotSingleRowGenerator 结束", f"滑动{sc}次")
                break
        else:
            if self.swipe_raise_ex:
                monitor_catch("超过滑动次数", status=10134, break_mode=BreakModeEnum.runloop)

class LongScreenshotLiteGenerator(LongScreenshotLite):
    def __init__(self, **kwds):
        """
        长截图有限次数精准滑动生成器
        适用场景：滑动页数确定，最后一页无需 match 拼接
        :param left
        :param right
        :param qc_func
        :param content_top
        :param content_bottom
        :param lastpage_content_top
        :param lastpage_content_bottom
        :param swipe_start_point
        :param swipe_delta_y
        :param swipe_count
        :param swipe_offset
        """
        self.lastpage_content_bottom = kwds.get("lastpage_content_bottom")
        super().__init__(**kwds)

    def __call__(self, *args, **kwargs):
        lastpage_content_bottom = self.lastpage_content_bottom or (self.content_bottom - self.content_top + self.lastpage_content_top)
        # 只有一页
        if self.swipe_count == 0:
            yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, lastpage_content_bottom), image=snapshot_hq(self.qc_func))
        # 存在多页
        else:
            for _ in range(self.swipe_count):
                yield snapshot_write(LT=(self.left, self.content_top), RB=(self.right, self.content_bottom), image=snapshot_hq(self.qc_func))
                SwipeAirtest(self.swipe_start_point, swipe_delta_from_env(self.swipe_delta_y), offset=self.swipe_offset, duration=self.swipe_duration)()
            else:
                # 最后一页
                yield snapshot_write(LT=(self.left, self.lastpage_content_top), RB=(self.right, lastpage_content_bottom), image=snapshot_hq(self.qc_func))

class ScreenshotRename:
    def __init__(self):
        """
        图片重命名，添加时间戳，排序
        """
        self.filesList = glob(OPJ(ST.LOG_DIR, "adc_result_*_$*.jpg"))

    def filename_split(self, old_filename):
        filename = OP.splitext(old_filename)[0]
        filename_split_list = filename.split("_")
        s1, s2 = filename_split_list[-2:]
        serial = int(s1) if s1.isdigit() else 0
        id_str = s2.strip("$")
        id_int = int(id_str) if id_str.isdigit() else 0
        new_filename = f"{'_'.join(filename_split_list[:-1])}"
        return old_filename, new_filename, id_int, serial

    def online(self, sorted_filesList):
        for old_filename, new_filename, *args in sorted_filesList:
            ext = OP.splitext(old_filename)[1]
            new_filename += f"_{timeStamp()}{ext}"
            os.rename(old_filename, new_filename)

    def offline(self, sorted_filesList):
        for old_filename, new_filename, id_int, serial in sorted_filesList:
            path, name = OP.split(new_filename)
            name_split = name.split("_")
            if name_split[-1].isdigit(): name = "_".join(name_split[:-1])
            ext = OP.splitext(old_filename)[1]
            new_filename = OPJ(path, f"{id_int}_{serial}_{name}{ext}")
            os.rename(old_filename, new_filename)

    def __call__(self, *args, **kwds):
        sorted_filesList = list(map(self.filename_split, self.filesList))
        sorted_filesList.sort(key=lambda item: item[-2:])
        if localRun:
            self.offline(sorted_filesList)
        else:
            self.online(sorted_filesList)

def screen_bombing(LT, RB, spacing=10, mode="col"):
    """
    屏幕轰炸
    :param LT:
    :param RB:
    :param spacing:
    :param mode:
    :return:
    """
    X = range(LT[0] + spacing // 2, RB[0], spacing or 1)
    Y = range(LT[1] + spacing // 2, RB[1], spacing or 1)
    if mode.startswith("c"):
        for y, x in itertools.product(Y, X): yield air_touch((x, y), sec=0.5)
    elif mode.startswith("r"):
        for x, y in itertools.product(X, Y): yield air_touch((x, y), sec=0.5)

class SwipeAirtest:
    def __init__(self, start_point, delta_y=0.0, delta_x=0.0, end_point=None, offset=None, duration=0.5, steps=None, hold_sec=0.5, sec=0.5):
        """
        Airtest滑动
        :param start_point: 开始点
        :param delta_y: 滑动距离Y
        :param delta_x: 滑动距离X
        :param end_point: 结束点
        :param offset: 滑动偏移
        :param duration: 滑动的持续时间
        :param hold_sec: 滑动到结尾保持的秒数
        :param sec: 滑动后等待的秒数
        :param steps: 滑动步数
        :return:
        """
        self.start_point = start_point
        self.delta_y = delta_y
        self.delta_x = delta_x
        self.hold_sec = hold_sec
        self.sec = sec
        self.offset = offset
        self.duration = duration
        self.steps = steps
        self.__start_point = None
        self.__end_point = None
        self.orientation = DEV.display_info["orientation"]
        self.screen_vertical = self.orientation in (1, 3)

        if end_point and isinstance(end_point, (List, Tuple)):
            self.delta_y = end_point[1] - self.start_point[1]
            self.delta_x = end_point[0] - self.start_point[0]

    @staticmethod
    def __screen_size():
        return DEV.get_current_resolution()

    def __screen_half(self):
        screen_size = self.__screen_size()
        return int(screen_size[0] / 2), int(screen_size[1] / 2)

    def processing(self):
        # 竖屏
        if self.screen_vertical:
            screen_half = self.__screen_half()
            self.__start_point = self.start_point[1], screen_half[0] - self.start_point[0] + screen_half[0]

            if any((self.delta_x, self.delta_y)):
                if self.orientation == 1:
                    self.__start_point = screen_half[1] - self.start_point[1] + screen_half[1], self.start_point[0]
                    __delta_x = -self.delta_x
                    __delta_y = self.delta_y
                    if self.offset: self.offset = -self.offset
                else:
                    __delta_x = self.delta_x
                    __delta_y = -self.delta_y
                self.__end_point = self.__start_point[0] - __delta_y, self.__start_point[1] - __delta_x

        # 横屏
        else:
            if any((self.delta_x, self.delta_y)):
                if self.orientation == 2:
                    screen_size = self.__screen_size()
                    self.start_point = screen_size[0] - self.start_point[0], screen_size[1] - self.start_point[1]
                    __delta_x = -self.delta_x
                    __delta_y = -self.delta_y
                    if self.offset: self.offset = -self.offset
                    self.__end_point = self.start_point[0] + __delta_x, self.start_point[1] + __delta_y
                else:
                    self.__end_point = self.start_point[0] + self.delta_x, self.start_point[1] + self.delta_y

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
        from_x, from_y = self.__start_point or self.start_point
        to_x, to_y = self.__end_point

        if self.offset and isinstance(self.offset, int):
            offset_end_point = (to_x, to_y)
            # 横屏向上滑动
            if not self.screen_vertical and self.delta_y < 0:
                offset_end_point = (to_x, to_y - self.offset)
            # 横屏向下滑动
            elif not self.screen_vertical and self.delta_y > 0:
                offset_end_point = (to_x, to_y + self.offset)
            # 横屏向左滑动
            elif not self.screen_vertical and self.delta_x < 0:
                offset_end_point = (to_x - self.offset, to_y)
            # 横屏向右滑动
            elif not self.screen_vertical and self.delta_x > 0:
                offset_end_point = (to_x + self.offset, to_y)

            # 竖屏向上滑动
            elif self.screen_vertical and self.delta_y < 0:
                offset_end_point = (to_x - self.offset, to_y)
            # 竖屏向下滑动
            elif self.screen_vertical and self.delta_y > 0:
                offset_end_point = (to_x + self.offset, to_y)
            # 竖屏向左滑动
            elif self.screen_vertical and self.delta_x < 0:
                offset_end_point = (to_x, to_y + self.offset)
            # 竖屏向右滑动
            elif self.screen_vertical and self.delta_x > 0:
                offset_end_point = (to_x, to_y - self.offset)

            self.__swipe_along([(from_x, from_y), (to_x, to_y), offset_end_point], duration=self.duration or 0.5, steps=self.steps or 5)
        else:
            self.__swipe_along([(from_x, from_y), (to_x, to_y)], duration=self.duration or 0.5, steps=self.steps or 5)

    # 放开
    def up(self):
        DEV.touch_proxy.perform([UpEvent(0), SleepEvent(self.sec)])

    def reset(self):
        self.delta_x = 0
        self.delta_y = 0

    def __enter__(self):
        self.down_swipe()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.up()

    def __call__(self, start_point=None, delta_y=0.0, delta_x=0.0, hold_sec=None, sec=None):
        if start_point: self.start_point = start_point
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

class Joystick:
    def __init__(self, centre, radius=0, angle=0, hold_sec=0):
        """
        游戏摇杆
        :param centre:
        :param radius:
        :param angle:
        :param hold_sec:
        """
        self.sa = None
        self.centre = centre
        self.radius = radius
        self.angle = -angle
        self.hold_sec = hold_sec

    def processing(self):
        x = int(self.centre[0] + self.radius * math.cos(math.radians(self.angle)))
        y = int(self.centre[1] + self.radius * math.sin(math.radians(self.angle)))
        self.sa = SwipeAirtest(self.centre, end_point=(x, y), hold_sec=self.hold_sec)

    def __enter__(self):
        self.processing()
        self.sa.down_swipe()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sa.up()

    def __call__(self, centre=None, radius=None, angle=None, hold_sec=0):
        if centre: self.centre = centre
        if radius: self.radius = radius
        if angle: self.angle = -angle
        self.processing()
        self.sa.down_swipe()
        if hold_sec: sleep(hold_sec)
        self.sa.up()

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
            track = track.start(pos_conver(self.start_point, mode="rel"))
            track = track.move(pos_conver(self.end_point, mode="rel"))
            track = track.hold(self.hold_sec)
        else:
            track = MotionTrackSuper([pos_conver(self.end_point, mode="rel")])
            # track = track.hold(self.sec)
        poco.apply_motion_tracks([track], accuracy=0.04)

    def reset(self):
        self.delta_x = 0
        self.delta_y = 0
        self.end_point = None

    def down_swipe(self):
        self.processing("down")

    def up(self):
        self.processing("up")
        sleep(self.sec)

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

def air_swipe_fast(
        start_point,
        delta_y=0,
        delta_x=0,
        end_point=None,
        offset=None,
        duration=None,
        steps=None,
        hold_sec=0.5,
        sec=0.5):
    """
    air快速滑动,先滑动delta_y，再滑动delta_x。
    end_point如果有，就重新计算delta_x,delta_y。
    :param start_point: 开始点
    :param delta_y: 滑动距离Y
    :param delta_x: 滑动距离X
    :param end_point: 结束点
    :param offset: 滑动偏移
    :param duration: 滑动持续时间
    :param steps: 滑动步数
    :param hold_sec: 滑动到结尾保持的秒数
    :param sec: 滑动后等待的秒数
    :return:
    """

    if isAndroid:
        SwipeAirtest(
            start_point,
            delta_y=delta_y,
            delta_x=delta_x,
            end_point=end_point,
            offset=offset,
            duration=duration or 0.5,
            hold_sec=hold_sec,
            sec=sec,
            steps=steps or 5)()
    else:
        if not end_point and any((delta_x, delta_y)):
            end_point = start_point[0] + delta_x, start_point[1] + delta_y
        adc_swipe(
            start_point,
            end_point,
            duration=duration or 1.0,
            steps=steps or 10,
            hold_sec=hold_sec,
            sec=sec or 0.1)

def poco_swipe_fast(start_point, delta_y=0.0, delta_x=0.0, end_point=None, sec=1):
    """
    poco快速滑动
    :param start_point:
    :param delta_y:
    :param delta_x:
    :param end_point:
    :param sec:
    :return:
    """
    if not end_point and any((delta_x, delta_y)):
        end_point = start_point[0] + delta_x, start_point[1] + delta_y
    poco.swipe(pos_conver(start_point, mode="rel"), pos_conver(end_point, mode="rel"), duration=0.5)
    sleep(sec)

def adb_swipe_fast(start_point, end_point, sec=1):
    """
    adb快速滑动
    :param start_point:
    :param end_point:
    :param sec:
    :return:
    """
    shell(f"input swipe {start_point[0]} {start_point[1]} {end_point[0]} {end_point[1]} {sec * 1000}")

def filename_extract(filename):
    if isinstance(filename, Template):
        filename = filename.filename
    elif isinstance(filename, Dict):
        filename = format_print(dict(map(lambda x: (x[0], x[1].filename if isinstance(x[1], Template) else x[1]), filename.items())))
    elif isinstance(filename, (List, Tuple)):
        filename = format_print(tuple(map(lambda x: x.filename if isinstance(x, Template) else x, filename)))
    return filename

def __air_exists_process(filename, image, threshold):
    """图片批量识别"""
    pos = None
    if not isinstance(image, np.ndarray):
        image = screenshot()
    if isinstance(filename, (Tuple, List)):
        for v in filename:
            if pos := adc_exists_with_image(v, image, threshold=threshold):
                filename = v
                if isinstance(filename, Template):
                    filename = filename.filename
                os_env.update(air_exists_filename=str(filename))
                break

    elif isinstance(filename, Dict):
        for d, v in filename.items():
            if pos := adc_exists_with_image(v, image, threshold=threshold):
                desc, filename = d, v
                if isinstance(filename, Template):
                    filename = filename.filename
                os_env.update(air_exists_desc=str(d), air_exists_filename=str(filename))
                break

    elif isinstance(filename, (str, Template)):
        pos = adc_exists_with_image(filename, image, threshold=threshold)

    return pos

@add_basedir
def air_exists(
        filename: Union[Template, str, Tuple, List, Dict],
        timeout: Union[int, float]=None,
        interval: Union[int, float]=0.5,
        include_area=None,
        exclude_area=None,
        title=None,
        desc="",
        image=None,
        threshold=None,
        pre_func=None,
        exists_func=None,
        not_exists_func=None,
        printLog=True,
        catch=False,
        **kwds):
    """
    图片识别
    :param filename:
    :param timeout:
    :param interval:
    :param include_area: 包含区域
    :param exclude_area: 排除区域
    :param title:
    :param desc:
    :param image:
    :param threshold:
    :param pre_func:
    :param exists_func:
    :param not_exists_func:
    :param printLog:
    :param catch: 保存现场
    :return:
    """
    pos = None
    if isinstance(filename, Template) and not OP.isfile(filename.filepath):
        monitor_task_status_v2("air_exists function", f"{filename.filepath} not exists")
        return
    if callable(pre_func):
        pre_func()

    if isinstance(filename, (Tuple, List)) or isinstance(filename, Dict) or isinstance(image, np.ndarray):
        start_time = time.time()
        while True:
            if pos := __air_exists_process(filename, image, threshold):
                break
            elif not timeout or (isinstance(timeout, (int, float)) and (time.time() - start_time) > timeout):
                break
            elif isinstance(interval, (int, float)) and interval > 0:
                sleep(interval)
                image = screenshot()
            else:
                image = screenshot()

    else:
        if (isAndroid or isiOSCloud) and isinstance(filename, Template):
            if not getattr(filename, "resolution"):
                setattr(filename, "resolution", get_resolution())
            pos = lx_safe_wait(filename, timeout=timeout or 2, interval=interval or 1, printLog=False)
        else:
            try:
                pos = adc_wait(filename, timeout=timeout or 2, interval=interval or 1)
            except TargetNotFoundError:
                ...

    if (pos and include_area and not pos_in_area(pos, include_area)) or \
        (pos and exclude_area and pos_in_area(pos, exclude_area)):
        pos = None

    if pos:
        if printLog:
            filename = filename_extract(filename)
            if title and desc:
                monitor_task_status_v2(title, f"{desc} {pos} {filename}")
                if catch:
                    monitor_catch(title, f"{desc} {pos}", printLog=False)
            else:
                monitor_print(font_blue + f"air_exists: {pos}{f'{desc_format(desc)} {filename}' if desc else f' {filename}'}" + font_reset)
        if callable(exists_func):
            exists_func()
        return pos
    else:
        if printLog:
            filename = filename_extract(filename)
            monitor_print(font_red + f"air_exists: {f'null{desc_format(desc)} {filename}' if desc else f'null {filename}'}" + font_reset)
        if callable(not_exists_func):
            not_exists_func()

def air_touch(
        pos: Union[Tuple, List],
        sec: Union[int, float]=1,
        offset=(0, 0),
        combo=1,
        title=None,
        desc="",
        pre_func=None,
        touch_after_func=None,
        printLog=True,
        catch=False,
        pm=None,
        **kwds):
    """
    Airtest点击
    :param pos: 位置
    :param offset: 位置偏移
    :param sec: 点击后等待
    :param combo: 连击
    :param title: 标题
    :param desc: 描述
    :param pre_func: 前置操作
    :param touch_after_func: 点击后行为
    :param printLog: 输出日志
    :param catch: 保存现场
    :param pm: x & y pos ±
    :return: 无
    """
    pos = (pos[0] + offset[0], pos[1] + offset[1])
    if callable(pre_func):
        pre_func()

    pos = tuple(map(int, pos))
    pos_str = str(pos)
    for i in range(combo):
        if pm:
            pos_ = random_pos(pos, pm=pm)
            if isinstance(pm, int) and pm > 0:
                pos_str = f"({pos[0]}±{pm}, {pos[1]}±{pm})"
            elif isinstance(pm, (List, Tuple)) and len(pm) >= 2:
                pos_str = f"({pos[0]}±{pm[0]}, {pos[1]}±{pm[1]})"
        else:
            pos_ = pos
        sec_ = random.uniform(0.2, 0.3) if i < combo - 1 else 0
        adc_touch(pos_, sec=sec_, printLog=False)

    if printLog:
        if title and desc:
            monitor_task_status_v2(title, f"{desc} {pos_str}")
        else:
            monitor_print(font_white + f"air_touch: {pos_str}{desc_format(desc)}" + font_reset)
    sleep(sec)
    if catch:
        if title and desc:
            monitor_catch(title, f"{desc} {pos_str}", printLog=False)
        elif title or desc:
            monitor_catch(f"{title}{desc} {pos_str}", printLog=False)
        else:
            monitor_catch(f"点击 {pos_str}", printLog=False)
    if callable(touch_after_func):
        touch_after_func()

    return pos

@add_basedir
def air_exists_touch(
        filename: Union[Template, str, Tuple, List, Dict],
        alt_v: Union[Tuple, List]=None,
        timeout: Union[int, float]=None,
        interval: Union[int, float]=0.5,
        include_area=None,
        exclude_area=None,
        sec: Union[int, float]=1,
        offset=(0, 0),
        combo=1,
        title=None,
        desc="",
        image=None,
        threshold=None,
        pre_func=None,
        exists_func=None,
        not_exists_func=None,
        touch_after_func=None,
        printLog=True,
        catch=False,
        pm=None,
        **kwds):
    """
    Airtest存在点击
    :param filename:
    :param alt_v:
    :param timeout:
    :param interval:
    :param include_area: 包含区域
    :param exclude_area: 排除区域
    :param sec:
    :param offset:
    :param combo:
    :param title:
    :param desc:
    :param image:
    :param threshold:
    :param pre_func:
    :param exists_func:
    :param not_exists_func:
    :param touch_after_func:
    :param printLog:
    :param catch: 保存现场
    :param pm: x & y pos ±
    :return:
    """
    if callable(pre_func):
        pre_func()
    if pos := air_exists(
            filename,
            timeout,
            interval=interval,
            include_area=include_area,
            exclude_area=exclude_area,
            image=image,
            threshold=threshold,
            exists_func=exists_func,
            not_exists_func=not_exists_func,
            printLog=False):
        pos = alt_v or pos
        pos = (pos[0] + offset[0], pos[1] + offset[1])
        air_touch(pos, 0, combo=combo, touch_after_func=touch_after_func, printLog=False, pm=pm)
        if printLog:
            if desc_ := os_env.get("air_exists_desc"):
                desc = desc_
                os_env.pop("air_exists_desc", None)
            if filename_ := os_env.get("air_exists_filename"):
                filename = filename_
                os_env.pop("air_exists_filename", None)

            filename = filename_extract(filename)
            if title and desc:
                monitor_task_status_v2(title, f"{desc} {pos} {filename}")
            else:
                monitor_print(font_blue + f"air_exists_touch: {pos}{f'{desc_format(desc)} {filename}' if desc else f' {filename}'}" + font_reset)
        sleep(sec)
        if catch:
            if title and desc:
                monitor_catch(title, f"{desc} {pos}", printLog=False)
            elif title or desc:
                monitor_catch(f"{title}{desc} {pos}", printLog=False)
            else:
                monitor_catch(f"点击 {pos}", printLog=False)

        return pos

    elif printLog:
        filename = filename_extract(filename)
        monitor_print(font_red + f"air_exists_touch: {f'null{desc_format(desc)} {filename}' if desc else f'null {filename}'}" + font_reset)

# Poco点击
def poco_touch(
        pos: Union[Tuple, List],
        sec: Union[int, float]=1,
        combo=1,
        title=None,
        desc="",
        touch_after_func=None,
        printLog=True):
    for i in range(combo):
        poco.click(pos_conver(pos, mode="rel"))
        if i < combo - 1: sleep(0.1)
    if printLog:
        if title and desc:
            monitor_task_status_v2(title, f"{desc} {pos}")
        else:
            monitor_print(font_white + f"poco_touch: {pos}{desc_format(desc)}" + font_reset)
    sleep(sec)
    if callable(touch_after_func):
        touch_after_func()

# Poco存在点击
@add_basedir
def poco_exists_touch(
        filename: Template,
        alt_v: Union[Tuple, List]=None,
        timeout: Union[int, float]=None,
        sec: Union[int, float]=1,
        offset=(0, 0),
        combo=1,
        title=None,
        desc="",
        exists_func=None,
        not_exists_func=None,
        touch_after_func=None,
        printLog=True,
        **kwds):
    if pos := air_exists(filename, timeout, exists_func=exists_func, not_exists_func=not_exists_func, printLog=False):
        pos_ = alt_v or pos
        pos_ = (pos_[0] + offset[0], pos_[1] + offset[1])
        poco_touch(pos_, 0, combo=combo, touch_after_func=touch_after_func, printLog=False)
        if printLog:
            if title and desc:
                monitor_task_status_v2(title, f"{desc} {pos}")
            else:
                monitor_print(font_blue + f"poco_exists_touch: {pos}{f'{desc_format(desc)} {filename}' if desc else f' {filename}'}" + font_reset)
        sleep(sec)
        return pos
    elif printLog:
        monitor_print(font_red + f"poco_exists_touch: {f'null{desc_format(desc)} {filename}' if desc else f'null {filename}'}" + font_reset)

# Adb点击
def adb_touch(
        pos: Union[Tuple, List],
        sec: Union[int, float]=1,
        combo=1,
        title=None,
        desc="",
        touch_after_func=None,
        printLog=True,
        **kwds):
    for i in range(combo):
        touchFunc = lambda: shell(f"input tap {pos[0]} {pos[1]}")
        lx_safe_touch(pos, sec=0, printLog=False, touchFunc=touchFunc)
        if i < combo - 1: sleep(0.1)
    if printLog:
        if title and desc:
            monitor_task_status_v2(title, f"{desc} {pos}")
        else:
            monitor_print(font_white + f"adb_touch: {pos}{desc_format(desc)}" + font_reset)
    sleep(sec)
    if callable(touch_after_func):
        touch_after_func()

# Adb存在点击
@add_basedir
def adb_exists_touch(
        filename: Template,
        alt_v: Union[Tuple, List]=None,
        timeout: Union[int, float]=None,
        interval=None,
        sec: Union[int, float]=1,
        offset=(0, 0),
        combo=1,
        title=None,
        desc="",
        exists_func=None,
        not_exists_func=None,
        touch_after_func=None,
        printLog=True,
        **kwds):
    if pos := air_exists(filename, timeout, interval=interval, exists_func=exists_func, not_exists_func=not_exists_func, printLog=False):
        pos_ = alt_v or pos
        pos_ = (pos_[0] + offset[0], pos_[1] + offset[1])
        adb_touch(pos_, 0, combo=combo, touch_after_func=touch_after_func, printLog=False)
        if printLog:
            if title and desc:
                monitor_task_status_v2(title, f"{desc} {pos}")
            else:
                monitor_print(font_blue + f"adb_exists_touch: {pos}{f'{desc_format(desc)} {filename}' if desc else f' {filename}'}" + font_reset)
        sleep(sec)
        return pos
    elif printLog:
        monitor_print(font_red + f"adb_exists_touch: {f'null{desc_format(desc)} {filename}' if desc else f'null {filename}'}" + font_reset)

# 存在点击上下文
@add_basedir
class ExistsTouch:
    def __init__(
            self,
            filename: Template,
            alt_v: Union[Tuple, List]=None,
            timeout: Union[int, float]=None,
            sec: Union[int, float]=1,
            offset=(0, 0),
            title=None,
            desc="",
            exists_func=None,
            not_exists_func=None,
            touch_after_func=None,
            printLog=True,
            mode="airtest"):
        self.filename = filename
        self.alt_v = alt_v
        self.timeout = timeout
        self.sec = sec
        self.offset = offset
        self.title = title
        self.desc = desc
        self.exists_func = exists_func
        self.not_exists_func = not_exists_func
        self.touch_after_func = touch_after_func
        self.printLog = printLog

        self.pos = None
        self.mode_name = "Air"
        self.touch_mode = air_touch
        self.exists_touch_mode = air_exists_touch
        if mode == "poco":
            self.mode_name = "Poco"
            self.touch_mode = poco_touch
            self.exists_touch_mode = poco_exists_touch
        elif mode == "adb":
            self.mode_name = "Adb"
            self.touch_mode = adb_touch
            self.exists_touch_mode = adb_exists_touch

    def __enter__(self):
        self.pos = air_exists(self.filename, self.timeout, exists_func=self.exists_func, not_exists_func=self.not_exists_func, printLog=False)
        if self.pos:
            return self.pos
        elif self.printLog:
            monitor_print(font_red + f"{self.mode_name}ExistsTouch: {f'null {self.filename}{desc_format(self.desc)}' if self.desc else f'null {self.filename}'}" + font_reset)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pos:
            pos_ = self.alt_v or self.pos
            pos_ = (pos_[0] + self.offset[0], pos_[1] + self.offset[1])
            self.touch_mode(pos_, 0, touch_after_func=self.touch_after_func, printLog=False)
            if self.printLog:
                if self.title and self.desc:
                    monitor_task_status_v2(self.title, self.desc)
                else:
                    monitor_print(font_blue + f"{self.mode_name}ExistsTouch: {self.pos} {self.filename}{f'{desc_format(self.desc)}' if self.desc else ''}" + font_reset)
            sleep(self.sec)

@add_basedir
def find_tpl(
        filename: Union[str, Template, np.array, Path]=None,
        area=None,
        lt=None,
        rb=None,
        width=None,
        height=None,
        timeout: Union[int, float]=0,
        interval: Union[int, float]=1,
        threshold=0.72,
        target_pos=TargetPosEnum.center,
        title=None,
        desc="",
        write_name=None,
        image=None,
        printLog=True,
        catch=False,
        **kwds):
    """
    找到 template 位置
    :param filename: 模板
    :param area: 包含区域
    :param lt: 左上
    :param rb: 右下
    :param width: 宽度
    :param height: 高度
    :param timeout: 超时
    :param interval: 识别间隔
    :param threshold: 相似度阈值
    :param target_pos: 目标位置
    :param title: 标题
    :param desc: 描述
    :param write_name: 保存名称
    :param image: 图像
    :param printLog: 打印日志
    :param catch: 保存现场
    :return: pos
    """
    if not isinstance(image, np.ndarray):
        image = screenshot()

    start_time = time.time()
    while True:
        if pos := snapshot_match(
            LT=lt,
            RB=rb,
            width=width,
            height=height,
            area=area,
            match_image=filename,
            image=image,
            write_name=write_name,
            threshold=threshold,
            target_pos=target_pos,
            absolute_pos=True,
            desc=desc,
            printLog=False):
            break
        elif not timeout or (isinstance(timeout, (int, float)) and (time.time() - start_time) > timeout):
            break
        elif isinstance(interval, (int, float)) and interval > 0:
            sleep(interval)
            image = screenshot()
        else:
            image = screenshot()

    if printLog:
        match_score = os_env.get("match_score")
        match_score = f" score: {float(match_score):.2f}" if match_score else ""
        os_env.pop("match_score", None)
        f_desc = f"{desc_format(desc)}" if desc else ""
        if isinstance(filename, np.ndarray):
            filename = type(filename).__name__
        elif isinstance(filename, Template):
            filename = filename.filename
            filename = Path(filename).name
        elif isinstance(filename, (Path, str)):
            filename = Path(filename).name

        if pos:
            if title and desc:
                monitor_task_status_v2(title, f"{desc} {pos} {filename}{match_score}".strip())
                if catch:
                    monitor_catch(title, f"{desc} {pos}", image=image, printLog=False)
            else:
                monitor_print(font_blue + f"find_tpl: {pos}{match_score}{f_desc} {filename}" + font_reset)

        else:
            monitor_print(font_red + f"find_tpl: null{match_score}{f_desc} {filename}")

    return pos

@add_basedir
def find_tpl_touch(
        filename: Union[str, Template, np.array, Path]=None,
        alt_pos: Union[Tuple, List]=None,
        area=None,
        lt=None,
        rb=None,
        width=None,
        height=None,
        offset=(0, 0),
        timeout: Union[int, float]=0,
        sec: Union[int, float]=1,
        interval: Union[int, float]=0.5,
        threshold=0.72,
        combo=1,
        title=None,
        desc="",
        write_name=None,
        image=None,
        printLog=True,
        catch=False,
        pm=None,
        **kwds):
    """
    找到 template 位置并点击
    :param filename: 模板
    :param alt_pos: 替代位置
    :param area: 包含区域
    :param lt: 左上
    :param rb: 右下
    :param width: 宽度
    :param height: 高度
    :param threshold: 相似度阈值
    :param sec: 点击后等待
    :param timeout: 超时
    :param interval: 识别间隔
    :param offset: 偏移量(X,Y元组)
    :param combo: 点击次数
    :param title: 标题
    :param desc: 描述
    :param write_name: 保存名称
    :param image: 图像
    :param printLog: 打印日志
    :param catch: 保存现场
    :param pm: x & y pos ±
    :return:
    """
    pos = find_tpl(
        filename,
        area=area,
        lt=lt,
        rb=rb,
        width=width,
        height=height,
        timeout=timeout,
        interval=interval,
        threshold=threshold,
        title=title,
        desc=desc,
        write_name=write_name,
        image=image,
        printLog=False)

    pos_ = pos
    if printLog:
        match_score = os_env.get("match_score")
        match_score = f" score: {float(match_score):.2f}" if match_score else ""
        os_env.pop("match_score", None)
        f_desc = f"{desc_format(desc)}" if desc else ""
        if isinstance(filename, np.ndarray):
            filename = type(filename).__name__
        elif isinstance(filename, Template):
            filename = filename.filename
            filename = Path(filename).name
        elif isinstance(filename, (Path, str)):
            filename = Path(filename).name

        if pos:
            if alt_pos:
                pos_ = (alt_pos[0] + offset[0], alt_pos[1] + offset[1])
            else:
                pos_ = (pos[0] + offset[0], pos[1] + offset[1])
            air_touch(pos_, 0, combo=combo, printLog=False, pm=pm)

            if any(offset) or alt_pos:
                if isinstance(pm, int) and pm > 0:
                    pos_str = f"{pos} -> ({pos_[0]}±{pm}, {pos_[1]}±{pm})"
                elif isinstance(pm, (List, Tuple)) and len(pm) >= 2:
                    pos_str = f"{pos} -> ({pos_[0]}±{pm[0]}, {pos_[1]}±{pm[1]})"
                else:
                    pos_str = f"{pos} -> {pos_}"
            else:
                if isinstance(pm, int) and pm > 0:
                    pos_str = f"({pos_[0]}±{pm}, {pos_[1]}±{pm})"
                elif isinstance(pm, (List, Tuple)) and len(pm) >= 2:
                    pos_str = f"({pos_[0]}±{pm[0]}, {pos_[1]}±{pm[1]})"
                else:
                    pos_str = f"{pos}"

            if title and desc:
                monitor_task_status_v2(title, f"{desc} {pos_str} {filename}{match_score}".strip())
            else:
                monitor_print(font_blue + f"find_tpl_touch: {pos_str}{match_score}{f_desc} {filename}" + font_reset)

            sleep(sec)
            if title and desc and catch:
                monitor_catch(title, f"{desc} {pos_str}", printLog=False)

        else:
            monitor_print(font_red + f"find_tpl_touch: null{match_score}{f_desc} {filename}")

    return pos_

@add_basedir
def find_tpl_touch_retimg(
        filename: Union[str, Template, np.array, Path]=None,
        alt_pos: Union[Tuple, List]=None,
        area=None,
        lt=None,
        rb=None,
        width=None,
        height=None,
        offset=(0, 0),
        timeout: Union[int, float]=0,
        sec: Union[int, float]=1,
        interval: Union[int, float]=0.5,
        threshold=0.72,
        combo=1,
        title=None,
        desc="",
        write_name=None,
        image=None,
        printLog=True,
        catch=False,
        pm=None,
        need_pos=False,
        **kwds):
    """
    找到 template 位置并点击返回新图像
    没有找到返回原图像
    :param filename: 模板
    :param alt_pos: 替代位置
    :param area: 包含区域
    :param lt: 左上
    :param rb: 右下
    :param width: 宽度
    :param height: 高度
    :param threshold: 相似度阈值
    :param sec: 点击后等待
    :param timeout: 超时
    :param interval: 识别间隔
    :param offset: 偏移量(X,Y元组)
    :param combo: 点击次数
    :param title: 标题
    :param desc: 描述
    :param write_name: 保存名称
    :param image: 图像
    :param printLog: 打印日志
    :param catch: 保存现场
    :param pm: x & y pos ±
    :param need_pos: 是否需要pos
    :return:
    """
    if not isinstance(image, np.ndarray):
        image = screenshot()
    locals_params = locals()
    locals_params.pop("kwds", None)
    if pos := find_tpl_touch(**locals_params):
        if need_pos:
            return screenshot(), pos
        return screenshot()
    elif need_pos:
        return image, None
    else:
        return image

def __find_text_process(text, area, image, model):
    find_text_result = {}
    if not isinstance(image, np.ndarray):
        image = screenshot()
    text_poses = ImageOcrRemote(area=area, image=image, model=model)() or ()

    if text and isinstance(text, str):
        find_text_result = default_dict(filter(lambda x: x[0] == text, text_poses))

    elif text and isinstance(text, (List, Dict, Tuple)):
        find_text_result = default_dict(filter(lambda x: x[0] in text, text_poses))

    elif not text:
        find_text_result = default_dict(text_poses) if text_poses else {}

    return find_text_result

def find_text(
        text: Union[str, List, Dict, Tuple]=None,
        area=None,
        timeout: Union[int, float]=0,
        interval: Union[int, float]=0.5,
        title=None,
        desc="",
        image=None,
        model=2,
        printLog=True,
        catch=False,
        **kwds):
    """
    找到图片中需要部分 text 的位置, 方法返回格式：{“识别内容”:(pos_x,pox_y), ...}
    这个地方由于返回的是绝对坐标，所以传递的图片大小如果和设备的大小不一样，就使用直接截图的操作，传递的图片就没用了
    :param text: 识别文字
    :param area: 包含区域
    :param timeout: 超时
    :param interval: 识别间隔
    :param title: 标题
    :param desc: 描述
    :param image: 图片
    :param model: 识别模型
    :param printLog: 打印日志
    :param catch: 保存现场
    :return: {“识别内容”:(pos_x,pox_y), ...}
    """
    start_time = time.time()
    while True:
        if find_text_result := __find_text_process(text, area, image, model):
            break
        elif not timeout or (isinstance(timeout, (int, float)) and (time.time() - start_time) > timeout):
            break
        elif isinstance(interval, (int, float)) and interval > 0:
            sleep(interval)
            image = screenshot()
        else:
            image = screenshot()

    if find_text_result:
        if printLog:
            if title and desc:
                monitor_task_status_v2(title, f"{desc} {format_print(find_text_result)}")
                if catch:
                    monitor_catch(title, f"{desc} {format_print(find_text_result)}", image=image, printLog=False)
            else:
                monitor_print(font_blue + f"find_text: {format_print(find_text_result)}{desc_format(desc)}" + font_reset)

        if text and isinstance(text, str):
            return find_text_result.popitem()[1]

    elif printLog:
        monitor_print(font_red + f"find_text: {f'null{desc_format(desc)} {text}' if desc else f'null {text}'}" + font_reset)
    return find_text_result

def find_text_touch(
        text: str,
        area=None,
        sec: Union[int, float]=1,
        timeout: Union[int, float]=0,
        interval: Union[int, float]=0.5,
        offset=(0, 0),
        combo=1,
        title=None,
        desc="",
        image=None,
        printLog=True,
        catch=False,
        **kwds):
    """
    找到 text 位置并点击
    :param text: 匹配文本
    :param area: 包含区域
    :param sec:
    :param timeout:
    :param interval:
    :param offset:
    :param combo:
    :param title:
    :param desc:
    :param image:
    :param printLog:
    :param catch: 保存现场
    :return:
    """
    if pos := find_text(
            text,
            area=area,
            timeout=timeout,
            interval=interval,
            title=title,
            desc=desc,
            image=image,
            printLog=False):
        pos = (pos[0] + offset[0], pos[1] + offset[1])
        air_touch(pos, 0, combo=combo, printLog=False)

        if printLog:
            if title:
                monitor_task_status_v2(title, f"{desc or f'点击{text}'} {pos}")
                if catch:
                    monitor_catch(title, f"{desc or f'点击{text}'} {pos}", printLog=False)
            else:
                monitor_print(font_blue + f"find_text_touch: {pos}{f'{desc_format(desc)} {text}' if desc else f' {text}'}" + font_reset)
        sleep(sec)
        return pos
    elif printLog:
        monitor_print(font_red + f"find_text_touch: {f'null{desc_format(desc)} {text}' if desc else f'null {text}'}" + font_reset)

# 任务异常
class TaskException(Exception):
    def __init__(self, title="未知错误", desc="", status: Union[str, int]=None, break_mode=None):
        self.title = title
        self.desc = desc
        self.status = status
        self.break_mode = break_mode

    def __str__(self):
        return "任务异常"

# 任务重试
class RetryDecorator:
    def __init__(self, retries=3, delay=1, exception_func=None):
        self.retries = retries
        self.delay = delay
        self.exception_func = exception_func

    def __call__(self, func):
        def wrapper(*args, **kwds):
            for i in range(1, self.retries + 1):
                try:
                    return func(*args, **kwds)
                except TaskException as e:
                    monitor_print(traceback.format_exc())
                    if i != self.retries:
                        if callable(self.exception_func): self.exception_func()
                        monitor_catch(e.title, f"{e.desc}，重试{i}")
                        sleep(self.delay)
                    else:
                        monitor_catch(e.title, e.desc, status=e.status, break_mode=e.break_mode)
        return wrapper

# 失败任务计数
task_failed_counter = CounterBase()
def failed_task_add1():
    if task_failed_counter() >= 5:
        monitor_task_status_v2("失败任务计数", "失败任务数量到达最大值")
        lx_break_runloop(desc="失败任务数量到达最大值")

# 错误属性值映射
rectify_data = {}
if OP.isfile(gameDir / "rectify.yaml"):
    with open(gameDir / "rectify.yaml", mode='r', encoding="utf8") as yaml_file:
        if yaml_data := yaml.load(yaml_file, Loader=yaml.FullLoader):
            rectify_data.update(yaml_data)
class Rectify:
    def __init__(self, map_name, isMatch=False):
        self.rectify_map = rectify_data.get(map_name)
        self.isMatch = isMatch

    def rectify(self, value_str):
        for wrong, right in self.rectify_map.items():
            wrong, right = str(wrong), str(right)
            if self.isMatch and value_str == wrong:
                return right
            elif not self.isMatch and right not in value_str and wrong in value_str:
                value_str = value_str.replace(wrong, right)
        return value_str

    def __call__(self, value):
        if self.rectify_map:
            if isinstance(value, (Dict, List)):
                return json.loads(self.rectify(json.dumps(value, ensure_ascii=False)))
            elif isinstance(value, str):
                return self.rectify(value)
        else:
            return value

class BreakModeEnum(Enum):
    runloop = "runloop"
    app = "app"

# 输出领域图片
def monitor_catch(
    title: str,
    desc="",
    filename="",
    printLog=True,
    return_text_image=False,
    status: Union[str, int]=None,
    break_mode: Union[str, Enum]=None,
    hold_game=False,
    image=None,
    write_catch_image=True,
    catch=True,
    raise_exception=True):
    """
    :param title: Title，会打在adc_catch的图片左上角
    :param desc: Describe，会打在adc_catch的图片左上角
    :param filename: Filename
    :param printLog: Print log
    :param return_text_image
    :param status: Error code
    :param break_mode: Raise exception, runloop or app
    :param hold_game: Hold game
    :param image: Numpy array image
    :param write_catch_image: Write catch image
    :param catch: Catch snapshop
    :param raise_exception: Raise exception
    :return: Numpy array image
    """
    if isinstance(status, str) and status.isdigit():
        status = int(status) if int(status) else None

    if catch:
        platform_pattern = re.compile(rf"（{platform}）|\({platform}\)")
        big_font = isAndroid or isiOSCloud or device_name in ["iPhone 12", "iPhone 13", "iPhone 14"]
        image = text_image = snapshot_write(image=image)
        try:
            text_image = image_multiline_text(
                image,
                f"{platform_pattern.sub('', title)}",
                font_size=45 if big_font else 28,
                textPoint=(15, 5) if big_font else (12, 5),
                shadow=1
            )
            if desc:
                text_image = image_multiline_text(
                    text_image,
                    platform_pattern.sub('', desc) if desc else "",
                    font_size=35 if big_font else 20,
                    textPoint=(15, 70) if big_font else (12, 45),
                    shadow=1
                )
            gameName_ = f" - {gameName}" if gameName else ""
            error_ = f' - Error {status}' if isinstance(status, int) else ''
            platform_ = f"{platform} common" if isCloudGame else platform
            platform_ = platform_.replace("common common", "common")
            text_image = image_multiline_text(
                text_image,
                text=f"{timeNowStr()} - {gameId}{gameName_} - {platform_} - {taskId}{error_}",
                font_size=25 if big_font else 18,
                textPoint=(15, image_size(text_image)[1] - 42) if big_font else (12, image_size(text_image)[1] - 32),
                shadow=1
            )
        except Exception:
            monitor_print(traceback.format_exc())

        if write_catch_image:
            filename = catch_name(f"{title}-{filename}") if filename else catch_name(title)
            snapshot_write(filename, image=text_image)
        # 返回带文字图片
        if return_text_image:
            image = text_image

    if raise_exception:
        if printLog:
            monitor_task_status_v2(title, desc, status if isinstance(status, int) else None)

        if isinstance(break_mode, Enum):
            break_mode = break_mode.value
        if break_mode == "runloop":
            if os.environ.get("thread_status") == "run": quit_thread()
            lx_break_runloop(f"{title}{f': {desc}' if desc else ''}")
        elif break_mode == "app" and str(status).isdigit():
            if os.environ.get("thread_status") == "run": quit_thread()
            lx_break_app(desc=f"{title}{f' - {desc}' if desc else ''}", ext_info={"key": str(status)}, hold_game=hold_game)

    return image

def monitor_catch_v2(
    title: str,
    desc="",
    status: Union[str, int]=None,
    break_mode: Union[str, Enum]=None,
    hold_game=False):
    """
    在日志中输出现场图片
    :param title: Title
    :param desc: Describe
    :param status: Error code
    :param break_mode: Raise exception, runloop or app
    :param hold_game: Hold game
    :return: None
    """
    if isinstance(status, str) and status.isdigit():
        status = int(status) if int(status) else None

    image = monitor_catch(
        title,
        desc,
        printLog=False,
        return_text_image=True,
        status=status,
        write_catch_image=False,
        raise_exception=False)
    imageUrl = image_upload('catch', image=image)[1]
    status = status if isinstance(status, int) else None
    monitor_task_status_v2(title, f"{desc}：{imageUrl}", status)

    if isinstance(break_mode, Enum):
        break_mode = break_mode.value
    if break_mode == "runloop":
        if os.environ.get("thread_status") == "run": quit_thread()
        lx_break_runloop(f"{title}{f': {desc}' if desc else ''}")
    elif break_mode == "app" and str(status).isdigit():
        if os.environ.get("thread_status") == "run": quit_thread()
        lx_break_app(desc=f"{title}{f': {desc}' if desc else ''}", ext_info={"key": str(status)}, hold_game=hold_game)

# 拖拽悬浮球
def float_ball(drag_to=(0, get_resolution()[1]), drop_mode="poco", safe_area=None, after_func=None):
    if poco is None:
        monitor_task_status_v2("拖拽悬浮球", f"poco is disenable")
        return True

    try:
        ball = None
        if platform == "3011":
            ball = poco(nameMatches="^.+:id/xt_root_float$")

        elif platform == "guopan":
            ball = poco(nameMatches="^.+:id/small_point_layout$")

        elif platform in ["4399", "4399box"]:
            ball = poco("android.view.View")

        elif platform in ["jiuyou", "xiyou", "xiaomi", "37shouyou"]:
            ball = poco("android.widget.ImageView")
            # drag_to = (1200, 1190)

        elif platform == "huawei":
            ball = poco(nameMatches="^.+:id/small_window_layout$")

        elif platform == "oppo":
            ball = poco(nameMatches="^.+:id/float_label")

        elif platform == "vivo":
            ball = poco(nameMatches="^.+:id/float_view_append")

        elif platform == "meizu":
            ball = poco("com.meizu.gamecenter.service:id/circle_percent_progress")

        elif platform == "nubiya":
            ball = poco("cn.nubia.nbgame:id/iv_little_worm")

        elif platform == "leidian":
            ball = poco("android.widget.FrameLayout")

        elif platform == "chongchong":
            ball = poco(nameMatches="^.+:id/lion_layout_floating_icon")

        elif platform == "dianchu":
            ball = poco(nameMatches="^.+:id/float_ball_icon")

        elif platform == "xiao7":
            ball = poco("android.view.ViewGroup")

        elif platform == "chuangyue":
            ball = poco(nameMatches="^.+:id/cs_iv_float")

        # elif __platform_tmp == "360": ball = poco("com.qihoo.gamecenter.pluginapk:id/base_icon_view")
        # elif __platform_tmp == "qq": ball = poco(nameMatches="^.+:")

        if safe_area:
            area_left, area_top = pos_conver(safe_area[:2], mode="rel")
            area_right, area_bottom = pos_conver(safe_area[2:], mode="rel")
            monitor_print(f"---ball安全区域：{area_left, area_top, area_right, area_bottom}")
        else:
            area_left = area_top = area_right = area_bottom = None

        if not property_read("float_ball") and ball is not None and ball.exists():
            for item in ball:
                start_point_normal = tuple(item.get_position())
                monitor_print(f"---ball坐标：{start_point_normal}")
                if start_point_normal != (0.5, 0.5) and not pos_in_area(start_point_normal, (area_left, area_top, area_right, area_bottom)):
                    start_point_normal = (start_point_normal[0] if start_point_normal[0] > 0 else 0.005, start_point_normal[1] if start_point_normal[1] > 0 else 0.005)
                    start_point_normal = (start_point_normal[0] if start_point_normal[0] < 1 else 0.995, start_point_normal[1] if start_point_normal[1] < 1 else 0.995)
                    resolution = get_resolution()
                    start_point = int(start_point_normal[0] * resolution[0]), int(start_point_normal[1] * resolution[1])

                    monitor_catch("拖拽悬浮球", f"拖拽前：{start_point}")
                    if drop_mode=="poco":
                        poco.swipe(start_point_normal, pos_conver(drag_to, mode="rel"), duration=1)
                    elif drop_mode=="air":
                        air_swipe_fast(start_point, end_point=drag_to)
                    elif drop_mode=="adb":
                        adb_swipe_fast(start_point, end_point=drag_to)
                    sleep(2)
                    monitor_catch("拖拽悬浮球", f"拖拽后：{start_point} -> {drag_to}（{platform}）")
                    property_write(float_ball="true")
                    if callable(after_func):
                        after_func()
                    return True

    except Exception:
        monitor_task_status_v2("拖拽悬浮球失败", traceback.format_exc())

# 子线程
def child_thread():
    ...

# 退出子线程
def quit_thread():
    os.environ.update(thread_status="wait")
    monitor_task_status_v2("子线程", '等待子线程退出')
    for i in range(60):
        if os.environ.get("thread_status") == "stop":
            os.environ.update(thread_status="run")
            break
        sleep(1)

# 下载服务器列表
def download_server_list(gameId, clientId):
    if isProd:
        host = 'adc-pc.alibaba-inc.com'
    else:
        host = 'pre-adc-pc.alibaba-inc.com'
    url = f"http://{host}/task/searchServerListV3"
    payload = {
        "gameId": gameId,
        "clientId": clientId,
        "scene": 1,
        "page": 1,
        "pageSize": 1000
    }

    server_list = []
    for page in itertools.count(1):
        payload["page"] = page
        res = requests.post(url, json=payload, verify=False)
        data = "{}"
        try:
            data = res.json().get("data")
        except Exception as e:
            monitor_catch("下载服务器列表", f"接口返回错误: {e}", status=10164, catch=False)

        if single_page_server_list := json.loads(data).get("result"):
            server_list.extend(single_page_server_list)
        else:
            return server_list

def update_server_list(game_id, platform, client_id, delta_qufu_data, image_list=None, status=0):
    """更新服务器列表"""
    if isProd:
        host = 'adc-pc.alibaba-inc.com'
    else:
        host = 'pre-adc-pc.alibaba-inc.com'
    url = f"http://{host}/task/uploadQufuUpdateData"
    payload = {
        "game_id": game_id,
        "game_platform": platform,
        "game_client_id": client_id,
        "delta_qufu_data": delta_qufu_data,
        "image_list": image_list or [],
        "status": status,
    }
    res = requests.post(url, json=payload, verify=False)
    try:
        return res.json()
    except Exception as e:
        monitor_catch("更新服务器列表", f"接口返回错误: {e}", status=10164, catch=False)

def upload_propreties(data, images=None, status=0):
    """上传新增属性到ADC平台"""
    if isinstance(data, Dict):
        data = [data]
    if not images:
        images = []
    elif isinstance(images, str):
        images = [images]
    elif isinstance(images, np.ndarray):
        images = [image_upload(image=images)[1]]
    [x.pop("imageUrl", None) for x in data]
    upload_propreties_with_data(
        game_id=gameId,
        game_platform=platform,
        data=data,
        images=images,
        addParams=True,
        isFromCollectTask=True,
        isNeedShenpi=True,
        taskIdList=[taskId],
        status=status,
    )

def upload_propreties_to_jym(data):
    """上传新增属性到交易猫"""
    if isinstance(data, Dict):
        data = [data]

    host = 'adc-pc.alibaba-inc.com'
    url = f"http://{host}/task/syncGameProperty"
    newGameId = get_newgameid_by_oldgameid(gameId)

    for i in data_pagination(data, 20):
        json_data = json.dumps(i, ensure_ascii=False)
        json_data_zip = gzip_text(json_data)

        payload = {
            "gameId": str(newGameId),
            "gamePropertiesCompressed": json_data_zip
        }
        respones = requests.post(url, json=payload)
        try:
            monitor_task_status_v2("上传属性到交易猫", payload)
            monitor_task_status_v2("上传完成", respones.json())
        except:
            monitor_task_status_v2("上传失败", respones.text)

# 根据传递参数，获取jiuyou渠道区服信息
def get_jiuyou_url():
    scriptEnv = ENV.scriptEnv
    monitor_task_status_v2("脚本运行环境", scriptEnv)
    if scriptEnv == "daily" or scriptEnv == "local":
        return "http://lingxi-adc-task-sever.taobao.net"
    elif scriptEnv == "pre":
        return "http://pre-lingxi-adc-task-server.alibaba-inc.com"
    else:
        return "http://lingxi-adc-task-server.alibaba-inc.com"

# 获取全部区服，传递为内容为：game_id交易猫里中的clientID
def get_jiuyou_all_servers(game_id: int):
    """
    调用 GET 全部区服接口
    接口: POST /ninegame/server/get
    参数: gameId：交易猫里中的clientID
    """
    BASE_URL = get_jiuyou_url()
    url = f"{BASE_URL}/ninegame/server/get"
    payload = {
        "gameId": game_id
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查 HTTP 错误

        result = response.json().get("serverList")
        return result

    except requests.exceptions.RequestException as e:
        monitor_task_status_v2("获取区服错误", e)
        return None

# 不用考虑去重问题，接口有自动去重
def push_jiuyou_server_incremental(game_id: int, server_list: list, taskId: int, bizId):
    """
    PS：注意，为了做执行时长告警，不管server_list是否为空，都需要调用这个方法
    调用 PUSH 增量区服接口
    接口: POST /ninegame/server/push
    参数: gameId, serverList (List[NineGameServerDTO])
    gameId: 交易猫里中的clientID
    serverList:列表，每个元素为NineGameServerDTO
    taskId: 任务id
    bizId:  业务id

    NineGameServerDTO格式：
    {
        "zoneName": "",
        "openServerTime": ""  # 时间戳，没有可传空值
    }
    """
    BASE_URL = get_jiuyou_url()
    url = f"{BASE_URL}/ninegame/server/push"
    # 构造 NineGameServerDTO 列表
    # 注意：openServerTime 是时间戳（毫秒），可以是 None
    payload = {
        "gameId": game_id,
        "serverList": server_list,
        "taskId": taskId,
        "bizId": bizId,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        return result

    except requests.exceptions.RequestException:
        return None

def report_task_failure(game_id, task_id, biz_id, failure_message):
    """
    九游区服更新异常处理问题，如果出现异常，需要调用这个代码进行异常上报
    向服务器上报任务失败信息
    :param game_id: 游戏 ID
    :param task_id: 任务 ID
    :param biz_id:
    :param failure_message: 失败原因描述
    :return: 响应字典，包含 success（是否成功）和 data/error 信息
    """
    # 请求数据体
    payload = {
        "gameId": game_id,
        "taskId": task_id,
        "errorMsg": failure_message,
        "bizId": biz_id
    }
    BASE_URL = get_jiuyou_url()
    url = f"{BASE_URL}/ninegame/server/error"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        return result

    except requests.exceptions.RequestException:
        return None

def property_write(key: Union[str, Dict]=None, value=None, **kwds):
    """采集属性写入"""
    with shelve.open(properties_path) as properties_data:
        if key and isinstance(key, str) and value is not None:
            properties_data.update({key: value})
        elif isinstance(key, dict):
            properties_data.update(key)
        if kwds:
            properties_data.update(kwds)

def property_read(key=None, default=None, useLocalData=None):
    """采集属性读取"""
    ret_properties_data = {}
    properties_json_path = gameDir / "properties_data_local.json"
    if localRun and useLocalData and properties_json_path.exists():
        ret_properties_data.update(json.loads(properties_json_path.read_text()))

    with shelve.open(properties_path) as properties_data:
        ret_properties_data.update(properties_data)

    if key is None:
        return ret_properties_data
    return ret_properties_data.get(key, default)

def property_del(*keys):
    """采集属性删除"""
    if not keys:
        return
    with shelve.open(properties_path) as properties_data:
        for key in keys:
            properties_data.pop(key, None)

def property_clear():
    """采集属性清理"""
    with shelve.open(properties_path) as properties_data:
        return properties_data.clear()

def keyboard_lock():
    """锁定键盘"""
    try:
        shell("am broadcast -a UPDATE_KEYBOARD --es VALUE '0.0001' com.alibaba.cgs.ime")
        monitor_task_status_v2("KEYBOARD", "LOCK KEYBOARD")
    except Exception as e:
        monitor_print(f"锁定键盘失败: {traceback.format_exc()}")
        monitor_task_status_v2("KEYBOARD", f"锁定键盘失败：{e}")

def delete_path(path_input: Union[str, Path, List[Union[str, Path]]], printLog=True):
    """
    删除文件或文件夹，支持单个路径或路径列表
    限制：只能在指定目录下删除，且不能删除目录本身
    :param: path_input: 文件路径、文件夹路径，或路径列表
    :param: printLog: 是否打印日志
    """

    def _is_in_allowed_dir(path_obj: Path) -> bool:
        """检查路径是否在允许的删除目录下"""
        try:
            path_obj.relative_to(logDir)
            return True
        except ValueError:
            return False

    def _delete_single(path_item: Union[str, Path]):
        """删除单个路径"""
        path_obj = Path(path_item) if isinstance(path_item, str) else path_item
        path_obj = path_obj.resolve()

        if not path_obj.exists():
            monitor_print(f"[跳过] 路径不存在: {path_obj}")
            return

        # 安全检查1：必须在允许的目录下
        if not _is_in_allowed_dir(path_obj):
            monitor_print(f"[跳过] 不在允许目录下: {path_obj}")
            return

        # 安全检查2：不能删除目录本身（必须是目录下的文件或子目录）
        if path_obj == logDir:
            monitor_print(f"[跳过] 不能删除根目录本身: {path_obj}")
            return

        # 删除文件或文件夹
        try:
            if path_obj.is_file():
                os.remove(path_obj)
                if printLog:
                    monitor_print(f"[删除文件] {path_obj}")
            elif path_obj.is_dir():
                shutil.rmtree(path_obj)
                if printLog:
                    monitor_print(f"[删除文件夹] {path_obj}")
        except Exception as e:
            monitor_print(f"[删除失败] {path_obj}: {e}")

    # 判断是否为列表
    if isinstance(path_input, list):
        for item in path_input:
            if isinstance(item, (str, Path)):
                _delete_single(item)
    # 判断是否为字符串或路径
    elif isinstance(path_input, (str, Path)):
        _delete_single(path_input)

def clean_old_timestamp_files(keep_count: int = 30):
    """
    清理 logDir 目录下以时间戳命名的旧jpg文件，保留最新的指定数量
    :param: keep_count: 保留最新文件数量，默认30个
    """
    # 时间戳文件名正则：匹配纯数字（时间戳）或数字.jpg 格式
    timestamp_pattern = re.compile(r'^\d{13}\.jpg$')

    # 获取所有时间戳命名的 jpg 文件
    timestamp_files = []
    for file_path in logDir.iterdir():
        if file_path.is_file() and timestamp_pattern.match(file_path.name):
            # 提取文件名中的时间戳数字用于排序
            timestamp = int(file_path.stem)
            timestamp_files.append((timestamp, file_path))

    # 按文件名时间戳降序排序（最新的在前）
    timestamp_files.sort(key=lambda x: x[0], reverse=True)

    # 保留最新 keep_count 个，其余删除
    if len(timestamp_files) > keep_count:
        files_to_delete = [f[1] for f in timestamp_files[keep_count:]]
        monitor_print(f"[清理文件] 发现{len(timestamp_files)}个时间戳jpg文件，保留最新{keep_count}个，删除{len(files_to_delete)}个")
        delete_path(files_to_delete, printLog=False)
    else:
        monitor_print(f"[清理文件] 发现{len(timestamp_files)}个时间戳jpg文件，未超过保留数量{keep_count}，无需删除")

def biz_msg(msg: str, work_time=True):
    """业务消息"""
    include_gameid_list = [
        "8788", "13765", "15574", "6586",
        "10025", "2717", "9207", "25398",
        "23016", "11446", "5799", "2416",
        "9999013", "9999017", "9999018",
    ]
    monitor_task_status_v2("业务消息", msg)
    if gameId not in include_gameid_list:
        return
    data = {
        "taskId": taskId,
        "gameName": gameName,
        "datetime": timeNowStr(),
        "msg": msg
    }
    if (work_time and is_work_time()) or not work_time:
        monitor_print(f"BUSINESS_MESSAGE: {json_dumps(data)}")
