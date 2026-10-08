# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

import json
import requests

from utility.base.adc_environment import *
from utility.base.adc_monitor import *

# ------------adc自有服务接口------------------
def get_adc_server_host(env, custom_env_type=None):
    scriptEnv = env.scriptEnv
    if custom_env_type is not None:
        scriptEnv = custom_env_type
    host=""
    if (scriptEnv == 'local'):
        # host = 'pre-adc-pc.alibaba-inc.com'
        host = 'test-adc-pc.alibaba.net'
    elif(scriptEnv == 'pre'):
        host = 'pre-adc-pc.alibaba-inc.com'
    elif(scriptEnv == 'prod'):
        host = 'adc-pc.alibaba-inc.com'
    else:
        host = 'test-adc-pc.alibaba.net'

    return host

def adc_server_request(path=None, request_type="get", params=None):
    env = AppEnv.get_instance()

    launchType = env.launchType
    if (launchType == 'localtest'):
        return

    host= get_adc_server_host(env)

    url = "http://{}/{}".format(host, path)


    # timestamp = time.time()*1000000
    # info = title + '+' + desc
    # monitor_print(info, timestamp)

    # payload = {"taskId": env.taskId, "taskStatus": taskStatus, "title": title, "description":desc, 'timestamp': int(time.time()*1000000)}
    monitor_print(f"---adc_server_request:{url},{request_type},{params}")

    payload = {}
    if request_type == "get":
        response = None
        try:
            response = requests.get(url, params=payload)
            # monitor_print(f"monitor_get_game_name_response: {response}")
            # monitor_print(f"monitor_get_game_name_response_json: {response.json()}")
            result = response.json()
            monitor_print(f"---adc_server_request_get_response: {result}")
            if result is not None:
                return result
        except Exception as e:
            monitor_print(f"---adc_server_request_get_response_error: {str(e)}")
            pass
    else:
        payload = params
        response = None
        try:
            response = requests.post(url, json=payload)
            # monitor_print(f"monitor_get_game_name_response: {response}")
            # monitor_print(f"monitor_get_game_name_response_json: {response.json()}")
            result = response.json()
            monitor_print(f"---adc_server_request_post_response: {result}")
            if result is not None:
                return result
        except Exception as e:
            monitor_print(f"---adc_server_request_post_response_error: {str(e)}")
            pass

    # print('updateTaskStatus:'+ str(response) + url)
    return None


def request_workflow_task_status(title, desc, status):
    env = AppEnv.get_instance()
    monitor_print(f'request_workflow_task_status:{title} -- {desc}; {status}')

    launchType = env.launchType
    if (launchType == 'localtest'):
        return

    taskStatus = status

    # if status:
    #     taskStatus = status

    # 这里在大于10000的情况下会上报任务中心错误，并且终止脚本执行
    # if (taskStatus > 10000):
    #     monitor_report_task_info(env, taskStatus)

    host = get_env_host(env)

    url = "http://{}/task/updateTaskStatus".format(host)

    timestamp = time.time() * 1000000
    info = title + '+' + desc

    payload = {"taskId": env.taskId, "taskStatus": taskStatus, "title": title, "description": desc,
               'timestamp': int(timestamp), 'game_dir': env.gameDir, 'game_name': env.game_name}
    monitor_print(f"request_workflow_task_status_url: {url}, payload: {payload}")
    response = None
    try:
        response = requests.get(url, params=payload)
        monitor_print(f"request_workflow_task_status_url_response: {response}")
        return response.text
    except Exception as e:
        monitor_print(f"request_workflow_task_status_url_response_error: {str(e)}")

    # print('updateTaskStatus:'+ str(response) + url)
    return None


def modaoshi_action_swipe(wda_port, data):
    url = f"http://127.0.0.1:{wda_port}/mds/multiPathGesture"  # 替换为你实际的端点

    headers = {
        "Content-Type": "application/json"
    }

    monitor_print(f"---modaoshi_action_swipe_Request_URL:{url},   {data}")

    response = requests.post(url, json=data, headers=headers)

    monitor_print(f"---modaoshi_action_swipe_Status_Code:{response.status_code},    {response.text}")