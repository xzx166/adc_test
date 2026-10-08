from airtest.core.api import *

from utility.base.adc_api import *

air_name = "11264_netease_index.air"
biz_module = lx_import(air_name)

from utility.biz_utils.biz_utils import *

game_will_launch = biz_module.game_will_launch
game_will_close = biz_module.game_will_close
game_will_clean = biz_module.game_will_clean
app_will_process_exception_snapshot = biz_module.app_will_process_exception_snapshot
app_will_process_sellers = biz_module.app_will_process_sellers
game_did_launch = biz_module.game_did_launch
app_did_get_properties = biz_module.app_did_get_properties
app_will_get_runloop_count = biz_module.app_will_get_runloop_count
# ----------------------------------------------------------------------------

class PropertiesBuild:
    def __init__(self, gameProperties):
        self.gameProperties = gameProperties
        self.properties_data = property_read()
        if self.properties_data and localRun:
            (gameDir / "properties_data_temp.json").write_text(json.dumps(self.properties_data, ensure_ascii=False, indent=4))
        if not self.properties_data and localRun and (gameDir / "properties_data_local.json").exists():
            self.properties_data = json.loads((gameDir / "properties_data_local.json").read_text())
        self.properties_callback_data = []

        # 属性库更新
        # self.propertiesUpdateTemplates = {}
        # json_path = gameDir / "propertiesUpdateTemplates.json"
        # if json_path.exists():
        #     json_data = json.loads(json_path.read_text())
        #     for property_item in json_data:
        #         self.propertiesUpdateTemplates[property_item["propertyName"]] = property_item

    def simple(self, item, property_name):
        property_items = self.properties_data.get(property_name)
        if property_items is not None:
            optionList = item.get("optionList")
            if optionList and property_name not in ["帐号类型"]:
                if isinstance(property_items, List):
                    property_exists_values = []
                    property_notexists_values = []
                    for property_item in property_items:
                        if property_item in optionList:
                            property_exists_values.append(property_item)
                        else:
                            for option in optionList:
                                if option in property_item:
                                # if option == property_item or difflib.SequenceMatcher(a=option, b=property_item).ratio() > 0.5:
                                    property_exists_values.append(option)
                                    break
                            else:
                                property_notexists_values.append(property_item)

                    self.properties_callback_data.append(dict(
                        propertyName=property_name,
                        value=",".join(property_exists_values) if property_exists_values else "无",
                        propertyId=item.get("propertyId"),
                    ))

                    if property_notexists_values:
                        output = format_print(property_notexists_values)
                        monitor_task_status_v2(f"{property_name}Property", f"未识别{property_name}：{output}")

                elif isinstance(property_items, str):
                    if property_items in optionList:
                        self.properties_callback_data.append(dict(
                            propertyName=property_name,
                            value=property_items,
                            propertyId=item.get("propertyId"),
                        ))
                    else:
                        monitor_task_status_v2(f"{property_name}Property", f"未识别{property_name}：{format_print(property_items)}")
            else:
                self.properties_callback_data.append(dict(
                    propertyName=property_name,
                    value=property_items,
                    propertyId=item.get("propertyId"),
                ))
        else:
            monitor_task_status_v2("未采集", property_name)

    def multichild(self, item, property_name):
        property_data = {}
        if property_list := self.properties_data.get(property_name):
            property_data.update(
                propertyName=property_name,
                gameProperties=[],
                propertyId=item.get("propertyId"),
                useGameProperty=item.get("useGameProperty"),
            )
            residue = []
            for single_property in property_list:
                single_propertyValue = single_property.get("名称")
                for gps in item.get("gameProperties"):
                    a = gps.get("propertyValue")
                    b = single_propertyValue
                    if a == b or (len(a) >= 5 and a in b):
                        childProperties = []
                        # 子属性
                        for cps in gps.get("childProperties", []):
                            childName = cps.get("propertyName")
                            if single_childPropertyValue := single_property.get(childName, ""):
                                for pvs in cps.get("propertyValues", []):
                                    if pvs.get("propertyValue", "") in single_childPropertyValue:
                                        childProperties.append(dict(
                                            childName=childName,
                                            value=pvs.get("propertyValue"),
                                            propertyExt=pvs.get("propertyExt"),
                                            propertyId=cps.get("propertyId"),
                                        ))
                                        break

                        childProperty = dict(
                            value=gps.get("propertyValue"),
                            childProperties=childProperties,
                            propertyExt=gps.get("propertyExt"),
                        )
                        if propertyImage := single_property.get("属性图片"):
                            if os.path.isfile(propertyImage):
                                childProperty["image"] = image_path_upload(propertyImage, local_save=True)[0]
                            else:
                                childProperty["image"] = propertyImage
                        property_data["gameProperties"].append(childProperty)
                        break
                else:
                    residue.append(f"{single_propertyValue}：名称未识别")

            if residue:
                output = format_print(residue)
                monitor_task_status_v2(f"{property_name} Property", output)

        if property_data:
            self.properties_callback_data.append(property_data)
        else:
            monitor_task_status_v2("未采集", property_name)

    def __call__(self, *args, **kwargs):
        if not localRun:
            monitor_print(f"本地采集原始数据: {json.dumps(dict(self.properties_data), ensure_ascii=False)}")
        for property_item in self.gameProperties:
            propertyName = property_item["propertyName"]
            if propertyName in ["服装", "发型", "变身器","武器皮肤"]:
                self.multichild(property_item, propertyName)
            else:
                self.simple(property_item, propertyName)
        else:
            if not isinstance(self.properties_data, Dict):
                self.properties_data.close()

            return self.properties_callback_data

# 多子属性
def app_will_process_properties(properties, urls="test"):
    if isinstance(properties, str): properties = json.loads(properties)
    properties_callback_data = PropertiesBuild(properties)()
    # if not localRun:
    #     monitor_print(f"返回结果: {json.dumps(properties_callback_data, ensure_ascii=False)}")
    return 6, properties_callback_data, None

# 多子属性-测试
def properties_test():
    gameProperties = json.loads((gameDir / "properties_remote.json").read_text())
    properties_callback_data = app_will_process_properties(gameProperties)[1]
    (gameDir / "properties_callback_local.json").write_text(json.dumps(properties_callback_data, ensure_ascii=False, indent=4))
