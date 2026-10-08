import re,os
from typing import Union, List, Dict
import json

import sys
print(sys.path)
# 获取当前文件路径
os_env = os.path.dirname(os.path.abspath(__file__))
# 切换工作目录
os.chdir(os_env)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


from utility.biz_utils.biz_utils import *

user_prompt = """
请将图片中的藏品名称提取出来， 并以json的格式将藏品名称整理给我，
注意：
    1.返回json格式时，不要带有```json```的markdown的内容；
    2.返回格式内容严格按照以下json格式,只用返回区服名称的内容，其他任何多余字符都不用返回
        {
            "name": "藏品名称"
        }
    3. 严格遵守以上要求

"""




def get_name_by_llm(image_url,user_prompt) -> str:
    """
    获取武器名称，并以json的形式返回
    :return:
    """
    system_prompt = """
    你是一个游戏游戏名称识别助手，可以帮助用户精准识别道游戏的藏品名称，并按照用户意愿，将藏品名称整理成指定的数据格式，
    """
    user_prompt = user_prompt
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
    name = area_server_dict.get("name", "")
    monitor_task_status_v2("获取名称",f"通过大模型获取藏品名称：{name}")
    return name


oss_pathes, cdn_url_list = upload_jym_oss_with_pathes(['merge.jpg'])


