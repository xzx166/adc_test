import importlib
import importlib.util
import inspect
from typing import ByteString

import requests
from airtest.aircv import aircv
from civita.uiautomator.point import Point
from civita.uiautomator.scroll import Scroll

from utility.base.adc_environment import *
from utility.base.adc_safe_base import *
from utility.base.adc_network import *
from utility.base.adc_utils import *


def lx_import(py_relative_path):
    air_name = py_relative_path
    env = AppEnv.get_instance()

    monitor_print(f"---lx_import_start")

    module_path = None
    module_name = None

    # 传入的是相对路径的情况
    if '/' in air_name:
        # 获取调用者文件的路径（即 `123_apple_fabu.py` 的路径）
        caller_frame = inspect.stack()[1]
        caller_file_path = caller_frame.filename
        caller_dir = Path(caller_file_path).parent

        # 获取调用者的全局命名空间（即 main.py 的全局作用域）
        caller_globals = caller_frame.frame.f_globals

        # 拼接路径并规范化为绝对路径
        absolute_path = caller_dir.joinpath(air_name).resolve()

        monitor_print(f"---lx_import_air_path:{absolute_path}")  # 输出：/User/zxh/adc/utility/aaa.py

        module_path = absolute_path

        # 使用 `Path` 自动处理路径末尾的斜杠
        file_path = Path(absolute_path).resolve()  # 自动规范化路径（如去掉末尾斜杠）
        name_without_ext = file_path.stem  # 直接获取去掉扩展名的文件名
        module_name = name_without_ext

    else:
        # 传入的是air名称的情况
        parts = air_name.split("_")  # 使用 "_" 分割字符串
        game_name = parts[0] + "_" + parts[1]

        air_path = f"{env.rootHome}/{game_name}/{air_name}"
        monitor_print(f"---lx_import_air_name:{env.rootHome}, {game_name}, {air_name}, {air_path}")
        # using(air_path)

        py_name = air_name[:-4]

        module_path = f"{env.rootHome}/{game_name}/{air_name}/{py_name}.py"
        module_name = py_name

    # 检查文件是否存在
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"文件 {module_path} 不存在！")

    print(f"---lx_import:{module_name}, {module_path}")

    if module_name in sys.modules:
        module = sys.modules[module_name]
        if module is not None:
            return module

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    sys.modules[module_name] = module

    print(f"---lx_import_end")
    monitor_print(f"------------lx_import: {module_name}")
    path = os.path.dirname(module_path)
    if path not in G.BASEDIR:
        G.BASEDIR.append(path)
    return module
    # return module
    # cur_global.update(vars(module))


class BreakMode(Enum):
    StartNextPhase = 1
    StopRunloop = 2
    StopApp = 3


class PhaseException(Exception):
    def __init__(self, e, ext_info=None):
        self.e = e
        self.ext_info = ext_info

    def __str__(self):
        return str(self.e)

    def get_inner_e(self):
        return self.e


class ExceptionStartNextPhase(PhaseException):
    pass


class ExceptionStopApp(PhaseException):
    pass


class ExceptionStopRunloop(PhaseException):
    pass


# 中断当前phase，会执行下一个phase
def lx_break_phase(e=None, desc=None):
    if desc:
        ExceptionStartNextPhase(Exception(desc))
    else:
        raise ExceptionStartNextPhase(e or "unkown")


# 中断当前runloop，会执行下一个runloop
def lx_break_runloop(e=None, desc=None, ext_info=None):
    if desc:
        raise ExceptionStopRunloop(Exception(desc), ext_info)
    else:
        raise ExceptionStopRunloop(e or "unkown", ext_info)

    # 中断脚本app，会结束脚本执行


# hold_game 标识是否需要中断关闭游戏
# ext_info 中断app需要透传的额外数据
# 注意：这里e和desc是互斥的
def lx_break_app(ext_info, e=None, desc=None, hold_game=False, partial_func=None):
    AppDynamicInfo.get_instance().setHoldGame(hold_game)
    if partial_func is not None:
        monitor_print(f"---lx_break_app_has_partial_func")
    else:
        monitor_print(f"---lx_break_app_has_NOT_partial_func")

    AppDynamicInfo.get_instance().partial_func = partial_func

    if desc:
        raise ExceptionStopApp(Exception(desc), ext_info)
    else:
        raise ExceptionStopApp(e or Exception("break_app"), ext_info)

def adc_touch(pos: Union[List, Tuple], sec=0, combo=1, printLog=False, touchFunc=None):
    """
    点击事件
    :param pos: 位置
    :param sec: 点击后等待
    :param combo: 连击
    :param printLog: 打印日志
    :param touchFunc: 点击函数
    :return: null
    """
    system = AppEnv.get_instance().system_type
    if system in ['android', "yunyou_ios"]:
        for i in range(combo):
            lx_safe_touch(pos, sec, printLog, touchFunc)
            if i < combo - 1: sleep(0.2)
    elif system == 'ios':
        __ios_touch(pos, sec, combo)
    if printLog:
        print(f"adc_touch: {pos}")

def __ios_touch(pos: Union[Tuple, List], sec=0, combo=1):
    """
    点击事件 ios
    :param pos: 位置
    :param sec: 点击后等待
    :param combo: 连击
    :return:
    """
    env = AppEnv.get_instance()
    session_ctrl = env.iOS_session_connect
    screenWidth = int(os.environ.get("screenWidth", "0"))
    screenHeight = int(os.environ.get("screenHeight", "0"))
    posDivisor = int(os.environ.get("posDivisor"))
    if screenWidth > screenHeight:
        pos = screenHeight - pos[1], pos[0]
    for i in range(combo):
        session_ctrl.ui.tap(Point(pos[0] // posDivisor, pos[1] // posDivisor, is_per=False))
        if i < combo - 1: sleep(0.1)
    sleep(sec)

def adc_snapshot(filename="snapshot", msg="", quality=None, max_size=None):
    """
    获取屏幕快照
    :param filename: 快照名称
    :param msg: 描述
    :param quality: 质量  android
    :param max_size: 最大尺寸 android
    :return: numpy array image object
    """
    system = AppEnv.get_instance().system_type
    if system in ['android', "yunyou_ios"]:
        return lx_safe_snapshot(filename, msg, quality, max_size)
    elif system == 'ios':
        return __ios_snapshot(filename)

def __ios_snapshot(filename=None):
    """
    获取屏幕快照 ios
    :param filename: 快照名称
    :return: numpy array image object
    """
    logDir = Path(AppEnv.get_instance().logPath).resolve()
    env = AppEnv.get_instance()
    session_ctrl = env.iOS_session_connect
    data = None
    for i in range(3):
        t0 = time.time()
        try:
            data = session_ctrl.screenshot()
        except Exception:
            monitor_task_status_v2("截图失败", traceback.format_exc(), status=120024)
            lx_break_runloop(desc="截图失败", ext_info={"key": "120024"})

        if image_url := data.get("full_url"):
            response = requests.get(image_url)
            content = response.content
            save_path = logDir / f"oss_{timeStamp()}.png"
            if isinstance(content, ByteString):
                save_path.write_bytes(content)
                image = cv2.imread(str(save_path))
                if os.environ.get("rotate_90"):
                    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                # 保存图片
                if filename is not None and isinstance(image, np.ndarray):
                    if os.path.splitext(filename)[-1] not in ('.png', '.jpg'):
                        filename = f"{filename}.jpg"
                    try:
                        cv2.imwrite(str(logDir / filename), image)
                    except Exception as e:
                        monitor_task_status_v2("---ios_save_image_error", f"{str(logDir / filename)}, error {e}")
                monitor_print(f"---ios_image_url: {image_url}, time: {time.time() - t0:.2f}s")
                return image

        elif i < 2:
            monitor_print(f"---ios_screenshot_data: {data}")
            sleep(1)
    else:
        monitor_task_status_v2("截图失败", data, status=120024)
        lx_break_runloop(desc="截图失败", ext_info={"key": "120024"})

def adc_swipe(start_point, end_point, duration=None, direction='up', speed=20, steps=10, hold_sec=0.5, sec=0):
    """
    滑动事件
    :param start_point: 开始点
    :param end_point: 结束点
    :param duration: 滑动持续时间 (android, yunyou_ios)
    :param speed: 滑动速度 (ios)
    :param direction: 滑动方向 (ios)
    :param steps: 滑动步数 (yunyou_ios)
    :param hold_sec: 滑动保持 (yunyou_ios)
    :param sec: 滑动后等待
    :return:
    """
    system = AppEnv.get_instance().system_type
    if system == SystemType.ANDROID.value:
        return __android_swipe(
            start_point,
            end_point,
            duration or 0.5,
            sec=sec)
    elif system == SystemType.IOS.value:
        return __ios_swipe(
            start_point,
            end_point,
            direction,
            speed,
            duration=duration or 1.0,
            sec=sec)
    elif system == SystemType.YUNYOU_IOS.value:
        return __yunyou_ios_swipe(
            start_point,
            end_point,
            duration=duration or 1.0,
            steps=steps or 10,
            hold_sec=hold_sec,
            sec=sec)

__step_dict = lambda x, y, offset: {"x": float(x), "y": float(y), "offset": offset}
def __swipe_move(from_xy, to_xy, duration, steps=5, hold_sec=0.5):
    from_x, from_y = from_xy
    to_x, to_y = to_xy

    ret = []
    interval = duration / (steps + 1)
    delta_x, delta_y = to_x - from_x, to_y - from_y

    for i in range(1, steps):
        x = from_x + delta_x * i / steps
        y = from_y + delta_y * i / steps
        ret.append(__step_dict(x, y, interval * i))
    ret.append(__step_dict(to_x, to_y, duration))
    ret.append(__step_dict(to_x, to_y, duration + hold_sec))
    return ret

def __swipe_along(coordinates_list, duration, steps=5, hold_sec=0.5):
    from pprint import pprint

    from_xy = coordinates_list[0]
    swipe_events = [__step_dict(*from_xy, 0)]
    for to_xy in coordinates_list[1:]:
        swipe_events.extend(__swipe_move(
            from_xy,
            to_xy,
            duration=duration,
            steps=steps,
            hold_sec=hold_sec))
        from_xy = to_xy
    return swipe_events

def __yunyou_ios_swipe(start_point, end_point, duration=1, steps=5, hold_sec=0.5, sec=0):
    """
    滑动事件 iOS云机
    :param start_point: 开始点
    :param end_point: 结束点
    :param duration: 滑动持续时间
    :param sec: 滑动后等待
    :param steps: 滑动步数 (yunyou_ios)
    :return:
    """
    ENV = AppEnv.get_instance()
    DEV = ENV.device
    if DEV.uuid.startswith("http+usbmux"):
        swipe(start_point, end_point, duration=duration)
        sleep(sec)
        return

    deviceUrl = f"{DEV.uuid}/wda/ttg/swipe"
    swipe_events = __swipe_along(
        [start_point, end_point],
        duration=duration,
        steps=steps,
        hold_sec=hold_sec)
    display_info = DEV.display_info
    width = display_info['width']
    height = display_info['height']
    if display_info["orientation"] == "LANDSCAPE":
        width, height = height, width
    payload = {
        "path": swipe_events,
        "xRange": width,
        "yRange": height,
    }
    requests.post(deviceUrl, json=payload)
    sleep(sec)

def __android_swipe(start_point, end_point, duration=0.5, sec=0):
    """
    滑动事件 android
    :param start_point: 开始点
    :param end_point: 结束点
    :param duration: 滑动持续时间
    :param sec: 滑动后等待
    :return:
    """
    from_x, from_y = start_point
    to_x, to_y = end_point
    dev = AppEnv.get_instance().device
    dev.touch_proxy.swipe_along([(from_x, from_y), (to_x, to_y-2), (to_x, to_y)], duration=duration)
    sleep(sec)

def __ios_swipe(start_point, end_point, direction='up', speed=20, sec=0, duration=1.0, offset=0.5):
    """
    滑动事件 ios
    :param start_point: 开始点
    :param end_point: 结束点
    :param direction: 滑动方向
    :param speed: 滑动速度
    :param sec: 滑动后等待
    :param duration: 滑动持续时间
    :return:
    """
    is_accurate_swipe = True
    env = AppEnv.get_instance()
    screenWidth = int(os.environ.get("screenWidth", "0"))
    screenHeight = int(os.environ.get("screenHeight", "0"))
    if screenWidth > screenHeight:
        start_point = screenHeight - start_point[1], start_point[0]
        end_point = screenHeight - end_point[1], end_point[0]
    if is_accurate_swipe:
        posDivisor = int(os.environ.get("posDivisor"))
        swipe_list = [
            {"x": start_point[0] / posDivisor, "y": start_point[1] / posDivisor, "offset": 0},
            {"x": end_point[0] / posDivisor, "y": end_point[1] / posDivisor, "offset": duration},
            {"x": end_point[0] / posDivisor, "y": end_point[1] / posDivisor, "offset": duration + offset}
        ]
        modaoshi_action_swipe(wda_port=env.iOS_wda_port, data={'path': swipe_list})
        sleep(sec)

        return

    scroll = None
    if direction == 'up':
        scroll = Scroll.up(1)
    elif direction == 'down':
        scroll = Scroll.down(1)
    elif direction == 'left':
        scroll = Scroll.left(1)
    elif direction == 'right':
        scroll = Scroll.right(1)

    def change_coordinate(startPoint, endPoint, direction='up'):
        if direction == 'up':
            height = abs(endPoint[1] - startPoint[1])
            # height = 2 * endPoint[1] + abs(startPoint[1] - endPoint[1]) - endPoint[1]
            width = 2 * endPoint[0]
            x = 0
            y = endPoint[1]
            return {'x': x, 'y': y, 'width': width, 'height': height}
        elif direction == 'down':
            height = abs(endPoint[1] - startPoint[1])
            # height = 2 * endPoint[1] + abs(startPoint[1] - endPoint[1]) - endPoint[1]
            width = 2 * endPoint[0]
            x = 0
            y = startPoint[1]
            return {'x': x, 'y': y, 'width': width, 'height': height}
        elif direction == 'left':
            height = 2 * endPoint[1]
            width = abs(endPoint[0] - startPoint[0])
            x = endPoint[0]
            y = 0
            return {'x': x, 'y': y, 'width': width, 'height': height}
        elif direction == 'right':
            height = 2 * endPoint[1]
            width = abs(endPoint[0] - startPoint[0])
            x = startPoint[0]
            y = 0
            return {'x': x, 'y': y, 'width': width, 'height': height}

    scroll.speed = speed

    startPoint, endPoint = (start_point[0] // 2, start_point[1] // 2), (end_point[0] // 2, end_point[1] // 2)
    cur_are = change_coordinate(startPoint, endPoint, direction=direction)
    print(f"xxxxddddJ: {cur_are}")
    scroll.area =  cur_are

    env.iOS_session_connect.ui.scroll(scroll)
    sleep(sec)


def __try_log_screen(screen=None, quality=None, max_size=None):
    """
    Save screenshot to file

    Args:
        screen: screenshot to be saved
        quality: The image quality, default is ST.SNAPSHOT_QUALITY
        max_size: the maximum size of the picture, e.g 1200

    Returns:
        {"screen": filename, "resolution": aircv.get_resolution(screen)}

    """
    if not ST.LOG_DIR or not ST.SAVE_IMAGE:
        return
    if not quality:
        quality = ST.SNAPSHOT_QUALITY
    if not max_size:
        max_size = ST.IMAGE_MAXSIZE
    if screen is None:
        screen = adc_snapshot(quality=quality)
    filename = "%(time)d.jpg" % {'time': time.time() * 1000}
    filepath = os.path.join(ST.LOG_DIR, filename)
    if screen is not None:
        aircv.imwrite(filepath, screen, quality, max_size=max_size)
        return {"screen": filename, "resolution": aircv.get_resolution(screen)}
    return None

def __loop_find(query, snapshot_path=None, timeout=ST.FIND_TIMEOUT, threshold=None, interval=1, intervalfunc=None):
    """
    Search for image template in the screen until timeout

    Args:
        query: image template to be found in screenshot
        timeout: time interval how long to look for the image template
        threshold: default is None
        interval: sleep interval before next attempt to find the image template
        intervalfunc: function that is executed after unsuccessful attempt to find the image template

    Raises:
        TargetNotFoundError: when image template is not found in screenshot

    Returns:
        TargetNotFoundError if image template not found, otherwise returns the position where the image template has
        been found in screenshot

    """
    # print(f"---lx_loop_find")
    G.LOGGING.info("Try finding: %s", query)
    start_time = time.time()
    while True:
        if isinstance(snapshot_path, str) and os.path.isfile(snapshot_path):
            screen = cv2.imread(snapshot_path)
        elif isinstance(snapshot_path, np.ndarray):
            screen = snapshot_path
        else:
            screen = adc_snapshot()

        # if not query.resolution:
        #     shape = screen.shape[:2]
        #     query.resolution = shape[1], shape[0]

        if screen is None:
            G.LOGGING.warning("Screen is None, may be locked")
        else:
            if threshold:
                query.threshold = threshold
            match_pos = query.match_in(screen)
            if match_pos:
                __try_log_screen(screen)
                return match_pos

        if intervalfunc is not None:
            intervalfunc()

        # 超时则raise，未超时则进行下次循环:
        if (time.time() - start_time) > timeout:
            __try_log_screen(screen)
            raise TargetNotFoundError('Picture %s not found in screen' % query)
        else:
            time.sleep(interval)

class CoustomTemplate(Template):
    def __init__(self, filename, record_pos=None, resolution=()):
        if not resolution:
            system_type = AppEnv.get_instance().system_type
            if system_type in ['android', "yunyou_ios"]:
                resolution = G.DEVICE.get_current_resolution()
            elif system_type == "ios":
                # TODO iOS 获取分辨率
                screenWidth = os.environ.get("screenWidth")
                screenHeight = os.environ.get("screenHeight")
                if str(screenWidth).isdigit() and str(screenHeight).isdigit():
                    resolution = int(screenWidth), int(screenHeight)
                else:
                    resolution = (750, 1334)
        super().__init__(filename, record_pos=record_pos, resolution=resolution)

def add_basedir(func):
    def wrapper(*args, **kwargs):
        caller_frame = inspect.stack()[1]
        caller_file_path = caller_frame.filename
        caller_dir = str(Path(caller_file_path).parent)
        # print(f"---add_basedir_before: {G.BASEDIR}")
        G.BASEDIR = list(filter(lambda x: x, G.BASEDIR))
        # print(f"---add_basedir_after: {G.BASEDIR}")
        if caller_dir not in G.BASEDIR:
            print(f"---add_basedir: {caller_dir}")
            G.BASEDIR.append(caller_dir)
        return func(*args, **kwargs)
    return wrapper

@add_basedir
def adc_wait(file_name, timeout=None, interval=1, intervalfunc=None, is_try=False):
    """
    wait方法 入参图片名
    :param file_name:
    :param timeout:
    :param interval:
    :param intervalfunc:
    :param is_try:
    :return:
    """
    # print(f"---adc_wait: {G.BASEDIR}")
    # v = CoustomTemplate(file_name)
    # timeout = timeout or ST.FIND_TIMEOUT
    # pos = __loop_find(v, timeout=timeout, interval=interval, intervalfunc=intervalfunc)
    # return pos

    try:
        v = CoustomTemplate(file_name)
        timeout = timeout or ST.FIND_TIMEOUT
        pos = __loop_find(v, timeout=timeout, interval=interval, intervalfunc=intervalfunc)
        return pos
    except Exception as e:
        print(f'---lx_wait_Exception:{e}, is_try:{is_try}')
        if is_try:
            return None
        else:
            raise e

@add_basedir
def adc_wait_touch(filename, sec=1, timeout=3, interval=1, title="", desc="", **kwds):
    """
    wait_touch方法 入参图片名
    :param filename:
    :param sec:
    :param timeout:
    :param interval:
    :param title:
    :param desc:
    :return:
    """
    try:
        v = CoustomTemplate(filename)
        if pos := __loop_find(v, timeout=timeout, interval=interval):
            adc_touch(pos, sec)
            if title and desc:
                monitor_task_status_v2(title, f"{desc} {pos}")
            elif title or desc:
                monitor_print(f"{title}{desc} {pos}")
            return pos
    except Exception as e:
        return None

@add_basedir
def adc_exists(file_name):
    """
    exists方法 入参图片名
    :param file_name:
    :return:
    """
    v = CoustomTemplate(file_name)
    try:
        pos = __loop_find(v, timeout=ST.FIND_TIMEOUT_TMP)
    except TargetNotFoundError:
        return False
    else:
        return pos

@add_basedir
def adc_exists_with_file(filename, snapshot_path, threshold=None, timeout=None):
    """
    判断filename是否在snapshot_path中
    :param filename:
    :param snapshot_path:
    :param threshold:
    :param timeout:
    :return:
    """
    try:
        if isinstance(filename, Template):
            v = filename
        else:
            v = CoustomTemplate(filename)
        real_timeout = ST.FIND_TIMEOUT_TMP
        if timeout is not None:
            real_timeout = timeout
        pos = __loop_find(v, snapshot_path, timeout=real_timeout, threshold=threshold)
    except TargetNotFoundError:
        return False
    else:
        return pos

def adc_exists_with_image(filename: Union[str, Template], image: np.ndarray, threshold=None):
    """
    判断filename是否在image中
    :param filename:
    :param image:
    :param threshold:
    :return:
    """
    try:
        if isinstance(filename, Template):
            v = filename
            shape = image.shape[:2]
            v.resolution = (shape[1], shape[0])
        else:
            shape = image.shape[:2]
            v = CoustomTemplate(filename, resolution=(shape[1], shape[0]))
        pos = __loop_find(v, image, timeout=0, threshold=threshold)
    except TargetNotFoundError:
        return False
    else:
        return pos

def adc_input(string):
    """
    输入文本,注意要在调用之前先触发输入框的响应状态
    :param string:
    :return:
    """
    env = AppEnv.get_instance()
    system = env.system_type
    if system == 'android':
        # 中文输入
        if tool_contains_chinese(string):
            # 判断设备是否有安装clipper
            if "ca.zgrs.clipper" not in shell("pm list package -3"):
                current_file_path = os.path.abspath(__file__)
                current_dir = os.path.dirname(current_file_path)
                install(f'{current_dir}/clipper.apk', install_options=["-r", "-f"])
                monitor_task_status_v2("Clipper安装完成")

            # 判断clipper是否被冻结
            if "ca.zgrs.clipper" in shell("pm list package -d"):
                shell("pm enable ca.zgrs.clipper")
                monitor_task_status_v2("启用Clipper")

            for _ in range(3):
                try:
                    shell("am startservice ca.zgrs.clipper/.ClipboardService")
                    shell(f'am broadcast -a clipper.set --es text "{string}"')
                    shell(f'input keyevent 279')
                    shell(f'am broadcast -a clipper.set --es text ""')
                    break
                except Exception as e:
                    monitor_task_status_v2("Clipper输入失败", e)
                    if pos := adc_exists("tpl20251126124607.png"):
                        adc_touch(pos, 1)
                        monitor_task_status_v2("向Clipper授予权限", f"点击继续 {pos}")

        # 非中文输入
        else:
            G.DEVICE.shell(f"input text \'{string}\'")

    elif system == 'ios':
        session_ctrl = env.iOS_session_connect
        session_ctrl.type_text(string)

    elif system == 'yunyou_ios':
        text(string)

class clipboardException(Exception):
    def __str__(self):
        return "剪贴板为空"

def adc_get_clipboard(packageName=None, useScheme1=False):
    """
    获取剪贴板文本
    :param: packageName:
    :return: text
    """
    # 方案1
    if useScheme1:
        if text := G.DEVICE.get_clipboard():
            return text
        else:
            return ""

    # 方案2
    # 判断设备是否有安装clipper
    for _ in range(3):
        try:
            start_app("ca.zgrs.clipper")
            sleep(1)
            text = shell('am broadcast -a clipper.get')

            if regex_result := "".join(re.findall("data=\"(.*)\"", text)):
                monitor_print(f"获取剪贴板文本: {regex_result}")
                shell(f'am broadcast -a clipper.set --es text ""')
                shell("am startservice ca.zgrs.clipper/.ClipboardService")
                # 启动应用或返回
                if packageName:
                    start_app(packageName)
                else:
                    keyevent("BACK")
                sleep(1)
                return regex_result

            else:
                raise clipboardException

        except Exception as e:
            if "ca.zgrs.clipper" not in shell("pm list package -3"):
                current_file_path = os.path.abspath(__file__)
                current_dir = os.path.dirname(current_file_path)
                install(f'{current_dir}/clipper.apk', install_options=["-r", "-f"])
                monitor_task_status_v2("Clipper安装完成")

            # 判断clipper是否被冻结
            if "ca.zgrs.clipper" in shell("pm list package -d"):
                shell("pm enable ca.zgrs.clipper")
                monitor_task_status_v2("启用Clipper")

            monitor_task_status_v2("Clipper获取失败", e)
            if adc_wait_touch("tpl20251126124607.png", timeout=2, title="向Clipper授予权限", desc="点击继续"):...
            elif adc_wait("tpl20260109153156.png", timeout=2, is_try=True):
                adc_wait_touch("tpl20260109153511.png", title="旧版Android弹窗", desc="点击确定")
            else:
                return ""

def adc_home():
    """
    返回系统首页
    :return:
    """

    env = AppEnv.get_instance()
    system = env.system_type
    if system == 'android':
        G.DEVICE.shell("input keyevent 3")
    elif system == 'ios':
        session_ctrl = env.iOS_session_connect
        session_ctrl.key_press("home")
    elif system == 'yunyou_ios':
        home()

def adc_start_app(gameName: str, packageName: str, sec=0, printLog=True):
    """
    启动游戏
    :param gameName: 游戏名称
    :param packageName: 包名
    :param sec: 启动后等待
    :param printLog:
    :return: 无
    """
    env = AppEnv.get_instance()
    if printLog:
        monitor_task_status_v2("启动游戏", gameName)
    if env.system_type == "android":
        start_app(packageName)
    else:
        ex = None
        for _ in range(6):
            try:
                start_result = env.iOS_session_connect.open_app(pkg=packageName)
                monitor_print(f"启动游戏结果: {start_result}")
                if start_result == True:
                    break
                else:
                    sleep(15)
                    continue
            except Exception as e:
                ex = e
        else:
            monitor_task_status_v2("启动游戏失败", traceback.format_exc())
            raise ex
    if isinstance(sec, (int, float)) and sec > 0:
        sleep(sec)

def adc_close_app(gameName: str, packageName: str):
    """
    关闭游戏
    :param gameName: 游戏名称
    :param packageName: 包名
    :return: 无
    """
    env = AppEnv.get_instance()
    monitor_task_status_v2("关闭游戏", gameName)
    if env.system_type == "android":
        stop_app(packageName)
    else:
        ex = None
        for _ in range(6):
            try:
                close_result = env.iOS_session_connect.close_app(pkg=packageName)
                if close_result == True:
                    break
                else:
                    sleep(15)
                    continue
            except Exception as e:
                ex = e
        else:
            monitor_task_status_v2("关闭游戏失败", traceback.format_exc())
            raise ex

