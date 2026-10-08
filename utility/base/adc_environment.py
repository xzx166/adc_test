# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

from enum import Enum

import json

import time

import os, sys



class TaskType(Enum):
    YANHAO = 3
    FABU = 2
    PC_FABU_OCR = 11
    CAPTCHA_TASK = 20
    AI_REBIND_TASK = 30
    CLEAN_GAME_TASK = 999  # 不做特殊处理，流程需要close和clean，走默认就可以
    UPDATE_QUFU_TASK = 1000
    EAGLE_DOWN_TASK = 1001
    EAGLE_QUERY_TASK = 1002
    GAME_GONGLUE_TASK = 1003
    MCP_TASK = 1004
    HEADLESS_CHROME_TASK = 1005

class SystemType(Enum):
    ANDROID = "android"
    IOS = "ios"
    YUNYOU_IOS = "yunyou_ios"



class TaskSource(Enum):
    BMAIJIA = 1
    TUOGUAN = 3

class TaskAppId(Enum):
    TASK_APPID_JIAOYIMAO = 'jiaoyimao'
    TASK_APPID_KEJINSHOU = '35020201'

class TaskBizPlatformType(Enum):
    BIZ_PLATFORM_ANDROID = 'android'
    BIZ_PLATFORM_IOS = 'ios'
    BIZ_PLATFORM_YUNYOU_IOS = 'yunyou_ios'
    BIZ_PLATFORM_HEADLESS_CHROME = 'headless_chrome'  # 这里主要是因为headless不用 airtest，所以需要特殊处理



class AppEnv:
    __app_env_instance = None

    def __init__(self):
        self.launchType = 'localtest'
        self.phone = ""
        self.smsCode = ""
        self.username = ""
        self.password = ""
        self.game_id = ''
        self.game_platfrom = ''
        self.taskId = "239"
        self.sleepTime = 0.5
        # 0:submit 1:start 2:device 3:script 4:running 5:result
        self.taskStatus = 4
        self.scriptEnv = "daily"
        self.logPath = ''
        self.gameDir = ''
        self.game_name = None
        self.scriptHome = ''
        self.taskType = TaskType.YANHAO.value
        self.rootHome = ''
        self.mode = "null"
        self.oss_mode = ''
        self.oss_app_id = ''
        self.oss_app_secret = ''
        self.device = None
        self.taskSource = 0
        self.game_area = None
        self.task_contenttype = 1
        self.transfer_account_info = ''
        self.account_attr = ''
        self.image_list_json = ''
        self.game_properties_version = 0



        self.common_properties_json = ''

        self.oss_eagle_app_id = ''
        self.oss_eagle_app_secret = ''

        self.oss_miniapp_app_id = ''
        self.oss_miniapp_app_secret = ''

        self.system_type = 'android'
        self.task_appId = TaskAppId.TASK_APPID_JIAOYIMAO.value

        self.iOSDeviceId = ''
        self.iOS_session_connect = None
        self.iOS_wda_port = None
        self.mds_client_token = None

        # local参数只在本地运行时有用，这三个参数在localtest_config中也有定义，建议在config文件中定义，这样不影响其他的游戏
        # --------本地测试的环境设置-----------
        # 在localtest下是否清理游戏
        self.localtest_need_clean = True
        # 在localtest下是否需要上传oss
        self.localtest_need_upload = True
        # 在localtest下是否删除logPath日志
        self.localtest_remove_log = True


    @classmethod
    def get_instance(cls):
        if not cls.__app_env_instance:
            cls.__app_env_instance = cls()
        return cls.__app_env_instance

    def setEnv(self, launchType, phone, smsCode, username, password, taskId, scriptEnv, mode, logPath, gameDir,
               scriptHome, rootHome, ossMode, ossAppId, ossAppSecret, sleepTime, taskType, taskSource, game_area,
               task_contenttype, transfer_account_info, account_attr, game_properties_version, image_list_json,
               common_properties_json, oss_eagle_app_id, oss_eagle_app_secret, device=None, system_type='android', iOSDeviceId=None, iOS_session_connect=None, mds_client_token=None, decrypt_key=None, oss_miniapp_app_id=None, oss_miniapp_app_secret=None):
        self.launchType = launchType
        self.phone = phone
        self.smsCode = smsCode
        self.username = username
        self.password = password
        self.taskId = taskId
        self.taskStatus = 4
        self.scriptEnv = scriptEnv
        self.logPath = logPath
        self.scriptHome = scriptHome
        self.rootHome = rootHome
        self.gameDir = gameDir
        self.mode = mode
        self.sleepTime = sleepTime
        self.taskType = taskType

        self.oss_mode = ossMode
        self.oss_app_id = ossAppId
        self.oss_app_secret = ossAppSecret

        self.oss_eagle_app_id = oss_eagle_app_id
        self.oss_eagle_app_secret = oss_eagle_app_secret

        self.oss_miniapp_app_id = oss_miniapp_app_id
        self.oss_miniapp_app_secret = oss_miniapp_app_secret

        self.device = device   # android的设备
        self.iOSDeviceId = iOSDeviceId  # iOS的设备

        self.taskSource = taskSource
        self.game_area = game_area
        self.task_contenttype = task_contenttype
        self.transfer_account_info = transfer_account_info
        self.account_attr = account_attr
        self.image_list_json = image_list_json
        self.game_properties_version = game_properties_version

        self.common_properties_json = common_properties_json

        self.internal_account_attr = self.parse_json_data(self.account_attr)
        self.internal_common_properties = self.parse_json_data(self.common_properties_json)
        self.internal_transferAccountInfo = self.parse_json_data(self.transfer_account_info)

        self.game_id = self.get_common_property_with_key("gameId")
        self.game_platfrom = self.get_common_property_with_key("gamePlatform")

        self.iOS_session_connect = iOS_session_connect
        self.system_type = system_type
        self.mds_client_token = mds_client_token

        self.decrypt_key = decrypt_key

    # captchaTaskStatus 手机号登录的执行的阶段
    # jymPackageName common参数要用到的报名
    # jymScheduleId  业务用不到，云游的ScheduleId
    # gamePlatform  游戏平台

    def parse_json_data(self, json_data):
        if json_data is not None and len(json_data) > 0:
            return json.loads(json_data)
        else:
            return None

    def get_common_property_with_key(self, key):
        if self.internal_common_properties is not None and len(self.internal_common_properties) > 0:
            return self.internal_common_properties.get(key)
        else:
            return None

    # domainId; domainName;
    # CLOUD_GAME_PC_SCHEDULE_ID  pc 容器的 scheduleid
    def get_account_attr_with_key(self, key):
        if self.internal_account_attr is not None and len(self.internal_account_attr) > 0:
            return self.internal_account_attr.get(key)
        else:
            return None

    def get_transfer_accountInfo_with_key(self, key):
        if self.internal_transferAccountInfo is not None and len(self.internal_transferAccountInfo) > 0:
            return self.internal_transferAccountInfo.get(key)
        else:
            return None

    def is_fabu_task(self):
        return self.taskType == TaskType.FABU.value or self.taskType == TaskType.PC_FABU_OCR.value



class AppPerformanceInfo:
    __instance = None

    def __init__(self):
        self.timeDurationMap = {}

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    def setTimeDurationMap(self, duration_key, duration_start=True):
        if duration_start:
            self.timeDurationMap[duration_key] = int(time.time() * 1000000)
        else:
            if duration_key not in self.timeDurationMap:
                raise Exception("duration_key not in self.timeDurationMap")
            else:
                self.timeDurationMap[duration_key] = int(time.time() * 1000000) - self.timeDurationMap[duration_key]
                # monitor_print(f"---setTimeDurationMap_{duration_key}: {self.timeDurationMap[duration_key]}")

    def getTimeDurationMap(self):
        return self.timeDurationMap


class AppDynamicInfo:
    __instance = None

    def __init__(self):
        self.hasLogin = False
        self.holdGame = False
        self.isM3Support = False
        self.iosHasKicked = False
        self.iosClient = None
        self.iosCb = None
        self.partial_func = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    def setHasLogin(self, login):
        self.hasLogin = login

    def getHasLogin(self):
        return self.hasLogin

    def setHoldGame(self, hold):
        self.holdGame = hold

    def getHoldGame(self):
        return self.holdGame

    def setIsM3Support(self, isM3Support):
        self.isM3Support = isM3Support

    def getIsM3Support(self):
        return self.isM3Support


def get_home_adc_directory():
    home_path = os.path.expanduser("~")
    directory = os.path.join(home_path, ".adc")
    # 判断目录是否存在
    if os.path.exists(directory):
        pass
        # print(f"目录 {directory} 已存在")
    else:
        # 创建目录
        os.makedirs(directory)
        # print(f"目录 {directory} 创建成功")
    return directory