import os
from pathlib import Path

from pandas.core.roperator import rsub
from xxlimited import Xxo

os.environ.update(
    indexDir=str(Path(__file__).resolve().parent),
    screenRotation="H",
    # poco_enable="true",
    gameName="永劫无间-PC",
    # packageName_test="",
    # platform_test="",
)
from utility.biz_utils.biz_utils import *

timer = 0
cover_images = []
properties_simple_global = {}

propertiesUpdateTemplates = {}
json_path = gameDir / "propertiesUpdateTemplates.json"
if json_path.exists():
    json_data = json.loads(json_path.read_text())
    for property_item in json_data:
        propertiesUpdateTemplates[property_item["propertyName"]] = property_item
# -------------------------------------------------------


home_pc_url = "https://cg-paas-test.aligames.com/h5demo/test-mobile-pc/#/cloudgame?gameId=2008953&gamePlatformType=1&isRandomUt=true&isRelease=true"
weapon_category_map = {}
mask = [(40,1187,580,1310),(1770,20,1935,70)]
all_shizhuang_red_pifu_list=[]
all_wuqi_red_pifu_list=[]
all_shizhuang_gold_pifu_list=[]
all_wuqi_gold_pifu_list=[]
weapons = {
    "近战": [
        "长剑",
        "太刀",
        "阔刀",
        "斩马刀",
        "棍",
        "匕首",
        "扇",
        "枪",
        "万刃轮",
        "双节棍",
        "双刀",
        "横刀",
        "双戟",
        "拳刃",
        "飞刀",
        "链剑"
    ],
    "远程": [
        "弓箭",
        "连弩",
        "鸟铳",
        "火炮",
        "五眼铳",
        "一窝蜂",
        "喷火筒",
        "双铳"
    ]
}
hero_dict=[
    {"名称": "",
     "英雄": "",
     "稀有度": "",
     "属性图片":"",
     "名称图片":""
    },
    {"名称": "",
     "英雄": "",
     "稀有度": "",
     "属性图片":"",
     "名称图片":""
    },
]
# 采集到的数据
gather_info = {
    "红皮数": "",
    "金皮数": "",
    "角色等级": "",
    "幻丝数": "",
    "总收藏值": "",
    "英雄皮肤数": "",
    "武器皮肤数": "",
    "三排段位": "",
    "通行证":"",
    "服装":"",
    "武器皮肤":"",
    "发型":"",
    "变身器": "",
}
def format_image(image_a,image_b):
    # 确保两张图通道数一致（都转为 RGBA）
    if isinstance(image_a, np.ndarray):
        if image_a.shape[-1] == 3:
            image_a = cv2.cvtColor(image_a, cv2.COLOR_RGB2RGBA)

    if isinstance(image_b, np.ndarray):
        if image_b.shape[-1] == 3:
            image_b = cv2.cvtColor(image_b, cv2.COLOR_RGB2RGBA)
    return image_a,image_b
def add_red_and_gold_wuqi_pifu(images_red,images_gold):

    for red_pifu in images_red:
        pifu_dict={}
        pifu_dict["属性图片"] = red_pifu["属性图片"]
        pifu_dict["名称"] = red_pifu["名称"]
        pifu_dict["品质"] = "红"
        all_wuqi_red_pifu_list.append(pifu_dict)
    for gold_pifu in images_gold:
        pifu_dict={}
        pifu_dict["属性图片"] = gold_pifu["属性图片"]
        pifu_dict["名称"] = gold_pifu["名称"]
        pifu_dict["品质"] = "金"
        all_wuqi_gold_pifu_list.append(pifu_dict)

def add_red_and_gold_fuzhuang_pifu(images_red,images_gold):
    for red_pifu in images_red:
        pifu_dict={}
        pifu_dict["属性图片"] = red_pifu["属性图片"]
        pifu_dict["名称"] = red_pifu["名称"]
        pifu_dict["稀有度"] = "红"
        all_shizhuang_red_pifu_list.append(pifu_dict)
    for gold_pifu in images_gold:
        pifu_dict={}
        pifu_dict["属性图片"] = gold_pifu["属性图片"]
        pifu_dict["名称"] = gold_pifu["名称"]
        pifu_dict["稀有度"] = "金"
        all_shizhuang_gold_pifu_list.append(pifu_dict)
# 状态检查
def check_status(title="", desc="", image=None, raise_ex=True):
    if not isinstance(image, np.ndarray):
        image = snapshot_write()

    # 踢号检测
    # if find_tpl("tpl20260315005544.png", image=image, desc="踢号检测1") or \
    #     find_tpl("tpl20260306003920.png", image=image, desc="踢号检测2"):
    #     property_del("enteredGame")
    #     monitor_catch("状态检查", f"被踢掉登录账户（{platform}）", status=10010, break_mode=BreakModeEnum.app)


    if raise_ex:
        monitor_catch(title, desc, status=10130, break_mode=BreakModeEnum.app, image=image)

    elif title:
        monitor_catch(title, desc, image=image)

class PopupHandler:
    def __init__(self, template_paths=None):
        # 默认模板路径列表
        if template_paths is None:
           template_paths = [
               "tpl20260327101450.png",
               "tpl20260316095222.png",
                "tpl20260309105410.png",
                "tpl20260311113948.png",
               "tpl20260312151925.png",
               "tpl20260312152309.png",
               "tpl165165156.png",
               "tpl20260320095632.png"

            ]
        self.template_paths = template_paths
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            image = snapshot_write()
            start_time = time.time()
            for _ in range(8):
                loop_break = True
                if find_tpl("tpl20260327101450.png", image=image):
                    monitor_catch("状态检查", f"被踢掉登录账户（{platform}）", status=10010, break_mode=BreakModeEnum.app)
                if find_tpl("tpl20260312102901.png", image=image):
                    result = snapshot_ocr(LT=(888, 590), RB=(1535, 715), image=image)
                    if "服务器将于" in result:
                        monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
                if find_tpl("tpl125478855220.png", image=image,threshold=0.7,desc="游戏热更新",catch= True) or find_tpl("tpl112345677878.png", image=image,threshold=0.7,desc="游戏热更新",catch= True):
                    monitor_catch("游戏热更新中")
                    sleep(60)
                    if time.time() - start_time > 420:
                        monitor_catch("状态检查", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
                    continue
                for template_path in self.template_paths:
                    if find_tpl_touch(template_path, image=image,area=area_rb):
                        image = snapshot_write()
                        loop_break = False
                        continue
                if loop_break:
                    break
                sleep(0.5)
            return func(*args, **kwargs)
        return wrapper
def gameClose():
    """关闭游戏"""
    stage = int(ENV.get_common_property_with_key('captchaTaskStatus')) if taskType == 20 else 0
    if stage == 1 or localRun:
        monitor_task_status_v2("关闭所有应用", "开始")
        kill_all_activity()

def gameLaunch():
    """启动游戏"""
    stage = int(ENV.get_common_property_with_key('captchaTaskStatus')) if taskType == 20 else 0
    # 验证码发布
    if taskType == 20 and stage == 1:
        game_dashen_launch()
        phone_captcha_send_captcha(1, need_captcha=True)
        lx_break_app(ext_info={'key': '200'}, desc='需要手机验证码', hold_game=True)
        return
    if taskType == 20 and stage == 2:
        game_dashen_launch()
        monitor_catch("启动Pc游戏(验证码发布)", "开始",catch= True)
        game_qq_launch()
        phone_captcha_verify_captcha(1)
        lx_break_app(ext_info={'key': '200'}, desc='登录成功', hold_game=True)
        return

    if taskType == 20 and stage == 3 or localRun:
        # stage = int(ENV.get_common_property_with_key('captchaTaskStatus'))
        if stage == 3 or localRun:
            monitor_task_status_v2("启动PC游戏(验证码发布)", "开始")
            url = "https://cg-paas-test.aligames.com/h5demo/test-mobile-pc/#/cloudgame?gameId=2008953&gamePlatformType=1&isRandomUt=true&isRelease=true"
            if localRun:
                connectPCDeviceByQQBrowser(url)
            else:
                connectPCDevice(url)
    # 普通发布
    elif taskType != 20:
        monitor_catch("启动PC游戏(普通发布)", "开始")
        if scheduledId := ENV_ATTR.get("CLOUD_GAME_PC_SCHEDULE_ID"):
            url = f"https://cg-paas-test.aligames.com/h5demo/test-mobile-pc/#/cloudgame?gameId=2008953&gamePlatformType=1&isRelease=true&scheduledId={scheduledId}"
        else:
            url = "https://cg-paas-test.aligames.com/h5demo/test-mobile-pc/#/cloudgame?gameId=2008953&gamePlatformType=1&isRandomUt=true&isRelease=true"
        connectPCDevice(url)
    fix_black_edge()
    monitor_catch("开始启动游戏",catch= True)

    # 属性信息清理
    property_clear()
    cover_images.clear()
    sleep(10)
    if taskType == 20 or localRun:
        stage = int(ENV.get_common_property_with_key('captchaTaskStatus'))
        if stage == 3 or localRun:
            image = snapshot_write()
            if find_tpl("tpl20260324094851.png",image=image):
                monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
            if find_tpl("tpl20260416105258.png",image=image,area=area_rb):
                monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
            for i in range(15):
                image = snapshot_write()
                if find_tpl_touch("tpl20260319135634.png",image=image,area=(1480,890, 1800, 985)):
                    monitor_catch(f"状态启动游戏按钮", "点击游戏启动")
                if find_tpl("tpl20260327215342.png",image=image,area=(1480,890, 1800, 985)):
                    monitor_catch(f"状态检测", "游戏更新等30s")
                    sleep(30)
                if find_tpl("tpl20260416105258.png", image=image, area=area_rb, threshold=0.7):
                    monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
                if "启动" in snapshot_ocr(LT=(1480,890), RB=(1800, 985), image=image):
                    monitor_catch(f"点击启动按钮", "点击游戏启动2")
                    air_touch((1645,940))
                sleep(1)
            for i in range(6):
                if find_tpl("tpl20260319140324.png",image=snapshot_write(),area=(950,460, 1520, 935)):
                    monitor_catch("启动游戏状态", "游戏启动中30s")
                    sleep(10)
                if find_tpl("tpl1232131232144.png", image=snapshot_write(), area=(1020, 300, 1500, 700)):
                    monitor_catch("进入游戏了", "进入游戏了")
                    air_touch((1200, 1120))
                    return
                sleep(1)

    else:
        image = snapshot_write()
        if find_tpl("tpl20260324094851.png", image=image):
            monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
        if find_tpl("tpl20260416105258.png", image=image, area=area_rb, threshold=0.7):
            monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
        for i in range(15):
            image = snapshot_write()
            if find_tpl_touch("tpl20260319135634.png", image=image, area=(1480,890, 1800, 985)):
                monitor_catch(f"状态启动游戏按钮", "点击游戏启动")
            if find_tpl("tpl20260327215342.png", image=image, area=(1480,890, 1800, 985)):
                monitor_catch(f"状态检测", "游戏更新等30s")
                sleep(30)
            if find_tpl("tpl20260416105258.png", image=image, area=area_rb, threshold=0.7):
                monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
            if "启动" in snapshot_ocr(LT=(1480,890), RB=(1800, 985), image=image):
                monitor_catch(f"点击启动按钮", "点击游戏启动2")
                air_touch((1645, 940))
            sleep(1)
        for i in range(6):
            if find_tpl("tpl20260319140324.png", image=snapshot_write(), area=(950,460, 1520, 935)):
                monitor_catch("启动游戏状态", "游戏启动中30s")
                sleep(10)
            if find_tpl("tpl1232131232144.png", image=snapshot_write(),area=(1020,300, 1500, 700)):
                monitor_catch("进入游戏了", "进入游戏了")
                air_touch((1200,1120))
                return
            sleep(1)
    image = snapshot_write()
    if find_tpl("tpl20260327215342.png", image=image, area=(1480,890, 1800, 985)):
        monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
    if find_tpl("tpl20260416105258.png", image=image, area=area_rb, threshold=0.7):
        monitor_catch(f"状态检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=image)
class EnterGame():
    def __call__(self):
        self.huadong_touch()
        self.open_game_launch()
        # self.guanbi_shejiao()
    def __init__(self):
        self.shejiao_lis=[(750,375),(750,485),(750,590),(750,700),(750,915),(750,1130)]
    def guanbi_shejiao(self):
        air_touch((2355, 40))
        find_tpl_touch("tpl20260311160141.png", title="关闭社交", desc="进入按键设置", catch=True)
        air_touch((830, 45))
        for i in self.shejiao_lis:
            for j in range(3):
                air_touch(i)
                sleep(0.5)
    def huadong_touch(self):
        if find_tpl("tpl20260326095815.png",area=(815,435,1585,905)):
            monitor_catch(f"状态检测", "检测到未实名认证，结束", break_mode=BreakModeEnum.app, status=10101, image=snapshot_write())
        for i in range(3):
            if find_tpl("tpl20260309155602.png", title="进入游戏", desc="接受服务条款", catch=True):
                air_swipe_fast((1844,470), end_point=(1844,1000),sec=0.2)
                sleep(1)
                air_swipe_fast((1844,900), end_point=(1844,1100),sec=0.2)
            if find_tpl("tpl20260326204452.png", title="进入游戏", desc="滑动接受服务条款"):
                break
        find_tpl_touch("tpl20260326204452.png", title="进入游戏", desc="点击接受服务条款", catch=True)
        air_touch((1844,1000))
    def open_game_launch(self):
        """启动游戏"""
        sleep(60)
        loop_break= True
        image = snapshot_write()
        for _ in range(10):
            if find_tpl("tpl20260319111207.png", image=image):
                monitor_catch(f"状态检测", "密码错误", break_mode=BreakModeEnum.app, status=10008, image=image)
            if find_tpl("tpl20260326095815.png", image=image):
                monitor_catch(f"状态检测", "检测到未实名认证，结束", break_mode=BreakModeEnum.app, status=10101, image=image)
            if find_tpl("tpl20260408113616.png", image=image,threshold=0.7):
                monitor_catch(f"账号登录异常", "账号登录异常需要手机短信验证", break_mode=BreakModeEnum.app, status=10116, image=image)
            if find_tpl("tpl1122547885202.png", image=image,threshold=0.7):
                monitor_catch(f"账号登录异常", "账号登录异常需要手机短信验证", break_mode=BreakModeEnum.app, status=10116, image=image)
            if find_tpl("tpl3322554111.png", image=image,threshold=0.7):
                monitor_catch("解除将军令-远程超时-远程",break_mode=BreakModeEnum.app, status=10224, image=image)
            if find_tpl("tpl1112335566.png", image=image, threshold=0.7):
                monitor_catch(f"状态检测", "卖家手机号待验证", break_mode=BreakModeEnum.app, status=10103, image=image)
            if find_tpl_touch("tpl20260309105010.png", image=image):
                image = snapshot_write()
                loop_break = False
            if find_tpl_touch("tpl20260309105410.png", image=image,area=area_rb):
                image = snapshot_write()
                loop_break = False
            if find_tpl_touch("tpl165165156.png", image=image,area=area_rb):
                image = snapshot_write()
                loop_break = False
            if find_tpl_touch("tpl20260312151925.png", image=image):
                image = snapshot_write()
                loop_break = False
            if find_tpl_touch("tpl20260312152309.png", image=image,area=area_rb,threshold=0.65):
                image = snapshot_write()
                loop_break = False
            if find_tpl_touch("tpl20260309105410.png", image=image,area=area_rb,threshold=0.65):
                image = snapshot_write()
                loop_break = False
            if find_tpl_touch("tpl20260323195937.png",image=image):
                image = snapshot_write()
                loop_break = False
            if loop_break:
                break
        monitor_task_status_v2("开始采集PC游戏", "开始")



def check_account_type(account):
    """
    判断账号类型：手机号或邮箱
    :param account: 账号字符串
    :return: "email" 或 "phone"
    :raises ValueError: 当输入不是有效的手机号或邮箱时
    """


    if "@" in account and "." in account.split("@")[-1]:
        return "email"

    else:
        return "phone"

class GameLogin:
    """ 登录"""
    def __init__(self):
        self. WindowArea = (975, 375, 1430, 980)
        self.username = ENV.username
        self.password = ENV.password
        self.captchaCode = ENV.smsCode
        self.stage = int(ENV.get_common_property_with_key('captchaTaskStatus')) if taskType == 20 else 0
        self.captchaTaskRetryCount = int(ENV.get_common_property_with_key('captchaTaskRetryCount'))
        self.stageMap = {1: "一", 2: "二", 3: "三"}
        self.title = ""

    def __call__(self, *args, **kwargs):

        if localRun:
            self.username = "adc1"

        if localRun or isPre:
            if self.username.startswith("adc1"):
                # 令牌验证
                self.username = "m13384267772@163.com"
                self.password = "Sb13703999553"

            elif self.username.startswith("adc2"):
                # 令牌验证
                self.username = "18203657629"
                self.password = "p9GeD5nU"

            elif self.username.startswith("adc3"):
                # 无验证
                self.username = "rigg4127"
                self.password = "r5BgY8Pj"

            elif self.username.startswith("adc4"):
                # 无验证
                self.username = "kw667132"
                self.password = "afx66350"

            elif self.username.startswith("jym1"):
                # 邮箱验证
                self.username = "pk0ng6nl7nw3"
                self.password = "a7QbD5eG"

            elif self.username.startswith("jym2"):
                # 无验证
                self.username = "jm4cx6as4fu9"
                self.password = "e7MuF5rs"

        if (localRun or isPre) and self.stage == 1:
            monitor_task_status_v2(" 登录一阶段", f"账号: {self.username}, 密码: {self.password}")

        if localRun:
            ENV.taskType = 20
            self.stage =3
            self.captchaCode = "375892"
        self.processLogin()


    def fengkong_shibie(self):
        sleep(10)
        image = snapshot_write()
        for i in range(3):
            if (find_tpl("tpl20260319143157.png", image=image) or find_tpl("tpl20260319143405.png", image=image)
                    or find_tpl("tpl20260323142714.png", image=image)) or find_tpl("tpl20260326200533.png", image=image):
                monitor_catch("解除将军令-远程超时-远程",break_mode=BreakModeEnum.app, status=10224, image=image)
            if find_tpl("tpl20260323143414.png",image=image):
                monitor_catch("登录成功")
                return True
            sleep(5)
            return  False

    def preLoginCheck(self):
        """登录前预处理"""
        for i in range(10):
            if find_tpl_touch("tpl20260319140557.png", image=snapshot_write()):
                monitor_catch("准备登录")
            if find_tpl("tpl20260327120627.png",threshold=0.7):
                air_touch((1220,1058))
                monitor_catch("准备登录222")
                sleep(2)
            if find_tpl("tpl20260318231019.png", title="开始登录", desc="已进入登录界面1"):
                return
            # if find_tpl("tpl20260326200533.png",image=snapshot_write()):
            #     monitor_catch("解除将军令-远程超时-远程", break_mode=BreakModeEnum.app, status=10224, image=snapshot_write())
            sleep(5)

    def firstStage(self, retry=False):
        """一阶段: 开始登录"""
        # 正则判断是邮箱还是手机号登录
        monitor_catch(f"开始登录,{ENV.taskType}")
        user_name = self.username
        login_type = check_account_type(user_name)
        pass_word = self.password
        monitor_catch(f"账号类型,{login_type}")
        if ENV.taskType != 20:
            if login_type == "email":
                air_touch((1100,525))
                sleep(1)
                air_touch((1055, 595), combo=10, sec=2, desc="点击账号输入框")
                adc_input(user_name)
                for i in range(5):
                    air_swipe_fast(start_point=(1195,525),end_point=(1118,563),sec=0.2)
                    sleep(0.5)
                monitor_catch("完成输入账号",catch= True)
            else:
                air_touch((1280,525))
                sleep(1)
                find_tpl_touch("tpl20260318234003.png",sec=2,desc="手机账密登录")
                for i in range(3):
                    air_touch((1175,600))
                    sleep(0.5)
                adc_input(user_name)
                monitor_catch("完成输入账号", catch=True)
            for i in range(3):
                n = random.randint(0, 3)
                air_swipe_fast(start_point=(1035 + n,670+n ), end_point=(1200 + n, 670+n), sec=0.5)
                sleep(0.5)
            adc_input(pass_word)
            monitor_catch("完成输入密码", catch=True)
        else:
            if login_type != "phone":
                monitor_catch(f"状态检测", "账密出错，账号非手机号", break_mode=BreakModeEnum.app, status=10008, image=snapshot_write())
            for i in range(3):
                if find_tpl("tpl20260330213229.png",desc="手机账密登录",area=(980,490,1410,570)):
                    find_tpl_touch("tpl20260330213229.png",sec=2,desc="手机账密登录")
                else:
                    monitor_catch("状态检测", "手机号登录界面异常", image=snapshot_write())
                shouji_result = snapshot_ocr(LT=(1220, 504), RB=(1365, 552))
                if '手机' in shouji_result:
                    air_touch((1175, 600))
                sleep(1)
            adc_input(user_name)
            for i in range(10):
                image = snapshot_write()
                if find_tpl("tpl20260318232406.png", sec=2, desc="点击确认登录", image=image,
                            area=(1035, 730, 1400, 860)):
                    n = random.randint(0, 3)
                    air_swipe_fast(start_point=(1145 + n, 795 + n), end_point=(1240 + n, 805 + n), sec=0.5)
                    monitor_catch("确认登录1")
                sleep(1)
                air_swipe_fast(start_point=(1300,666), end_point=(1350,666), sec=0.2)
                if find_tpl_touch("tpl20260322214152.png",sec=2,desc="点击确认协议",image=snapshot_write(),area=(1200, 730, 1400, 800)):
                    monitor_catch("授权协议")
                    sleep(2)
                result =snapshot_ocr(image=snapshot_write(), LT=(1235, 743), RB=(1370, 800))
                if "同意" in result :
                    air_touch((1300, 770))
                    sleep(3)
                if find_tpl("tpl20260322214532.png",sec=2,desc="验证码已发送",image=snapshot_write(),area=(1250,630, 1430, 730)):
                    phone_captcha_send_captcha(1, need_captcha=True)
                    lx_break_app(ext_info={'key': '200'}, desc='需要手机验证码', hold_game=True)
                    return
                if "已发送" in snapshot_ocr(image=snapshot_write(), LT=(1250,630), RB=(1430, 715)):
                    phone_captcha_send_captcha(1, need_captcha=True)
                    lx_break_app(ext_info={'key': '200'}, desc='需要手机验证码', hold_game=True)
                    return
                else:
                    if find_tpl("tpl20260401143745.png", sec=2, desc="验证码未发送,重发", image=snapshot_write(),
                             area=(1250, 630, 730, 1430, 715)):
                        air_touch((1320,675))
                        sleep(1)

            monitor_catch("验证码发送失败", break_mode=BreakModeEnum.app, status=10139, image=snapshot_write())
        for i in range(3):
            image = snapshot_write()
            if find_tpl("tpl20260318232406.png",sec=2,desc="点击确认登录",image=image,area=(1035,730,1400,860)):
                n = random.randint(0, 3)
                air_swipe_fast(start_point=(1145 + n, 795 + n), end_point=(1240 + n, 805 + n), sec=0.5)
                monitor_catch("确认登录1")
            sleep(1)
            image =snapshot_write()
            if find_tpl_touch("tpl20260319115449.png", sec=2, desc="点击确认协议", image=image):
                monitor_catch("确认协议1")
            if "同意" in snapshot_ocr(image=image, LT=(1245, 688), RB=(1480, 960)):
                air_touch((1317, 775))
                monitor_catch("确认协议2")
                sleep(2)
        image = snapshot_write()
        result=snapshot_ocr(image=image,LT=(1011,740),RB=(1155,760))
        if find_tpl("tpl20260319111207.png",image=image,area=(1000,730,1200,780)) or ("密码错误" in result or "错误" in result):
            monitor_catch(f"状态检测", "密码错误", break_mode=BreakModeEnum.app, status=10008, image=image)
        for i in range(3):
            result = snapshot_ocr(LT=(1055,1080),RB=(1375,1160),image=snapshot_write(),desc="点击屏幕进入游戏判断")
            if "点击" in result or "进入" in result:
                air_touch((1160,1070))
                monitor_catch(self.title, "点击进入游戏")
                return
            air_touch((1160, 1070))
            sleep(1.5)


    def secondStage(self):
        """二阶段: 输入 验证码"""

        for i in range(3):
            air_touch((1275, 530))
            sleep(1)
        for i in range(3):
            air_touch((1100, 670))
            sleep(1)
        adc_input(self.captchaCode)
        monitor_catch(self.title, f" 验证码输入后: {self.captchaCode}")
        for i in range(5):
            image = snapshot_write()
            for i in range(3):
                if find_tpl("tpl20260318232406.png", sec=2, desc="点击确认登录", image=image):
                    n = random.randint(0, 3)
                    air_swipe_fast(start_point=(1145 + n, 795 + n), end_point=(1240 + n, 805 + n), sec=0.2)
                sleep(1)
                image = snapshot_write()

                sleep(0.5)
                if find_tpl("tpl20260322222012.png", sec=1, desc="登录成功", image=image):
                    monitor_catch("进入游戏成功")
                    phone_captcha_verify_captcha(1)
                    lx_break_app(ext_info={'key': '200'}, desc='登录成功', hold_game=True)
                    return
            image = snapshot_write()
            result = snapshot_ocr(image=image, LT=(1011, 740), RB=(1155, 760))
            if find_tpl("tpl20260322213543.png", image=image) or ("密码错误" in result or "错误" in result):
                phone_captcha_verify_captcha(3)
                monitor_catch("验证码错误", raise_exception=10142, break_mode=BreakModeEnum.app, image=image)
            sleep(1.5)
            result = snapshot_ocr(LT=(1055, 1080), RB=(1375, 1160), image=snapshot_write(), desc="点击屏幕进入游戏判断")
            if "点击" in result or "进入" in result:
                air_touch((1160, 1070))
                monitor_catch(self.title, "点击进入游戏")
                phone_captcha_verify_captcha(1)
                lx_break_app(ext_info={'key': '200'}, desc='登录成功', hold_game=True)
                return


    def thirdStage(self):
        """三阶段: 登录完成"""
        for i in range(3):
            sleep(1)
            if find_tpl("tpl20260318231019.png", title="开始登录", desc="已进入登录界面5"):
                break
        for i in range(5):
            air_touch((1400, 950))
            sleep(1)
            if find_tpl("tpl20260410152849.png", title="开始登录", desc="识别到大神二维码",area=(1160, 840, 1230, 900),threshold=0.8):
                monitor_catch("进入二维码登录", catch=True)
                break


        #保存最新登录二维码图片
        _, image_path = snapshot_write(area=(980, 375, 1425, 975), write_name="登录二维码/dashendenglu.png", needPath=True)
        monitor_catch( "保存最新登录二维码图片", catch=True)
        game_dashen_launch(is_login=True,image_path=image_path)
        monitor_catch("大神登录完成", catch=True)
        sleep(3)
        game_qq_launch()
        sleep(5)
        if find_tpl("tpl20260412170141.png", title="登录成功", desc="登录成功",area=(930, 355, 1500, 440),threshold=0.8):
            monitor_catch("登录成功")
            return

    def processLogin(self):
        """登录流程"""
        if ENV.taskType == 20:
            for _ in range(3):
                num_zh = self.stageMap.get(self.stage, '')
                self.title = f" 登录{num_zh}阶段"
                # if self.stage == 1:
                #     self.preLoginCheck()
                #     self.firstStage()
                #     break
                # if self.stage == 2:
                #     self.secondStage()
                #     break
                if self.stage == 3:
                    self.preLoginCheck()
                    self.thirdStage()
                    return

        # 账密登录
        else:
            self.title = " 登录阶段"
            monitor_task_status_v2(self.title, f"账密登录")
            self.preLoginCheck()
            self.firstStage()
            self.fengkong_shibie()




@PopupHandler()
class AvatarCollector():
    def __init__(self):
        self.long_creenshot = []
        self.gather_info={}
        self.long_creenshot_path = [
            {"LT":(100,295),"RB":(1665,1165)},
            {"LT":(100,275),"RB":(1665,1140)},
            {"LT":(100,320),"RB":(1665,1190)},
            {"LT":(100,290),"RB":(1665,1165)},
            {"LT":(100,275),"RB":(1665,1140)},
            {"LT":(100,320),"RB":(1665,1190)},
            {"LT": (100, 290), "RB": (1665, 1165)},
            {"LT": (100, 275), "RB": (1665, 1140)},
            {"LT": (100, 320), "RB": (1665, 1190)},
            {"LT": (100, 290), "RB": (1665, 1165)},
            {"LT": (100, 910), "RB": (1665, 1260)},
        ]
        self.shuot_donwn_path = [0,12,11,12,12,11,12,12,11,12,5]
    def __call__(self):
        self.get_home_page_info()
        self.shejiao_touxiang()
        self.avatarLongScreenshot()

    def get_grid_positions_touxiang(self, total=30):
        """
        获取指定数量的网格位置坐标

        规则:
        - 起点：(100, 280), (260, 435)
        - 每步 x+175，走八步
        - x 回滚成 100，y+180
        - 返回格式：[(x1, y1, x2, y2), ...]
        """
        positions = []

        # 两组起点
        base_x1, base_y1 = 100, 280
        base_x2, base_y2 = 260, 435

        x_step = 175  # x 每次增加
        y_step = 180  # y 每次增加
        cycle_length = 9  # 每 8 步回滚

        for index in range(total):
            # 计算在循环中的位置
            position_in_cycle = index % cycle_length

            # 计算当前组的偏移
            group_offset = index // cycle_length

            # 第一组坐标
            x1 = base_x1 + (position_in_cycle * x_step)
            y1 = base_y1 + (group_offset * y_step)

            # 第二组坐标
            x2 = base_x2 + (position_in_cycle * x_step)
            y2 = base_y2 + (group_offset * y_step)

            # 返回四个值的元组
            positions.append((x1, y1, x2, y2))

        return positions

    def get_unlocked_touxiang(self):
        unlocked_touxiang_list=[]
        image =snapshot_write()
        # 获取 45 个坐标对
        coords = self.get_grid_positions_touxiang(45)
        for coord in coords:
            x1, y1, x2, y2 = coord
            if find_tpl("tpl20260324222834.png", area=(x1, y1, x2, y2), threshold=0.6, image=image):
            # if find_tpl("tpl20260324210832.png",area=(x1, y1, x2, y2),threshold=0.7,image=image):
                continue
            touxiang=snapshot_write(area=(x1, y1, x2, y2),image=image)
            touxiang=EditImage(touxiang).resize((0, 100))
            unlocked_touxiang_list.append(touxiang)
        return unlocked_touxiang_list


    def avatarLongScreenshot(self):
        touxiang_name_list=[]
        pre_image = None
        for i in range(10):
            this_image = snapshot_write(LT=(90, 1080), RB=(1670, 1250))

            if pre_image is not None and snapshot_match(image=pre_image, match_image=this_image, threshold=0.5):
                break
            pre_image = this_image
            for touxiang in self.get_unlocked_touxiang():
                # air_touch(touxiang)
                # if find_tpl("tpl20260310181617.png", desc="已解锁头像识别") or find_tpl("tpl20260310181742.png",desc="已解锁头像识别"):
                #     touxiang_name = snapshot_ocr(LT=(1825,655),RB=(2265,740),image=snapshot_write(),desc="头像名识别")
                #     if touxiang_name in touxiang_name_list:
                #         continue
                #     touxiang_name_list.append(touxiang_name)
                #     self.long_creenshot.append(snapshot_write(LT=(1850,320),RB=(2175,655)))
                self.long_creenshot.append(touxiang)
            for i in range(2):
                air_swipe_fast(start_point=(875, 1220), end_point=(875, 491), sec=0.2)

        #最后一列识别
        x=0
        y=0
        for i in range(18):
            air_touch((180+x,995+y))
            if find_tpl("tpl20260310181617.png", desc="已解锁头像识别") or find_tpl("tpl20260310181742.png",
                                                                                    desc="已解锁头像识别"):

                touxiang_name = snapshot_ocr(LT=(1825, 655), RB=(2265, 740), image=snapshot_write(), desc="t头像名识别")
                if touxiang_name in touxiang_name_list:
                    x += 180
                    if i % 8 == 0 and i != 0:
                        x = 0
                        y += 180
                    continue
                touxiang = snapshot_write(LT=(1850, 320), RB=(2175, 655))
                touxiang = EditImage(touxiang).resize((0, 100))
                touxiang_name_list.append(touxiang_name)
                self.long_creenshot.append(touxiang)

            x+=180
            if i % 8 == 0 and i != 0:
                x = 0
                y += 180

        touxiang_long_image=combine_images_write(images=self.long_creenshot,cols=5)
        if touxiang_long_image:
            snapshot_write(write_name="$_头像合集",image=touxiang_long_image[0],sn=11264004)
        else:
            monitor_catch("未采集到头像")

    def grid_positions(self,x_start=180, y_start =400,step = 168,cols = 9,num=45):
        """
        生成网格位置坐标
        起始点 (180, 400)
        每行 9 个，x 每次 +165
        每走 9 个，y +165，共 5 行（45 个元素）
        """

        for index in range(num):  # 总共 46 个
            row = index // cols  # 计算行数
            col = index % cols  # 计算列数

            # 计算当前坐标
            x = x_start + col * step
            y = y_start + row * step

            yield x, y # 返回坐标和序号（从 1 开始）




    def shejiao_touxiang(self):
        for i in range(3):
            air_touch((885,40))
            sleep(1)
        air_touch((1695,730))
        # press_up(combo=100,sec=0.5)
        pre_image = None
        for i in range(16):
            air_swipe_fast(start_point=(875,300), end_point=(875,1200), sec=0)
            this_image = snapshot_write(LT=(100, 300), RB=(1660, 465))

            if pre_image is not None and snapshot_match(image=pre_image, match_image=this_image, threshold=0.5):
                break
            pre_image = this_image
    def get_home_page_info(self):
        zhuye_result= snapshot_ocr(LT=(1110, 15), RB=(1188, 65), image=snapshot_write(), desc="识别大厅信息")
        if find_tpl("tpl20260306171400.png", title="主页信息", desc="识别主页", catch=True) or "大厅" in zhuye_result:
            snapshot_write(write_name="$_游戏首页",mask=(90,930,500,1350),sn=11264002)
        for i in range(3):
            air_touch((85,1270))
            sleep(2)
            result = snapshot_ocr(LT=(320,13),RB=(420,70),image=snapshot_write(),desc="确认个人信息")
            if  "个人" in result or "信息" in result:
                zhuye_image=snapshot_write()
                youxi_lv=snapshot_ocr(LT=(222,357),RB=(264,375),image=zhuye_image)
                self.gather_info["角色等级"] = youxi_lv if youxi_lv else "0"
                monitor_catch("角色等级", youxi_lv)
                yingxiong_pifu_num=snapshot_ocr(LT=(335,635),RB=(455,675),image=zhuye_image,is_digit= True)
                wuqi_pifu_num=snapshot_ocr(LT=(520,635),RB=(620,670),image=zhuye_image,is_digit= True)
                monitor_catch("英雄皮肤数",yingxiong_pifu_num)
                monitor_catch("武器皮肤数",wuqi_pifu_num)
                self.gather_info["英雄皮肤数"] = yingxiong_pifu_num if yingxiong_pifu_num else "0"
                self.gather_info["武器皮肤数"] = wuqi_pifu_num if wuqi_pifu_num else "0"
                property_write(self.gather_info)
                snapshot_write(write_name="$_主页信息",mask=[(335,239,731,284),(1375,239,1600,284),(90,930,500,1350)],sn=11264003)
                break



@PopupHandler()
class SeasonCollector:
    """赛季数据采集"""
    def __init__(self):
        self.saiji_lis=[]
        self.gather_info={}
    def __call__(self):
        # 赛季数据采集逻辑
        self.touch_saijishuju()
    def touch_saijishuju(self):
        """点击赛季数据"""
        for i in range(3):
            air_touch((75, 1270))
            sleep(2)
            air_touch((580, 45))
            sleep(1)
            air_touch((1900, 218))
            sleep(1)
            find_tpl_touch("tpl20260409151750.png", title="赛季数据", desc="点击排位赛",area=(1775, 185,2025, 560))
            sleep(1)
            if find_tpl_touch("tpl20260311150037.png", title="赛季数据", desc="点击单排赛季数据"):
                danpai_lv=snapshot_ocr(LT=(250,1000),RB=(590,1085),image=snapshot_write())
                monitor_catch("单排赛季数据",danpai_lv)
                self.saiji_lis.append(snapshot_write(mask=[(95,168,555,245),(40,1200,385,1315)]))
            if find_tpl_touch("tpl20260311150142.png", title="赛季数据", desc="点击双排赛季数据"):
                shuangpai_lv = snapshot_ocr(LT=(250, 1000), RB=(590, 1085), image=snapshot_write())
                monitor_catch("双排赛季数据",shuangpai_lv)
                self.saiji_lis.append(snapshot_write(mask=[(95,168,555,245),(40,1200,385,1315)]))
            if find_tpl_touch("tpl20260311150219.png", title="赛季数据", desc="点击三排赛季数据"):
                sanpai_lv = snapshot_ocr(LT=(250, 1000), RB=(590, 1085), image=snapshot_write())
                self.gather_info["三排段位"] = sanpai_lv
                property_write(self.gather_info)
                monitor_catch("三排赛季数据",sanpai_lv)
                self.saiji_lis.append(snapshot_write(mask=[(95,168,555,245),(40,1200,385,1315)]))
            if len(self.saiji_lis) >0:
                saiji_long_image=combine_images_write(images=self.saiji_lis)
                snapshot_write(write_name="$_赛季数据",image=saiji_long_image[0],sn=11264005)
                return
            else:
                monitor_catch("赛季数据未采集")
        monitor_catch(f"状态检测", "界面标识未识别", break_mode=BreakModeEnum.app, status=10130, image=snapshot_write())


def chinese_number_to_int(text):
    """
    将带中文单位的数字字符串转换为int
    支持：万、千、百、亿等单位
    """
    if not text:
        monitor_catch("幻丝总览未采集成功", catch=True)
        return 0

    text = str(text).strip()

    # 定义单位映射
    unit_map = {
        '万': 10000,
        '千': 1000,
        '百': 100,
        '亿': 100000000,
    }

    # 检查是否包含中文单位
    for unit, multiplier in unit_map.items():
        if unit in text:
            # 提取数字部分
            num_str = text.replace(unit, '').strip()
            try:
                num = float(num_str)
                return int(num * multiplier)
            except ValueError:
                monitor_catch("幻丝总览未采集成功", catch=True)
                return 0

    # 没有单位，直接转换
    try:
        return int(float(text))
    except ValueError:
        monitor_catch("幻丝总览未采集成功", catch=True)
        return 0


@PopupHandler()
class AlbumCollecto():
    """图鉴采集"""
    def __init__(self):
       self.tujian_lis=[]
       self.gather_info={}
    def __call__(self):
       self.touch_tuji()
    def touch_tuji(self):
        """点击图鉴"""
        air_touch((75, 1270))
        sleep(1)
        air_touch((1190, 45))
        sleep(1)
        zonglan_image= snapshot_write(mask=mask)
        red_num =snapshot_ocr(LT=(1815,715),RB=(1915,750),image=zonglan_image,is_digit= True,desc="红装总览")
        if red_num == "":
            red_num = "0"
            monitor_catch("红皮总览未采集成功", catch= True)
        self.gather_info["红皮数"] = red_num
        monitor_catch("红装总览", red_num)
        yellow_num =snapshot_ocr(LT=(1770,930),RB=(1920,970),image=zonglan_image,is_digit= True,desc="金装总览")
        if yellow_num == "":
            yellow_num = "0"
            monitor_catch("金皮总览未采集成功", catch= True)
        self.gather_info["金皮数"] = yellow_num
        monitor_catch("金皮总览", yellow_num)
        huansi =snapshot_ocr(LT=(1930,40),RB=(2030,70),image=zonglan_image,desc="幻丝总览")
        huansi_num = huansi.replace(',', '')
        huansi_num =chinese_number_to_int(huansi_num)
        self.gather_info["幻丝数"] = huansi_num
        monitor_catch("幻丝总览", f"{huansi_num}")
        zonglan_num=snapshot_ocr(LT=(850,850),RB=(1200,935),image=zonglan_image,desc="总收藏值")
        if zonglan_num == "":
            zonglan_num = "0"
            monitor_catch("总收藏值未采集成功", catch= True)
        self.gather_info["总收藏值"] = zonglan_num
        monitor_catch("总收藏值", zonglan_num)
        # self.tujian_lis.append(zonglan_image)
        property_write(self.gather_info)
        air_touch((1245, 110))
        # self.tujian_lis.append(snapshot_write(mask=mask))
        # tujian_long_image=combine_images_write(images=self.tujian_lis)
        snapshot_write(write_name="$_图鉴收藏",image=zonglan_image,sn=11264006)


@PopupHandler()
class PassCollector:
    """通行证采集"""
    def __init__(self):
        self.gather_info = {}
    def __call__(self):
        # 通行证采集逻辑
        self.touch_tongxingzheng()
    def touch_tongxingzheng(self):
        """点击通行证"""
        air_touch((140, 40))
        sleep(5)
        for i in range(3):
            find_tpl_touch("tpl20260311151947.png", title="通行证界面", desc="点击日常")
            if find_tpl("tpl20260311152231.png", desc="日常界面判断") or find_tpl("tpl20260316205354.png", desc="日常界面判断"):
                tongxingzheng_lv=snapshot_ocr(LT=(205,45),RB=(420,80),image=snapshot_write(),is_digit= True)
                self.gather_info["通行证等级"] = int(tongxingzheng_lv)
                property_write(self.gather_info)
                snapshot_write(write_name="$_通行证截图",sn=11264006,mask=mask)
                monitor_catch(f"状态检测", f"通行证采集结束,等级{tongxingzheng_lv}")
                return
            else:
                find_tpl_touch("tpl20260311152654.png", title="重新进通行证界面", desc="点击日常")



@PopupHandler()
class GameplayCollector:
    """玩法采集"""
    def __call__(self):
        self.touch_zhengsheng()
    def touch_zhengsheng(self):
        """点击hengshui"""
        air_touch((1375, 110))
        sleep(5)
        air_touch((990,45))
        if find_tpl("tp214885775049.jpg", desc="hengshui界面判断"):
            find_tpl_touch("tpl20260311154638.png", title="征神界面", desc="关闭弹窗")
        if find_tpl("tpl20260311142315.png", desc="征神界面判断"):
            snapshot_write(write_name="$_征神",mask=mask,sn=11264007)
            monitor_catch(f"状态检测", "检测到征神，结束")



@PopupHandler()
class LimitedItemCollector:
    """幻丝道具采集"""
    def __call__(self):
        # 幻丝道具采集逻辑
        self.touch_huansi()
    def touch_huansi(self):
        air_touch((1365,45))
        find_tpl_touch("tpl20260311143940.png", title="幻丝界面", desc="点击日常")
        find_tpl_touch("tpl20260311144032.png", title="幻丝界面", desc="点击幻丝")
        snapshot_write(write_name="$_幻丝",mask=mask,sn=11264008)



@PopupHandler()
class GachaCollector:
    """抽卡采集"""
    def __init__(self):
        self.gacha_image = []
        self.chouka_name_lis= []
        self.xianshi_lis = [(265,470),(265,600),(265,700), (265,830), (265,920)]
    def __call__(self):
        # 抽卡采集逻辑
        self.touch_chouka()
    def touch_chouka(self):
        for i in range(3):
            if find_tpl_touch("tpl20260325100035.png", area=(20, 525, 490, 580)):
                break
            if find_tpl_touch("tpl20260325100256.png", area=(20, 525, 490, 580)):
                break
        air_touch((117, 640))
        sleep(10)
        for i in self.xianshi_lis:
            air_touch(i)
            sleep(1)
            chouka_name=snapshot_ocr(LT=(90,190),RB=(600,280),image=snapshot_write())
            if chouka_name in self.chouka_name_lis:
                continue
            self.chouka_name_lis.append(chouka_name)
            self.gacha_image.append(snapshot_write(mask= mask))
        chouka_long_image=combine_images_write(images=self.gacha_image)
        snapshot_write(write_name="$_抽卡",image=chouka_long_image[0],sn=11264009,mask=mask)

@PopupHandler()
class HeroCollector:
    """英雄采集"""
    def __init__(self):
        self.json_path = gameDir.parent / '11264_netease/皮肤属性_备份.json'
        self.image_url =  gameDir.parent / '11264_netease/属性图片.json'
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.pifu_data = json.load(f)
        self.fuzhuang_data=self.pifu_data["服装"]
        self.aoyi_data=self.pifu_data["变身器"]
        with open(self.image_url, 'r', encoding='utf-8') as f:
            self.pifu_image_url = json.load(f)
        self.base_aoyi_name =("金钟罩", "隐身", "北冥锁", "妖刀", "阴神之眼", "金刚","回春","沙牢","烈火","神将","御气","山兽之君","幽魂链","青狐","流金剑","恩威之光","风雷真身","小李飞刀")
        self.unlocked ="tpl20260323144054.png"
        self.gather_info_list = []
        self.hero_pifu_all_pic = {}
        self.image_path = gameDir / "materials_icons"
        self.font_path =str(gameDir.parent / '11264_netease/Alimamakaishu/AlimamaDongFangDaKai-Regular.otf')
        self.finish_hero_list=[]
        self.hero_fuzhuang_list = []
        self.hair_pifu_list = []
        self.hero_aoyi_list = []
        self.finish_shizhuang_list = []
        self.finish_hair_list = []
        self.finish_aoyi_list = []
        self.hero_path_list = [
            {"path": (380, 270), "color": {"LT": (200, 270), "RB": (202, 273)}},
            {"path": (380, 360), "color": {"LT": (200, 360), "RB": (202, 363)}},
            {"path": (380, 450), "color": {"LT": (200, 450), "RB": (202, 453)}},
            {"path": (380, 540), "color": {"LT": (200, 540), "RB": (202, 543)}},
            {"path": (380, 630), "color": {"LT": (200, 630), "RB": (202, 633)}},
            {"path": (380, 720), "color": {"LT": (200, 720), "RB": (202, 723)}},
            {"path": (380, 810), "color": {"LT": (200, 810), "RB": (202, 813)}},
            {"path": (380, 900), "color": {"LT": (200, 800), "RB": (202, 903)}},
            {"path": (380, 990), "color": {"LT": (200, 990), "RB": (202, 993)}},
            {"path": (380, 1080), "color": {"LT": (200, 1080), "RB": (202, 1083)}},
            {"path": (380, 1170), "color": {"LT": (200, 1170), "RB": (202, 1173)}}
        ]

        self.hero_hair_lis = [
            {"点击": (180, 420), "区域": (100, 305, 255, 525), "颜色": {"LT": (142, 520), "RB": (200, 522)}},
            {"点击": (350, 420), "区域": (275, 305, 425, 525), "颜色": {"LT": (324, 520), "RB": (382, 522)}},
            {"点击": (520, 420), "区域": (445, 305, 595, 525), "颜色": {"LT": (482, 520), "RB": (560, 522)}},
            {"点击": (175, 650), "区域": (100, 540, 255, 765), "颜色": {"LT": (142, 754), "RB": (200, 756)}},
            {"点击": (350, 650), "区域": (275, 540, 425, 765), "颜色": {"LT": (324, 754), "RB": (382, 756)}},
            {"点击": (520, 650), "区域": (445, 540, 595, 765), "颜色": {"LT": (482, 754), "RB": (560, 756)}},
            {"点击": (180, 880), "区域": (100, 775, 255, 995), "颜色": {"LT": (142, 988), "RB": (200, 990)}},
            {"点击": (350, 880), "区域": (275, 775, 425, 995), "颜色": {"LT": (324, 988), "RB": (382, 990)}},
            {"点击": (520, 880), "区域": (445, 775, 595, 995), "颜色": {"LT": (482, 988), "RB": (560, 990)}}
        ]
        self.hero_aoyi_lis = [
            (140, 260),
            (140, 350),
            (140, 440),
            (140, 530),
            (140, 620),
            (140, 720),
            (140, 770)
        ]
        self.aoyi_pifu_lis = [
            {"坐标": (400, 260), "颜色": {"LT": (200, 250), "RB": (202, 253)}},
            {"坐标": (400, 350), "颜色": {"LT": (200, 350), "RB": (202, 353)}},
            {"坐标": (400, 440), "颜色": {"LT": (200, 450), "RB": (202, 453)}},
            {"坐标": (400, 530), "颜色": {"LT": (200, 550), "RB": (202, 553)}},
            {"坐标": (400, 620), "颜色": {"LT": (200, 650), "RB": (202, 653)}},
            {"坐标": (400, 720), "颜色": {"LT": (200, 750), "RB": (202, 753)}},
            {"坐标": (400, 770), "颜色": {"LT": (200, 850), "RB": (202, 853)}}
        ]

    def __call__(self):
       self.touch_hero()

    def is_yingxiong(self):
        for i in range(3):
            air_touch((875,45))
            sleep(2)
            if "英雄" in snapshot_ocr(image=snapshot_write(), LT=(670, 80), RB=(800, 125), desc="检测英雄界面"):
                monitor_catch(f"状态检测", "已经进入英雄页面")
                return
            if "外观" in snapshot_ocr(image=snapshot_write(), LT=(170, 1145), RB=(290, 1190), desc="检测英雄界面"):
                monitor_catch(f"状态检测", "已经进入英雄页面")
                return
            else:
                for i in range(3):
                    if find_tpl("tpl20260316150349.png", image=snapshot_write(), desc="重制英雄界面",area=area_rb):
                        monitor_catch(f"状态检测", "未进入英雄界面，重新进入")
                        air_touch((2340,1318))
                    else:
                        return
    def touch_hero(self):
        self.is_yingxiong()
        sleep(1)
        for i in range(3):
            for i in self.get_grid_positions():
                for n in range(2):
                    air_touch(i)
                image = snapshot_write(desc="识别英雄主页")
                hero_name = snapshot_ocr(image=image, LT=(1795, 170), RB=(2070, 245), desc="识别英雄名称")
                hero_name = self.hero_name_check(hero_name)
                if hero_name in self.finish_hero_list:
                    continue
                if hero_name == "宁红夜":
                    sleep(2)
                if find_tpl_touch("tpl20260313105824.png", title="英雄界面", desc="打开装扮"):
                    if hero_name == "宁红夜":
                        sleep(2)
                    self.get_hero_fuzhuang_color(hero_name)
                    self.finish_shizhuang_list.extend(self.hero_fuzhuang_list)
                    self.get_hero_hair(hero_name)
                    self.finish_hair_list.extend(self.hair_pifu_list)
                    self.get_hero_aoyi(hero_name)
                    self.finish_aoyi_list.extend(self.hero_aoyi_list)
                    self.merge_pic(hero_name)
                    self.cler_pic()
                    self.finish_hero_list.append(hero_name)
                    monitor_catch(f"英雄{hero_name}采集完毕")
                    monitor_catch(f"已经采集的英雄{len(self.finish_hero_list)}个")
                    if len(self.finish_hero_list) >= 26 or hero_name== "巫真" :
                        monitor_catch("所有英雄采集完毕")
                        self.upload_properties()
                        monitor_catch("属性回传")
                        return
                else:
                    self.is_yingxiong()
        self.upload_properties()
        monitor_catch("属性回传")
        return
    def upload_properties(self):
        new_fuzhuang_pifu_list=[]
        new_aoyi_pifu_list=[]
        for fuzhuang_pifu in self.finish_shizhuang_list:
            if self.pifu_image_url.get(fuzhuang_pifu["名称"]):
                fuzhuang_pifu["属性图片"]= str(self.pifu_image_url.get(fuzhuang_pifu["名称"]))
            else:
                # _,image_path=snapshot_write(read_name=str(self.image_path /  f"默认背景.png"),needPath= True)
                fuzhuang_pifu["属性图片"] = str(self.pifu_image_url.get("默认背景"))
            new_fuzhuang_pifu_list.append(fuzhuang_pifu)
        for aoyi in self.finish_aoyi_list:
            if self.pifu_image_url.get(aoyi["名称"]):
                aoyi["属性图片"] = str(self.pifu_image_url.get(aoyi["名称"]))
            else:
                # _,image_path=snapshot_write(read_name=str(self.image_path /  f"默认背景.png"),needPath= True)
                aoyi["属性图片"] = str(self.pifu_image_url.get("默认背景"))
            new_aoyi_pifu_list.append(aoyi)
        property_write("服装",new_fuzhuang_pifu_list)
        property_write("发型",self.finish_hair_list)
        property_write("变身器",new_aoyi_pifu_list)

    def hero_name_check(self, hero_name):
        if "真" in hero_name:
            hero_name = "巫真"
        elif "欢" in hero_name:
            hero_name = "李寻欢"
        elif "灵" in hero_name:
            hero_name = "张起灵"
        elif "三" in hero_name:
            hero_name = "崔三娘"
        elif "哈" in hero_name:
            hero_name = "哈迪"
        elif "尘" in hero_name:
            hero_name = "无尘"
        elif "山" in hero_name:
            hero_name = "岳山"
        elif "田" in hero_name:
            hero_name = "武田信忠"
        elif "玉" in hero_name:
            hero_name = "玉玲珑"
        elif "轻" in hero_name:
            hero_name = "魏轻"
        elif "万" in hero_name:
            hero_name = "万钧"
        elif "刘" in hero_name:
            hero_name = "刘炼"
        elif "沧" in hero_name:
            hero_name = "季沧海"
        elif "天" in hero_name:
            hero_name = "天海"
        elif "莹" in hero_name:
            hero_name = "季莹莹"
        elif "宁" in hero_name:
            hero_name = "宁红夜"
        elif "拉" in hero_name:
            hero_name = "席拉"
        elif "木" in hero_name or "尔" in hero_name:
            hero_name = "特木尔"
        elif "门" in hero_name:
            hero_name = "土御门胡桃"
        elif "梦" in hero_name:
            hero_name = "蓝梦"
        elif "南" in hero_name:
            hero_name = "迦南"
        elif "沈" in hero_name:
            hero_name = "沈妙"
        elif "顾" in hero_name:
            hero_name = "顾清寒"
        elif "刀" in hero_name:
            hero_name = "妖刀姬"
        elif "萍" in hero_name:
            hero_name = "殷紫萍"
        elif "为" in hero_name:
            hero_name = "胡为"
        return hero_name

    def merge_test(self):
        merge_lis = [
            "封面沈妙.png",
            "封面胡为.png"
        ]
        pifu_image = snapshot_write(read_name=str(self.image_path / "背景封面.png"))
        biaoti_image = snapshot_write(read_name=str(self.image_path / "皮肤标题.png"))

        # 确保两张图都是 RGBA 四通道
        if isinstance(pifu_image, np.ndarray):
            if pifu_image.shape[-1] == 3:
                pifu_image = cv2.cvtColor(pifu_image, cv2.COLOR_RGB2RGBA)

        if isinstance(biaoti_image, np.ndarray):
            if biaoti_image.shape[-1] == 3:
                biaoti_image = cv2.cvtColor(biaoti_image, cv2.COLOR_RGB2RGBA)

        biaoti_image = EditImage(biaoti_image).resize((900, 0))
        pifu_image = EditImage(pifu_image).resize((1000, 0))
        pifu_image = EditImage(pifu_image).images_fill_alpha(((40, 0), biaoti_image))
        for i in merge_lis:
            hero_image = snapshot_write(read_name=str(self.image_path / i))
            if isinstance(hero_image, np.ndarray):
                if hero_image.shape[-1] == 3:
                    hero_image = cv2.cvtColor(hero_image, cv2.COLOR_RGB2RGBA)
            if isinstance(pifu_image, np.ndarray):
                if pifu_image.shape[-1] == 3:
                    pifu_image = cv2.cvtColor(pifu_image, cv2.COLOR_RGB2RGBA)
            hero_image = EditImage(hero_image).resize((200, 0))
            pifu_image = EditImage(pifu_image).images_fill_alpha(((40, 50), hero_image))
            snapshot_write(write_name=i,image=pifu_image )

    def merge_pic(self,hero_name):
        self.merge_hero_pifu_pic(hero_name)
        # property_write("服装",self.hero_fuzhuang_list)
        self.merge_hair_pifu_pic(hero_name)
        # property_write("发型",self.hair_pifu_list)
        self.merge_aoyi_pic(hero_name)
        # property_write("变身器",self.hero_aoyi_list )
        self.merge_suoyou_pic(hero_name)

    def cler_pic(self):
        self.hero_fuzhuang_list = []
        self.hair_pifu_list = []
        self.hero_aoyi_list = []
        self.hero_pifu_all_pic ={}

    def get_hero_aoyi(self,hero_name):
        # air_touch((970, 35))

        image = snapshot_write()
        if not find_tpl("tpl20260326162316.png", image=image, area=(290, 15, 1135, 75),threshold=0.6):
            monitor_catch(f"{hero_name}没有技能奥义")
            air_touch((2320, 1315))
            return
        find_tpl_touch("tpl20260324144242.png", desc="点击技能奥义", area=(290, 15, 1135, 75), image=image,threshold=0.6)
        aoyi_list= []
        pre_image = None
        for aoyi in self.hero_aoyi_lis:
            air_touch(aoyi)
            air_touch((420,950))
            this_image = snapshot_write(LT=(195, 220), RB=(675, 1100))

            if pre_image is not None and snapshot_match(image=pre_image,match_image=this_image,threshold=0.5):
                continue
            pre_image = this_image
            self.get_aoyi_name(hero_name,aoyi_list)
        air_touch((2320, 1315))


    def get_unlocked_aoyi_pifu(self,aoyi_path_list):
        unlocked_list = []
        x = 225
        y = 300
        for hero in aoyi_path_list:
            hero_pifu_dict = {}
            image = snapshot_write()
            if snapshot_match(filename="tpl20260323221309.png", LT=(580, x), RB=(670, y),
                              image=image,threshold=0.8):
                pass
            else:
                this_color = snapshot_color(LT=hero["颜色"]["LT"], RB=hero["颜色"]["RB"], image=image)
                if 0 < this_color["h"] < 20:
                    hero_pifu_dict["稀有度"] = "红"
                elif 20 < this_color["h"] < 50:
                    hero_pifu_dict["稀有度"] = "金"
                else:
                    return unlocked_list
                hero_pifu_dict["皮肤坐标"] = hero["坐标"]
                unlocked_list.append(hero_pifu_dict)
            x += 90
            y += 90
        return unlocked_list

    def get_aoyi_name(self,hero_name,aoyi_list):
        unlocked_list =self.get_unlocked_aoyi_pifu(self.aoyi_pifu_lis)
        for pifu in unlocked_list:
            aoyi_fushi_dict = {
                "名称":"",
                "英雄": hero_name,
                "稀有度": pifu["稀有度"],
                "属性图片": ""
            }

            air_touch(pifu["皮肤坐标"])
            aoyi_pifu_name = snapshot_ocr(LT=(1295, 220), RB=(2155, 285))
            if aoyi_pifu_name in aoyi_list or aoyi_pifu_name in self.base_aoyi_name:
                return
            re = snapshot_ocr(LT=(1925, 1145), RB=(2208, 1195), image=snapshot_write())
            if find_tpl("tpl20260313165519.png", desc="装扮界面判断") or ("装" in re or "配" in re):
                aoyi_list.append(aoyi_pifu_name)
                sleep(2)
                aoyi_image = snapshot_write(width=500, height=750, LT=(1260, 300))
                aoyi_image = EditImage(aoyi_image).resize((200,0))
                _, e_path = snapshot_write(needPath=True, write_name=f"奥义皮肤/{aoyi_pifu_name}",image=aoyi_image)
                aoyi_fushi_dict["属性图片"] = e_path
                aoyi_fushi_dict["名称"] = aoyi_pifu_name
                self.hero_aoyi_list.append(aoyi_fushi_dict)
            else:
                continue
    def huadong_fuzhuang_fuyuan(self):
        pre_image = None
        for i in range(8):
            air_touch((320,600))
            result = snapshot_ocr(LT=(2260, 1300), RB=(2370, 1340), image=snapshot_write())
            if "展开" in result or "列表" in result:
                air_touch((2280,1310))
                sleep(1)
            air_swipe_fast((320, 500), end_point=(320, 1540), sec=0.1)
            this_image = snapshot_write(LT=(195, 220), RB=(675, 395))

            if pre_image is not None and snapshot_match(image=pre_image, match_image=this_image, threshold=0.6):
                break
            pre_image = this_image


    def huadong_fuzhuang_next(self):
        air_touch((375,1140))
        result = snapshot_ocr(LT=(2260, 1300), RB=(2370, 1340), image=snapshot_write())
        if "展开" in result or "列表" in result:
            air_touch((2280,1310))
            sleep(2)
        air_swipe_fast((375,1140), end_point=(375,265),sec=0.1)

    def huadong_hair_fuyuan(self):
        pre_image = None
        for i in range(8):
            air_touch((350,360))
            result = snapshot_ocr(LT=(2260, 1300), RB=(2370, 1340), image=snapshot_write())
            if "展开" in result or "列表" in result:
                air_touch((2280,1310))
            air_swipe_fast((350,360), end_point=(350,1200),sec=0.1)
            this_image = snapshot_write(LT=(100, 300), RB=(595, 540))

            if pre_image is not None and snapshot_match(image=pre_image, match_image=this_image, threshold=0.5):
                break
            pre_image = this_image

    def huadong_hair_next(self):
        air_touch((350, 925))
        result = snapshot_ocr(LT=(2260, 1300), RB=(2370, 1340), image=snapshot_write())
        if "展开" in result or "列表" in result:
            air_touch((2280, 1310))
            sleep(1)
        air_swipe_fast((350, 925), end_point=(350, 370), sec=0.1)
        air_swipe_fast((350, 925), end_point=(350, 693), sec=0.1)

    def get_unlocked_hero_pifu(self):
        unlocked_list = []
        x= 225
        y= 300
        for i in range(11):
            is_locked_path = [(200, x), (670, y)]
            hero_pifu_dict={}
            image=snapshot_write()
            if snapshot_match(filename="tpl20260323144054.png",LT=is_locked_path[0], RB=is_locked_path[1],image=image,threshold=0.7):
                x += 90
                y += 90
                continue
            pifu_name = snapshot_ocr(area=(200, x, 580, y), image=image)
            hero_pifu_dict["名称"] = pifu_name
            if self.fuzhuang_data.get(pifu_name):
               hero_pifu_dict["稀有度"] = self.fuzhuang_data[pifu_name]
            else:
                if find_tpl("tpl20260324170835.png",image=image,area=(195, x,260, y),threshold=0.6,desc="稀有度为红的相似度"):
                    hero_pifu_dict["稀有度"] = "红"
                elif find_tpl("tpl20260324171020.png",image=image,area=(195, x,260, y),threshold=0.6,desc="稀有度为金的相似度"):
                    hero_pifu_dict["稀有度"] = "金"
                else:
                    # this_color = snapshot_color(LT=wuqi["color"]["LT"], RB=wuqi["color"]["RB"], image=image)
                    # if 0 < this_color["h"] < 20:
                    #     hero_pifu_dict["稀有度"] = "红"
                    # elif 20 < this_color["h"] < 50:
                    #     hero_pifu_dict["稀有度"] = "金"
                    # else:
                    #     hero_pifu_dict["稀有度"] = "紫色"
                    #     unlocked_list.append(hero_pifu_dict)
                    #     return unlocked_list
                    monitor_catch("稀有度不是金和红退出")
                    hero_pifu_dict["稀有度"] = "紫"
                    unlocked_list.append(hero_pifu_dict)
                    return unlocked_list
            x += 90
            y += 90
            unlocked_list.append(hero_pifu_dict)
        return unlocked_list


    def get_hero_fuzhuang_color(self,hero_name):
        sleep(1)
        fuzhuang_result=snapshot_ocr(LT=(380, 13), RB=(428, 75), image=snapshot_write())
        if  "时装" in fuzhuang_result or "时" in fuzhuang_result:
            air_touch((400, 48))
            monitor_catch("识别服装界面")
        else:
            monitor_catch("未找到时装界面")
            return
        self.huadong_fuzhuang_fuyuan()
        fuzhuang_list=[]
        for i in range(4):
            unlocked_list=self.get_unlocked_hero_pifu()
            for hero in unlocked_list:
                if hero.get("稀有度") not in  ("金","红"):
                    return
                hero_fushi_dict = {"名称": hero["名称"], "英雄": hero_name, "稀有度": hero["稀有度"], "属性图片": ""}
                hero_pifu_name = hero["名称"]
                if hero_pifu_name in fuzhuang_list:
                    continue
                fuzhuang_list.append(hero_pifu_name)
                if self.pifu_image_url.get(hero_pifu_name) :
                    # c_img_path= self.pifu_image_url.get(hero_pifu_name)
                    fuzhuang_image = snapshot_write(read_name=str(self.pifu_image_url.get(hero_pifu_name)),desc="属性库存在图片")
                else:
                    # c_img_path=self.image_path /  f"默认背景.png"
                    fuzhuang_image = snapshot_write(read_name=str(self.image_path /  f"默认背景.png"),desc="属性库不存在")
                fuzhuang_image = cv2.resize(fuzhuang_image, (200, 280))
                _, c_img_path = snapshot_write(image=fuzhuang_image,
                                               write_name=f"服装皮肤/{hero['名称']}", needPath=True)
                hero_fushi_dict["属性图片"] = str(c_img_path)
                hero_fushi_dict["名称"] = hero["名称"]
                self.hero_fuzhuang_list.append(hero_fushi_dict)
                print(self.hero_fuzhuang_list)
            self.huadong_fuzhuang_next()


    def get_unlocked_heir_pifu(self,hero_path_list):
        unlocked_list = []

        for hair in hero_path_list:
            # lt= hair["区域"][:2]
            # rb= hair["区域"][-2:]
            hero_pifu_dict = {}
            image = snapshot_write()
            # if snapshot_match(filename="tpl20260323220008.png", LT=lt, RB=rb, image=image,threshold=0.5):
            if find_tpl("tpl20260323220008.png", area=hair["区域"], image=image, threshold=0.8):
                pass
            else:
                if find_tpl("tpl20260324170835.png",image=image,area=hair["区域"],threshold=0.8,desc="稀有度为红的相似度"):
                    hero_pifu_dict["稀有度"] = "红"
                elif find_tpl("tpl20260324171020.png",image=image,area=hair["区域"],threshold=0.8,desc="稀有度为金的相似度"):
                    hero_pifu_dict["稀有度"] = "金"
                else:
                    hero_pifu_dict["非红金"] = True
                    unlocked_list.append(hero_pifu_dict)
                    return unlocked_list
                # this_color = snapshot_color(LT=hair["颜色"]["LT"], RB=hair["颜色"]["RB"], image=image)
                # if 0 < this_color["h"] < 20:
                #     hero_pifu_dict["稀有度"] = "红"
                # elif 20 < this_color["h"] < 50:
                #     hero_pifu_dict["稀有度"] = "金"
                # else:
                #     hero_pifu_dict["非红金"] = True
                #     unlocked_list.append(hero_pifu_dict)
                #     return unlocked_list
                hero_pifu_dict["皮肤坐标"] = hair["点击"]
                hero_pifu_dict["区域"] = hair["区域"]
                unlocked_list.append(hero_pifu_dict)
        return unlocked_list

    def get_hero_hair(self,hero_name):
        if hero_name == "妖刀姬":
            monitor_catch(f"{hero_name}没有发型")
            return
        faxing_result = snapshot_ocr(LT=(544, 20), RB=(590, 71))
        if "发型" in faxing_result or "发" in faxing_result:
            air_touch((560, 45))
            monitor_catch("识别发型界面")
        else:
            monitor_catch("未找到发型界面")
            return
        hair_set=set()
        self.huadong_hair_fuyuan()
        for i in range(3):
            unlocked_list = self.get_unlocked_heir_pifu(self.hero_hair_lis)
            for hair in unlocked_list:
                if hair.get("非红金"):
                    return
                hair_pifu_dict = {
                    "名称": "",
                    "英雄": hero_name,
                    "稀有度": hair["稀有度"],
                    "属性图片": ""
                }
                air_touch(hair["皮肤坐标"])

                result = snapshot_ocr(LT=(2260, 1300), RB=(2370, 1340), image=snapshot_write())
                if "展开" in result or "列表" in result:
                    air_touch((2280, 1310))
                    sleep(1)
                hair_pifu_name = snapshot_ocr(LT=(1795, 240), RB=(2300, 295))
                if hair_pifu_name in hair_set:
                    continue
                re = snapshot_ocr(LT=(1995, 1147), RB=(2108, 1192), image=snapshot_write())
                if find_tpl("tpl20260325012558.png", desc="装扮界面判断") or ("装" in re or "配" in re):
                    hair_set.add(hair_pifu_name)
                    air_touch((1150,350))
                    hair_image = snapshot_write(width=160, height=220, LT=hair["区域"][:2],write_name=hair_pifu_name)
                    hair_image = EditImage(hair_image).resize((200,0))
                    _, d_img_path=snapshot_write(write_name=f"发型皮肤/{hair_pifu_name}", image=hair_image,needPath=True)
                    hair_pifu_dict["属性图片"] = d_img_path
                    hair_pifu_dict["名称"] = hair_pifu_name
                    self.hair_pifu_list.append(hair_pifu_dict)
                    print(self.hair_pifu_list)
                else:
                    continue
            self.huadong_hair_next()
            sleep(1)

    def get_grid_positions(self,total=27):
        """
        获取指定数量的网格位置坐标

        Args:
            total: 总数量，默认 50 个
        """
        x_start, y_start = 145, 360
        x_step = 105
        y_step = 120
        cols = 5

        positions = []
        for index in range(total):
            row = index // cols
            col = index % cols
            x = x_start + col * x_step
            y = y_start + row * y_step
            positions.append((x, y))

        return positions

    def gold_or_red_pifu(self,pifu_list):
        red_pifu_list = []
        gold_pifu_list = []
        for pifu_dict in pifu_list:
            pifu_image= snapshot_write(read_name=str(self.image_path / pifu_dict["属性图片"]))
            pifu_image = EditImage(pifu_image).resize((120, 0))
            if pifu_dict["稀有度"] == "金":
                beijing_image = np.array(Image.open(str(self.image_path / "金装背景.png")).convert('RGBA'))
                beijing_image = cv2.cvtColor(beijing_image, cv2.COLOR_BGRA2RGBA)
                beijing_image = cv2.resize(beijing_image,image_size(pifu_image))
                pifu_image= EditImage(pifu_image).images_fill_alpha(((0, 0), beijing_image))
                _, pifu_path = snapshot_write(needPath=True, image=pifu_image,
                                              write_name=f"金装武器/{pifu_dict['名称']}")
                gold_pifu_list.append({"图片": pifu_image, "名称": pifu_dict["名称"], "属性图片": pifu_path, "稀有度": pifu_dict["稀有度"]})

            elif pifu_dict["稀有度"] == "红":
                beijing_image = np.array(Image.open(str(self.image_path / "红装背景.png")).convert('RGBA'))
                beijing_image = cv2.cvtColor(beijing_image, cv2.COLOR_BGRA2RGBA)
                beijing_image = cv2.resize(beijing_image,image_size(pifu_image))
                pifu_image= EditImage(pifu_image).images_fill_alpha(((0, 0), beijing_image))
                _, pifu_path = snapshot_write(needPath=True, image=pifu_image,
                                              write_name=f"金装武器/{pifu_dict['名称']}")
                red_pifu_list .append({"图片": pifu_image, "名称": pifu_dict["名称"], "属性图片": pifu_path, "稀有度": pifu_dict["稀有度"]})

        return red_pifu_list,gold_pifu_list



    def merge_suoyou_pic(self,hero_name):
        hero_pifu_list = []
        hero_pifu_list.append(self.hero_pifu_all_pic.get("服装合图"))
        hero_pifu_list.append(self.hero_pifu_all_pic.get("发型合图"))
        hero_pifu_list.append(self.hero_pifu_all_pic.get("奥义合图"))
        all_image=combine_images_write(images=hero_pifu_list, write_name="英雄最终合图")
        snapshot_write(write_name=f"$_英雄{hero_name}皮肤合图",image= all_image[0],sn=11264010)

    def merge_hair_pifu_pic(self,hero_name):
        if len(self.hair_pifu_list) == 0:
            return
        biaoti_image = snapshot_write(read_name=str(self.image_path / "标题背景.png"))

        # 确保两张图通道数一致（都转为 RGBA）
        if isinstance(biaoti_image, np.ndarray):
            if biaoti_image.shape[-1] == 3:
                biaoti_image = cv2.cvtColor(biaoti_image, cv2.COLOR_RGB2RGBA)


        biaoti_image = EditImage(biaoti_image).resize((940, 0))
        pos_text = (460, 5)
        text = "发型"
        biaoti_image = image_multiline_text(
            biaoti_image,
            text,
            font_size=30,
            textPoint=pos_text,
            center_alignment=True,
            font_path=self.font_path
        )

        # 确保文字处理后的图片也是 RGBA 四通道
        if isinstance(biaoti_image, np.ndarray):
            if biaoti_image.shape[-1] == 3:
                biaoti_image = cv2.cvtColor(biaoti_image, cv2.COLOR_RGB2RGBA)

        # biaoti_image=snapshot_write(read_name=str(self.image_path /  "发型标题.png"))
        red_hari_pifu_list,gold_hair_pifu_list=self.gold_or_red_pifu(self.hair_pifu_list)
        pifu_kuozhan_list = self.merge_pic_list(red_hari_pifu_list, gold_hair_pifu_list,str(self.image_path /  "背景图扩展.png"))
        pifu_kuozhan_list.insert(0,biaoti_image)
        pifu_kuozhan_list = self.images_resize(pifu_kuozhan_list, 1000)
        pifu_kuozhan_images = combine_images_write(images=pifu_kuozhan_list, write_name="发型皮肤拓展合图")

        _, pifu_path = snapshot_write(write_name=f"完整发型合图/{hero_name}", image=pifu_kuozhan_images[0],
                                      needPath=True)
        self.hero_pifu_all_pic["发型合图"] = pifu_path

    def merge_pic_list(self,red_ist,gold_ist,image_path):
        pifu_kuozhan_list = []
        combined_list = red_ist + gold_ist
        if len(combined_list) > 8:
            # 按 14 个分块
            chunk_size = 8
            chunks = []
            for i in range(0, len(combined_list), chunk_size):
                chunk = combined_list[i:i + chunk_size]
                chunks.append(chunk)
            for chunk in chunks:
                self.pifu_merge_pic(chunk, pifu_kuozhan_list,
                                    snapshot_write(read_name=image_path), 41, 15)
        else:
            self.pifu_merge_pic(combined_list, pifu_kuozhan_list,
                                snapshot_write(read_name=image_path), 41, 15)
        return pifu_kuozhan_list

    def merge_aoyi_pic(self,hero_name):
        if len(self.hero_aoyi_list) == 0:
            return
        biaoti_image= snapshot_write(read_name=str(self.image_path / "标题背景.png"))
        red_aoyi_pifu_list, gold_aoyi_pifu_list=self.gold_or_red_pifu(self.hero_aoyi_list)
        pifu_kuozhan_list  =self.merge_pic_list(red_aoyi_pifu_list, gold_aoyi_pifu_list,str(self.image_path / "背景图扩展.png"))


        # 确保两张图通道数一致（都转为 RGBA）
        if isinstance(biaoti_image, np.ndarray):
            if biaoti_image.shape[-1] == 3:
                biaoti_image = cv2.cvtColor(biaoti_image, cv2.COLOR_RGB2RGBA)

        biaoti_image = EditImage(biaoti_image).resize((940, 0))
        pos_text = (460, 5)
        text = "奥义"
        biaoti_image  = image_multiline_text(
            biaoti_image ,
            text,
            font_size=30,
            textPoint=pos_text,
            center_alignment=True,
            font_path=self.font_path
        )

        # 确保文字处理后的图片也是 RGBA 四通道
        if isinstance(biaoti_image, np.ndarray):
            if biaoti_image.shape[-1] == 3:
                biaoti_image = cv2.cvtColor(biaoti_image, cv2.COLOR_RGB2RGBA)
        pifu_kuozhan_list.insert(0,biaoti_image)
        pifu_kuozhan_list = self.images_resize(pifu_kuozhan_list, 1000)
        pifu_kuozhan_images = combine_images_write(images=pifu_kuozhan_list, write_name="奥义皮肤拓展合图")

        _, pifu_path = snapshot_write(write_name=f"完整奥义合图/{hero_name}", image=pifu_kuozhan_images[0],
                                      needPath=True)
        self.hero_pifu_all_pic["奥义合图"] = pifu_path

    def generate_hero_cover(self, hero_fengmian_bash_image, biaoti):

        biaoti_beijing_image = snapshot_write(read_name=str(self.image_path / "标题背景.png"))
        beijing_image = snapshot_write(read_name=str(self.image_path / "背景封面.png"))

        # 确保两张图通道数一致（都转为 RGBA）
        if isinstance(biaoti_beijing_image, np.ndarray):
            if biaoti_beijing_image.shape[-1] == 3:
                biaoti_beijing_image = cv2.cvtColor(biaoti_beijing_image, cv2.COLOR_RGB2RGBA)

        # 确保两张图通道数一致（都转为 RGBA）
        if isinstance(beijing_image, np.ndarray):
            if beijing_image.shape[-1] == 3:
                beijing_image = cv2.cvtColor(beijing_image, cv2.COLOR_RGB2RGBA)

        # 确保两张图通道数一致（都转为 RGBA）
        if isinstance(hero_fengmian_bash_image, np.ndarray):
            if hero_fengmian_bash_image.shape[-1] == 3:
                hero_fengmian_bash_image = cv2.cvtColor(hero_fengmian_bash_image, cv2.COLOR_RGB2RGBA)

        hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).resize((224,0))
        biaoti_beijing_image = EditImage(biaoti_beijing_image).resize((938,0))
        beijing_image = EditImage(beijing_image).resize((1000,0))
        pos_text = (460, 5)
        text = biaoti
        fuzhuang_pifu = image_multiline_text(
            biaoti_beijing_image,
            text,
            font_size=30,
            textPoint=pos_text,
            center_alignment=True,
            font_path=self.font_path
        )

        # 确保文字处理后的图片也是 RGBA 四通道
        if isinstance(fuzhuang_pifu, np.ndarray):
            if fuzhuang_pifu.shape[-1] == 3:
                fuzhuang_pifu = cv2.cvtColor(fuzhuang_pifu, cv2.COLOR_RGB2RGBA)

        finishi_beijing_image = EditImage(beijing_image).images_fill(
            ((28, 15), fuzhuang_pifu))
        finishi_beijing_image = EditImage(finishi_beijing_image).images_fill(
            ((28, 70), hero_fengmian_bash_image))
        snapshot_write(write_name=biaoti, image=finishi_beijing_image)
        return finishi_beijing_image

    def merge_hero_pifu_pic(self,hero_name):
        hero_pifu_pic_dict = {

            "万钧": "封面万钧.png",
            "刘炼": "封面刘炼.png",
            "哈迪": "封面哈迪.png",
            "天海": "封面天海.png",
            "季沧海": "封面季沧海.png",
            "季莹莹": "封面季莹莹.png",
            "宁红夜": "封面宁红夜.png",
            "岳山": "封面岳山.png",
            "崔三娘": "封面崔三娘.png",
            "巫真": "封面巫真.png",
            "席拉": "封面席拉.png",
            "无尘": "封面无尘.png",
            "武田信忠": "封面武田信忠.png",
            "特木尔": "封面特木尔.png",
            "玉玲珑": "封面玉玲珑.png",
            "土御门胡桃": "封面胡桃.png",
            "蓝梦": "封面蓝梦.png",
            "迦南": "封面迦南.png",
            "顾清寒": "封面顾清寒.png",
            "魏轻": "封面魏轻.png",
            "沈妙": "封面沈妙.png",
            "李寻欢": "封面李寻欢.png",
            "张起灵": "封面张起灵.png",
            "妖刀姬": "封面妖刀姬.png",
            "殷紫萍": "封面殷紫萍.png",
            "胡为": "封面胡为.png"

        }
        monitor_catch(f"英雄{hero_name}封面生成中")
        hero_fengmian_bash_image = snapshot_write(read_name=str(self.image_path/hero_pifu_pic_dict[hero_name]))
        # 封面图生成
        hero_fengmian_bash_image = self.generate_hero_cover(hero_fengmian_bash_image,"英雄皮肤")

        hong_pifu_image_list,jin_pifu_image_list=self.gold_or_red_pifu(self.hero_fuzhuang_list)
        # all_shizhuang_red_pifu_list.extend(hong_pifu_image_list)
        # all_shizhuang_gold_pifu_list.extend(jin_pifu_image_list)
        add_red_and_gold_fuzhuang_pifu(hong_pifu_image_list, jin_pifu_image_list)
        left = 0
        high = 0
        combined_list = hong_pifu_image_list + jin_pifu_image_list
        new_pifu_list= combined_list if len( combined_list) < 13 else  combined_list[:12]

        for pifu in new_pifu_list:

            fuzhuang_pifu = pifu["图片"]
            #阿里妈妈字体导入

            pos_text = (60, 140)
            text = pifu["名称"]
            fuzhuang_pifu = image_multiline_text(
                fuzhuang_pifu,
                text,
                font_size=12,
                textPoint=pos_text,
                center_alignment=True,
                font_path=self.font_path
            )
            # 确保两张图通道数一致（都转为 RGBA）
            fuzhuang_pifu,hero_fengmian_bash_image =format_image(fuzhuang_pifu,hero_fengmian_bash_image)


            fuzhuang_pifu= EditImage(fuzhuang_pifu).resize((112, 0))

            hero_fengmian_bash_image= EditImage(hero_fengmian_bash_image).resize((1000,0))


            hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).images_fill(((274+left,70+high), fuzhuang_pifu))
            left += 116
            if left > 580:
                left = 0
                high += 175

        pifu_kuozhan_list = [hero_fengmian_bash_image]
        if len(combined_list) > 12:
            remaining_pifu_list = combined_list[12:]
            if len(remaining_pifu_list) >8:
                # 按 14 个分块
                chunk_size = 8
                chunks = []
                for i in range(0, len(remaining_pifu_list), chunk_size):
                    chunk = remaining_pifu_list[i:i + chunk_size]
                    chunks.append(chunk)
                for chunk in chunks:
                    self.pifu_merge_pic(chunk, pifu_kuozhan_list,snapshot_write(read_name=str(self.image_path / "扩展图.png")),41,15)
            else:
                self.pifu_merge_pic(remaining_pifu_list,pifu_kuozhan_list,snapshot_write(read_name=str(self.image_path / "扩展图.png")),41,15)
        pifu_kuozhan_list = self.images_resize(pifu_kuozhan_list,1000)
        pifu_kuozhan_images =combine_images_write(images=pifu_kuozhan_list, write_name="服装皮肤拓展合图")

        _,pifu_path=snapshot_write(write_name=f"完整皮肤合图/{hero_name}", image=pifu_kuozhan_images[0],needPath= True)
        self.hero_pifu_all_pic["服装合图"] = pifu_path

    def images_resize(self,imags,resiz):
        new_images = []
        for image in imags:
            if isinstance(image, np.ndarray):
                if image.shape[-1] == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            new_image= EditImage(image).resize((resiz, 0))
            new_images.append(new_image)
        return new_images

    def pifu_merge_pic(self, remaining_pifu_list,pifu_kuozhan_list,hero_fengmian_bash_image,x,y):
        left = 0

        # 确保两张图通道数一致（都转为 RGBA）
        if isinstance(hero_fengmian_bash_image, np.ndarray):
            if hero_fengmian_bash_image.shape[-1] == 3:
                hero_fengmian_bash_image = cv2.cvtColor(hero_fengmian_bash_image, cv2.COLOR_RGB2RGBA)

        for pifu in remaining_pifu_list:
            fuzhuang_pifu = pifu["图片"]
            pos_text = (60, 140)
            text = pifu["名称"]
            fuzhuang_pifu = image_multiline_text(
                fuzhuang_pifu,
                text,
                font_size=15,
                textPoint=pos_text,
                center_alignment=True,
                font_path=self.font_path
            )
            fuzhuang_pifu,hero_fengmian_bash_image = format_image(fuzhuang_pifu,hero_fengmian_bash_image)
            fuzhuang_pifu = EditImage(fuzhuang_pifu).resize((112, 0))
            hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).resize((1000,0))

            hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).images_fill(
                ((x + left, y), fuzhuang_pifu))
            left += 116
        pifu_kuozhan_list.append(hero_fengmian_bash_image)


@PopupHandler()
class WeaponEquipmentCollector:
    """武器装备采集"""
    def __init__(self):
        self.json_path = gameDir.parent / '11264_netease/皮肤属性_备份.json'
        self.image_url = gameDir.parent / '11264_netease/属性图片.json'
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.pifu_data = json.load(f)
        self.wuqi_data = self.pifu_data["武器"]
        with open(self.image_url, 'r', encoding='utf-8') as f:
            self.pifu_image_url = json.load(f)
        self.image_path = gameDir / "materials_icons"
        self.font_path = str(gameDir.parent / '11264_netease/Alimamakaishu/AlimamaDongFangDaKai-Regular.otf')
        self.wuqi_pifu_list= []
        self.wuqi_type_list= set()
        self.merge_wuqi_hetu_list=[]
        self.finish_wuqi_pifu_list = []
        self.wuqi_leixing_list = [
            (330,360),
            (330,540),
            (330,720),
            # (330,900),
        ]
        self.jinzhan_wuqi_list=[
            (330, 360),
            (330, 540),
            (330, 720),
        ]


        self.wuqi_path_list = [
            {"path": (380, 270), "color": {"LT": (104, 270), "RB": (106, 273)}},
            {"path": (380, 360), "color": {"LT": (104, 360), "RB": (106, 363)}},
            {"path": (380, 450), "color": {"LT": (104, 450), "RB": (106, 453)}},
            {"path": (380, 540), "color": {"LT": (104, 540), "RB": (106, 543)}},
            {"path": (380, 630), "color": {"LT": (104, 630), "RB": (106, 633)}},
            {"path": (380, 720), "color": {"LT": (104, 720), "RB": (106, 723)}},
            {"path": (380, 810), "color": {"LT": (104, 810), "RB": (106, 813)}},
            {"path": (380, 900), "color": {"LT": (104, 800), "RB": (106, 903)}},
            {"path": (380, 990), "color": {"LT": (104, 990), "RB": (106, 993)}},
            {"path": (380, 1080), "color": {"LT": (104, 1080), "RB": (106, 1083)}},
            {"path": (380, 1170), "color": {"LT": (104, 1170), "RB": (106, 1173)}}
        ]
    def __call__(self):
        # 武器装备采集逻辑
        self.touch_wuqi()
        self.yuancheng_wuqi()
        self.jinzhan_wuqi()
        self.wuqi_hetu_merge()
        self.upload_properties()

    def upload_properties(self):
        if len(self.finish_wuqi_pifu_list) == 0:
            return
        new_pifu_list = []
        for wuqi_pifu in self.finish_wuqi_pifu_list:
            if self.pifu_image_url.get(wuqi_pifu["名称"]) is not None:
                wuqi_pifu["属性图片"] = str(self.pifu_image_url[wuqi_pifu["名称"]])
            else:
                wuqi_pifu["属性图片"] =  str(self.pifu_image_url["默认背景"])
            wuqi_pifu["属性图片"] = str(url_parse(wuqi_pifu["属性图片"]).path)
            new_pifu_list.append(wuqi_pifu)
        property_write("武器皮肤", self.finish_wuqi_pifu_list)
        monitor_catch("武器属性采集完成", )
    def wuqi_hetu_merge(self):
        wuqi_hetu_list = []
        for wuqi_path in self.merge_wuqi_hetu_list:
            hetu_image = snapshot_write(read_name=str(wuqi_path))
            wuqi_hetu_list.append(hetu_image)
        if not wuqi_hetu_list:
            return
        combine_images_write(images=wuqi_hetu_list, write_name="$_武器皮肤最终合图",sn=11264011)
    def touch_wuqi(self):
        for i in range(3):
            air_touch((935,42))
            sleep(1)
            if find_tpl("tpl20260320100009.png",image=snapshot_write()):
                return

    def yuancheng_wuqi(self):
        wuqi_type_list = []
        air_touch((220, 250))
        is_next = False
        for i in range(15):
            if not is_next:
                for wuqi in self.wuqi_leixing_list:
                    air_touch(wuqi)
                    if find_tpl_touch("tpl20260316103551.png", desc="点击武器外观",area=(188,1112,590,1240)):
                        wuqi_type = self.get_wuqi_type(True)
                        if wuqi_type in wuqi_type_list:
                            air_touch((2285, 1314))
                            continue
                        wuqi_type_list.append(wuqi_type)
                        self.get_wuqi_pifu(wuqi_type,True)
                        self.finish_wuqi_pifu_list.extend(self.wuqi_pifu_list)
                        self.merge_wuqi_pic(wuqi_type, self.wuqi_pifu_list)
                        self.cler_wuqi_pifu_list()
                        monitor_catch(f"{wuqi_type}采集完毕", f"已采集{len(wuqi_type_list)}个武器")
                    else:
                        self.is_yuancheng_wuqi()
                is_next = True
            air_touch((305, 890))
            if find_tpl_touch("tpl20260316103551.png", desc="点击武器外观",area=(188,1112,590,1240)):
                wuqi_type = self.get_wuqi_type(True)
                if wuqi_type in wuqi_type_list:
                    air_touch((2285, 1314))
                    continue
                wuqi_type_list.append(wuqi_type)
                self.get_wuqi_pifu(wuqi_type, True)
                self.finish_wuqi_pifu_list.extend(self.wuqi_pifu_list)
                self.merge_wuqi_pic(wuqi_type, self.wuqi_pifu_list)
                self.cler_wuqi_pifu_list()
                monitor_catch(f"{wuqi_type}采集完毕", f"已采集{len(wuqi_type_list)}个武器")
                if len(wuqi_type_list) >= 8 or wuqi_type == "喷火器":
                    return
            else:
                self.is_yuancheng_wuqi()

            # air_touch((2285, 1314))
    def is_yuancheng_wuqi(self):
        for i in range(3):
            if find_tpl("tpl20260316150349.png", image=snapshot_write(), desc="重制武器界面",
                        area=area_rb):
                monitor_catch(f"状态检测", "未进入武器界面，重新进入")
                air_touch((2340, 1318))
                sleep(1)
                air_touch((940, 45))
                sleep(1)
                air_touch((220, 250))
                return
            else:
                air_touch((940, 45))
                sleep(1)
                air_touch((220, 250))
                return
    def is_jinzhan_wuqi(self):
        for i in range(3):
            if find_tpl("tpl20260316150349.png", image=snapshot_write(), desc="重制武器界面",
                        area=area_rb):
                monitor_catch(f"状态检测", "未进入武器界面，重新进入")
                air_touch((2340, 1318))
                sleep(1)
                air_touch((940, 45))
                sleep(1)
                air_touch((460, 250))
                return
            else:
                air_touch((940, 45))
                sleep(1)
                air_touch((460, 250))
                return
    def jinzhan_wuqi(self):
        wuqi_type_list = []
        air_touch((460, 250))
        sleep(1)
        is_next = False
        for i in range(30):
            if not is_next:
                for wuqi in self.jinzhan_wuqi_list:
                    air_touch(wuqi)
                    if find_tpl_touch("tpl20260316103551.png", desc="点击武器外观",area=(188,1112,590,1240)):
                        wuqi_type = self.get_wuqi_type(False)
                        if wuqi_type in wuqi_type_list  :
                            air_touch((2285, 1314))
                            continue
                        wuqi_type_list.append(wuqi_type)
                        self.get_wuqi_pifu(wuqi_type,False)
                        self.finish_wuqi_pifu_list.extend(self.wuqi_pifu_list)
                        self.merge_wuqi_pic(wuqi_type,self.wuqi_pifu_list)
                        self.cler_wuqi_pifu_list()
                        monitor_catch(f"{wuqi_type}采集完毕", f"已采集{len(wuqi_type_list)}个武器")
                    else:
                        self.is_jinzhan_wuqi()
                    # air_touch((2285, 1314))
                is_next = True
            air_touch((330, 890))
            if find_tpl_touch("tpl20260316103551.png", desc="点击武器外观",area=(188,1112,590,1240)):
                wuqi_type = self.get_wuqi_type(False)
                if wuqi_type in wuqi_type_list:
                    air_touch((2285, 1314))
                    continue
                wuqi_type_list.append(wuqi_type)
                self.get_wuqi_pifu(wuqi_type, False)
                self.finish_wuqi_pifu_list.extend(self.wuqi_pifu_list)
                self.merge_wuqi_pic(wuqi_type, self.wuqi_pifu_list)
                self.cler_wuqi_pifu_list()
                monitor_catch(f"{wuqi_type}采集完毕", f"已采集{len(wuqi_type_list)}个武器")
                if len(wuqi_type_list) >= 16 or wuqi_type == "万刃轮":
                    return
            else:
                self.is_jinzhan_wuqi()
            # air_touch((2285, 1314))

    def get_wuqi_type(self,is_yuancheng=False):
        wuqi_type = snapshot_ocr(LT=(1788, 300), RB=(2000, 355), image=snapshot_write(),
                                 desc="识别武器类型")
        if not is_yuancheng:
            return wuqi_type
        if "双" in wuqi_type or "双统" == wuqi_type:
            return "双铳"
        if "鸟" in wuqi_type or"鸟统" == wuqi_type:
            return "鸟铳"
        if "五眼" in wuqi_type:
            return "五眼铳"
        return wuqi_type

    def get_unlocked_wuqi(self):
        unlocked_list = []
        x = 225
        y = 300
        image = snapshot_write()
        for i in range(11):
            hero_pifu_dict = {}
            if find_tpl("tpl20260323234153.png", image=image, area=(485, x, 570, y),threshold=0.7):
                x += 90
                y += 90
                continue

            wuqi_name = snapshot_ocr(LT=(160, x), RB=(485, y), image=image)
            hero_pifu_dict["名称"]= wuqi_name
            if self.wuqi_data.get(wuqi_name):
                hero_pifu_dict["品质"] = self.wuqi_data.get(wuqi_name)
            else:
                if find_tpl("tpl20260324170835.png",image=image,area=(100, x,175, y),threshold=0.7,desc="稀有度为红的相似度"):
                    hero_pifu_dict["品质"] = "红"
                elif find_tpl("tpl20260324171020.png",image=image,area=(100, x,170, y),threshold=0.7,desc="稀有度为金的相似度"):
                    hero_pifu_dict["品质"] = "金"
                else:
                    # this_color = snapshot_color(LT=wuqi["color"]["LT"], RB=wuqi["color"]["RB"], image=image)
                    # if 0 < this_color["h"] < 20:
                    #     hero_pifu_dict["稀有度"] = "红"
                    # elif 20 < this_color["h"] < 50:
                    #     hero_pifu_dict["稀有度"] = "金"
                    # else:
                    #     hero_pifu_dict["稀有度"] = "紫色"
                    #     unlocked_list.append(hero_pifu_dict)
                    #     return unlocked_list
                    hero_pifu_dict["品质"] = "紫"
                    unlocked_list.append(hero_pifu_dict)
                    return unlocked_list
            unlocked_list.append(hero_pifu_dict)
            x += 90
            y += 90
        return unlocked_list

    def get_wuqi_pifu(self, wuqi_type, is_yuancheng):
        self.huadong_wuqi_next(start_point=(380, 500), end_point=(380, 1200))
        wuqi_name_list =[]
        for i in range(3):
            unlocked_wuqi_list = self.get_unlocked_wuqi()
            for pifu in unlocked_wuqi_list:
                pifu_dict = {
                    "武器": wuqi_type,
                    "品质": "",
                    "名称": "",
                    "属性图片": ""
                }
                if pifu.get("品质") not in ("红" ,"金"):
                    air_touch((2345, 1325))
                    return
                pifu_dict["品质"] = pifu["品质"]
                pifu_name = pifu["名称"]
                pifu_dict["名称"] = pifu_name
                if pifu_name in wuqi_name_list:
                    continue
                wuqi_name_list.append(pifu_name)
                # result = snapshot_ocr(LT=(2260, 1300), RB=(2370, 1340), image=snapshot_write())
                # if "展开" in result or "列表" in result:
                #     air_touch((2280, 1310))
                #     sleep(1)
                # image = snapshot_write()
                # pifu_name = snapshot_ocr(LT=(1795, 220), RB=(2350, 280), image=image)

                if self.pifu_image_url.get(pifu_name) :
                    wuqi_image = snapshot_write(read_name=str(self.pifu_image_url.get(pifu_name)),desc="属性库存在图片")
                else:
                    wuqi_image = snapshot_write(read_name=str(self.image_path /  f"默认背景.png"),desc="属性库不存在")
                wuqi_image = cv2.resize(wuqi_image, (200, 280))


                pifu_dict["名称"] = pifu_name
                _, w_path = snapshot_write(image=wuqi_image, write_name=f"{pifu_dict['武器']}皮肤/{pifu_name}", needPath=True)
                pifu_dict["属性图片"] = str(w_path)
                self.wuqi_pifu_list.append(pifu_dict)
                print(self.wuqi_pifu_list)

            self.huadong_wuqi_next(start_point=(380, 1170), end_point=(380, 290),is_next=True)
        air_touch((2345, 1325))

    def huadong_wuqi_next(self,start_point,end_point,is_next=False):
        pre_image = None
        for i in range(8):
            air_touch(start_point)
            sleep(1)
            result = snapshot_ocr(LT=(2260, 1300), RB=(2370, 1340), image=snapshot_write())
            if "展开" in result or "列表" in result:
                air_touch((2280, 1310))
                sleep(3)
            air_swipe_fast(start_point=start_point, end_point=end_point, sec=0.1)
            air_touch((724, 275))
            this_image = snapshot_write(LT=(100, 220), RB=(580, 350))
            if is_next:
                return
            if pre_image is not None and snapshot_match(image=pre_image, match_image=this_image, threshold=0.5):
                return
            pre_image = this_image

    def merge_wuqi_pic(self,wiqi_type,wuqi_pifu_list):
        if len(wuqi_pifu_list) == 0:
            return
        pifu_kuozhan_list = []
        self.get_wuqi_fengmian(wiqi_type,pifu_kuozhan_list)
        red_pifu_list,gold_pifu_list=self.gold_or_red_pifu(wuqi_pifu_list)
        add_red_and_gold_wuqi_pifu(red_pifu_list, gold_pifu_list)
        # all_wuqi_red_pifu_list.extend(red_pifu_list)
        # all_wuqi_gold_pifu_list.extend(gold_pifu_list)
        combined_list = red_pifu_list + gold_pifu_list
        if len(combined_list) > 8:
            # 按 14 个分块
            chunk_size = 8
            chunks = []
            for i in range(0, len(combined_list), chunk_size):
                chunk = combined_list[i:i + chunk_size]
                chunks.append(chunk)
            for chunk in chunks:
                self.pifu_merge_pic(chunk, pifu_kuozhan_list, 41, 15)
        else:
            self.pifu_merge_pic(combined_list, pifu_kuozhan_list, 41, 15)
        pifu_kuozhan_list = self.images_resize(pifu_kuozhan_list,1000)
        pifu_kuozhan_images = combine_images_write(images=pifu_kuozhan_list, write_name="武器皮肤拓展合图")
        _,wuqi_path = snapshot_write(write_name=f"武器皮肤合图/{wiqi_type}皮肤合图",image=pifu_kuozhan_images[0],needPath=True)
        self.merge_wuqi_hetu_list.append(wuqi_path)

    def images_resize(self,imags,resiz):
        new_images = []
        for image in imags:
            if isinstance(image, np.ndarray):
                if image.shape[-1] == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            new_image= EditImage(image).resize((resiz, 0))
            new_images.append(new_image)
        return new_images

    def gold_or_red_pifu(self,pifu_list):
        red_pifu_list = []
        gold_pifu_list = []
        for pifu_dict in pifu_list:
            pifu_image= snapshot_write(read_name=str(pifu_dict["属性图片"]))
            pifu_image = cv2.resize(pifu_image, (200, 280))
            pifu_image = EditImage(pifu_image).resize((120, 0))
            if pifu_dict["品质"] == "金":
                beijing_image = np.array(Image.open(str(self.image_path / "金装背景.png")).convert('RGBA'))
                beijing_image = cv2.cvtColor(beijing_image, cv2.COLOR_BGRA2RGBA)
                beijing_image = cv2.resize(beijing_image, image_size(pifu_image))
                pifu_image= EditImage(pifu_image).images_fill_alpha(((0, 0), beijing_image))
                _, pifu_path=snapshot_write(needPath= True,image=pifu_image,write_name=f"金装武器/{pifu_dict['名称']}")
                gold_pifu_list.append({"图片": pifu_image, "名称": pifu_dict["名称"],"属性图片":pifu_path,"品质":"金"})
            elif pifu_dict["品质"] == "红":
                beijing_image = np.array(Image.open(str(self.image_path / "红装背景.png")).convert('RGBA'))
                beijing_image = cv2.cvtColor(beijing_image, cv2.COLOR_BGRA2RGBA)
                beijing_image = cv2.resize(beijing_image, image_size(pifu_image))
                pifu_image= EditImage(pifu_image).images_fill_alpha(((0, 0), beijing_image))
                _, pifu_path=snapshot_write(needPath= True,image=pifu_image,write_name=f"红装武器/{pifu_dict['名称']}")
                red_pifu_list.append({"图片": pifu_image, "名称": pifu_dict["名称"],"属性图片":pifu_path,"品质":"红"})
        return red_pifu_list,gold_pifu_list

    def pifu_merge_pic(self, remaining_pifu_list, pifu_kuozhan_list, x, y):
            left = 0
            hero_fengmian_bash_image = snapshot_write(read_name=str(self.image_path / "扩展图.png"))

            # 确保两张图通道数一致（都转为 RGBA）
            if isinstance(hero_fengmian_bash_image, np.ndarray):
                if hero_fengmian_bash_image.shape[-1] == 3:
                    hero_fengmian_bash_image = cv2.cvtColor(hero_fengmian_bash_image, cv2.COLOR_RGB2RGBA)

            for pifu in remaining_pifu_list:
                fuzhuang_pifu = pifu["图片"]
                pos_text = (60, 140)
                text = pifu["名称"]
                fuzhuang_pifu = image_multiline_text(
                    fuzhuang_pifu,
                    text,
                    font_size=15,
                    textPoint=pos_text,
                    center_alignment=True,
                    font_path=self.font_path
                )
                fuzhuang_pifu, hero_fengmian_bash_image = format_image(fuzhuang_pifu, hero_fengmian_bash_image)
                fuzhuang_pifu = EditImage(fuzhuang_pifu).resize((109, 148))
                hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).resize((1000,0))

                hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).images_fill(
                    ((x + left, y ), fuzhuang_pifu))
                left += 116
            hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).resize((1000, 0))
            snapshot_write(write_name="皮肤合图",image=hero_fengmian_bash_image)
            pifu_kuozhan_list.append(hero_fengmian_bash_image)

    def get_wuqi_fengmian(self,wiqi_type,pic_list):
        wuqi_biaoti = f"武器·{wiqi_type}"
        biaoti_image = snapshot_write(read_name=str(self.image_path / "武器类型封面.png"))
        biaoti_image = EditImage(biaoti_image).resize((1000, 0))
        pos_text = (460, 5)
        biaoti_image = image_multiline_text(
            biaoti_image,
            wuqi_biaoti,
            font_size=30,
            textPoint=pos_text,
            center_alignment=True,
            font_path=self.font_path
        )
        pic_list.append(biaoti_image)

    def cler_wuqi_pifu_list(self):
        self.wuqi_pifu_list = []



class CoverCollector:
    """封面合图采集"""

    def __init__(self):
        self.cover_images = []
        self.image_path = gameDir / "materials_icons"
        self.font_path = str(gameDir.parent / '11264_netease/Alimamakaishu/AlimamaDongFangDaKai-Regular.otf')
        self.shizhuang_fengmian=None
        self.wuqi_fengmian = None
    def __call__(self):
        # 封面合图逻辑
        self.get_all_pifu_list()
    def get_all_pifu_list(self):
        try:
            self.get_shizhuang_pifu_list(all_shizhuang_red_pifu_list, all_shizhuang_gold_pifu_list)
            self.get_wuqi_pifu_list(all_wuqi_red_pifu_list, all_wuqi_gold_pifu_list)
        except Exception as e:
            monitor_catch(f"大合图失败", e)
    def add_text_to_image(self,image_text,image,pos):
        pos_text = pos
        image = image_multiline_text(
            image,
            image_text,
            font_size=15,
            textPoint=pos_text,
            center_alignment=True,
            font_path=self.font_path
        )
        return image
    def get_shizhuang_pifu_list(self, all_shizhuang_red_pifu_list, all_shizhuang_gold_pifu_list):
        all_shizhuang_pifu_list =all_shizhuang_red_pifu_list + all_shizhuang_gold_pifu_list
        hero_fengmian_bash_image = snapshot_write(read_name=str(self.image_path / "背景封面.png"))
        shizhuang_tianchong = {"图片": snapshot_write(read_name=str(self.image_path / '时装填充.png')),
                               "名称": "" if len(all_shizhuang_pifu_list) <14 else f"+{len(all_shizhuang_pifu_list) - 14}",
                               "end_image":True
                               }

        if len(all_shizhuang_pifu_list) >= 15:
            shizhuang_list = all_shizhuang_pifu_list[:14]
            shizhuang_list.append(shizhuang_tianchong)
        else:
            num = 15 - len(all_shizhuang_pifu_list)
            for i in range(num):
                all_shizhuang_pifu_list.append(shizhuang_tianchong)
            shizhuang_list = all_shizhuang_pifu_list

        x =15
        y = 25
        for shizhuang in shizhuang_list:
            if shizhuang.get("end_image"):
                fuzhuang_pifu = shizhuang["图片"]
                pos_text = (43, 55)
                font_size = 26
                font_path = ENV.rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'
            else:
                fuzhuang_pifu = snapshot_write(read_name=str(shizhuang.get("属性图片")))
                pos_text = (60, 140)
                font_size = 12
                font_path = self.font_path
            text =shizhuang.get("名称", "")
            fuzhuang_pifu = image_multiline_text(
                fuzhuang_pifu,
                text,
                font_size=font_size,
                textPoint=pos_text,
                center_alignment=True,
                font_path=font_path
            )
            fuzhuang_pifu, hero_fengmian_bash_image = format_image(fuzhuang_pifu, hero_fengmian_bash_image)
            fuzhuang_pifu = cv2.resize(fuzhuang_pifu, (100, 152))
            hero_fengmian_bash_image =cv2.resize(hero_fengmian_bash_image, (1000, 520))
            hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).images_fill(
                ((x, y), fuzhuang_pifu))
            x += 120
            if x >= 120*5:
                x = 15
                y += 160

        snapshot_write(image=hero_fengmian_bash_image, write_name="时装封面大合图.png")
        self.shizhuang_fengmian = hero_fengmian_bash_image

    def get_wuqi_pifu_list(self, all_wuqi_red_pifu_list, all_wuqi_gold_pifu_list):
        all_wuqi_pifu_list = all_wuqi_red_pifu_list + all_wuqi_gold_pifu_list
        hero_fengmian_bash_image = self.shizhuang_fengmian
        shizhuang_tianchong = {"图片": snapshot_write(read_name=str(self.image_path / '武器填充.png')),
                               "名称": "" if len(all_wuqi_pifu_list) <9 else f"+{len(all_wuqi_pifu_list) - 9}",
                               "end_image": True
                               }

        if len(all_wuqi_pifu_list) >= 9:
            shizhuang_list = all_wuqi_pifu_list[:8]
            shizhuang_list.append(shizhuang_tianchong)
        else:
            num = 9 - len(all_wuqi_pifu_list)
            for i in range(num):
                all_wuqi_pifu_list.append(shizhuang_tianchong)
            shizhuang_list=all_wuqi_pifu_list
        x = 15
        y = 25
        for shizhuang in shizhuang_list:
            print(shizhuang)
            if shizhuang.get("end_image"):
                fuzhuang_pifu = shizhuang["图片"]
                pos_text = (43, 55)
                font_size = 26
                font_path =ENV.rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'
            else:
                fuzhuang_pifu = snapshot_write(read_name=str(shizhuang.get("属性图片")))
                pos_text = (60, 140)
                font_size = 12
                font_path = self.font_path
            text = shizhuang.get("名称", "")
            fuzhuang_pifu = image_multiline_text(
                fuzhuang_pifu,
                text,
                font_size=font_size,
                textPoint=pos_text,
                center_alignment=True,
                font_path=font_path
            )
            fuzhuang_pifu, hero_fengmian_bash_image = format_image(fuzhuang_pifu, hero_fengmian_bash_image)
            fuzhuang_pifu = cv2.resize(fuzhuang_pifu, (100, 152))
            hero_fengmian_bash_image = cv2.resize(hero_fengmian_bash_image, (1000,520))
            hero_fengmian_bash_image = EditImage(hero_fengmian_bash_image).images_fill(
                ((630+x, y), fuzhuang_pifu))
            x += 120
            if x >= 120 * 3:
                x = 15
                y += 160

        snapshot_write(image=hero_fengmian_bash_image, write_name="$_封面大合图001.png",sn=11264001)

# 业务流程
def game_did_launch(env):
    phaseList = [
        Phase("关闭游戏", lambda: gameClose()),
        Phase("启动游戏", lambda: gameLaunch()),
        Phase("游戏客户端登录", lambda: GameLogin()()),
        Phase("进入游戏", lambda: EnterGame()()),
        Phase("头像采集", lambda: AvatarCollector()()),
        Phase("图鉴收集", lambda: AlbumCollecto()()),
        Phase("赛季数据采集", lambda: SeasonCollector()()),
        Phase("通行证采集", lambda: PassCollector()()),
        Phase("玩法采集", lambda: GameplayCollector()()),
        Phase("限购道具采集", lambda: LimitedItemCollector()()),
        Phase("抽卡采集", lambda: GachaCollector()()),
        Phase("英雄采集", lambda: HeroCollector()()),
        Phase("武器装备采集", lambda: WeaponEquipmentCollector()()),
        Phase("封面合图", lambda: CoverCollector()())

    ]


    if localRun:
        biz_module_fabu = lx_import("11264_netease_fabu.air")
        phaseList = [
            # Phase("清除属性", lambda: property_clear()),
            # Phase("关闭游戏", lambda: gameClose()),
            Phase("启动游戏", lambda: gameLaunch()),
            Phase("游戏客户端登录", lambda: GameLogin()()),
            # Phase("进入游戏", lambda: EnterGame()()),
            # Phase("头像采集", lambda: AvatarCollector()()),
            # Phase("图鉴收集", lambda: AlbumCollecto()()),
            # Phase("赛季数据采集", lambda: SeasonCollector()()),
            # Phase("通行证采集", lambda: PassCollector()()),
            # Phase("玩法采集", lambda: GameplayCollector()()),
            # Phase("限购道具采集", lambda: LimitedItemCollector()()),
            # Phase("抽卡采集", lambda: GachaCollector()()),
            # Phase("英雄采集", lambda: HeroCollector()()),
            # Phase("武器装备采集", lambda: WeaponEquipmentCollector()()),
            # Phase("封面合图", lambda: CoverCollector()()),
            # Phase("多子属性-测试", lambda: biz_module_fabu.properties_test())
            # add_text_to_image(image=snapshot_write(read_name=str(gameDir / "materials_icons" / '时装填充.png')),image_text=("+55"),pos=(43, 55),size=26),
            # add_text_to_image(image=snapshot_write(read_name=str(gameDir / "materials_icons" / '武器填充.png')),
            #                   image_text=("+55"), pos=(45, 55), size=25)
            # push_image_test()
            # game_dashen_launch()
        ]

    phaseList.extend([
        Phase("图片文件补充时间戳", lambda: ScreenshotRename()()),
    ])

    return phaseList

# 启动游戏
def game_will_launch(env=None):
    ...

# 关闭游戏
def game_will_close(env=None):
    gameClose()

# 游戏信息清理
def game_will_clean(env=None):
    ...

# 异常处理
def app_will_process_exception_snapshot(snapshot_path):
    ...

# 卖家ID
def app_will_process_sellers(seller_urls):
    seller_info = {}
    properties_data = property_read()
    if userID := properties_data.get("userID"):
        seller_info.update(roleId=userID)

    if serverInfo := properties_data.get("区服信息"):
        monitor_task_status_v2(f"seller区服信息", format_print(serverInfo))
        serverName = serverInfo["serverName"]
        serverImagesUrls = serverInfo["serverImagesUrls"]
        model = DomainServerModel(
            real_game_area=serverName,
            real_game_qu=None,
            max_count=5,
            is_for_all_platform=False,
            image_list=serverImagesUrls)
        seller_info.update(get_domain_and_server_info(model))

    if seller_info:
        monitor_task_status_v2(f"seller_info上报", format_print(seller_info))
        return seller_info

# 预拉取属性库
def app_did_get_properties(properties_remote=None):
    if localRun and (gameDir / "properties_remote.json").exists():
        properties_remote = json.loads((gameDir / "properties_remote.json").read_text())

    if isinstance(properties_remote, str):
        properties_remote = json.loads(properties_remote)

    properties_organize_result = properties_organize(properties_remote)
    properties_simple = properties_organize_simple(properties_organize_result)
    properties_simple_global.update(properties_simple)

def test():
    image_name = "默认背景"
    imge = snapshot_write(read_name=str(gameDir / "materials_icons" /  f"默认背景.png"))
    print(image_upload(image_name,imge))
    # snapshot_write("ssd",image=imge )


def add_text_to_image(image_text,image,pos,size):
    pos_text = pos
    image = image_multiline_text(
        image,
        image_text,
        font_size=size,
        textPoint=pos_text,
        center_alignment=True,
        # font_path=str(gameDir.parent / '11264_netease/Alimamakaishu/AlimamaDongFangDaKai-Regular.otf'
        font_path=ENV.rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'
    )
    snapshot_write(image=image, write_name="测试和图.png")
    return
# 运行循环次数
def app_will_get_runloop_count():
    return 1

def push_image_test():
    _, image_path=snapshot_write(area=(980,375,1425,975),write_name="登录二维码/ssd.png",needPath= True)
    print(image_path)
    remote_path = DEV.push(image_path,  "/sdcard")
    print(remote_path)

    print(f"已推送到：{remote_path}")
    game_dashen_launch()
    sleep(5)
    # game_qq_launch()
    # DEV.shell(f"rm {remote_path}")

def game_dashen_launch(is_login=False,image_path=None):
    launchGame("大神", "com.netease.gl")
    if find_tpl("tpl20260414111910.png",threshold=0.8,desc="检测到踢登"):
        monitor_catch("状态检查", f"被踢掉登录账户（{platform}）", status=10010, break_mode=BreakModeEnum.app)
    if find_tpl("tpl20260408102514.png",threshold=0.8,desc="检测到更新") or find_tpl("tpl20260414113120.png",threshold=0.8,area=(300,800,1100,1700),desc="检测到更新"):
        monitor_catch(f"状态大神检测", "大神更新")
        if find_tpl_touch("tpl20260413214106.png",threshold=0.8,desc="点击不更新", area=(940,600,1200,900)):
            monitor_catch("跳过更新", "点击不更新")
    if is_login:
        # 首先删除设备上所有图片
        device_dirpath = "/sdcard/Pictures"
        DEV.shell(f"rm -rf {device_dirpath} && mkdir {device_dirpath}")
        sleep(2)
        for i in range(3):
            if find_tpl_touch("tpl20260410153506.png",threshold=0.7,area=(1100,85,1185,170)):
                monitor_catch("已打开扫码", catch=True)
                # 先保存大神二维码，然后覆盖
            if find_tpl("tpl20260412163036.png",threshold=0.8,desc="识别保存大神二维码"):
                break
        if find_tpl_touch("tpl20260412163036.png",threshold=0.8,desc="保存大神二维码"):
            sleep(2)
            find_tpl_touch("tpl20260412163246.png",threshold=0.8,desc="下载大神二维码")
            monitor_catch("已下载二维码", catch=True)
            sleep(2)
        air_touch((70, 70))
        monitor_catch("后退回扫码界面", catch=True)
        sleep(2)
        # 推送文件
        if device_filename := DEV.shell(f"ls {device_dirpath}").strip():
            # 使用 adb push 将本地文件推送到设备
            import subprocess
            device_serial = DEV.uuid if hasattr(DEV, 'uuid') else None

            if device_serial:
                cmd = ["adb", "-s", device_serial, "push", image_path, f"/sdcard/Pictures/{device_filename}"]
            else:
                cmd = ["adb", "push", image_path, f"/sdcard/Pictures/{device_filename}"]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                monitor_catch("二维码截图保存成功",f"/sdcard/Pictures/{device_filename}",catch=True)
            else:
                monitor_catch(f"推送失败", f"{result.stderr}", catch=True)
        air_touch((1265, 133))
        monitor_catch("打开已有二维码", catch=True)
        sleep(2)
        air_touch((220, 350))
        monitor_catch("扫瞄第一张二维码", catch=True)
        if find_tpl_touch("tpl20260412165203.png",threshold=0.8,desc="点击dashen登录"):
            monitor_catch("已点击登录", catch=True)
        # 删除二维码截图
        device_dirpath = "/sdcard/Pictures"
        DEV.shell(f"rm -rf {device_dirpath} && mkdir {device_dirpath}")
        if find_tpl_touch("tpl1558852235.png",threshold=0.8,desc="大神登录游戏风控"):
            monitor_catch("解除将军令-远程超时-远程", break_mode=BreakModeEnum.app, status=10224, image=snapshot_write())
        return
    sleep(5)
    result = snapshot_ocr(LT=(110, 445), RB=(730, 525),desc="识别验证码区域")
    if "填写" in result or "手机短信" in result:
        monitor_catch("正在输入验证码", catch=True)
        for i  in range(3):
            air_touch((190,745))
        adc_input(ENV.smsCode)
        monitor_catch("已输入验证码",catch= True)
        if find_tpl_touch("tpl20260410142725.png", threshold=0.8):
            monitor_catch("点击授权", catch=True)
        if find_tpl_touch("tpl20260410145145.png",threshold=0.7):
            monitor_catch(f"状态检测", "验证码有误", break_mode=BreakModeEnum.app, status=10007, image=snapshot_write())
        monitor_catch("验证码输入无误，已登录大神", catch=True)
        return
    for i in range(5):
        if find_tpl_touch ("tpl20260408163220.png",area=area_rt,threshold=0.8):
            monitor_catch("已找到游戏圈1")
        if "同意" in snapshot_ocr(LT=(920,1610), RB=(1060,1680)):
            air_touch((980,1650))
            monitor_catch("已找到游戏圈2")
        if find_tpl_touch ("tpl20260408101818.png",area=area_rt,threshold=0.8):
            monitor_catch("已找到游戏圈3")
        if find_tpl_touch ("tpl20260410140721.png",threshold=0.8):
            monitor_catch("已找我的登录界面")
        if find_tpl("tpl20260408102514.png",threshold=0.8,desc="检测到更新") or find_tpl("tpl20260414113120.png",threshold=0.8,area=(300,800,1100,1700),desc="检测到更新"):
            monitor_catch(f"状态大神检测", "大神更新")
            if find_tpl_touch("tpl20260413214106.png",threshold=0.8,desc="点击不更新", area=(940,600,1200,900)):
                monitor_catch("跳过更新", "点击不更新")
            # monitor_catch(f"状态大神检测", "游戏更新", break_mode=BreakModeEnum.app, status=10108, image=snapshot_write())
        if find_tpl_touch ("tpl20260408213315.png",threshold=0.8):
            monitor_catch("开始登录")
        if find_tpl("tpl20260410141424.png",threshold=0.8):
            monitor_catch("已找到手机号登录界面")
            for i in range(5):
                air_touch((450,675))
                monitor_catch("已输入手机号",catch= True)
            break
    if isPre:
        adc_input(ENV.username)
        monitor_catch("已输入手机号",f"{ENV.username}",catch= True)
    else:
        adc_input(ENV.username)
        monitor_catch("已输入手机号",catch= True)
    if find_tpl_touch ("tpl20260410142438.png",threshold=0.8):
        air_touch((690,850))
        monitor_catch("点击下一步", catch=True)
    if find_tpl_touch("tpl20260410142725.png",threshold=0.8):
        monitor_catch("点击授权", catch=True)
    result = snapshot_ocr(LT=(110, 445), RB=(730, 525),desc="识别验证码区域")
    if "填写" in result or "手机短信" in result:
        monitor_catch("验证码发送成功",catch= True)
        return
    monitor_catch("验证码发送失败", break_mode=BreakModeEnum.app, status=10139, image=snapshot_write())

def game_qq_launch():
    if localRun:
        packageName = "com.tencent.mtt"
    else:
        packageName = "com.ttg.demoh5"
    launchGame("启动浏览器", packageName)
    monitor_catch("切换Pc端",catch= True)

