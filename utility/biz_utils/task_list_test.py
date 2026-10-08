import requests
import datetime
from time import sleep
from subprocess import Popen
import json
from pathlib import Path

session = requests.session()
session.verify = False
requests.packages.urllib3.disable_warnings() # type: ignore

gameid_list = ["10025", "2717"]

def get_task_list():
    url = "https://adc-pc.alibaba-inc.com/task/getList"
    gameId = gameid_list.pop(0)
    gameid_list.append(gameId)
    payload = {
        "current": 1,
        "game_id": gameId,
        # "game_platform": "jiuyou",
        "pageSize": 100,
    }
    response = session.post(url, json=payload)
    task_list = response.json()["result"]["data"]["content"]
    timeNowStr = now_time.strftime('%Y-%-m-%-d %-H:%M:%S')
    print("check", timeNowStr, gameId)
    return task_list

def get_task_status(task_id):
    url = f"https://adc-pc.alibaba-inc.com/task/getTaskStatus?taskId={task_id}"
    response = session.get(url)
    ret = response.json()
    for i in ret["data"]:
        if i["status"] == 4:
            last_status = i["data"][-1]
            title = last_status["title"]
            desc = last_status["description"]
            if title == "黑边检测" and desc == "设备黑边":
                return True

if __name__ == "__main__":
    print("开始运行")
    is_runing = 1
    task_id_list = []
    while is_runing:
        now_time = datetime.datetime.now()
        for task in get_task_list():
            if task["task_status"] == 4:
                task_id = task["id"]
                platform = task["game_platform"]
                account_attr = json.loads(task["account_attr"])
                task_time = datetime.datetime.fromtimestamp(int(task["callback_timestamp"] / 10 ** 3))
                if now_time - task_time >= datetime.timedelta(minutes=1) and \
                    get_task_status(task_id):
                    text = f"黑边 {task_id}"
                    task_id_list.append(text)
                    is_runing = 0

        if is_runing:
            sleep(1 * 60)

    if not is_runing:
        for i in task_id_list:
            print(i)
        Popen(['afplay', "/Users/vip/Music/DNF.mp3"])
        sleep(20)
        Popen(["killall", "afplay"])
