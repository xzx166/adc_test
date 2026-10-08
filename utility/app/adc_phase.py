# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

import time

from utility.base.adc_monitor import *

class Phase:
    def __init__(self, name, doTask):
        self.name = name
        self.doTask = doTask

    def run(self, env):
        monitor_task_status(env, f"{self.name}  start", '')
        performance_start_timestamp = int(time.time() * 1000000)
        self.doTask()
        performance_interval = int(time.time() * 1000000) - performance_start_timestamp
        monitor_task_status(env, f"{self.name}  end", f"phase cost {performance_interval} us(微秒)")
        monitor_task_status(env, f"{self.name}  end", f"phase结束专门上报5，保证设备不超时", status=5)