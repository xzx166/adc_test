import datetime
import hashlib
import json
import time
import urllib
from pprint import pprint
from typing import Iterable

import requests

from utility.biz_utils.biz_tools import timeStamp, area2pos
from utility.base.adc_environment import AppEnv
from utility.base.adc_monitor import monitor_print

ENV = AppEnv.get_instance()
def image_ocr(imageurl: str, model=2, needBox=True):
    """
    文字识别
    :param imageurl: 图片链接
    :param model: 识别模型
        1-旧的包含异形字的ocr模型，
        2-中英数综合模型，通用的识别模型，实测针对标准字体类型2的识别率高很多
        3-英文数字模型
        4-中英数轻量模型（中文识别精度高，识别快，如果ocr_ch识别不到，可以尝试该模型）
    :param needBox: 是否需要检测
    :return: 识别结果
    """
    if ENV.launchType != "localtest" and ENV.scriptEnv in ["prod", "pre"]:
        host = "http://eas-zhangbei-b-intranet.alibaba-inc.com"
    else:
        host = "http://eas-zhangbei-b.alibaba-inc.com"

    if not (1 <= model <= 4):
        model = 2

    if model == 1:
        if ENV.scriptEnv in ["prod", "pre"]:
            ocrUrl = f"{host}/api/predict/lingxialgo_vision_adc"
        else:
            ocrUrl = f"{host}/api/predict/lingxialgo_adc_ocr_pre"
    else:
        if ENV.scriptEnv == "prod":
            ocrUrl = f"{host}/api/predict/lingxialgo_vision_ocr"
        else:
            ocrUrl = f"{host}/api/predict/lingxialgo_ocr_service_pre"

    # 构建请求体
    payload = {
        "caller": "adc",
        "requestId": timeStamp(),
        "imageUrl": imageurl,
        "recoType": "ocr",
        "det": needBox  # model==1，默认返回box
    }

    if model == 2:
        payload["model"] = "ocr_ch"
    elif model == 3:
        payload["model"] = "ocr_en"
    elif model == 4:
        payload["model"] = "ocr_ch_mobile"

    # 构建请求头
    js = json.dumps(payload).strip()
    js = js.encode('utf-8')
    content_md5 = hashlib.md5(js).hexdigest()
    utcnow = datetime.datetime.now()
    current_time = utcnow.strftime('%a, %d %b %Y %H:%M:%S GMT')
    if model == 1:
        access_token = 'NDI0ODI1OTgxZTRkZjM1Njk5MjAwMTZmYzA3Y2JlNDllZDQyNzE2NA=='
    else:
        access_token = 'bGluZ3hpYWxnb19vY3JfdG9rZW4K'

    session = requests.session()
    session.headers.update({
        'Content-MD5': content_md5,
        'Date': current_time,
        'Content-Type': 'application/json',
        'Content-Length': str(len(js)),
        'Authorization': access_token
    })

    response = session.post(ocrUrl, json=payload)
    try:
        result = response.json()
        payload_json = json.dumps(payload, ensure_ascii=False)
        result_json = json.dumps(result, ensure_ascii=False)
        monitor_print(f"---ocr_request: {ocrUrl}, model: {model}, payload: {payload_json}, result: {result_json}")
        return result['message']['data'] or []

    except Exception as e:
        monitor_print(response.text)
        return []

def ocr_data_process(ocr_data):
    """
    OCR数据处理
    :param ocr_data: OCR数据
    :return: OCR数据
    """
    ocr_data_new = []
    for item in ocr_data:
        txts = item.get("txts")
        if not txts:
            continue
        if box := item.get("box"):
            lt = (int(box[0][0]), int(box[0][1]))
            rb = (int(box[2][0]), int(box[2][1]))
            area = (*lt, *rb)
            ocr_data_new.append({
                "txts": txts,
                "area": area,
                "pos": area2pos(area),
            })
        else:
            ocr_data_new.append({"txts": txts})

    return ocr_data_new

def ocr_result_merge(ocr_result_list):
    """OCR结果合并
    :param ocr_result_list: OCR结果
    :return: OCR结果
    """
    text = "".join(map(lambda x: x["txts"], ocr_result_list or [])).strip()
    return text

def multi_model_ocr_v2(imageurl: str, options, match_func=None):
    """
    多模型文字识别
    :param imageurl: 图片链接
    :param options: 匹配项
    :param match_func: 匹配方法
    :return: 识别结果
    状态码说明:
    1: 识别正确
    2: 模型识别一致, 但是结果不在匹配项中
    0: 模型识别不一致
    -1: 识别结果为空
    """
    wrong_list = []
    match_item = None
    for model in [2, 1, 4]:
        ocr_result_list = image_ocr(imageurl, model=model)
        ocr_result = ocr_result_merge(ocr_result_list)
        monitor_print(f"---multi_model_ocr_v2: imageurl: {imageurl}, model: {model:}, ocr_result:{ocr_result}")
        if ocr_result in options:
            return {"status": 1, "result": ocr_result}
        elif callable(match_func):
            match_item = match_func(ocr_result)
            if isinstance(match_item, str):
                if match_item in options:
                    return {"status": 1, "result": match_item}
                elif match_item != ocr_result:
                    return {"status": 2, "result": match_item}

            elif isinstance(match_item, Iterable):
                for i in match_item:
                    if i in options:
                        return {"status": 1, "result": i}

        if ocr_result and ocr_result not in wrong_list:
            wrong_list.append(ocr_result)

    if wrong_list:
        # 使用替换匹配项
        if isinstance(match_item, str):
            return {"status": 2, "result": match_item}
        # 模型识别一致
        elif len(wrong_list) == 1:
            return {"status": 2, "result": wrong_list[0]}
        # 模型识别不一致
        else:
            return {"status": 0, "result": wrong_list[0], "wrong_list": wrong_list}
    else:
        return {"status": -1, "result": "", "wrong_list": []}

if __name__ == '__main__':
    # url = "https://static.jiaoyimao.com/jym-oss/resource/vmos/20260309/adc_15270216/upload_枪皮ocr-手枪4_1773039097188912.jpg"
    url = "https://static.jiaoyimao.com/jym-oss/resource/vmos/20260309/adc_15270216/upload_枪皮ocr-近战2_1773039116908820.jpg"
    ocr_list = image_ocr(url, model=2)
    # odp = ocr_data_process(ocr_list)
    print(ocr_result_merge(ocr_list))
    # title_list, desc_list = [], []
    # title_check = False
    # for i in odp:
    #     if i["height"] < 25 and not title_check:
    #         continue
    #     elif i["height"] > 25:
    #         title_list.append(i["txts"])
    #         title_check = True
    #     else:
    #         desc_list.append(i["txts"])
    #
    # title = "".join(title_list)
    # desc = "".join(desc_list)
    # print(f"{title=}, {desc=}")
