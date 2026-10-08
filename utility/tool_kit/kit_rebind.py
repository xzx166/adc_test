from utility.tool_kit.tool_kit import *
from functools import partial
from utility.app.rebind.rebind_request import *
rebind_json = json.loads(ENV.get_common_property_with_key('aiRebindExtParams'))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in G.BASEDIR:
    G.BASEDIR.append(BASE_DIR)

def kit_rebind_handle(**kwargs):
    '''
        ai换绑错误异常处理
    '''
    code = kwargs.get("code", "")
    message = kwargs.get("message", "")
    success = kwargs.get("success", False)
    ext_info = kwargs.get("ext_info", {})
    ext_code = kwargs.get("ext_code", "200")
    image = kwargs.get("image", "")
    stage = rebind_json.get('scriptName')
    callback_img = kwargs.get("callback_img", "")
    if not callback_img:
        callback_img = snapshotImg(f"callback", catch_file_name, path=True)
        oss_pathes, oss_urls = upload_jym_oss_with_pathes([callback_img])
    else:
        oss_pathes, oss_urls = upload_jym_oss_with_pathes(callback_img)
    ext_info["screenshot_url"] = oss_urls[0]
    bound_b = partial(rebind_execute_callback, task_id=rebind_json['taskId'], code=code, message=message,ext_info=ext_info, success=success)
    if not success:
        monitor_task_status_v2("异常", f"{stage} {message}")
        snapshotImg(f"{stage}_error",catch_file_name, path=True)
    lx_break_app(ext_info={'key': ext_code}, desc=code, hold_game=True, partial_func=bound_b)


def process_check():
    '''
        云游容器释放检测
    '''
    if kit_wait_find(Template(r"tpl1758509208340.png", record_pos=(0.002, 0.0)),timeout=2):
        kit_rebind_handle(code="internal_error", message=f"云游容器进程释放", success=False)


def kit_rebind_game_action(**kwargs):
    '''
        游戏相关操作
        :param set_resolution_and_density: 是否设置分辨率和密度
        :param is_horizontal: 是否横屏
        :param disable_keyboard: 是否禁用键盘
        :param clean_game_func: 清理游戏函数
        :param package_name: 游戏包名
        :param stop_game: 是否停止游戏
        :param start_game: 是否启动游戏
    '''
    set_resolution_and_density = kwargs.get("set_resolution_and_density", True)
    is_horizontal = kwargs.get("is_horizontal", True)
    disable_keyboard = kwargs.get("disable_keyboard", True)
    stop_game = kwargs.get("stop_game", True)
    start_game = kwargs.get("start_game", True)
    clean_game_func = kwargs.get("clean_game_func", None)
    package_name = kwargs.get("package_name")
    if stop_game:
        stop_app(package_name)
    if set_resolution_and_density:
        if is_horizontal:
            shell("wm size 2400x1350")
        else:
            shell("wm size 1350x2400")
        shell("wm density 450")
    if disable_keyboard:
        shell("am broadcast -a UPDATE_KEYBOARD --es VALUE '0.0001' com.alibaba.cgs.ime")
    if clean_game_func:
        clean_game_func(package_name)
    if start_game:
        monitor_task_status_v2( "启动游戏", f"启动{package_name}")
        shell(f'pm  enable {package_name}')
        shell(f"monkey -p {package_name} 1 ")
    return True

def kit_rebind_text_verify(**kwargs):
    '''
        文字验证码校验
    '''
    crop_pos_img_path = kwargs.get("crop_pos_img_path")
    captchaType = kwargs.get("captchaType")
    recoType = kwargs.get("recoType", "文字验证码")

    monitor_print(f'---kit_rebind_text_verify_img_path: {crop_pos_img_path}')
    env = AppEnv.get_instance()

    if not crop_pos_img_path.startswith("http"):
        localFileList = []
        localFileList.append(crop_pos_img_path)
        _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
        if cdn_url_list:
            qufu_crop_img_url = cdn_url_list[0]
    else:
        qufu_crop_img_url = crop_pos_img_path

    resData = {}
    resData['requestId'] = str(int(time.time() * 1000000))
    resData['imageUrl'] = qufu_crop_img_url
    resData['recoType'] = recoType
    resData['captchaType'] = captchaType

    risk_path = '/api/predict/lingxialgo_ocr_service_pre'
    scriptEnv = env.scriptEnv
    if (scriptEnv == 'local'):
        risk_path = "/api/predict/lingxialgo_ocr_service_pre"
    elif (scriptEnv == 'pre'):
        risk_path = "/api/predict/lingxialgo_ocr_service_pre"
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_ocr'

    monitor_print(f'---get_env_ocr_path: {risk_path}, env:{scriptEnv}')

    data = enhanced_easrequest(risk_path, resData, type=2)
    if data is not None and 'message' in data and ('status' in data['message']) and ('data' in data['message']):
        ocrResult = data['message']['data']
        status = data['message']['status']
        monitor_task_status(ENV, "风控识别结果", f"{ocrResult}")
        monitor_print(f'---kit_rebind_text_verify_result:{status},{qufu_crop_img_url},{ocrResult}')
        return qufu_crop_img_url, ocrResult
    else:
        return qufu_crop_img_url, None
    
def kit_rebind_start_xbrowser(**kwargs):
    '''
        启动x浏览器
        :param set_resolution_and_density: 是否设置分辨率和密度
        :param is_portrait: 是否竖屏
        :return: 启动结果
    '''
    set_resolution_and_density = kwargs.get("set_resolution_and_density", True)
    is_portrait_screen = kwargs.get("is_portrait_screen", True)
    if set_resolution_and_density:
        shell("wm size 2400x1350")
        shell("wm density 450")
    xVxbrowser = "com.mmbox.xbrowser"
    shell("am broadcast -a UPDATE_KEYBOARD --es VALUE '0.0001' com.alibaba.cgs.ime")
    shell(f"am force-stop {xVxbrowser}") # kill 浏览器
    sleep(2)
    shell(f"pm clear {xVxbrowser}")
    shell(f"pm enable {xVxbrowser}")
    shell(f"monkey -p {xVxbrowser} 1")
    sleep(5)
    for i in range(2):
        shell("settings put system accelerometer_rotation 0")
        if is_portrait_screen:
            shell("settings put system user_rotation 1")
        else:
            shell("settings put system user_rotation 0")
        shell("settings put system accelerometer_rotation 1")
        sleep(3)
    pop1 = kit_wait_find(Template(r"tpl1757062008455.png", record_pos=(0.148, 0.259), resolution=(1350, 2400)),timeout=6)
    if not pop1: 
        monitor_task_status_v2(f"X浏览器打开异常", f"")
        return False

    adc_touch(pop1, 1)
    monitor_task_status_v2(f"X浏览器", f"进入")
    if is_portrait_screen:
        iKonwRegion = kit_wait_find(Template(r"tpl1757584200639.png", record_pos=(-0.002, 0.421), resolution=(1350, 2400)),timeout=8)
        if iKonwRegion:adc_touch(iKonwRegion, 1)
    else:
        iKonwRegion = kit_wait_find(Template(r"tpl1762502684126.png", record_pos=(-0.184, -0.225), resolution=(2400, 1350)),timeout=8)
        if iKonwRegion:adc_touch((1088,1253), 1)
    if is_portrait_screen:
        close_button_area_pos = (1160,2080,1350,2250)
    else:
        close_button_area_pos = (2200,1000,2400,1200)
    if pop_windows_close_button :=kit_wait_find(Template(r"tpl1764931781724.png", record_pos=(0.472, 0.18), resolution=(2400, 1350)), threshold=0.98, area_pos=close_button_area_pos):
        monitor_task_status_v2(f"X浏览器检测到插件提示框", f"关闭")
        adc_touch(pop_windows_close_button, 1)
    v_list = [
        Template(r"tpl1760170544087.png", record_pos=(-0.003, -0.418), resolution=(1350, 2400)),
        Template(r"tpl1762504868998.png", record_pos=(-0.419, -0.249), resolution=(2400, 1350))
    ]
    if kit_wait_find_plus(v_list, threshold=0.8, timeout=10):
        return True
    else:
        return False
    
def kit_rebind_common_verify(**kwargs):
    '''
        通用验证码校验
        :param crop_pos_img_path 图片本地路径
        :param recoType 验证码类型
            1 图形验证码
            2 文字验证码
            3 语序验证码
            4 滑块验证码
            5 空间推理验证码
    '''
    crop_pos_img_path = kwargs.get("crop_pos_img_path")
    reco_type = kwargs.get("recoType", 1)
    captchaType = kwargs.get("captchaType", "")
    monitor_print(f'---kit_rebind_common_verify_img_path: {crop_pos_img_path}')
    env = AppEnv.get_instance()

    if not crop_pos_img_path.startswith("http"):
        localFileList = []
        localFileList.append(crop_pos_img_path)
        _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
        if cdn_url_list:
            qufu_crop_img_url = cdn_url_list[0]
    else:
        qufu_crop_img_url = crop_pos_img_path

    resData = {}
    resData['requestId'] = str(int(time.time() * 1000000))
    resData['imageUrl'] = qufu_crop_img_url
    if reco_type == 3:
        resData['captchaType'] = "鸣潮语序"
    elif reco_type != 5:
        resData['imageProperties'] =  [{"propertyId": "验证码"}]
    if captchaType:
        resData['captchaType'] = captchaType
    if reco_type == 1:
        resData['recoType'] = "图形验证码"
    elif reco_type == 4:
        resData['recoType'] = "拼图验证码"
    elif reco_type == 5:
        resData['recoType'] = "空间推理验证码"
    else:
        resData['recoType'] = "文字验证码"

    risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
    scriptEnv = env.scriptEnv
    if (scriptEnv == 'local'):
        risk_path = "/api/predict/lingxialgo_adc_ocr_pre"
    elif (scriptEnv == 'pre'):
        risk_path = "/api/predict/lingxialgo_adc_ocr_pre"
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_adc'
    risk_path = '/api/predict/lingxialgo_ocr_service_pre'
    scriptEnv = ENV.scriptEnv
    if reco_type == 4:
        if scriptEnv == 'local':
            risk_path = '/api/predict/lingxialgo_vision_adc_pre'
        elif scriptEnv == 'pre':
            risk_path = '/api/predict/lingxialgo_vision_adc'
        elif scriptEnv == 'prod':
            risk_path = '/api/predict/lingxialgo_vision_adc'
        else:
            risk_path = '/api/predict/lingxialgo_vision_adc_pre'
    else:
        if (scriptEnv == 'local'):
            risk_path = "/api/predict/lingxialgo_ocr_service_pre"
        elif (scriptEnv == 'pre'):
            risk_path = "/api/predict/lingxialgo_ocr_service_pre"
        elif (scriptEnv == 'prod'):
            risk_path = '/api/predict/lingxialgo_vision_ocr'
        
    monitor_print(f'---kit_rebind_common_verify_get_env_ocr_path: {risk_path}, env:{scriptEnv}')
    if reco_type == 4:
        data = easRequest(risk_path, resData)
    else:
        data = enhanced_easrequest(risk_path,resData, type=2)
    if reco_type == 4:
        if data is not None and 'message' in data and ('status' in data['message']) and ('imagePropertyValues' in data['message']):
            ocrResult = data['message']['imagePropertyValues']
            status = data['message']['status']
            monitor_task_status(ENV, "风控识别结果", f"{ocrResult}")
            monitor_print(f'---kit_rebind_common_verify_result:{status},{qufu_crop_img_url},{ocrResult}')
            return qufu_crop_img_url,ocrResult
        else:
            return qufu_crop_img_url,None
    else:
        if data is not None and 'message' in data and ('status' in data['message']) and ('data' in data['message']):
            ocrResult = data['message']['data']
            status = data['message']['status']
            monitor_task_status(ENV, "风控识别结果", f"{ocrResult}")
            monitor_print(f'---kit_rebind_common_verify_result:{status},{qufu_crop_img_url},{ocrResult}')
            return qufu_crop_img_url,ocrResult
        else:
            return qufu_crop_img_url,None
