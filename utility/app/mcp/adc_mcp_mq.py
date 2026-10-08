from rocketmq.client import PushConsumer
from rocketmq.client import Producer, Message

import logging
import os, json, traceback
logger = logging.getLogger()
from urllib.parse import quote

from utility.base.adc_monitor import *
from utility.base.adc_api import *
from utility.app.service.adc_oss import *


MCP_ACTION_STATUS_SUCCESS = 1
MCP_ACTION_STATUS_FAIL = 2


# labels = quote("unit:%s,site:%s,app:%s,stage:%s" % (
#     os.getenv("SIGMA_APP_UNIT"),
#     os.getenv("SIGMA_APP_SITE"),
#     os.getenv("SIGMA_APP_NAME"),
#     os.getenv("SIGMA_APP_STAGE")
# ))

# todo - 预发和线上的labels信息配置
labels = quote("unit:None,site:None,app:None,stage:None")

mcp_producer = None

class McpMessageQueue:
    def __init__(self):
        monitor_print("----McpMessageQueue_init")
        env = AppEnv.get_instance()

        self.labels = quote("unit:None,site:None,app:None,stage:None")

        mcp_send_cmd_tag = env.get_common_property_with_key("mcpTag")

        # 初始化send_cmd_consumer
        monitor_print("----McpMessageQueue_start____CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ")
        self.send_cmd_consumer = PushConsumer('CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ')
        # 下面这行，在生产环境不要省略，测网，预发，正式都一样的地址
        self.send_cmd_consumer.set_namesrv_domain('http://jmenv.tbsite.net:8080/rocketmq/nsaddr?labels=' + self.labels)
        # todo - 后续用tag过滤
        # consumer.subscribe('TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ', mcp_send_cmd_callback, expression=mcp_send_cmd_tag)
        self.send_cmd_consumer.subscribe('TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ', self.mcp_send_cmd_callback, expression='*')
        self.send_cmd_consumer.start()
        monitor_print("----McpMessageQueue_finish____CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ")
        # logger.info("CID_LX_ADC_AUTO_MQ_ACK Consumer started...")


        # 初始化send_cmd_producer
        monitor_print("----McpMessageQueue_start____PID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_RESPONSE")
        self.send_cmd_producer = Producer('PID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_RESPONSE')
        # 下面这行，在生产环境不要省略，测网，预发，正式都一样的地址
        self.send_cmd_producer.set_namesrv_domain('http://jmenv.tbsite.net:8080/rocketmq/nsaddr?labels=' + self.labels)
        self.send_cmd_producer.start()
        monitor_print("----McpMessageQueue_finish____PID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_RESPONSE")

        # 初始化bind_session_producer
        monitor_print("----McpMessageQueue_start____PID_SCRIPT_TOPIC_BIND_SESSION_TASK_TO_SCRIPT_RESPONSE")
        self.bind_session_producer = Producer('PID_SCRIPT_TOPIC_BIND_SESSION_TASK_TO_SCRIPT_RESPONSE')
        # 下面这行，在生产环境不要省略，测网，预发，正式都一样的地址
        self.bind_session_producer.set_namesrv_domain('http://jmenv.tbsite.net:8080/rocketmq/nsaddr?labels=' + self.labels)
        self.bind_session_producer.start()
        monitor_print("----McpMessageQueue_finish____PID_SCRIPT_TOPIC_BIND_SESSION_TASK_TO_SCRIPT_RESPONSE")

        # 告知bind_session已完成
        session_id = env.get_common_property_with_key("sessionId")
        action_id = env.get_common_property_with_key("actionId")
        req_parasm = {"sessionId": session_id, "actionId": action_id}
        req_parasm["status"] = str(MCP_ACTION_STATUS_SUCCESS)
        req_parasm["message"] = "bind_session_suc"
        monitor_print("----mcp_bind_session_send____PID_SCRIPT_TOPIC_BIND_SESSION_TASK_TO_SCRIPT_RESPONSE")
        self.mcp_bind_session_send(req_parasm)

        # consumer保活逻辑
        monitor_print("-----------------consumer_while-----------------")
        try:
            i = 0
            while True:
                time.sleep(1)
                i = i + 1
                # monitor_print(f"consumer正在运行{i}...")
        except KeyboardInterrupt:
            monitor_print("正在关闭消费者...")
            monitor_print("-----------------consumer_excetion-----------------")
        finally:
            monitor_print("-----------------consumer_shutdown-----------------")
            self.send_cmd_consumer.shutdown()



    # def mcp_mq_init(self):
    #     print("CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ_mcp_mq_init_start")
    #     monitor_print("CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ_mcp_mq_init_start")
    #     env = AppEnv.get_instance()
    #     mcp_send_cmd_tag = env.get_common_property_with_key("mcpTag")
    #
    #     # 初始化consumer
    #     consumer = PushConsumer('CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ')
    #     # 下面这行，在生产环境不要省略，测网，预发，正式都一样的地址
    #     consumer.set_namesrv_domain('http://jmenv.tbsite.net:8080/rocketmq/nsaddr?labels=' + labels)
    #     # todo - 后续用tag过滤
    #     # consumer.subscribe('TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ', mcp_send_cmd_callback, expression=mcp_send_cmd_tag)
    #     consumer.subscribe('TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ', mcp_send_cmd_callback, expression='*')
    #     consumer.start()
    #     monitor_print("CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ_Consumer_started...")
    #     # logger.info("CID_LX_ADC_AUTO_MQ_ACK Consumer started...")
    #
    #     monitor_print("CID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_REQ_yield...")
    #
    #     # 初始化producer
    #     global mcp_producer
    #     mcp_producer = Producer('PID_SCRIPT_TOPIC_SEND_CMD_TASK_TO_SCRIPT_RESPONSE')
    #     # 下面这行，在生产环境不要省略，测网，预发，正式都一样的地址
    #     mcp_producer.set_namesrv_domain('http://jmenv.tbsite.net:8080/rocketmq/nsaddr?labels=' + labels)
    #     mcp_producer.start()
    #     monitor_print("PID_SEND_CMD_TASK_TO_SCRIPT_producer_started...")
    #
    #     # consumer保活逻辑
    #     monitor_print("-----------------consumer_while-----------------")
    #     try:
    #         i = 0
    #         while True:
    #             time.sleep(1)
    #             i = i + 1
    #             # monitor_print(f"consumer正在运行{i}...")
    #     except KeyboardInterrupt:
    #         monitor_print("正在关闭消费者...")
    #     finally:
    #         consumer.shutdown()

    def mcp_bind_session_send(self, raw_msg):
        monitor_print(f"-----------------mcp_bind_session_send_before-----------------")
        monitor_print(f"---mcp_bind_session_send_raw_msg: {raw_msg}")
        raw_msg_json = json.dumps(raw_msg)
        monitor_print(f"---mcp_bind_session_send_raw_msg_json: {raw_msg_json}")

        msg = Message('TOPIC_BIND_SESSION_TASK_TO_SCRIPT_RESPONSE')  # 注意每条消息都要实例化，不要多条消息共用一个 msg 对象
        msg.set_keys('keys')
        msg.set_tags('*')
        msg.set_body(raw_msg_json)
        try:
            monitor_print(f"---mcp_bind_session_send: {msg}")
            ret = self.bind_session_producer.send_sync(msg)
            monitor_print(f"---mcp_bind_session_send_ret: {ret.status}, {ret.msg_id}, {ret.offset}")
            if ret:
                monitor_print(f"---mcp_bind_session_send_suc_ret: {ret.status}, {ret.msg_id}, {ret.offset}")
            else:
                monitor_print(f"---mcp_bind_session_send_fail: {msg}")
        except Exception as e:
            monitor_print(f"---mcp_bind_session_send_exception: {msg}")

        monitor_print(f"-----------------mcp_bind_session_send_after-----------------")



    def mcp_send_cmd_send(self, raw_msg):
        monitor_print(f"-----------------mcp_send_cmd_send_before-----------------")
        monitor_print(f"---mcp_send_cmd_send_raw_msg: {raw_msg}")
        raw_msg_json = json.dumps(raw_msg)
        monitor_print(f"---mcp_send_cmd_send_raw_msg_json: {raw_msg_json}")

        msg = Message('TOPIC_SEND_CMD_TASK_TO_SCRIPT_RESPONSE')  # 注意每条消息都要实例化，不要多条消息共用一个 msg 对象
        msg.set_keys('keys')
        msg.set_tags('*')
        msg.set_body(raw_msg_json)
        try:
            monitor_print(f"---mcp_send_cmd_send: {msg}")
            ret = self.send_cmd_producer.send_sync(msg)
            monitor_print(f"---mcp_send_cmd_send_ret: {ret.status}, {ret.msg_id}, {ret.offset}")
            if ret:
                monitor_print(f"---mcp_send_cmd_send_suc_ret: {ret.status}, {ret.msg_id}, {ret.offset}")
            else:
                monitor_print(f"---mcp_send_cmd_send_fail: {msg}")
        except Exception as e:
            monitor_print(f"---mcp_send_cmd_send_exception: {msg}")

        monitor_print(f"-----------------mcp_send_cmd_send_after-----------------")

    def mcp_send_cmd_callback(self, msg):
        monitor_print(f"-----------------mcp_send_cmd_callback_before-----------------")
        monitor_print(f"---mcp_send_cmd_callback_raw-msg: {msg}")
        env = AppEnv.get_instance()
        session_id = None
        action_id = None
        try:

            monitor_print(f"---mcp_send_cmd_callback: {msg.id}, {msg.body}")
            body = json.loads(msg.body)

            monitor_print(f"---mcp_send_cmd_callback_body: {msg.id}, {msg.body}")

            action_id = body.get("actionId")
            session_id = body.get("sessionId")
            action_name = body.get("action")
            params = body.get("params")

            monitor_print(f"---mcp_send_cmd_callback_body_info: {action_id}, {session_id}, {action_name}, {params}")

            if action_name is None or params is None or session_id is None or action_id is None:
                monitor_print(f"---mcp_exe_action_params_none: {action_name}, {params}, {session_id}, {action_id}")
                return None

            monitor_print(f"---mcp_exe_action_desc: {session_id}, {action_id}, {action_name}, {params}")


            before_file_name = f"before_mcp_action_{str(int(time.time() * 1000000))}.jpg"
            adc_snapshot(filename=before_file_name)
            before_file_name_path = os.path.join(env.logPath, before_file_name)
            # 动态加载mcp底层执行模块
            env = AppEnv.get_instance()
            py_relative_path = f'./adc_mcp_atom.py'
            monitor_print(f"---import_adc_mcp_atom:{py_relative_path}")

            exe_module = lx_import(py_relative_path)

            req_parasm = {"sessionId": session_id, "actionId": action_id}

            if hasattr(exe_module, action_name):
                module_method = getattr(exe_module, action_name)
                if module_method:
                    try:
                        response = module_method(*params)
                        monitor_print(f"-----------------mcp_send_cmd_callback_exe-----------------")
                    except Exception as e:
                        req_parasm["mcpActionStatus"] = str(MCP_ACTION_STATUS_FAIL)
                        req_parasm["errorMessage"] = str(e)
                        self.mcp_send_cmd_send(req_parasm)
                        return
            else:
                req_parasm["mcpActionStatus"] = str(MCP_ACTION_STATUS_FAIL)
                req_parasm["errorMessage"] = f"未找到对应的方法{action_name}"
                self.mcp_send_cmd_send(req_parasm)
                return

            after_file_name = f"after_mcp_action_{str(int(time.time() * 1000000))}.jpg"
            adc_snapshot(filename=after_file_name)
            after_file_name_path = os.path.join(env.logPath, after_file_name)

            monitor_print(f"---mcp_exe_action_image_path: {before_file_name_path}, {after_file_name_path}")

            try:
                oss_info = upload_jym_oss_with_pathes([before_file_name_path, after_file_name_path])
                oss_pathes, cdn_urls = oss_info
                if cdn_urls is None or len(cdn_urls) == 0:
                    monitor_print(f"---mcp_exe_action_image_upload_error")
                    req_parasm["mcpActionStatus"] = str(MCP_ACTION_STATUS_FAIL)
                    req_parasm["errorMessage"] = "mcp上传图片失败"
                    self.mcp_send_cmd_send(req_parasm)
                    return
                else:
                    req_parasm["mcpActionStatus"] = str(MCP_ACTION_STATUS_SUCCESS)
                    req_parasm["data"] = {"images": cdn_urls}
            except Exception as e:
                monitor_print(f"---mcp_exe_action_image_upload_exception: {str(e)}")
                req_parasm["mcpActionStatus"] = str(MCP_ACTION_STATUS_FAIL)
                req_parasm["errorMessage"] = str(e)
                self.mcp_send_cmd_send(req_parasm)
                return

            self.mcp_send_cmd_send(req_parasm)

            return

        except Exception as e:
            req_parasm = {"sessionId": session_id, "actionId": action_id}
            monitor_print(f"---mcp_exe_action_Exception: {str(e)}")
            req_parasm["mcpActionStatus"] = str(MCP_ACTION_STATUS_FAIL)
            req_parasm["errorMessage"] = str(e)
            self.mcp_send_cmd_send(req_parasm)
            return