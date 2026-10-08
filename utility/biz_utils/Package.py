from subprocess import run, call, Popen
from pathlib import Path
import os
import datetime


ZIP_DIR = Path.home().resolve()
ADC_SC = f"{ZIP_DIR}/adc-sc"

games_list = [
    {
        "gameName": "明日方舟",
        "gameId": "8788",
        "mainDir": "yingjiao",
        "platform": [
            "yingjiao",
            "common",
        ]
    },
    {
        "gameName": "长安幻想",
        "gameId": "13765",
        "mainDir": "shiyue",
        "platform": [
            "shiyue",
            "common",
            # "qufu",
        ]
    },
    {
        "gameName": "最强祖师",
        "gameId": "15574",
        "mainDir": "xingjia",
        "platform": [
            "xingjia",
            "common",
        ]
    },
    {
        "gameName": "第五人格",
        "gameId": "6586",
        "mainDir": "common",
        "platform": [
            "common",
            "jiuyou",
            "oppo"
        ]
    },
    {
        "gameName": "光·遇",
        "gameId": "10025",
        "mainDir": "common",
        "platform": [
            "common",
            "jiuyou",
        ]
    },
    {
        "gameName": "率土之滨",
        "gameId": "2717",
        "mainDir": "common",
        "platform": [
            "common",
            "jiuyou",
            # "qufu",
        ]
    },
    {
        "gameName": "三国志·战略版",
        "gameId": "9207",
        "mainDir": "jiuyou",
        "platform": [
            "common",
            "jiuyou",
            "xiyou",
            "oppo",
            "lingxi",
            "xiaomi",
        ]
    },
    {
        "gameName": "向僵尸开炮iOS",
        "gameId": "ios_23016",
        "mainDir": "shengchang",
        "platform": [
            "shengchang",
            "common"
            # "qufu",
        ]
    },
    {
        "gameName": "斗罗大陆：魂师对决iOS",
        "gameId": "ios_11446",
        "mainDir": "37shouyou",
        "platform": [
            "37shouyou",
            "qufu",
        ]
    },
    {
        "gameName": "伊瑟",
        "gameId": "25398",
        "mainDir": "common",
        "platform": [
            "common",
            # "qufu",
        ]
    },
    {
        "gameName": "话题采集",
        "gameId": "9999013",
        "mainDir": "qufu",
        "platform": [
            "qufu",
        ]
    },
    {
        "gameName": "话题采集",
        "gameId": "9999017",
        "mainDir": "qufu",
        "platform": [
            "qufu",
        ]
    },
    {
        "gameName": "抖音达人",
        "gameId": "9999018",
        "mainDir": "qufu",
        "platform": [
            "qufu",
        ]
    },
    {
        "gameName": "绝地求生PUBG-PC",
        "gameId": "5799",
        "mainDir": "steam",
        "platform": [
            "steam",
        ]
    },
    {
        "gameName": "王者荣耀",
        "gameId": "2416",
        "mainDir": "common",
        "platform": [
            "common",
        ]
    },
    {
        "gameName": "烈焰觉醒",
        "gameId": "25115",
        "mainDir": "common",
        "platform": [
            "common",
        ]
    }
]
scriptPackaging_cmd = [f"touch {ZIP_DIR}/0.zip && rm {ZIP_DIR}/*.zip && cd {ADC_SC}"]
for game in games_list:
    if game["gameName"] in [
        # "明日方舟",
        # "长安幻想",
        # "最强祖师",
        # "第五人格",
        # "光·遇",
        # "率土之滨",
        # "三国志·战略版",
        # "斗罗大陆：魂师对决iOS",
        # "伊瑟",
        # "话题采集",
        # "抖音达人",
        # "向僵尸开炮iOS",
        "绝地求生PUBG-PC",
        # "王者荣耀",
        # "烈焰觉醒"
    ]:
        pkgsh = "./zip_ios_pkg.sh" if game["gameId"].startswith("ios") else "./zip_pkg.sh"
        for gameDir in game["platform"]:
            # if gameDir != "jiuyou":
            #     continue
            cmd_item = f"&& {pkgsh} {game['gameId']}_{gameDir} "
            if gameDir not in [game["mainDir"], "qufu"]:
                cmd_item += f"{game['gameId']}_{game['mainDir']}"
            scriptPackaging_cmd.append(cmd_item)

timeNowStr = lambda: datetime.datetime.now().strftime('%Y-%-m-%-d %-H:%M:%S')
print(cmd := " ".join(scriptPackaging_cmd))
run(cmd, shell=True)
print(f"打包时间：{timeNowStr()}")
