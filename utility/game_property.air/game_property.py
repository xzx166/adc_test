# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

import importlib
import sys

from airtest.core.api import *
from airtest.core.helper import G
from airtest.core.cv import *
from airtest.core.error import TargetNotFoundError, InvalidMatchingMethodError
from airtest.core.android.android import *
from enum import Enum

auto_setup(__file__)

using("../utility/monitor.air")
from monitor import *

using("../utility/adc_tools.air")
from adc_tools import *

import cv2
import time
import json

######################注意事项######################
'''
upload_properties_info_map 这个参数是本地采集的多子属性的总数据，要用下面的方法，该数据有两个基本要求：
1.  所有的key值必须跟多字属性保持一致
2.  除了二级属性中的 '名称'和'image'，这两个必须是写死的key，这两个分别对应比如物品的名字和图片链接,其他的按照多子属性的key来命名
3.  game_properties中的每个元素对应的是如下的数据结构:
        {

            "名称": "青珑挂珠",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/zhuangbei_crop_1716205180935549.jpg"
        }
4. optionlist对应的是如下的数据结构:
    ['aaa', 'bbb']

示例：
{
    "等级": 84,
    "性别": "女",
    "装备":
    [
        {
            "改造等级": "改4",
            "名称": "狐皮袄",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/zhuangbei_crop_1716205196567560.jpg"
        },
        {
            "名称": "青珑挂珠",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/zhuangbei_crop_1716205180935549.jpg"
        },
        {
            "改造等级": "改4",
            "名称": "疾风履",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/zhuangbei_crop_1716205199159203.jpg"
        },
        
    ],
    "宠物":
    [
        {
            "名称": "仙阳剑",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/chongwu_touxiang_crop_1716205342859950.jpg"
        },
        {
            "名称": "仙阳剑",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/chongwu_touxiang_crop_1716205662171782.jpg"
        }
    ],
    "外观":
    [
        {
            "名称": "如意令",
            "分类": "队标",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/shizhuang_touxiang_crop_1716205235755276.jpg"
        },
        {
            "名称": "如意令",
            "分类": "队标",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/shizhuang_touxiang_crop_1716205555869494.jpg"
        }
    ],
    "守护":
    [
        {
            "名称": "云霄长老",
            "稀有度": "优良",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/touxiang_image_1716205406357951.jpg"
        },
        {
            "名称": "云霄童子",
            "稀有度": "普通",
            "image": "/jym-oss/resource/vmos/20240520/adc_139114/touxiang_image_1716205409547004.jpg"
        },
    ],
    "主要属性": "法",
    "主要相性": "金",
    "等级排行": "榜外",
    "门派": "玉柱洞",
    "道行": "1642年42天",
    "道行排名": "1754",
    "角色战力": "133840"
}

'''


# game_property_name对应最外层的属性名，比如宠物
# upload_properties_info_map 是本地处理的多子属性数据
# local_property_item 对应处理的根item，从common方法中传入
# child_object_name对应宠物中的每个宠物名，比如朱雀
# child_object_property_name 对应每个宠物的维度属性，比如稀有度，命座等
def get_property_value_by_gameinfo(game_property_name, upload_properties_info_map, local_property_item=None, child_object_name=None, child_object_property_name=None):

    local_property_key = game_property_name
    print("local_property_key: ", local_property_key)
    if child_object_name == None:
        return upload_properties_info_map.get(local_property_key)
    else:
        if local_property_item is not None:
            if local_property_item.get('名称') == child_object_name:
                return local_property_item.get(child_object_property_name)
        else:
            property_info_list = upload_properties_info_map.get(local_property_key)
            for index, item in enumerate(property_info_list):
                if item.get('名称') == child_object_name:
                    return item.get(child_object_property_name)


# properties是从app_will_process_properties接口获取的properties
# upload_properties_info_map 是本地采集的多子属性数据
def process_game_properties(properties, upload_properties_info_map):
    monitor_print(f"---process_game_properties:{upload_properties_info_map}")

    gameProperties = []
    if is_valid_json(properties):
        gameProperties = json.loads(properties)

    result_arr = []
    for index, item in enumerate(gameProperties):
        if item is not None:
            target_map = common_process_game_properties_item(item, upload_properties_info_map)

            if target_map is not None and len(target_map) > 0:
                result_arr.append(target_map)
    return result_arr

def common_process_game_properties_item(game_properties_item, upload_properties_info_map):
    target_game_properties_item_map = {}

    property_id = game_properties_item.get('propertyId')
    property_name = game_properties_item.get('propertyName')
    useGameProperty = game_properties_item.get('useGameProperty')
    game_properties = game_properties_item.get('gameProperties')
    game_option_list = game_properties_item.get('optionList')

    # 对于没有gameProperties的情况
    if game_properties is None or len(game_properties) == 0:
        value = get_property_value_by_gameinfo(property_name, upload_properties_info_map)
        if value is not None:
            if isinstance(value, list):
                list_value_str = ""
                for value_index, value_item in enumerate(value):
                    if game_option_list is not None and len(game_option_list) > 0:
                        if value_item in game_option_list:
                            if len(list_value_str) == 0:
                                list_value_str += value_item
                            else:
                                list_value_str += "," + value_item
                    else:
                        # 在没有option的情况下，存在多个，默认拼接
                        if len(list_value_str) == 0:
                            list_value_str += value_item
                        else:
                            list_value_str += "," + value_item

                if len(list_value_str) > 0:
                    target_game_properties_item_map['propertyId'] = property_id
                    target_game_properties_item_map['propertyName'] = property_name
                    target_game_properties_item_map['value'] = list_value_str
            else:
                target_game_properties_item_map['propertyId'] = property_id
                target_game_properties_item_map['propertyName'] = property_name
                target_game_properties_item_map['value'] = value
            return target_game_properties_item_map
        else:
            return None

    # 对于有gameProperties的情况
    target_game_properties_list = []

    local_property_list = get_property_value_by_gameinfo(property_name, upload_properties_info_map)
    if local_property_list is None or len(local_property_list) == 0:
        return None

    for local_property_index,local_property_item in enumerate(local_property_list):
        local_property_item_name = local_property_item.get('名称')

        for item in game_properties:
            child_properties_item = item

            target_game_property_map = {}

            child_properties_info_list = child_properties_item.get('childProperties')
            child_properties_name = child_properties_item.get('propertyValue')
            child_properties_ext = child_properties_item.get('propertyExt')

            # 对于带空格的name的特殊处理，在比对的时候需要去掉空格，在回传的时候要保持空格
            strip_child_properties_name = child_properties_name.strip()

            if strip_child_properties_name != local_property_item_name:
                continue

            target_child_propertys_list = []

            if child_properties_info_list is None or len(child_properties_info_list) == 0:
                continue

            for child_property in child_properties_info_list:
                child_property_id = child_property.get('propertyId')
                child_property_name = child_property.get('propertyName')
                child_property_values = child_property.get('propertyValues')

                target_child_perperty_map = {}

                has_find_child_property_value = False
                if child_property_values is None or len(child_property_values) == 0:
                    game_info = get_property_value_by_gameinfo(property_name,upload_properties_info_map, local_property_item, strip_child_properties_name, child_property_name)
                    if game_info is not None:
                        has_find_child_property_value = True

                    monitor_print(f"---common_process_game_properties_no_child_property_values:{property_name},{local_property_item}, {strip_child_properties_name}, {child_property_name},---->{game_info}")
                    if has_find_child_property_value == True:
                        # 当没有propertyValues时，是从游戏中获取的信息填入结果数据
                        target_child_perperty_map['propertyId'] = child_property_id
                        # todo - 游戏信息
                        target_child_perperty_map['value'] = game_info
                        target_child_propertys_list.append(target_child_perperty_map)
                elif len(child_property_values) ==1:
                    # 当只有一个propertyValue时，直接从该数据中获取，并填入结果数据
                    child_property_value = child_property_values[0]
                    child_property_value_property_value = child_property_value.get('propertyValue')

                    # 对于child_property_value_property_value的不同情况的处理
                    local_ocr_value = get_property_value_by_gameinfo(property_name,upload_properties_info_map, local_property_item,strip_child_properties_name,child_property_name)
                    monitor_print(f"---common_process_game_properties_1_child_property_values:{property_name},{local_property_item}, {strip_child_properties_name}, {child_property_name},---->{local_ocr_value}, {child_property_value_property_value}")

                    if child_property_value_property_value == None:
                        target_child_perperty_map['value'] = local_ocr_value
                        has_find_child_property_value = True
                    else:
                        has_find_child_property_value = True
                        if local_ocr_value == None:
                            target_child_perperty_map['value'] = child_property_value_property_value
                        elif local_ocr_value == child_property_value_property_value:
                            target_child_perperty_map['value'] = local_ocr_value
                        else:
                            monitor_game_properties_difference(1007, property_name + ':' + local_property_item_name, child_property_value_property_value, local_ocr_value)
                            has_find_child_property_value = False

                    if has_find_child_property_value == True:
                        target_child_perperty_map['propertyId'] = child_property_id
                        target_child_perperty_map['propertyName'] = child_property_name

                        child_property_value_property_ext = child_property_value.get('propertyExt')
                        if child_property_value_property_ext is not None:
                            target_child_perperty_map['propertyExt'] = child_property_value_property_ext
                        target_child_propertys_list.append(target_child_perperty_map)
                else:
                    # 当有多个propertyValue时，要基于从游戏中获取的信息进行匹配，然后再填入结果数据
                    game_ocr_property_value = get_property_value_by_gameinfo(property_name,upload_properties_info_map, local_property_item,
                                                                             strip_child_properties_name, child_property_name)
                    monitor_print(
                        f"---common_process_game_properties_n_child_property_values:{property_name},{local_property_item}, {strip_child_properties_name}, {child_property_name},---->{game_ocr_property_value}")
                    if game_ocr_property_value is not None:
                        if type(game_ocr_property_value) is str:
                            game_ocr_property_value = [game_ocr_property_value]
                        for game_ocr_property_value_sub in game_ocr_property_value:
                            for each_child_property_value in child_property_values:
                                each_child_property_value_property_value = each_child_property_value.get('propertyValue')
                                each_child_property_value_property_ext = each_child_property_value.get('propertyExt')

                                if each_child_property_value_property_value == game_ocr_property_value_sub:
                                    has_find_child_property_value = True
                                    target_child_perperty_map['value'] = each_child_property_value_property_value
                                    if each_child_property_value_property_ext is not None:
                                        target_child_perperty_map['propertyExt'] = each_child_property_value_property_ext
                                    break


                            if has_find_child_property_value == True:
                                target_child_perperty_map['propertyId'] = child_property_id
                                target_child_perperty_map['propertyName'] = child_property_name
                                target_child_propertys_list.append(target_child_perperty_map)
                            else:
                                monitor_game_properties_difference(1007, property_name + ':' + local_property_item_name,
                                                                   '',
                                                                   game_ocr_property_value)


            # 处理每个元素的结果数据
            if target_child_propertys_list is not None and len(target_child_propertys_list) > 0:
                target_game_property_map['value'] = child_properties_name
                if child_properties_ext is not None:
                    target_game_property_map['propertyExt'] = child_properties_ext
                target_game_property_map['childProperties'] = target_child_propertys_list

                image_value = get_property_value_by_gameinfo(property_name,upload_properties_info_map,local_property_item, strip_child_properties_name, 'image')
                if image_value is not None:
                    target_game_property_map['image'] = image_value

                if target_game_property_map is not None and len(target_game_property_map) > 0:
                    target_game_properties_list.append(target_game_property_map)
            break

    # 处理最外层的结果数据
    target_game_properties_item_map['propertyId'] = property_id
    target_game_properties_item_map['propertyName'] = property_name
    target_game_properties_item_map['useGameProperty'] = useGameProperty
    target_game_properties_item_map['gameProperties'] = target_game_properties_list

    return target_game_properties_item_map


# 将属性库原始字典optionList转换为gameProperties数据结构
def change_optionList_to_gameProperties(original_dict: dict, get_ocr_properties_by_name) -> dict:
    """
    :param original_dict: 原始字典，格式为{"采集类名": ["名称1", "名称2", ...]}
    :return: 新数据结构
    """
    result_arr = []
    for index, item in enumerate(original_dict):
        if item is not None:
            target_map = process_chanage_optionlist_game_properties_item(item, get_ocr_properties_by_name)

            if target_map is not None:
                result_arr.append(target_map)

    monitor_print(f'---change_optionList_to_gameProperties_result_arr:{result_arr}')

    return result_arr

def process_chanage_optionlist_game_properties_item(game_properties_item, get_ocr_properties_by_name):
    target_game_properties_item_map = {}

    property_id = game_properties_item.get('propertyId')
    property_name = game_properties_item.get('propertyName')
    game_properties = game_properties_item.get('gameProperties')
    optionList = game_properties_item.get('optionList')
    if optionList is not None and len(optionList) > 0:
        values = get_ocr_properties_by_name(property_name)
        option_values_str = ''
        for value_index, value_item in enumerate(values):
            if value_item in optionList:
                if value_index == len(values) - 1:
                    option_values_str = option_values_str + value_item
                else:
                    option_values_str = option_values_str + value_item + ','
        target_game_properties_item_map['propertyId'] = property_id
        target_game_properties_item_map['propertyName'] = property_name
        target_game_properties_item_map['value'] = option_values_str
        return target_game_properties_item_map

    else:
        # 对于有gameProperties的情况
        monitor_print('========111========',property_name)
        target_game_properties_list = []
        monitor_print('================',property_name)
        local_property_list = get_property_value_by_gameinfo(property_name)
        if local_property_list is None or len(local_property_list) == 0:
            return None

        # splitName = local_property_list.split(',')
        for propertyValueItem in game_properties_item.get("gameProperties"):
            if propertyValueItem['propertyValue'] in local_property_list:
                target_game_properties_list.append({
                    "value": propertyValueItem['propertyValue'],
                    "propertyExt": propertyValueItem['propertyExt'],
                    "childProperties": propertyValueItem["childProperties"],
                })

        # 处理最外层的结果数据
        target_game_properties_item_map['propertyId'] = property_id
        target_game_properties_item_map['propertyName'] = property_name
        target_game_properties_item_map['gameProperties'] = target_game_properties_list

        return target_game_properties_item_map