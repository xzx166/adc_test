# -*- encoding=utf8 -*-
__author__ = "yangxiao"

from airtest.core.api import *
from airtest.core.error import *
from enum import Enum

import traceback
import time
import os
import subprocess

using("../utility/api.air")
from api import *

using("../utility/monitor.air")
from monitor import *

using("../utility/image.air")
from image import *

using("../utility/adc_tools.air")
from adc_tools import *

auto_setup(__file__)

# local_app_env = AppEnv.get_instance()
# # using(f"./{local_app_env.gameDir}/index.air")
# # from index import app_will_process_exception_snapshot

# script_path = f"./{local_app_env.gameDir}/{local_app_env.gameDir}_index.air"
# if local_app_env.taskType == TaskType.FABU.value:
#     script_path = f"./{local_app_env.gameDir}/{local_app_env.gameDir}_fabu.air"
#     # using(script_path)
#     # from {gameDir}_fabu  import app_will_process_exception_snapshot
#     # game_will_launch, game_did_launch, game_will_close,game_will_clean,app_will_process_exception_snapshot,app_will_process_properties
# else:
#     pass
#     # using(script_path)
#     # from index import app_will_process_exception_snapshot
biz_module = None
local_app_env = AppEnv.get_instance()
if local_app_env.taskType == TaskType.FABU.value:
    air_name = f"{local_app_env.gameDir}_fabu.air"
    biz_module = lx_import(air_name)
    # globals().update(vars(module))
elif local_app_env.taskType == TaskType.YANHAO.value:
    air_name = f"{local_app_env.gameDir}_index.air"
    biz_module = lx_import(air_name)
    # globals().update(vars(module))

class AppActionType(Enum):
    STOP_PHASE = 1  # 退出phase
    STOP_RUNLOOP = 2  # 退出当前runloop
    STOP_APP = 3 # 退出app
    STOP_OTHER = 4 # 其他各种情况引起的退出

class AppRunResult:
    def __init__(self, e = None, ext_info = None):
        self.updateInfo(AppActionType.STOP_APP, e, ext_info)

    def updateInfo(self,action, e, ext_info = None):
        self.actionType = action
        self.exception = e
        self.ext_info =ext_info

    def getActionType(self):
        return self.actionType

    def exceptionInfo(self):
        return self.exception

    def get_ext_info(self):
        return self.ext_info


class Application:
    def __init__(self):
            self.phaseList = []

    def setPhaseList(self,phaseList):
        self.phaseList = phaseList

    def run(self, env):
        global biz_module
        result = AppRunResult()

        for phase_index,phase in enumerate(self.phaseList):
            if env.launchType == 'localtest' and env.localtest_need_clean == False:
                if phase.name == '登录':
                    monitor_print(f"在本地环境，并且不需要清理登录，略过登录phase和区服")
                    continue
            try:
                lx_safe_snapshot(filename=f"adc_catch_phase_{phase_index}_before_{str(int(time.time() * 1000000))}.jpg")
                phase.run(env)
                lx_safe_snapshot(filename=f"adc_catch_phase_{phase_index}_after_{str(int(time.time() * 1000000))}.jpg")
                # memory_usage = get_memory_usage()
                # monitor_task_status_v2(f"{phase.name}内存使用情况", f"当前内存使用情况: {phase.name} ,{memory_usage}KB")
                # monitor_print(f"---phase内存使用情况: {phase.name} , {memory_usage}KB")
            except ExceptionStartNextPhase as e:  # 只中断当前phase, 后续流程不影响
                error_traceback = traceback.format_exc()
                monitor_task_status(env,str(e), f"{error_traceback}")
                if biz_module is not None:
                    file_name_path = snapshot_when_exception('adc_exception_next_phase')
                    biz_module.app_will_process_exception_snapshot(file_name_path)
                continue
            except ExceptionStopRunloop as e:     # 需要中断app的执行
                error_traceback = traceback.format_exc()
                monitor_task_status(env, str(e), f"{error_traceback}")
                result.updateInfo(AppActionType.STOP_RUNLOOP, e)
                break;
            except ExceptionStopApp as e:     # 需要中断app的执行
                error_traceback = traceback.format_exc()
                monitor_task_status(env, str(e), f"{error_traceback}")
                result.updateInfo(AppActionType.STOP_APP, e, ext_info = e.ext_info)
                break;
            except AdbError as e:
                error_traceback = traceback.format_exc()
                monitor_task_status(env, str(e), f"{error_traceback}")
                ext_info={'key':'120001'}
                result.updateInfo(AppActionType.STOP_APP, e, ext_info = ext_info)
                break;
            except Exception as e:
                error_traceback = traceback.format_exc()
                monitor_task_status(env,str(e), f"{error_traceback}")
                # 其他未知错误要通过runloop重试
                ext_info = {'key': '120007'}
                result.updateInfo(AppActionType.STOP_APP, e, ext_info = ext_info)
                break


        return result


















