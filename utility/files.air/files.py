# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

from airtest.core.api import *

using("../utility/monitor.air")
from monitor import *

using("../utility/api.air")
from api import *

from utility.base.adc_utils import *

auto_setup(__file__)

import os
import glob
import time
import shutil

import re
import json


def update_taskid_subext_file(task_id, file_name, ext_info):
    monitor_print(f"---update_taskid_subext_file:{task_id} {file_name} {ext_info}")

    home_path = os.path.expanduser("~")
    directory = os.path.join(home_path, ".adc")
    # 判断目录是否存在
    if os.path.exists(directory):
        print(f"目录 {directory} 已存在")
    else:
        # 创建目录
        os.makedirs(directory)
        print(f"目录 {directory} 创建成功")

    sec_dir = os.path.join(directory, task_id)
    # 判断目录是否存在
    if os.path.exists(sec_dir):
        print(f"目录 {sec_dir} 已存在")
    else:
        # 创建目录
        os.makedirs(sec_dir)
        print(f"目录 {sec_dir} 创建成功")

    # file_name = f"sub_ext.json"
    # 拼接文件路径
    filepath = os.path.join(sec_dir, file_name)
    
    # 创建文件
    ext_json = json.dumps(ext_info)
    with open(filepath, "w") as file:
        file.write(ext_json)

    print(f"文件 {filepath} 创建成功")

def get_taskid_subext_file(task_id, file_name):
    monitor_print(f"---get_taskid_subext_file:{task_id} {file_name}")
    home_path = os.path.expanduser("~")
    directory = os.path.join(home_path, ".adc")
    # 判断目录是否存在
    if not os.path.exists(directory):
        return None

    print(f"目录 {directory} 已存在")
    sec_dir = os.path.join(directory, task_id)
    # 判断目录是否存在
    if not os.path.exists(sec_dir):
        return None

    print(f"目录 {sec_dir} 已存在")
    # file_name = f"sub_ext.json"
    # 拼接文件路径
    filepath = os.path.join(sec_dir, file_name)
    # 判断文件是否存在
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, "r") as file:
        content = file.read()
        json_content = json.loads(content)
        monitor_print(f"---get_taskid_subext_file_json_content:{json_content}")
        return json_content


def clean_all_info_file(task_id):
    home_path = os.path.expanduser("~")
    directory = os.path.join(home_path, ".adc")
    # 判断目录是否存在
    if os.path.exists(directory):
        print(f"目录 {directory} 已存在")
        sec_dir = os.path.join(directory, task_id)
        # 判断目录是否存在
        if os.path.exists(sec_dir):
            print(f"目录 {sec_dir} 已存在")

        else:
            return
    else:
        return
    sec_dir = os.path.join(directory, task_id)
    # 判断目录是否存在
    if os.path.exists(sec_dir):
        print(f"目录 {sec_dir} 已存在")
        try:
            shutil.rmtree(sec_dir)
            print(f"Directory {sec_dir} and all its contents were removed successfully")
        except OSError as error:
            print(f"Error: {error}")
    else:
        return

def remove_script_end_task_file(task_id):
    home_path = os.path.expanduser("~")
    directory = os.path.join(home_path, ".adc")
    # 判断目录是否存在
    if os.path.exists(directory):
        print(f"目录 {directory} 已存在")
    else:
        # 创建目录
        os.makedirs(directory)
        print(f"目录 {directory} 创建成功")

    file_name = f"{str(task_id)}.lock"
    # 拼接文件路径
    filepath = os.path.join(directory, file_name)
    # 判断文件是否存在
    if os.path.exists(filepath):
        # 删除文件
        os.remove(filepath)
        print(f"文件 {filepath} 删除成功")
    else:
        print(f"文件 {filepath} 不存在 ")