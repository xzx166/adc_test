# -*- encoding=utf8 -*-


import argparse
import os
import sys
import time
from pathlib import Path
import subprocess
__author__ = "xiaohanzhu"

PYTHONPATH = str(Path(__file__).resolve().parent.parent)
os.environ.update(PYTHONPATH=PYTHONPATH)
sys.path.insert(0, PYTHONPATH)

from utility.base.adc_environment import *
from utility.base.adc_monitor import *

# ----------------确定机器类型------------------
def set_chip_type():
    try:
        # 执行 sysctl 命令获取机器硬件信息
        result = subprocess.run(['sysctl', 'machdep.cpu.brand_string'], capture_output=True, text=True)

        # 获取输出并解析
        chip_type = result.stdout.strip()
        monitor_print(f"chip_type:{chip_type}")

        dynamic_info = AppDynamicInfo.get_instance()
        chip_start_time = time.perf_counter()
        chip_end_time = time.perf_counter()
        monitor_print(f"---set_chip_type:{chip_end_time - chip_start_time}, {chip_type}")
        if 'M3' in chip_type or 'M4' in chip_type:
            dynamic_info.setIsM3Support(True)

    except Exception as e:
        monitor_print(f"---set_chip_type_error:{e}")

set_chip_type()


from utility.app.adc_application import *

if __name__ == '__main__':
    # 解析参数,注意这里一定要在Application初始化之前调用
    main_parse_args(system_type='android')
    app = Application()
    app.start()

