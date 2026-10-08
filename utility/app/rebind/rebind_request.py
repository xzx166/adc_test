
import requests
import json
import logging

from utility.base.adc_environment import AppEnv
from utility.app.service.adc_request import HttpClient, monitor_task_flow_status_info
from utility.base.adc_monitor import *

from utility.app.service.adc_oss import *

from airtest.core.api import *
from airtest.core.settings import *

from utility.base.adc_api import adc_snapshot


from functools import partial


def rebind_msg_send_env_host():
    env = AppEnv.get_instance()
    scriptEnv = env.scriptEnv
    host=""
    if (scriptEnv == 'local'):
        # host = 'pre-adc-pc.alibaba-inc.com'
        host = 'http://ieu-ai-proxy-task.taobao.net'
    elif (scriptEnv == 'pre'):
        host = 'http://pre-ieu-ai-customer-proxy.alibaba-inc.com'
    elif (scriptEnv == 'prod'):
        host = 'http://ieu-ai-customer-proxy.alibaba-inc.com'
    else:
        host = 'http://ieu-ai-proxy-task.taobao.net'

    return host


def rebind_msg_send(order_id, type='msg', content=''):
    env = AppEnv.get_instance()
    client = HttpClient(rebind_msg_send_env_host())

    append_content = f"{content}"

    # 构建请求的 JSON 数据
    req = {
        "order_id": order_id,
        "type": type,
        "content": append_content,
    }

    monitor_print(f"rebind_msg_send: {req}")

    # 发送请求
    response = client.post("/message/send", json=[req])
    # 处理响应
    if response:
        try:
            monitor_task_status_v2(f"rebind_msg_send_response_before",
                                   f'rebind_msg_send_response_before:{response}, {response.text}')
            # json_response = response.json()
            if '成功' in response.text:
                return True
            # monitor_task_status_v2(f"rebind_msg_send_response",
            #                        f'rebind_msg_send_response: {json_response}')
            # return json_response
        except json.JSONDecodeError:
            return None
    return None

def rebind_env_host():
    env = AppEnv.get_instance()
    scriptEnv = env.scriptEnv
    host=""
    if (scriptEnv == 'local'):
        # host = 'pre-adc-pc.alibaba-inc.com'
        host = 'http://test-ieu-ai-scipt-execute.alibaba.net'
    elif (scriptEnv == 'pre'):
        host = 'http://pre-ieu-ai-scipt-execute.aligames.com'
    elif (scriptEnv == 'prod'):
        host = 'http://ieu-ai-scipt-execute.aligames.com'
    else:
        host = 'http://test-ieu-ai-scipt-execute.alibaba.net'

    return host

def rebind_partial_func(status):
    # 该方法只在 stop_app，并且是换绑任务的情况下生效
    env = AppEnv.get_instance()
    rebind_json = json.loads(env.get_common_property_with_key('aiRebindExtParams'))

    crop_ = f"adc_catch_application_rebind_error_{str(int(time.time() * 1000000))}.jpg"
    adc_snapshot(filename=crop_)
    c_img_path = os.path.join(ST.LOG_DIR, crop_)
    upload_qufu_image_list = [c_img_path]
    oss_pathes, oss_urls = upload_jym_oss_with_pathes(upload_qufu_image_list)

    #  响应内部报错

    # rebind_execute_callback(task_id=rebind_json['taskId'], code=code, message=message,
    #                         ext_info={'screenshot_url': oss_urls[0]})
    # lx_break_app(ext_info={'key': '200'}, desc=code, hold_game=True)
    rebind_ext_info = {'screenshot_url': list(oss_urls)[0]}

    monitor_print(f"---rebind_ext_info: {rebind_ext_info}")
    bound_b = partial(rebind_execute_callback, task_id=rebind_json['taskId'], code='internal_error',
                      message=f'application_rebind执行异常_{status}',
                      ext_info=rebind_ext_info, success=False, sub_code=status)
    AppDynamicInfo.get_instance().partial_func = bound_b

# 这里要注意调用adc的接口要用json参数，调用换绑的接口要用params参数
def rebind_execute_callback(task_id, code, message, ext_info, success=True, sub_code=None):
    monitor_print(f"---rebind_execute_callback_start: {task_id} , {code} , {message} , {ext_info}")
    env = AppEnv.get_instance()
    client = HttpClient(get_env_host(env, need_prefix=True))

    rebind_json = json.loads(env.get_common_property_with_key('aiRebindExtParams'))
    script_name = rebind_json.get('scriptName')

    append_message = f"{message}_{env.taskId}"

    adc_task_id = env.taskId
    sub_code_str = ""
    if sub_code is not None:
        sub_code_str = str(sub_code)
    elif code == 'internal_error':
        sub_code_str = "10215"

    adc_platform = env.game_platfrom
    adc_game_id = env.game_id

    # adc_platform = 'shiyue'
    # adc_game_id = '777715674'

    # 构建请求的 JSON 数据
    extinfo_json = None
    try:
        extinfo_json = json.dumps(ext_info, ensure_ascii=False) if ext_info else ""
    except Exception as e:
        monitor_task_status_v2(f"---rebind_execute_callback_json_dumps", f"---rebind_execute_callback_json_dumps:{ext_info}, {str(e)}")
        monitor_print(f"---rebind_execute_callback_json_dumps_print:{ext_info}, {str(e)}")
        return None


    req = {
        "taskId": task_id,
        "code": code,
        "message": append_message,
        "extInfo": extinfo_json,
        "success": success,
        "adcTaskId": adc_task_id,
        "subCode": sub_code_str,
        "platform": adc_platform,
        "gameId": adc_game_id,
    }

    # monitor_task_status_v2(f"rebind_execute_callback_request", f'rebind_execute_callback_request:{req}')
    # monitor_print(f"---rebind_execute_callback_request: {req}")
    # # 发送请求
    # response = client.post("/task/reportAiRebindTask", json=req)
    #
    # # 处理响应
    # if response:
    #     try:
    #         monitor_task_status_v2(f"rebind_execute_callback_response_before",
    #                                f'rebind_execute_callback_response_before:{response}, {response.text}')
    #         json_response = response.json()
    #         monitor_task_status_v2(f"rebind_execute_callback_response",
    #                                f'rebind_execute_callback_response: {json_response}')
    #         if json_response.get("success") == True:
    #            return json_response.get("data")
    #         else:
    #             return None
    #     except json.JSONDecodeError:
    #         return None


    try:
        monitor_task_status_v2(f"---rebind_execute_callback_request: {script_name}", f'---rebind_execute_callback_request:{req}')
        monitor_print(f"---rebind_execute_callback_request:{script_name}, {req}")
        # 发送请求
        response = client.post("/task/reportAiRebindTask", json=req)

        monitor_task_status_v2(f"rebind_execute_callback_response_before",
                               f'rebind_execute_callback_response_before {script_name} :{response}, {response.text}')
        json_response = response.json()
        monitor_task_status_v2(f"rebind_execute_callback_response",
                               f'rebind_execute_callback_response {script_name} : {json_response}')

        data_response = json_response.get("data")
        state_code = data_response.get("stateCode")
        if state_code != 'INNER_ERROR' and json_response.get("success") == True:
            return json_response.get("data")
        else:
            return None

    except Exception as e:
        monitor_print(f"rebind_execute_callback------response_error: {str(e)}")

    return None

def verify_order_identity(order_id, unique_id):
    client = HttpClient(rebind_env_host())

    # 构建请求的 JSON 数据
    req = {
        "orderId": order_id,
        "gameAccount": unique_id
    }

    monitor_print(f"verify_order_identity: {req}")

    # 发送请求
    response = client.post("/proxy/identity", headers={
        'Content-Type': 'application/json'
    }, params=req)

    # 处理响应
    if response:
        try:
            json_response = response.json()
            print(json_response)
            if json_response.get("status") == 200:
                logging.info(f"Verify order identity succeeded: {json_response}")
                monitor_print(f"Verify_order_identity_succeeded: {json_response}")
                data = json_response.get("data")
                if not data:
                    return False, 'external_invoke_error', '调用异常'
                data_json = json.loads(data)
                verify_result = data_json.get("verifyResult")
                if verify_result is None:
                    return False, 'external_invoke_error', '调用异常'
                if verify_result is False:
                    return False, 'check_unique_id_error', '唯一id校验失败，直接取消交易'
                return True, 'success', '唯一id校验成功'

            else:
                logging.warning(f"Verify order identity failed: {json_response}")
                monitor_print(f"Verify_order_identity_failed: {json_response}")
                return False, 'external_invoke_error', '调用异常'
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON response.")
            monitor_print("Failed to decode JSON response.")
    else:
        logging.error("Failed to call verifyOrderIdentity")
        monitor_print("Failed to call verifyOrderIdentity")
    return False, 'external_invoke_error', '调用异常'


def rebind_set_stage_info(stage_type, stage_data):
    monitor_print(f"rebind_set_stage_info: {stage_type} , {stage_data}")
    # return monitor_task_flow_status_info(stage_type, stage_data)

    env = AppEnv.get_instance()
    client_host = get_env_host(env, need_prefix=True)
    client = HttpClient(client_host)
    task_id = env.taskId
    game_id = env.game_id
    game_platform = env.game_platfrom
    # 构建请求的 JSON 数据
    new_message = {"game_dir": env.gameDir, "game_id": game_id, "game_platform": game_platform}
    if stage_data:
        new_message.update(stage_data)

    the_time = int(time.time() * 1000)
    payload = {"task_id": task_id, "log_type": stage_type, "message": json.dumps(new_message, ensure_ascii=False),
               "timestamp": the_time}

    monitor_print(f"rebind_set_stage_info_payload: {client_host} payload: {payload}")

    # payload = {"task_id": real_task_id, "log_type": log_type, "message": json.dumps(new_message, ensure_ascii=False),
    #            "timestamp": the_time}

    monitor_print(f"rebind_set_stage_info_info: {payload}")

    # 发送请求
    response = client.post("/task/uploadAiRebindTaskStatus", json=payload)

    # 处理响应
    if response:
        try:
            monitor_task_status_v2(f"rebind_set_stage_info_response_before",
                                   f'rebind_set_stage_info_response_before:{response}, {response.text}')

            json_response = response.json()

            monitor_task_status_v2(f"rebind_set_stage_info_response", f'rebind_set_stage_info_response: {json_response}')
            if json_response.get("success") == True:
                return json_response.get("data")
            else:
                return None
        except json.JSONDecodeError:
            return None
    return None


def rebind_get_stage_info(stage_type):
    env = AppEnv.get_instance()
    client = HttpClient(get_env_host(env, need_prefix=True))
    task_id = env.taskId
    # 构建请求的 JSON 数据
    req = {
        "task_id": task_id,
        "log_type": stage_type,
    }

    # payload = {"task_id": real_task_id, "log_type": log_type, "message": json.dumps(new_message, ensure_ascii=False),
    #            "timestamp": the_time}

    monitor_print(f"rebind_get_stage_info: {req}")

    # 发送请求
    response = client.post("/task/queryAiRebindTaskStatus", json=req)

    # 处理响应
    if response:
        try:
            monitor_task_status_v2(f"rebind_get_stage_info_response_before",
                                   f'rebind_get_stage_info_response_before:{response}, {response.text}')

            json_response = response.json()

            monitor_task_status_v2(f"rebind_get_stage_info_response", f'rebind_get_stage_info_response: {json_response}')
            if json_response.get("success") == True:
                return json_response.get("data")
            else:
                return None
        except json.JSONDecodeError:
            return None
    return None