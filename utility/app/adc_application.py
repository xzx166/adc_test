# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

import argparse
import os

import threading
# 日志级别
import logging

import concurrent.futures

from civita import Client, SessionEvent
from civita.exceptions import *

from airtest.core.api import *
from airtest.core.error import *

from utility.app.service.adc_prd_code import phase_composite_image
# from utility.app.mcp.adc_mcp_mq import *

from utility.utility_header import *
from utility.app.rebind.rebind_request import *

# 默认就是DEBUG
logger = logging.getLogger("airtest")
logger.setLevel(logging.INFO)

# using("./utility/monitor.air")
# from monitor import *
#
# using("./utility/api.air")
# from api import *


# using("../utility/files.air")
# from files import *
#
# using("../utility/security.air")
# from security import *
#
# using("../utility/upload.air")
# from upload import *
#
# using("../utility/adc_request.air")
# from adc_request import *
#
# using("../utility/adc_tools.air")
# from adc_tools import *
#
# using("../utility/upload.air")
# from upload import upload_oss, upload_jym_oss
#
# using("../utility/monitor.air")
# from monitor import *


# auto_setup(__file__)

# 这里优先统计脚本开始时间点
AppPerformanceInfo.get_instance().setTimeDurationMap('captcha_time', duration_start=True)

# ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
ST.CVSTRATEGY = ['mstpl', 'tpl']
ST.SNAPSHOT_QUALITY = 99

# 启动不同的阶段（内部使用）
# 目前有 start ,upload
# 本地调试命令：
# airtest run ../main.air --device "Android:///localhost:9898" --log "/Users/xiaohanzhu/androidLogResult"

# CLIENT_TOKEN = '8r0864y6y8g'

### **********************入参解析********************** ###


# 需要游戏的index实现的方法包括：
# game_will_launch  告知游戏实现launch能力
# game_did_launch   告知游戏launch完成后要实现的能力,返回phase数据
# game_will_close
# game_will_clean
# app_will_process_exception_snapshot  内部不能执行任何操作game的代码
# app_will_process_properties 用于业务处理oss_urls
# app_did_get_properties  多子属性预拉取


ext_info = None
error_desc = None


# using("../utility/api.air")
# from api import *
#
# using("../utility/monitor.air")
# from monitor import *
#
# using("../utility/image.air")
# from image import *
#
# using("../utility/adc_tools.air")
# from adc_tools import *



# biz_module = None
# local_app_env = AppEnv.get_instance()
# if local_app_env.taskType == TaskType.FABU.value:
#     air_name = f"{local_app_env.gameDir}_fabu.air"
#     biz_module = lx_import(air_name)
#     # globals().update(vars(module))
# elif local_app_env.taskType == TaskType.YANHAO.value:
#     air_name = f"{local_app_env.gameDir}_index.air"
#     biz_module = lx_import(air_name)
#     # globals().update(vars(module))



def print_env_args():
    env = AppEnv.get_instance()
    monitor_print(f"脚本环境数据>>>>>>>>>>>>", level=PRINT_LEVEL.INFO)
    monitor_print(f"launchType:{env.launchType}", level=PRINT_LEVEL.INFO)
    monitor_print(f"phone:{env.phone}", level=PRINT_LEVEL.INFO)
    monitor_print(f"smsCode:{env.smsCode}", level=PRINT_LEVEL.INFO)
    monitor_print(f"username:{env.username}", level=PRINT_LEVEL.INFO)
    monitor_print(f"taskId:{env.taskId}", level=PRINT_LEVEL.INFO)
    monitor_print(f"sleepTime:{env.sleepTime}", level=PRINT_LEVEL.INFO)
    monitor_print(f"taskStatus:{env.taskStatus}", level=PRINT_LEVEL.INFO)
    monitor_print(f"SCRIPT_ENV:{env.scriptEnv}", level=PRINT_LEVEL.INFO)
    monitor_print(f"logPath:{env.logPath}", level=PRINT_LEVEL.INFO)
    monitor_print(f"game_name:{env.game_name}", level=PRINT_LEVEL.INFO)
    monitor_print(f"scriptHome:{env.scriptHome}", level=PRINT_LEVEL.INFO)
    monitor_print(f"taskType:{env.taskType}", level=PRINT_LEVEL.INFO)
    monitor_print(f"rootHome:{env.rootHome}", level=PRINT_LEVEL.INFO)
    monitor_print(f"mode:{env.mode}", level=PRINT_LEVEL.INFO)
    monitor_print(f"oss_mode:{env.oss_mode}", level=PRINT_LEVEL.INFO)
    monitor_print(f"oss_app_id:{env.oss_app_id}", level=PRINT_LEVEL.INFO)
    monitor_print(f"oss_app_secret:{env.oss_app_secret}", level=PRINT_LEVEL.INFO)
    monitor_print(f"device:{env.device}", level=PRINT_LEVEL.INFO)
    monitor_print(f"taskSource:{env.taskSource}", level=PRINT_LEVEL.INFO)
    monitor_print(f"game_area:{env.game_area}", level=PRINT_LEVEL.INFO)
    monitor_print(f"task_contenttype:{env.task_contenttype}", level=PRINT_LEVEL.INFO)
    monitor_print(f"transfer_account_info:{env.transfer_account_info}", level=PRINT_LEVEL.INFO)
    monitor_print(f"account_attr:{env.account_attr}", level=PRINT_LEVEL.INFO)
    monitor_print(f"image_list_json:{env.image_list_json}", level=PRINT_LEVEL.INFO)
    monitor_print(f"game_properties_version:{env.game_properties_version}", level=PRINT_LEVEL.INFO)
    monitor_print(f"common_properties_json:{env.common_properties_json}", level=PRINT_LEVEL.INFO)
    monitor_print(f"logpath:{env.logPath}", level=PRINT_LEVEL.INFO)
    monitor_print(f"iOSDeviceId:{env.iOSDeviceId}", level=PRINT_LEVEL.INFO)
    monitor_print(f"system_type:{env.system_type}", level=PRINT_LEVEL.INFO)
    monitor_print(f"app_id:{env.task_appId}", level=PRINT_LEVEL.INFO)
    monitor_task_status_v2(f"---env_args",
                           f'launchType:{env.launchType}, phone:{env.phone}, smsCode:{env.smsCode}, username:{env.username}, taskId:{env.taskId}, sleepTime:{env.sleepTime}, taskStatus:{env.taskStatus}, SCRIPT_ENV:{env.scriptEnv}, logPath:{env.logPath}, game_name:{env.game_name}, scriptHome:{env.scriptHome}, taskType:{env.taskType}, rootHome:{env.rootHome}, mode:{env.mode}, oss_mode:{env.oss_mode}, device:{env.device}, taskSource:{env.taskSource}, game_area:{env.game_area}, task_contenttype:{env.task_contenttype}, transfer_account_info:{env.transfer_account_info}, account_attr:{env.account_attr}, image_list_json:{env.image_list_json}, game_properties_version:{env.game_properties_version}, common_properties_json:{env.common_properties_json}, system_type: {env.system_type}, app_id:{env.task_appId}')
    monitor_print(f"<<<<<<<<<<<<脚本环境数据", level=PRINT_LEVEL.INFO)


def main_parse_args(system_type=None):
    launchType = 'localtest'
    username = ""
    phone = ""
    smsCode = ""
    password = ""
    taskId = ""
    SCRIPT_ENV = ""
    taskType = TaskType.YANHAO.value
    mode = ""
    gameDir = ''
    sleepTime = 0.5
    oss_mode = ''
    oss_app_id = ''
    oss_app_secret = ''
    task_source = 0
    game_area = None
    task_contenttype = 1
    transfer_account_info = ''
    account_attr = ''
    image_list_json = ''
    game_properties_version = 0
    common_properties_json = ''

    oss_eagle_app_id = ''
    oss_eagle_app_secret = ''

    oss_miniapp_app_id = ''
    oss_miniapp_app_secret = ''

    task_appid = TaskAppId.TASK_APPID_JIAOYIMAO.value

    # 下面的参数需要经过参数传入
    logPath = ''
    scriptHome = ''
    rootHome = ''
    iOSDeviceId = ''
    system_type = system_type
    mdsClientToken = None
    decrypt_key = None

    localNeedClean = True
    localNeedUpload = True
    localRemoveLog = True

    # global launchType
    # global phone
    # global smsCode
    # global username
    # global password
    # global taskId
    # global SCRIPT_ENV
    # global taskType
    # global mode
    # global gameDir
    # global logPath
    # global scriptHome
    # global rootHome
    #
    # global oss_mode
    # global oss_app_id
    # global oss_app_secret
    # global sleepTime
    #
    #
    #
    # global task_source
    # global game_area
    # global task_contenttype
    # global transfer_account_info
    # global account_attr
    # global image_list_json
    # global game_properties_version
    # global common_properties_json
    #
    # global oss_eagle_app_id
    # global oss_eagle_app_secret

    monitor_print('parsed args start')
    envLaunch = os.getenv('launchType')
    if envLaunch is not None:
        launchType = envLaunch
    # launchType就是启动的环境是本地还是云端，默认是本地

    if launchType != 'localtest':
        monitor_print("-----parsed args:")

        monitor_task_status_v2(f"before_IOS_DEVICE_SOURCE: {os.getenv('IOS_DEVICE_SOURCE')}", "")

        if system_type == 'android':

            parser = argparse.ArgumentParser(description="解析命令行参数示例",
                                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser.add_argument("run", action="store")
            parser.add_argument("script_home", action="store")
            parser.add_argument("--log", action="store")
            parser.add_argument("--device", action="store")

            args = vars(parser.parse_args())
            logPath = args['log']
        else:
            parser = argparse.ArgumentParser(description='解析命令行参数示例')

            # 添加参数
            parser.add_argument('--device', type=str, help='设备名称')  # 添加 --device 参数
            parser.add_argument('--log', type=str, help='日志路径')  # 添加 --log 参数

            # 解析参数
            args = parser.parse_args()

            # 使用参数
            monitor_print(f"设备名称: {args.device}")
            monitor_print(f"日志路径: {args.log}")

            logPath = args.log
            iOSDeviceId = args.device

            mdsClientToken = os.getenv('MDS_CLIENT_TOKEN')

            system_type = os.getenv('IOS_DEVICE_SOURCE')
            monitor_task_status_v2(f"IOS_DEVICE_SOURCE: {system_type}", "")

        username = os.getenv('name')
        phone = os.getenv('phone')
        decrypt_key = os.getenv('SECRTET_DECRYPT_PASSWORD')

        secret_smsCode = os.getenv('smsCode')
        monitor_print(f"secret_smsCode:{secret_smsCode}")
        smsCode = ''
        if secret_smsCode and len(secret_smsCode) > 0 and decrypt_key and len(decrypt_key) > 0:
            smsCode = decrypt(secret_smsCode, decrypt_key)

        secret_password = os.getenv('password')
        monitor_print(f"secret_password:{secret_password}")
        password = ''
        if secret_password and len(secret_password) > 0 and decrypt_key and len(decrypt_key) > 0:
            password = decrypt(secret_password, decrypt_key)

        taskId = os.getenv('taskId')
        SCRIPT_ENV = os.getenv('SCRIPT_ENV')
        taskType = os.getenv('taskType')
        # scriptHome = os.getenv('SCRIPT_HOME')
        mode = os.getenv('actionType')
        gameDir = os.getenv('zipFileName')
        # sleepTime = os.getenv('sleepTime')

        oss_mode = os.getenv('OSS_MODE')
        oss_app_id = os.getenv('OSS_APP_ID')
        oss_app_secret = os.getenv('OSS_APP_SECRET')

        oss_eagle_app_id = os.getenv('OSS_EAGLE_APP_ID')
        oss_eagle_app_secret = os.getenv('OSS_EAGLE_APP_SECRET')

        oss_miniapp_app_id = os.getenv('OSS_MINI_APP_APP_ID')
        oss_miniapp_app_secret = os.getenv('OSS_MINI_APP_APP_SECRET')

        task_source = os.getenv('taskSource')
        if task_source is None or not task_source.isdigit():
            task_source = '0'

        game_properties_version_str = os.getenv('gamePropertiesVersion')
        if game_properties_version_str is None or len(game_properties_version_str) == 0:
            game_properties_version = 0
        else:
            game_properties_version = int(game_properties_version_str)

        temp_game_area = os.getenv('gameArea')
        if temp_game_area == 'null':
            game_area = None
        else:
            game_area = temp_game_area

        task_contenttype = os.getenv('taskContentType')
        if task_contenttype is None or not task_contenttype.isdigit():
            task_contenttype = 1

        # transfer_account_info = os.getenv('transferAccountInfo')

        temp_transfer_account_info = os.getenv('transferAccountInfo')
        if temp_transfer_account_info == 'null':
            transfer_account_info = None
        else:
            transfer_account_info = temp_transfer_account_info

        temp_account_attr = os.getenv('accountAttr')
        if temp_account_attr == 'null':
            account_attr = None
        else:
            account_attr = temp_account_attr
        # account_attr = os.getenv('accountAttr')

        # image_list_json = os.getenv('imageListJson')


        temp_image_list_json = os.getenv('imageListJson')
        if temp_image_list_json == 'null':
            image_list_json = None
        else:
            image_list_json = temp_image_list_json

        common_properties_json = os.getenv('commonPropertiesJson')
    else:
        monitor_print("-----parsed localtest args:")

        home_dir = os.path.expanduser("~")
        # 读取放到adc目录下的localtest_config.json文件
        configPath = home_dir + '/.adc/localtest_config.json'
        if os.path.exists(configPath) and os.path.isfile(configPath):
            with open(f"{configPath}", 'r') as file:
                content = file.read()
                if content == None or len(content) == 0:
                    monitor_print(f"***本地测试配置文件不能为空")
                    exit()
        else:
            monitor_print(f"***没有找到本地测试配置文件: {configPath}")
            exit()

        # 解析 JSON 内容
        data = json.loads(content)

        monitor_print(f"localtest_file:{data}")

        if system_type == 'android' or system_type == 'kejinshou':
            parser = argparse.ArgumentParser(description="解析命令行参数示例",
                                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser.add_argument("run", action="store")
            parser.add_argument("script_home", action="store")
            parser.add_argument("--log", action="store")
            parser.add_argument("--device", action="store")

            args = vars(parser.parse_args())
            logPath = args['log']
        else:
            parser = argparse.ArgumentParser(description='解析命令行参数示例')

            # 添加参数
            parser.add_argument('--device', type=str, help='设备名称')  # 添加 --device 参数
            parser.add_argument('--log', type=str, help='日志路径')  # 添加 --log 参数

            # 解析参数
            args = parser.parse_args()

            # 使用参数
            monitor_print(f"设备名称: {args.device}")
            monitor_print(f"日志路径: {args.log}")

            logPath = args.log
            iOSDeviceId = args.device
            system_type = data['IOS_DEVICE_SOURCE']


        if system_type == SystemType.IOS:
            # logPath = data.get('RESULT_HOME')
            # iOSDeviceId = data.get('iOSDeviceId')
            mdsClientToken = data.get('MDS_CLIENT_TOKEN')

        username = data['username']
        phone = data['phone']
        smsCode = data['smsCode']
        password = data['password']
        taskId = data['taskId']
        SCRIPT_ENV = data['SCRIPT_ENV']
        taskType = data['taskType']
        mode = data['mode']
        gameDir = data['gameDir']
        sleepTime = data['sleepTime']
        oss_mode = data['oss_mode']
        oss_app_id = data['oss_app_id']
        oss_app_secret = data['oss_app_secret']

        oss_eagle_app_id = data.get('OSS_EAGLE_APP_ID')
        oss_eagle_app_secret = data.get('OSS_EAGLE_APP_SECRET')

        oss_miniapp_app_id = data.get('OSS_MINI_APP_APP_ID')
        oss_miniapp_app_secret = data.get('OSS_MINI_APP_APP_SECRET')

        decrypt_key = data.get('decrypt_key')

        task_source = data.get('taskSource')
        game_area = data.get('gameArea')
        task_contenttype_str = data.get('taskContentType')
        transfer_account_info = data.get('transferAccountInfo')
        account_attr = data.get('accountAttr')
        if task_contenttype_str is None:
            task_contenttype = 1
        else:
            task_contenttype = int(task_contenttype_str)

        if transfer_account_info is None:
            transfer_account_info = ''

        if account_attr is None:
            account_attr = ''

        if task_source is None:
            task_source = '0'

        image_list_json = data.get('imageListJson')

        game_properties_version = data.get('gamePropertiesVersion')
        if game_properties_version is None:
            game_properties_version = 0

        temp_need_clean = data.get('local_need_clean')
        if temp_need_clean is not None:
            if int(temp_need_clean) == 1:
                localNeedClean = True
            else:
                localNeedClean = False

        temp_need_upload = data.get('local_need_upload')
        if temp_need_upload is not None:
            if int(temp_need_upload) == 1:
                localNeedUpload = True
            else:
                localNeedUpload = False

        temp_remove_log = data.get('local_remove_log')
        if temp_remove_log is not None:
            if int(temp_remove_log) == 1:
                localRemoveLog = True
            else:
                localRemoveLog = False

        common_properties_json = data.get('commonPropertiesJson')

        monitor_print(f"localNeedClean:{localNeedClean}")
        monitor_print(f"localNeedUpload:{localNeedUpload}")
        monitor_print(f"localRemoveLog:{localRemoveLog}")

    # 获取当前文件的路径
    current_path = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.dirname(current_path)
    scriptHome = dir_path + '/' + gameDir

    rootHome = dir_path

    rootHome = os.environ.get("PYTHONPATH")
    scriptHome = rootHome + '/' + gameDir

    monitor_print("-----parsed args end")

    env = AppEnv.get_instance()
    print(f"---env: {env.launchType}")

    cur_device = None

    if system_type in ['android', "yunyou_ios", 'kejinshou']:
        cur_device = device()
    # localtest_config.json文件都配置到了AppEnv中
    env.setEnv(launchType, phone, smsCode,
               username, password,
               taskId, SCRIPT_ENV, mode, logPath, gameDir, scriptHome,
               rootHome, oss_mode, oss_app_id, oss_app_secret, sleepTime,
               taskType=int(taskType),
               taskSource=int(task_source),
               game_area=game_area,
               task_contenttype=int(task_contenttype),
               transfer_account_info=transfer_account_info,
               account_attr=account_attr,
               game_properties_version=int(game_properties_version),
               image_list_json=image_list_json,
               common_properties_json=common_properties_json,
               oss_eagle_app_id=oss_eagle_app_id,
               oss_eagle_app_secret=oss_eagle_app_secret,
               device=cur_device,
               iOSDeviceId=iOSDeviceId,
               system_type=system_type,
               mds_client_token=mdsClientToken,
               decrypt_key=decrypt_key,
               oss_miniapp_app_id=oss_miniapp_app_id,
               oss_miniapp_app_secret=oss_miniapp_app_secret)

    env.localtest_need_clean = localNeedClean
    env.localtest_need_upload = localNeedUpload
    env.localtest_remove_log = localRemoveLog
    ST.LOG_DIR = env.logPath

    # 这里必须在 setEnv 结束后再设置
    env.task_appId = env.get_account_attr_with_key('appId')

    print_env_args()


# ### **********************设置环境变量********************** ###
# # 设置环境变量
# env = AppEnv.get_instance()
# env.setEnv(launchType, phone, smsCode, username, password, taskId, SCRIPT_ENV, mode, logPath, gameDir, scriptHome,
#            rootHome, oss_mode, oss_app_id, oss_app_secret, sleepTime, taskType=int(taskType),
#            taskSource=int(task_source), game_area=game_area, task_contenttype=int(task_contenttype),
#            transfer_account_info=transfer_account_info, account_attr=account_attr,
#            game_properties_version=int(game_properties_version), image_list_json=image_list_json,
#            common_properties_json=common_properties_json, oss_eagle_app_id=oss_eagle_app_id,
#            oss_eagle_app_secret=oss_eagle_app_secret, device=device())


# 这里要注意采用STAGE_RUN_PHASE之后是可以上报异常信息的，但是后面的阶段无法上报异常信息
class AppStateType(Enum):
    STAGE_DEFAULT = 0  #
    STAGE_BEFORE_RUN = 1  #
    STAGE_RUN_PHASE = 2  #
    STAGE_REPORT_EXCEPT = 3
    STAGE_AFTER_RUN = 4 #


class AppActionType(Enum):
    STOP_DEFAULT = 0  # 开始phase
    STOP_PHASE = 1  # 退出phase
    STOP_RUNLOOP = 2  # 退出当前runloop
    STOP_APP = 3 # 退出app
    STOP_OTHER = 4 # 其他各种情况引起的退出

class AppRunResult:
    def __init__(self, e = None, ext_info = None, desc = None):
        self.updateInfo(AppActionType.STOP_DEFAULT, e, ext_info, desc)

    def updateInfo(self,action, e, ext_info = None, desc = None):
        self.actionType = action
        self.exception = e
        self.ext_info =ext_info
        self.desc = desc

    def getActionType(self):
        return self.actionType

    def exceptionInfo(self):
        return self.exception

    def get_ext_info(self):
        return self.ext_info

    def get_desc(self):
        return self.desc




class Application:
    def __init__(self):
        self.phaseList = []


    def setPhaseList(self,phaseList):
        self.phaseList = phaseList

    def run(self, env):
        result = AppRunResult()

        for phase_index,phase in enumerate(self.phaseList):
            if env.launchType == 'localtest' and env.localtest_need_clean == False:
                if phase.name == '登录':
                    # monitor_print(f"在本地环境，并且不需要清理登录，略过登录phase和区服")
                    continue
            try:
                # lx_safe_snapshot(filename=f"adc_catch_phase_{phase_index}_before_{str(int(time.time() * 1000000))}.jpg")
                phase.run(env)
                # lx_safe_snapshot(filename=f"adc_catch_phase_{phase_index}_after_{str(int(time.time() * 1000000))}.jpg")
                # memory_usage = get_memory_usage()
                # monitor_task_status_v2(f"{phase.name}内存使用情况", f"当前内存使用情况: {phase.name} ,{memory_usage}KB")
                # monitor_print(f"---phase内存使用情况: {phase.name} , {memory_usage}KB")
            except ExceptionStartNextPhase as e:  # 只中断当前phase, 后续流程不影响
                error_traceback = traceback.format_exc()
                monitor_task_status(env,f"---phase_run_nextphase:{str(e)}", f"{error_traceback}")
                if self.biz_module is not None:
                    file_name_path = self.app_snapshot_when_exception('adc_exception_next_phase')
                    self.biz_module.app_will_process_exception_snapshot(file_name_path)
                continue
            except Exception as e:
                error_traceback = traceback.format_exc()
                monitor_task_status_v2(f'---phase_run_exception', f'{error_traceback}')
                result = self.handle_all_exceptions(e, error_traceback, AppStateType.STAGE_RUN_PHASE)
                break


        return result

    def handle_all_exceptions(self, e, error_traceback, stage_type=AppStateType.STAGE_DEFAULT):
        # 一些特殊的exception的优先级更高，可以覆盖业务给的异常情况，比如adberror
        result = AppRunResult()
        env = AppEnv.get_instance()

        stage_name = str(stage_type)

        monitor_task_status_v2(f"---handle_all_exceptions:{str(e)}", f"{error_traceback}")

        if isinstance(e, ExceptionStopRunloop):
            monitor_task_status_v2(f"---app_{stage_name}_except_stoprunloop:{str(e)}", f"{error_traceback}")
            result.updateInfo(AppActionType.STOP_RUNLOOP, e, ext_info=e.ext_info)
        elif isinstance(e, ExceptionStopApp):
            monitor_task_status_v2(f"---app_{stage_name}_except_stopapp:{str(e)}", f"{error_traceback}")
            result.updateInfo(AppActionType.STOP_APP, e, ext_info=e.ext_info)
        elif isinstance(e, AdbError):
            monitor_task_status_v2(f"---app_{stage_name}_except_adberror:{str(e)}", f"{error_traceback}")
            ext_info = {'key': '120001'}
            result.updateInfo(AppActionType.STOP_APP, e, ext_info=ext_info)
            if self.is_ai_rebind_task():
                rebind_partial_func('120001')
        elif isinstance(e, TimeoutError):
            if env.system_type == SystemType.IOS:
                monitor_task_status_v2(f"---app_{stage_name}_except_timeout:{str(e)}", f"{error_traceback}")
                # 其他未知错误要通过runloop重试
                ext_info = {'key': '120024'}
                result.updateInfo(AppActionType.STOP_RUNLOOP, e, ext_info=ext_info)
            else:
                monitor_task_status(env, f"---app_{stage_name}_except_normal:{str(e)}", f"{error_traceback}")
                # 其他未知错误要通过runloop重试
                ext_info = {'key': '120007'}
                result.updateInfo(AppActionType.STOP_APP, e, ext_info=ext_info)
                if self.is_ai_rebind_task():
                    rebind_partial_func('120007')
        elif isinstance(e, ServerSessionException) or isinstance(e, ControlSessionException) or isinstance(e, ServerSessionNotInUseException) or isinstance(e, WebDriverException) or isinstance(e, NoAvailableResourceException):
            monitor_task_status_v2(f"---app_{stage_name}_except_session:{str(e)}", f"{error_traceback}")
            # 其他未知错误要通过runloop重试
            ext_info = {'key': '120024'}
            result.updateInfo(AppActionType.STOP_RUNLOOP, e, ext_info=ext_info)
        else:
            monitor_task_status(env, f"---app_{stage_name}_except_normal:{str(e)}", f"{error_traceback}")
            # 其他未知错误要通过runloop重试
            ext_info = {'key': '120007'}
            result.updateInfo(AppActionType.STOP_APP, e, ext_info=ext_info)
            if self.is_ai_rebind_task():
                rebind_partial_func('120007')

        return result


    def init_mds(self):
        env = AppEnv.get_instance()
        launch_type = env.launchType
        client = Client(env.mds_client_token)
        monitor_task_status_v2("---iOS设备_init_client", "iOS设备_init_client")

        AppDynamicInfo.get_instance().iosClient = client
        AppDynamicInfo.get_instance().iosHasKicked = False

        # 启动civita-client-agent, 只有需要使用ADB或者WDA时，才需要调用此方法
        # civita-client-agent是全局共享的，不需要反复启动
        monitor_task_status_v2("---iOS设备_setup_device_agent_start", "iOS设备_setup_device_agent_start")


        def retry_setup_device_agent(cur_client):
            agent_response = False
            for i in range(4):
                try:
                    cur_client.setup_device_agent()
                    monitor_task_status_v2(f"---iOS设备_setup_device_agent", f"")
                    monitor_print(f"---iOS设备_setup_device_agent")

                    monitor_task_status_v2("---iOS设备_setup_device_agent成功", f"")
                    agent_response = True
                    break
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    monitor_task_status_v2("---iOS设备_setup_device_agent_Except", f"{str(e)}_{error_traceback}")
                    sleep(15)

            return agent_response

        # real_agent_response = retry_setup_device_agent(client)
        real_agent_response = True

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(retry_setup_device_agent, client)
            try:
                real_agent_response = future.result(timeout=80)  # 设置超时时间
            except concurrent.futures.TimeoutError:
                future.cancel()
                monitor_print(f"------iOS设备_setup_device_agent_timeout")
                monitor_task_status_v2("------iOS设备_setup_device_agent_timeout", "---iOS设备_setup_device_agent超时")
                lx_break_app(ext_info={'key': '120025'}, desc='---iOS设备_setup_device_agent超时', hold_game=False)

        if real_agent_response is False:
            monitor_task_status_v2("---iOS设备_setup_device_agent失败", f"")
            lx_break_app(ext_info={'key': '120023'}, desc='ios设备_setup_device_agent失败', hold_game=False)


        def cb(evt: SessionEvent, *args):
            monitor_task_status_v2("---iOS设备_cb_start", f"")
            if SessionEvent.EVENT_DEV_ADBDISCONNECTED == evt:
                monitor_task_status_v2("---iOS设备_adb_disconnected", f"")
                monitor_print(f"---iOS设备_adb_disconnected")
            elif SessionEvent.EVENT_DEV_WDAPORTCLOSED == evt:
                monitor_task_status_v2("---iOS设备_wda_disconnected", f"")
                monitor_print(f"---iOS设备_wda_disconnected")
            elif SessionEvent.EVENT_DEV_KICKED == evt:

                AppDynamicInfo.get_instance().iosHasKicked = True

        monitor_task_status_v2("---iOS设备_setup_cb", "iOS设备_setup_cb")
        AppDynamicInfo.get_instance().iosCb = cb



    def connect_mds(self):
        env = AppEnv.get_instance()
        launch_type = env.launchType
        client = AppDynamicInfo.get_instance().iosClient

        AppDynamicInfo.get_instance().iosHasKicked = False

        # 强制释放设备
        if launch_type != 'localtest':
            # 本地调试的情况下，不用强制释放设备
            monitor_task_status_v2("---强制释放iOS设备_start", "强制释放iOS设备_start")
            release_response = None
            for i in range(3):
                try:
                    release_response = client.release_device(env.iOSDeviceId)
                    monitor_task_status_v2("---强制释放iOS设备", f"---")
                    if release_response is not None:
                        monitor_task_status_v2("---强制释放iOS设备成功", f"")
                        break
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    monitor_task_status_v2("---强制释放iOS设备_Except", f"{str(e)}_{error_traceback}")
                    sleep(2)

            # 释放完设备，等待3s
            sleep(3)

        # # 启动civita-client-agent, 只有需要使用ADB或者WDA时，才需要调用此方法
        # # civita-client-agent是全局共享的，不需要反复启动
        # monitor_task_status_v2("---iOS设备_setup_device_agent_start", "iOS设备_setup_device_agent_start")
        # agent_response = False
        # for i in range(3):
        #     try:
        #         client.setup_device_agent()
        #         monitor_task_status_v2(f"---iOS设备_setup_device_agent_{agent_response}", f"")
        #         monitor_print(f"---iOS设备_setup_device_agent")
        #
        #         monitor_task_status_v2("---iOS设备_setup_device_agent成功", f"")
        #         agent_response = True
        #         break
        #     except Exception as e:
        #         error_traceback = traceback.format_exc()
        #         monitor_task_status_v2("---iOS设备_setup_device_agent_Except", f"{str(e)}_{error_traceback}")
        #         sleep(2)
        #
        # if agent_response is False:
        #     monitor_task_status_v2("---iOS设备_setup_device_agent失败", f"")
        #     lx_break_app(ext_info={'key':'120023'}, desc='ios设备_setup_device_agent失败', hold_game=False)


        monitor_task_status_v2("---连接iOS设备_start", "连接iOS设备")
        # 请求获取一台设备，并建立会话连接
        session_connect = None
        session_connect = self.connect_mds_session(client)

        if session_connect is None:
            monitor_task_status_v2("---iOS设备session连接失败", f"")
            lx_break_app(ext_info={'key':'120020'}, desc='iOS设备session连接失败',hold_game= False)

        # def cb(evt: SessionEvent, *args):
        #     monitor_task_status_v2("---iOS设备_cb_start", f"")
        #     if SessionEvent.EVENT_DEV_ADBDISCONNECTED == evt:
        #         monitor_task_status_v2("---iOS设备_adb_disconnected", f"")
        #         monitor_print(f"---iOS设备_adb_disconnected")
        #     elif SessionEvent.EVENT_DEV_WDAPORTCLOSED == evt:
        #         monitor_task_status_v2("---iOS设备_wda_disconnected", f"")
        #         monitor_print(f"---iOS设备_wda_disconnected")
        #     elif SessionEvent.EVENT_DEV_KICKED == evt:
        #
        #         AppDynamicInfo.get_instance().iosHasKicked = True
                # 设备会话已经断开
                # monitor_task_status_v2("---iOS设备_has_kicked", f"")
                # monitor_print(f"---iOS设备_has_kicked")
                #
                # new_session_connect = None
                # new_session_connect = self.connect_mds_session(client)
                #
                # # def new_cb(evt: SessionEvent, *args):
                # #     monitor_task_status_v2("---iOS设备_new_cb_start", f"")
                # #     if SessionEvent.EVENT_DEV_ADBDISCONNECTED == evt:
                # #         monitor_task_status_v2("---iOS设备_new_cb_adb_disconnected", f"")
                # #         monitor_print(f"---iOS设备_new_cb_adb_disconnected")
                # #     elif SessionEvent.EVENT_DEV_WDAPORTCLOSED == evt:
                # #         monitor_task_status_v2("---iOS设备_new_cb_wda_disconnected", f"")
                # #         monitor_print(f"---iOS设备_new_cb_wda_disconnected")
                # #     elif SessionEvent.EVENT_DEV_KICKED == evt:
                # #         # 设备会话已经断开
                # #         monitor_task_status_v2("---iOS设备_new_cb_has_kicked", f"")
                # #         monitor_print(f"---iOS设备_new_cb_has_kicked")
                #
                # self.config_mds_session(new_session_connect, cb)

        self.config_mds_session(session_connect, AppDynamicInfo.get_instance().iosCb)

    def connect_mds_session(self, client):
        env = AppEnv.get_instance()
        # 请求获取一台设备，并建立会话连接
        session_connect = None
        def retry_connect(client):
            cur_session_connect = None
            for i in range(8):
                try:
                    monitor_task_status_v2(f"---连接iOS设备_连接_{i}", f"---")
                    cur_session_connect = client.request_device_session(selector={'deviceid': env.iOSDeviceId})
                    if cur_session_connect is not None:
                        monitor_task_status_v2("---连接iOS设备_连接成功", f"---{cur_session_connect.ready}")
                        if cur_session_connect.agent_session is not None:
                            monitor_task_status_v2("---连接iOS设备_连接成功_agent_session", f"")
                        if cur_session_connect.ready == True:
                            monitor_task_status_v2("---连接iOS设备_连接成功_ready", f"")
                        break
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    monitor_task_status_v2(f"---连接iOS设备_连接失败_{str(e)}", f"{error_traceback}")
                    sleep(15*i)

            return cur_session_connect

        # session_connect = retry_connect(client)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(retry_connect, client)
            try:
                session_connect = future.result(timeout=60*5)  # 设置超时时间
            except concurrent.futures.TimeoutError:
                future.cancel()
                monitor_print(f"---连接iOS设备_session_timeout")
                monitor_task_status_v2("---连接iOS设备_session_timeout", "连接iOS设备超时")
                lx_break_app(ext_info={'key': '120022'}, desc='iOS设备session连接超时', hold_game=False)

        if session_connect is None:
            monitor_task_status_v2("---iOS设备session连接失败", f"")
            lx_break_app(ext_info={'key': '120020'}, desc='iOS设备session连接失败', hold_game=False)

        return session_connect

    def config_mds_session(self, session_connect, cb):
        env = AppEnv.get_instance()
        # 设置会话事件回调
        session_connect.set_event_listener(cb)
        monitor_task_status_v2("---iOS设备_set_event_listener", f"")
        monitor_print(f"---iOS设备_set_event_listener")

        # 这个代码， 会导致进程无法结束，另外需要确定到底是什么功能
        # session_connect.setup_display_touch_channel()

        self.config_mds_wda(session_connect)

        env.iOS_session_connect = session_connect
        device_info = session_connect.device
        display_width = device_info["display_width"]
        screen_width = device_info["deviceModel"]["screen_width"]
        os.environ.update(posDivisor=str(screen_width // display_width))
        monitor_print(f"---iOS_session_id: {session_connect.sessionid}")

    def config_mds_wda(self, session_connect):
        env = AppEnv.get_instance()
        # 连接远程ADB，连接成功以后，才能通过ADB使用远程设备
        # 成功连接adb的返回形如 {'success': True, 'adbdPort': 65235, 'adbHostPort': '5037'}
        conn = session_connect.setup_wda_proxy()
        monitor_task_status_v2("---iOS设备_setup_wda_proxy", f"")
        monitor_print(f"---iOS设备_setup_wda_proxy: {conn}")

        if conn.get('success') is False:
            raise Exception("setup_wda_proxy failed")

        wda_port = conn.get('wdaPort')
        if wda_port is None:
            raise Exception("wda_port is None")

        env.iOS_wda_port = wda_port

    # 清理本地文件
    # def clean_cache_info(self):
    #     env = AppEnv.get_instance()
    #     launchType = env.launchType
    #     # 清理本地文件
    #     if launchType == 'localtest':
    #         ST.SAVE_IMAGE = False
    #         adc_dir = get_home_adc_directory()
    #         adc_monitor_file = adc_dir + '/' + gameDir + '.log'
    #         if os.path.exists(adc_monitor_file):
    #             os.remove(adc_monitor_file)
    #
    #         if localNeedClean == False:
    #             env.localtest_need_clean = False
    #     else:
    #         ST.SAVE_IMAGE = True

    # 获取游戏名称
    def get_cur_game_name(self):
        env = AppEnv.get_instance()
        # 获取游戏名称
        env.game_name = get_cur_game_name()
        os.environ.update(
            taskId=str(env.taskId),
            game_name=str(env.game_name),
            game_platfrom=str(env.game_platfrom),
            game_id=str(env.game_id)
        )

# # 清理本地文件
# if launchType == 'localtest':
#     ST.SAVE_IMAGE = False
#     adc_dir = get_home_adc_directory()
#     adc_monitor_file = adc_dir + '/' + gameDir + '.log'
#     if os.path.exists(adc_monitor_file):
#         os.remove(adc_monitor_file)
#
#     if localNeedClean == False:
#         env.localtest_need_clean = False
# else:
#     ST.SAVE_IMAGE = True
#
# # 获取游戏名称
# env.game_name = monitor_get_game_name()
# os.environ.update(
#     taskId=str(env.taskId),
#     game_name=str(env.game_name),
#     game_platfrom=str(env.game_platfrom),
#     game_id=str(env.game_id)
# )
#
# monitor_task_status(env, f"执行账户 {username}", '')

# using("./utility/application.air")
# from application import *



# 打印环境参数
# print_env_args()


    ### **********************任务类型区分********************** ###
    def is_fabu_task(self):
        env = AppEnv.get_instance()
        is_fabu = env.taskType == TaskType.FABU.value or env.taskType == TaskType.PC_FABU_OCR.value or env.taskType == TaskType.CAPTCHA_TASK.value
        monitor_print(f"---is_fabu_task:{is_fabu}")
        return is_fabu


    # 这个接口用于确定是脚本自己登录，还是外部登录（手机号发布）, 托管发布不做处理是因为网易系的游戏重启登录态还在，可以尝试解决踢登问题
    def is_outer_login_task(self):
        env = AppEnv.get_instance()
        is_outer_fabu = (env.taskType == TaskType.CAPTCHA_TASK.value)
        monitor_print(f"---is_outer_fabu:{is_outer_fabu}")
        return is_outer_fabu


    # 处理不同类型下的订单，是否需要脚本执行前的清理
    def before_start_clean(self):
        env = AppEnv.get_instance()
        launchType = env.launchType
        # 这里的tuoguan是针对common脚本的处理，保证不会clean
        if env.taskSource == TaskSource.TUOGUAN.value or env.mode == 'submit_ext_info' or env.taskType == TaskType.CAPTCHA_TASK.value:
            # 这些case不需要脚本执行前的清理
            monitor_print(f"---before_start_clean_no_need")
        else:
            monitor_print(f"---before_start_clean")
            if launchType == 'localtest':
                if env.localtest_need_clean:
                    try:
                        self.main_clean_game(-1, desc='from_start')
                    except Exception:
                        ...
            else:
                try:
                    self.main_clean_game(-1, desc='from_start')
                except Exception:
                    ...


    def is_clean_game_task(self):
        env = AppEnv.get_instance()
        is_clean_game = env.taskType == TaskType.CLEAN_GAME_TASK.value
        return is_clean_game


    def is_update_qufu_task(self):
        env = AppEnv.get_instance()
        is_update_qufu = env.taskType == TaskType.UPDATE_QUFU_TASK.value
        return is_update_qufu


    def is_gonglue_game_task(self):
        env = AppEnv.get_instance()
        is_gonglue_game = env.taskType == TaskType.GAME_GONGLUE_TASK.value
        return is_gonglue_game


    def is_eagle_down_task(self):
        env = AppEnv.get_instance()
        is_eagle_down_task = env.taskType == TaskType.EAGLE_DOWN_TASK.value
        return is_eagle_down_task


    def is_eagle_query_task(self):
        env = AppEnv.get_instance()
        is_eagle_query_task = env.taskType == TaskType.EAGLE_QUERY_TASK.value
        return is_eagle_query_task

    def is_mcp_task(self):
        env = AppEnv.get_instance()
        is_mcp_task = env.taskType == TaskType.MCP_TASK.value
        return is_mcp_task

    def is_ai_rebind_task(self):
        # 7777是换绑任务前缀； 7778是换绑手机号释放任务前缀
        env = AppEnv.get_instance()
        is_ai_rebind = env.taskType == TaskType.AI_REBIND_TASK.value
        return is_ai_rebind

    def is_headless_chrome_task(self):
        #
        env = AppEnv.get_instance()
        is_headless_chrome = env.taskType == TaskType.HEADLESS_CHROME_TASK.value
        return is_headless_chrome




    ### **********************不同任务对应的脚本依赖********************** ###
    # 根据发布和验号，引用不同的脚本
    # 根据发布和验号，引用不同的脚本
    # biz_module = None
    # if is_fabu_task():
    #     air_name = f"{gameDir}_fabu.air"
    #     biz_module = lx_import(air_name)
    #
    #     monitor_task_status(env, f"执行发布脚本", '')
    #     # game_will_launch, game_did_launch, game_will_close,game_will_clean,app_will_process_exception_snapshot,app_will_process_properties
    # elif is_clean_game_task():
    #     air_name = f"{gameDir}_clean.air"
    #     biz_module = lx_import(air_name)
    #     monitor_task_status(env, f"执行clean脚本", '')
    # elif is_update_qufu_task():
    #     air_name = f"{gameDir}_qufu.air"
    #     biz_module = lx_import(air_name)
    #     monitor_task_status(env, f"执行区服更新脚本", '')
    # elif is_gonglue_game_task():
    #     air_name = f"{gameDir}_gonglue.air"
    #     biz_module = lx_import(air_name)
    #     monitor_task_status(env, f"执行游戏攻略脚本", '')
    # elif is_eagle_down_task():
    #     air_name = f"{gameDir}_down.air"
    #     biz_module = lx_import(air_name)
    #     monitor_task_status(env, f"执行down脚本", '')
    # elif is_eagle_query_task():
    #     air_name = f"{gameDir}_query.air"
    #     biz_module = lx_import(air_name)
    #     monitor_task_status(env, f"执行query脚本", '')
    # else:
    #     air_name = f"{gameDir}_index.air"
    #     biz_module = lx_import(air_name)
    #
    #     monitor_task_status(env, f"执行验号脚本", f'{air_name}')
        # game_will_launch, game_did_launch, game_will_close,game_will_clean,app_will_process_exception_snapshot,app_will_process_properties


    def import_game_module(self):
        env = AppEnv.get_instance()
        cur_module = None

        def process_import_relative_path(py_dir, py_name):
            # 传入的是相对路径的情况
            py_relative_path = None
            # 这里交易猫的 case 下task_appId是空的，务必要注意
            if env.task_appId == TaskAppId.TASK_APPID_KEJINSHOU.value:
                py_relative_path = f'../../kejinshou/{env.gameDir}/{py_dir}/{py_name}'
            else:
                if env.system_type == 'android':
                    py_relative_path = f'../../{env.gameDir}/{py_dir}/{py_name}'
                elif env.system_type == TaskBizPlatformType.BIZ_PLATFORM_HEADLESS_CHROME.value:
                    py_relative_path = f'../../headless_chrome/{env.gameDir}/{py_dir}/{py_name}'
                else:
                    py_relative_path = f'../../iOS/{env.gameDir}/{py_dir}/{py_name}'

            monitor_task_status(env, f"---import_game_module:{py_relative_path}", '')
            monitor_print(f"---import_game_module:{py_relative_path}")
            return py_relative_path

        air_name = None
        py_name = None
        if env.task_appId == TaskAppId.TASK_APPID_KEJINSHOU.value:
            monitor_task_status(env, f"kejinshou执行", '')
            if self.is_fabu_task():
                air_name = f"{env.gameDir}_fabu"
                py_name = f"{env.gameDir}_fabu.py"

                monitor_task_status(env, f"kejinshou执行发布脚本: {air_name}, {py_name}", '')
        else:
            monitor_task_status(env, f"jiaoyimao执行", '')

            if env.system_type == TaskBizPlatformType.BIZ_PLATFORM_ANDROID.value or env.system_type == TaskBizPlatformType.BIZ_PLATFORM_IOS.value or env.system_type == TaskBizPlatformType.BIZ_PLATFORM_YUNYOU_IOS.value:
                if self.is_fabu_task():
                    air_name = f"{env.gameDir}_fabu.air" if env.system_type == 'android' else f"{env.gameDir}_fabu"
                    py_name = f"{env.gameDir}_fabu.py"

                    monitor_task_status(env, f"执行发布脚本: {air_name}, {py_name}", '')
                    # game_will_launch, game_did_launch, game_will_close,game_will_clean,app_will_process_exception_snapshot,app_will_process_properties
                elif self.is_clean_game_task():
                    air_name = f"{env.gameDir}_clean.air" if env.system_type == 'android' else f"{env.gameDir}_clean"
                    py_name = f"{env.gameDir}_clean.py"

                    # cur_module = lx_import(air_name)
                    monitor_task_status(env, f"执行clean脚本: {air_name}, {py_name}", '')
                elif self.is_update_qufu_task():
                    air_name = f"{env.gameDir}_qufu.air" if env.system_type == 'android' else f"{env.gameDir}_qufu"
                    py_name = f"{env.gameDir}_qufu.py"

                    monitor_task_status(env, f"执行区服更新脚本: {air_name}, {py_name}", '')
                elif self.is_gonglue_game_task():
                    air_name = f"{env.gameDir}_gonglue.air" if env.system_type == 'android' else f"{env.gameDir}_gonglue"
                    py_name = f"{env.gameDir}_gonglue.py"

                    monitor_task_status(env, f"执行游戏攻略脚本: {air_name}, {py_name}", '')
                elif self.is_eagle_down_task():
                    air_name = f"{env.gameDir}_down.air" if env.system_type == 'android' else f"{env.gameDir}_down"
                    py_name = f"{env.gameDir}_down.py"

                    monitor_task_status(env, f"执行down脚本: {air_name}, {py_name}", '')
                elif self.is_eagle_query_task():
                    air_name = f"{env.gameDir}_query.air" if env.system_type == 'android' else f"{env.gameDir}_query"
                    py_name = f"{env.gameDir}_query.py"

                    monitor_task_status(env, f"执行query脚本: {air_name}, {py_name}", '')
                elif self.is_mcp_task():
                    air_name = f"{env.gameDir}_action.air" if env.system_type == 'android' else f"{env.gameDir}_action"
                    py_name = f"{env.gameDir}_action.py"

                    monitor_task_status(env, f"执行mcp_action脚本: {air_name}, {py_name}", '')
                elif self.is_ai_rebind_task():
                    air_name = f"{env.gameDir}_rebind.air" if env.system_type == 'android' else f"{env.gameDir}_rebind"
                    py_name = f"{env.gameDir}_rebind.py"

                    monitor_task_status(env, f"执行ai_rebind脚本: {air_name}, {py_name}", '')
                else:
                    air_name = f"{env.gameDir}_index.air" if env.system_type == 'android' else f"{env.gameDir}_index"
                    py_name = f"{env.gameDir}_index.py"

                    monitor_task_status(env, f"执行验号脚本: {air_name}, {py_name}", f'{air_name}')
            elif env.system_type == TaskBizPlatformType.BIZ_PLATFORM_HEADLESS_CHROME.value:
                if self.is_headless_chrome_task():
                    air_name = f"{env.gameDir}_headlesschrome"
                    py_name = f"{env.gameDir}_headlesschrome.py"

                monitor_task_status(env, f"执行headlesschrome脚本: {air_name}, {py_name}", '')
            else:
                monitor_task_status(env, f"未找到对应的执行脚本", '')
                raise RuntimeError(
                    "没有找到对应的脚本，请检查task_appId, system_type, task_type, task_source"
                )

        py_relative_path = process_import_relative_path(air_name, py_name)
        cur_module = lx_import(py_relative_path)

        return cur_module

    # def test_game_properties():
    #     # 代码
    #     properties = get_game_proerties_by_task()
    #     with open('output.txt', 'w') as file:
    #         # 写入文件
    #         file.write(json.dumps(properties) + '\n')
    #         # 打印到控制台
    #         # print(text_to_write)
    # test_game_properties()

    def set_login_status(self):
        env = AppEnv.get_instance()
        if env.taskSource == TaskSource.TUOGUAN.value:
            AppDynamicInfo.get_instance().setHasLogin(True)


    # 获取attr方法
    def get_module_attr_method(self, cur_module, func_name):
        if hasattr(cur_module, func_name):
            module_method = getattr(cur_module, func_name)
            return module_method
        return None


    ### **********************多子属性预拉取********************** ###
    # def app_did_get_properties(properties):
    def process_all_sub_properties(self, callback_func_name):
        monitor_print(f"---开始处理预拉取多子属性：{callback_func_name}")
        need_laqu_game_properties = False

        need_duozi_func = 'app_need_game_properties'
        # 判断模块中是否实现了指定方法
        if hasattr(self.biz_module, need_duozi_func):
            module_method = getattr(self.biz_module, need_duozi_func)
            need_game_properties = module_method()
            if need_game_properties:
                need_laqu_game_properties = True

        if need_laqu_game_properties == False:
            if self.is_fabu_task() == False:
                need_laqu_game_properties = False
            else:
                need_laqu_game_properties = True

        if need_laqu_game_properties == False:
            monitor_print(f"---不需要预拉取多子属性：{need_laqu_game_properties}")
            return

        monitor_print(f"---预拉取多子属性：{need_laqu_game_properties}")
        func_name = callback_func_name
        # 判断模块中是否实现了指定方法
        if hasattr(self.biz_module, func_name):
            # if func_name in globals():
            # 函数存在，可以安全地调用它
            properties = get_game_proerties_by_task()
            # if launchType == 'localtest':
            #     properties = get_game_proerties_by_task('729')

            if properties and len(properties) > 0 and properties['data'] and properties['data'][
                'gameProperties'] and len(properties['data']['gameProperties']) > 0:
                # monitor_print(f"---预拉取多子属性数据：{properties['data']['gameProperties']}")

                module_method = getattr(self.biz_module, func_name)
                module_method(properties['data']['gameProperties'])
            else:
                monitor_print(f"发布脚本：多子属性获取失败")
        else:
            monitor_print(f"---未实现多子属性获取方法：{callback_func_name}")


    ### **********************脚本loop设置********************** ###
    # 这里是从脚本获取执行的runloop数
    def get_runloop_count(self):
        loop = 2
        env = AppEnv.get_instance()
        launchType = env.launchType
        func_name = 'app_will_get_runloop_count'
        if hasattr(self.biz_module, func_name):
            runloop_count_method = getattr(self.biz_module, func_name)
            loop_count = runloop_count_method()
            loop = loop_count
            monitor_print(f"----app_will_get_runloop_count:{loop_count}")
        else:
            if env.taskSource == TaskSource.TUOGUAN.value:
                loop = 3
            elif env.taskType == TaskType.CAPTCHA_TASK.value and env.get_common_property_with_key(
                    'captchaTaskStatus') != None and int(env.get_common_property_with_key('captchaTaskStatus')) < 3:
                loop = 1
            elif env.taskType == TaskType.CLEAN_GAME_TASK.value:
                loop = 1

        return loop


    # 将当前的loop发给游戏
    def send_runloop_count(self, index):
        AppEnv.get_instance().runloop_index = index
        func_name = 'app_will_send_runloop_count'
        if hasattr(self.biz_module, func_name):
            runloop_count_method = getattr(self.biz_module, func_name)
            runloop_count_method(index)


    ### **********************主流程核心处理接口********************** ###

    def main_clean_game(self, index, desc=None):
        env = AppEnv.get_instance()

        if desc is None:
            monitor_print(f"---main_clean_game: index:{index}")
            monitor_task_status_v2(f"---main_clean_game: index:{index}", '')
        else:
            monitor_print(f"---main_clean_game_{desc}: index:{index}")
            monitor_task_status_v2(f"---main_clean_game_{desc}: index:{index}", '')

        try:
            self.biz_module.game_will_clean(env)
        except Exception:
            ...

        AppDynamicInfo.get_instance().setHasLogin(False)


    def main_close_game(self, index, desc=None):
        env = AppEnv.get_instance()
        if desc is None:
            monitor_print(f"---main_close_game: index:{index}")
            monitor_task_status_v2(f"---main_close_game: index:{index}", '')
        else:
            monitor_print(f"---main_close_game_{desc}: index:{index}")
            monitor_task_status_v2(f"---main_close_game_{desc}: index:{index}", '')
        # if index == 0 and env.taskType == TaskType.CAPTCHA_TASK.value and env.get_common_property_with_key('captchaTaskStatus') != None and int(env.get_common_property_with_key('captchaTaskStatus')) == 1:
        #     AppDynamicInfo.get_instance().setEnterCaptcha(True)
        self.biz_module.game_will_close(env)


    def start_game_thread(self):
        env = AppEnv.get_instance()
        if hasattr(self.biz_module, "game_thread_task"):
            monitor_print(f"---start_game_thread")
            monitor_task_status(env, "子线程启动", '')
            t = threading.Thread(target=self.biz_module.game_thread_task, args=(env,))
            t.setDaemon(True)
            t.start()


    def report_performance_log(self):
        per_info = AppPerformanceInfo.get_instance().getTimeDurationMap()
        monitor_print(f"---report_performance_log: {per_info}")
        monitor_task_flow_status_info(1010, per_info)


    def need_clean_and_close_game_before_run(self, index):
        monitor_task_status_v2(f'---need_clean_and_close_game_before_run____start', '')
        env = AppEnv.get_instance()
        launchType = env.launchType

        # 这两个参数的控制不影响本地执行逻辑
        need_clean_game = True
        need_close_game = True
        # if need_close_game:
        #     pass

        if index == 0 and env.mode == 'submit_ext_info':
            monitor_print('submit_ext_info任务不需要清理游戏，开始执行')
            monitor_task_status_v2(f'submit_ext_info任务不需要清理游戏，开始执行', '')
            need_clean_game = False
            need_close_game = False

        elif index == 0 and (env.taskType == TaskType.CAPTCHA_TASK.value or env.taskType == TaskType.CLEAN_GAME_TASK.value):
            # 手机号验证码的captchaTaskStatus存在并且不为1的情况下，不清理游戏
            need_clean_game = False
            need_close_game = False
            monitor_print(f"---任务不需要clean和close: index:{index}, tasktype:{env.taskType}")
            monitor_task_status_v2(f"---任务不需要clean和close: index: index:{index}, tasktype:{env.taskType}", '')
        else:
            if AppDynamicInfo.get_instance().getHoldGame() == True:
                need_close_game = False
                need_clean_game = False
                monitor_print(f"---任务HoldGame_true: index:{index}, tasktype:{env.taskType}")
                monitor_task_status_v2(f"---任务HoldGame_true: index:{index}, tasktype:{env.taskType}", '')
            else:
                if AppDynamicInfo.get_instance().getHasLogin() == True:
                    monitor_print(f"---任务HoldGame_false_login_true: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(f"---任务HoldGame_false_login_true: index:{index}, tasktype:{env.taskType}", '')
                    need_close_game = True
                    need_clean_game = False
                else:
                    monitor_print(f"---任务HoldGame_false_login_false: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(f"---任务HoldGame_false_login_false: index:{index}, tasktype:{env.taskType}", '')
                    need_close_game = True
                    need_clean_game = True

        monitor_print(
            f'---need_clean_and_close_game_before_run_final_check: need_clean_game: {need_clean_game}, need_close_game:{need_close_game}')
        monitor_task_status_v2(
            f'---need_clean_and_close_game_before_run_final_check: need_clean_game:{need_clean_game}, need_close_game:{need_close_game}',
            '')

        if need_close_game == True:
            if launchType == 'localtest':
                if env.localtest_need_clean:
                    self.main_close_game(index, desc='before_run')
                    monitor_print(f"---need_clean_and_close_game_before_run_need_close_game_local: index:{index}")
                    monitor_task_status_v2(f"---need_clean_and_close_game_before_run_need_close_game_local: index:{index}",
                                           '')
            else:
                self.main_close_game(index, desc='before_run')
                monitor_print(f"---need_clean_and_close_game_before_run_need_close_game: index:{index}")
                monitor_task_status_v2(f"---need_clean_and_close_game_before_run_need_close_game: index:{index}", '')

        # 这里无论是否close，都要启动下应用，保证应用启动，并且在前台
        # if check_phone_captcha() == False:
        #     monitor_print(f"---check_phone_captcha_no_launch: index:{index}, tasktype:{env.taskType}")
        #     monitor_task_status_v2(f"---check_phone_captcha_no_launch: index:{index}, tasktype:{env.taskType}", '')
        #     biz_module.game_will_launch(env)
        # else:
        #     monitor_print(f"---check_phone_captcha_launch: index:{index}, tasktype:{env.taskType}")
        #     monitor_task_status_v2(f"---check_phone_captcha_launch: index:{index}, tasktype:{env.taskType}", '')

        if need_clean_game == True:
            if launchType == 'localtest':
                if env.localtest_need_clean:
                    self.main_clean_game(index, desc='before_run')
            else:
                self.main_clean_game(index, desc='before_run')
                monitor_print(
                    f"---need_clean_and_close_game_before_run_need_clean_game: index:{index}, tasktype:{env.taskType}")
                monitor_task_status_v2(
                    f"---need_clean_and_close_game_before_run_need_clean_game: index:{index}, tasktype:{env.taskType}", '')

        # 这里的启动要等到clean后才能再启动，并且启动要根据need_close_game参数来决定
        if need_close_game == True:
            if launchType == 'localtest':
                if env.localtest_need_clean:
                    monitor_print(
                        f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}", '')
                    self.biz_module.game_will_launch(env)
            else:
                monitor_print(
                    f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}")
                monitor_task_status_v2(
                    f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}", '')
                self.biz_module.game_will_launch(env)

        monitor_task_status_v2(f'---need_clean_and_close_game_before_run____end', '')


    def check_phone_captcha(self):
        env = AppEnv.get_instance()
        phone_captch = False
        if env.taskType == TaskType.CAPTCHA_TASK.value or env.taskType == TaskType.CLEAN_GAME_TASK.value:
            phone_captch = True
        return phone_captch


    def need_clean_and_close_game_after_run(self, index, suc=False, result=None):
        monitor_task_status_v2(f'---need_clean_and_close_game_after_run____start', '')
        env = AppEnv.get_instance()
        launchType = env.launchType

        # 这两个参数的控制不影响本地执行逻辑,脚本执行结束的处理默认是false
        need_clean_game = False
        need_close_game = False

        if suc == False:
            monitor_print(f"---need_clean_and_close_game_after_run_suc_false: index:{index}")
            monitor_task_status_v2(f"---need_clean_and_close_game_after_run_suc_false: index:{index}", '')
            action_type = result.getActionType()
            if action_type == AppActionType.STOP_APP:
                if AppDynamicInfo.get_instance().getHoldGame() == True:
                    monitor_print(
                        f"---need_clean_and_close_game_after_run_stop_app_hold_game: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---need_clean_and_close_game_after_run_stop_app_hold_game: index:{index}, tasktype:{env.taskType}",
                        '')
                    need_clean_game = False
                    need_close_game = False
                else:
                    monitor_print(
                        f"---need_clean_and_close_game_after_run_stop_app_no_hold_game: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---need_clean_and_close_game_after_run_stop_app_no_hold_game: index:{index}, tasktype:{env.taskType}",
                        '')
                    need_clean_game = True
                    need_close_game = True
            elif action_type == AppActionType.STOP_RUNLOOP:
                if index == self.get_runloop_count() - 1:
                    monitor_print(
                        f"---need_clean_and_close_game_after_run_stop_runloop_last_loop: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---need_clean_and_close_game_after_run_stop_runloop_last_loop: index:{index}, tasktype:{env.taskType}",
                        '')
                    need_clean_game = True
                    need_close_game = True
                else:
                    if AppDynamicInfo.get_instance().getHasLogin() == True:
                        monitor_print(
                            f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_has_login: index:{index}, tasktype:{env.taskType}")
                        monitor_task_status_v2(
                            f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_has_login: index:{index}, tasktype:{env.taskType}",
                            '')
                        need_clean_game = False
                        need_close_game = True
                    else:
                        monitor_print(
                            f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_not_has_login: index:{index}, tasktype:{env.taskType}")
                        monitor_task_status_v2(
                            f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_not_has_login: index:{index}, tasktype:{env.taskType}",
                            '')
                        need_clean_game = True
                        need_close_game = True
            else:
                need_clean_game = True
                need_close_game = True
        else:
            monitor_print(
                f"---need_clean_and_close_game_after_run_suc: index:{index}, tasktype:{env.taskType}")
            monitor_task_status_v2(
                f"---need_clean_and_close_game_after_run_suc: index:{index}, tasktype:{env.taskType}",
                '')
            need_clean_game = True
            need_close_game = True

        if self.check_phone_captcha() == False:
            if need_close_game:
                if launchType == 'localtest':
                    if env.localtest_need_clean:
                        self.main_close_game(index, desc='after_run')
                else:
                    self.main_close_game(index, desc='after_run')
                    monitor_print(
                        f"---check_phone_captcha_after_run_close_game: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---check_phone_captcha_after_run_close_game: index:{index}, tasktype:{env.taskType}",
                        '')

            if need_clean_game:
                if launchType == 'localtest':
                    if env.localtest_need_clean:
                        self.main_clean_game(index, desc='after_run')
                else:
                    self.main_clean_game(index, desc='after_run')
                    monitor_print(
                        f"---check_phone_captcha_after_run_clean_game: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---check_phone_captcha_after_run_clean_game: index:{index}, tasktype:{env.taskType}",
                        '')
        else:
            if need_clean_game:
                if launchType == 'localtest':
                    if env.localtest_need_clean:
                        self.main_clean_game(index, desc='after_run')
                else:
                    self.main_clean_game(index, desc='after_run')
                    monitor_print(
                        f"---normal_after_run_clean_game: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---normal_after_run_clean_game: index:{index}, tasktype:{env.taskType}",
                        '')

            if need_close_game:
                if launchType == 'localtest':
                    if env.localtest_need_clean:
                        self.main_close_game(index, desc='after_run')
                else:
                    self.main_close_game(index, desc='after_run')
                    monitor_print(
                        f"---normal_after_run_close_game: index:{index}, tasktype:{env.taskType}")
                    monitor_task_status_v2(
                        f"---normal_after_run_close_game: index:{index}, tasktype:{env.taskType}",
                        '')

            monitor_task_status_v2(f'---need_clean_and_close_game_after_run____end', '')

            # 结束后上报性能日志
            self.report_performance_log()


    def files_clean_and_adjust(self, index):

        env = AppEnv.get_instance()

        if is_directory_exists(env.logPath):
            if env.launchType != 'localtest' or env.localtest_remove_log == True:
                delete_files_with_format(env, index, env.logPath, '*.jpg', 'adc_exception_')

            if index > 0:  # 第二次及以后的重试修改为log_{index}.tst文件，最后一次的log是log.txt
                rename_file_with_format(env, index, env.logPath, '*.txt')


    def process_exception_after_change_result(self, index, result):
        error_task_status = get_task_status_last_errorcode()
        monitor_print(
            f"---process_exception_after_change_result_start:{result.getActionType()}, {result.get_ext_info()}, {error_task_status}")
        if error_task_status is None:
            return result

        # 如果是账号被踢，同时是手机号发布，则需要调整异常
        if error_task_status == 10010 and self.is_outer_login_task():
            monitor_print(
                f"---process_exception_after_change_result_before:{result.getActionType()}, {result.get_ext_info()}")
            new_result = AppRunResult()
            new_ext_info = {'key': str(error_task_status)}
            new_result.updateInfo(AppActionType.STOP_APP, Exception("process_exception后的异常调整"), ext_info=new_ext_info)
            monitor_task_status_v2(f'---process_exception_after_change_result_change', 'process_exception后的异常调整')
            monitor_print(
                f"---process_exception_after_change_result_after:{new_result.getActionType()}, {new_result.get_ext_info()}")
            return new_result

        return result


    ### **********************脚本正式启动********************** ###
    # 脚本正式启动
    def start_core_flow(self):
        env = AppEnv.get_instance()
        monitor_task_status_v2(f'---main_run____start', '')

        start_time = time.perf_counter()
        global ext_info
        global error_desc

        launchType = env.launchType

        # app = Application()

        # 处理不同类型下的订单，是否需要先清理登录态
        self.before_start_clean()

        # 根据入参设置登录状态
        self.set_login_status()

        # 预先获取多子属性
        self.process_all_sub_properties('app_did_get_properties')

        # 启动子线程
        self.start_game_thread()

        loop = self.get_runloop_count()

        index = 0
        sucessFinish = False
        for index in range(0, loop):

            # ios下，如果是被踢状态，则需要重连，被踢状态有2个地方设备，一个是120024的异常，一个是cb
            if env.system_type == SystemType.IOS and AppDynamicInfo.get_instance().iosHasKicked == True:
                self.connect_mds()

            self.send_runloop_count(index)

            monitor_task_status(env, f"脚本重试loop - {index}", '')

            self.files_clean_and_adjust(index)

            self.need_clean_and_close_game_before_run(index)

            phaseList = self.biz_module.game_did_launch(env)[:] # 进行深拷贝，避免修改全局变量
            self.setPhaseList(phaseList)
            self.phaseList.append(Phase("商品码合图", lambda: phase_composite_image(env)))
            monitor_task_status(env, f"{env.gameDir} 游戏脚本运行开始", '')
            result = self.run(env)
            monitor_task_status(env, f"{env.gameDir} 游戏脚本运行结束", '')

            # 无论是否有异常，都正常上传adc_catch图片，在子线程中执行上传
            monitor_task_status_v2(f'---upload_adc_catch_images:{index}', '')
            self.upload_adc_catch_images(index)

            if result.getActionType() == AppActionType.STOP_DEFAULT:
                monitor_task_status_v2(f'---current_loop_success:{index}', '')

                sucessFinish = True

                self.need_clean_and_close_game_after_run(index, True)

                monitor_task_status(env, f"{env.gameDir} 游戏脚本main start运行结束", '')
                break

            # 这里的errorInfo可能是错误，也可能是正常的业务流程的结束（比如手机号验证码登录）
            errorInfo = result.exceptionInfo()
            if errorInfo:
                monitor_task_status_v2(f'---current_loop_fail:{index}', '')

                monitor_task_status_v2(f'---report_exception_info:{index}', '')
                try:
                    result = self.report_exception_info(env, result, index)
                # except Exception as e:
                #     error_traceback = traceback.format_exc()
                #     monitor_task_status(env, '脚本app_will_process_exception_snapshot方法抛出异常', f"{error_traceback}",
                #                         10104)
                #     ext_info = {'key': '120008', 'desc': "脚本app_will_process_exception_snapshot方法抛出异常",
                #                 'type': AppActionType.STOP_APP}
                #     break
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    monitor_task_status_v2(f'---report_exception_info_exception:{index}', '')
                    self.handle_all_exceptions(e, error_traceback, AppStateType.STAGE_REPORT_EXCEPT)
                    # if new_result.getActionType() == AppActionType.STOP_APP:
                    #     result = new_result


                monitor_print(f"---upload_adc_catch_images:{result.getActionType()}")
                monitor_task_status_v2(f'---need_clean_and_close_game_after_run:{index}', '')

                try:
                    self.need_clean_and_close_game_after_run(index, False, result)
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    monitor_task_status_v2(f'---need_clean_and_close_game_after_run_exception:{index}', '')
                    self.handle_all_exceptions(e, error_traceback, AppStateType.STAGE_AFTER_RUN)
                    # if new_result.getActionType() == AppActionType.STOP_APP:
                    #     result = new_result

                monitor_print(f"---adc_change_result:{result.getActionType()}, {result.get_ext_info()}")
                monitor_task_status_v2(f'---after_run_process_result:{index}', '')

                if result.getActionType() == AppActionType.STOP_RUNLOOP:
                    monitor_print(f"---adc_start_stop_runloop:{result.getActionType()}, {result.get_ext_info()} ")
                    if index == loop - 1:
                        ext_info = {'key': '120000', 'desc': '两次重试出错', 'type': AppActionType.STOP_RUNLOOP}
                        error_desc = '两次重试出错'
                    else:
                        if env.system_type == SystemType.IOS:
                            # 这里是针对ios操作超时后，等待一定的时间，让自动重连连接成功
                            temp_ext_info = result.get_ext_info()
                            if temp_ext_info is not None and 'key' in temp_ext_info:
                                status = int(temp_ext_info['key'])
                                if status == 120024:
                                    AppDynamicInfo.get_instance().iosHasKicked = True

                    continue
                elif result.getActionType() == AppActionType.STOP_APP:
                    # 这里如果是传递了错误码，则按错误码处理统一为120006
                    ext_info = result.get_ext_info()
                    if isinstance(errorInfo, PhaseException):
                        error_desc = self.get_exception_desc(errorInfo)
                    else:
                        error_desc = str(errorInfo)
                    ext_info['desc'] = error_desc
                    ext_info['type'] = AppActionType.STOP_APP

                    monitor_print(f"---adc_start_stop_app:{result.getActionType()}, {result.get_ext_info()}")
                    break

        if index >= loop - 1 and sucessFinish == False:
            # todo - 给游戏接口确定是否要在最终结束后，重启游戏
            need_launch = True
            cur_method = self.get_module_attr_method(self.biz_module, 'game_need_launch_last')
            if cur_method:
                need_launch = cur_method()
            if need_launch:
                self.biz_module.game_will_launch(env)

        end_time = time.perf_counter()
        monitor_print(f"---纯脚本耗时:{end_time - start_time}")

        monitor_task_status_v2(f'---main_run____end', '')


    ### **********************异常状态的处理********************** ###
    def upload_adc_catch_images(self, index):
        monitor_task_status_v2(f'---upload_adc_catch_images____start', '')

        env = AppEnv.get_instance()
        start_time = time.perf_counter()
        launchType = env.launchType

        if launchType == 'localtest' and env.localtest_need_upload == False:
            return

        # 获取脚本名称
        script_name = ""
        rebind_json = env.get_common_property_with_key('aiRebindExtParams')
        if rebind_json is not None:
            rebind_data = json.loads(rebind_json)
            script_name = rebind_data.get('scriptName')

        files = get_sorted_files_with_prefix(ST.LOG_DIR, 'adc_catch')
        if files is not None and len(files) > 0:
            _, cdn_urls = upload_jym_oss_with_pathes(files)
            if cdn_urls is not None and len(cdn_urls) > 0:
                # 这里的第二个参数不能动，因为要用于神之领域
                monitor_post_task_status(f'上传自定义图片_{script_name}', f"{cdn_urls}")
                # monitor_task_status_v2(f'上传自定义图片', f"{cdn_urls}")
            else:
                monitor_post_task_status(f'上传空自定义图片_{script_name}', f"{cdn_urls}")
        end_time = time.perf_counter()
        monitor_print(f"---上传自定义图片耗时s:{end_time - start_time}")

        monitor_task_status_v2(f'---upload_adc_catch_images____end', '')


    def report_exception_info(self, env, result, index):
        # raise Exception("report_exception_info_not_implement")

        launchType = env.launchType
        if launchType == 'localtest' and env.localtest_need_upload == False:
            return result

        performance_start_timestamp = int(time.time() * 1000000)
        except_type = result.getActionType()

        monitor_task_status_v2(f'---report_exception_info____start', '')

        monitor_print(f"---process_except:except_type:{except_type}, index:{index}")
        file_prefix = 'adc_exception'
        if except_type == AppActionType.STOP_APP:
            file_prefix = 'adc_exception_stop_app'
        elif except_type == AppActionType.STOP_RUNLOOP:
            file_prefix = 'adc_exception_stop_runloop'

        # 上报异常图片
        file_name_path = None
        file_name_path = self.app_snapshot_when_exception(file_prefix, index)

        # 这里当holdgame的情况下，则不用调用处理异常的接口，认为是游戏界面是正常的
        if AppDynamicInfo.get_instance().getHoldGame() == False:
            monitor_task_status(env, '---处理app_will_process_exception_snapshot', f"")
            self.biz_module.app_will_process_exception_snapshot(file_name_path)

        except_oss_info = upload_jym_oss_with_pathes([file_name_path])
        except_oss_pathes, except_cdn_urls = except_oss_info

        monitor_task_status(env, '上传exception图片', f"{except_cdn_urls}")

        # 改变Result状态
        result = self.process_exception_after_change_result(index, result)

        # 上报时光机
        all_operate_image_pathes = get_directory_sorted_timestamp_files(ST.LOG_DIR)
        operate_image_pathes = all_operate_image_pathes[-30:]

        operate_oss_info = upload_jym_oss_with_pathes(operate_image_pathes)
        operate_oss_pathes, operate_cdn_urls = operate_oss_info

        sorted_operate_cdn_urls = sorted(operate_cdn_urls, key=get_number_from_path)

        # 获取脚本名称
        script_name = ""
        rebind_json = env.get_common_property_with_key('aiRebindExtParams')
        if rebind_json is not None:
            rebind_data = json.loads(rebind_json)
            script_name = rebind_data.get('scriptName')

        monitor_task_status(env, f'上传操作流30张图片_{script_name}', f"{sorted_operate_cdn_urls}")

        monitor_task_status_v2(f'---report_exception_info____end', '')

        performance_interval = int(time.time() * 1000000) - performance_start_timestamp
        monitor_task_status_v2(f"report_exception_info_cost", f"---report_exception_info_cost:{performance_interval}")

        return result

    def app_snapshot_when_exception(self, file_name_prefix, loop_index=None):
        file_name = file_name_prefix + '_' + str(int(time.time() * 1000000)) + '.jpg'
        if loop_index != None and loop_index >= 0:
            file_name = file_name_prefix + '_' + str(loop_index) + '_' + str(int(time.time() * 1000000)) + '.jpg'
        adc_snapshot(filename=file_name, msg="get a snapshot.")
        final_path = os.path.join(ST.LOG_DIR, file_name)
        return final_path

    def get_exception_desc(self, e):
        inner_e = e.get_inner_e()
        e_args = inner_e.args
        if len(e_args) > 0:
            return e_args[0]
        return None


    ################### 失败后的处理
    def process_ext_info(self, env, ext_info):
        monitor_task_status_v2(f'---process_ext_info____start', '')

        status = int(ext_info['key'])
        type = ext_info['type']
        desc = ext_info['desc']

        # upload_oss(env)
        log_oss_result = upload_jymoss_with_prefix_name('log', need_sort=False)
        if log_oss_result is not None:
            log_oss_path, log_cdn_urls = log_oss_result
            monitor_task_status_v2('上传log.txt', f"{log_cdn_urls}")
        else:
            monitor_task_status_v2('上传log.txt', f"没有log.txt")


        partial_func = AppDynamicInfo.get_instance().partial_func

        monitor_print(f"---process_ext_info:{status}, type:{type}, desc:{desc}, partial_func:{partial_func}")
        monitor_task_status_v2('---process_ext_info_upload', f"{status}, type:{type}, desc:{desc},partial_func:{partial_func}")

        if type == AppActionType.STOP_RUNLOOP:
            if status == 120000:
                monitor_task_status(env, '脚本main start结束', '两次重试出错')

                error_task_status = get_task_status_last_errorcode()
                monitor_print(f"---process_ext_info_get_task_status_last_errorcode:{error_task_status}")
                monitor_task_status_v2('process_ext_info',
                                       f"last_errorcode:{error_task_status}")

                if error_task_status is not None:
                    monitor_task_status_v2('上报stop_runloop错误结束码', f'串流上报错误结束码{error_task_status},{desc}')
                    request_workflow_task_status('上报stop_runloop错误结束码',
                                                 f'串流上报错误结束码{error_task_status},{desc}', error_task_status)

                    monitor_task_status_v2('任务中心stop_runloop错误结束码',
                                           f'任务中心上报错误结束码{error_task_status},{desc}')
                    monitor_report_task_info(env, error_task_status)
                    if partial_func:
                        monitor_task_status_v2('before执行partial_func', 'before执行partial_func')
                        partial_func()
                        monitor_task_status_v2('after执行partial_func', 'after执行partial_func')
                else:
                    monitor_task_status_v2('上报stop_runloop结束码', f'串流上报错误结束码{status},{desc}')
                    request_workflow_task_status('上报stop_runloop结束码', f'串流上报错误结束码{status},{desc}', status)

                    monitor_task_status_v2('任务中心stop_runloop结束码', f'任务中心上报错误结束码{status},{desc}')
                    monitor_report_task_info(env, status)
                    if partial_func:
                        monitor_task_status_v2('before执行partial_func', 'before执行partial_func')
                        partial_func()
                        monitor_task_status_v2('after执行partial_func', 'after执行partial_func')

        elif type == AppActionType.STOP_APP:
            monitor_task_status_v2('上报stop_app结束码', f'串流上报结束码{status},{desc}')
            if status == 200:
                # 游戏保持，并holdgame的流程中，从设备角度看一直是任务执行中，需要按照4的状态来上报串流
                request_workflow_task_status('上报stop_app结束码', f'串流上报结束码{status},{desc}', 4)
            else:
                if self.is_ai_rebind_task():
                    monitor_task_status_v2('ai换绑任务异常状态修改status为4', f'源状态{status}')
                    status = '4'
                request_workflow_task_status('上报stop_app结束码', f'串流上报结束码{status},{desc}', status)

            monitor_task_status_v2('任务中心stop_app结束码', f'任务中心上报结束码{status},{desc}')
            monitor_report_task_info(env, status)
            if partial_func:
                monitor_task_status_v2('before执行partial_func', 'before执行partial_func')
                partial_func()
                monitor_task_status_v2('after执行partial_func', 'after执行partial_func')

        monitor_task_status_v2(f'---process_ext_info____end', '')


    ### **********************成功后的数据上传********************** ###
    def process_upload_oss(self, env):
        monitor_task_status_v2(f'---process_upload_oss____start', '')

        partial_func = AppDynamicInfo.get_instance().partial_func

        # 处理结果图片
        report_urls = []
        report_cdn_urls = []
        if self.is_fabu_task() or self.is_ai_rebind_task():
            url_info = upload_jym_oss(env)
            if url_info is not None and len(url_info) > 0:
                report_urls, report_cdn_urls = url_info

            upload_jym_oss_with_log()
        else:
            urls = upload_oss(env)
            report_urls = urls
            report_cdn_urls = urls

        if report_urls is None or len(report_urls) == 0:
            monitor_task_status(env, 'report_urls上传None', "")
        else:
            monitor_task_status(env, '上传urls', f"{report_urls}")
            monitor_task_status(env, '上传cdn_urls', f"{report_cdn_urls}")

        # 处理seller图片
        # seller_urls = []
        report_seller_urls = []
        report_seller_cdn_urls = []
        if self.is_fabu_task():
            seller_url_info = upload_jymoss_with_prefix_name('adc_seller')
            if seller_url_info is not None and len(seller_url_info) > 0:
                report_seller_urls, report_seller_cdn_urls = seller_url_info
        else:
            seller_urls = upload_lingxioss_with_prefix_name('adc_seller')
            report_seller_urls = seller_urls

        if report_seller_urls is None or len(report_seller_urls) == 0:
            monitor_task_status(env, '没有seller_urls', '')
        else:
            monitor_task_status(env, '上传seller urls', f"{report_seller_urls}")

        # 处理seller信息
        seller_properties = None
        # app_will_process_sellers 返回的map中可能有两个key：roleId和channelUserId
        seller_func = 'app_will_process_sellers'
        if hasattr(self.biz_module, seller_func):
            monitor_print(f"----app_will_process_sellers:{report_seller_urls}")
            module_seller_method = getattr(self.biz_module, seller_func)
            sellers_info = module_seller_method(report_seller_urls)

            if sellers_info is not None and len(sellers_info) > 0:
                seller_properties = sellers_info

        # 上传log.txt文件
        log_pathes = get_log_txt_files(env)
        _, log_cdn_urls = upload_jym_oss_with_pathes(log_pathes)
        monitor_task_status(env, '上传log.txt', f"{log_cdn_urls}")

        # 图片上传后统计内存
        memory_usage = get_memory_usage()
        monitor_task_status_v2(f"内存使用情况", f"当前内存使用情况: {memory_usage}KB")
        monitor_print(f"---phase内存使用情况: {memory_usage}KB")

        launchType = env.launchType
        game_properties = None
        task_status = 6

        # 处理多子属性信息
        monitor_task_status_v2(f'---process_upload_oss____properties', '')
        reward_method = self.get_module_attr_method(self.biz_module, 'game_need_force_upload_properties')
        force_upload_properties = False
        if reward_method:
            force_upload_properties = reward_method()
            monitor_print(f"---game_need_force_upload_properties_main: {force_upload_properties}")

        func_name = 'app_will_process_properties'
        if (self.is_fabu_task() or force_upload_properties == True) and report_cdn_urls and len(report_cdn_urls) > 0:
            # 判断模块中是否实现了指定方法
            if hasattr(self.biz_module, func_name):
                # if func_name in globals():
                # 函数存在，可以安全地调用它
                if  env.task_appId == TaskAppId.TASK_APPID_KEJINSHOU.value:
                    monitor_task_status_v2(f'---kejinshou_process_upload_oss____get_properties', '')
                    module_method = getattr(self.biz_module, func_name)
                    result_properties = module_method([], report_cdn_urls)
                    # result_properties = module_method(properties['data']['gameProperties'], report_cdn_urls)
                    task_status, game_properties, append_oss_info = result_properties
                    monitor_print(f"---kejinshou_app_will_process_properties_result:{result_properties}")
                    if append_oss_info is not None:
                        oss_pathes, cdn_urls = append_oss_info
                        report_urls = oss_pathes + report_urls
                else:
                    monitor_task_status_v2(f'---process_upload_oss____get_properties', '')

                    properties = get_game_proerties_by_task()
                    if properties is not None:
                        monitor_print(f"---app_will_process_properties_source_has:{properties}, {type(properties)}")
                    else:
                        monitor_print(f"---app_will_process_properties_source_none")
                    # if launchType == 'localtest':
                    #     properties = get_game_proerties_by_task('729')

                    if properties and len(properties) > 0 and properties['data'] and properties['data'][
                        'gameProperties'] and len(properties['data']['gameProperties']) > 0:
                        # 获取方法对象
                        monitor_print(f"---app_will_process_properties_source:{properties}")
                        monitor_print(
                            f"---app_will_process_properties_source_gameProperties:{properties['data']['gameProperties']}")
                        module_method = getattr(self.biz_module, func_name)
                        result_properties = module_method(properties['data']['gameProperties'], report_cdn_urls)
                        task_status, game_properties, append_oss_info = result_properties
                        monitor_print(f"---app_will_process_properties_result:{result_properties}")
                        if append_oss_info is not None:
                            oss_pathes, cdn_urls = append_oss_info
                            report_urls = oss_pathes + report_urls
                    else:
                        monitor_print(f"发布脚本：多子属性获取失败")
                        # app_will_process_properties(properties['data']['gameProperties'], urls)
            else:
                monitor_print(f"发布脚本：：函数 '{func_name}' 必须实现")

        sanmou_result = None
        if hasattr(self.biz_module, "app_will_process_sanmou_result"):
            sanmou_result = getattr(self.biz_module, "app_will_process_sanmou_result")()
        monitor_print(f"----8888:{report_urls}, {report_cdn_urls}, {report_seller_urls}, {report_seller_cdn_urls}")

        monitor_task_status_v2('成功结束', '串流上报结束状态6')
        request_workflow_task_status('成功结束', '串流上报结束状态6', 6)
        # for i in range(3):
        #     request_workflow_task_status('成功结束', '串流上报结束状态6', 6)
        #     sleep(0.5)

        # monitor_task_status(env,  '成功结束', '上报结束状态6', 6)

        monitor_print(f"----monitor_report_task_info_final:{task_status},{report_urls}, {report_seller_urls}")
        monitor_print(f"----monitor_report_task_info_inspect_properties: {seller_properties}")
        monitor_task_status_v2('成功结束', '任务中心上报结束状态6')

        monitor_report_task_info(env, task_status, imgs=report_urls, seller_imgs=report_seller_urls,
                                 inspect_properties=seller_properties, properties=game_properties,
                                 sanmou_result=sanmou_result)

        if partial_func:
            monitor_task_status_v2('before执行partial_func', 'before执行partial_func')
            partial_func()
            monitor_task_status_v2('after执行partial_func', 'after执行partial_func')

        monitor_task_status_v2(f'---process_upload_oss____end', '')

    def app_remove_script_end_task_file(self, task_id):
        home_path = os.path.expanduser("~")
        directory = os.path.join(home_path, ".adc")
        # 判断目录是否存在
        if os.path.exists(directory):
            print(f"目录 {directory} 已存在")
        else:
            # 创建目录
            os.makedirs(directory)
            print(f"目录 {directory} 创建成功")

        file_name = f"{str(task_id)}.lock"
        # 拼接文件路径
        filepath = os.path.join(directory, file_name)
        # 判断文件是否存在
        if os.path.exists(filepath):
            # 删除文件
            os.remove(filepath)
            print(f"文件 {filepath} 删除成功")
        else:
            print(f"文件 {filepath} 不存在 ")

    def process_except_result(self):
        env = AppEnv.get_instance()
        monitor_task_status(env, '异常结束', '')

    def mcp_start(self):
        env = AppEnv.get_instance()
        monitor_print(f"---mcp_start: {env.taskId} {env.gameDir} logPath: {env.logPath}")
        # self.biz_module.mcp_exe_action()
        # 初始化mq
        # mcp_mq = McpMessageQueue()

    def start_pre_flow(self):
        env = AppEnv.get_instance()
        if env.system_type == SystemType.IOS:
            self.init_mds()
            self.connect_mds()

        self.biz_module = self.import_game_module()
        print(f"application_init_end")

    def start(self):
        env = AppEnv.get_instance()
        launchType = env.launchType

        # 这里是mcp的执行流程
        if self.is_mcp_task():
            self.mcp_start()
            return


        global ext_info
        global error_desc

        monitor_print(f"---application_start: {env.taskId} {env.gameDir} logPath: {env.logPath}")

        if env.taskId == None or len(env.taskId) == 0:
            return

        if env.gameDir == None or len(env.gameDir) == 0:
            return
        if env.logPath == None or len(env.logPath) == 0:
            return

        result = AppRunResult()
        try:
            # 执行预处理
            self.start_pre_flow()

            # 执行脚本
            self.start_core_flow()
        except ExceptionStopApp as e:  # 需要中断app的执行
            error_traceback = traceback.format_exc()
            monitor_task_status(env, f"--whole_except_{str(e)}", f"{error_traceback}")
            result.updateInfo(AppActionType.STOP_APP, e, ext_info=e.ext_info)

            ext_info = result.get_ext_info()
            ext_info['desc'] = error_traceback
            ext_info['type'] = AppActionType.STOP_APP
            error_desc = error_traceback
        except Exception as e:
            error_traceback = traceback.format_exc()
            monitor_task_status(env, f"--whole_except_{str(e)}", f"{error_traceback}")
            # 其他未知错误要通过runloop重试
            ext_info = {'key': '120009'}
            result.updateInfo(AppActionType.STOP_APP, e, ext_info=ext_info)

            ext_info = result.get_ext_info()
            ext_info['desc'] = error_traceback
            ext_info['type'] = AppActionType.STOP_APP
            error_desc = error_traceback

            if self.is_ai_rebind_task():
                rebind_partial_func('120009')
        finally:
            monitor_task_status(env, '---app_start_finally', '')
            if env.system_type == SystemType.IOS and env.iOS_session_connect is not None:
                env.iOS_session_connect.release()
                monitor_task_status(env, '---ios设备释放_session_release', '')
                monitor_print(f"---ios设备释放_session_release")


        # 处理异常，上传oss及后续操作
        monitor_task_status(env, '---处理结果', '')
        if launchType != 'localtest' or ((self.is_fabu_task()) and env.localtest_need_upload == True) or self.is_ai_rebind_task():
            monitor_task_status(env, '---处理结果_enter', '')
            if ext_info != None:
                status = int(ext_info['key'])
                if status == 6:
                    # 这里之所以要单独基于break_app增加6的正常结束，是因为换绑的需求需要在stop_script中上报正常结束，并且需要上报换绑的时机保持跟reporttask一致
                    monitor_task_status(env, '---process_upload_oss', '')
                    monitor_print(f"---process_upload_oss")
                    self.process_upload_oss(env)
                    monitor_task_status(env, '成功结束', '')
                else:
                    monitor_task_status(env, '---process_ext_info', '')
                    monitor_print(f"---process_ext_info:{ext_info}")
                    self.process_ext_info(env, ext_info)
                    if status == 200:
                        monitor_task_status(env, '成功结束', '')
                    else:
                        monitor_task_status(env, '异常结束', '')
            else:
                monitor_task_status(env, '---process_upload_oss', '')
                monitor_print(f"---process_upload_oss")
                self.process_upload_oss(env)
                monitor_task_status(env, '成功结束', '')

        monitor_task_status(env, '---重置基本信息', '')
        ext_info = None
        error_desc = None

        self.app_remove_script_end_task_file(env.taskId)

        monitor_task_status(env, '---application_end', '')
        monitor_print(f"---application_end: {env.taskId} {env.gameDir} logPath: {env.logPath}")


# monitor_print("This is the main program.")
# main()
# monitor_print("End of the main program.")
