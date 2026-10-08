from subprocess import run, call, Popen
from pathlib import Path
import os
import datetime

timeNow = lambda: datetime.datetime.now().strftime('%Y-%-m-%-d %-H:%M:%S')

ZIP_DIR = "~"
ADC_SC = "~/projects/adc-sc"

games_list = [
    # {
    #     "gameName": "主宰世界",
    #     "gameId": "3869",
    #     "sourceDir": "qufu",
    #     "gameDirs": [
    #         "qufu",
    #     ]
    # },
    # {
    #     "gameName": "造梦西游OL",
    #     "gameId": "3364",
    #     "sourceDir": "qufu",
    #     "gameDirs": [
    #         "qufu",
    #     ]
    # },
    # {
    #     "gameName": "最强祖师",
    #     "gameId": "15574",
    #     "sourceDir": "qufu",
    #     "gameDirs": [
    #         "qufu",
    #     ]
    # },
    # {
    #     "gameName": "仙遇",
    #     "gameId": "24048",
    #     "sourceDir": "qufu",
    #     "gameDirs": [
    #         "qufu",
    #     ]
    # },
    # {
    #     "gameName": "黑子的篮球：街头对决",
    #     "gameId": "24964",
    #     "sourceDir": "common",
    #     "gameDirs": [
    #         # "hypergryph",
    #         "jiuyou",
    #         "common",
    #     ]
    # },
    {
        "gameName": "烈焰觉醒",
        "gameId": "25115",
        "sourceDir": "common",
        "gameDirs": [
            # "common",
            # "jiuyou",
            # "oppo",
            "xiaomi",
        ]
    },
    # {
    #     "gameName": "烈焰觉醒",
    #     "gameId": "25115",
    #     "sourceDir": "qufu",
    #     "gameDirs": [
    #         "qufu",
    #     ]
    # },
    # {
    #     "gameName": "烈焰觉醒",
    #     "gameId": "88883122201",
    #     "sourceDir": "jiuyou",
    #     "gameDirs": [
    #         "jiuyou",
    #     ]
    # },
    {
        "gameName": "三国群英传：策定九州",
        "gameId": "88883112738",
        "sourceDir": "jiuyou",
        "gameDirs": [
            "jiuyou",
        ]
    }
]
scriptPackaging_cmd = [f"touch {ZIP_DIR}/0.zip && rm {ZIP_DIR}/*.zip && cd {ADC_SC}"]
for game in games_list:
    if game["gameName"] in [
        "烈焰觉醒",
    ]:
        pkgsh = "./zip_ios_pkg.sh" if game["gameId"].startswith("ios") else "./zip_pkg.sh"
        for gameDir in game["gameDirs"]:
            cmd_item = f"&& {pkgsh} {game['gameId']}_{gameDir} "
            if gameDir not in [game["sourceDir"], "qufu"]:
                cmd_item += f"{game['gameId']}_{game['sourceDir']}"
            scriptPackaging_cmd.append(cmd_item)

print(cmd := " ".join(scriptPackaging_cmd))
run(cmd, shell=True)
print(f"打包时间：{timeNow()}")
