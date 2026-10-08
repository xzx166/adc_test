# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

from airtest.core.api import *
from utility.base.adc_utils import *

auto_setup(__file__)

def touch_number_keyboard(sms_code):
    number_map = {'0': (1015,1277), '1': (501,819), '2':(1015,819),'3':(1525,819),
                    '4':(504,972), '5':(1018,975), '6':(1528,975),
                    '7':(510,1122), '8':(1015,1125), '9':(1528,1127)}
    for item in sms_code:
        number_point = number_map[item]
        touch(number_point)
        sleep(0.2)
#
#
# def is_valid_phone_number(phone_number):
#     pattern = r'^1[3456789]\d{9}$'  # 以1开头，后面跟10位数字
#
#     is_phone = False
#     if re.match(pattern, phone_number):
#         is_phone = True
#     else:
#         is_phone = False
#     print(f'--xxxxyy:{is_phone}')
#     return is_phone
#
#
# def is_six_digit_number(string):
#     if string.isdigit() and len(string) == 6:
#         return True
#     else:
#         return False
#
#
# # 正则表达式匹配中文字符
# def tool_contains_chinese(text):
#     pattern = re.compile(r'[一-龥]')
#     if re.search(pattern, text):
#         return True
#     else:
#         return False
#
# def is_valid_json(json_str):
#     try:
#         json.loads(json_str)
#         return True
#     except ValueError:
#         return False
#
# def get_num_from_str(string, all_num=False):
#     pattern = re.compile(r'\d+')
#     nums = re.findall(pattern, string)
#     if nums:
#         if all_num:
#             return nums
#         else:
#             return nums[0]
#     else:
#         return None
#
# def contains_digit(s):
#     return bool(re.search(r'\d', s))
#
# def get_memory_usage():
#     # 获取当前进程的PID
#     pid = os.getpid()
#
#     # 使用`ps`命令获取当前进程的信息
#     command = f'ps -o rss= -p {pid}'
#     memory_usage = subprocess.check_output(command, shell=True, text=True)
#
#     return memory_usage.strip()  # 返回占用的内存（以KB为单位）






