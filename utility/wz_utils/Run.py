from subprocess import run
from pathlib import Path
import os

id_rsa_online = "/Users/weizun/projects/adb-key/id_rsa_online"
# ip_port, private_key = "111.62.192.12:5989", id_rsa_online
adb_ip, adb_ssl_port, adb_local_port, private_key = "111.62.192.12", "5989", "15989", id_rsa_online
# adb_ip, adb_ssl_port, adb_local_port, private_key = "111.6.24.11", "5989", "15989", id_rsa_online

class RunScript:
    def __init__(self, **kwds):
        # Airtest 项目目录
        self.AIRTEST_DIR = kwds.get("AIRTEST_DIR")
        # 脚本截图输出目录
        self.LOG_DIR = kwds.get("LOG_DIR")
        # Python 解释器
        self.PYTHON = kwds.get("PYTHON")
        # ADC 项目目录
        self.ADC_SC = kwds.get("ADC_SC")
        # 源目录
        self.sourceDir = kwds.get("sourceDir")
        # 启动目录
        self.gameDir = kwds.get("gameDir")
        # 任务类型（2发布，3验号）
        self.taskType = kwds.get("taskType")
        # 运行类型（1运行，2打包）
        self.runType = kwds.get("runType")
        # 设备ID
        self.deviceId = kwds.get("deviceId")

    def __call__(self, *args, **kwargs):
        connect_cmd = ""
        isiOS = self.gameDir.startswith("ios")
        if not isiOS:
            # ip, port = ip_port.split(":")
            # adb_local_port = f"1{adb_ssl_port}"
            connect_cmd = f"""
            ssh -L {adb_local_port}:localhost:5555 root@{adb_ip} -p {adb_ssl_port} \
                -i {private_key} -Nf -o ServerAliveInterval=60 -o StrictHostKeyChecking=no \
                -o CheckHostIP=no -o UserKnownHostsFile=/dev/null
            adb connect localhost:{adb_local_port}
            """
        # """
        # ssh -L 15690:localhost:5555 root@111.62.192.12 -p 5690 \
        #     -i /Users/weizun/projects/adb-key/id_rsa_online \
        #     -Nf -o ServerAliveInterval=60 -o StrictHostKeyChecking=no \
        #     -o CheckHostIP=no -o UserKnownHostsFile=/dev/null
        # adb connect localhost:15690
        # """

        # 本地运行环境，就是把游戏目录下的localtest_config.json放在.adc下的位置
        # env_cmd = f"rm -rf {self.LOG_DIR}/* && cd {self.ADC_SC}"
        env_cmd = f"cd {self.ADC_SC}"
        if not isiOS:
            env_cmd += f"&& {self.PYTHON} local_test.py {self.gameDir} {self.taskType}"
        else:
            env_cmd += f"&& {self.PYTHON} local_test.py iOS/{self.gameDir} {self.taskType}"
        """
        localtest.py作用：读游戏目录下的localtest_config.json，根据命令行的taskType修改json数据并重新保存
        拷贝一份放在.adc下，下一步运行脚本需要用拷贝在.adc下的localtest_config.json文件
        """
        """
        cd /Users/weizun/projects/adc-sc
        python3 local_test.py 000000_common 2
        """
        # 运行脚本
        if not isiOS:
            run_cmd = f'''
            cd {self.ADC_SC}/main.air
            {self.PYTHON} -m airtest run ../main.air --device "Android:///localhost:{adb_local_port}" --log {self.LOG_DIR}
            '''
        #     python3 -m airtest run ../main.air --device "Android:///localhost:15690" --log /Users/weizun/logs
        #     python3 -m airtest run ../<xxxx>.air --device "Android:///localhost:15690" --log /Users/weizun/logs
        else:
            run_cmd = f'''
            cd {self.ADC_SC}/iOS
            {self.PYTHON} ios_main.py --device {self.deviceId} --log {self.LOG_DIR}
            '''

        """
        每个项目都需要微调，所以都需要使用这个test.ipynb文件，进行软连接，当然也可以直接复制
        """
        # test.ipynb 软链接到 sourceDir
        biz_utils_path = Path(__file__).resolve().parent / "test.ipynb"
        if biz_utils_path.exists():
            if not isiOS:
                source_utils_path = Path(self.ADC_SC).resolve() / self.sourceDir / "test.ipynb"
            else:
                source_utils_path = Path(self.ADC_SC).resolve() / "iOS" / self.sourceDir / "test.ipynb"
            if not os.path.islink(source_utils_path) or os.readlink(source_utils_path) != str(biz_utils_path):
                run(f"ln -sfn {biz_utils_path} {source_utils_path}", shell=True)

        temp = f"{connect_cmd}{env_cmd}{run_cmd}"
        print(f"temp为------------\n{temp}")
        run(f"{connect_cmd}{env_cmd}{run_cmd}", shell=True)


if __name__ == '__main__':
    # 明日方舟
    # sourceDir = gameDir = "8788_yingjiao"
    # sourceDir, gameDir = "8788_yingjiao", "8788_common"

    # 长安幻想
    # sourceDir = gameDir = "13765_shiyue"
    # sourceDir, gameDir = "13765_shiyue", "13765_common"
    # sourceDir = gameDir = "13765_qufu"

    # 最强祖师
    # sourceDir = gameDir = "15574_xingjia"
    # sourceDir, gameDir = "15574_xingjia", "15574_common"
    # sourceDir, gameDir = "15574_xingjia", "15574_jiuyou"

    # 第五人格
    # sourceDir = gameDir = "6586_common"
    # sourceDir, gameDir = "6586_common", "6586_jiuyou"
    # sourceDir, gameDir = "6586_common", "6586_oppo"
    # sourceDir = gameDir = "6586_qufu"

    # 光遇
    # sourceDir = gameDir = "10025_common"
    # sourceDir, gameDir = "10025_common", "10025_jiuyou"
    # sourceDir, gameDir = "10025_common", "10025_oppo"

    # 率土之滨
    # sourceDir = gameDir = "2717_common"
    # sourceDir, gameDir = "2717_common", "2717_jiuyou"
    # sourceDir, gameDir = "2717_common", "2717_oppo"
    # sourceDir = gameDir = "2717_qufu"

    # 三国志・战略版
    # sourceDir = gameDir = "9207_jiuyou"
    # sourceDir, gameDir = "9207_jiuyou", "9207_common"
    # sourceDir, gameDir = "9207_jiuyou", "9207_oppo"
    # sourceDir, gameDir = "9207_jiuyou", "9207_lingxi"
    # sourceDir, gameDir = "9207_jiuyou", "9207_xiyou"
    # sourceDir, gameDir = "9207_jiuyou", "9207_xiaomi"

    # 向僵尸开炮iOS
    # sourceDir = gameDir = "ios_23016_shengchang"

    # 斗罗大陆：魂师对决iOS
    # sourceDir = gameDir = "ios_11446_37shouyou"

    # TEST
    # sourceDir = gameDir = "abc_test"

    # 光遇
    # sourceDir = gameDir = "10025_common"
    # sourceDir = gameDir = "11445_qufu"

    # 黑子的篮球：街头对决
    # 得意扬帆
    # sourceDir = gameDir = "24964_common"
    # jiuyou
    # sourceDir = gameDir = "24964_jiuyou"

    # 快来当领主
    # sourceDir = gameDir = "15863_qufu"

    # 主宰世界
    # sourceDir = gameDir = "3869_qufu"

    # 造梦西游OL
    # sourceDir = gameDir = "3364_qufu"

    # 最强祖师
    # sourceDir = gameDir = "15574_qufu"

    # 仙遇
    # sourceDir = gameDir = "24048_qufu"

    # 烈焰觉醒
    # sourceDir = gameDir = "25115_common"
    # sourceDir = "25115_common"
    # gameDir = "25115_jiuyou"
    # gameDir = "25115_oppo"
    # gameDir = "25115_xiaomi"
    sourceDir = gameDir = "25115_qufu"
    # 烈焰觉醒jiuyou
    # sourceDir = gameDir = "88883122201_jiuyou"

    # 三国群英传：策定九州
    # sourceDir = gameDir = "88883112738_jiuyou"

    RunScript(
        # 这个参数没用了
        AIRTEST_DIR="/Users/weizun/test.air",
        LOG_DIR="/Users/weizun/logs",
        PYTHON="python3",
        ADC_SC="/Users/weizun/projects/adc-sc",
        sourceDir=sourceDir,
        gameDir=gameDir,
        # deviceId = "273901279d122fd9643566e4d655c8bdc5eaf5e1",   # 手机1
        # deviceId = "225359eee8648d4de359d99cd6e851f37e793b95",   # 手机3
        # deviceId = "3096e342b7f777b174423617c8641eef00d6f5ac",   # 手机4
        # deviceId = "c37c415e978388919c3602602b89f511b71b3949",   # 手机5
        # deviceId = "a3996ce27930443356b5a57fd60c95859575cf1e",   # 手机6
        deviceId = "46d6a589051fdac053f0f1f756f0506c312a4a68",   # 手机7
        # 任务类型（2发布，3验号，20验证码登录，21三战孔明锁，1000区服更新）
        # taskType=2,
        taskType=1000,
    )()
