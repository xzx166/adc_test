import requests
# from airtest.core.api import *

from utility.base.adc_environment import *

# auto_setup(__file__)

performance_start_timestamp = 0


task_status_last_errorcode = None
def get_task_status_last_errorcode():
    global task_status_last_errorcode
    monitor_print(f"---get_task_status_last_errorcode: {task_status_last_errorcode}")
    return task_status_last_errorcode

def set_task_status_last_errorcode(errorcode):
    global task_status_last_errorcode
    task_status_last_errorcode = errorcode
    monitor_print(f"---set_task_status_last_errorcode: {task_status_last_errorcode}")

def get_env_host(env, custom_env_type=None, need_prefix=False):
    scriptEnv = env.scriptEnv
    if custom_env_type is not None:
        scriptEnv = custom_env_type
    host=""

    if need_prefix:
        if (scriptEnv == 'local'):
            # host = 'pre-adc-pc.alibaba-inc.com'
            host = 'http://test-adc-pc.alibaba.net'
        elif(scriptEnv == 'pre'):
            host = 'http://pre-adc-pc.alibaba-inc.com'
        elif(scriptEnv == 'prod'):
            host = 'http://adc-pc.alibaba-inc.com'
        else:
            host = 'http://test-adc-pc.alibaba.net'
    else:
        if (scriptEnv == 'local'):
            # host = 'pre-adc-pc.alibaba-inc.com'
            host = 'test-adc-pc.alibaba.net'
        elif(scriptEnv == 'pre'):
            host = 'pre-adc-pc.alibaba-inc.com'
        elif(scriptEnv == 'prod'):
            host = 'adc-pc.alibaba-inc.com'
        else:
            host = 'test-adc-pc.alibaba.net'

    return host

def get_home_adc_directory():
    home_path = os.path.expanduser("~")
    directory = os.path.join(home_path, ".adc")
    # 判断目录是否存在
    if os.path.exists(directory):
        pass
        # print(f"目录 {directory} 已存在")
    else:
        # 创建目录
        os.makedirs(directory)
        # print(f"目录 {directory} 创建成功")
    return directory


class AppPerformanceInfo:
    __instance = None

    def __init__(self):
        self.timeDurationMap = {}

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    def setTimeDurationMap(self, duration_key, duration_start=True):
        if duration_start:
            self.timeDurationMap[duration_key] = int(time.time() * 1000000)
        else:
            if duration_key not in self.timeDurationMap:
                raise Exception("duration_key not in self.timeDurationMap")
            else:
                self.timeDurationMap[duration_key] = int(time.time() * 1000000) - self.timeDurationMap[duration_key]
                monitor_print(f"---setTimeDurationMap_{duration_key}: {self.timeDurationMap[duration_key]}")

    def getTimeDurationMap(self):
        return self.timeDurationMap


class PRINT_LEVEL(Enum):
    INFO = 1
    DEBUG = 2
    WARN = 3
    ERROR = 4

# level: debug, info, warn, error
def monitor_print(desc, timestamp=None, level=PRINT_LEVEL.DEBUG):

    GRAY = "\033[37m"  # 浅灰色
    BLUE = "\033[94m"    # 蓝色
    YELLOW = "\033[93m"  # 黄色
    RED = "\033[91m"     # 红色
    GREEN = "\033[92m"   # 绿色

    RESET = "\033[0m"    # 重置颜色

    env = AppEnv.get_instance()
    taskId = env.taskId
    game_dir = env.gameDir
    game_name = env.game_name
    game_id = env.game_id
    game_platfrom = env.game_platfrom
    launchType = env.launchType
    info = ' adc-sc-log--> '+'desc:'+desc + '; '

    if taskId:
        info = 'adc-sc-log--> '+ 'taskId:' + taskId + '; '

    if game_id is not None and len(game_id) > 0:
        info = info + 'gameId:' + game_id + '; '

    if game_platfrom is not None and len(game_platfrom) > 0:
        info = info + 'gamePlatform:' + game_platfrom + '; '

    if game_dir is not None and len(game_dir) > 0:
        info = info + 'game_dir:' + game_dir + '; '

    if game_name is not None and len(game_name) > 0:
        info = info + 'game_name:' + game_name + '; '

    if timestamp is not None:
        info = info + 'print_timestamp:' + str(int(timestamp)) + '; '
    else:
        info = info + 'print_timestamp:' + str(int(time.time()*1000000)) + '; '

    info = info + 'desc:'+desc+'; '

    real_color = GRAY
    if level == PRINT_LEVEL.ERROR:
        real_color = RED
    elif level == PRINT_LEVEL.WARN:
        real_color = YELLOW
    elif level == PRINT_LEVEL.DEBUG:
        real_color = GREEN
    elif level == PRINT_LEVEL.INFO:
        real_color = BLUE

    # need_write = True
    if launchType == 'localtest':
        print(real_color + info + RESET + '\n')
        adc_dir = get_home_adc_directory()
        adc_monitor_file = adc_dir + '/' + game_dir + '.log'
        with open(adc_monitor_file, 'a') as f:
            f.write(info + '\n')
    else:
        print(info + '\n')

def monitor_post_task_status(title, desc, status=None):
    env = AppEnv.get_instance()
    monitor_print(title + ',' + desc)

    launchType = env.launchType
    if (launchType == 'localtest'):
        return

    taskStatus = env.taskStatus
    if status is not None:
        set_task_status_last_errorcode(status)
        desc = str(status) + '+' + desc
        title = str(status) + '+' + title
        monitor_print(f'---monitor_post_task_status_error_status: {title}, {desc},{status}')

    host = get_env_host(env)

    url = "http://{}/task/postUpdateTaskStatus".format(host)

    timestamp = time.time() * 1000000
    info = title + '+' + desc
    monitor_print(info, timestamp)

    # payload = {"taskId": env.taskId, "taskStatus": taskStatus, "title": title, "description":desc, 'timestamp': int(time.time()*1000000)}
    payload = {"taskId": env.taskId, "taskStatus": taskStatus, "title": title, "description": desc,
               'timestamp': int(timestamp), 'game_dir': env.gameDir, 'game_name': env.game_name}
    monitor_print(f"---monitor_post_task_status_start ------ url: {url}, payload: {payload}")
    response = None
    try:
        response = requests.post(url, json=payload)
        monitor_print(f"monitor_task_status_response: {response.status_code}, text:{response.text}")
        if (launchType == 'localtest'):
            monitor_print(f"monitor_task_status_response_json: {response.json()}")
        return response.json()
    except Exception as e:
        monitor_print(f"monitor_task_status------response_error: {str(e)}")

    # print('updateTaskStatus:'+ str(response) + url)
    return None

def monitor_task_status_v2(title, desc="", status=None):
    env = AppEnv.get_instance()
    return monitor_task_status(env, title, desc, status)

def monitor_task_status(env, title, desc="", status=None):
    title, desc= str(title), str(desc)
    monitor_print(f'---monitor_task_status: {title},{desc},{status}')

    launchType = env.launchType
    if (launchType == 'localtest'):
        return

    taskStatus = env.taskStatus

    if status is not None:
        assert type(status) == int, "错误码必须是整数"
        assert status > 0, "错误码必须大于0"
        if status == 5:
            taskStatus = status
        else:
            set_task_status_last_errorcode(status)
            desc = f"{status} + {desc}"
            title = f"{status} + {title}"
            monitor_print(f'---monitor_task_status_error_status: {title}, {desc}, {status}')
    

    # if status:
    #     taskStatus = status

    # 这里在大于10000的情况下会上报任务中心错误，并且终止脚本执行
    # if (taskStatus > 10000):
    #     monitor_report_task_info(env, taskStatus)

    host= get_env_host(env)

    url = "http://{}/task/updateTaskStatus".format(host)

    timestamp = time.time()*1000000
    info = f"{title} + {desc}"
    monitor_print(info, timestamp)

    # payload = {"taskId": env.taskId, "taskStatus": taskStatus, "title": title, "description":desc, 'timestamp': int(time.time()*1000000)}
    payload = {"taskId": env.taskId, "taskStatus": taskStatus, "title": title, "description":desc, 'timestamp': int(timestamp), 'game_dir': env.gameDir, 'game_name': env.game_name}
    monitor_print(f"---monitor_task_status_start_url: {url}, payload: {payload}")
    response = None
    try:
        response = requests.get(url, params=payload)
        monitor_print(f"---monitor_task_status_response: {response}")
        return response.text
    except Exception as e:
        monitor_print(f"---monitor_task_status_response_error: {str(e)}")



    # print('updateTaskStatus:'+ str(response) + url)
    return None

