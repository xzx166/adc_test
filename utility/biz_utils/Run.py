import datetime
import re
from subprocess import Popen, run, PIPE
from pathlib import Path
import os

timeNowStr = lambda: datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

id_rsa_1 = "/Users/vip/aic-jymadc-keypair-test/id_rsa_1"
id_rsa_2 = "/Users/vip/aic-jymadc-keypair-test/id_rsa_2"

# ip_port, private_key = "111.62.192.12:5690", id_rsa_1
ip_port, private_key = "111.62.192.12:5647", id_rsa_1
# ip_port, private_key = "111.6.24.11:5999", id_rsa_1
# ip_port, private_key = "111.62.192.12:5719", id_rsa_1  # 抖音达人
# ip_port, private_key = "120.232.194.43:10078", id_rsa_2  # Dome
# ip_port, private_key = "111.62.192.12:5910", id_rsa_1  # Dome

class RunScript:
    def __init__(self, **kwds):
        # Airtest 项目目录
        # 脚本截图输出目录
        self.LOG_DIR = kwds.get("LOG_DIR")
        # Python 解释器
        self.PYTHON = kwds.get("PYTHON")
        # ADC 项目目录
        self.ADC_SC = kwds.get("ADC_SC")
        # 主目录
        self.mainDir = kwds.get("mainDir")
        # 启动目录
        self.gameDir = kwds.get("gameDir")
        # 任务类型（2发布，3验号）
        self.taskType = kwds.get("taskType")
        # 设备ID
        self.deviceId = kwds.get("deviceId", "")

    def __call__(self, *args, **kwargs):
        local_port = connect_cmd = ""

        if self.deviceId.startswith("iOS"):
            isiOS = False
            isiOSCloud = True
        else:
            isiOS = self.gameDir.startswith("ios")
            isiOSCloud = False
        isAndroid = not (isiOS or isiOSCloud)

        if isAndroid:
            ip, port = ip_port.split(":")
            local_port = f"1{port[-4:]}"
            connect_cmd = f"""
            ssh -L {local_port}:localhost:5555 root@{ip} -p {port} \
            -i {private_key} -Nf -o ServerAliveInterval=60 -o StrictHostKeyChecking=no \
            -o CheckHostIP=no -o UserKnownHostsFile=/dev/null
            adb connect localhost:{local_port}
            """

        # 本地运行环境
        env_cmd = f"rm -rf {self.LOG_DIR}/* && cd {self.ADC_SC}"
        # env_cmd = f"cd {self.ADC_SC}"
        if isiOS or isiOSCloud:
            env_cmd += f"&& {self.PYTHON} local_test.py iOS/{self.gameDir} {self.taskType}"
        else:
            env_cmd += f"&& {self.PYTHON} local_test.py {self.gameDir} {self.taskType}"

        # 运行脚本
        if isAndroid:
            run_cmd = f'''
            cd {self.ADC_SC}/main.air
            {self.PYTHON} -m airtest run ../main.air --device "Android:///localhost:{local_port}" --log {self.LOG_DIR}
            '''
            # {self.PYTHON} -m airtest run ../main.air --device "Android:///192.168.50.154:46143" --log {self.LOG_DIR}
        else:
            run_cmd = f'''
            cd {self.ADC_SC}/iOS
            {self.PYTHON} ios_main.py --device {self.deviceId} --log {self.LOG_DIR}
            '''

        # biz_test.ipynb 软链接到 mainDir
        biz_utils_path = Path(__file__).resolve().parent / "biz_test.ipynb"
        if biz_utils_path.exists():
            if isAndroid:
                source_utils_path = Path(self.ADC_SC).resolve() / self.mainDir / "biz_test.ipynb"
            else:
                source_utils_path = Path(self.ADC_SC).resolve() / "iOS" / self.mainDir / "biz_test.ipynb"
            if not os.path.islink(source_utils_path) or os.readlink(source_utils_path) != str(biz_utils_path):
                run(f"ln -sfn {biz_utils_path} {source_utils_path}", shell=True)

        # print(f"{connect_cmd}{env_cmd}{run_cmd}")
        run(f"{connect_cmd}{env_cmd}{run_cmd}", shell=True)
        # run(f"{env_cmd}{run_cmd}", shell=True)

        # filename = Path(self.LOG_DIR).resolve() / f".sh"
        # filename.write_text(f"{connect_cmd}{env_cmd}{run_cmd}")
        # filename.chmod(0o700)
        # Popen(['/System/Applications/Utilities/Terminal.app/Contents/MacOS/Terminal', filename])


if __name__ == '__main__':
    # 明日方舟
    # mainDir = gameDir = "8788_yingjiao"
    # mainDir, gameDir = "8788_yingjiao", "8788_common"

    # 长安幻想
    # mainDir = gameDir = "13765_shiyue"
    # mainDir, gameDir = "13765_shiyue", "13765_common"
    # mainDir = gameDir = "13765_qufu"

    # 最强祖师
    # mainDir = gameDir = "15574_xingjia"
    # mainDir, gameDir = "15574_xingjia", "15574_common"
    # mainDir, gameDir = "15574_xingjia", "15574_jiuyou"

    # 第五人格
    # mainDir = gameDir = "6586_common"
    # mainDir, gameDir = "6586_common", "6586_jiuyou"
    # mainDir = gameDir = "6586_qufu"

    # 光遇
    # mainDir = gameDir = "10025_common"
    # mainDir, gameDir = "10025_common", "10025_jiuyou"

    # 率土之滨
    # mainDir = gameDir = "2717_common"
    # mainDir, gameDir = "2717_common", "2717_jiuyou"
    # mainDir = gameDir = "2717_qufu"

    # 三国志・战略版
    # mainDir = gameDir = "9207_jiuyou"
    # mainDir, gameDir = "9207_jiuyou", "9207_common"
    # mainDir, gameDir = "9207_jiuyou", "9207_oppo"
    # mainDir, gameDir = "9207_jiuyou", "9207_lingxi"
    # mainDir, gameDir = "9207_jiuyou", "9207_xiyou"
    # mainDir, gameDir = "9207_jiuyou", "9207_xiaomi"

    # 斗罗大陆：魂师对决iOS
    # mainDir = gameDir = "ios_11446_37shouyou"
    # mainDir = gameDir = "ios_11446_qufu"

    # 伊瑟
    # mainDir = gameDir = "25398_common"

    # 抖音话题
    # mainDir = gameDir = "9999013_qufu"

    # 快手话题
    # mainDir = gameDir = "9999017_qufu"

    # 抖音达人
    # mainDir = gameDir = "9999018_qufu"

    # 绝地求生PUBG-PC
    mainDir = gameDir = "5799_steam"

    # 向僵尸开炮iOS
    # mainDir = gameDir = "ios_23016_shengchang"
    # mainDir = gameDir = "ios_23016_qufu"

    # 烈焰觉醒
    # mainDir = gameDir = "25115_qufu"

    # 王者荣耀混采
    # mainDir = gameDir = "2416_common"

    # 测试
    # mainDir = gameDir = "abc_test"

    RunScript(
        LOG_DIR=f"~/logs",
        PYTHON="python3",
        ADC_SC="/Users/vip/adc-sc",
        mainDir=mainDir,
        gameDir=gameDir,
        # deviceId = "iOS:///http://220.176.196.253:15078",  # 电信 iOS 设备1 串流 15054
        # deviceId = "iOS:///http://113.195.134.221:15078",  # 联通 iOS 设备1 串流 15054
        # deviceId = "iOS:///http://220.176.196.253:15118",  # 电信 iOS 设备2 串流 15094
        # deviceId = "iOS:///http://113.195.134.221:15118",  # 联通 iOS 设备2 串流 15094
        # 任务类型（2发布，3验号，20验证码登录，21三战孔明锁，1000区服更新）
        taskType=1000 if "qufu" in gameDir else 2
    )()
