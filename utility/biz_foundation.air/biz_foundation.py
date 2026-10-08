# -*- encoding=utf8 -*-
__author__ = "mengba"

from airtest.core.api import *
from airtest.core.error import *
from enum import Enum

import uuid
import os

# from openai import OpenAI
# import sseclient
# import requests

import json

from utility.app.service.adc_request import *

using("../utility/api.air")
from api import *

using("../utility/monitor.air")
from monitor import *

using("../utility/adc_request.air")
from adc_request import *

using("../utility/ocr.air")
from ocr import *


class AdcAiController(object):
    def __init__(self):
        self.bot_app_key = "PTEtuYZb"  # 机器人密钥，不是BotBizId (从运营接口人处获取)
        self.visitor_biz_id = "100040660338"  # 访客 ID（外部系统提供，需确认不同的访客使用不同的 ID）
        self.streaming_throttle = 1

    def get_session(self):
        # 生成一个 UUID
        new_uuid = uuid.uuid4()
        # 将 UUID 转换为字符串
        session_id = str(new_uuid)
        return session_id

    def get_request_id(self):  # 生成的request_id有48位
        # 生成 24 个字节的随机数据
        random_bytes = os.urandom(24)

        # 将随机数据转换为十六进制字符串
        request_id = random_bytes.hex()
        return request_id

    def ds_r1_reasoning_request(self, agent_id, request_content,model=None):
        result = remote_ds_r1_reasoning(agent_id, request_content, model=model)
        return result

    def request_remote_ai_helper(self, image_url, task_enter):
        return remote_ai_helper(image_url, task_enter)

    # tengxun的ds接口
    def sse_client_request(self, request_content):
        pass

        # chat_sid = self.get_session()
        # req_data = {
        #     "content": request_content,
        #     "bot_app_key": self.bot_app_key,
        #     "visitor_biz_id": self.visitor_biz_id,
        #     "session_id": chat_sid,
        #     "streaming_throttle": self.streaming_throttle
        # }
        #
        # ds_result = None
        # try:
        #
        #     # req_data["content"] =  """
        #     #             你是一个股票金融投资专家，我现在有50w元资金，想要做投资，平时比较忙，没什么投资经验，也没有太多时间投入，帮我做一份理财计划，要求易上手，风险低。 我想买美股或者中概股，给我规划几只股票以及资金分配
        #     #             """
        #     # req_data["content"] = """“773服云起龙骥,768服乒不厌诈,767服昨者为王”.这些词出自三国谋定天下游戏服务器名称，其中有的字因OCR识别有误，可能缺字，可能字是错的，帮我找出来哪些词可能有问题，只输出错误信息，以如下的json数组格式展示：\n                                [\n                                    {\n                                        "qufu_name": "xxxx",\n                                        "error_reason": "xxxx"\n"""
        #     monitor_print(f"---sse_client_request_req_data_start: {req_data}")
        #     resp = requests.post("https://wss.lke.cloud.tencent.com/v1/qbot/chat/sse", data=json.dumps(req_data),
        #                          stream=True, headers={"Accept": "text/event-stream"})
        #     client = sseclient.SSEClient(resp)
        #
        #     monitor_print(f"---sse_client_request_processing: ******")
        #     for ev in client.events():
        #         # print(f'event:{ev.event}, "data:"{ev.data}')
        #         data = json.loads(ev.data)
        #         if ev.event == "reply":
        #             if data["payload"]["is_from_self"]:  # 自己发出的包
        #                 # print(f'is_from_self, event:{ev.event}, "content:"{data["payload"]["content"]}')
        #                 pass
        #             elif data["payload"]["is_final"]:  # 服务端event传输完毕；服务端的回复是流式的，最后一条回复的content，包含完整内容
        #                 if data["payload"]["content"] is not None:
        #                     ds_result = data["payload"]["content"]
        #                 monitor_print(f'---sse_client_request_processing_result: event:{ev.event},payload:{data["payload"]}, "content:"{data["payload"]["content"]}')
        #         else:
        #             # monitor_print(f'event:{ev.event}, "data:"{ev.data}"')
        #             pass
        # except Exception as e:
        #     monitor_print(f'---sse_client_request_processing_error: {e}')
        #
        # return ds_result