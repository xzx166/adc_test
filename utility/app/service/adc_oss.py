# -*- encoding=utf8 -*-
import subprocess

import oss2

from utility.base.adc_api import lx_safe_snapshot
from utility.base.adc_monitor import *
from utility.base.adc_network import request_workflow_task_status


def get_miniapp_stsToken(env):
    monitor_print(f"getStsToken")
    script_env = env.scriptEnv
    monitor_print(f"getStsToken: script_env {script_env}")

    app_id = ''
    app_secret = ''

    url = "https://mcc.9game.cn/auth/oss/path/apply"
    if (script_env == 'local'):
        url = "http://daily-mcc-server.aligames.com/auth/oss/path/apply"
        app_id = 'adc_mini_app'
        app_secret = 'ecb20fc70f4b236040e7fc3d4130c1'
    elif (script_env == 'pre'):
        url = "https://mcc.9game.cn/auth/oss/path/apply"
        app_id = 'adc_mini_app'
        app_secret = 'fcb14cb29e6g14e614f3ax4d8271f9'
    elif (script_env == 'prod'):
        url = "https://mcc.9game.cn/auth/oss/path/apply"
        app_id = 'adc_mini_app'
        app_secret = 'fcb14cb29e6g14e614f3ax4d8271f9'
    else:
        url = "http://daily-mcc-server.aligames.com/auth/oss/path/apply"
        app_id = 'adc_mini_app'
        app_secret = 'ecb20fc70f4b236040e7fc3d4130c1'

    # app_id = env.oss_miniapp_app_id
    # app_secret = env.oss_miniapp_app_secret

    payload = {"appId": app_id,
               "appSecret": app_secret,
               "duration": 900,
               "resList": [""]
               }
    monitor_print(f"getStsToken: payload {payload}")
    monitor_print(f"getStsToken: url {url}")
    response = requests.post(url, json=payload)

    # monitor_print(f"sts reponse url:{response.status}")
    monitor_print(f"sts reponse url:{response.url}")
    monitor_print(f"sts reponse text:{response.text}")
    result = response.json()
    monitor_print(f"sts result: {result}")
    return result

def getStsToken(env):
    monitor_print(f"getStsToken")
    script_env = env.scriptEnv
    monitor_print(f"getStsToken: script_env {script_env}")
    script_env = 'prod'
    url = "https://mcc.9game.cn/auth/oss/path/apply"
    if (script_env == 'local'):
        url = "http://daily-mcc-server.aligames.com/auth/oss/path/apply"
    elif (script_env == 'pre'):
        url = "https://mcc.9game.cn/auth/oss/path/apply"
    elif (script_env == 'prod'):
        url = "https://mcc.9game.cn/auth/oss/path/apply"
    else:
        url = "http://daily-mcc-server.aligames.com/auth/oss/path/apply"

    # payload = {"appId": env.oss_app_id,
    #            "appSecret": env.oss_app_secret,
    #            "duration": 900,
    #            "resList": [""]
    #            }

    payload = {"appId": 'adc_pc',
               "appSecret": '4a038e854bd9f8cfce1ae536ca',
               "duration": 900,
               "resList": [""]
               }

    monitor_print(f"getStsToken: payload {payload}")
    monitor_print(f"getStsToken: url {url}")
    response = requests.post(url, json=payload)

    # monitor_print(f"sts reponse url:{response.status}")
    monitor_print(f"sts reponse url:{response.url}")
    monitor_print(f"sts reponse text:{response.text}")
    result = response.json()
    monitor_print(f"sts result: {result}")
    return result


def upload_sonar_airtest(env):
    imsdk_oss_appid_test = env.oss_app_id
    imsdk_oss_secrect_key_test = env.oss_app_secret
    # auth = oss2.Auth(ossAppId, ossSecretKey)
    auth = oss2.Auth(imsdk_oss_appid_test, imsdk_oss_secrect_key_test)
    # yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
    # 填写Bucket名称。
    bucket = oss2.Bucket(
        auth, "https://oss-cn-zhangjiakou.aliyuncs.com", 'sonar-airtest')

    bucketName = 'sonar-airtest'
    endPoint = 'oss-cn-zhangjiakou.aliyuncs.com'
    # taskStatus = 5
    ossPrePath = 'oss-android' + '/' + str(env.taskId)
    upload_files(env, bucket, ossPrePath, bucketName)


def upload_lingxioss_with_prefix_name(prefix_name):
    env = AppEnv.get_instance()
    monitor_print('upload_lingxioss_with_prefix_name')
    stsToken = getStsToken(env)
    credential = stsToken['credential']
    sts_env = stsToken['env']
    resList = stsToken['resList']
    auth = oss2.StsAuth(credential['accessKeyId'],
                        credential['accessKeySecret'], credential['securityToken'])

    bucket = oss2.Bucket(
        auth, sts_env['publicEndpoint'], sts_env['bucket'])

    bucketName = sts_env['bucket']
    endPoint = sts_env['publicEndpoint']
    cdnDomain = sts_env['cdnDomain']

    cdnPath = resList[0]
    monitor_print(
        f"bucketName: {bucketName}, endPoint:{endPoint}, cdnDomain: {cdnDomain}, cdnpath: {cdnPath}")
    # taskStatus = 5
    ossPrePath = cdnPath + 'oss-android' + '/' + str(env.taskId)
    # urls = upload_lingxi_files(env, bucket, ossPrePath, bucketName, cdnDomain)

    monitor_print('upload_lingxi_files')
    scriptPath = env.logPath
    files = os.listdir(scriptPath)
    urls = []
    needReport = False
    for file in files:
        if not os.path.isdir(file):
            if prefix_name in file:
                with open(scriptPath + '/' + file, 'rb') as fileobj:
                    monitor_print(f"upload_lingxi_files_with_prefix_name: {file}")
                    # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
                    fileobj.seek(0, os.SEEK_SET)
                    # Tell方法用于返回当前位置。
                    current = fileobj.tell()

                    # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
                    osspath = ossPrePath + '/' + file
                    monitor_print(f"upload_lingxioss_with_prefix_name oss upload osspath:{osspath}")
                    result = bucket.put_object(osspath, fileobj)
                    if (result.status == 200):
                        url = cdnDomain + osspath
                        monitor_print(f"upload_lingxioss_with_prefix_name oss_upload finished:{url}")
                        urls.append(url)

    return urls


def geteagleStsToken(env):
    monitor_print(f"getStsToken")
    script_env = env.scriptEnv
    monitor_print(f"getStsToken: script_env {script_env}")
    url = "https://mcc.9game.cn/auth/oss/path/apply"
    if (script_env == 'local'):
        url = "https://mcc.9game.cn/auth/oss/path/apply"
    elif (script_env == 'pre'):
        url = "https://mcc.9game.cn/auth/oss/path/apply"
    elif (script_env == 'prod'):
        url = "https://mcc.9game.cn/auth/oss/path/apply"
    else:
        url = "https://mcc.9game.cn/auth/oss/path/apply"

    appId = "eagle_cro"
    appSecret = "6C8678A4EAA59DFA80F72E89CE1A5EBD"

    payload = {
        "appId": appId,
        "appSecret": appSecret,
        "duration": 900,
        "resList": [""]
    }

    monitor_print(f"getStsToken: payload {payload}")
    monitor_print(f"getStsToken: url {url}")
    response = requests.post(url, json=payload)

    # monitor_print(f"sts reponse url:{response.status}")
    monitor_print(f"sts_reponse_url:{response.url}")
    monitor_print(f"sts_reponse_text:{response.text}")
    result = response.json()
    monitor_print(f"sts_result: {result}")
    return result


def upload_eagle_lingxioss_with_pathes(pathes):
    env = AppEnv.get_instance()
    monitor_print('upload_lingxioss_with_prefix_name')
    # sig_result = get_eagle_oss_signature(env)
    # final_sig_result_json = sig_result['data']
    # dumpsfinal_sig_result_json = json.dumps(final_sig_result_json)
    stsToken = geteagleStsToken(env)
    credential = stsToken['credential']
    sts_env = stsToken['env']
    resList = stsToken['resList']
    auth = oss2.StsAuth(credential['accessKeyId'],
                        credential['accessKeySecret'], credential['securityToken'])

    bucket = oss2.Bucket(
        auth, sts_env['publicEndpoint'], sts_env['bucket'])

    bucketName = sts_env['bucket']
    endPoint = sts_env['publicEndpoint']
    cdnDomain = sts_env['cdnDomain']
    # cdnDomain = "adc_eagle/"

    cdnPath = resList[0]
    monitor_print(
        f"bucketName: {bucketName}, endPoint:{endPoint}, cdnDomain: {cdnDomain}, cdnpath: {cdnPath}")
    # taskStatus = 5
    ossPrePath = cdnPath + 'oss-android/eagle' + '/' + str(env.taskId)
    # urls = upload_lingxi_files(env, bucket, ossPrePath, bucketName, cdnDomain)

    monitor_print('upload_lingxi_files')
    scriptPath = env.logPath
    file = pathes
    urls = []
    needReport = False
    # for file in files:
    if not os.path.isdir(file):
        with open(file, 'rb') as fileobj:
            monitor_print(f"upload_lingxioss_with_pathes: {file}")
            # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
            fileobj.seek(0, os.SEEK_SET)
            # Tell方法用于返回当前位置。
            current = fileobj.tell()

            file_name = os.path.basename(file)

            # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
            osspath = ossPrePath + '/' + file_name
            monitor_print(f"upload_lingxioss_with_pathes oss upload osspath:{osspath}")
            result = bucket.put_object(osspath, fileobj)
            if (result.status == 200):
                url = cdnDomain + osspath
                monitor_print(f"upload_lingxioss_with_pathes oss_upload finished:{url}")
                urls.append(url)

    return urls[0]


def upload_miniapp_oss_with_pathes(pathes):
    env = AppEnv.get_instance()
    monitor_print(f'upload_miniapp_oss_with_pathes:{pathes}')
    stsToken = get_miniapp_stsToken(env)
    credential = stsToken['credential']
    sts_env = stsToken['env']
    resList = stsToken['resList']
    auth = oss2.StsAuth(credential['accessKeyId'],
                        credential['accessKeySecret'], credential['securityToken'])

    bucket = oss2.Bucket(
        auth, sts_env['publicEndpoint'], sts_env['bucket'])

    bucketName = sts_env['bucket']
    endPoint = sts_env['publicEndpoint']
    cdnDomain = sts_env['cdnDomain']

    cdnPath = resList[0]
    monitor_print(
        f"bucketName: {bucketName}, endPoint:{endPoint}, cdnDomain: {cdnDomain}, cdnpath: {cdnPath}")
    # taskStatus = 5
    ossPrePath = cdnPath + 'oss-android' + '/' + str(env.taskId)
    # urls = upload_lingxi_files(env, bucket, ossPrePath, bucketName, cdnDomain)

    monitor_print(f'upload_miniapp_oss_with_pathes_info:{ossPrePath}')
    scriptPath = env.logPath
    files = pathes
    urls = []
    needReport = False
    for file in files:
        if not os.path.isdir(file):
            with open(file, 'rb') as fileobj:
                monitor_print(f"upload_miniapp_oss_with_pathes: {file}")
                # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
                fileobj.seek(0, os.SEEK_SET)
                # Tell方法用于返回当前位置。
                current = fileobj.tell()

                file_name = os.path.basename(file)

                # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
                osspath = ossPrePath + '/' + file_name
                monitor_print(f"upload_miniapp_oss_with_pathes_osspath:{osspath}")
                result = bucket.put_object(osspath, fileobj)
                if (result.status == 200):
                    url = cdnDomain + osspath
                    monitor_print(f"upload_miniapp_oss_with_pathes_finished:{url}")
                    urls.append(url)

    return urls



def upload_lingxioss_with_pathes(pathes):
    env = AppEnv.get_instance()
    monitor_print('upload_lingxioss_with_pathes')
    stsToken = getStsToken(env)
    credential = stsToken['credential']
    sts_env = stsToken['env']
    resList = stsToken['resList']
    auth = oss2.StsAuth(credential['accessKeyId'],
                        credential['accessKeySecret'], credential['securityToken'])

    bucket = oss2.Bucket(
        auth, sts_env['publicEndpoint'], sts_env['bucket'])

    bucketName = sts_env['bucket']
    endPoint = sts_env['publicEndpoint']
    cdnDomain = sts_env['cdnDomain']

    cdnPath = resList[0]
    monitor_print(
        f"bucketName: {bucketName}, endPoint:{endPoint}, cdnDomain: {cdnDomain}, cdnpath: {cdnPath}")
    # taskStatus = 5
    ossPrePath = cdnPath + 'oss-android' + '/' + str(env.taskId)
    # urls = upload_lingxi_files(env, bucket, ossPrePath, bucketName, cdnDomain)

    monitor_print('upload_lingxi_files')
    scriptPath = env.logPath
    files = pathes
    urls = []
    needReport = False
    for file in files:
        if not os.path.isdir(file):
            with open(file, 'rb') as fileobj:
                monitor_print(f"upload_lingxioss_with_pathes: {file}")
                # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
                fileobj.seek(0, os.SEEK_SET)
                # Tell方法用于返回当前位置。
                current = fileobj.tell()

                file_name = os.path.basename(file)

                # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
                osspath = ossPrePath + '/' + file_name
                monitor_print(f"upload_lingxioss_with_pathes oss upload osspath:{osspath}")
                result = bucket.put_object(osspath, fileobj)
                if (result.status == 200):
                    url = cdnDomain + osspath
                    monitor_print(f"upload_lingxioss_with_pathes oss_upload finished:{url}")
                    urls.append(url)

    return urls


def upload_lingxioss(env):
    monitor_print('upload_lingxioss')
    stsToken = getStsToken(env)
    credential = stsToken['credential']
    sts_env = stsToken['env']
    resList = stsToken['resList']
    auth = oss2.StsAuth(credential['accessKeyId'],
                        credential['accessKeySecret'], credential['securityToken'])

    bucket = oss2.Bucket(
        auth, sts_env['publicEndpoint'], sts_env['bucket'])

    bucketName = sts_env['bucket']
    endPoint = sts_env['publicEndpoint']
    cdnDomain = sts_env['cdnDomain']

    cdnPath = resList[0]
    monitor_print(
        f"bucketName: {bucketName}, endPoint:{endPoint}, cdnDomain: {cdnDomain}, cdnpath: {cdnPath}")
    # taskStatus = 5
    ossPrePath = cdnPath + 'oss-android' + '/' + str(env.taskId)
    urls = upload_lingxi_files(env, bucket, ossPrePath, bucketName, cdnDomain)
    return urls


def upload_lingxi_files(env, bucket, ossPrePath, bucketName, cdnDomain):
    monitor_print('upload_lingxi_files')
    scriptPath = env.logPath
    files = os.listdir(scriptPath)
    urls = []
    needReport = False
    for file in files:
        if not os.path.isdir(file):
            if 'adc_result_' in file or 'log' in file:
                with open(scriptPath + '/' + file, 'rb') as fileobj:
                    monitor_print(f"upload_lingxi_files: {file}")
                    # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
                    fileobj.seek(0, os.SEEK_SET)
                    # Tell方法用于返回当前位置。
                    current = fileobj.tell()

                    # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
                    osspath = ossPrePath + '/' + file
                    monitor_print(f"oss upload osspath:{osspath}")
                    result = bucket.put_object(osspath, fileobj)
                    if (result.status == 200):
                        url = cdnDomain + osspath
                        monitor_print(f"oss_upload finished:{url}")
                        if 'adc_result_' in file:
                            urls.append(url)
                            needReport = True
                        else:
                            monitor_task_status(env, url, '')

                        # url='oss://sonar-airtest/oss-android/16/adc_result_1694522952.jpg'
                        # 调用 Shell 命令
    monitor_print(f"sorted_urls_before:{urls}")
    sorted_urls = sorted(urls, key=get_number_from_path)
    monitor_print(f"sorted_urls_after:{sorted_urls}")
    for url in sorted_urls:
        request_workflow_task_status(url, f'上报url', 5)
        # monitor_task_status(env, url, '',  5)

    if needReport == True:
        return sorted_urls
        # monitor_report_task_info(env, 6, urls)


def get_number_from_path(path):
    file_name = path.split("/")[-1]
    result = file_name.split("_")[-1].split(".")[0]
    if result and result.isdigit():
        return int(result)
    elif result and result.isalpha():
        return 0
    else:
        return 1

def upload_files(env, bucket, ossPrePath, bucketName):
    # 必须以二进制的方式打开文件。
    # 填写本地文件的完整路径。如果未指定本地路径，则默认从示例程序所属项目对应本地路径中上传文件。
    scriptPath = env.logPath
    files = os.listdir(scriptPath)
    urls = []
    for file in files:
        if not os.path.isdir(file):
            if 'adc_result_' in file or 'log' in file:
                with open(scriptPath + '/' + file, 'rb') as fileobj:
                    # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
                    fileobj.seek(0, os.SEEK_SET)
                    # Tell方法用于返回当前位置。
                    current = fileobj.tell()

                    # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
                    osspath = ossPrePath + '/' + file
                    print(f"oss upload: osspath:{osspath}")
                    result = bucket.put_object(osspath, fileobj)
                    print(f"oss upload: result:{result}")
                    if (result.status == 200):
                        url = 'oss://' + bucketName + '/' + osspath
                        # url='oss://sonar-airtest/oss-android/16/adc_result_1694522952.jpg'
                        # 调用 Shell 命令

                        current_directory = os.path.dirname(
                            os.path.abspath(__file__))

                        ossutilName = ''

                        if (env.scriptEnv == 'local'):
                            ossutilName = 'ossutil'
                        else:
                            ossutilName = 'ossutil-linux-64'

                        command = '{}/../oss/{} sign {} --timeout 6000000 -c {}/../oss/ossconfig'.format(
                            current_directory, ossutilName, url, current_directory)
                        print('command :{}'.format(command))
                        result = subprocess.run(
                            command, shell=True, capture_output=True, text=True)
                        print(result.stdout)
                        # 获取执行结果的第一行
                        output_lines = result.stdout.splitlines()
                        first_line = output_lines[0] if output_lines else ''
                        print(first_line)
                        request_workflow_task_status(first_line, f'上报url', 5)
                        # monitor_task_status(env, first_line, '',  5)
                        urls.append(url)
                        print(f"oss_upload: finished:{url}")
                    else:
                        monitor_task_status(env, '上传单个url失败', f"{result}")

                    # 交易猫的oss - jiaoyimaooss


# 媒体云统一的oss - lingxioss
# 自有的oss - sonar-airtest
# 三中选一个
# ossChannel = 'sonar-airtest'
# ossChannel = 'lingxioss'

def upload_oss(env):
    oss_mode = env.oss_mode
    urls = []
    # seller_urls = []
    try:
        if oss_mode == 'sonar-airtest':
            upload_sonar_airtest(env)
        elif oss_mode == 'lingxioss':
            urls = upload_lingxioss(env)
            monitor_task_status(env, f"oss:{env.oss_mode}上传结束", '')
        else:
            pass

        return urls

    except Exception as e:
        monitor_task_status(env, 'upload_oss上传失败', f"{e}")
        return None
        # if need_report_finish:
        #     monitor_task_status(env,  '上报结束状态6', '失败结束', 6)
        #     monitor_report_task_info(env, 6)


def get_jym_env(env):
    monitor_print(f"get_jym_env")
    script_env = env.scriptEnv
    monitor_print(f"get_jym_env: {script_env}")
    url = "http://adc-pc.alibaba-inc.com/task/getJymOssSignature"
    if (script_env == 'local'):
        url = "http://pre-adc-pc.alibaba-inc.com/task/getJymOssSignature"
    elif (script_env == 'pre'):
        url = "http://pre-adc-pc.alibaba-inc.com/task/getJymOssSignature"
    elif (script_env == 'prod'):
        url = "http://adc-pc.alibaba-inc.com/task/getJymOssSignature"
    else:
        url = "http://pre-adc-pc.alibaba-inc.com/task/getJymOssSignature"

    return url

def get_task_server_env(env):
    monitor_print(f"get_task_server_env")
    script_env = env.scriptEnv
    monitor_print(f"get_jym_env: {script_env}")
    url = "https://pre-lingxi-adc-task-server.alibaba-inc.com/task/getFileUploadSignatureInternal"
    if (script_env == 'local'):
        url = "https://pre-lingxi-adc-task-server.alibaba-inc.com/task/getFileUploadSignatureInternal"
    elif (script_env == 'pre'):
        url = "https://pre-lingxi-adc-task-server.alibaba-inc.com/task/getFileUploadSignatureInternal"
    elif (script_env == 'prod'):
        url = "https://lingxi-adc-task-server.alibaba-inc.com/task/getFileUploadSignatureInternal"
    else:
        url = "https://pre-lingxi-adc-task-server.alibaba-inc.com/task/getFileUploadSignatureInternal"

    return url


def get_jym_oss_signature(task_id=None):
    is_new_api = True
    if is_new_api:
        return get_task_server_oss_signature(task_id)

    env = AppEnv.get_instance()
    url = get_jym_env(env)

    monitor_print(f"get_jym_oss_signature start ------ url: {url}")
    real_task_id = env.taskId
    if task_id:
        real_task_id = task_id

    the_time = int(time.time() * 1000)
    payload = {"taskId": real_task_id, "timestamp": the_time}

    monitor_print(f"get_jym_oss_signature_payload: {payload}")

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)

            monitor_print(f"get_jym_oss_signature_end_response: {response}")
            monitor_print(f"get_jym_oss_signature_end_response_url: {response.url}")
            monitor_print(f"get_jym_oss_signature_end_response_text: {response.text}")
            # print('updateTaskStatus:'+ str(response) + url)
            parse_response = response.json()
            out_suc = parse_response.get('success')
            if out_suc == True:
                parse_response_data = parse_response.get('data')
                parse_response_data_object = json.loads(parse_response_data)
                in_suc = parse_response_data_object.get('success')
                if in_suc == True:
                    return parse_response
        except Exception as e:
            monitor_print(f"get_jym_oss_signature_response_error:{i}, {str(e)}")
    return None

def get_task_server_oss_signature(task_id=None):
    env = AppEnv.get_instance()
    url = get_task_server_env(env)

    monitor_print(f"get_task_server_oss_signature start ------ url: {url}")
    real_task_id = env.taskId
    if task_id:
        real_task_id = task_id

    the_time = int(time.time() * 1000)
    payload = {"taskId": real_task_id, "timestamp": the_time}

    monitor_print(f"get_task_server_oss_signature_payload: {payload}")

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)

            monitor_print(f"get_task_server_oss_signature_end_response: {response}")
            monitor_print(f"get_task_server_oss_signature_end_response_url: {response.url}")
            monitor_print(f"get_task_server_oss_signature_end_response_text: {response.text}")
            # print('updateTaskStatus:'+ str(response) + url)
            parse_response = response.json()
            out_suc = parse_response.get('success')
            if out_suc == True:
                return parse_response
        except Exception as e:
            monitor_print(f"get_task_server_oss_signature_response_error:{i}, {str(e)}")
    return None


def get_eagle_env(env):
    monitor_print(f"get_eagle_env")
    script_env = env.scriptEnv
    monitor_print(f"get_eagle_env: {script_env}")
    url = "http://ieu-eagle-spider.alibaba-inc.com/oss/getSts"
    if (script_env == 'local'):
        url = "http://ieu-eagle-spider-daily.taobao.net/oss/getSts"
    elif (script_env == 'pre'):
        url = "http://ieu-eagle-spider-daily.taobao.net/oss/getSts"
    elif (script_env == 'prod'):
        url = "http://ieu-eagle-spider.alibaba-inc.com/oss/getSts"
    else:
        url = "http://ieu-eagle-spider-daily.taobao.net/oss/getSts"
    return url


def get_eagle_oss_signature(filePath=""):
    env = AppEnv.get_instance()
    url = get_eagle_env(env)

    monitor_print(f"get_eagle_oss_signature start ------ url: {url}")

    the_time = int(time.time() * 1000)
    payload = {
        "requestTime": the_time,
        "caller": "cro",
        "filePath": filePath
    }

    response = None
    for i in range(3):
        try:
            response = requests.post(url, json=payload)

            monitor_print(f"get_eagle_oss_signature_end_response: {response}")
            monitor_print(f"get_eagle_oss_signature_end_response_url: {response.url}")
            monitor_print(f"get_eagle_oss_signature_end_response_text: {response.text}")
            # print('updateTaskStatus:'+ str(response) + url)
            return response.json()
        except Exception as e:
            monitor_print(f"get_eagle_oss_signature_response_error:{i}, {str(e)}")
    return None


def upload_jym_oss(env):
    scriptPath = env.logPath
    files = os.listdir(scriptPath)
    monitor_print(f"---upload_jym_oss_pathes_files:{files}")
    upload_pathes = []

    for file in files:
        if not os.path.isdir(file):
            if 'adc_result_' in file:
                upload_path = scriptPath + '/' + file
                upload_pathes.append(upload_path)

    if len(upload_pathes) == 0:
        monitor_print(f"---upload_jym_oss_pathes_none:{upload_pathes}")
        return None

    monitor_print(f"---upload_jym_oss_upload_pathes:{upload_pathes}")

    url_info = upload_jym_oss_with_pathes(upload_pathes)
    if url_info is None or len(url_info) == 0:
        return None

    urls, cdn_urls = url_info
    new_urls = []
    new_cdn_urls = []

    # final_url_list = []
    # urls = []
    # cdn_urls = []
    for index, url_item in enumerate(urls):
        # oss_path, cdn_url = url_info
        if 'adc_result_' in url_item:
            new_urls.append(url_item)
    for index, url_item in enumerate(cdn_urls):
        # oss_path, cdn_url = url_info
        if 'adc_result_' in url_item:
            new_cdn_urls.append(url_item)

    if len(new_urls) == 0 or len(new_cdn_urls) == 0:
        return None

    monitor_print(f"sorted_urls_before:{new_urls}")
    sorted_urls = sorted(new_urls, key=get_number_from_path)
    monitor_print(f"sorted_urls_after:{sorted_urls}")

    monitor_print(f"sorted_cdn_urls_before:{new_cdn_urls}")
    sorted_cdn_urls = sorted(new_cdn_urls, key=get_number_from_path)
    monitor_print(f"sorted_cdn_urls_after:{sorted_cdn_urls}")

    for cdn_item in sorted_cdn_urls:
        request_workflow_task_status(cdn_item, f'上报url', 5)
        # monitor_task_status(env, cdn_item, '',  5)

    return (sorted_urls, sorted_cdn_urls)


def upload_jym_oss_with_log():
    env = AppEnv.get_instance()
    scriptPath = env.logPath
    files = os.listdir(scriptPath)
    upload_pathes = []

    for file in files:
        if not os.path.isdir(file):
            if '.txt' in file:
                upload_path = scriptPath + '/' + file
                upload_pathes.append(upload_path)

    if len(upload_pathes) == 0:
        return None

    monitor_print(f"---upload_jym_oss_with_log_upload_pathes:{upload_pathes}")

    url_info = upload_jym_oss_with_pathes(upload_pathes)
    if url_info is None or len(url_info) == 0:
        return None

    urls, cdn_urls = url_info
    for cdn_item in cdn_urls:
        monitor_task_status(env, cdn_item, '', 5)
    return (urls, cdn_urls)


def upload_jymoss_with_prefix_name(prefix_name, need_sort=True):
    env = AppEnv.get_instance()
    scriptPath = env.logPath
    if not os.path.exists(scriptPath):
        return None

    files = os.listdir(scriptPath)
    upload_pathes = []

    for file in files:
        if not os.path.isdir(file):
            if prefix_name in file:
                upload_path = scriptPath + '/' + file
                upload_pathes.append(upload_path)

    monitor_print(f'----upload_jym_oss_upload_pathes:{upload_pathes}')

    if len(upload_pathes) == 0:
        return None

    url_info = upload_jym_oss_with_pathes(upload_pathes)
    if url_info is None or len(url_info) == 0:
        return None

    urls, cdn_urls = url_info

    if len(urls) == 0 or len(cdn_urls) == 0:
        return None

    if need_sort:
        monitor_print(f"sorted_urls_before:{urls}")
        sorted_urls = sorted(urls, key=get_number_from_path)
        monitor_print(f"sorted_urls_after:{sorted_urls}")

        monitor_print(f"sorted_cdn_urls_before:{cdn_urls}")
        sorted_cdn_urls = sorted(cdn_urls, key=get_number_from_path)
        monitor_print(f"sorted_cdn_urls_after:{sorted_cdn_urls}")

        for cdn_item in sorted_cdn_urls:
            request_workflow_task_status(cdn_item, f'上报sort_url', 5)
            # monitor_task_status(env, cdn_item, '',  5)
        return (sorted_urls, sorted_cdn_urls)
    else:
        for cdn_item in cdn_urls:
            request_workflow_task_status(cdn_item, f'上报url', 5)
        return (urls, cdn_urls)


def upload_jym_oss_with_pathes(image_pathes):
    sig_result = get_jym_oss_signature()
    monitor_print(f"---upload_jym_oss_with_pathes_sig_result:{sig_result}")
    if sig_result is None:
        monitor_task_status_v2('get_jym_oss_signature', "get_jym_oss_signature_none")
        return None

    final_sig_result_object = None
    is_new_api = True
    if is_new_api:
        final_sig_result_object = sig_result
    else:
        final_sig_result_json = sig_result['data']
        final_sig_result_object = json.loads(final_sig_result_json)


    final_sig_result = final_sig_result_object['result']
    if final_sig_result is None or len(final_sig_result) == 0:
        return None

    access_id = final_sig_result['accessId']
    policy = final_sig_result['policy']
    signature = final_sig_result['signature']
    dir = final_sig_result['dir']
    host = final_sig_result['host']
    expire = final_sig_result['expire']

    # 构建OSS上传URL
    url = host

    oss_path_list = []
    cdn_url_list = []
    image_info = []
    # 构建文件表单数据
    for image_path in image_pathes:
        local_file_path = image_path

        if not os.path.exists(local_file_path):
            continue

        file_name = os.path.basename(local_file_path)

        files = {
            'file': open(local_file_path, 'rb'),
        }
        object_name = f"{dir}{file_name}"

        # 设置请求参数
        params = {
            'OSSAccessKeyId': access_id,
            'policy': policy,
            'Signature': signature,
            'key': object_name,
            'success_action_status': '200',
        }
        # print(f"---2222:{params}")
        # 发送POST请求
        response = requests.post(url, data=params, files=files)

        if response.status_code == 200:
            oss_path = '/' + object_name
            cdn_url = 'https://static.jiaoyimao.com' + oss_path
            # print(f"-------3333:{response.status_code}  {oss_path}  {cdn_url}")
            oss_path_list.append(oss_path)
            cdn_url_list.append(cdn_url)
        else:
            retry_response = requests.post(url, data=params, files=files)

            if retry_response.status_code == 200:
                oss_path = '/' + object_name
                cdn_url = 'https://static.jiaoyimao.com' + oss_path
                # print(f"-------3333:{response.status_code}  {oss_path}  {cdn_url}")
                oss_path_list.append(oss_path)
                cdn_url_list.append(cdn_url)
            else:
                monitor_print(f"upload_jym_oss_with_pathes 重试失败，status_code: {retry_response.status_code}")
            # image_info.append((oss_path, cdn_url))

    # monitor_print(f"sorted_urls_before:{oss_path_list}")
    # sorted_urls = sorted(oss_path_list, key=get_number_from_path)
    # monitor_print(f"sorted_urls_after:{sorted_urls}")

    # monitor_print(f"sorted_cdn_urls_before:{cdn_url_list}")
    # sorted_cdn_urls = sorted(cdn_url_list, key=get_number_from_path)
    # monitor_print(f"sorted_cdn_urls_after:{sorted_cdn_urls}")
    monitor_print(f"---upload_jym_oss_with_pathes:{oss_path_list},{cdn_url_list}")
    return (oss_path_list, cdn_url_list)


def monitor_current_snapshot(name):
    env = AppEnv.get_instance()
    filename = 'monitor_current_snapshot_' + str(int(time.time() * 1000000)) + '.jpg'
    lx_safe_snapshot(filename=filename, msg="get a snapshot.")
    image_path = env.logPath + '/' + filename
    _, cdn_url_list = upload_jym_oss_with_pathes([image_path])
    monitor_task_status(env, f"调试截图_{name}", f"{cdn_url_list}")


def upload_biubiuoss_with_prefix_name(prefix_name, get_token_data):
    env = AppEnv.get_instance()
    monitor_print('upload_biubiuoss_with_prefix_name')
    stsToken = getBiubiuStsToken(env, get_token_data)
    auth = oss2.StsAuth(stsToken['accessKeyId'],
                        stsToken['accessKeySecret'], stsToken['securityToken'])

    bucketName = stsToken['bucket']

    # taskStatus = 5
    # urls = upload_lingxi_files(env, bucket, ossPrePath, bucketName, cdnDomain)

    monitor_print('upload_lingxi_files')
    scriptPath = env.logPath
    files = os.listdir(scriptPath)
    osspath = stsToken['fileKey']
    url = stsToken['fileUrl']
    endPoint = stsToken['publicEndpoint']
    monitor_print(
        f"bucketName: {bucketName}, endPoint:{endPoint}")
    urls = []
    bucket = oss2.Bucket(
        auth, endPoint, bucketName)
    needReport = False
    for file in files:
        if not os.path.isdir(file):
            if prefix_name in file:
                with open(scriptPath + '/' + file, 'rb') as fileobj:
                    monitor_print(f"upload_biubiu_files_with_prefix_name: {file}")
                    # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
                    fileobj.seek(0, os.SEEK_SET)
                    # Tell方法用于返回当前位置。
                    current = fileobj.tell()
                     
                    # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
                    monitor_print(f"upload_biubiuoss_with_prefix_name oss upload osspath:{osspath}")
                    result = bucket.put_object(osspath, fileobj)
                    if (result.status == 200):
                        monitor_print(f"upload_biubiuoss_with_prefix_name oss_upload finished:{url}")
                        urls.append(url)

    return urls


def getAdcTaskServerHost(env, custom_env_type=None, need_prefix=False):
    scriptEnv = env.scriptEnv
    if custom_env_type is not None:
        scriptEnv = custom_env_type
    host=""

    if need_prefix:
        if (scriptEnv == 'local'):
            # host = 'pre-adc-pc.alibaba-inc.com'
            host = 'http://pre-lingxi-adc-task-server.alibaba-inc.com'
        elif(scriptEnv == 'pre'):
            host = 'http://pre-lingxi-adc-task-server.alibaba-inc.com'
        elif(scriptEnv == 'prod'):
            host = 'http://lingxi-adc-task-server.alibaba-inc.com'
        else:
            host = 'http://pre-lingxi-adc-task-server.alibaba-inc.com'
    else:
        if (scriptEnv == 'local'):
            # host = 'pre-adc-pc.alibaba-inc.com'
            host = 'pre-lingxi-adc-task-server.alibaba-inc.com'
        elif(scriptEnv == 'pre'):
            host = 'pre-lingxi-adc-task-server.alibaba-inc.com'
        elif(scriptEnv == 'prod'):
            host = 'lingxi-adc-task-server.alibaba-inc.com'
        else:
            host = 'pre-lingxi-adc-task-server.alibaba-inc.com'

    return host


def getBiubiuStsToken(env, get_token_data):
    monitor_print(f"---getBiubiuStsToken")
    script_env = env.scriptEnv
    monitor_print(f"---getBiubiuStsToken: script_env {script_env}")
    host = getAdcTaskServerHost(env)
    url = f'http://{host}/biubiu/getOssToken'
    monitor_print(f"---getBiubiuStsToken: payload {get_token_data}")
    monitor_print(f"---getBiubiuStsToken: url {url}")
    for i in range(3):
        try:
            response = requests.post(url, json=get_token_data)

            # monitor_print(f"sts reponse url:{response.status}")
            monitor_print(f"---biubiu_sts reponse url:{response.url}")
            monitor_print(f"---biubiu_sts reponse text:{response.text}")
            result = response.json()
            monitor_print(f"---biubiu_sts result: {result}")
            if result['code'] != 200:
                monitor_print(f"---biubiu_sts_result_code_error: {result}")
                continue
            if result['data'] is None:
                monitor_print(f"---biubiu_sts_result_data_error is None: {result}")
                continue
            return result['data']['data']
        except Exception as e:
            monitor_print(f"---biubiu_sts_result_error: {e}")
            continue
    return None
    
if __name__ == '__main__':
    oss_path_list, cdn_url_list = upload_jym_oss_with_pathes(
        ['/Users/two/Desktop/CA6EA94A-0D4E-4F1F-A112-9B66C80508CF.png'])
    print(oss_path_list, cdn_url_list)
