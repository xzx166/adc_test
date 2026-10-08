# -*- encoding=utf8 -*-
from airtest.core.api import *
import time



using("../utility/mask.air")
from mask import *

using("../utility/swipe.air")
from swipe import *

using("../utility/image.air")
from image import *

using("../utility/ocr.air")
from ocr import *


using("../utility/upload.air")
from upload import *


air_name = "11264_netease_index.air"

indexModule = lx_import(air_name)
ENV = AppEnv.get_instance()

import json
import re

auto_setup(__file__)

gameName = "永劫无间PC" 
allOCRData = {}

ENV = AppEnv.get_instance()


# ================== get home ocr ==========================
def aTask():
    monitor_task_status(ENV, "游戏 - start", "")

def getYJWJCommonPropertyInfo(dict, properties):

    checkedList = []
    if dict is not None:
        for key in dict:
            aStr = dict[key]
            for item in properties:
                if key == item['propertyName']:
                    resItem = {}
                    resItem['propertyId'] = item['propertyId']
                    if 'optionList' in item:
                        optionList = item['optionList']
                        for option in optionList:
                            if option == aStr:
                                resItem['value'] = option
                    else:
                        resItem['value'] = aStr
                    
                    checkedList.append(resItem)
                    break
    print(f'yjwj_checkedList:{checkedList}')
    return checkedList

def getYJWJPifuAndFaxingPropertyInfo(properties):
    global indexModule

    checkedList = []
    waiguanOCRList = indexModule.get_yjwj_ocr_waiguan_list()
    faxingOCRList = indexModule.get_yjwj_ocr_faxing_list()

    for item in properties:
        cengji1Item = {}
        if 'propertyId' in item and 'useGameProperty' in item:
            cengji1Item['propertyId'] = item['propertyId']
            cengji1Item['useGameProperty'] = item['useGameProperty']
        
        cengji1GameProperties = []
        if 'gameProperties' in item and len(item['gameProperties'])>0:
            gamePropertiesList = item['gameProperties']
            for gameProperty in gamePropertiesList:
                if 'propertyValue' in gameProperty:
                    value = gameProperty['propertyValue']
                    subItemMap = {'value':value, 'childProperties':gameProperty['childProperties'], 'propertyExt':gameProperty['propertyExt']}

                    for waiguanName in waiguanOCRList:
                        if waiguanName in value and '发型' not in value:
                            monitor_print(f"propertyValue00000waiguan:{value}")
                            cengji1GameProperties.append(subItemMap)
                            break
                    for faxingName in faxingOCRList:
                        if faxingName in value and '发型' in value:
                            monitor_print(f"propertyValue00000faxing:{value}")
                            cengji1GameProperties.append(subItemMap)
                            break
        if len(cengji1GameProperties)>0:
            cengji1Item['gameProperties'] = cengji1GameProperties
            checkedList.append(cengji1Item)

            monitor_print(f"cengji1Item:{cengji1Item}")

    return checkedList


# ============================================
def restructure_sub_item_child(childProperties):
    restructureList = []
    for child in childProperties:
        chidData = {}
        chidData['propertyId'] = child['propertyId']

        propertyValues = child['propertyValues']
        if propertyValues is not None and len(propertyValues) >0:
            firstItem = propertyValues[0]
            if 'propertyValue' in firstItem:
                chidData['value'] = firstItem['propertyValue']
            if 'propertyExt' in firstItem:
                chidData['propertyExt'] = firstItem['propertyExt']
        restructureList.append(chidData)
    return restructureList

def newChildProperties(name):
    if 'childProperties' in name:
        child_properties = restructure_sub_item_child(name['childProperties'])
    else:
        child_properties = []
    return child_properties
    
def meger_child_properties(childProperties):
    global indexModule

    waiguanAllOCRList = []
    waiguanOCRList = indexModule.get_yjwj_ocr_waiguan_list()
    faxingOCRList = indexModule.get_yjwj_ocr_faxing_list()
    waiguanAllOCRList.extend(waiguanOCRList)
    waiguanAllOCRList.extend(faxingOCRList)
    monitor_print(f"yjwj_wujiangAllData:{waiguanAllOCRList}")

    combined_array = [{'childProperties': newChildProperties(name), 'propertyExt':name['propertyExt'], 'value': name['propertyValue']}
                  for name in childProperties
                  for value in waiguanAllOCRList
                  if value == name['propertyValue']]
    return combined_array

def get_last_create_upload_proerties(jymProperties):
    allWujiangKeys = ['英雄皮肤','武器皮肤','挂饰皮肤']
    wujiangAllData = []

    for property in jymProperties:
        for wjKey in allWujiangKeys:
            if property['propertyName'] == wjKey:
                currentMap = {}
                duihuanProperties = property['gameProperties']
                duihuanCombined = meger_child_properties(duihuanProperties)

                currentMap['useGameProperty'] = property['useGameProperty']
                currentMap['propertyId'] = property['propertyId']
                currentMap['gameProperties'] = duihuanCombined
                wujiangAllData.append(currentMap)
    monitor_print(f"yjwj_wujiangAllData:{wujiangAllData}")
    return wujiangAllData


# ============================================
def cleanGame(env):
    # shell("rm -rf /sdcard/37shouyou") 
    # shell("rm -rf /data/data/com.sy.dldlhsdj.gw/databases") 
    # shell("rm -rf /data/data/com.sy.dldlhsdj.gw/shared_prefs") 

    monitor_task_status(env, "清理游戏信息", "")

def closeGame(env):
    # stop_app("com.sy.dldlhsdj.gw")
    monitor_task_status(env, "关闭游戏", "")

def game_will_launch(env):     
    # global gameName
    monitor_task_status(env, "启动游戏", f"启动{gameName}")
    ### start_app("com.dldlhsdj.wzpz1")
    # start_app("com.sy.dldlhsdj.gw")
   



app_did_get_properties = indexModule.app_did_get_properties
def game_did_launch(env):
    global indexModule

    print('game_did_launch=====fabu')
    monitor_task_status(env, "fabu", f"taskType{env.taskType}")

    phaseList = []


    phase = Phase("start",lambda: indexModule.startTask())
    phaseList.append(phase)

    return phaseList
    
def game_will_close(env):
    closeGame(env)


def game_will_clean(env):
    cleanGame(env)


def app_will_process_exception_snapshot(snapshot_path):
    print("dd")
    # if lx_exists_with_file(Template(r"tpl1701743490373.png", record_pos=(-0.102, 0.12), resolution=(2400, 1350)), snapshot_path):
    #     monitor_task_status(AppEnv.get_instance(), "账号被踢上报", "")
    #     monitor_task_flow_status_info(1001, '被踢掉登录账户')
    # elif lx_exists_with_file(Template(r"tpl1702611844423.png", record_pos=(-0.102, 0.12), resolution=(2400, 1350)), snapshot_path) or lx_exists_with_file(Template(r"tpl1702611856576.png", record_pos=(-0.102, 0.12), resolution=(2400, 1350)), snapshot_path):
    #     monitor_task_status(AppEnv.get_instance(), "账号异地游戏中", "")
    #     monitor_task_flow_status_info(1001, '账号异地游戏中')
    # elif exists(Template(r"tpl1702456637314.png", record_pos=(-0.102, 0.12), resolution=(2400, 1350))):
    #     monitor_task_status(AppEnv.get_instance(), "卖家手机号待验证 - 上报", "")
    #     monitor_task_flow_status_info(10103, '卖家手机号待验证')

def is_valid_json(json_string):
    try:
        json.loads(json_string)  # 尝试解析JSON
        return True  # 解析成功，返回True
    except json.JSONDecodeError:  # 解析失败，捕获异常
        return False  # 返回False

def app_will_process_properties(properties,urls):
    gameProperties = []
    if is_valid_json(properties):
        gameProperties = json.loads(properties)


    global indexModule

    calMap = indexModule.get_yjwj_eas_response_map()
    monitor_print(f'cal_calMap:{calMap}')
    
    calProperties = []
    if calMap is not None:
        calProperties = getYJWJCommonPropertyInfo(calMap, gameProperties)
        monitor_print(f'calProperties:{calProperties}')
    
    # calProperties.extend(getYJWJPifuAndFaxingPropertyInfo(gameProperties))
    calProperties.extend(get_last_create_upload_proerties(gameProperties))
    
    
    return (6,calProperties,None)