# -*- encoding=utf8 -*-


import argparse
import os
import sys
import time
from pathlib import Path
import subprocess
__author__ = "xiaohanzhu"

PYTHONPATH = str(Path(__file__).resolve().parent.parent)
os.environ.update(PYTHONPATH=PYTHONPATH)
sys.path.insert(0, PYTHONPATH)

from utility.base.adc_environment import *
from utility.base.adc_monitor import *

# ----------------确定机器类型------------------
def set_chip_type():
    try:
        # 执行 sysctl 命令获取机器硬件信息
        result = subprocess.run(['sysctl', 'machdep.cpu.brand_string'], capture_output=True, text=True)

        # 获取输出并解析
        chip_type = result.stdout.strip()
        monitor_print(f"chip_type:{chip_type}")

        dynamic_info = AppDynamicInfo.get_instance()
        chip_start_time = time.perf_counter()
        chip_end_time = time.perf_counter()
        monitor_print(f"---set_chip_type:{chip_end_time - chip_start_time}, {chip_type}")
        if 'M3' in chip_type or 'M4' in chip_type:
            dynamic_info.setIsM3Support(True)

    except Exception as e:
        monitor_print(f"---set_chip_type_error:{e}")

set_chip_type()


from utility.app.adc_application import *

if __name__ == '__main__':
    # 解析参数,注意这里一定要在Application初始化之前调用
    main_parse_args(system_type='android')
    app = Application()
    app.start()


# from airtest.core.api import *
#
# import time
# import json
# import threading
# # 日志级别
# import logging
# # 默认就是DEBUG
# logger = logging.getLogger("airtest")
# logger.setLevel(logging.INFO)
#
# import traceback
#
# using("./utility/monitor.air")
# from monitor import *
#
# using("./utility/api.air")
# from api import *
#
# import subprocess
#
# def get_chip_type():
#     try:
#         # 执行 sysctl 命令获取机器硬件信息
#         result = subprocess.run(['sysctl', 'machdep.cpu.brand_string'], capture_output=True, text=True)
#
#         # 获取输出并解析
#         chip_type = result.stdout.strip()
#         print(f"chip_type:{chip_type}")
#
#         return chip_type
#     except Exception as e:
#         return f"An error occurred: {e}"
#
# dynamic_info = AppDynamicInfo.get_instance()
# chip_start_time = time.perf_counter()
# chip_type = get_chip_type()
# chip_end_time = time.perf_counter()
# monitor_print(f"---get_chip_type:{chip_end_time-chip_start_time}, {chip_type}")
# if 'M3' in chip_type:
#     dynamic_info.setIsM3Support(True)
#
# # 这里优先统计脚本开始时间点
# AppPerformanceInfo.get_instance().setTimeDurationMap('captcha_time', duration_start=True)
#
# using("./utility/files.air")
# from files import *
#
# using("./utility/security.air")
# from security import *
#
# using("./utility/upload.air")
# from upload import *
#
# using("./utility/adc_request.air")
# from adc_request import *
#
# using("./utility/adc_tools.air")
# from adc_tools import *
#
# auto_setup(__file__)
#
# from airtest.core.settings import Settings as ST
#
#
# # ST.CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
# ST.CVSTRATEGY = ['mstpl', 'tpl']
# ST.SNAPSHOT_QUALITY = 99
# # 启动不同的阶段（内部使用）
# # 目前有 start ,upload
# # 本地调试命令：
# # airtest run ../main.air --device "Android:///localhost:9898" --log "/Users/xiaohanzhu/androidLogResult"
#
# launchType = 'localtest'
# # local参数只在本地运行时有用，这三个参数在localtest_config中也有定义，建议在config文件中定义，这样不影响其他的游戏
# # 在localtest下是否清理游戏
# localNeedClean = True
#
# # 在localtest下是否需要上传oss
# localNeedUpload = True
#
# # 在localtest下是否删除logPath日志
# localRemoveLog = True
#
# ### **********************入参解析********************** ###
#
# username = ""
# phone = ""
# smsCode = ""
# password = ""
# taskId = ""
# SCRIPT_ENV = ""
# taskType = TaskType.YANHAO.value
# mode = ""
# gameDir=''
# sleepTime=0.5
# oss_mode = ''
# oss_app_id = ''
# oss_app_secret = ''
# task_source = 0
# game_area = None
# task_contenttype=1
# transfer_account_info=''
# account_attr=''
# image_list_json=''
# game_properties_version=0
# common_properties_json=''
#
# oss_eagle_app_id = ''
# oss_eagle_app_secret = ''
#
# #下面的参数需要经过参数传入
# logPath=''
# scriptHome=''
# rootHome=''
# # 需要游戏的index实现的方法包括：
# # game_will_launch  告知游戏实现launch能力
# # game_did_launch   告知游戏launch完成后要实现的能力,返回phase数据
# # game_will_close
# # game_will_clean
# # app_will_process_exception_snapshot  内部不能执行任何操作game的代码
# # app_will_process_properties 用于业务处理oss_urls
# # app_did_get_properties  多子属性预拉取
#
#
#
# ext_info = None
# error_desc = None
#
#
# def main_parse_args():
#     global launchType
#     global phone
#     global smsCode
#     global username
#     global password
#     global taskId
#     global SCRIPT_ENV
#     global taskType
#     global mode
#     global gameDir
#     global logPath
#     global scriptHome
#     global rootHome
#
#     global oss_mode
#     global oss_app_id
#     global oss_app_secret
#     global sleepTime
#
#     global localNeedClean
#     global localNeedUpload
#     global localRemoveLog
#
#     global task_source
#     global game_area
#     global task_contenttype
#     global transfer_account_info
#     global account_attr
#     global image_list_json
#     global game_properties_version
#     global common_properties_json
#
#     global oss_eagle_app_id
#     global oss_eagle_app_secret
#
#     monitor_print('parsed args start')
#     envLaunch = os.getenv('launchType')
#     if envLaunch is not None:
#         launchType = envLaunch
#
#     if launchType != 'localtest':
#         monitor_print("-----parsed args:")
#         parser = argparse.ArgumentParser(description="Just an example",
#                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#         parser.add_argument("run", action="store")
#         parser.add_argument("script_home", action="store")
#         parser.add_argument("--log", action="store")
#         parser.add_argument("--device", action="store")
#
#         args = vars(parser.parse_args())
#         logPath =args['log']
#
#         username = os.getenv('name')
#         phone = os.getenv('phone')
#         decrypt_key = os.getenv('SECRTET_DECRYPT_PASSWORD')
#
#         secret_smsCode = os.getenv('smsCode')
#         monitor_print(f"secret_smsCode:{secret_smsCode}")
#         smsCode = ''
#         if secret_smsCode and len(secret_smsCode) > 0 and decrypt_key and len(decrypt_key)>0:
#             smsCode = decrypt(secret_smsCode, decrypt_key)
#
#
#         secret_password = os.getenv('password')
#         monitor_print(f"secret_password:{secret_password}")
#         password = ''
#         if secret_password and len(secret_password)>0 and decrypt_key and len(decrypt_key)>0:
#             password = decrypt(secret_password, decrypt_key)
#
#         taskId = os.getenv('taskId')
#         SCRIPT_ENV = os.getenv('SCRIPT_ENV')
#         taskType = os.getenv('taskType')
#         # scriptHome = os.getenv('SCRIPT_HOME')
#         mode = os.getenv('actionType')
#         gameDir = os.getenv('zipFileName')
#         # sleepTime = os.getenv('sleepTime')
#
#         oss_mode = os.getenv('OSS_MODE')
#         oss_app_id = os.getenv('OSS_APP_ID')
#         oss_app_secret = os.getenv('OSS_APP_SECRET')
#
#         oss_eagle_app_id = os.getenv('OSS_EAGLE_APP_ID')
#         oss_eagle_app_secret = os.getenv('OSS_EAGLE_APP_SECRET')
#
#         task_source = os.getenv('taskSource')
#         if task_source is None or not task_source.isdigit():
#             task_source = '0'
#
#         game_properties_version_str = os.getenv('gamePropertiesVersion')
#         if game_properties_version_str is None or len(game_properties_version_str) == 0:
#             game_properties_version = 0
#         else:
#             game_properties_version = int(game_properties_version_str)
#
#         temp_game_area = os.getenv('gameArea')
#         if temp_game_area == 'null':
#             game_area = None
#         else:
#             game_area = temp_game_area
#
#         task_contenttype = os.getenv('taskContentType')
#         if task_contenttype is None or not task_contenttype.isdigit():
#             task_contenttype = 1
#
#         # transfer_account_info = os.getenv('transferAccountInfo')
#
#         temp_transfer_account_info = os.getenv('transferAccountInfo')
#         if temp_transfer_account_info == 'null':
#             transfer_account_info = None
#         else:
#             transfer_account_info = temp_transfer_account_info
#
#
#         temp_account_attr = os.getenv('accountAttr')
#         if temp_account_attr == 'null':
#             account_attr = None
#         else:
#             account_attr = temp_account_attr
#         # account_attr = os.getenv('accountAttr')
#
#         # image_list_json = os.getenv('imageListJson')
#
#         temp_image_list_json = os.getenv('imageListJson')
#         if temp_image_list_json == 'null':
#             image_list_json = None
#         else:
#             image_list_json = temp_image_list_json
#
#         common_properties_json = os.getenv('commonPropertiesJson')
#     else:
#         monitor_print("-----parsed localtest args:")
#         parser = argparse.ArgumentParser(description="Just an example",
#                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#         parser.add_argument("run", action="store")
#         parser.add_argument("script_home", action="store")
#         parser.add_argument("--log", action="store")
#         parser.add_argument("--device", action="store")
#
#         args = vars(parser.parse_args())
#         logPath =args['log']
#
#         home_dir = os.path.expanduser("~")
#         configPath = home_dir + '/.adc/localtest_config.json'
#         if os.path.exists(configPath) and os.path.isfile(configPath):
#             with open(f"{configPath}", 'r') as file:
#                 content = file.read()
#                 if content == None or len(content) == 0:
#                     monitor_print(f"***本地测试配置文件不能为空")
#                     exit()
#         else:
#             monitor_print(f"***没有找到本地测试配置文件: {configPath}")
#             exit()
#
#         # 解析 JSON 内容
#         data = json.loads(content)
#
#         monitor_print(f"localtest_file:{data}")
#
#         username = data['username']
#         phone = data['phone']
#         smsCode = data['smsCode']
#         password = data['password']
#         taskId = data['taskId']
#         SCRIPT_ENV = data['SCRIPT_ENV']
#         taskType = data['taskType']
#         mode = data['mode']
#         gameDir = data['gameDir']
#         sleepTime = data['sleepTime']
#         oss_mode = data['oss_mode']
#         oss_app_id = data['oss_app_id']
#         oss_app_secret = data['oss_app_secret']
#
#         oss_eagle_app_id = data.get('OSS_EAGLE_APP_ID')
#         oss_eagle_app_secret = data.get('OSS_EAGLE_APP_SECRET')
#
#         task_source = data.get('taskSource')
#         game_area = data.get('gameArea')
#         task_contenttype_str = data.get('taskContentType')
#         transfer_account_info = data.get('transferAccountInfo')
#         account_attr = data.get('accountAttr')
#         if task_contenttype_str is None:
#             task_contenttype = 1
#         else:
#             task_contenttype = int(task_contenttype_str)
#
#         if transfer_account_info is None:
#             transfer_account_info = ''
#
#         if account_attr is None:
#             account_attr = ''
#
#         if task_source is None:
#             task_source = '0'
#
#         image_list_json = data.get('imageListJson')
#
#         game_properties_version = data.get('gamePropertiesVersion')
#         if game_properties_version is None:
#             game_properties_version = 0
#
#         temp_need_clean = data.get('local_need_clean')
#         if temp_need_clean is not None:
#             if int(temp_need_clean) == 1:
#                 localNeedClean = True
#             else:
#                 localNeedClean = False
#
#
#         temp_need_upload = data.get('local_need_upload')
#         if temp_need_upload is not None:
#             if int(temp_need_upload) == 1:
#                 localNeedUpload = True
#             else:
#                 localNeedUpload = False
#
#         temp_remove_log = data.get('local_remove_log')
#         if temp_remove_log is not None:
#             if int(temp_remove_log) == 1:
#                 localRemoveLog = True
#             else:
#                 localRemoveLog = False
#
#         common_properties_json = data.get('commonPropertiesJson')
#
#         monitor_print(f"localNeedClean:{localNeedClean}")
#         monitor_print(f"localNeedUpload:{localNeedUpload}")
#         monitor_print(f"localRemoveLog:{localRemoveLog}")
#
#     # 获取当前文件的路径
#     current_path = os.path.dirname(os.path.abspath(__file__))
#     dir_path = os.path.dirname(current_path)
#     scriptHome = dir_path + '/' + gameDir
#
#     rootHome = dir_path
#
#     monitor_print("-----parsed args end")
#
#
# # 解析参数
# main_parse_args()
#
# ### **********************设置环境变量********************** ###
# # 设置环境变量
# env = AppEnv.get_instance()
# env.setEnv(launchType, phone, smsCode, username, password, taskId, SCRIPT_ENV, mode, logPath, gameDir,scriptHome, rootHome, oss_mode, oss_app_id, oss_app_secret, sleepTime, taskType=int(taskType), taskSource=int(task_source),game_area=game_area,task_contenttype=int(task_contenttype),transfer_account_info=transfer_account_info, account_attr=account_attr, game_properties_version = int(game_properties_version), image_list_json = image_list_json, common_properties_json = common_properties_json, oss_eagle_app_id=oss_eagle_app_id, oss_eagle_app_secret=oss_eagle_app_secret, device= device())
#
# def print_env_args():
#     env = AppEnv.get_instance()
#     monitor_print(f"脚本环境数据>>>>>>>>>>>>", level=PRINT_LEVEL.INFO)
#     monitor_print(f"launchType:{env.launchType}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"phone:{env.phone}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"smsCode:{env.smsCode}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"username:{env.username}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"password:{env.password}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"taskId:{env.taskId}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"sleepTime:{env.sleepTime}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"taskStatus:{env.taskStatus}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"SCRIPT_ENV:{env.scriptEnv}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"logPath:{env.logPath}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"game_name:{env.game_name}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"scriptHome:{env.scriptHome}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"taskType:{env.taskType}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"rootHome:{env.rootHome}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"mode:{env.mode}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"oss_mode:{env.oss_mode}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"oss_app_id:{env.oss_app_id}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"oss_app_secret:{env.oss_app_secret}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"device:{env.device}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"taskSource:{env.taskSource}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"game_area:{env.game_area}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"task_contenttype:{env.task_contenttype}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"transfer_account_info:{env.transfer_account_info}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"account_attr:{env.account_attr}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"image_list_json:{env.image_list_json}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"game_properties_version:{env.game_properties_version}", level=PRINT_LEVEL.INFO)
#     monitor_print(f"common_properties_json:{env.common_properties_json}", level=PRINT_LEVEL.INFO)
#     monitor_task_status_v2(f"---env_args", f'launchType:{env.launchType}, phone:{env.phone}, smsCode:{env.smsCode}, username:{env.username}, taskId:{env.taskId}, sleepTime:{env.sleepTime}, taskStatus:{env.taskStatus}, SCRIPT_ENV:{env.scriptEnv}, logPath:{env.logPath}, game_name:{env.game_name}, scriptHome:{env.scriptHome}, taskType:{env.taskType}, rootHome:{env.rootHome}, mode:{env.mode}, oss_mode:{env.oss_mode}, device:{env.device}, taskSource:{env.taskSource}, game_area:{env.game_area}, task_contenttype:{env.task_contenttype}, transfer_account_info:{env.transfer_account_info}, account_attr:{env.account_attr}, image_list_json:{env.image_list_json}, game_properties_version:{env.game_properties_version}, common_properties_json:{env.common_properties_json}')
#     monitor_print(f"<<<<<<<<<<<<脚本环境数据", level=PRINT_LEVEL.INFO)
#
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
# monitor_task_status(env,f"执行账户 {username}",'')
#
# using("./utility/application.air")
# from application import *
#
# using("./utility/upload.air")
# from upload import upload_oss, upload_jym_oss
#
# # 打印环境参数
# print_env_args()
#
#
# ### **********************任务类型区分********************** ###
# def is_fabu_task():
#     env = AppEnv.get_instance()
#     is_fabu = env.taskType == TaskType.FABU.value or env.taskType == TaskType.PC_FABU_OCR.value or env.taskType == TaskType.CAPTCHA_TASK.value
#     monitor_print(f"---is_fabu_task:{is_fabu}")
#     return is_fabu
#
# # 这个接口用于确定是脚本自己登录，还是外部登录（手机号发布）, 托管发布不做处理是因为网易系的游戏重启登录态还在，可以尝试解决踢登问题
# def is_outer_login_task():
#     env = AppEnv.get_instance()
#     is_outer_fabu = (env.taskType == TaskType.CAPTCHA_TASK.value)
#     monitor_print(f"---is_outer_fabu:{is_outer_fabu}")
#     return is_outer_fabu
#
# # 处理不同类型下的订单，是否需要脚本执行前的清理
# def before_start_clean():
#     global biz_module
#     env = AppEnv.get_instance()
#     # 这里的tuoguan是针对common脚本的处理，保证不会clean
#     if env.taskSource == TaskSource.TUOGUAN.value or mode == 'submit_ext_info' or env.taskType == TaskType.CAPTCHA_TASK.value:
#         # 这些case不需要脚本执行前的清理
#         monitor_print(f"---before_start_clean_no_need")
#     else:
#         monitor_print(f"---before_start_clean")
#         if launchType == 'localtest':
#             if localNeedClean:
#                 try:
#                     main_clean_game(-1, desc='from_start')
#                 except Exception:
#                     ...
#         else:
#             try:
#                 main_clean_game(-1, desc='from_start')
#             except Exception:
#                 ...
#
# def is_clean_game_task():
#     env = AppEnv.get_instance()
#     is_clean_game = env.taskType == TaskType.CLEAN_GAME_TASK.value
#     return is_clean_game
#
# def is_update_qufu_task():
#     env = AppEnv.get_instance()
#     is_update_qufu = env.taskType == TaskType.UPDATE_QUFU_TASK.value
#     return is_update_qufu
#
# def is_gonglue_game_task():
#     env = AppEnv.get_instance()
#     is_gonglue_game = env.taskType == TaskType.GAME_GONGLUE_TASK.value
#     return is_gonglue_game
#
# def is_eagle_down_task():
#     env = AppEnv.get_instance()
#     is_eagle_down_task = env.taskType == TaskType.EAGLE_DOWN_TASK.value
#     return is_eagle_down_task
#
# def is_eagle_query_task():
#     env = AppEnv.get_instance()
#     is_eagle_query_task = env.taskType == TaskType.EAGLE_QUERY_TASK.value
#     return is_eagle_query_task
#
# ### **********************不同任务对应的脚本依赖********************** ###
# # 根据发布和验号，引用不同的脚本
# # 根据发布和验号，引用不同的脚本
# biz_module = None
# if is_fabu_task():
#     air_name = f"{gameDir}_fabu.air"
#     biz_module= lx_import(air_name)
#
#     monitor_task_status(env,f"执行发布脚本",'')
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
#     monitor_task_status(env,f"执行验号脚本",f'{air_name}')
#     # game_will_launch, game_did_launch, game_will_close,game_will_clean,app_will_process_exception_snapshot,app_will_process_properties
#
# # def test_game_properties():
# #     # 代码
# #     properties = get_game_proerties_by_task()
# #     with open('output.txt', 'w') as file:
# #         # 写入文件
# #         file.write(json.dumps(properties) + '\n')
# #         # 打印到控制台
# #         # print(text_to_write)
# # test_game_properties()
#
# def set_login_status():
#     env = AppEnv.get_instance()
#     if env.taskSource == TaskSource.TUOGUAN.value:
#         AppDynamicInfo.get_instance().setHasLogin(True)
#
# # 获取attr方法
# def get_module_attr_method(cur_module, func_name):
#     if hasattr(cur_module, func_name):
#         module_method = getattr(cur_module, func_name)
#         return module_method
#     return None
#
# ### **********************多子属性预拉取********************** ###
# # def app_did_get_properties(properties):
# def process_all_sub_properties(callback_func_name):
#     monitor_print(f"---开始处理预拉取多子属性：{callback_func_name}")
#     need_laqu_game_properties = False
#
#     need_duozi_func = 'app_need_game_properties'
#     # 判断模块中是否实现了指定方法
#     if hasattr(biz_module, need_duozi_func):
#         module_method = getattr(biz_module, need_duozi_func)
#         need_game_properties = module_method()
#         if need_game_properties:
#             need_laqu_game_properties = True
#
#     if need_laqu_game_properties == False:
#         if is_fabu_task() == False:
#             need_laqu_game_properties = False
#         else:
#             need_laqu_game_properties = True
#
#     if need_laqu_game_properties == False:
#         monitor_print(f"---预拉取多子属性：{need_laqu_game_properties}")
#         return
#
#     monitor_print(f"---预拉取多子属性：{need_laqu_game_properties}")
#     func_name = callback_func_name
#     # 判断模块中是否实现了指定方法
#     if hasattr(biz_module, func_name):
#         # if func_name in globals():
#         # 函数存在，可以安全地调用它
#         properties = get_game_proerties_by_task()
#         # if launchType == 'localtest':
#         #     properties = get_game_proerties_by_task('729')
#
#         if properties and len(properties) > 0 and properties['data'] and properties['data'][
#             'gameProperties'] and len(properties['data']['gameProperties']) > 0:
#             monitor_print(f"---预拉取多子属性数据：{properties['data']['gameProperties']}")
#
#             module_method = getattr(biz_module, func_name)
#             module_method(properties['data']['gameProperties'])
#         else:
#             monitor_print(f"发布脚本：多子属性获取失败")
#     else:
#         monitor_print(f"---未实现多子属性获取方法：{callback_func_name}")
#
#
# ### **********************脚本loop设置********************** ###
# # 这里是从脚本获取执行的runloop数
# def get_runloop_count():
#     loop = 2
#     env = AppEnv.get_instance()
#
#     func_name = 'app_will_get_runloop_count'
#     if hasattr(biz_module, func_name):
#         runloop_count_method = getattr(biz_module, func_name)
#         loop_count = runloop_count_method()
#         loop = loop_count
#         monitor_print(f"----app_will_get_runloop_count:{loop_count}")
#     else:
#         if env.taskSource == TaskSource.TUOGUAN.value:
#             loop = 3
#         elif env.taskType == TaskType.CAPTCHA_TASK.value and env.get_common_property_with_key('captchaTaskStatus') != None and int(env.get_common_property_with_key('captchaTaskStatus')) < 3:
#             loop = 1
#         elif env.taskType == TaskType.CLEAN_GAME_TASK.value:
#             loop = 1
#
#     if launchType == 'localtest':
#         loop = 3
#
#     return loop
#
# # 将当前的loop发给游戏
# def send_runloop_count(index):
#     func_name = 'app_will_send_runloop_count'
#     if hasattr(biz_module, func_name):
#         runloop_count_method = getattr(biz_module, func_name)
#         runloop_count_method(index)
#
#
# ### **********************主流程核心处理接口********************** ###
#
# def main_clean_game(index, desc=None):
#     global biz_module
#     env = AppEnv.get_instance()
#
#     if desc is None:
#         monitor_print(f"---main_clean_game: index:{index}")
#         monitor_task_status_v2(f"---main_clean_game: index:{index}", '')
#     else:
#         monitor_print(f"---main_clean_game_{desc}: index:{index}")
#         monitor_task_status_v2(f"---main_clean_game_{desc}: index:{index}", '')
#
#     try:
#         biz_module.game_will_clean(env)
#     except Exception:...
#
#     AppDynamicInfo.get_instance().setHasLogin(False)
#
# def main_close_game(index, desc=None):
#     global biz_module
#     env = AppEnv.get_instance()
#     if desc is None:
#         monitor_print(f"---main_close_game: index:{index}")
#         monitor_task_status_v2(f"---main_close_game: index:{index}", '')
#     else:
#         monitor_print(f"---main_close_game_{desc}: index:{index}")
#         monitor_task_status_v2(f"---main_close_game_{desc}: index:{index}", '')
#     # if index == 0 and env.taskType == TaskType.CAPTCHA_TASK.value and env.get_common_property_with_key('captchaTaskStatus') != None and int(env.get_common_property_with_key('captchaTaskStatus')) == 1:
#     #     AppDynamicInfo.get_instance().setEnterCaptcha(True)
#     biz_module.game_will_close(env)
#
# def start_game_thread():
#     global biz_module
#     env = AppEnv.get_instance()
#     if hasattr(biz_module, "game_thread_task"):
#         monitor_print(f"---start_game_thread")
#         monitor_task_status(env, "子线程启动", '')
#         t = threading.Thread(target=biz_module.game_thread_task, args=(env,))
#         t.setDaemon(True)
#         t.start()
#
# def report_performance_log():
#     per_info = AppPerformanceInfo.get_instance().getTimeDurationMap()
#     monitor_print(f"---report_performance_log: {per_info}")
#     monitor_task_flow_status_info(1010, per_info)
#
# def need_clean_and_close_game_before_run(index):
#     monitor_task_status_v2(f'---need_clean_and_close_game_before_run____start', '')
#     global biz_module
#     env = AppEnv.get_instance()
#     global launchType
#
#     # 这两个参数的控制不影响本地执行逻辑
#     need_clean_game = True
#     need_close_game = True
#     # if need_close_game:
#     #     pass
#
#     if index == 0 and env.mode == 'submit_ext_info':
#         monitor_print('submit_ext_info任务不需要清理游戏，开始执行')
#         monitor_task_status_v2(f'submit_ext_info任务不需要清理游戏，开始执行', '')
#         need_clean_game = False
#         need_close_game = False
#
#     elif index == 0 and (env.taskType == TaskType.CAPTCHA_TASK.value or env.taskType == TaskType.CLEAN_GAME_TASK.value):
#         # 手机号验证码的captchaTaskStatus存在并且不为1的情况下，不清理游戏
#         need_clean_game = False
#         need_close_game = False
#         monitor_print(f"---任务不需要clean和close: index:{index}, tasktype:{env.taskType}")
#         monitor_task_status_v2(f"---任务不需要clean和close: index: index:{index}, tasktype:{env.taskType}", '')
#     else:
#         if AppDynamicInfo.get_instance().getHoldGame() == True:
#             need_close_game = False
#             need_clean_game = False
#             monitor_print(f"---任务HoldGame_true: index:{index}, tasktype:{env.taskType}")
#             monitor_task_status_v2(f"---任务HoldGame_true: index:{index}, tasktype:{env.taskType}", '')
#         else:
#             if AppDynamicInfo.get_instance().getHasLogin() == True:
#                 monitor_print(f"---任务HoldGame_false_login_true: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(f"---任务HoldGame_false_login_true: index:{index}, tasktype:{env.taskType}", '')
#                 need_close_game = True
#                 need_clean_game = False
#             else:
#                 monitor_print(f"---任务HoldGame_false_login_false: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(f"---任务HoldGame_false_login_false: index:{index}, tasktype:{env.taskType}", '')
#                 need_close_game = True
#                 need_clean_game = True
#
#
#     monitor_print(f'---need_clean_and_close_game_before_run_final_check: need_clean_game: {need_clean_game}, need_close_game:{need_close_game}')
#     monitor_task_status_v2(f'---need_clean_and_close_game_before_run_final_check: need_clean_game:{need_clean_game}, need_close_game:{need_close_game}', '')
#
#     if need_close_game == True:
#         if launchType == 'localtest':
#             if localNeedClean:
#                 main_close_game(index, desc='before_run')
#                 monitor_print(f"---need_clean_and_close_game_before_run_need_close_game_local: index:{index}")
#                 monitor_task_status_v2(f"---need_clean_and_close_game_before_run_need_close_game_local: index:{index}", '')
#         else:
#             main_close_game(index, desc='before_run')
#             monitor_print(f"---need_clean_and_close_game_before_run_need_close_game: index:{index}")
#             monitor_task_status_v2(f"---need_clean_and_close_game_before_run_need_close_game: index:{index}", '')
#
#     # 这里无论是否close，都要启动下应用，保证应用启动，并且在前台
#     # if check_phone_captcha() == False:
#     #     monitor_print(f"---check_phone_captcha_no_launch: index:{index}, tasktype:{env.taskType}")
#     #     monitor_task_status_v2(f"---check_phone_captcha_no_launch: index:{index}, tasktype:{env.taskType}", '')
#     #     biz_module.game_will_launch(env)
#     # else:
#     #     monitor_print(f"---check_phone_captcha_launch: index:{index}, tasktype:{env.taskType}")
#     #     monitor_task_status_v2(f"---check_phone_captcha_launch: index:{index}, tasktype:{env.taskType}", '')
#
#     if need_clean_game == True:
#         if launchType == 'localtest':
#             if localNeedClean:
#                 main_clean_game(index, desc='before_run')
#         else:
#             main_clean_game(index, desc='before_run')
#             monitor_print(f"---need_clean_and_close_game_before_run_need_clean_game: index:{index}, tasktype:{env.taskType}")
#             monitor_task_status_v2(f"---need_clean_and_close_game_before_run_need_clean_game: index:{index}, tasktype:{env.taskType}", '')
#
#     # 这里的启动要等到clean后才能再启动，并且启动要根据need_close_game参数来决定
#     if need_close_game == True:
#         if launchType == 'localtest':
#             if localNeedClean:
#                 monitor_print(f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}", '')
#                 biz_module.game_will_launch(env)
#         else:
#             monitor_print(f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}")
#             monitor_task_status_v2(f"---need_clean_and_close_game_before_run_will_launch: index:{index}, tasktype:{env.taskType}", '')
#             biz_module.game_will_launch(env)
#
#     monitor_task_status_v2(f'---need_clean_and_close_game_before_run____end', '')
#
# def check_phone_captcha():
#     env = AppEnv.get_instance()
#     phone_captch = False
#     if env.taskType == TaskType.CAPTCHA_TASK.value or env.taskType == TaskType.CLEAN_GAME_TASK.value:
#         phone_captch = True
#     return phone_captch
#
# def need_clean_and_close_game_after_run(index, suc=False, result=None):
#     monitor_task_status_v2(f'---need_clean_and_close_game_after_run____start', '')
#     global biz_module
#     env = AppEnv.get_instance()
#     global launchType
#
#     # 这两个参数的控制不影响本地执行逻辑,脚本执行结束的处理默认是false
#     need_clean_game = False
#     need_close_game = False
#
#     if suc == False:
#         monitor_print(f"---need_clean_and_close_game_after_run_suc_false: index:{index}")
#         monitor_task_status_v2(f"---need_clean_and_close_game_after_run_suc_false: index:{index}", '')
#         action_type = result.getActionType()
#         if action_type == AppActionType.STOP_APP:
#             if AppDynamicInfo.get_instance().getHoldGame() == True:
#                 monitor_print(f"---need_clean_and_close_game_after_run_stop_app_hold_game: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(f"---need_clean_and_close_game_after_run_stop_app_hold_game: index:{index}, tasktype:{env.taskType}", '')
#                 need_clean_game = False
#                 need_close_game = False
#             else:
#                 monitor_print(f"---need_clean_and_close_game_after_run_stop_app_no_hold_game: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(
#                     f"---need_clean_and_close_game_after_run_stop_app_no_hold_game: index:{index}, tasktype:{env.taskType}", '')
#                 need_clean_game = True
#                 need_close_game = True
#         elif action_type == AppActionType.STOP_RUNLOOP:
#             if index == get_runloop_count() - 1:
#                 monitor_print(f"---need_clean_and_close_game_after_run_stop_runloop_last_loop: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(
#                     f"---need_clean_and_close_game_after_run_stop_runloop_last_loop: index:{index}, tasktype:{env.taskType}", '')
#                 need_clean_game = True
#                 need_close_game = True
#             else:
#                 if AppDynamicInfo.get_instance().getHasLogin() == True:
#                     monitor_print(
#                         f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_has_login: index:{index}, tasktype:{env.taskType}")
#                     monitor_task_status_v2(
#                         f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_has_login: index:{index}, tasktype:{env.taskType}", '')
#                     need_clean_game = False
#                     need_close_game = True
#                 else:
#                     monitor_print(
#                         f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_not_has_login: index:{index}, tasktype:{env.taskType}")
#                     monitor_task_status_v2(
#                         f"---need_clean_and_close_game_after_run_stop_runloop_not_last_loop_not_has_login: index:{index}, tasktype:{env.taskType}",
#                         '')
#                     need_clean_game = True
#                     need_close_game = True
#         else:
#             need_clean_game = True
#             need_close_game = True
#     else:
#         monitor_print(
#             f"---need_clean_and_close_game_after_run_suc: index:{index}, tasktype:{env.taskType}")
#         monitor_task_status_v2(
#             f"---need_clean_and_close_game_after_run_suc: index:{index}, tasktype:{env.taskType}",
#             '')
#         need_clean_game = True
#         need_close_game = True
#
#     if check_phone_captcha() == False:
#         if need_close_game:
#             if launchType == 'localtest':
#                 if localNeedClean:
#                     main_close_game(index, desc='after_run')
#             else:
#                 main_close_game(index, desc='after_run')
#                 monitor_print(
#                     f"---check_phone_captcha_after_run_close_game: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(
#                     f"---check_phone_captcha_after_run_close_game: index:{index}, tasktype:{env.taskType}",
#                     '')
#
#         if need_clean_game:
#             if launchType == 'localtest':
#                 if localNeedClean:
#                     main_clean_game(index, desc='after_run')
#             else:
#                 main_clean_game(index, desc='after_run')
#                 monitor_print(
#                     f"---check_phone_captcha_after_run_clean_game: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(
#                     f"---check_phone_captcha_after_run_clean_game: index:{index}, tasktype:{env.taskType}",
#                     '')
#     else:
#         if need_clean_game:
#             if launchType == 'localtest':
#                 if localNeedClean:
#                     main_clean_game(index, desc='after_run')
#             else:
#                 main_clean_game(index, desc='after_run')
#                 monitor_print(
#                     f"---normal_after_run_clean_game: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(
#                     f"---normal_after_run_clean_game: index:{index}, tasktype:{env.taskType}",
#                     '')
#
#
#         if need_close_game:
#             if launchType == 'localtest':
#                 if localNeedClean:
#                     main_close_game(index, desc='after_run')
#             else:
#                 main_close_game(index, desc='after_run')
#                 monitor_print(
#                     f"---normal_after_run_close_game: index:{index}, tasktype:{env.taskType}")
#                 monitor_task_status_v2(
#                     f"---normal_after_run_close_game: index:{index}, tasktype:{env.taskType}",
#                     '')
#
#         monitor_task_status_v2(f'---need_clean_and_close_game_after_run____end', '')
#
#         # 结束后上报性能日志
#         report_performance_log()
#
# def files_clean_and_adjust(index):
#     global localRemoveLog
#
#     env = AppEnv.get_instance()
#
#     if is_directory_exists(env.logPath):
#         if env.launchType != 'localtest' or localRemoveLog == True:
#             delete_files_with_format(env, index, env.logPath, '*.jpg', 'adc_exception_')
#
#         if index > 0:  # 第二次及以后的重试修改为log_{index}.tst文件，最后一次的log是log.txt
#             rename_file_with_format(env, index, env.logPath, '*.txt')
#
# def process_exception_after_change_result(index, result):
#     error_task_status = get_task_status_last_errorcode()
#     monitor_print(f"---process_exception_after_change_result_start:{result.getActionType()}, {result.get_ext_info()}, {error_task_status}")
#     if error_task_status is None:
#         return result
#
#     # 如果是账号被踢，同时是手机号发布，则需要调整异常
#     if error_task_status == 10010 and is_outer_login_task():
#         monitor_print(f"---process_exception_after_change_result_before:{result.getActionType()}, {result.get_ext_info()}")
#         new_result = AppRunResult()
#         new_ext_info = {'key': str(error_task_status)}
#         new_result.updateInfo(AppActionType.STOP_APP, Exception("process_exception后的异常调整"), ext_info=new_ext_info)
#         monitor_task_status_v2(f'---process_exception_after_change_result_change', 'process_exception后的异常调整')
#         monitor_print(
#             f"---process_exception_after_change_result_after:{new_result.getActionType()}, {new_result.get_ext_info()}")
#         return new_result
#
#     return result
#
# ### **********************脚本正式启动********************** ###
# # 脚本正式启动
# def start(env):
#     monitor_task_status_v2(f'---main_run____start', '')
#
#     start_time = time.perf_counter()
#     global gameDir
#     global ext_info
#     global error_desc
#
#     global launchType
#
#     global localNeedClean
#
#     global biz_module
#
#     app = Application()
#
#     # 处理不同类型下的订单，是否需要先清理登录态
#     before_start_clean()
#
#     # 根据入参设置登录状态
#     set_login_status()
#
#     # 预先获取多子属性
#     process_all_sub_properties('app_did_get_properties')
#
#     # 启动子线程
#     start_game_thread()
#
#     loop = get_runloop_count()
#
#     index = 0
#     sucessFinish = False
#     for index in range(0, loop):
#
#         send_runloop_count(index)
#
#         monitor_task_status(env, f"脚本重试loop - {index}",'')
#
#         files_clean_and_adjust(index)
#
#         need_clean_and_close_game_before_run(index)
#
#         phaseList = biz_module.game_did_launch(env)
#
#         app.setPhaseList(phaseList)
#         monitor_task_status(env, f"{gameDir} 游戏脚本运行开始", '')
#         result = app.run(env)
#         monitor_task_status(env, f"{gameDir} 游戏脚本运行结束", '')
#
#         errorInfo = result.exceptionInfo()
#
#         # 无论是否有异常，都正常上传adc_catch图片，在子线程中执行上传
#         upload_adc_catch_images(index)
#
#         # 这里的errorInfo可能是错误，也可能是正常的业务流程的结束（比如手机号验证码登录）
#         if errorInfo:
#             try:
#                 result = report_exception_info(env, result, index)
#             except Exception as e:
#                 error_traceback = traceback.format_exc()
#                 monitor_task_status(env, '脚本app_will_process_exception_snapshot方法抛出异常', f"{error_traceback}", 10104)
#                 ext_info={'key':'120008', 'desc': "脚本app_will_process_exception_snapshot方法抛出异常", 'type': AppActionType.STOP_APP}
#                 break
#
#             monitor_print(f"---adc_start:{result.getActionType()}")
#
#             need_clean_and_close_game_after_run(index, False, result)
#
#             monitor_print(f"---adc_change_result:{result.getActionType()}, {result.get_ext_info()}")
#
#             if result.getActionType() == AppActionType.STOP_RUNLOOP:
#                 if index == loop - 1:
#                    ext_info={'key':'120000', 'desc': '两次重试出错', 'type': AppActionType.STOP_RUNLOOP}
#                    error_desc = '两次重试出错'
#                 monitor_print(f"---adc_start_stop_runloop:{result.getActionType()}, {result.get_ext_info()} ")
#                 continue
#             elif result.getActionType() == AppActionType.STOP_APP:
#                 # 这里如果是传递了错误码，则按错误码处理统一为120006
#                 ext_info=result.get_ext_info()
#                 if isinstance(errorInfo, PhaseException):
#                     error_desc = get_exception_desc(errorInfo)
#                 else:
#                     error_desc = str(errorInfo)
#                 ext_info['desc'] = error_desc
#                 ext_info['type'] = AppActionType.STOP_APP
#
#                 monitor_print(f"---adc_start_stop_app:{result.getActionType()}, {result.get_ext_info()}")
#                 break
#         else:
#             sucessFinish = True
#
#             need_clean_and_close_game_after_run(index, True)
#
#             monitor_task_status(env,f"{gameDir} 游戏脚本main start运行结束",'')
#             break
#
#     if index >= loop-1 and sucessFinish == False:
#         # todo - 给游戏接口确定是否要在最终结束后，重启游戏
#         need_launch = True
#         cur_method = get_module_attr_method(biz_module, 'game_need_launch_last')
#         if cur_method:
#             need_launch = cur_method()
#         if need_launch:
#             biz_module.game_will_launch(env)
#
#     end_time = time.perf_counter()
#     monitor_print(f"---纯脚本耗时:{end_time - start_time}")
#
#     monitor_task_status_v2(f'---main_run____end', '')
#
# ### **********************异常状态的处理********************** ###
# def upload_adc_catch_images(index):
#     monitor_task_status_v2(f'---upload_adc_catch_images____start', '')
#
#     start_time = time.perf_counter()
#     global localNeedUpload
#     global launchType
#
#     if launchType == 'localtest' and localNeedUpload == False:
#         return
#
#     files = get_sorted_files_with_prefix(ST.LOG_DIR, 'adc_catch')
#     if files is not None and len(files) > 0:
#         _, cdn_urls = upload_jym_oss_with_pathes(files)
#         if cdn_urls is not None and len(cdn_urls) > 0:
#             # 这里的第二个参数不能动，因为要用于神之领域
#             monitor_post_task_status(f'---上传自定义图片', f"{cdn_urls}")
#             # monitor_task_status_v2(f'上传自定义图片', f"{cdn_urls}")
#         else:
#             monitor_post_task_status(f'---上传空自定义图片', f"{cdn_urls}")
#     end_time = time.perf_counter()
#     monitor_print(f"---上传自定义图片耗时s:{end_time - start_time}")
#
#     monitor_task_status_v2(f'---upload_adc_catch_images____end', '')
#
#
# def report_exception_info(env, result, index):
#     if launchType == 'localtest' and localNeedUpload == False:
#         return
#
#     performance_start_timestamp = int(time.time() * 1000000)
#     except_type = result.getActionType()
#
#     monitor_task_status_v2(f'---report_exception_info____start', '')
#
#     monitor_print(f"---process_except:except_type:{except_type}, index:{index}")
#     file_prefix = 'adc_exception'
#     if except_type == AppActionType.STOP_APP:
#         file_prefix = 'adc_exception_stop_app'
#     elif except_type == AppActionType.STOP_RUNLOOP:
#         file_prefix = 'adc_exception_stop_runloop'
#
#     # 上报异常图片
#     file_name_path = None
#     # if except_type == AppActionType.STOP_APP or (index == get_runloop_count() - 1):
#     file_name_path = snapshot_when_exception(file_prefix, index)
#
#     # 这里当holdgame的情况下，则不用调用处理异常的接口，认为是游戏界面是正常的
#     if AppDynamicInfo.get_instance().getHoldGame() == False:
#         monitor_task_status(env, '---处理app_will_process_exception_snapshot', f"")
#         biz_module.app_will_process_exception_snapshot(file_name_path)
#
#     except_oss_info = upload_jym_oss_with_pathes([file_name_path])
#     except_oss_pathes, except_cdn_urls = except_oss_info
#
#     monitor_task_status(env, '上传exception图片', f"{except_cdn_urls}")
#
#     # 改变Result状态
#     result = process_exception_after_change_result(index, result)
#
#     # 上报时光机
#     all_operate_image_pathes = get_directory_sorted_timestamp_files(ST.LOG_DIR)
#     operate_image_pathes = all_operate_image_pathes[-30:]
#
#     operate_oss_info = upload_jym_oss_with_pathes(operate_image_pathes)
#     operate_oss_pathes, operate_cdn_urls = operate_oss_info
#
#     sorted_operate_cdn_urls = sorted(operate_cdn_urls, key=get_number_from_path)
#
#     monitor_task_status(env,  '上传操作流30张图片', f"{sorted_operate_cdn_urls}")
#
#     monitor_task_status_v2(f'---report_exception_info____end', '')
#
#     performance_interval = int(time.time() * 1000000) - performance_start_timestamp
#     monitor_task_status_v2(f"report_exception_info_cost", f"---report_exception_info_cost:{performance_interval}")
#
#     return result
#
#
# def get_exception_desc(e):
#     inner_e = e.get_inner_e()
#     e_args = inner_e.args
#     if len(e_args) > 0:
#         return e_args[0]
#     return None
#
#
# ################### 失败后的处理
# def process_ext_info(env, ext_info):
#     monitor_task_status_v2(f'---process_ext_info____start', '')
#
#     status = int(ext_info['key'])
#     type = ext_info['type']
#     desc = ext_info['desc']
#
#     monitor_print(f"---process_ext_info:{status}, type:{type}, desc:{desc}")
#
#     if type == AppActionType.STOP_RUNLOOP:
#         if status == 120000:
#             monitor_task_status(env, '脚本main start结束', '两次重试出错')
#
#             error_task_status = get_task_status_last_errorcode()
#             monitor_print(f"---process_ext_info_get_task_status_last_errorcode:{error_task_status}")
#             monitor_task_status_v2('process_ext_info',
#                                    f"last_errorcode:{error_task_status}")
#
#             if error_task_status is not None:
#                 monitor_task_status_v2('上报stop_runloop错误结束码', f'串流上报错误结束码{error_task_status},{desc}')
#                 request_workflow_task_status('上报stop_runloop错误结束码', f'串流上报错误结束码{error_task_status},{desc}', error_task_status)
#
#                 monitor_task_status_v2('任务中心stop_runloop错误结束码', f'任务中心上报错误结束码{error_task_status},{desc}')
#                 monitor_report_task_info(env, error_task_status)
#             else:
#                 monitor_task_status_v2('上报stop_runloop结束码', f'串流上报错误结束码{status},{desc}')
#                 request_workflow_task_status('上报stop_runloop结束码', f'串流上报错误结束码{status},{desc}', status)
#
#                 monitor_task_status_v2('任务中心stop_runloop结束码', f'任务中心上报错误结束码{status},{desc}')
#                 monitor_report_task_info(env, status)
#     elif type == AppActionType.STOP_APP:
#         monitor_task_status_v2('上报stop_app结束码', f'串流上报结束码{status},{desc}')
#         if status == 200:
#             # 游戏保持，并holdgame的流程中，从设备角度看一直是任务执行中，需要按照4的状态来上报串流
#             request_workflow_task_status('上报stop_app结束码', f'串流上报结束码{status},{desc}', 4)
#         else:
#             request_workflow_task_status('上报stop_app结束码', f'串流上报结束码{status},{desc}', status)
#
#         monitor_task_status_v2('任务中心stop_app结束码', f'任务中心上报结束码{status},{desc}')
#         monitor_report_task_info(env, status)
#
#     # upload_oss(env)
#     log_oss_result = upload_jymoss_with_prefix_name('log', need_sort=False)
#     if log_oss_result is not None:
#         log_oss_path,log_cdn_urls = log_oss_result
#         monitor_task_status_v2('上传log.txt', f"{log_cdn_urls}")
#     else:
#         monitor_task_status_v2('上传log.txt', f"没有log.txt")
#
#     monitor_task_status_v2(f'---process_ext_info____end', '')
#
#
# ### **********************成功后的数据上传********************** ###
# def process_upload_oss(env):
#     monitor_task_status_v2(f'---process_upload_oss____start', '')
#
#     # 处理结果图片
#     report_urls = []
#     report_cdn_urls = []
#     if is_fabu_task():
#         url_info = upload_jym_oss(env)
#         if url_info is not None and len(url_info) > 0:
#             report_urls, report_cdn_urls = url_info
#
#         upload_jym_oss_with_log()
#     else:
#         urls = upload_oss(env)
#         report_urls = urls
#         report_cdn_urls = urls
#
#     if report_urls is None or len(report_urls) == 0:
#         monitor_task_status(env, 'report_urls上传失败', "", 10011)
#         return
#     elif len(report_urls) < 3:
#         # need_report_finish = False
#         monitor_task_status(env,  '上传不足数量的urls', f"{report_urls}")
#         monitor_task_flow_status_info(1002, '上传不足数量的urls')
#     else:
#         monitor_task_status(env,  '上传urls', f"{report_urls}")
#         monitor_task_status(env, '上传cdn_urls', f"{report_cdn_urls}")
#
#     # 处理seller图片
#     # seller_urls = []
#     report_seller_urls = []
#     report_seller_cdn_urls = []
#     if is_fabu_task():
#         seller_url_info = upload_jymoss_with_prefix_name('adc_seller')
#         if seller_url_info is not None and len(seller_url_info) > 0:
#             report_seller_urls, report_seller_cdn_urls = seller_url_info
#     else:
#         seller_urls = upload_lingxioss_with_prefix_name('adc_seller')
#         report_seller_urls = seller_urls
#
#     if report_seller_urls is None or len(report_seller_urls) == 0:
#         monitor_task_status(env,  '没有seller_urls', '')
#     else:
#         monitor_task_status(env,  '上传seller urls', f"{report_seller_urls}")
#
#     # 处理seller信息
#     seller_properties = None
#     # app_will_process_sellers 返回的map中可能有两个key：roleId和channelUserId
#     seller_func = 'app_will_process_sellers'
#     if hasattr(biz_module, seller_func):
#         monitor_print(f"----app_will_process_sellers:{report_seller_urls}")
#         module_seller_method = getattr(biz_module, seller_func)
#         sellers_info = module_seller_method(report_seller_urls)
#
#         if sellers_info is not None and len(sellers_info) > 0:
#             seller_properties = sellers_info
#
#     # 上传log.txt文件
#     log_pathes = get_log_txt_files(env)
#     _, log_cdn_urls = upload_jym_oss_with_pathes(log_pathes)
#     monitor_task_status(env, '上传log.txt', f"{log_cdn_urls}")
#
#     # 图片上传后统计内存
#     memory_usage = get_memory_usage()
#     monitor_task_status_v2(f"内存使用情况", f"当前内存使用情况: {memory_usage}KB")
#     monitor_print(f"---phase内存使用情况: {memory_usage}KB")
#
#     global launchType
#     game_properties = None
#     task_status = 6
#
#     # 处理多子属性信息
#     monitor_task_status_v2(f'---process_upload_oss____properties', '')
#     reward_method = get_module_attr_method(biz_module, 'game_need_force_upload_properties')
#     force_upload_properties = False
#     if reward_method:
#         force_upload_properties = reward_method()
#         monitor_print(f"---game_need_force_upload_properties_main: {force_upload_properties}")
#
#     func_name = 'app_will_process_properties'
#     if (is_fabu_task() or force_upload_properties == True) and report_cdn_urls and len(report_cdn_urls) > 0:
#         # 判断模块中是否实现了指定方法
#         if hasattr(biz_module, func_name):
#         # if func_name in globals():
#             # 函数存在，可以安全地调用它
#             monitor_task_status_v2(f'---process_upload_oss____get_properties', '')
#
#             properties = get_game_proerties_by_task()
#             if properties is not None:
#                 monitor_print(f"---app_will_process_properties_source_has:{properties}, {type(properties)}")
#             else:
#                 monitor_print(f"---app_will_process_properties_source_none")
#             # if launchType == 'localtest':
#             #     properties = get_game_proerties_by_task('729')
#
#             if properties and len(properties) > 0 and properties['data'] and properties['data']['gameProperties'] and len(properties['data']['gameProperties']) > 0:
#                 # 获取方法对象
#                 monitor_print(f"---app_will_process_properties_source:{properties}")
#                 monitor_print(f"---app_will_process_properties_source_gameProperties:{properties['data']['gameProperties']}")
#                 module_method = getattr(biz_module, func_name)
#                 result_properties = module_method(properties['data']['gameProperties'], report_cdn_urls)
#                 task_status, game_properties, append_oss_info = result_properties
#                 monitor_print(f"---app_will_process_properties_result:{result_properties}")
#                 if append_oss_info is not None:
#                     oss_pathes, cdn_urls = append_oss_info
#                     report_urls = oss_pathes + report_urls
#             else:
#                 monitor_print(f"发布脚本：对子属性获取失败")
#                     # app_will_process_properties(properties['data']['gameProperties'], urls)
#         else:
#             monitor_print(f"发布脚本：：函数 '{func_name}' 必须实现")
#
#     sanmou_result = None
#     if hasattr(biz_module, "app_will_process_sanmou_result"):
#         sanmou_result = getattr(biz_module, "app_will_process_sanmou_result")()
#     monitor_print(f"----8888:{report_urls}, {report_cdn_urls}, {report_seller_urls}, {report_seller_cdn_urls}")
#
#     monitor_task_status_v2('成功结束', '串流上报结束状态6')
#     request_workflow_task_status('成功结束', '串流上报结束状态6', 6)
#
#     # monitor_task_status(env,  '成功结束', '上报结束状态6', 6)
#
#     monitor_print(f"----monitor_report_task_info_final:{task_status},{report_urls}, {report_seller_urls}")
#     monitor_print(f"----monitor_report_task_info_inspect_properties: {seller_properties}")
#     monitor_task_status_v2('成功结束', '任务中心上报结束状态6')
#
#     monitor_report_task_info(env, task_status, imgs= report_urls, seller_imgs = report_seller_urls, inspect_properties=seller_properties, properties=game_properties, sanmou_result=sanmou_result)
#
#     monitor_task_status_v2(f'---process_upload_oss____end', '')
#
# def main():
#     global launchType
#     global env
#     global localNeedUpload
#
#     global ext_info
#     global error_desc
#
#     if taskId == None or len(taskId) == 0:
#         return
#
#     if gameDir == None or len(gameDir) == 0:
#         return
#     if logPath == None or len(logPath) == 0:
#         return
#     # 执行脚本
#     start(env)
#
#     # 处理异常，上传oss及后续操作
#     if launchType != 'localtest' or ((is_fabu_task()) and localNeedUpload == True):
#         if ext_info != None:
#             process_ext_info(env, ext_info)
#             monitor_task_status(env, '异常结束', '')
#         else:
#             process_upload_oss(env)
#             monitor_task_status(env, '成功结束', '')
#
#     ext_info = None
#     error_desc = None
#
#     remove_script_end_task_file(env.taskId)
#
#
# monitor_print("This is the main program.")
# main()
# monitor_print("End of the main program.")
