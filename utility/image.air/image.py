# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

from airtest.core.api import *


using("../utility/api.air")
from api import *

from utility.app.service.adc_ocr import *

# using("../utility/base")
# from adc_image import *

from utility.base.adc_image import *

using("../utility/monitor.air")
from monitor import *

# 截图并ocr
def crop_image_and_ocr(p1, p2, ocr_type='ch'):
    monitor_print(f"---crop_image_and_ocr: {p1}, {p2}, {ocr_type}")
    crop_qufu_name = f"adc_catch_crop_image_and_ocr_{str(int(time.time() * 1000000))}.jpg"
    lx_crop_image(p1, p2, write_name=crop_qufu_name)
    crop_qufu_image_path = os.path.join(ST.LOG_DIR, crop_qufu_name)
    result_arr = None
    if ocr_type == 'ch':
        result_arr = ocr_chinese_by_eas(crop_qufu_image_path)
    elif ocr_type == 'num':
        result_arr = ocr_num_by_eas(crop_qufu_image_path)

    return result_arr






