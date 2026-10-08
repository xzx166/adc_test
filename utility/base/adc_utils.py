# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

import re
import os
import json

import time
import subprocess

import glob
import shutil


# todo - 替换touch
from utility.base.adc_api import *
from utility.base.adc_monitor import *

def is_valid_phone_number(phone_number):
    pattern = r'^1[3456789]\d{9}$'  # 以1开头，后面跟10位数字

    is_phone = False
    if re.match(pattern, phone_number):
        is_phone = True
    else:
        is_phone = False
    print(f'--xxxxyy:{is_phone}')
    return is_phone


def is_six_digit_number(string):
    if string.isdigit() and len(string) == 6:
        return True
    else:
        return False


# 正则表达式匹配中文字符
def tool_contains_chinese(text):
    pattern = re.compile(r'[一-龥]')
    if re.search(pattern, str(text)):
        return True
    else:
        return False


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except Exception as e:
        return False


def get_num_from_str(string, all_num=False):
    pattern = re.compile(r'\d+')
    nums = re.findall(pattern, string)
    if nums:
        if all_num:
            return nums
        else:
            return nums[0]
    else:
        return None


def contains_digit(s):
    return bool(re.search(r'\d', s))


def get_memory_usage():
    # 获取当前进程的PID
    pid = os.getpid()

    # 使用`ps`命令获取当前进程的信息
    command = f'ps -o rss= -p {pid}'
    memory_usage = subprocess.check_output(command, shell=True, text=True)

    return memory_usage.strip()  # 返回占用的内存（以KB为单位）


# --------------文件相关操作---------------------
def delete_files_with_format(env, index, directory, file_format, except_string=None):
    files = glob.glob(os.path.join(directory, file_format))
    monitor_task_status(env, f"清理{directory}目录下的{file_format}文件", '')
    if except_string:
        # 过滤不包含adc_前缀的文件名
        files = [file for file in files if not except_string in file]
    for file in files:
        os.remove(file)


def rename_file_with_format(env, index, directory, file_format):
    files = glob.glob(os.path.join(directory, file_format))
    for file in files:
        filename = os.path.basename(file)
        name_without_extension = os.path.splitext(filename)[0]
        if '_' in name_without_extension:
            continue

        extesion = os.path.splitext(filename)[1]
        newname = name_without_extension + '_' + str(index) + extesion
        oldFilePath = file
        newFilePath = directory + '/' + newname
        monitor_task_status(env, '重命名log文件', f"{newFilePath}")
        copy_file_with_path(oldFilePath, newFilePath)


def copy_file_with_path(old_path, new_path):
    monitor_print(f"{old_path}")
    monitor_print(f"{new_path}")
    shutil.copy2(old_path, new_path)


def is_directory_exists(directory):
    return os.path.exists(directory) and os.path.isdir(directory)


def get_log_txt_files(env):
    scriptPath = env.logPath
    files = os.listdir(scriptPath)
    upload_pathes = []

    for file in files:
        if not os.path.isdir(file):
            if 'log' in file:
                upload_path = scriptPath + '/' + file
                upload_pathes.append(upload_path)
    return upload_pathes

def get_files_with_prefix(directory, prefix):
    file_list = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(prefix):
                file_list.append(os.path.join(root, file))

    return file_list


def get_sorted_files_with_prefix(directory, prefix):
    file_list = get_files_with_prefix(directory, prefix)

    def get_time_from_path(path):
        file_name = path.split("/")[-1]
        result = file_name.split("_")[-1].split(".")[0]
        return int(result)

    monitor_print(f"sorted_files_before:{file_list}")
    sorted_urls = sorted(file_list, key=get_time_from_path)
    monitor_print(f"sorted_files_after:{sorted_urls}")
    return sorted_urls

def get_directory_sorted_timestamp_files(directory):

    sorted_files = None
    # 获取目录下所有文件
    files = os.listdir(directory)

    # 使用正则表达式匹配时间戳命名的.jpg文件，并提取时间戳
    pattern = r"(\d+)\.jpg$"
    timestamped_files = [os.path.join(directory, file) for file in files if re.match(pattern, file)]
    sorted_files = sorted(timestamped_files, key=lambda x: int(re.search(pattern, x).group(1)))

    return sorted_files
