import datetime
import hashlib
import logging
import urllib
import urllib.error
import urllib.error
import urllib.request
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from utility.app.service.adc_oss import upload_jym_oss_with_pathes
from utility.base.adc_api import lx_break_runloop
from utility.base.adc_monitor import *

IS_M3_CHIP = AppDynamicInfo.get_instance().getIsM3Support()

if IS_M3_CHIP == False:
    from paddleocr import PaddleOCR

    logging.getLogger('ppocr').setLevel(logging.CRITICAL)


    # 禁用PP-OCR库的调试信息输出
    def ocr_image(img, en_ocr=False):
        ocr = PaddleOCR(lang='ch', use_gpu=False, use_angle_cls=False)
        ocr_en = PaddleOCR(lang='en', use_gpu=False, use_angle_cls=False)

        array = []
        result = []
        if False == en_ocr:
            result = ocr.ocr(img)
        else:
            result = ocr_en.ocr(img)

        if True == en_ocr and (result is None or (len(result) > 0 and result[0] is None)):
            # 英文模式下 -识别无结果，降级中文识别一下；中文模式下禁止降级！！！
            result = ocr.ocr(img)
        print(f'ocr_image:{result}')

        if result and len(result):
            for line in result:
                if line and len(line):
                    for word in line:
                        array.append(word[1])

        return array


    def enhanced_image(img, enhance_size=None):
        height, width = img.shape[:2]
        enhance_width, enhance_height = None, None
        if enhance_size is None:
            enhance_width, enhance_height = width * 4, height * 4
        else:
            enhance_width, enhance_height = enhance_size

        monitor_print(f'---enhance_image: {enhance_width}, {enhance_height}')
        resize_crop_img = cv2.resize(img, (enhance_width, enhance_height))
        img_rgb = cv2.cvtColor(resize_crop_img, cv2.COLOR_BGR2RGB)
        deal_crop_name_image = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        deal_crop_name_image = cv2.medianBlur(deal_crop_name_image, 15)
        return deal_crop_name_image


    def enhanced_ocr_image(img, en_ocr=False, enhance_size=None):
        if enhance_size is None:
            return ocr_image(img, en_ocr)

        image = enhanced_image(img, enhance_size)

        deal_ocr_arr = ocr_image(image, en_ocr)
        return deal_ocr_arr


    def ocr_image_list(images, en_ocr=False):
        ocr = PaddleOCR(lang='ch', use_gpu=False, use_angle_cls=False)
        ocr_en = PaddleOCR(lang='en', use_gpu=False, use_angle_cls=False)

        logs = []
        result = []
        for img in images:
            array = []
            if False == en_ocr:
                result = ocr.ocr(img)
            else:
                result = ocr_en.ocr(img)
            for line in result:
                for word in line:
                    array.append(word[1])
            logs.append(array)

        return logs


# **********************************远端识别模型接口*******************************************
# 注意type的类型对应不同的识别模型
# 1是旧的包含异形字的ocr模型，
# 2是中英数综合模型，通用的识别模型，实测针对标准字体类型2的识别率高很多
# 3是英文数字模型
# 4是中英数轻量模型（中文识别精度高，识别快，如果ocr_ch识别不到，可以尝试该模型）

def ocr_chinese_by_eas(crop_pos_img_path, upload_image_log_tag=None):
    ocr_result_1 = ocr_image_by_eas(crop_pos_img_path, type=2, upload_image_log_tag=upload_image_log_tag)
    if ocr_result_1 is not None and len(ocr_result_1) > 0:
        monitor_print(f'---ocr_chinese_by_eas: {ocr_result_1}, type:2, image_path:{crop_pos_img_path}')
        return ocr_result_1

    ocr_result_2 = ocr_image_by_eas(crop_pos_img_path, type=4, upload_image_log_tag=upload_image_log_tag)
    if ocr_result_2 is not None and len(ocr_result_2) > 0:
        monitor_print(f'---ocr_chinese_by_eas: {ocr_result_2}, type:4, image_path:{crop_pos_img_path}')
        return ocr_result_2

    ocr_result_3 = ocr_image_by_eas(crop_pos_img_path, type=1, upload_image_log_tag=upload_image_log_tag)
    if ocr_result_3 is not None and len(ocr_result_3) > 0:
        monitor_print(f'---ocr_chinese_by_eas: {ocr_result_3}, type:1, image_path:{crop_pos_img_path}')
        return ocr_result_3


def ocr_num_by_eas(crop_pos_img_path, upload_image_log_tag=None):
    ocr_result_1 = ocr_image_by_eas(crop_pos_img_path, type=3, upload_image_log_tag=upload_image_log_tag)

    if ocr_result_1 is not None and len(ocr_result_1) > 0:
        monitor_print(f'---ocr_num_by_eas: {ocr_result_1}, type:3, image_path:{crop_pos_img_path}')
        return ocr_result_1

    ocr_result_2 = ocr_image_by_eas(crop_pos_img_path, type=2, upload_image_log_tag=upload_image_log_tag)
    if ocr_result_2 is not None and len(ocr_result_2) > 0:
        monitor_print(f'---ocr_num_by_eas: {ocr_result_2}, type:2, image_path:{crop_pos_img_path}')
        return ocr_result_2

    ocr_result_3 = ocr_image_by_eas(crop_pos_img_path, type=4, upload_image_log_tag=upload_image_log_tag)
    if ocr_result_3 is not None and len(ocr_result_3) > 0:
        monitor_print(f'---ocr_num_by_eas: {ocr_result_3}, type:4, image_path:{crop_pos_img_path}')
        return ocr_result_3

    ocr_result_4 = ocr_image_by_eas(crop_pos_img_path, type=1, upload_image_log_tag=upload_image_log_tag)
    if ocr_result_4 is not None and len(ocr_result_4) > 0:
        monitor_print(f'---ocr_num_by_eas: {ocr_result_4}, type:1, image_path:{crop_pos_img_path}')
        return ocr_result_4


# 注意type的类型对应不同的识别模型
# 1是旧的包含异形字的ocr模型，
# 2是中英数综合模型，通用的识别模型，实测针对标准字体类型2的识别率高很多
# 3是英文数字模型
# 4是中英数轻量模型（中文识别精度高，识别快，如果ocr_ch识别不到，可以尝试该模型）
def ocr_image_by_eas(crop_pos_img_path, type=1, upload_image_log_tag=None):
    monitor_print(f'---ocr_image_by_eas: {crop_pos_img_path}, type:{type}')
    env = AppEnv.get_instance()

    # cropFileName = f'crop_{cropFileName}' + str(int(time.time() * 1000000)) + '.jpg'
    #
    # crop_pos_img = crop_pos_image_from_snapshot(f"temp.jpg", cropFileName, crop_start, crop_end)

    # item_full_path = os.path.join(ST.LOG_DIR, cropFileName)

    def get_env_ocr_path(env, type=1):
        scriptEnv = env.scriptEnv
        risk_path = ""
        launch_type = env.launchType
        if launch_type == 'localtest':
            scriptEnv = 'local'

        if type == 1:
            if (scriptEnv == 'local'):
                risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
            elif (scriptEnv == 'pre'):
                risk_path = '/api/predict/lingxialgo_vision_adc'
            elif (scriptEnv == 'prod'):
                risk_path = '/api/predict/lingxialgo_vision_adc'
            else:
                risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
        else:
            if (scriptEnv == 'local'):
                risk_path = "/api/predict/lingxialgo_ocr_service_pre"
            elif (scriptEnv == 'pre'):
                risk_path = "/api/predict/lingxialgo_ocr_service_pre"
            elif (scriptEnv == 'prod'):
                risk_path = '/api/predict/lingxialgo_vision_ocr'
            else:
                risk_path = '/api/predict/lingxialgo_ocr_service_pre'

        monitor_print(f'---get_env_ocr_path: {risk_path}, type:{type}, env:{scriptEnv}')
        return risk_path

    def getOCRRequestDataWithURL(url, type=1):
        resData = {}
        resId = str(int(time.time() * 1000000))
        resData['requestId'] = resId
        resData['imageUrl'] = url
        resData['recoType'] = "ocr"

        if type == 2:
            resData['model'] = "ocr_ch"
        if type == 3:
            resData['model'] = "ocr_en"
        if type == 4:
            resData['model'] = "ocr_ch_mobile"

        monitor_print(f'---getOCRRequestDataWithURL: {resData}, type:{type}')
        return resData

    if not crop_pos_img_path.startswith("http"):
        localFileList = []
        localFileList.append(crop_pos_img_path)
        _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
        if cdn_url_list:
            qufu_crop_img_url = cdn_url_list[0]
        else:
            monitor_print(f'图片上传失败: {crop_pos_img_path}')
            return None
    else:
        qufu_crop_img_url = crop_pos_img_path

    if upload_image_log_tag is not None:
        monitor_print(f'---ocr_image_by_eas_url {upload_image_log_tag}: {qufu_crop_img_url}, type: {type}')
    else:
        monitor_print(f'---ocr_image_by_eas_url: {qufu_crop_img_url}, type: {type}')

    data = enhanced_easrequest(get_env_ocr_path(env, type=type), getOCRRequestDataWithURL(qufu_crop_img_url, type=type),
                               type=type)

    if data is not None and 'message' in data and ('status' in data['message']) and ('data' in data['message']):
        ocrResult = data['message']['data']
        status = data['message']['status']

        if upload_image_log_tag is not None:
            monitor_print(
                f'---ocr_image_by_eas_result {upload_image_log_tag}: {status},{type},{qufu_crop_img_url},{ocrResult}')
        else:
            monitor_print(f'---ocr_image_by_eas_result: {status},{type},{qufu_crop_img_url},{ocrResult}')
        return ocrResult
    else:
        if upload_image_log_tag is not None:
            monitor_print(f'---ocr_image_by_eas_result_none {upload_image_log_tag}: {type},{qufu_crop_img_url}')
        else:
            monitor_print(f'---ocr_image_by_eas_result_none: {type},{qufu_crop_img_url}')

        return None


def get_eas_host(type, preUseLocal=False):
    env = AppEnv.get_instance()
    scriptEnv = env.scriptEnv
    host = ""

    launch_type = env.launchType
    if launch_type == 'localtest':
        scriptEnv = 'local'

    if (scriptEnv == 'local'):
        host = 'http://eas-zhangbei-b.alibaba-inc.com'
    elif (scriptEnv == 'daily'):
        host = 'http://eas-zhangbei-b.alibaba-inc.com'
    elif (scriptEnv == 'pre'):
        host = 'http://eas-zhangbei-b-intranet.alibaba-inc.com'
        if preUseLocal:
            host = 'http://eas-zhangbei-b.alibaba-inc.com'
    elif (scriptEnv == 'prod'):
        ####
        ####
        host = 'http://eas-zhangbei-b-intranet.alibaba-inc.com'
    else:
        host = 'http://eas-zhangbei-b.alibaba-inc.com'

    monitor_print(f'---get_eas_host: {host}, type: {type}, env:{scriptEnv}')
    return host


def get_eas_token(type):
    access_token = 'NDI0ODI1OTgxZTRkZjM1Njk5MjAwMTZmYzA3Y2JlNDllZDQyNzE2NA=='
    if type == 1:
        access_token = 'NDI0ODI1OTgxZTRkZjM1Njk5MjAwMTZmYzA3Y2JlNDllZDQyNzE2NA=='
    else:
        access_token = 'bGluZ3hpYWxnb19vY3JfdG9rZW4K'

    monitor_print(f'---get_eas_token: {access_token}, type: {type}')
    return access_token


def enhanced_easrequest(canonicalizedresource, resData, type=1, is_break_runloop=False, preUseLocal=False, token=None):
    scriptEnv = AppEnv.get_instance().scriptEnv
    host = get_eas_host(type, preUseLocal)

    # resData = {"imageProperties":[{"propertyId":"史诗皮肤"}],"requestId":"7018857656240641028","imageUrl":"https://media-test.9game.cn/test/oss-android/239/adc_ocr_shishi_pifu_ocr_shishi_pifu_0_1703076957782571.jpg","recoType":"三国杀"}

    monitor_print(f'resData = {resData}')
    js = json.dumps(resData).strip()
    js = js.encode('utf-8')
    # canonicalizedresource = '/api/predict/lingxialgo_vision_adc'
    if token is not None:
        access_token = token
    else:
        access_token = get_eas_token(type)

    content_md5 = hashlib.md5(js).hexdigest()
    content_type = 'application/json'
    utcnow = datetime.datetime.now()
    current_time = utcnow.strftime('%a, %d %b %Y %H:%M:%S GMT')
    verb = 'POST'

    # auth = '%s\n%s\n%s\n%s\n%s' % (verb, content_md5, content_type, current_time, canonicalizedresource)

    url = '%s%s' % (host, canonicalizedresource)
    # monitor_print(f"---easRequest url: {url}")
    # url = 'http://eas-zhangbei-b.alibaba-inc.com/api/predict/lingxialgo_vision_adc'
    error_msg = None

    for i in range(3):
        try:
            req = urllib.request.Request(url, data=js)
            req.add_header('Content-MD5', content_md5)
            req.add_header('Date', current_time)
            req.add_header('Content-Type', content_type)
            req.add_header('Content-Length', '%d' % len(js))
            req.add_header('Authorization', access_token)
            response = urllib.request.urlopen(req)
            content = response.read()
            response.close()
            if response.status != 200:
                monitor_print(
                    f'---easRequest_url_response_fei200: {url} ---resData = {resData} ---eas content:{content}',
                    level=PRINT_LEVEL.INFO)
                monitor_print(response.content)
                # if is_break_runloop:
                #     lx_break_runloop(desc=f'OCR接口异常,响应非200')
                # return {}
                error_msg = f'---easRequest接口异常: 重试次数{i},响应非200'
            else:
                newData = content.decode('utf-8')
                json_object = json.loads(newData)
                monitor_print(
                    f"---easRequest_url_response_200: {url} ---resData = {resData} ------result:{json_object}",
                    level=PRINT_LEVEL.INFO)
                return json_object

        except Exception as e:
            monitor_print(
                f'---easRequest接口捕获到异常: 重试次数{i},{url} ---resData = {resData} ---request_remote_eas_url_fail: {e}',
                level=PRINT_LEVEL.ERROR)
            # if is_break_runloop:
            #     lx_break_runloop(desc=f'---easRequest接口捕获到异常: {e}')
            # return {}
            error_msg = f'---easRequest接口捕获到异常:重试次数{i},{url},{e}'

    if is_break_runloop:
        lx_break_runloop(desc=error_msg)
    return {}


def easRequest(canonicalizedresource, resData, is_break_runloop=False, preUseLocal=False, token=None):
    return enhanced_easrequest(canonicalizedresource, resData, type=1, is_break_runloop=is_break_runloop,
                               preUseLocal=preUseLocal, token=token)


def eas_ocr_check(data, url, output_dir, file_name, keys, size=25):
    """
    easRequest 返回的数据进行原图标记
    :param data: ocr识别返回参数 ["message"]["imagePropertyValues"][0]["value"]
    :param url: 网络路径或本地路径
    :param output_dir: 输出文件夹
    :param file_name: 文件名
    :param keys: 响应数据中的属性
    :param size: 画框文字的大小
    :return:
    """
    # data = data["message"]["imagePropertyValues"][0]["value"]
    # 使用 urllib 打开 URL
    launchType = AppEnv.get_instance().launchType
    if launchType != 'localtest':
        return
    if url.startswith("http"):
        resp = urllib.request.urlopen(url)
        # 读取返回的字节数据
        image_data = resp.read()
        # 将字节数据转换为 NumPy 数组
        image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
        # 将 NumPy 数组解码为 OpenCV 图像格式
        result_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    else:
        result_img = cv2.imread(url)
    font = ImageFont.truetype(font="STHeiti Light.ttc", size=size)
    image_pil = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    for index, item in enumerate(data):
        text = "_".join([str(item[i]) for i in keys])
        if "box" in item:
            draw.rectangle((tuple([int(i) for i in item["box"][0]]), tuple([int(i) for i in item["box"][2]])),
                           fill=None,
                           outline='red', width=5)
            draw.text([int(i) for i in item["box"][3]], text, font=font,
                      fill=(255, 0, 0))
        else:
            draw.text((10 * (index + 1), 10), text, font=font,
                      fill=(255, 0, 0))
    result_img = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(output_dir, f"{file_name}.jpg"), result_img)


# 针对adc_ocr的路径和入参的配置
def config_eas_adc_request_path():
    env = AppEnv.get_instance()
    scriptEnv = env.scriptEnv
    risk_path = ""
    launch_type = env.launchType
    if launch_type == 'localtest':
        scriptEnv = 'local'

    if (scriptEnv == 'local'):
        risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
    elif (scriptEnv == 'pre'):
        risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_adc'
    else:
        risk_path = '/api/predict/lingxialgo_adc_ocr_pre'

    return risk_path


def config_eas_adc_request_data(url, reco_type, img_property_values, need_box=False):
    resData = {}
    resId = str(int(time.time() * 1000000))
    resData['requestId'] = resId
    resData['imageUrl'] = url
    resData['recoType'] = reco_type
    resData['needBox'] = need_box
    resData['imageProperties'] = img_property_values

    ###### 适用于每个游戏的OCR的远端接口 ######
    ##示例如下：
    # {
    #   "imageProperties": [
    #     {
    #       "propertyId": "武将",
    #       "expCount":6,
    #       "optionList": [
    #         "贾诩 魏 S1"
    #       ]
    #     }
    #   ],
    #   "requestId": "7018857656240641028",
    #   "imageUrl": "https://media.9game.cn/adc/oss-android/109306/adc_result_hunshi_combined_1_1714647672895016.jpg",
    #   "recoType": "三国谋定天下",
    #   "needBox": false
    # }
    #
    # ##

    return resData


def request_game_ocr_by_eas(crop_file_path, game_name, image_properties, need_box=False):
    reco_type = game_name
    imageProperties = image_properties
    monitor_print(f'---request_game_ocr_by_eas_args:{crop_file_path},{reco_type},{need_box}', level=PRINT_LEVEL.INFO)

    localFileList = []
    localFileList.append(crop_file_path)
    _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
    ocr_crop_url = None
    if cdn_url_list is not None and len(cdn_url_list) > 0:
        ocr_crop_url = cdn_url_list[0]

    if ocr_crop_url is None:
        monitor_print(f'---request_game_ocr_by_eas_none_url:{crop_file_path}, {reco_type}', level=PRINT_LEVEL.ERROR)
        return (ocr_crop_url, None)

    env = AppEnv.get_instance()
    game_ocr_path = config_eas_adc_request_path()
    game_ocr_resdata = config_eas_adc_request_data(ocr_crop_url, reco_type, imageProperties, need_box)

    data = easRequest(game_ocr_path, game_ocr_resdata, is_break_runloop=True)
    monitor_print(f'---request_game_ocr_by_eas_resdata:{ocr_crop_url},{reco_type},{need_box}, result:{data}',
                  level=PRINT_LEVEL.INFO)

    message = data.get('message')
    status = message.get('status')
    if status == 1:
        monitor_print(f'---request_game_ocr_by_eas_status_1:{ocr_crop_url}, {reco_type}, {need_box}, result:{data}',
                      level=PRINT_LEVEL.INFO)

        image_property_values = message.get('imagePropertyValues')

        if image_property_values is None:
            monitor_print(
                f'---request_remote_eas_url_none_image_property_values:{ocr_crop_url}, {reco_type}, {need_box}  result:{data}',
                level=PRINT_LEVEL.ERROR)
        else:
            monitor_print(
                f'---request_game_ocr_by_eas_image_property_values:{ocr_crop_url}, {reco_type}, {need_box},result:{data}',
                level=PRINT_LEVEL.INFO)
        return (ocr_crop_url, image_property_values)
        # for index, item in enumerate(image_property_values):
        #     item_id = item.get('propertyId')
        #     if item_id == property_name:
        #         item_value_list = item.get('value')
        #         monitor_print(f'item_value_list:{item_value_list}')
        #         if item_value_list is not None:
        #             return item_value_list
    else:
        monitor_print(f'---request_game_ocr_by_eas_status_fei1:{ocr_crop_url}, {reco_type}, {need_box}, result:{data}',
                      level=PRINT_LEVEL.ERROR)

    return (ocr_crop_url, None)


# 针对service_ocr的路径和入参的配置

def config_eas_service_token():
    access_token = 'bGluZ3hpYWxnb19vY3JfdG9rZW4K'
    monitor_print(f'---config_eas_service_token: {access_token}')
    return access_token


def config_eas_service_request_path():
    env = AppEnv.get_instance()
    scriptEnv = env.scriptEnv
    risk_path = ""
    launch_type = env.launchType
    if launch_type == 'localtest':
        scriptEnv = 'local'

    if (scriptEnv == 'local'):
        risk_path = "/api/predict/lingxialgo_ocr_service_pre"
    elif (scriptEnv == 'pre'):
        risk_path = "/api/predict/lingxialgo_ocr_service_pre"
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_ocr'
    else:
        risk_path = '/api/predict/lingxialgo_ocr_service_pre'

    return risk_path


def config_eas_service_request_data(url, reco_type, model=None, imageProperties=None, need_box=False):
    resData = {}
    resId = str(int(time.time() * 1000000))
    resData['requestId'] = resId
    resData['imageUrl'] = url
    resData['recoType'] = reco_type
    if model is not None:
        resData['model'] = model

    if imageProperties is not None:
        resData['imageProperties'] = imageProperties
    return resData


# 用于风控的接口
def request_word_risk_by_eas(crop_file_path, reco_type, image_properties=None, need_box=False):
    imageProperties = image_properties
    monitor_print(f'---request_word_risk_by_eas_args:{crop_file_path},{reco_type},{need_box}', level=PRINT_LEVEL.INFO)

    start_time = time.perf_counter()
    localFileList = []
    localFileList.append(crop_file_path)
    _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
    ocr_crop_url = None
    if cdn_url_list is not None and len(cdn_url_list) > 0:
        ocr_crop_url = cdn_url_list[0]

    if ocr_crop_url is None:
        monitor_print(f'---request_word_risk_by_eas_none_url:{crop_file_path}, {reco_type}', level=PRINT_LEVEL.ERROR)
        return (ocr_crop_url, None)

    end_time = time.perf_counter()
    monitor_print(f"---request_word_risk_by_eas_oss:{end_time - start_time}")

    start_time = time.perf_counter()

    env = AppEnv.get_instance()
    game_ocr_path = config_eas_service_request_path()
    token = config_eas_service_token()
    game_ocr_resdata = config_eas_service_request_data(ocr_crop_url, reco_type, imageProperties, need_box)

    print(f'--xxxxxx:{ocr_crop_url}, {game_ocr_resdata}, {token}')
    data = easRequest(game_ocr_path, game_ocr_resdata, is_break_runloop=True, token=token)
    monitor_print(f'---request_word_risk_by_eas_resdata:{ocr_crop_url},{reco_type},{need_box}, result:{data}',
                  level=PRINT_LEVEL.INFO)

    message = data.get('message')
    status = message.get('status')
    image_property_values = None

    if status == 1:
        monitor_print(f'---request_word_risk_by_eas_status_1:{ocr_crop_url}, {reco_type}, {need_box}, result:{data}',
                      level=PRINT_LEVEL.INFO)

        image_property_values = message.get('data')

        if image_property_values is None:
            monitor_print(
                f'---request_word_risk_by_eas_url_none_image_property_values:{ocr_crop_url}, {reco_type}, {need_box}  result:{data}',
                level=PRINT_LEVEL.ERROR)
        else:
            monitor_print(
                f'---request_word_risk_by_eas_image_property_values:{ocr_crop_url}, {reco_type}, {need_box},result:{data}',
                level=PRINT_LEVEL.INFO)

    else:
        monitor_print(f'---request_word_risk_by_eas_status_fei1:{ocr_crop_url}, {reco_type}, {need_box}, result:{data}',
                      level=PRINT_LEVEL.ERROR)

    end_time = time.perf_counter()
    monitor_print(f"---request_word_risk_by_eas_ocr:{end_time - start_time}")
    return (ocr_crop_url, image_property_values)


## adc_deepseek能力接口

def config_ds_service_token():
    access_token = 'bGluZ3hpYWxnb19sbG1fYWRjX3Rva2VuCg=='
    monitor_print(f'---config_ds_service_token: {access_token}')
    return access_token


def config_ds_service_request_path():
    env = AppEnv.get_instance()
    scriptEnv = env.scriptEnv
    risk_path = ""
    launch_type = env.launchType
    if launch_type == 'localtest':
        scriptEnv = 'local'

    if (scriptEnv == 'local'):
        risk_path = "/api/predict/lingxialgo_llm_adc_pre"
    elif (scriptEnv == 'pre'):
        risk_path = "/api/predict/lingxialgo_llm_adc_pre"
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_llm_adc'
    else:
        risk_path = '/api/predict/lingxialgo_llm_adc_pre'

    return risk_path


def config_ds_service_request_data(reco_type, agentId, input_content, model=None):
    resData = {}
    resId = str(int(time.time() * 1000000))
    resData['requestId'] = resId
    resData['agentId'] = agentId
    resData['recoType'] = reco_type
    resData['input'] = input_content
    if model is not None:
        resData['model'] = model

    return resData


def get_remote_ds_r1_agentid(agentid_des):
    if agentid_des == '智能区服':
        return '73402dfcd0a54a34a47fd7cca38c25d3'


def remote_ds_r1_reasoning(agentId, input_content, model=''):
    start_time = time.perf_counter()

    env = AppEnv.get_instance()
    game_ocr_path = config_ds_service_request_path()
    token = config_ds_service_token()
    reco_type = '大模型应用'
    game_ocr_resdata = config_ds_service_request_data(reco_type, agentId, input_content, model=model)

    monitor_print(f'--remote_ds_r1_reasoning:{reco_type}, {agentId}, {input_content}, {token}')
    data = easRequest(game_ocr_path, game_ocr_resdata, is_break_runloop=True, token=token)
    monitor_print(f'---remote_ds_r1_reasoning_resdata:{reco_type},{game_ocr_resdata}, result:{data}',
                  level=PRINT_LEVEL.INFO)

    message = data.get('message')
    status = message.get('status')
    image_property_values = None

    if status == 1:
        monitor_print(f'---remote_ds_r1_reasoning: {reco_type}, {game_ocr_resdata}, result:{data}',
                      level=PRINT_LEVEL.INFO)

        output_values = message.get('output')

        if output_values is None:
            monitor_print(
                f'---remote_ds_r1_reasoning_output_none:{reco_type}, {game_ocr_resdata}  result:{data}',
                level=PRINT_LEVEL.ERROR)
            return None
        else:
            monitor_print(
                f'---remote_ds_r1_reasoning_output: {reco_type}, {game_ocr_resdata} result:{data}',
                level=PRINT_LEVEL.INFO)
            return output_values
        # for index, item in enumerate(image_property_values):
        #     item_id = item.get('propertyId')
        #     if item_id == property_name:
        #         item_value_list = item.get('value')
        #         monitor_print(f'item_value_list:{item_value_list}')
        #         if item_value_list is not None:
        #             return item_value_list
    else:
        monitor_print(f'---remote_ds_r1_reasoning_fail: {reco_type}, {game_ocr_resdata}, result:{data}',
                      level=PRINT_LEVEL.ERROR)
        return None


def remote_ai_helper(image_url, task_enter):
    start_time = time.perf_counter()

    env = AppEnv.get_instance()
    game_ocr_path = config_ds_service_request_path()

    token = config_ds_service_token()
    reco_type = 'agent'

    game_ocr_resdata = {}
    resId = str(int(time.time() * 1000000))
    game_ocr_resdata['requestId'] = resId
    game_ocr_resdata['recoType'] = reco_type
    game_ocr_resdata['imageUrl'] = image_url
    game_ocr_resdata['task'] = task_enter

    monitor_print(f'--remote_ai_helper_request:{reco_type}, {token}, {game_ocr_resdata}')
    data = easRequest(game_ocr_path, game_ocr_resdata, is_break_runloop=True, token=token)
    monitor_print(f'---request_remote_ai_helper_result:{reco_type},{game_ocr_resdata}, result:{data}',
                  level=PRINT_LEVEL.INFO)

    message = data.get('message')
    code = data.get('code')

    if message is None or code != 200:
        return None

    action = message.get('action')
    status = message.get('status')

    if status == 1:
        monitor_print(f'---request_remote_ai_helper_status_1: {reco_type}, {game_ocr_resdata}, result:{data}',
                      level=PRINT_LEVEL.INFO)

        return message
    else:
        monitor_print(f'---request_remote_ai_helper_fail: {reco_type}, {game_ocr_resdata}, result:{data}',
                      level=PRINT_LEVEL.ERROR)
        return None


if __name__ == '__main__':
    res = ocr_image_by_eas(
        "https://static.jiaoyimao.com/jym-oss/resource/vmos/20250508/adc_5964961/adc_catch_phase_16_after_1746698758498445.jpg",
        type=1)
    print(res)
