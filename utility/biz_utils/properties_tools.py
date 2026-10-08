import json
from typing import List, Dict


def getGameProperties(property_item):
    propertyName = property_item.get("propertyName")
    gameProperties = property_item.get("gameProperties", [])
    optionList = property_item.get("optionList", [])
    return propertyName, gameProperties, optionList

def getChildProperties(property_item):
    propertyValue = property_item.get("propertyValue")
    childProperties = property_item.get("childProperties", [])
    return propertyValue, childProperties

def getPropertyValues(property_item):
    propertyName = property_item.get("propertyName")
    propertyValues = property_item.get("propertyValues", [])
    return propertyName, propertyValues

def properties_organize(properties_data: List):
    if isinstance(properties_data, str):
        properties_data = json.loads(properties_data)
    """属性库整理"""
    p0_dict = {}
    for p1 in properties_data:
        propertyName1, gameProperties, optionList = getGameProperties(p1)
        p1_dict = {}
        if gameProperties:
            for p2 in gameProperties:
                propertyValue, childProperties = getChildProperties(p2)
                p2_dict = {"名称": propertyValue}
                for p3 in childProperties:
                    propertyName, propertyValues = getPropertyValues(p3)
                    p3_dict = {}
                    for p4 in propertyValues:
                        propertyValue, childProperties = getChildProperties(p4)
                        p3_dict.setdefault(propertyName, []).append(propertyValue)
                        if childProperties:
                            print("p4childProperties:", childProperties)
                    p3_dict.setdefault(propertyName, None)
                    p2_dict.update(p3_dict)
                p1_dict.setdefault(propertyName1, []).append(p2_dict)
            p0_dict.update(p1_dict)

        elif optionList:
            p0_dict.update({propertyName1: optionList})
        p0_dict.setdefault(propertyName1, None)
    return p0_dict

def properties_organize_simple(properties_organize_result: Dict):
    properties_simple = {}
    for key, value in properties_organize_result.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    properties_simple.setdefault(key, {}).update({item["名称"]: item})
                elif isinstance(item, str):
                    properties_simple.setdefault(key, []).append(item)
        properties_simple.setdefault(key, value)

    # for key0, value0 in properties_organize_result.items():
    #     if isinstance(value0, list):
    #         for item in value0:
    #             if isinstance(item, dict):
    #                 name = item["名称"]
    #                 for key1, value1 in item.items():
    #                     if key1 == "名称": continue
    #                     if isinstance(value1, list):
    #                         for key2 in value1:
    #                             keystr = f"{key0}-{key1}-{key2}"
    #                             properties_simple.setdefault(keystr, []).append(name)
                        # else:
                        #     keystr = f"{key0}-{key1}"
                        #     properties_simple.setdefault(keystr, []).append(name)

    return properties_simple

def properties_organize_simple_v2(properties_organize_result: Dict):
    properties_simple = {}
    for key, value in properties_organize_result.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    properties_simple.setdefault(key, []).append(item["名称"])
                elif isinstance(item, str):
                    properties_simple.setdefault(key, []).append(item)
        properties_simple.setdefault(key, value)

    return properties_simple
