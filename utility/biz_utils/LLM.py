import json
import re
import time
from typing import Union, Dict, List

from utility.app.service.adc_ocr import config_ds_service_request_path, config_ds_service_token, easRequest
from utility.base.adc_environment import AppEnv
from utility.base.adc_monitor import monitor_print, PRINT_LEVEL, monitor_task_status_v2


def config_ds_service_request_data_hd_copy(reco_type, agentId, input_content, model=None):
    resData = {}
    resId = str(int(time.time() * 1000000))
    resData['requestId'] = resId
    if agentId != "":
        resData['agentId'] = agentId
    resData['recoType'] = reco_type
    resData['input'] = input_content
    if model is not None:
        resData['model'] = model

    return resData

def parse_model_output_to_json_copy(text: str) -> Union[Dict, List]:
    """
    将大模型返回的文本解析为 JSON 格式
    支持处理注释和常见格式问题
    """
    # 1. 移除注释（处理 // 和 /* */ 样式注释）
    text = re.sub(r'//.*?\n', '\n', text)  # 单行注释
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)  # 多行注释

    # 2. 移除 Markdown 代码块标记（如果有的话）
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```', '', text)

    # 3. 修复常见的 JSON 格式问题
    text = text.replace("'", '"')  # 替换单引号为双引号
    text = re.sub(r'(\w+):', r'"\1":', text)  # 为未加引号的键添加引号

    # 4. 使用第三方库处理更复杂的格式问题（可选）
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # 如果标准解析失败，尝试使用容错库（需要安装 demjson）
        try:
            import demjson
            return demjson.decode(text)
        except Exception as ex:
            raise ValueError(
                f"JSON 解析失败: {str(e)} | 原始文本: {text[:200]}...") from ex


def remote_ds_r1_reasoning_copy(input_content, model='', agentId=''):
    start_time = time.perf_counter()

    env = AppEnv.get_instance()
    game_ocr_path = config_ds_service_request_path()
    token = config_ds_service_token()
    reco_type = '大模型应用'
    game_ocr_resdata = config_ds_service_request_data_hd_copy(reco_type, agentId, input_content, model=model)

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
    else:
        monitor_print(f'---remote_ds_r1_reasoning_fail: {reco_type}, {game_ocr_resdata}, result:{data}',
                      level=PRINT_LEVEL.ERROR)
        return None


def get_name_large_model_copy(image_url, prompt="") -> str:
    """
    获取武器名称，并以json的形式返回
    :return:
    """
    system_prompt = """
    你是一个ocr助手，可以帮助用户精准识别图片中的文字，并按照用户意愿，将识别出的文字以指定的格式返回，
    """
    user_prompt = """
    请将图片中的藏品名称提取出来， 并以json的格式将区服名称整理给我，
    注意：
        1.返回json格式时，不要带有```json```的markdown的内容；
        2.返回格式内容严格按照以下json格式,只用返回区服名称的内容，其他任何多余字符都不用返回
            {
                "name": "藏品名称"
            }
        3. 严格遵守以上要求

    """
    if prompt:
        user_prompt = prompt

    message = [
        {"role": "system",
         "content": [
             {"text": system_prompt}
         ]
         },
        {
            "role": "user",
            "content": [
                {"image": image_url},
                {"text": user_prompt}
            ]
        }
    ]
    area_server_res = remote_ds_r1_reasoning_copy(input_content=message,
                                                  model="qwen-vl-max")
    area_server_dict = parse_model_output_to_json_copy(area_server_res)
    monitor_print(f"llm-输出结果：{area_server_dict}")
    name = area_server_dict.get("name", "")
    monitor_task_status_v2("获取名称", f"通过大模型获取藏品名称：{name}")
    return name
