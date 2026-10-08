import requests
import time
import json
def get_pre_proerties():
    task_id = 9948934
    host = 'adc-pc.alibaba-inc.com'
    url = "http://{}/task/getGamePropertiesByTaskId".format(host)
    the_time = int(time.time()*1000)
    payload = {"taskId": task_id, "timestamp": the_time}
    response = requests.post(url, json=payload)
    res_json = response.json()
    gameProperties = json.loads(res_json["data"]["gameProperties"])
    print(len(gameProperties))
    with open(f'/Users/weizun/projects/adc-sc/utility/wz_utils/proerties.json', 'w+',encoding="utf8") as f:
        f.write(json.dumps(gameProperties,ensure_ascii=False))


def get_jiuyou_url(enviroment):
    if enviroment == "daily":
        return "http://lingxi-adc-task-sever.taobao.net"


def get_jiuyou_all_servers(enviroment, game_id: int):
    """
    调用 GET 全部区服接口
    接口: POST /ninegame/server/get
    参数: gameId：交易猫里中的clientID
    """
    BASE_URL = get_jiuyou_url(enviroment)
    url = f"{BASE_URL}/ninegame/server/get"
    payload = {
        "gameId": game_id
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查 HTTP 错误

        result = response.json()
        # result = response.json().get("serverList")
        return result

    except requests.exceptions.RequestException as e:
        return None


def push_jiuyou_server_incremental(enviroment: str, game_id: int, server_list: list):
    """
    调用 PUSH 增量区服接口
    接口: POST /ninegame/server/push
    参数: gameId, serverList (List[NineGameServerDTO])
    gameId: 交易猫里中的clientID
    serverList:列表，每个元素为NineGameServerDTO
    NineGameServerDTO格式：
    {
        "zoneName": "",
        "openServerTime": ""  # 时间戳，没有可传空值
    }
    """
    BASE_URL = get_jiuyou_url(enviroment)
    url = f"{BASE_URL}/ninegame/server/push"
    headers = {
        "Content-Type": "application/json"
    }

    # 构造 NineGameServerDTO 列表
    # 注意：openServerTime 是时间戳（毫秒），可以是 None
    payload = {
        "gameId": game_id,
        "serverList": server_list
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        return result

    except requests.exceptions.RequestException as e:
        return None



servers_to_push = [
        {
            "zoneName": "S1 武林至尊",
            "openServerTime": ""  # 毫秒时间戳
        },
        {
            "zoneName": "S23 测试测试",
            "openServerTime": ""  # 毫秒时间戳
        },
        {
            "zoneName": "S3 青云之巅",
            "openServerTime": ""  # 毫秒时间戳
        }
    ]
print(get_jiuyou_all_servers("daily",3122201))
# print(push_jiuyou_server_incremental("daily",3122201, servers_to_push))
# print(get_jiuyou_all_servers("daily",3122201))
# print(get_all_servers(88883122201))
