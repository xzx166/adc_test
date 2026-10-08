# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

from airtest.core.api import *

import json
import itertools

from enum import Enum


from utility.base.adc_api import *
from utility.base.adc_monitor import *

import requests

from utility.base.adc_network import *


class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def post(self, endpoint, headers=None, json=None, data=None, params=None):
        url = self.base_url + endpoint
        try:
            response = requests.post(url, headers=headers, json=json, data=data, params=params)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            monitor_print(f"---HttpClient_post_exception: {e}")
            return None

    def get(self, endpoint, headers=None, params=None):
        url = self.base_url + endpoint
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            monitor_print(f"---HttpClient_get_exception: {e}")
            return None


# 用于实现公用的业务请求
def upload_propreties_with_data(game_id,game_platform,data,images, addParams=False,isFromCollectTask=True,isNeedShenpi=True,taskIdList=[], status=None):
    env = AppEnv.get_instance()
    host = get_env_host(env)
    url = "http://{}/task/uploadGamePropertyData".format(host)

    payload = {
                "game_id" : str(game_id),
                "game_platform" : str(game_platform),
                "delta_game_data" : data,
                "image_list": images
            }
    if status:
        payload["status"] = status

    if addParams:
        payload["is_from_collect_task"] = isFromCollectTask
        payload["is_need_shenpi"] = isNeedShenpi
        payload["task_id_list"] = taskIdList

    monitor_print(f"uploadGamePropertyData ------ payload text: {payload}")
    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            launchType = env.launchType
            if (launchType != 'localtest'):
                monitor_print(f"upload_propreties_with_data_end ------ response text: {response.text}")
            return response.json()
        except Exception as e:
            monitor_print(f"upload_propreties_with_data ------response_error:{i}, {str(e)}")
    return None


class PhoneCaptchaSendStatus(Enum):
    SUCCESS = 1  #
    FAIL = 2  #


def phone_captcha_send_captcha(send_status, captcha_task_map=None, need_captcha=False, display_info=None):
    env = AppEnv.get_instance()

    host = get_env_host(env)
    url = "http://{}/task/reportCaptchaTask".format(host)

    payload = {"taskId": int(env.taskId), "sendStatus": send_status}

    if captcha_task_map:
        payload.update(captcha_task_map)

    if need_captcha == True:
        payload.update({"needCaptcha": need_captcha})

    if display_info is not None:
        payload.update({"displayInfo": display_info})

    monitor_print(f"---phone_login_send_captcha_payload:{payload}")

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            launchType = env.launchType
            if (launchType != 'localtest'):
                monitor_print(f"phone_login_send_captcha_end ------ response text: {response.text}")

            AppPerformanceInfo.get_instance().setTimeDurationMap('captcha_time', duration_start=False)

            return response.json()
        except Exception as e:
            monitor_print(f"phone_login_send_captcha ------response_error:{i}, {str(e)}")

    return None

class PhoneCaptchaVerifyStatus(Enum):
    SUCCESS = 1  #
    FAIL = 2  #

def phone_captcha_verify_captcha(verify_status, captcha_task_map=None, need_captcha=False, display_info=None):
    env = AppEnv.get_instance()

    host = get_env_host(env)
    url = "http://{}/task/reportCaptchaTask".format(host)

    payload = {"taskId": int(env.taskId), "verifyStatus": verify_status}
    if captcha_task_map:
        payload.update(captcha_task_map)

    if need_captcha == True:
        payload.update({"needCaptcha": need_captcha})

    if display_info is not None:
        payload.update({"displayInfo": display_info})

    monitor_print(f"---phone_login_verify_captcha_payload:{payload}")

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            launchType = env.launchType
            if (launchType != 'localtest'):
                monitor_print(f"phone_login_verify_captcha_end ------ response text: {response.text}")

            return response.json()
        except Exception as e:
            monitor_print(f"phone_login_verify_captcha ------response_error:{i}, {str(e)}")

    return None

def upload_biz_qufu_data(game_id, game_platform, is_for_all_platform, delta_qufu_data, image_list=None):
    env = AppEnv.get_instance()

    host = get_env_host(env)
    url = "http://{}/task/uploadBizQufuData".format(host)

    payload = {"taskId": int(env.taskId), "game_id": game_id, "game_platform": game_platform,
               "is_for_all_platform": is_for_all_platform, "delta_qufu_data": delta_qufu_data}
    if image_list:
        payload.update({"image_list": image_list})

    monitor_print(f"---upload_biz_qufu_data_payload:{url},{payload}")

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            launchType = env.launchType
            if (launchType != 'localtest'):
                monitor_print(f"---upload_biz_qufu_data_end ------ response text: {response.text}")

            return response.json()
        except Exception as e:
            monitor_print(f"---upload_biz_qufu_data_response_error:{i}, {str(e)}")

    return None

def get_domain_and_server_status(game_id, server_name,  domain_name=None):
    env = AppEnv.get_instance()
    host = get_env_host(env)
    url = "http://{}/task/checkGameServerNameAndDomain".format(host)
    payload = {"oldGameId": game_id, "gameServerName": server_name}
    if domain_name is not None:
        payload.update({"domainName": domain_name})
    monitor_print(f"---get_domain_and_server_status_payload:{url},{payload}")
    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            launchType = env.launchType
            if (launchType != 'localtest'):
                monitor_print(f"---get_domain_and_server_status_end_response_text: {response.text}")
            return response.json()
        except Exception as e:
            monitor_print(f"---get_domain_and_server_status_response_error:{i}, {str(e)}")
    return None

def get_game_zhandou_info(start_time, end_time, log_type=1011):
    env = AppEnv.get_instance()
    host = get_env_host(env, custom_env_type='pre')
    url = "http://{}/task/queryAdcLog".format(host)
    # 这里必须是ms时间戳
    payload = {"startTime": start_time, "endTime": end_time, 'logType': log_type}

    monitor_print(f"---get_game_zhandou_info:{url},{payload}")
    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            launchType = env.launchType
            if (launchType != 'localtest'):
                monitor_print(f"---get_game_zhandou_info_response_text: {response.text}")
            return response.json()
        except Exception as e:
            monitor_print(f"---get_game_zhandou_info_response_error:{i}, {str(e)}")
    return None


# 下载服务器列表
def download_qufu_list(gameId, clientId):
    ENV = AppEnv.get_instance()
    if ENV.scriptEnv in ['local', 'daily', 'pre']:
        host = 'pre-adc-pc.alibaba-inc.com'
    else:
        host = 'adc-pc.alibaba-inc.com'
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
        monitor_task_status_v2("拉取远程区服参数", f"{gameId}  {clientId}")
        payload["page"] = page
        monitor_print(f"---download_qufu_list_payload:{url},{payload}")
        res = requests.post(url, json=payload, verify=False)
        data = res.json().get("data")
        monitor_task_status_v2("拉取远程区服res", f"{ res.json()} ")
        if single_page_server_list := json.loads(data).get("result"):
            server_list.extend(single_page_server_list)
        else:
            return server_list

# 这里的status标识提交状态，0是未提交，1是已提交
def update_qufu_list(game_id, platform, client_id, delta_qufu_data, image_list, status=0):
    ENV = AppEnv.get_instance()
    if ENV.scriptEnv in ['local', 'daily', 'pre']:
        host = 'pre-adc-pc.alibaba-inc.com'
    else:
        host = 'adc-pc.alibaba-inc.com'
    url = f"http://{host}/task/uploadQufuUpdateData"
    payload = {
        "game_id": game_id,
        "game_platform": platform,
        "game_client_id": client_id,
        "delta_qufu_data": delta_qufu_data,
        "image_list": image_list,
        "status": status,
    }

    monitor_print(f"---update_qufu_list_payload:{url},{payload}")
    monitor_task_status_v2(f"update_server_payload", str(payload))
    res = requests.post(url, json=payload, verify=False)
    return res.json()

def update_qufu_list_to_jym(new_game_id,  delta_qufu_data):
    ENV = AppEnv.get_instance()
    if ENV.scriptEnv in ['local', 'daily', 'pre']:
        host = 'pre-adc-pc.alibaba-inc.com'
    else:
        host = 'adc-pc.alibaba-inc.com'
    url = f"http://{host}/task/syncGameServerByGameIdClientIdDomainId"
    payload = {
        "newGameId": new_game_id,
        "requests": delta_qufu_data,
    }

    monitor_print(f"---update_qufu_list_to_jym:{url},{payload}")
    monitor_task_status_v2(f"update_qufu_list_to_jym", str(payload))
    res = requests.post(url, json=payload, verify=False)
    monitor_print(f"---update_qufu_list_to_jym_res:{res.text}")
    monitor_print(f"---update_qufu_list_to_jym_res:{res}")
    return res.json()

def submit_sanmou_battleLog(battle_info):
    ENV = AppEnv.get_instance()
    if ENV.scriptEnv in ['local', 'daily', 'pre']:
        # host = 'test-adc-pc.alibaba.net'
        host = 'pre-adc-pc.alibaba-inc.com'
    else:
        host = 'adc-pc.alibaba-inc.com'
    url = f"http://{host}/task/submitSanmouBattleLog"
    payload = battle_info

    monitor_print(f"---submit_sanmou_battleLog:{url},{payload}")
    monitor_task_status_v2(f"submit_sanmou_battleLog", str(payload))
    res = requests.post(url, json=payload, verify=False)
    monitor_print(f"---submit_sanmou_battleLog_res:{res.text}")
    return res.json()

def get_newgameid_by_oldgameid(old_game_id):
    ENV = AppEnv.get_instance()
    if ENV.scriptEnv in ['local', 'daily', 'pre']:
        host = 'pre-adc-pc.alibaba-inc.com'
    else:
        host = 'adc-pc.alibaba-inc.com'
    url = f"http://{host}/task/getNewGameIdByOldGameId"
    payload = {
        "oldGameId": old_game_id
    }

    monitor_print(f"---get_newgameid_by_oldgameid:{url},{payload}")
    monitor_task_status_v2(f"get_newgameid_by_oldgameid", str(payload))
    res = requests.post(url, json=payload, verify=False)
    # monitor_print(f"---get_newgameid_by_oldgameid_res:{res.text}")
    monitor_print(f"---get_newgameid_by_oldgameid_res:{res}")
    res_object = res.json()
    if res_object is not None:
        if res_object.get("success") is True:
            res_data = res_object.get("data")
            if res_data is not None:
                res_data_object = json.loads(res_data)
                res_result = res_data_object.get("result")
                if res_result is not None:
                    return res_result

    return None

def get_cur_game_name():
    env = AppEnv.get_instance()

    result = adc_server_request("/gameslist/getGamesList")
    if result is not None:
        all_groups = result['data']['allGroups']

        game_dir = env.gameDir
        parts = game_dir.split('_')
        cur_game_id = parts[0]

        for group in all_groups:
            if cur_game_id == group['gameId']:
                return group['gameName']

    return None

# 上报错误信息和任务结果
def monitor_report_task_info(env, taskStatus, imgs=None, seller_imgs=None, inspect_properties=None, properties=None, sanmou_result=None):
    host = get_env_host(env)
    url = "http://{}/task/reportTask".format(host)


    payload = {"taskId": env.taskId, "taskStatus": taskStatus}
    if imgs and len(imgs) > 0:
        payload = {"taskId": env.taskId, "taskStatus": taskStatus,"images": imgs }

    if seller_imgs and len(seller_imgs) > 0:
        payload['sellerImages'] = seller_imgs

    if inspect_properties:
        payload['inspectProperties'] = inspect_properties
        # 处理腾讯游戏为正常ocr的图片信息
        if "unRecognizePicList" in inspect_properties:
            un_recognize_pic_list = inspect_properties.pop("unRecognizePicList")
            if un_recognize_pic_list or len(un_recognize_pic_list) > 0:
                payload['unRecognizePicList'] = un_recognize_pic_list


    ENV = AppEnv.get_instance()
    needCheck = False
    if is_valid_json(ENV.account_attr):
        if CLOUD_GAME_RESINFO := json.loads(ENV.account_attr).get("CLOUD_GAME_RESINFO"):
            if CLOUD_GAME_RESINFO is not None:
                if json.loads(CLOUD_GAME_RESINFO).get("MIXED_CAPTURE_TASK"):
                    monitor_task_status_v2(title="MIXED_CAPTURE_TASK,米哈游混合采集", desc="开始")
                    if properties:
                        needCheck = True
                else:
                    monitor_task_status_v2(title="米哈游混合采集-MIXED_CAPTURE_TASK获取失败", desc="结束")

    if properties:
        if needCheck:
            payload['properties'] = json.dumps(properties, ensure_ascii=False)
        else:
            payload['properties'] = json.dumps(properties, ensure_ascii=False)

    if sanmou_result:
        payload['sanmouResult'] = json.dumps(sanmou_result, ensure_ascii=False)

    monitor_print(f"monitor_report_task_info_start_url: {url}, payload: {payload}")
    monitor_task_status_v2(f"monitor_report_task_info", f"monitor_report_task_info_start_url: {url}, payload: {payload}")

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            monitor_print(f"monitor_report_task_info------response: {response}")
            monitor_print(f"monitor_report_task_info end   ------ response url: {response.url}")
            launchType = env.launchType
            if (launchType != 'localtest'):
                monitor_print(f"monitor_report_task_info end   ------ response text: {response.text}")

            monitor_task_status_v2(f"monitor_report_task_info_response_json: {response.text}, {response.status_code}")
            return response.json()
        except Exception as e:
            monitor_print(f"monitor_report_task_info------response_error:{i}  {str(e)}")

    # print('updateTaskStatus:'+ str(response) + url)
    return None


def report_mcp_task(params):
    monitor_print(f"---report_mcp_task_request: {params}")
    result = adc_server_request("task/reportMCPTask", request_type="post", params=params)
    if result is not None:
        monitor_print(f"---report_mcp_task_response: {result}")
        return result

    return None


"""
 * 监控游戏属性差异
 * @param log_type 日志类型，对于上报多子属性差异的，使用1007
 * @param phase_tag  业务类型，比如是武将差异
 * @param src_property  多子属性源数据的值
 * @param local_property  本地识别出来的值
 * @return
 """
def monitor_game_properties_difference(log_type, phase_tag=None, src_property=None, local_property=None):
    new_message = {}
    if phase_tag:
        new_message['tag'] = phase_tag

    if src_property:
        new_message['src_property'] = src_property

    if local_property:
        new_message['local_property'] = local_property

    monitor_print(f'---monitor_game_properties_difference:{log_type},{phase_tag},{src_property},{local_property}')

    return monitor_task_flow_status_info(log_type,new_message)

# 上报任务流状态信息, uploadLog接口
# log_type: 1007 多子属性源数据和本地数据不同
def monitor_task_flow_status_info(log_type,message=None):
    # task_id;log_type;message; timestamp
    env = AppEnv.get_instance()
    host = get_env_host(env)
    if env.scriptEnv in ['local', 'daily']:
        host = 'test-adc-pc.alibaba.net'
    elif env.scriptEnv == 'pre':
        host = 'pre-adc-pc.alibaba-inc.com'
    else:
        host = 'adc-pc.alibaba-inc.com'

    url = "http://{}/task/uploadLog".format(host)
    game_id = env.game_id
    game_platform = env.game_platfrom

    real_task_id = env.taskId

    new_message = {"game_dir":env.gameDir, "game_id": game_id, "game_platform": game_platform}

    if message and len(message) > 0:
        if isinstance(message, str):
            new_message['msg'] = message
        else:
            new_message.update(message)


    the_time = int(time.time()*1000)
    payload = {"task_id": real_task_id, "log_type": log_type,"message": json.dumps(new_message, ensure_ascii=False), "timestamp": the_time}

    monitor_print(f"monitor_task_flow_status_info_start_url: {url} payload: {payload}")
    response = None
    try:
        response = requests.post(url, json=payload)
        monitor_print(f"monitor_task_flow_status_info_response: {response}")
        monitor_print(f"monitor_task_flow_status_info_end_response_url: {response.url}")
        # monitor_print(f"monitor_task_flow_status_info_end_response_text: {response.text}")

        return response.json()
    except Exception as e:
        monitor_print(f"monitor_task_flow_status_info_response_error: {str(e)}")

    # print('updateTaskStatus:'+ str(response) + url)
    return None


def get_game_proerties_by_task(task_id=None):
    env = AppEnv.get_instance()

    # if env.scriptEnv in ['local', 'daily', 'pre']:
    #     host = 'pre-adc-pc.alibaba-inc.com'
    # else:
    #     host = 'adc-pc.alibaba-inc.com'

    host = get_env_host(env)

    url = "http://{}/task/getGamePropertiesByTaskId".format(host)

    monitor_print(f"monitor_get_game_proerties_start_url: {url}")
    real_task_id = env.taskId
    if task_id:
        real_task_id = task_id

    the_time = int(time.time()*1000)
    payload = {"taskId": real_task_id, "timestamp": the_time}

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)
            monitor_print(f"get_game_proerties_by_task------response: {response}")
            # monitor_print(f"get_game_proerties_by_task end   ------ response url: {response.url}")
            # monitor_print(f"get_game_proerties_by_task end   ------ response text: {response.text}")
            return response.json()
        except Exception as e:
            monitor_print(f"get_game_proerties_by_task_response_error:{i} {str(e)}")
    # print('updateTaskStatus:'+ str(response) + url)
    return None

def monitor_get_game_name():
    env = AppEnv.get_instance()

    launchType = env.launchType
    if (launchType == 'localtest'):
        return

    host= get_env_host(env)

    url = "http://{}/gameslist/getGamesList".format(host)


    # timestamp = time.time()*1000000
    # info = title + '+' + desc
    # monitor_print(info, timestamp)

    # payload = {"taskId": env.taskId, "taskStatus": taskStatus, "title": title, "description":desc, 'timestamp': int(time.time()*1000000)}
    payload = {}
    monitor_print(f"monitor_get_game_name start ------ url: {url}")
    response = None
    try:
        response = requests.get(url, params=payload)
        monitor_print(f"monitor_get_game_name_response: {response}")
        monitor_print(f"monitor_get_game_name_response_json: {response.json()}")
        result = response.json()
        all_groups = result['data']['allGroups']

        game_dir = env.gameDir
        parts = game_dir.split('_')
        cur_game_id = parts[0]

        for group in all_groups:
            if cur_game_id == group['gameId']:
                return group['gameName']
    except Exception as e:
        monitor_print(f"monitor_get_game_name_response_error: {str(e)}")

    # print('updateTaskStatus:'+ str(response) + url)
    return None


class DomainServerModel:
    def __init__(self, real_game_area,real_game_qu=None, max_count=5, is_for_all_platform=True, image_list=None, report_count=None):
        self.real_game_qu = real_game_qu
        self.real_game_area = real_game_area
        self.is_for_all_platform = is_for_all_platform
        self.image_list = image_list
        self.max_count = max_count
        self.report_count = report_count


def get_domain_and_server_info(model):
    env = AppEnv.get_instance()
    game_area = env.game_area
    game_qu = env.get_account_attr_with_key('DOMAIN_NAME')
    seller_info = {}

    real_game_area = model.real_game_area
    real_game_qu = model.real_game_qu
    is_for_all_platform = model.is_for_all_platform

    monitor_print(f"---app_will_process_sellers_origin_info: {game_qu}, {game_area}, {real_game_qu}, {real_game_area}")

    # real_game_area = 'S2-009test'
    if game_qu != real_game_qu or game_area != real_game_area:
        monitor_print(f"---app_will_process_sellers: 区服信息不一致")
        monitor_task_status_v2("区服信息不一致", "")

        game_id = env.game_id
        game_platform = env.game_platfrom

        # 在区和服都存在的情况下，这个的区服信息直接回传交易猫，用于展示区服信息
        status_result = get_domain_and_server_status(game_id, real_game_area, real_game_qu)
        monitor_print(f"---get_domain_and_server_status_from_result: {status_result}")
        status_data_json = None
        if status_result is not None and 'data' in status_result:
            status_data_json = status_result.get('data')
        if status_data_json is not None:
            status_data_object = json.loads(status_data_json)
            status_map = status_data_object.get('result')
            domain_status = status_map.get('domainNameExist')
            server_status = status_map.get('gameServerNameExist')
            if real_game_qu is None or len(real_game_qu) == 0:
                if server_status == True:
                    monitor_print(f"---app_will_process_sellers_domain_server_status: {domain_status}, {server_status}")
                    seller_info['gameArea'] = real_game_area
                    monitor_task_flow_status_info(1012, seller_info)
                    return seller_info
            else:
                if domain_status == True and server_status == True:
                    monitor_print(f"---app_will_process_sellers_domain_server_status: {domain_status}, {server_status}")
                    seller_info['gameArea'] = real_game_area
                    seller_info['syncNewDomainName'] = real_game_qu
                    monitor_task_flow_status_info(1012, seller_info)
                    return seller_info
        else:
            monitor_print(f"---get_domain_and_server_status_from_result_error: {status_result}")

        max_count = model.max_count
        report_count = model.report_count
        if report_count is not None and report_count > 0:
            if report_count >= max_count:
                lx_break_app("区服上报次数必须小于max_count阈值")

        qufu_data = {'gameArea': real_game_area}
        if real_game_qu is not None and len(real_game_qu) > 0:
            qufu_data['syncNewDomainName'] = real_game_qu
        # qufu_data_json = json.dumps(qufu_data)

        image_list = model.image_list
        result = upload_biz_qufu_data(game_id, game_platform, is_for_all_platform=is_for_all_platform, delta_qufu_data=qufu_data, image_list=image_list)
        monitor_print(f"---app_will_process_sellers_result:  {result}")
        suc = result.get('success')
        if suc == True:
            result_data_map = result.get('result').get('data')
            result_count = result_data_map.get('count')
            if report_count is not None:
                if report_count == 0:
                    monitor_print(f"qufu_huitian_report_count_{game_id}: {result_count} {result_data_map}")
                elif result_count >= report_count and result_count < max_count:
                    # 场景命名（gameid）；
                    monitor_print(f"qufu_huitian_report_count_{game_id}: {result_count} {result_data_map}")

            if result_count >= max_count:
                seller_info['gameArea'] = real_game_area
                if real_game_qu is not None and len(real_game_qu) > 0:
                    seller_info['syncNewDomainName'] = real_game_qu
                monitor_print(f"qufu_huitian_jiaoyimao_{game_id}: {result_count} {result_data_map}")
                monitor_task_flow_status_info(1012, seller_info)
                return seller_info


    monitor_print(f"---app_will_process_sellers_info: {seller_info}")
    return seller_info
