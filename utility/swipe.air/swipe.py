# -*- encoding=utf8 -*-
__author__ = "xiaohanzhu"

from airtest.core.api import *
from airtest.aircv import *


using("../utility/monitor.air")
from monitor import *

using("../utility/api.air")
from api import *

using("../utility/image.air")
from image import *

using("../utility/upload.air")
from upload import *

import cv2
import numpy as np
import math

auto_setup(__file__)

swipe_duration = 0.5
swipe_touchEnd = False
system_portrait = False
swipe_adc_catch = False

swipe_bottom_retry = 1

def toSetSwipeDuration(duration):
    global swipe_duration
    swipe_duration = duration

def toSetSwipeTouchEnd(needTouch):
    global swipe_touchEnd
    swipe_touchEnd = needTouch

def toSetSwipeAdcCatch(needCatch):
    global swipe_adc_catch
    swipe_adc_catch = needCatch

# 在竖屏的游戏中，必须调用该方法，确保swipe方法中的resolution的宽高是竖屏的
def toSetSystemPortrait():
    global system_portrait
    system_portrait = True

def toSetSwipeBottomRetry(retry):
    global swipe_bottom_retry
    swipe_bottom_retry = retry

def get_system_portrait_resolution():
    global system_portrait
    if system_portrait:
        return (1350, 2400)
    else:
        return (2400, 1350)

def swipe_only(startPos, endPos, duration=0.8):
    d = AppEnv.get_instance().device
    lx_swipe(d, startPos, endPos, duration) 



###***********************纵向滑动***********************

#默认支持纵向滑动
def lx_swipe(actionDevice, p1, p2, duration=0.5, steps=5):
    # actionDevice.touch_proxy.touch(p1)
    from_x, from_y = p1
    to_x, to_y = p2

    global swipe_duration
    actionDevice.touch_proxy.swipe_along([(from_x, from_y), (to_x, to_y-2), (to_x, to_y)], duration=swipe_duration)

    if swipe_touchEnd:
        actionDevice.touch_proxy.touch(p2)
    

def swipe_with_seperate(startPos, endPos, seperate_count=1):
    d = AppEnv.get_instance().device
    for i in range(seperate_count):
        lx_swipe(d, startPos, endPos)
        sleep(0.5)
    
    
    

# 该接口不再维护，请不要使用，使用新接口swipe_crop_many_rows 
# 该接口不再维护，请不要使用，使用新接口swipe_crop_many_rows
# 该接口不再维护，请不要使用，使用新接口swipe_crop_many_rows
# 单行截图的接口，并且一页只展示一行，
#startPos, endPos 滑动开始坐标和结束坐标
# check_bottom_start, check_bottom_end  用于check是否滑到底，基于滑动区域外的开始坐标和结束坐标构成的区域
# crop_start, crop_end   截取的图片区域，基于开始坐标和结束坐标构成的区域
# crop_bottom_start, crop_bottom_end  当滑到底部的时候需要截取的图片区域，基于开始坐标和结束坐标构成的区域 
# combine_part_name  图片的分组名称, 最终的命名规范：combine_image_{combine_part_name}_{时间戳}.jpg，注意：不要用中文
def swipe_crop_row(startPos, endPos, check_bottom_start, check_bottom_end,crop_start, crop_end,crop_bottom_start, crop_bottom_end,combine_part_name, bottom_confidence=0.75):
    isBottom = 0
    count=0
    crop_imgs = []

    crop_pos_img = crop_pos_image_from_snapshot(f"final_crop_snapshot_{combine_part_name}_{count}.jpg", f"cropped_image_{combine_part_name}_0.jpg", crop_start,crop_end)
    crop_imgs.append(crop_pos_img)

    monitor_print(f"----------cropped_image_{combine_part_name}_0.jpg")

    android = AppEnv.get_instance().device
    while isBottom == 0: 
        count=count+1
        monitor_print(f"----------{count}")


        isBottom = swipe_with_bottom(startPos, endPos, check_bottom_start, check_bottom_end,crop_start, bottom_confidence = bottom_confidence)
        
        
        result_img = None
        if isBottom == 0:
            result_img = crop_pos_image_from_snapshot(f"final_crop_snapshot_{combine_part_name}_{count}.jpg", f"cropped_image_{combine_part_name}_{count}.jpg", crop_start,crop_end)
        else:
            result_img = crop_pos_image_from_snapshot(f"final_crop_snapshot_{combine_part_name}_{count}.jpg", f"cropped_image_{combine_part_name}_{count}.jpg", crop_bottom_start,crop_bottom_end)  

        crop_imgs.append(result_img)
        monitor_print(f"----------cropped_image_{combine_part_name}_{count}.jpg")
        
            
    return crop_imgs


class CropManyRowModel:
    def __init__(self, swipe_start_pos,swipe_end_pos,check_bottom_start, check_bottom_end, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, max_swipe_count=None, bottom_confidence=None, swipe_sleep=None):
        self.swipe_start_pos = swipe_start_pos
        self.swipe_end_pos = swipe_end_pos
        self.check_bottom_start = check_bottom_start
        self.check_bottom_end = check_bottom_end
        self.crop_data = crop_data
        self.bottom_origin_pos = bottom_origin_pos
        self.combine_part_name = combine_part_name
        self.check_normal_image_func = check_normal_image_func
        self.seperate_count = seperate_count
        self.max_swipe_count = max_swipe_count
        self.bottom_confidence = bottom_confidence
        self.swipe_sleep = swipe_sleep

# 适用于多行截图 - 带判底的多行!!!
def swipe_crop_many_rows_by_model(model):

    swipe_start_pos = model.swipe_start_pos
    swipe_end_pos = model.swipe_end_pos
    check_bottom_start = model.check_bottom_start
    check_bottom_end = model.check_bottom_end
    crop_data = model.crop_data
    bottom_origin_pos = model.bottom_origin_pos 
    combine_part_name = model.combine_part_name
    check_normal_image_func = model.check_normal_image_func
    seperate_count = model.seperate_count
    max_swipe_count= model.max_swipe_count
    bottom_confidence = model.bottom_confidence
    swipe_sleep = model.swipe_sleep 

    origin_x,origin_y,  width,heigt,  interval_x,interval_y, count_x,count_y = crop_data

    bottom_origin_x, bottom_origin_y = bottom_origin_pos


    # swipe_start_pos_y = origin_y + (interval_y+heigt) * count_y
    # swipe_end_pos_y = origin_y
    # swipe_start_pox_x = origin_x + width + 2 

    # swipe_start_pos = (swipe_start_pox_x,swipe_start_pos_y)
    # swipe_end_pos = (swipe_start_pox_x, swipe_end_pos_y)

    bottom_pos_list = []
    for index in range(count_y):
        bottom_y = bottom_origin_y + index * (interval_y+heigt)
        bottom_pos_list.append((origin_x, bottom_y))

    bottomType = 0
    count=0
    crop_imgs = []

    android = AppEnv.get_instance().device

    while bottomType == 0: 
        count=count+1
        monitor_print(f"----------{count}")

        snap_file_name = f"adc_record_swipe_final_crop_snapshot_{combine_part_name}_{count}.jpg"
        # lx_safe_snapshot(filename=snap_file_name, msg="Please fill in the test point.")
        
        crop_start_pos_x = origin_x 
        crop_start_pos_y = origin_y
        crop_end_pos_x = crop_start_pos_x + width * count_x + interval_x * (count_x-1)
        crop_end_pos_y = crop_start_pos_y + heigt * count_y + interval_y * (count_y-1) + interval_y//2

        result_img = crop_pos_image_from_snapshot(snap_file_name, f"cropped_image_{combine_part_name}_{count}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))
        
        snap_file_path = os.path.join(ST.LOG_DIR, snap_file_name)
        snap_file_image = cv2.imread(snap_file_path)
        if check_normal_image_func is not None:
            if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), snap_file_image):
                crop_imgs.append(result_img)
            else:
                return crop_imgs
        else:
            crop_imgs.append(result_img)

        # if swipe_count > 0:
        #     if count >= swipe_count:
        #         break
        
        if max_swipe_count is not None :
            if count >= max_swipe_count:
                monitor_print(f"-------------max_swipe_count break")
                break
                
        
        if count == 1:
            crop_top_start_pos_x = origin_x 
            crop_top_start_pos_y = origin_y
            crop_top_end_pos_x = crop_top_start_pos_x + width * count_x + interval_x * (count_x-1)
            crop_top_end_pos_y = crop_top_start_pos_y + heigt 
            bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,(origin_x, origin_y), bottom_pos_list,  seperate_count, check_top_area = (crop_top_start_pos_x, crop_top_start_pos_y, crop_top_end_pos_x,crop_top_end_pos_y),bottom_tolerance=interval_y,bottom_confidence=bottom_confidence)
        else:
            bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,(origin_x, origin_y), bottom_pos_list, seperate_count, bottom_tolerance=interval_y,bottom_confidence=bottom_confidence)
        monitor_print(f"-------------bottomType: {bottomType}")

        if swipe_sleep is not None:
            sleep(swipe_sleep)

        if bottomType == 0:
            continue
        elif bottomType == -1:
            break
        elif bottomType > 0:
            btm_index = bottomType -1
            btm_cur_pos = bottom_pos_list[btm_index]
            btm_cur_pos_x, btm_cur_pos_y = btm_cur_pos

            btm_row_count = count_y - btm_index

            snap_bottom_file_name = f"adc_record_swipe_final_crop_bottom_snapshot_{combine_part_name}_{count}_bottom.jpg"
            # lx_safe_snapshot(filename=snap_bottom_file_name, msg="Please fill in the test point.")

            crop_start_pos_x = btm_cur_pos_x 
            crop_start_pos_y = btm_cur_pos_y
            crop_end_pos_x = crop_start_pos_x + width * count_x + interval_x * (count_x-1)
            crop_end_pos_y = crop_start_pos_y + heigt * btm_row_count + interval_y * (btm_row_count-1)

            result_img = crop_pos_image_from_snapshot(snap_file_name, f"cropped_image_{combine_part_name}_{count}_bottom.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))
            
            snap_file_path = os.path.join(ST.LOG_DIR, snap_file_name)
            snap_file_image = cv2.imread(snap_file_path)
            if check_normal_image_func is not None:
                if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), snap_file_image):
                    crop_imgs.append(result_img)
                else:
                    return crop_imgs
            else:
                crop_imgs.append(result_img)

            # 退出while循环   
            break
        
    return crop_imgs

# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 适用于多行截图 - 带判底的多行!!!
def swipe_crop_many_rows(swipe_start_pos,swipe_end_pos,check_bottom_start, check_bottom_end, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, max_swipe_count=None, bottom_confidence=None, swipe_sleep=None):
    model = CropManyRowModel(swipe_start_pos,swipe_end_pos,check_bottom_start, check_bottom_end, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func, seperate_count, max_swipe_count, bottom_confidence, swipe_sleep)
    
    return swipe_crop_many_rows_by_model(model)


class CropManyRowWithCountModel:
    def __init__(self,swipe_start_pos,swipe_end_pos, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, swipe_count=0, swipe_count_remainder=None):
        self.swipe_start_pos = swipe_start_pos
        self.swipe_end_pos = swipe_end_pos
        self.crop_data = crop_data
        self.bottom_origin_pos = bottom_origin_pos
        self.combine_part_name = combine_part_name
        self.check_normal_image_func = check_normal_image_func
        self.seperate_count = seperate_count
        self.swipe_count = swipe_count 
        self.swipe_count_remainder = swipe_count_remainder

def swipe_crop_many_rows_with_count_by_model(model):
    swipe_start_pos = model.swipe_start_pos
    swipe_end_pos = model.swipe_end_pos
    crop_data = model.crop_data
    bottom_origin_pos = model.bottom_origin_pos
    combine_part_name = model.combine_part_name
    check_normal_image_func = model.check_normal_image_func
    seperate_count = model.seperate_count
    swipe_count = model.swipe_count
    swipe_count_remainder = model.swipe_count_remainder


    origin_x,origin_y,  width,heigt,  interval_x,interval_y, count_x,count_y = crop_data

    bottom_origin_x, bottom_origin_y = bottom_origin_pos

    bottom_pos_list = []
    for index in range(count_y):
        bottom_y = bottom_origin_y + index * (interval_y+heigt)
        bottom_pos_list.append((origin_x, bottom_y))

    bottomType = 0
    count=0
    crop_imgs = []

    android = AppEnv.get_instance().device

    while bottomType == 0: 
        count=count+1
        monitor_print(f"----------{count}")

        snap_file_name = f"adc_record_swipe_final_crop_snapshot_{combine_part_name}_{count}.jpg"
        # lx_safe_snapshot(filename=snap_file_name, msg="Please fill in the test point.")
        
        crop_start_pos_x = origin_x 
        crop_start_pos_y = origin_y
        crop_end_pos_x = crop_start_pos_x + width * count_x + interval_x * (count_x-1)
        crop_end_pos_y = crop_start_pos_y + heigt * count_y + interval_y * (count_y-1) + interval_y//2

        result_img = crop_pos_image_from_snapshot(snap_file_name, f"adc_record_swipe_cropped_image_{combine_part_name}_{count}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))
        
        snap_file_path = os.path.join(ST.LOG_DIR, snap_file_name)
        snap_file_image = cv2.imread(snap_file_path)
        if check_normal_image_func is not None:
            if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), snap_file_image):
                crop_imgs.append(result_img)
            else:
                return crop_imgs
        else:
            crop_imgs.append(result_img)

        # if swipe_count > 0:
        #     if count >= swipe_count:
        #         break
        
        if swipe_count <= 0:
            monitor_print(f"-------xxxxxxx{swipe_count}")
            bottomType = -1
        else:
            swipe_with_seperate(swipe_start_pos, swipe_end_pos, seperate_count)
            if count == swipe_count:
                if swipe_count_remainder is not None and swipe_count_remainder > 0:
                    remainder_row_count = swipe_count_remainder//count_x
                    if swipe_count_remainder%count_x > 0:
                        remainder_row_count = remainder_row_count + 1
                        
                    bottomType = (count_y - remainder_row_count)+1
                    # bottomType = (count_y - swipe_count_remainder)+1
                else:
                    bottomType = 0
            elif count == swipe_count + 1:
                break

        if bottomType == 0:
            continue
        elif bottomType == -1:
            break
        elif bottomType > 0:
            # 解决底部回弹问题
            sleep(2)
            
            btm_index = bottomType -1
            btm_cur_pos = bottom_pos_list[btm_index]
            btm_cur_pos_x, btm_cur_pos_y = btm_cur_pos

            btm_row_count = count_y - btm_index

            # snap_bottom_file_name = f"final_crop_bottom_snapshot_{combine_part_name}_{count}_bottom.jpg"
            # lx_safe_snapshot(filename=snap_bottom_file_name, msg="Please fill in the test point.")
            

            crop_start_pos_x = btm_cur_pos_x 
            crop_start_pos_y = btm_cur_pos_y
            crop_end_pos_x = crop_start_pos_x + width * count_x + interval_x * (count_x-1)
            crop_end_pos_y = crop_start_pos_y + heigt * btm_row_count + interval_y * (btm_row_count-1)

            result_img = crop_pos_image_from_snapshot(snap_file_name, f"cropped_image_{combine_part_name}_{count}_bottom.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))
            
            snap_file_path = os.path.join(ST.LOG_DIR, snap_file_name)
            snap_file_image = cv2.imread(snap_file_path)
            if check_normal_image_func is not None:
                if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), snap_file_image):
                    crop_imgs.append(result_img)
                else:
                    return crop_imgs
            else:
                crop_imgs.append(result_img)

            # 退出while循环   
            break
        
    return crop_imgs

# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 适用于多行截图 - 不带判底的多行!!!只根据swipe_count决定滑动次数
def swipe_crop_many_rows_with_count(swipe_start_pos,swipe_end_pos, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, swipe_count=0, swipe_count_remainder=None):
    model = CropManyRowWithCountModel(swipe_start_pos,swipe_end_pos, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func, seperate_count, swipe_count, swipe_count_remainder)    

    return swipe_crop_many_rows_with_count_by_model(model)


# need_top_bottom 表示当首页只有一页的情况下
class CropIndividualModel:
    def __init__(self, swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, max_swipe_count=None,bottom_confidence=None, check_normal_image_continue=False,  visual_count_y=None, bottom_tolerance=None, expect_swipe_only=False,swipe_duration=0.5, top_tolerance=None, process_func=None, process_func_continue=False, need_top_page_bottom_pos=None):
        self.swipe_start_pos = swipe_start_pos
        self.swipe_end_pos = swipe_end_pos
        self.check_bottom_start = check_bottom_start
        self.check_bottom_end = check_bottom_end
        self.crop_data = crop_data
        self.bottom_origin_pos = bottom_origin_pos
        self.combine_part_name = combine_part_name
        self.check_normal_image_func = check_normal_image_func
        self.check_normal_image_continue = check_normal_image_continue
        self.seperate_count = seperate_count
        self.max_swipe_count = max_swipe_count
        self.bottom_confidence = bottom_confidence
        self.visual_count_y = visual_count_y  # 实际界面有两行半，但是第三行无法用于判底的情况
        self.bottom_tolerance = bottom_tolerance
        self.expect_swipe_only = expect_swipe_only
        self.swipe_duration = swipe_duration
        self.top_tolerance = top_tolerance
        self.process_func = process_func
        self.process_func_continue = process_func_continue
        self.need_top_page_bottom_pos = need_top_page_bottom_pos

# 适用于多行中多对象截图 - 带判底的
# check_bottom_start, check_bottom_end  用于确定底部的截图坐标
# crop_data 每个单独截图的对象的信息，包括：x坐标，y坐标，宽，高，间隔x，间隔y，横向的数量，纵向滑动的数量
# bottom_origin_pos 滑动到底部后的可能的第一行的x,y坐标（底部可能的第一行指：底部的纵向滑动数量的倒数行）
# combine_part_name  用于区分不同组截图的名称
# check_normal_image_func  用于判断截图是否正常,入参是img对象，返回值是bool值
# seperate_count  用于确定需要几次完成一个纵向滑动的数量
def swipe_crop_individual_by_model(model):
    swipe_start_pos = model.swipe_start_pos
    swipe_end_pos = model.swipe_end_pos
    check_bottom_start = model.check_bottom_start 
    check_bottom_end = model.check_bottom_end
    crop_data = model.crop_data
    bottom_origin_pos = model.bottom_origin_pos
    combine_part_name = model.combine_part_name
    check_normal_image_func = model.check_normal_image_func
    seperate_count = model.seperate_count
    max_swipe_count = model.max_swipe_count
    bottom_confidence = model.bottom_confidence
    check_normal_image_continue = model.check_normal_image_continue
    bottom_tolerance = model.bottom_tolerance
    expect_swipe_only = model.expect_swipe_only

    origin_x,origin_y,  width,heigt,  interval_x,interval_y, count_x,count_y = crop_data

    bottom_origin_x, bottom_origin_y = bottom_origin_pos
    visual_count_y = model.visual_count_y

    swipe_duration = model.swipe_duration
    top_tolerance = model.top_tolerance

    process_func = model.process_func
    process_func_continue = model.process_func_continue
    need_top_page_bottom_pos = model.need_top_page_bottom_pos


    # swipe_start_pos_y = origin_y + (interval_y+heigt) * count_y
    # swipe_end_pos_y = origin_y
    # swipe_start_pox_x = origin_x + width + 2 

    # swipe_start_pos = (swipe_start_pox_x,swipe_start_pos_y)
    # swipe_end_pos = (swipe_start_pox_x, swipe_end_pos_y)

    bottom_pos_list = []
    for index in range(count_y if not visual_count_y else visual_count_y):
        bottom_y = bottom_origin_y + index * (interval_y+heigt)
        bottom_pos_list.append((origin_x, bottom_y))

    bottomType = 0
    count=0
    crop_imgs = []

    android = AppEnv.get_instance().device

    while bottomType == 0: 
        count=count+1
        monitor_print(f"----------swipe_crop_individual_by_model:{count}")

        snap_file_name = f"adc_record_swipe_final_crop_snapshot_{combine_part_name}_{count}.jpg"
        lx_safe_snapshot(filename=snap_file_name, msg="Please fill in the test point.")
        snap_file_path = os.path.join(ST.LOG_DIR, snap_file_name)
        snap_file_image = cv2.imread(snap_file_path)

        for i in range(count_x * count_y):
            row_index = i//count_x+1
            column_index = i%count_x+1
            
            crop_start_pos_x = origin_x + (column_index-1) * (interval_x+width)
            crop_start_pos_y = origin_y + (row_index-1) * (interval_y+heigt)
            crop_end_pos_x = crop_start_pos_x + width
            crop_end_pos_y = crop_start_pos_y + heigt
            
            result_img = crop_pos_image_from_snapshot(snap_file_name, f"adc_record_swipe_cropped_image_{combine_part_name}_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), False)
            if check_normal_image_func is not None:
                if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y),snap_file_image):
                    crop_imgs.append(result_img)
                else:
                    if check_normal_image_continue == False:
                        return crop_imgs
            else:
                if process_func is not None:
                    if process_func(result_img, (crop_start_pos_x, crop_start_pos_y),
                                               (crop_end_pos_x, crop_end_pos_y),(count, row_index, column_index, 'normal'), snap_file_image):
                        crop_imgs.append(result_img)
                    else:
                        if process_func_continue == False:
                            return crop_imgs
                else:
                    crop_imgs.append(result_img)

        # if swipe_count > 0:
        #     if count >= swipe_count:
        #         print(f"-------------swipe_count: {swipe_count}")
        #         break
        if max_swipe_count is not None :
            if count >= max_swipe_count:
                monitor_print(f"-------------max_swipe_count break")
                break

        if bottom_tolerance is not None :
            toler = bottom_tolerance
        else:
            toler = interval_y


        if count == 1:
            if expect_swipe_only:
                monitor_print(f"-------------bottomType expect_swipe_only: {bottomType}")
                swipe_only(swipe_start_pos, swipe_end_pos)
            else:
                crop_top_start_pos_x = origin_x 
                crop_top_start_pos_y = origin_y
                crop_top_end_pos_x = crop_top_start_pos_x + width * count_x + interval_x * (count_x-1)
                crop_top_end_pos_y = crop_top_start_pos_y + heigt 
                bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,(origin_x, origin_y), bottom_pos_list, seperate_count, check_top_area = (crop_top_start_pos_x, crop_top_start_pos_y, crop_top_end_pos_x,crop_top_end_pos_y),bottom_tolerance=toler,bottom_confidence=bottom_confidence, swipe_duration=swipe_duration, top_tolerance=top_tolerance, combine_part_name=combine_part_name)
        else:
            if expect_swipe_only:
                monitor_print(f"-------------bottomType expect_swipe_only: {bottomType}")
                swipe_only(swipe_start_pos, swipe_end_pos)
            else:
                bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,(origin_x, origin_y), bottom_pos_list, seperate_count,bottom_tolerance=toler,bottom_confidence=bottom_confidence, swipe_duration=swipe_duration, top_tolerance=top_tolerance, combine_part_name=combine_part_name)
        monitor_print(f"-------------bottomType: {bottomType}")

        if bottomType == 0:
            continue
        elif bottomType == -1:
            # 这里的逻辑是为了处理当只有一页的情况下，并且出现了最后一行个数比count_y多1个的情况，因为正常情况下不会出现多一行，多一行是因为底部的半行无法用于识别底部，只能用倒数第二行来识别
            monitor_print(f"-------------swipe_bottomType: {bottomType}")
            if need_top_page_bottom_pos is not None:
                btm_cur_pos_x, btm_cur_pos_y = need_top_page_bottom_pos

                snap_bottom_file_name = f"adc_record_swipe_final_crop_bottom_snapshot_{combine_part_name}_{count}.jpg"
                lx_safe_snapshot(filename=snap_bottom_file_name, msg="Please fill in the test point.")
                snap_file_path = os.path.join(ST.LOG_DIR, snap_bottom_file_name)
                snap_file_image = cv2.imread(snap_file_path)

                btm_total_count = count_x

                for i in range(btm_total_count):
                    row_index = i // count_x + 1
                    column_index = i % count_x + 1

                    crop_start_pos_x = btm_cur_pos_x + (column_index - 1) * (interval_x + width)
                    crop_start_pos_y = btm_cur_pos_y + (row_index - 1) * (interval_y + heigt)
                    crop_end_pos_x = crop_start_pos_x + width
                    crop_end_pos_y = crop_start_pos_y + heigt

                    middle_x = crop_start_pos_x + width // 2
                    middle_y = crop_start_pos_y + heigt // 2

                    # monitor_print(f"-------------xxx: {btm_total_count},{need_top_page_bottom_pos}, {(crop_start_pos_x, crop_start_pos_y)}")

                    result_img = crop_pos_image_from_snapshot(snap_bottom_file_name,
                                                              f"adc_record_swipe_cropped_bottom_image_{combine_part_name}_{count}_{i}.jpg",
                                                              (crop_start_pos_x, crop_start_pos_y),
                                                              (crop_end_pos_x, crop_end_pos_y), False)
                    if check_normal_image_func is not None:
                        if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),
                                                   (crop_end_pos_x, crop_end_pos_y), snap_file_image):
                            crop_imgs.append(result_img)
                        else:
                            if check_normal_image_continue == False:
                                return crop_imgs
                    else:
                        if process_func is not None:
                            if process_func(result_img, (crop_start_pos_x, crop_start_pos_y),
                                            (crop_end_pos_x, crop_end_pos_y),
                                            (count, row_index, column_index, 'bottom'),
                                            snap_file_image):
                                crop_imgs.append(result_img)
                            else:
                                if process_func_continue == False:
                                    return crop_imgs
                        else:
                            crop_imgs.append(result_img)
            break
        elif bottomType > 0:
            monitor_print(f"-------------swipe_bottomType: {bottomType}")
            btm_index = bottomType -1
            btm_cur_pos = bottom_pos_list[btm_index]
            btm_cur_pos_x, btm_cur_pos_y = btm_cur_pos

            btm_row_count = (count_y if not visual_count_y else visual_count_y) - btm_index
            btm_total_count = count_x * btm_row_count # 这里需要增加策略来确定最后一行有多少个对象

            snap_bottom_file_name = f"adc_record_swipe_final_crop_bottom_snapshot_{combine_part_name}_{count}.jpg"
            lx_safe_snapshot(filename=snap_bottom_file_name, msg="Please fill in the test point.")
            snap_file_path = os.path.join(ST.LOG_DIR, snap_bottom_file_name)
            snap_file_image = cv2.imread(snap_file_path)

            for i in range(btm_total_count):
                row_index = i//count_x+1
                column_index = i%count_x+1
                
                crop_start_pos_x = btm_cur_pos_x + (column_index-1) * (interval_x+width)
                crop_start_pos_y = btm_cur_pos_y + (row_index-1) * (interval_y+heigt)
                crop_end_pos_x = crop_start_pos_x + width
                crop_end_pos_y = crop_start_pos_y + heigt
                
                middle_x = crop_start_pos_x + width//2
                middle_y = crop_start_pos_y + heigt//2

                result_img = crop_pos_image_from_snapshot(snap_bottom_file_name, f"adc_record_swipe_cropped_bottom_image_{combine_part_name}_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), False)
                if check_normal_image_func is not None:
                    if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y),snap_file_image):
                        crop_imgs.append(result_img)
                    else:
                        if check_normal_image_continue == False:
                            return crop_imgs
                else:
                    if process_func is not None:
                        if process_func(result_img, (crop_start_pos_x, crop_start_pos_y),
                                        (crop_end_pos_x, crop_end_pos_y), (count, row_index, column_index, 'bottom'), snap_file_image):
                            crop_imgs.append(result_img)
                        else:
                            if process_func_continue == False:
                                return crop_imgs
                    else:
                        crop_imgs.append(result_img)

                    # crop_imgs.append(result_img)
                # crop_imgs.append(result_img)
            # 退出while循环   
            break
        
    return crop_imgs

# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 适用于多行中多对象截图 - 带判底的
# check_bottom_start, check_bottom_end  用于确定底部的截图坐标
# crop_data 每个单独截图的对象的信息，包括：x坐标，y坐标，宽，高，间隔x，间隔y，横向的数量，纵向滑动的数量
# bottom_origin_pos 滑动到底部后的可能的第一行的x,y坐标（底部可能的第一行指：底部的纵向滑动数量的倒数行）
# combine_part_name  用于区分不同组截图的名称
# check_normal_image_func  用于判断截图是否正常,入参是img对象，返回值是bool值
# seperate_count  用于确定需要几次完成一个纵向滑动的数量
def swipe_crop_individual(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, max_swipe_count=None,bottom_confidence=None):
    model = CropIndividualModel(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func, seperate_count, max_swipe_count,bottom_confidence)

    return swipe_crop_individual_by_model(model)


class CropIndividualWithCountModel:
    def __init__(self,swipe_start_pos, swipe_end_pos, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, swipe_count=0, swipe_count_remainder=None, check_normal_image_continue=False):
        self.swipe_start_pos = swipe_start_pos
        self.swipe_end_pos = swipe_end_pos
        self.crop_data = crop_data
        self.bottom_origin_pos = bottom_origin_pos
        self.combine_part_name = combine_part_name
        self.check_normal_image_func = check_normal_image_func
        self.check_normal_image_continue = check_normal_image_continue
        self.seperate_count = seperate_count
        self.swipe_count = swipe_count
        self.swipe_count_remainder = swipe_count_remainder

# 适用于多行截图 - 不带判底的多行!!!只根据swipe_count决定滑动次数
def swipe_crop_individual_with_count_by_model(model):
    swipe_start_pos = model.swipe_start_pos
    swipe_end_pos = model.swipe_end_pos
    crop_data = model.crop_data
    bottom_origin_pos = model.bottom_origin_pos
    combine_part_name = model.combine_part_name
    check_normal_image_func = model.check_normal_image_func
    seperate_count = model.seperate_count
    swipe_count = model.swipe_count
    swipe_count_remainder = model.swipe_count_remainder
    check_normal_image_continue = model.check_normal_image_continue

    origin_x,origin_y,  width,heigt,  interval_x,interval_y, count_x,count_y = crop_data

    bottom_origin_x, bottom_origin_y = bottom_origin_pos

    bottom_pos_list = []
    for index in range(count_y):
        bottom_y = bottom_origin_y + index * (interval_y+heigt)
        bottom_pos_list.append((origin_x, bottom_y))

    bottomType = 0
    count=0
    crop_imgs = []

    android = AppEnv.get_instance().device

    while bottomType == 0: 
        count=count+1
        monitor_print(f"----------swipe_crop_individual_with_count  current count:{count}")

        snap_file_name = f"adc_record_swipe_final_crop_snapshot_{combine_part_name}_{count}.jpg"
        lx_safe_snapshot(filename=snap_file_name, msg="Please fill in the test point.")
        snap_file_name_path = os.path.join(ST.LOG_DIR, snap_file_name)
        snap_file_image = cv2.imread(snap_file_name_path)

        for i in range(count_x * count_y):
            row_index = i//count_x+1
            column_index = i%count_x+1
            
            crop_start_pos_x = origin_x + (column_index-1) * (interval_x+width)
            crop_start_pos_y = origin_y + (row_index-1) * (interval_y+heigt)
            crop_end_pos_x = crop_start_pos_x + width
            crop_end_pos_y = crop_start_pos_y + heigt

            middle_x = crop_start_pos_x + width//2
            middle_y = crop_start_pos_y + heigt//2 
            
            result_img = crop_pos_image_from_snapshot(snap_file_name, f"adc_record_swipe_cropped_image_{combine_part_name}_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), False)
            if check_normal_image_func is not None:
                if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), snap_file_image):
                    crop_imgs.append(result_img)
                else:
                    if check_normal_image_continue == False:
                        return crop_imgs
            else:
                crop_imgs.append(result_img)

        if swipe_count <= 0:
            bottomType = -1
        else:
            swipe_with_seperate(swipe_start_pos, swipe_end_pos, seperate_count)
            if count == swipe_count:
                if swipe_count_remainder is not None and swipe_count_remainder > 0:
                    remainder_row_count = swipe_count_remainder//count_x
                    if swipe_count_remainder%count_x > 0:
                        remainder_row_count = remainder_row_count + 1

                    bottomType = (count_y - remainder_row_count)+1
                else:
                    bottomType = 0
            elif count == swipe_count + 1:
                break

        if bottomType == 0:
            continue
        elif bottomType == -1:
            break
        elif bottomType > 0:
            # 解决底部回弹问题
            sleep(2)

            btm_index = bottomType -1
            btm_cur_pos = bottom_pos_list[btm_index]
            btm_cur_pos_x, btm_cur_pos_y = btm_cur_pos

            btm_row_count = count_y - btm_index
            btm_total_count = count_x * btm_row_count # 这里需要增加策略来确定最后一行有多少个对象

            snap_bottom_file_name = f"adc_record_swipe_final_crop_bottom_snapshot_{combine_part_name}_{count}.jpg"
            lx_safe_snapshot(filename=snap_bottom_file_name, msg="Please fill in the test point.")
            snap_file_name_path = os.path.join(ST.LOG_DIR, snap_bottom_file_name)
            snap_file_image = cv2.imread(snap_file_name_path)

            for i in range(btm_total_count):
                row_index = i//count_x+1
                column_index = i%count_x+1
                
                crop_start_pos_x = btm_cur_pos_x + (column_index-1) * (interval_x+width)
                crop_start_pos_y = btm_cur_pos_y + (row_index-1) * (interval_y+heigt)
                crop_end_pos_x = crop_start_pos_x + width
                crop_end_pos_y = crop_start_pos_y + heigt

                middle_x = crop_start_pos_x + width//2
                middle_y = crop_start_pos_y + heigt//2
                
                result_img = crop_pos_image_from_snapshot(snap_bottom_file_name, f"adc_record_swipe_cropped_bottom_image_{combine_part_name}_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), False)
                if check_normal_image_func is not None:
                    if check_normal_image_func(result_img, (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), snap_file_image):
                        crop_imgs.append(result_img)
                    else:
                        if check_normal_image_continue == False:
                            return crop_imgs
                else:
                    crop_imgs.append(result_img)
                # crop_imgs.append(result_img)
            # 退出while循环   
            break
        
    return crop_imgs

# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 适用于多行截图 - 不带判底的多行!!!只根据swipe_count决定滑动次数
def swipe_crop_individual_with_count(swipe_start_pos, swipe_end_pos, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func=None, seperate_count=None, swipe_count=0, swipe_count_remainder=None):
    model = CropIndividualWithCountModel(swipe_start_pos, swipe_end_pos, crop_data, bottom_origin_pos, combine_part_name, check_normal_image_func, seperate_count, swipe_count, swipe_count_remainder)

    return swipe_crop_individual_with_count_by_model(model)


class ProcessIndividualModel:
    def __init__(self,swipe_start_pos, swipe_end_pos,check_bottom_start, check_bottom_end, individual_data, bottom_origin_pos, process_func=None,  seperate_count=None, max_swipe_count=None,bottom_confidence=None):
        self.swipe_start_pos = swipe_start_pos
        self.swipe_end_pos = swipe_end_pos
        self.check_bottom_start = check_bottom_start
        self.check_bottom_end = check_bottom_end
        self.individual_data = individual_data
        self.bottom_origin_pos = bottom_origin_pos
        self.process_func = process_func
        self.seperate_count = seperate_count
        self.max_swipe_count = max_swipe_count
        self.bottom_confidence = bottom_confidence

# 适用于多行中多对象自定义处理 - 带判底的
def swipe_then_process_individual_by_model(model):
    swipe_start_pos = model.swipe_start_pos 
    swipe_end_pos = model.swipe_end_pos
    check_bottom_start = model.check_bottom_start
    check_bottom_end = model.check_bottom_end
    individual_data = model.individual_data
    bottom_origin_pos = model.bottom_origin_pos
    process_func = model.process_func
    seperate_count = model.seperate_count
    max_swipe_count = model.max_swipe_count
    bottom_confidence = model.bottom_confidence

    origin_x,origin_y,  width,heigt,  interval_x,interval_y, count_x,count_y = individual_data

    bottom_origin_x, bottom_origin_y = bottom_origin_pos


    # swipe_start_pos_y = origin_y + (interval_y+heigt) * count_y
    # swipe_end_pos_y = origin_y
    # swipe_start_pox_x = origin_x + width//2

    # swipe_start_pos = (swipe_start_pox_x,swipe_start_pos_y)
    # swipe_end_pos = (swipe_start_pox_x, swipe_end_pos_y)

    bottom_pos_list = []
    for index in range(count_y):
        bottom_y = bottom_origin_y + index * (interval_y+heigt)
        bottom_pos_list.append((origin_x, bottom_y))

    bottomType = 0
    count=0
    process_results = []

    process_func_count = 0

    android = AppEnv.get_instance().device

    while bottomType == 0: 
        count=count+1
        monitor_print(f"----------while {count} start")

        for i in range(count_x * count_y):
            row_index = i//count_x+1
            column_index = i%count_x+1
            
            crop_start_pos_x = origin_x + (column_index-1) * (interval_x+width)
            crop_start_pos_y = origin_y + (row_index-1) * (interval_y+heigt)
            crop_end_pos_x = crop_start_pos_x + width
            crop_end_pos_y = crop_start_pos_y + heigt
            
            result_img = crop_pos_image_from_snapshot(f"cropped_individual_snap_image_{count}_{i}.jpg", f"cropped_individual_image_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))
            
            process_row_index = process_func_count//count_x + 1
            process_column_index = process_func_count%count_x + 1
            process_status = process_func(process_results,(crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y),(process_row_index, process_column_index))
            if process_status == False:
                monitor_print(f"----------while {count} process_status False")
                return process_results
            else:
                process_func_count = process_func_count + 1

        monitor_print(f"----------while {count} crop finish")

        if max_swipe_count is not None:
            if count >= max_swipe_count:
                monitor_print(f"-------------max_swipe_count break")
                break

        
        monitor_print(f"----------while {count} swipe_with_bottom")
        if count == 1:
            crop_top_start_pos_x = origin_x 
            crop_top_start_pos_y = origin_y
            crop_top_end_pos_x = crop_top_start_pos_x + width * count_x + interval_x * (count_x-1)
            crop_top_end_pos_y = crop_top_start_pos_y + heigt 
            bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,(origin_x, origin_y), bottom_pos_list,  seperate_count, check_top_area = (crop_top_start_pos_x, crop_top_start_pos_y, crop_top_end_pos_x,crop_top_end_pos_y),bottom_confidence=bottom_confidence)
        else:
            bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,(origin_x, origin_y), bottom_pos_list,  seperate_count,bottom_confidence=bottom_confidence)
        
        monitor_print(f"-------------while{count} ,swipe finish bottomType: {bottomType}")

        if bottomType == 0:
            continue
        elif bottomType == -1:
            break
        elif bottomType > 0:
            btm_index = bottomType -1
            btm_cur_pos = bottom_pos_list[btm_index]
            btm_cur_pos_x, btm_cur_pos_y = btm_cur_pos

            btm_row_count = count_y - btm_index
            btm_total_count = count_x * btm_row_count # 这里需要增加策略来确定最后一行有多少个对象

            for i in range(btm_total_count):
                row_index = i//count_x+1
                column_index = i%count_x+1
                
                crop_start_pos_x = btm_cur_pos_x + (column_index-1) * (interval_x+width)
                crop_start_pos_y = btm_cur_pos_y + (row_index-1) * (interval_y+heigt)
                crop_end_pos_x = crop_start_pos_x + width
                crop_end_pos_y = crop_start_pos_y + heigt
                
                result_img = crop_pos_image_from_snapshot(f"cropped_individual_snap_btm_image_{count}_{i}.jpg", f"cropped_individual_btm_image_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))


                process_row_index = process_func_count//count_x + 1
                process_column_index = process_func_count%count_x + 1
                process_status = process_func(process_results,(crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y),(process_row_index, process_column_index))
                if process_status == False:
                    return process_results
                else:
                    process_func_count = process_func_count + 1
            # 退出while循环   
            break
        
    return process_results

# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 适用于多行中多对象自定义处理 - 带判底的
def swipe_then_process_individual(swipe_start_pos, swipe_end_pos,check_bottom_start, check_bottom_end, individual_data, bottom_origin_pos, process_func=None,  seperate_count=None, max_swipe_count=None,bottom_confidence=None):
    model = ProcessIndividualModel(swipe_start_pos, swipe_end_pos,check_bottom_start, check_bottom_end, individual_data, bottom_origin_pos, process_func,  seperate_count, max_swipe_count,bottom_confidence)

    return swipe_then_process_individual_by_model(model)


class ProcessIndividualWithCountModel:
    def __init__(self,swipe_start_pos, swipe_end_pos, individual_data, bottom_origin_pos, process_func=None,  seperate_count=None, swipe_count=0,swipe_count_remainder = None):
        self.swipe_start_pos = swipe_start_pos
        self.swipe_end_pos = swipe_end_pos
        self.individual_data = individual_data
        self.bottom_origin_pos = bottom_origin_pos
        self.process_func = process_func
        self.seperate_count = seperate_count
        self.swipe_count = swipe_count
        self.swipe_count_remainder = swipe_count_remainder


# 适用于多行中多对象自定义处理 - 不带判底的，只根据swipe_count决定滑动次数
# 注意：如果是存在拥有和未拥有的情况，也就是不存在真正的底的情况，则不要传递swipe_count_remainder，靠process_func来结束
# 对于只有拥有的情况的底，需要传递swipe_count_remainder
def swipe_then_process_individual_with_count_by_model(model):
    swipe_start_pos = model.swipe_start_pos 
    swipe_end_pos = model.swipe_end_pos
    individual_data = model.individual_data
    bottom_origin_pos = model.bottom_origin_pos
    process_func = model.process_func
    seperate_count = model.seperate_count
    swipe_count = model.swipe_count
    swipe_count_remainder = model.swipe_count_remainder

    origin_x,origin_y,  width,heigt,  interval_x,interval_y, count_x,count_y = individual_data

    bottom_origin_x, bottom_origin_y = bottom_origin_pos


    # swipe_start_pos_y = origin_y + (interval_y+heigt) * count_y
    # swipe_end_pos_y = origin_y
    # swipe_start_pox_x = origin_x + width//2

    # swipe_start_pos = (swipe_start_pox_x,swipe_start_pos_y)
    # swipe_end_pos = (swipe_start_pox_x, swipe_end_pos_y)

    bottom_pos_list = []
    for index in range(count_y):
        bottom_y = bottom_origin_y + index * (interval_y+heigt)
        bottom_pos_list.append((origin_x, bottom_y))

    bottomType = 0
    count=0
    process_results = []

    process_func_count = 0

    android = AppEnv.get_instance().device

    while bottomType == 0: 
        count=count+1
        monitor_print(f"----------while {count} start")

        for i in range(count_x * count_y):
            row_index = i//count_x+1
            column_index = i%count_x+1
            
            crop_start_pos_x = origin_x + (column_index-1) * (interval_x+width)
            crop_start_pos_y = origin_y + (row_index-1) * (interval_y+heigt)
            crop_end_pos_x = crop_start_pos_x + width
            crop_end_pos_y = crop_start_pos_y + heigt
            
            result_img = crop_pos_image_from_snapshot(f"cropped_individual_snap_image_{count}_{i}.jpg", f"cropped_individual_image_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))
            
            process_row_index = process_func_count//count_x + 1
            process_column_index = process_func_count%count_x + 1
            process_status = process_func(process_results,(crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y),(process_row_index, process_column_index, count_x, count_y))
            if process_status == False:
                monitor_print(f"----------while {count} process_status False")
                return process_results
            else:
                process_func_count = process_func_count + 1

        monitor_print(f"----------while {count} crop finish")

        if swipe_count <= 0:
            bottomType = -1
        else:
            swipe_with_seperate(swipe_start_pos, swipe_end_pos, seperate_count)
            if count == swipe_count:
                if swipe_count_remainder is not None and swipe_count_remainder > 0:
                    remainder_row_count = swipe_count_remainder//count_x
                    if swipe_count_remainder%count_x > 0:
                        remainder_row_count = remainder_row_count + 1
                        
                    bottomType = (count_y - remainder_row_count)+1
                    # bottomType = (count_y - swipe_count_remainder)+1
                else:
                    bottomType = 0
            elif count == swipe_count + 1:
                break

        monitor_print(f"-------------while{count} ,swipe finish bottomType: {bottomType}")

        if bottomType == 0:
            continue
        elif bottomType == -1:
            break
        elif bottomType > 0:
            # 解决底部回弹问题
            sleep(2)

            btm_index = bottomType -1
            btm_cur_pos = bottom_pos_list[btm_index]
            btm_cur_pos_x, btm_cur_pos_y = btm_cur_pos

            btm_row_count = count_y - btm_index
            btm_total_count = count_x * btm_row_count # 这里需要增加策略来确定最后一行有多少个对象

            for i in range(btm_total_count):
                row_index = i//count_x+1
                column_index = i%count_x+1
                
                crop_start_pos_x = btm_cur_pos_x + (column_index-1) * (interval_x+width)
                crop_start_pos_y = btm_cur_pos_y + (row_index-1) * (interval_y+heigt)
                crop_end_pos_x = crop_start_pos_x + width
                crop_end_pos_y = crop_start_pos_y + heigt
                
                result_img = crop_pos_image_from_snapshot(f"cropped_individual_snap_btm_image_{count}_{i}.jpg", f"cropped_individual_btm_image_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y))


                process_row_index = process_func_count//count_x + 1
                process_column_index = process_func_count%count_x + 1
                process_status = process_func(process_results,(crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y),(process_row_index, process_column_index, count_x, count_y))
                if process_status == False:
                    return process_results
                else:
                    process_func_count = process_func_count + 1
            # 退出while循环   
            break
        
    return process_results


# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 注意：请使用带by_model的方法
# 适用于多行中多对象自定义处理 - 不带判底的，只根据swipe_count决定滑动次数
# 注意：如果是存在拥有和未拥有的情况，也就是不存在真正的底的情况，则不要传递swipe_count_remainder，靠process_func来结束
# 对于只有拥有的情况的底，需要传递swipe_count_remainder
def swipe_then_process_individual_with_count(swipe_start_pos, swipe_end_pos, individual_data, bottom_origin_pos, process_func=None,  seperate_count=None, swipe_count=0,swipe_count_remainder = None):
    model = ProcessIndividualWithCountModel(swipe_start_pos, swipe_end_pos, individual_data, bottom_origin_pos, process_func,  seperate_count, swipe_count,swipe_count_remainder)

    return swipe_then_process_individual_with_count_by_model(model)


# 通用的判断底部策略
# 返回值0表示未滑动到底部
# 大于0表示滑动到底部，并且返回的int值表示是滑动前的截图在底部的那行位置
# 返回-1标识第一页就是底部
# check_top_area 只在第一次滑动的时候传入该参数，其他时候不需要
def swipe_with_bottom(startPos, endPos, check_bottom_start, check_bottom_end, expect_pos, bottom_pos_list=None, seperate_count=None, check_top_area=None, bottom_tolerance=None, bottom_confidence=None, swipe_duration=0.5, top_tolerance=None,combine_part_name=''):
    temp_per = int(time.time()*1000000)
    # start_pos_x,start_pos_y = startPos
    # _,end_pos_y = endPos
    # half_height = (start_pos_y - end_pos_y)//2
    # monitor_print(f"----------half_height: {startPos},{(start_pos_x, start_pos_y-half_height-100)}")

    isBottomType = 0
    android = AppEnv.get_instance().device

    global swipe_adc_catch

    # 滑动前
    snap_file_name = f"adc_record_swipe_with_bottom_{combine_part_name}_swipe_before_snapshot_007_{str(int(time.time()*1000000))}.jpg"
    if swipe_adc_catch:
        snap_file_name = f"adc_catch_swipe_with_bottom_{combine_part_name}_swipe_before_snapshot_007_{str(int(time.time() * 1000000))}.jpg"
    lx_safe_snapshot(filename=snap_file_name, msg="Please fill in the test point.")
    snap_before_path = os.path.join(ST.LOG_DIR, snap_file_name)

    upload_oss_count_1 = []

    if check_top_area:
        check_top_start_x,check_top_start_y, check_top_end_x,check_top_end_y =check_top_area 
        check_top_start = (check_top_start_x,check_top_start_y)
        check_top_end = (check_top_end_x,check_top_end_y)
        before_top_img =  crop_pos_image_from_snapshot(snap_file_name, f"is_top_crop_007.jpg", check_top_start,check_top_end, need_snapshot=False)
        top_path = os.path.join(ST.LOG_DIR, 'is_top_crop_007.jpg')
        cv2.imwrite(top_path, before_top_img)

        upload_oss_count_1.append(top_path)


    bottom_crop_image_name = f"adc_record_swipe_with_bottom_{combine_part_name}_is_bottom_crop_007_{str(int(time.time()*1000000))}.jpg"
    if swipe_adc_catch:
        bottom_crop_image_name = f"adc_catch_swipe_with_bottom_{combine_part_name}_is_bottom_crop_007_{str(int(time.time() * 1000000))}.jpg"
    before_img =  crop_pos_image_from_snapshot(snap_file_name, bottom_crop_image_name, check_bottom_start,check_bottom_end)
    wirte_path = os.path.join(ST.LOG_DIR, bottom_crop_image_name)
    cv2.imwrite(wirte_path, before_img)
    
    # performance_start_timestamp = int(time.time()*1000000)
    start_pos_x,start_pos_y = startPos
    end_pos_x, end_pos_y = endPos
    new_pos_y = end_pos_y 
    
    if seperate_count is not None:
        # swipe_step_height = (start_pos_y - new_pos_y)//seperate_count
        for i in range(seperate_count):
            # if i == seperate_count -1:
            #     new_end_pos = (end_pos_x,start_pos_y-(start_pos_y - new_pos_y-i*swipe_step_height))
            # else:
            #     new_end_pos = (end_pos_x, start_pos_y - swipe_step_height)
            lx_swipe(android, startPos, endPos, duration=swipe_duration)
            sleep(0.5)
    else:
        lx_swipe(android, startPos, endPos, duration=swipe_duration)
        sleep(0.5)
    # lx_swipe(android, startPos, (start_pos_x, start_pos_y-half_height-105))
    # sleep(1)
    # lx_swipe(android, startPos, (start_pos_x, start_pos_y-half_height-105))
    # lx_swipe(android, startPos, (start_pos_x, start_pos_y-half_height))
    # lx_swipe(android, (start_pos_x,start_pos_y-half_height), endPos)

    # performance_interval = int(time.time()*1000000) - performance_start_timestamp
    # monitor_task_status(AppEnv.get_instance(), "性能统计", f"lx_swipe_interval:{str(performance_interval)}")
    monitor_print(f"----------lxswipe: {startPos},{endPos}")
    # 滑动后
    sleep(AppEnv.get_instance().sleepTime)
    # performance_interval = int(time.time()*1000000) - performance_start_timestamp
    # monitor_task_status(AppEnv.get_instance(), "性能统计", f"sleep_interval:{str(performance_interval)}")

    toler = 10
    if bottom_tolerance is not None:
        toler = bottom_tolerance

    top_toler = 10
    if top_tolerance is not None:
        top_toler = top_tolerance
    else:
        top_toler = toler

    confidence = 0.75
    if bottom_confidence is not None:
        confidence = bottom_confidence

    global swipe_bottom_retry

    # 这里的重试是针对一些随机的屏幕中漂浮的情况的适配
    pos = None
    for i in range(swipe_bottom_retry):
        pos = None

        snap_file_name = f"adc_record_swipe_with_bottom_{combine_part_name}_swipe_after_snapshot_007_{str(int(time.time() * 1000000))}.jpg"
        if swipe_adc_catch:
            snap_file_name = f"adc_catch_swipe_with_bottom_{combine_part_name}_swipe_after_snapshot_007_{str(int(time.time() * 1000000))}.jpg"
        lx_safe_snapshot(filename=snap_file_name, msg="Please fill in the test point.")
        snap_after_path = os.path.join(ST.LOG_DIR, snap_file_name)

        if check_top_area:
            top_path=ST.LOG_DIR + '/is_top_crop_007.jpg'

            top_pos = lx_exists_with_file(Template(filename=f"{top_path}", target_pos=1, record_pos=(0.276, 0.254), resolution=get_system_portrait_resolution()), snap_after_path,threshold=confidence)
            monitor_print(f"--------swip_with_bottom_top_pos: {top_pos}, expect_pos {expect_pos},top_path {top_path}, {snap_after_path}, toler:{top_toler}")

            env = AppEnv.get_instance()
            launchType = env.launchType
            if (launchType != 'localtest'):
                upload_oss_count_1.append(snap_before_path)
                upload_oss_count_1.append(snap_after_path)
                upload_info = upload_jym_oss_with_pathes(upload_oss_count_1)
                oss_pathes, cdn_urls = upload_info
                monitor_task_status(AppEnv.get_instance(),  '第一页的判底图片信息', f"{cdn_urls}")


            if top_pos and expect_pos:
                pos_x, pos_y = top_pos
                except_x, except_y = expect_pos
                if abs(pos_y - except_y) < top_toler and abs(pos_x - except_x) < 10:
                    isBottomType = -1
                    monitor_print(f"--------swip_with_bottom_top_1: {isBottomType}")
                    return isBottomType

        path=os.path.join(ST.LOG_DIR, bottom_crop_image_name)
        monitor_print(f"--------swipe_after_pos_list: {bottom_pos_list}")

        pos = lx_exists_with_file(Template(filename=f"{path}", target_pos=1, record_pos=(0.276, 0.254), resolution=get_system_portrait_resolution()),snap_after_path,threshold=confidence)
        if pos == False:
            monitor_print(f"--------swip_with_bottom_pos_is_False, {snap_after_path}")
            sleep(2)
            continue
        else:
            monitor_print(f"--------swipe_after_exists_pos: {pos},{expect_pos}")
            break
        # performance_interval = int(time.time()*1000000) - performance_start_timestamp
        # monitor_task_status(AppEnv.get_instance(), "性能统计", f"exists_interval:{str(performance_interval)}")
    
    if bottom_pos_list is not None:
        if pos and expect_pos:
            _, pos_y = pos
            _, except_y = expect_pos
            if abs(pos_y - except_y) < toler:
                isBottomType = 0
            else:
                offset_arr = []
                for index, item in enumerate(bottom_pos_list):
                    _, bottom_pos_y = item
                    offset_arr.append(abs(pos_y - bottom_pos_y))
                    # if abs(pos_y - bottom_pos_y) < toler:
                    #     isBottomType = index+1
                    #     break
                min_index = offset_arr.index(min(offset_arr))
                isBottomType = min_index + 1
                monitor_print(f"--------swipe_after_bottom_pos_y_except_y: {abs(pos_y - except_y)}, toler:{toler}, bottomType:{isBottomType}")
        else:
            # # 这种情况是滑动出现了问题，需要抛出异常
            monitor_print(f"----------未找到check滑动底部的位置，默认按照底部1的情况处理, bottom_pos_list is no None")
            isBottomType = 1
    else:
        # isBottom = is_bottom_by_pos(path, expect_pos)

        if pos and expect_pos:
            _, pos_y = pos
            _, except_y = expect_pos
            if abs(pos_y - except_y) < toler:
                isBottomType = 0
            else:
                isBottomType = 1
        else:
            # # 这种情况是滑动出现了问题，需要抛出异常
            monitor_print(f"----------未找到check滑动底部的位置，默认按照底部1的情况处理, bottom_pos_list is None")
            isBottomType = 1

    temp_per = int(time.time()*1000000) - temp_per
    # monitor_task_status(AppEnv.get_instance(), "性能统计", f"swipe_with_bottom:{str(temp_per)}")
    return isBottomType


# ================== 特殊的纵向判断底部逻辑，用于三国杀，其他游戏不要使用 ==========================

#全屏----[两行]（武将、皮肤等场景）-------滑动，用最下一行判断  
#[仅支持 - 两行元素]！！！！！！
#[仅支持 - 两行元素]！
#返回 0表示上次的判断行不存在，即不是底部
#返回 1底部，上次的‘底部行’存在为上部
#返回 2底部，上次的‘底部行’存在为下部
def swipe_full_screen_with_bottom(startPos, endPos, check_bottom_start, check_bottom_end, expect_pos):
    bottomTag = 0
    android = AppEnv.get_instance().device
    swipe_full_screen_before(check_bottom_start, check_bottom_end)
    lx_swipe(android, startPos, endPos)
    monitor_print(f"----------lx swipe_full_screen: {startPos},{endPos}")
    bottomTag = swipe_full_screen_after(check_bottom_start, check_bottom_end, expect_pos)
    return bottomTag

def swipe_full_screen_before(check_bottom_start, check_bottom_end, count=None):
    # lx_safe_snapshot(filename=f"03-before.jpg", msg="Please fill in the test point.") 

    lx_safe_snapshot(filename=f"full_screen_bottom_snapshot_007.jpg", msg="Please fill in the test point.")
    crop_pos_image_from_snapshot(f"full_screen_bottom_snapshot_007.jpg", f"full_screen_bottom_crop_007.jpg", check_bottom_start,check_bottom_end)

def swipe_full_screen_after(check_bottom_start,check_bottom_end,crop_start, count=None):
    sleep(AppEnv.get_instance().sleepTime)

    path=ST.LOG_DIR + '/full_screen_bottom_crop_007.jpg'

    bottomType = 0
    bottomType = is_full_screen_bottom_more_per(path, crop_start)
       
    return bottomType

def is_full_screen_bottom_more_per(d_file_name, expect_pos):   
    # pos = exists(Template(filename=f"{d_file_name}", target_pos=1, record_pos=(0.276, 0.254), resolution=(2400, 1350)))

    timestamp_ms = time.time() * 1000
    monitor_print("当前时间戳（毫秒-0）：", timestamp_ms)
    lx_safe_snapshot(filename=f"full_screen_bottom_snapshot_008.jpg", msg="Please fill in the test point.")
    path=ST.LOG_DIR + '/full_screen_bottom_snapshot_008.jpg'
    tempalte = Template(filename=f"{d_file_name}", target_pos=1, record_pos=(0.276, 0.254), resolution=get_system_portrait_resolution())
    img_cv = cv2.imread(path)
    pos = tempalte.match_in(img_cv)

    timestamp_ms = time.time() * 1000 -timestamp_ms
    monitor_print("当前时间戳（毫秒-1）：", timestamp_ms)

    pos = exists(Template(filename=f"{d_file_name}", target_pos=1, record_pos=(0.276, 0.254), resolution=get_system_portrait_resolution()))
    monitor_print(f"------is_full_screen_bottom_more_per:{pos},{expect_pos}")
    if pos and expect_pos:
        _, pos_y = pos
        _, except_y = expect_pos
        if pos_y < except_y:
            return 1
        else:
            return 2
    else:
        return 0



###************************ 横向滑动 ************************

#横向滑动 - lx
def lx_horizontal_swipe(actionDevice, p1, p2, duration=0.6, steps=5):
    # actionDevice.touch_proxy.touch(p1)
    from_x, from_y = p1
    to_x, to_y = p2
    # if abs(from_x - to_x) > 1000:
    #     actionDevice.touch_proxy.swipe_along([(from_x, from_y), (from_x - (from_x - to_x)/2, to_y), (to_x+2, to_y), (to_x, to_y)], duration=0.8)
    # else :
    actionDevice.touch_proxy.swipe_along([(from_x, from_y), (to_x+2, to_y), (to_x, to_y)], duration)

###注意注意!!!!  返回的index 从【1】开始 ，取值注意不是从0开始
###注意注意!!!!  返回的index 从【1】开始
###注意注意!!!!  返回的index 从【1】开始

#全屏两行（武将、皮肤等场景）滑动，用最下一行判断   
#返回 0表示上次的判断行不存在，即不是底部
#返回 index 返回在第几个坐标
#expect_pos_list
def swipe_horizontal_with_bottom(target_swipe_list, check_bottom_start, check_bottom_end, expect_pos_list):
    bottomTag = 0
    android = AppEnv.get_instance().device
    swipe_horizontal_before(check_bottom_start, check_bottom_end)
    for index, item in enumerate(target_swipe_list):
        lx_horizontal_swipe(android, item[0], item[1])
        if index > 0:
            #尽量不要连续多次滑动 耗时较长
            sleep(0.15)
    monitor_print(f"----------lx swipe_full_screen: {target_swipe_list}")
    bottomTag = swipe_horizontal_after(check_bottom_start, check_bottom_end, expect_pos_list)
    return bottomTag

def swipe_horizontal_before(check_bottom_start, check_bottom_end, count=None):
    # lx_safe_snapshot(filename=f"03-before.jpg", msg="Please fill in the test point.") 

    lx_safe_snapshot(filename=f"full_screen_bottom_snapshot_007.jpg", msg="Please fill in the test point.")
    crop_pos_image_from_snapshot(f"full_screen_bottom_snapshot_007.jpg", f"full_screen_bottom_crop_007.jpg", check_bottom_start,check_bottom_end)

def swipe_horizontal_after(check_bottom_start,check_bottom_end, expect_pos_list, count=None):
    sleep(AppEnv.get_instance().sleepTime)

    path=ST.LOG_DIR + '/full_screen_bottom_crop_007.jpg'

    bottomType = 0
    bottomType = is_horizontal_bottom_more_per(path, expect_pos_list)
       
    return bottomType
###!!!!  c返回的index 从1开始
def is_horizontal_bottom_more_per(d_file_name, expect_pos_list):   
    timestamp_ms = time.time() * 1000
    monitor_print("当前时间戳（毫秒-0）：", timestamp_ms)

    pos = exists(Template(filename=f"{d_file_name}", target_pos=1, record_pos=(0.276, 0.254), resolution=get_system_portrait_resolution()))
    timestamp_ms = time.time() * 1000 -timestamp_ms
    monitor_print("当前时间戳（毫秒-1）：", timestamp_ms)

    # lx_safe_snapshot(filename=f"full_screen_bottom_snapshot_008.jpg", msg="Please fill in the test point.")
    # path=ST.LOG_DIR + '/full_screen_bottom_snapshot_008.jpg'
    # tempalte = Template(filename=f"{d_file_name}", target_pos=1, record_pos=(0.276, 0.254), resolution=(2400, 1350))
    # img_cv = cv2.imread(path)
    # pos = tempalte.match_in(img_cv)

    monitor_print(f"------is_full_screen_bottom_more_per:{pos}")
    if pos and expect_pos_list:
        pos_x, _ = pos
        matchIndex = 0
        for index, expect_pos in enumerate(expect_pos_list):
            except_x, _ = expect_pos
            if pos_x < except_x:
                matchIndex = index
                break
        return matchIndex+1
    else:
        return 0


class TouchCropIndividualModel:
    def __init__(self, swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end, expect_pos, touch_data, return_pos,
                 combine_part_name, check_normal_touch_func, crop_data=None, seperate_count=None,
                 max_swipe_count=None, bottom_tolerance=None, bottom_confidence=None, check_normal_touch_continue=False):
        """
        滑动点击进入详情页截图参数
        :param swipe_start_pos: 滑动起始坐标
        :param swipe_end_pos: 滑动终止坐标
        :param check_bottom_start: 用于判底区域的起始坐标
        :param check_bottom_end: 用于判底区域的终止坐标
        :param expect_pos: 底部区域预期滑动后左上角坐标
        :param touch_data: 点击坐标的数据 x坐标，y坐标，到底了的y坐标, 间隔x, 间隔y, 一排几个, 一页几排
        :param return_pos: 返回坐标
        :param combine_part_name: 文件名
        :param check_normal_touch_func: 检查点击是否正常
        :param crop_data: 详情页截图坐标 取值(x,y, x1,y1)或者None(截全屏)
        :param seperate_count: 滑动次数，默认1次
        :param max_swipe_count: 最大滑动次数， 默认滑到底
        :param bottom_tolerance: 判断底部坐标偏移容忍度 默认10
        :param bottom_confidence: 判断底识图的一个阈值 默认0.75
        :param check_normal_touch_continue: 检查点击不正常后是否继续 默认不继续了
        """
        self.swipe_start_pos = swipe_start_pos
        self.swipe_end_pos = swipe_end_pos
        self.check_bottom_start = check_bottom_start
        self.check_bottom_end = check_bottom_end
        self.expect_pos = expect_pos
        self.crop_data = crop_data
        self.touch_data = touch_data
        self.return_pos = return_pos
        self.combine_part_name = combine_part_name
        self.check_normal_touch_func = check_normal_touch_func
        self.check_normal_touch_continue = check_normal_touch_continue
        self.seperate_count = seperate_count
        self.max_swipe_count = max_swipe_count
        self.bottom_confidence = bottom_confidence
        self.bottom_tolerance = bottom_tolerance


def swipe_touch_crop_individual_by_model(model: TouchCropIndividualModel):
    """
    适用于滑动时候需要点击进入详情截图
    :param model: TouchCropIndividualModel
    :return:
    """
    swipe_start_pos = model.swipe_start_pos
    swipe_end_pos = model.swipe_end_pos
    check_bottom_start = model.check_bottom_start
    check_bottom_end = model.check_bottom_end
    expect_pos = model.expect_pos
    touch_data = model.touch_data
    return_pos = model.return_pos
    combine_part_name = model.combine_part_name
    check_normal_touch_func = model.check_normal_touch_func
    seperate_count = model.seperate_count
    max_swipe_count = model.max_swipe_count
    bottom_confidence = model.bottom_confidence
    check_normal_touch_continue = model.check_normal_touch_continue
    bottom_tolerance = model.bottom_tolerance

    # 点击坐标的数据 x坐标，y坐标，到底了的y坐标, 间隔x, 间隔y, 一排几个, 一页几排
    origin_x, origin_y, bottom_origin_y, interval_x, interval_y, count_x, count_y = touch_data
    bottom_origin_x = origin_x

    bottom_pos_list = []
    for index in range(count_y):
        bottom_y = bottom_origin_y + index * interval_y
        bottom_pos_list.append((origin_x, bottom_y))

    bottomType = 0
    count = 0
    crop_imgs = []
    while bottomType == 0:
        count = count + 1
        monitor_print(f"----------swipe_touch_crop_individual_by_model:{count}")
        for i in range(count_x * count_y):
            row_index = i // count_x + 1
            column_index = i % count_x + 1
            touch_pos_x = origin_x + (column_index - 1) * interval_x
            touch_pos_y = origin_y + (row_index - 1) * interval_y
            # 点击进入详情页
            lx_touch((touch_pos_x, touch_pos_y), 1)
            s_file_name = f"cropped_image_{combine_part_name}_{count}_{i}.jpg"
            lx_safe_snapshot(filename=s_file_name, msg="Please fill in the test point.")
            path = os.path.join(ST.LOG_DIR, s_file_name)
            result_img = cv2.imread(path)
            if check_normal_touch_func(result_img):
                crop_imgs.append(result_img)
                # 返回
                lx_touch(return_pos, 1)
            else:
                if not check_normal_touch_continue:
                    return crop_imgs
        if max_swipe_count is not None:
            if count >= max_swipe_count:
                monitor_print(f"-------------max_swipe_count break")
                break
        if count == 1:
            crop_top_start_pos_x = origin_x
            crop_top_start_pos_y = origin_y
            crop_top_end_pos_x = origin_x + interval_x * (count_x - 1)
            crop_top_end_pos_y = origin_y + interval_y
            bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,
                                           expect_pos, bottom_pos_list, seperate_count=seperate_count, check_top_area=(
                crop_top_start_pos_x, crop_top_start_pos_y, crop_top_end_pos_x, crop_top_end_pos_y),
                                           bottom_tolerance=bottom_tolerance, bottom_confidence=bottom_confidence)
        else:
            bottomType = swipe_with_bottom(swipe_start_pos, swipe_end_pos, check_bottom_start, check_bottom_end,
                                           expect_pos, bottom_pos_list, seperate_count=seperate_count,
                                           bottom_tolerance=bottom_tolerance, bottom_confidence=bottom_confidence)

        if bottomType == 0:
            continue
        elif bottomType == -1:
            monitor_print(f"-------------swipe_bottomType: {bottomType}")
            break
        elif bottomType > 0:
            monitor_print(f"-------------swipe_bottomType: {bottomType}")
            btm_total_count = count_x * count_y  # 这里需要增加策略来确定最后一行有多少个对象
            for i in range(btm_total_count):
                row_index = i // count_x + 1
                column_index = i % count_x + 1
                touch_pos_x = bottom_origin_x + (column_index - 1) * interval_x
                touch_pos_y = bottom_origin_y + (row_index - 1) * interval_y
                # 点击进入详情页
                lx_touch((touch_pos_x, touch_pos_y), 1)
                s_file_name = f"cropped_image_{combine_part_name}_{count}_{i}.jpg"
                lx_safe_snapshot(filename=s_file_name, msg="Please fill in the test point.")
                path = os.path.join(ST.LOG_DIR, s_file_name)
                result_img = cv2.imread(path)
                if check_normal_touch_func(result_img):
                    crop_imgs.append(result_img)
                    # 返回
                    lx_touch(return_pos, 1)
                else:
                    if not check_normal_touch_continue:
                        return crop_imgs
            # 退出while循环
            break
    return crop_imgs











