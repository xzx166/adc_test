
import difflib
import time
import traceback
from PIL import Image, ImageDraw, ImageFont,ImageStat
import numpy as np
import requests

import threading
import queue
from airtest.core.api import *
import cv2
from airtest import aircv
from utility.biz_utils.base_module import *
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont

png_file_name = 'adc_result'
catch_file_name = 'adc_catch'
tmp_file_name = 'tmp'
ENV = AppEnv.get_instance()

tool_kit_env = {
    'snapshot_mode': None
}

def tool_kit_set_env(**kwargs):
    for k, v in kwargs.items():
        tool_kit_env[k] = v
    monitor_print(f'---tool_kit_env: {tool_kit_env}')

def streamSnapshot(filename = None, msg = None, is_try = True):
    try:
        system = ENV.system_type
        if system == 'android':
            device = ENV.device
            data = device.screen_proxy.get_frame_from_stream()
            frame = aircv.utils.string_2_img(data)
            
            frame = resize_by_max(frame, 2400)
            now_displayinfo = get_now_displayinfo()
            if filename:
                monitor_print(f'---kit_streamSnapshot_orientation: {now_displayinfo} filename: {filename}')
            if tool_kit_env['snapshot_mode'] == 'auto':
                frame = cv2.resize(frame, now_displayinfo)
            if filename is not None:
                path = os.path.join(ST.LOG_DIR, filename)
                cv2.imwrite(path, frame)
        elif system == 'ios':
            if filename:
                frame = adc_snapshot(filename)
            else:
                frame = adc_snapshot()
        return frame
    except Exception as e:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit stream adc_snapshot error({ENV.gameDir}): {error_traceback}')
        if is_try:
            lx_break_app(desc='截图失败', hold_game=True,ext_info={'key':'10163'})
        return None
def resize_by_max(img, max_size=800):
    if img is None:
        return np.zeros((max_size, max_size, 3), dtype=np.uint8)
    max_len = max(img.shape[0], img.shape[1])
    if max_len > max_size:
        scale = max_size / max_len
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
    return img

def kit_wait(v, timeout=None, interval=0.5, intervalfunc=None, is_try = False):
    try:
        monitor_print(f'---kit_wait_finding: {v}')
        start_time = time.time()
        while True:
            screen = streamSnapshot()
            if screen is None:
                monitor_print(f'---kit_wait_error: Screen is None, may be locked')
                if timeout is None:
                    return None
            else:
                pos = v.match_in(screen)
                if pos:
                    monitor_print(f'---kit_wait_finding: {v} pos: {pos}')
                    return pos
                if timeout is None:
                    return None
                if (time.time() - start_time) > timeout:
                    return None
                else:
                    time.sleep(interval)
    except:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit_wait_exception: {error_traceback}')
        if is_try:
            return None

def kit_wait_find_plus(v_list, timeout=None, interval=0.5, threshold=0.7, area_pos = None, is_back_threshold = False):
    try:
        monitor_print(f'---kit_wait_find_plus: {v_list}')
        start_time = time.time()
        while True:
            screen = streamSnapshot()
            if screen is None:
                monitor_print(f'---kit_wait_find_plus_error: Screen is None, may be locked')
                if timeout is None:
                    return None
            else:
                q = queue.Queue()
                threads = []
                if area_pos is not None:
                    screen = screen[area_pos[1]:area_pos[3], area_pos[0]:area_pos[2]]
                for v in v_list:
                    file_path = v._filepath
                    filename = v.filename
                    file_np = cv2.imread(file_path)
                    t = threading.Thread(target=kit_match_in_thread, args=(file_np, q, screen, threshold, f'---kit_wait_find_plus: {v}', is_back_threshold, filename))
                    t.start()
                    threads.append(t)
                    # pos = kit_match_in(file_np, screen, threshold)
                    
                for t in threads:
                    t.join()

                match_back_result = []
                while not q.empty():
                    match_result = q.get()
                    if is_back_threshold:
                        if match_result is not None:
                            match_back_result.append(match_result)
                    else:
                        pos = match_result
                        if pos is not None:
                            break
                if is_back_threshold:
                    if match_back_result:
                        monitor_print(f'---kit_wait_find_plus: {v_list} match_back_result: {match_back_result}')
                        return match_back_result
                else:
                    if pos:
                        if area_pos is not None:
                            pos = (pos[0] + area_pos[0], pos[1] + area_pos[1])
                        try:
                            try_log_screen(screen)
                        except:
                            pass
                        monitor_print(f'---kit_wait_find_plus: {v_list} pos: {pos}')
                        return pos
                if timeout is None:
                    monitor_print(f'---kit_wait_find_plus: {v_list} pos: None')
                    return None
                if (time.time() - start_time) > timeout:
                    return None
                else:
                    time.sleep(interval)
    except:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit_wait_find_plus_exception: {error_traceback}')
        return None
    

def snapshotImg(name, type_name = tmp_file_name, mask = None, LT = None, RB = None, path=False, custom_suffix = ''):
    """
        截图
    """
    if custom_suffix:
        img_filename = f'{type_name}_{name}_{custom_suffix}.jpg'
    else:
        img_filename = f'{type_name}_{name}_{str(int(time.time() * 1000000))}.jpg'
    
    streamSnapshot(filename = img_filename, msg="get a adc_snapshot.")
    image_path = os.path.join(ST.LOG_DIR, img_filename)
    if mask is not None:
        for mask_one in mask:
            mask_image_range_tosave(image_path, mask_one[0], mask_one[1])
    image_np = cv2.imread(image_path)
    if LT is not None and RB is not None:
        image_np = image_np[LT[1]:RB[1], LT[0]:RB[0]]
        cv2.imwrite(image_path, image_np)
    if path:
        return image_path
    else:
        return image_np
    
def kit_wait_find(v, timeout=None, interval=0.5, threshold=0.7, area_pos = None):
    try:
        monitor_print(f'---kit_wait_finding: {v}')
        start_time = time.time()
        while True:
            screen = streamSnapshot()
            if screen is None:
                monitor_print(f'---kit_wait_error: Screen is None, may be locked')
                if timeout is None:
                    return None
            else:
                file_path = v._filepath
                file_np = cv2.imread(file_path)
                if area_pos is not None:
                    screen = screen[area_pos[1]:area_pos[3], area_pos[0]:area_pos[2]]
                pos = kit_match_in(file_np, screen, threshold, print_str = f'---kit_wait {v}')
                if pos:
                    if area_pos is not None:
                        pos = (pos[0] + area_pos[0], pos[1] + area_pos[1])
                    try:
                        try_log_screen(screen)
                    except:
                        pass
                    monitor_print(f'---kit_wait_finding: {v} pos: {pos}')
                    return pos
                if timeout is None:
                    return None
                if (time.time() - start_time) > timeout:
                    return None
                else:
                    time.sleep(interval)
    except:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit_wait_find_exception: {error_traceback}')
        return None
        
def kit_match_in(small_img_np, main_img_np = None, threshold=0.7, print_str = '', is_back_threshold = False, filename = None):
    small_img_gray = cv2.cvtColor(small_img_np, cv2.COLOR_BGR2GRAY)
    if main_img_np is not None:
        main_img_gray = cv2.cvtColor(main_img_np, cv2.COLOR_BGR2GRAY)
    else:
        file_name = f'{catch_file_name}_kit_match_in_{str(int(time.time()*1000000))}.jpg'
        adc_snapshot(filename=file_name, msg="get a adc_snapshot.")
        img_path = os.path.join(ST.LOG_DIR, file_name)
        main_img_gray = cv2.imread(img_path, 0)
    # 进行模板匹配
    res = cv2.matchTemplate(main_img_gray, small_img_gray, cv2.TM_CCOEFF_NORMED)

    # 找到最大和最小值及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # 使用最大值位置作为匹配结果
    top_left = max_loc
    h, w = small_img_gray.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    pos = (top_left[0] + int(w / 2), top_left[1] + int(h / 2))
    if print_str:
        monitor_print(f'{print_str}, max_val: {max_val}')
    if max_val > threshold:
        if is_back_threshold:
            return {
                "pos": pos,
                "threshold": max_val,
                "filename": filename
            }
        else:
            return pos
    else:
        return None


def kit_match_in_thread(small_img_np , q, main_img_np = None, threshold=0.57, print_str = '', is_back_threshold = False, filename = None):
    pos = kit_match_in(small_img_np, main_img_np, threshold, print_str, is_back_threshold, filename)
    q.put(pos)   # 将结果放入队列


# ocr某个区域
def ocr_keyword_with_img_np(ocr_region, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}, name = '', det = True, is_expand = False, name_type = catch_file_name):
    if name:
        ocr_file_name = f'ocr_{name}'
    else:
        ocr_file_name = 'ocr'
    img_path = snapshotImg(ocr_file_name, name_type ,LT=(ocr_region[0], ocr_region[1]),RB=(ocr_region[2], ocr_region[3]),path=True)
    if is_expand:
        img_np = cv2.imread(img_path)
        img_expend = cv2.resize(img_np, (int(img_np.shape[1] * 4), int(img_np.shape[0] * 4)))
        cv2.imwrite(img_path, img_expend)
    for type in remote_ocr_type:
        if type in [2, 1]:
            res = kit_ocr_chinese_by_eas(img_path, det=det)
        else:
            res = kit_ocr_num_by_eas(img_path, det=det)
        if res:
            ocr_res = [(item["txts"], ((item["box"][0][0]+item["box"][1][0])/2+ocr_region[0], (item["box"][0][1]+item["box"][1][1])/2
                                       + ocr_region[1]) if item["box"] else None) for item in res]
            if ocr_res:
                for item in ocr_res:
                    if item[0] in fault_tolerant_map:
                        item[0] = fault_tolerant_map[item[0]]
                return ocr_res
    return []


def ocr_keyword_return_pos_with_image_np(img,name_type = catch_file_name, remote_ocr_type='chinese', fault_tolerant_map={}, name = '', det = True, is_expand = False):

    img_path = None
    if isinstance(img, str):
        if img.startswith("http"):
            # 从URL获取图像内容
            response = requests.get(img)
            img_path = os.path.join(ST.LOG_DIR, f"{name_type}_ocr_{str(int(time.time() * 1000000))}.jpg")
            with open(img_path, "wb") as f:
                f.write(response.content)
        else:
            img_path = img
    elif isinstance(img, np.ndarray):
        if name:
            img_name = f"{name_type}_ocr_{name}_{str(int(time.time() * 1000000))}.jpg"
        else:
            img_name = f"{name_type}_ocr_{str(int(time.time() * 1000000))}.jpg"
        img_path = os.path.join(ST.LOG_DIR, img_name)
        cv2.imwrite(img_path, img)
    elif isinstance(img, Image.Image):
        img_path = os.path.join(ST.LOG_DIR, f"{name_type}_ocr_{str(int(time.time() * 1000000))}.jpg")
        img.save(img_path)
    if not img_path:
        return []
    if is_expand:
        img_np = cv2.imread(img_path)
        img_expend = cv2.resize(img_np, (int(img_np.shape[1] * 4), int(img_np.shape[0] * 4)))
        cv2.imwrite(img_path, img_expend)
    # for type in remote_ocr_type:
    if remote_ocr_type == 'en':
        res = kit_ocr_num_by_eas(img_path, det = det)
    else:
        res = kit_ocr_chinese_by_eas(img_path, det = det)   
    if res:
        ocr_res = [(item["txts"], ((item["box"][0][0]+item["box"][1][0])/2, (item["box"][0][1]+item["box"][1][1])/2) if item["box"] else None) for item in res]
        if ocr_res:
            for item in ocr_res:
                if item[0] in fault_tolerant_map:
                    item[0] = fault_tolerant_map[item[0]]
            return ocr_res
    return []

# 比较图像相似度
def compare_histograms(img1, img2, threshold = 0.9):
    # 转换为HSV色彩空间，因为HSV更能反映人类对颜色的感知
    img1_hsv = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    img2_hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
    # 计算图像的HSV色彩空间的直方图
    hist1 = cv2.calcHist([img1_hsv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([img2_hsv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    # 归一化直方图
    cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    # 计算直方图的相似度，这里使用Correlation方法
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    print("\033[1;33m", f"<相似度: {similarity}>".center(100, "="), "\033[0m", sep="")
    if similarity > threshold:
        return True
    else:
        return False
# ssim结构相似度指数
def compare_ssim_func(img1, img2, threshold = 0.9):
    from skimage.metrics import structural_similarity as compare_ssim
    # 确保图片已经正确读取
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # 计算SSIM
    ssim_score = compare_ssim(gray1, gray2)
    monitor_print(f'---ssim compare is {ssim_score}')
    # print("\033[1;33m", f"<ssim 相似度: {ssim_score}>".center(100, "="), "\033[0m", sep="")
    if ssim_score > threshold:
        return True
    else:
        return False
    
# 长截图合成
def long_snapshot_comp(img_np_list, name, one_row_count = 1, max_rows_count = 6, spacing = 10, spacing_color = (196, 175, 153), bg_path = None, title_info = None, image_type = png_file_name):
    if img_np_list != []:
        new_img_list = []
        combine_imgs = combine_images(img_np_list, one_row_count = one_row_count, max_rows_count = max_rows_count, spacing = spacing, spacing_color = spacing_color)
        for idx, image in enumerate(combine_imgs):
            if bg_path and title_info:
                combine_final_image =  combine_images_with_bg_and_title(image, bg_path, (10,10,10,10), sub_title_info = title_info)
                write_path = os.path.join(ST.LOG_DIR, f"{image_type}_{name}_{idx}_" + str(int(time.time()*1000000)) + ".jpg")
                cv2.imwrite(write_path, combine_final_image)
                new_img_list.append(combine_final_image)
            else:
                write_path = os.path.join(ST.LOG_DIR, f"{image_type}_{name}_{idx}_" + str(int(time.time()*1000000)) + ".jpg")
                cv2.imwrite(write_path, image)
                new_img_list.append(image)
        return new_img_list
    else:
        return None
       

class KitSwipe():
    '''
        combine_part_name: 截图分类名称
        swipe_start_pos: 滑动起始位置
        swipe_end_pos: 滑动结束位置
        check_bottom_start: 判底起始位置
        check_bottom_end: 判底结束位置
        img_num: 图片总数  已知需要截取小图总数情况下使用
        swipe_count: 滑动次数   已知需要滑动总数情况下使用
        bottom_origin_pos: 到底后起点坐标
        crop_data: 每个单独截图的对象的信息包括:x坐标,y坐标,宽,高,间隔x,间隔y,横向的数量,纵向的数量   全屏截图可以不传
        check_normal_image_func: 自定义校验函数 校验小图是否符合 返回结果: True/False  True则继续 False则停止
        same_type: 判底相似度校验类型: 
            1 采用match_in比较 
            2 采用直方图比较相似度 
            3 采用灰度直方图算法比较相似度 
            4 采用ocr结果比较相似度
            5 固定滑动次数判底类型 swipe_count参数必传
            6 指定区域内容ocr结果为空判断到底
            7 指定区域底部亮度阈值判断到底  亮度阈值默认40
            8 指定区域边框检测判断到底  未检测到边框则判断到底
        swipe_durations: 滑动时长 默认0.5
        ocr_check_bottom: 是否采用ocr判断到底后数据重复 默认False
        is_del_bottom_error_img: 是否删除到底错误图片 默认True
        one_line_swipe: 是否一行滑动 默认False
        del_error_img_func: 删除错误图片函数(暂停使用)
        compare_check_bottom: 到底后是否采用ssim相似度去除重复截图(暂停使用)
        text_similarity: 到底后采用ocr结果去重 与ocr_check_bottom共用
        is_keep_first: 是否保留第一个截图 默认False
        check_func: 滑动过程中校验图片合法性函数 通常滑动时校验图片是否存在弹窗
        try_snapshot_func: 滑动过程中校验图片是否需要重新截取 True需要 False不需要
        second_check_func: 滑动结束后二次校验是否停止滑动截图 True继续截图 False 停止
        last_repeat_check: 最后一张重复截图校验 默认 False 打开后取中心区域比对,相似度达到0.9以上则判定相同
        check_normal_image_index: 图片校验函数是否传入 当前图片索引下标 默认False 
        match_threshold: 相似度阈值 默认0.7
        is_back_full_screen: 是否返回整屏截图 默认False
        compare_check_bottom_threshold: 底部重复图片相似度阈值 默认0.9
        swipe_offset_func: 滑动偏移函数,参数传入 滑动距离
        blank_exceed_one_line: 游戏内最后一页道具格子是否自动补全超过一行 默认True
    '''
    def __init__(self,**kwargs):
        self.combine_part_name = kwargs.get('combine_part_name', '')
        self.swipe_start_pos = kwargs.get('swipe_start_pos', None)
        self.swipe_end_pos = kwargs.get('swipe_end_pos', None)
        self.check_bottom_start = kwargs.get('check_bottom_start', None)
        self.check_bottom_end = kwargs.get('check_bottom_end', None)
        self.img_num = kwargs.get('img_num', None)
        self.swipe_count = kwargs.get('swipe_count', None)
        self.bottom_origin_pos = kwargs.get('bottom_origin_pos', None)
        self.crop_data = kwargs.get('crop_data', None)
        self.check_normal_image_func = kwargs.get('check_normal_image_func', None)
        self.same_type = kwargs.get('same_type', 1)
        self.swipe_durations = kwargs.get('swipe_durations', 0.5)
        self.ocr_check_bottom = kwargs.get('ocr_check_bottom', False)
        self.is_del_bottom_error_img = kwargs.get('is_del_bottom_error_img', True)
        self.one_line_swipe = kwargs.get('one_line_swipe', False)
        self.del_error_img_func = kwargs.get('del_error_img_func', None)
        self.compare_check_bottom = kwargs.get('compare_check_bottom', False)
        self.text_similarity = kwargs.get('text_similarity', 0.8)
        self.is_keep_first = kwargs.get('is_keep_first', False)
        self.check_func = kwargs.get('check_func', None)
        self.try_snapshot_func = kwargs.get('try_snapshot_func', None)
        self.mask_func = kwargs.get('mask_func', None)
        self.second_check_func = kwargs.get('second_check_func', None)
        self.last_repeat_check = kwargs.get('last_repeat_check', False)
        self.swipe_time_sleep = kwargs.get('swipe_time_sleep', 0.5)
        self.check_bottom_func = kwargs.get('check_bottom_func', None)
        self.check_normal_image_index = kwargs.get('check_normal_image_index', False)
        self.match_threshold = kwargs.get('match_threshold', 0.7)
        self.is_back_full_screen = kwargs.get('is_back_full_screen', False)
        self.compare_check_bottom_threshold = kwargs.get('compare_check_bottom_threshold', 0.9)
        self.swipe_offset_func = kwargs.get('swipe_offset_func', None)
        self.image_offset_func = kwargs.get('image_offset_func', None)
        self.blank_exceed_one_line = kwargs.get('blank_exceed_one_line', True)
    def snapshot_swipe(self):
        # 滑动次数
        count = 0
        # 滑动状态
        swipe_status = True
        if self.crop_data:
            origin_x,origin_y,  width,heigt,  interval_x,interval_y, count_x, count_y = self.crop_data
            all_num = count_x * count_y
        crop_imgs = []
        last_img_name = []
        # 判底图片数组
        judge_bottom_img = None
        last_img_ocr_name = None
        # 相同类型 主要处理第四种类型判底逻辑
        is_same_type = 1
        # 第6种判底方式 使用滑动完的惯性截图底部未下来区域截图来判底
        is_bottom = False
        # 全屏截图
        full_img_list = []
        while swipe_status:
            if count > 100:
                lx_break_runloop(desc='长截图失败失败')
                break
            if self.try_snapshot_func:
                for try_count in range(5):
                    snap_file_name = f"{catch_file_name}_swipe_{self.combine_part_name}_{count}_{str(int(time.time() * 1000000))}.jpg"
                    adc_snapshot(filename=snap_file_name, msg="get a adc_snapshot.")
                    img_status = self.try_snapshot_func(snap_file_name)
                    if not img_status:
                        break
                    else:
                        monitor_task_status(ENV, f"{self.combine_part_name} 截图校验检测到异常", "重新截取图片")
            else:
                snap_file_name = f"{catch_file_name}_swipe_{self.combine_part_name}_{count}_{str(int(time.time() * 1000000))}.jpg"
                adc_snapshot(filename=snap_file_name, msg="get a adc_snapshot.")
            if self.check_func is not None:
                self.check_func(snap_file_name)
            if judge_bottom_img is None:
                judge_bottom_img = crop_pos_image_from_snapshot(snap_file_name, f"{tmp_file_name}_judge_bottom_img_{self.combine_part_name}.jpg", self.check_bottom_start,self.check_bottom_end, False)
                if self.same_type == 4:
                    # 第一行名称
                    ocr_result = ocr_keyword_with_img_np((self.check_bottom_start[0],self.check_bottom_start[1],self.check_bottom_end[0],self.check_bottom_end[1]), remote_ocr_type = (2,1))
                    if ocr_result:
                        last_img_ocr_name = ocr_result[-1][0]
            else:
                now_bottom_img = crop_pos_image_from_snapshot(snap_file_name, f"{tmp_file_name}_now_bottom_img_{self.combine_part_name}.jpg", self.check_bottom_start,self.check_bottom_end, False)
                if self.same_type == 1:
                    # 是否相同判断
                    is_same = kit_match_in(judge_bottom_img, now_bottom_img, threshold=self.match_threshold, print_str = f'---kit_swipe_match {self.combine_part_name}')
                elif self.same_type == 2:
                    # 直方图比较方法
                    is_same = compare_histograms(judge_bottom_img, now_bottom_img)
                elif self.same_type == 3:
                    if calculate(judge_bottom_img, now_bottom_img) > 0.7:
                        is_same = True
                    else:
                        is_same = False
                elif self.same_type == 4:
                    # 第一行名称
                    ocr_result = ocr_keyword_with_img_np((self.check_bottom_start[0],self.check_bottom_start[1],self.check_bottom_end[0],self.check_bottom_end[1]), remote_ocr_type = (2,))
                    if ocr_result:
                        now_check_bottom_name = ocr_result[-1][0]
                        monitor_print(f'---{self.combine_part_name} swipe same type four orc result: {ocr_result}')
                        # print("\033[1;33m", f"<ocr结果: {now_check_bottom_name} 比较上一次: {last_img_ocr_name}> ".center(100, "="), "\033[0m", sep="")
                        if now_check_bottom_name == last_img_ocr_name:
                            is_same = True
                        else:
                            is_same = False
                            last_img_ocr_name = now_check_bottom_name
                    else:
                        is_same = True
                        is_same_type = 2
                        monitor_print(f'---{self.combine_part_name} swipe adc_snapshot ocr result is none')
                    # print("\033[1;33m", f"最后名称: {last_img_ocr_name}>".center(100, "="), "\033[0m", sep="")
                    # if ocr_result:
                elif self.same_type in [6, 7, 8, 9]:
                    if is_bottom:
                        is_same = True
                    else:
                        is_same = False
                # 固定数量的滑动
                if self.swipe_count is not None:
                    if count >= self.swipe_count:
                        is_same = True
                    else:
                        is_same = False
                if is_same:
                    if self.bottom_origin_pos:
                        if self.same_type in [5,8] or self.img_num is not None:
                            origin_x,origin_y = self.bottom_origin_pos
                        else:
                            if count != 1:
                                origin_x,origin_y = self.bottom_origin_pos
                            if is_same_type == 2:
                                origin_x,origin_y = self.bottom_origin_pos
                            if self.same_type in [9]:
                                origin_x,origin_y = self.bottom_origin_pos
                    swipe_status = False
                    if self.img_num is None:
                        if crop_imgs != [] and self.is_del_bottom_error_img:
                            if self.crop_data:
                                if self.one_line_swipe:
                                    del crop_imgs[-1]
                                else:
                                    if len(crop_imgs) > all_num:
                                        for i in range(all_num):
                                            del crop_imgs[-1]
                                        if self.is_back_full_screen:
                                            del full_img_list[-1]
                                    else:
                                        crop_imgs.clear()
                            else:
                                del crop_imgs[-1]
                else:
                    judge_bottom_img = crop_pos_image_from_snapshot(snap_file_name, f"tmp_judge_bottom_img_{self.combine_part_name}.jpg", self.check_bottom_start,self.check_bottom_end, False)
            if self.is_back_full_screen:
                snap_one_img_path = os.path.join(ST.LOG_DIR, snap_file_name)
                snap_one_img_np = cv2.imread(snap_one_img_path)
                if self.mask_func:
                    self.mask_func(snap_one_img_np, is_np = True)
                full_img_list.append(snap_one_img_np)
            if self.crop_data:
                first_index = 0
                end_index = None
                if self.img_num:
                    if not swipe_status:
                        # 余数 
                        remainder = self.img_num % all_num
                        if remainder != 0:
                            if count_x != 1:
                                # 结束前空格子数
                                blank = count_x - (remainder % count_x)
                                if not self.blank_exceed_one_line and blank == count_x:
                                    blank = 0
                            else:
                                blank = 0
                            first_index = all_num - remainder - blank
                            end_index = all_num - blank - 1
                    else:
                        if self.img_num < all_num:
                            end_index = self.img_num - 1
                if self.one_line_swipe:
                    if count > 0:
                        first_index = count_x * (count_y - 1)
                    else:
                        first_index = 0

                for i in range(first_index, all_num):
                    if end_index is not None:
                        if i > end_index:
                            break
                    row_index = i//count_x+1
                    column_index = i%count_x+1
                    offset_x, offset_y = 0, 0 
                    if self.image_offset_func:
                        if self.check_normal_image_index:
                            offset_x, offset_y = self.image_offset_func(self.combine_part_name,[count, i])
                        else:
                            offset_x, offset_y = self.image_offset_func(self.combine_part_name)
                    
                    crop_start_pos_x = origin_x + (column_index-1) * (interval_x +width) + offset_x
                    crop_start_pos_y = origin_y + (row_index-1) * (interval_y + heigt) + offset_y 
                    crop_end_pos_x = crop_start_pos_x + width
                    crop_end_pos_y = crop_start_pos_y + heigt

                    middle_x = crop_start_pos_x + width//2
                    middle_y = crop_start_pos_y + heigt//2 
                    result_img = crop_pos_image_from_snapshot(snap_file_name, f"{tmp_file_name}_swipe_cropped_image_{self.combine_part_name}_{count}_{i}.jpg", (crop_start_pos_x, crop_start_pos_y),(crop_end_pos_x, crop_end_pos_y), False)
                    if self.ocr_check_bottom:
                        if not swipe_status:
                            if not last_img_name:
                                for img in crop_imgs[-all_num :]:
                                    img_res = ocr_keyword_return_pos_with_image_np(img)
                                    if img_res:
                                        img_name_str = ''
                                        for img_name in img_res:
                                            img_name_str += img_name[0]
                                        last_img_name.append(img_name_str)
                            is_continue = False
                            result_img_res = ocr_keyword_return_pos_with_image_np(result_img)
                            if result_img_res:
                                now_img_name = ''
                                for n_img_name in result_img_res:
                                    now_img_name += n_img_name[0]
                                for item in last_img_name:
                                    matcher_ratio = difflib.SequenceMatcher(a = item, b = now_img_name).ratio()
                                    if matcher_ratio > self.text_similarity:
                                        monitor_task_status(ENV, f"{self.combine_part_name} 判断底部校验结果", f"{item} 与 {now_img_name} 相似度: {matcher_ratio}")
                                        # print("\033[1;33m", f"<{item} 与 {now_img_name}相似度: {matcher_ratio}>".center(100, "="), "\033[0m", sep="")
                                        is_continue = True
                                        break

                            if is_continue:
                                continue
                    if self.compare_check_bottom:
                        if not swipe_status:
                            if not last_img_name:
                                is_continue = False
                                for img in crop_imgs[-all_num :]:
                                    ssim_compare = compare_ssim_func(result_img, img, threshold=self.compare_check_bottom_threshold)
                                    if ssim_compare:
                                        is_continue = True
                                        break
                                if is_continue:
                                    continue
                    if self.check_normal_image_func is not None:
                        check_pos = (crop_start_pos_x + width / 2, crop_start_pos_y + heigt / 2)
                        if self.check_normal_image_index:
                            verify_func = self.check_normal_image_func(result_img, self.combine_part_name, check_pos,[count, i])
                        else:
                            verify_func = self.check_normal_image_func(result_img, self.combine_part_name, check_pos)
                        
                        if verify_func:
                            if verify_func != 'pass':
                                crop_imgs.append(result_img)
                        else:
                            if self.is_keep_first:
                                if len(crop_imgs) == 0:
                                    crop_imgs.append(result_img)
                            swipe_status = False
                            break
                    else:
                        crop_imgs.append(result_img)
                if self.second_check_func:
                    if not self.second_check_func(snap_file_name):
                        swipe_status = False
            else:
                full_screen_path = os.path.join(ST.LOG_DIR, snap_file_name)
                if self.mask_func:
                    self.mask_func(full_screen_path)
                full_screen_np = cv2.imread(full_screen_path)
                
                if self.check_normal_image_func is not None:
                    if self.check_normal_image_func(full_screen_np, self.combine_part_name):
                        crop_imgs.append(full_screen_np)
                    else:
                        swipe_status = False
                else:
                    full_screen_path = os.path.join(ST.LOG_DIR, snap_file_name)
                    full_screen_np = cv2.imread(full_screen_path)
                    crop_imgs.append(full_screen_np)
            if self.swipe_count is not None:
                if self.swipe_count == count and self.swipe_count == 0 and self.img_num is not None:
                    swipe_status = False
            if swipe_status:
                if self.one_line_swipe:
                    before_img = snapshotImg(f'{self.combine_part_name}_before_swipe_{count}', catch_file_name ,LT=self.check_bottom_start, RB=self.check_bottom_end)
                if self.swipe_offset_func:
                    swipe_end_pos = self.swipe_offset_func(self.swipe_end_pos, count)
                else:
                    swipe_end_pos = self.swipe_end_pos
                if self.same_type not in [6, 7, 8, 9]:
                    if self.swipe_durations:
                        swipe_duration(self.swipe_start_pos, swipe_end_pos, duration = self.swipe_durations, sleep_time=self.swipe_time_sleep)
                    else:
                        swipe_with_seperate(startPos=self.swipe_start_pos,endPos=self.swipe_end_pos)
                else:
                    snap_befor_file_name = f"{catch_file_name}_{self.combine_part_name}_befor_swipe_{count}_{str(int(time.time() * 1000000))}.jpg"
                    if self.swipe_durations:
                        swipe_duration(self.swipe_start_pos, self.swipe_end_pos, sleep_time=0, duration = self.swipe_durations, snapshot_name = snap_befor_file_name)
                    else:
                        swipe_duration(self.swipe_start_pos, self.swipe_end_pos, sleep_time=0, snapshot_name = snap_befor_file_name)
                    check_bottom_file_name = f"{catch_file_name}_{self.combine_part_name}_befor_swipe_check_{count}_{str(int(time.time() * 1000000))}.jpg"
                    second = crop_pos_image_from_snapshot(snap_befor_file_name, check_bottom_file_name, self.check_bottom_start, self.check_bottom_end, False)
                    # 指定区域亮度阈值判断到底
                    if self.same_type == 7:
                        bottom_brightness = calculate_average_brightness(second, path=False, print_result=self.combine_part_name)
                        monitor_print(f"---check calculate_average_brightness is: {bottom_brightness},img name {check_bottom_file_name}")
                        if bottom_brightness:
                            is_bottom = True
                    # 指定区域内容为空判断到底
                    elif self.same_type == 6:
                        img_ocr_res = ocr_keyword_return_pos_with_image_np(second)
                        monitor_print(f"---check ocr is None result: {img_ocr_res},img name {check_bottom_file_name}")
                        if not img_ocr_res:
                            is_bottom = True
                            if count == 0:
                                swipe_status = False
                    # 指定区域边框检测判断到底
                    elif self.same_type == 8:
                        edge_list = check_grap_edges(second)
                        monitor_print(f"---check grap edges is {edge_list},img name {check_bottom_file_name}")
                        if not edge_list:
                            is_bottom = True
                    elif self.same_type == 9:
                        check_bottom_status = self.check_bottom_func(second)
                        monitor_print(f"---check_bottom_status is {check_bottom_status},img name {check_bottom_file_name}")
                        if check_bottom_status:
                            is_bottom = True
                if self.one_line_swipe:
                    check_pos = self.find_position(before_img, count)
                    if check_pos:
                        # 计算差异
                        expected_dy = check_pos[1] - self.crop_data[1]
                        monitor_print(f'---check_swipe_offset: offset_num {expected_dy} new_origin_y {check_pos[1]}')
                        # if expected_dy < 5 and expected_dy > -5 and expected_dy != 0:
                        #     origin_y = check_pos[1]
                        # else:
                        #     new_end_pos = (self.swipe_start_pos[0], self.swipe_start_pos[1] - (expected_dy * 3))
                        #     print(new_end_pos)
                        #     swipe_duration(self.swipe_start_pos, new_end_pos, duration = self.swipe_durations, sleep_time=self.swipe_time_sleep)
                        #     origin_y = self.crop_data[1]
            count += 1
        if self.last_repeat_check:
            if len(crop_imgs) >= 2:
                last_first_line, last_first_img, last_first_central_area = kit_check_grap_edges(crop_imgs[-1])
                last_second_line, last_second_img, last_second_central_area = kit_check_grap_edges(crop_imgs[-2])
                last_first_central_img = crop_imgs[-1][last_first_central_area['min_y']:last_first_central_area['max_y'], last_first_central_area['min_x']:last_first_central_area['max_x']]
                last_second_central_img = crop_imgs[-2][last_second_central_area['min_y']:last_second_central_area['max_y'], last_second_central_area['min_x']:last_second_central_area['max_x']]
                try:
                    check_img = kit_match_in(last_first_central_img, last_second_central_img, threshold = 0.9)
                    if check_img:
                        crop_imgs = crop_imgs[:-1]
                except:
                    check_img = kit_match_in(crop_imgs[-1], crop_imgs[-2], threshold = 0.7)
                    if check_img:
                        crop_imgs = crop_imgs[:-1]
        if self.is_back_full_screen:
            if len(full_img_list) >= 2:
                back_full_screen_last_first = full_img_list[-1][self.check_bottom_start[1]:self.check_bottom_end[1], self.check_bottom_start[0]:self.check_bottom_end[0]]
                back_full_screen_last_second = full_img_list[-2][self.check_bottom_start[1]:self.check_bottom_end[1], self.check_bottom_start[0]:self.check_bottom_end[0]]
                check_back_full_screen = kit_match_in(back_full_screen_last_first, back_full_screen_last_second, threshold = self.match_threshold)
                if check_back_full_screen:
                    full_img_list = full_img_list[:-1]

            return crop_imgs, full_img_list
        return crop_imgs
    
    def find_position(self, template, count, threshold=0.9):
        """通过模板匹配定位特征点位置"""
        after_img = snapshotImg(f'{self.combine_part_name}_after_swipe_{count}', catch_file_name)
        result = cv2.matchTemplate(after_img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        print(max_val)
        return max_loc if max_val > threshold else None 


#默认支持纵向滑动
def swipe_duration(p1, p2, duration=0.5, steps=5, sleep_time = 0.5, snapshot_name = False):
    # actionDevice.touch_proxy.touch(p1)
    from_x, from_y = p1
    to_x, to_y = p2
    system = ENV.system_type
    if system == 'android':
        device = ENV.device
        # swipe_along_func([p1, (to_x, to_y)], duration = duration)
        device.touch_proxy.swipe_along([(from_x, from_y), (to_x, to_y-2), (to_x, to_y)], duration=duration)
    elif system == 'ios':
        adc_swipe((from_x, from_y), (to_x, to_y), duration = duration)
    if snapshot_name:
        adc_snapshot(filename = snapshot_name, msg="get a adc_snapshot.")
        time.sleep(0.5)
    if sleep_time != 0:
        time.sleep(sleep_time)


def calculate_slide_error(before_img, after_img, direction='horizontal'):
    """
    通过特征匹配计算实际滑动距离
    :return: (实际像素偏移量, 置信度)
    """
    # 初始化 SIFT 特征检测器
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(before_img, None)
    kp2, des2 = sift.detectAndCompute(after_img, None)

    # FLANN 特征匹配
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # Lowe's 比率测试
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    # 计算特征点偏移
    if len(good) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
        
        # 计算单应性矩阵
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if M is not None:
            # 提取平移分量
            dx = M[0, 2]
            dy = M[1, 2]
            confidence = np.sum(mask) / len(mask)
            return (dx if direction == 'horizontal' else dy, confidence)
    
    return (0, 0)  # 匹配失败

def get_slide_direction(start_x, start_y, end_x, end_y):
    """自动判断主要滑动方向"""
    dx = end_x - start_x
    dy = end_y - start_y
    
    if abs(dx) > abs(dy):
        return 'horizontal', abs(dx), abs(dy)
    else:
        return 'vertical', abs(dy), abs(dx)

class SlideCalibrator:
    def __init__(self):
        self.h_factor = 0  # 水平校准系数
        self.v_factor = 0  # 垂直校准系数
        self.calibration_factor = 1.0
        self.error_history = []

    def adaptive_swipe(self, start_x, start_y, end_x, end_y, max_retry=3):
        """
        自适应校准滑动（新版）
        :param start_x: 起始点X坐标
        :param start_y: 起始点Y坐标
        :param end_x: 目标X坐标
        :param end_y: 目标Y坐标
        """
        # 计算预期滑动参数
        expected_dx = end_x - start_x
        expected_dy = end_y - start_y
        if expected_dx == 0:
            distance = expected_dy
        else:
            distance = expected_dx
        main_dir, main_dist, sub_dist = get_slide_direction(start_x, start_y, end_x, end_y)
        
        for attempt in range(max_retry):
            # 步骤1: 获取滑动前截图
            before_img = snapshotImg('before_swipe', catch_file_name ,LT=(357, 640), RB=(2179, 895))
            
            # 步骤2: 执行原始滑动（使用初始校准系数）
            calibrated_end_x = start_x + expected_dx + self.h_factor
            calibrated_end_y = start_y + expected_dy + self.v_factor
            print('-----swipe',(start_x, start_y), (calibrated_end_x, calibrated_end_y))
            adc_swipe((start_x, start_y), (calibrated_end_x, calibrated_end_y))
            
            # 步骤3: 获取滑动后截图
            time.sleep(0.3)
            
            new_pos = self.find_position(before_img)
            if new_pos:
                print('-----差异', new_pos)
            break
        print("❌ 达到最大重试次数")
        return False
    def find_position(self, template, threshold=0.9):
        """通过模板匹配定位特征点位置"""
        screen = snapshotImg('search', catch_file_name)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_loc if max_val > threshold else None 
        
    def _fallback_calculation(self, before, after, direction):
        """备用方案：基于边缘检测的偏移计算"""
        # 灰度化 + Canny边缘检测
        gray_before = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
        gray_after = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
        edges_before = cv2.Canny(gray_before, 50, 150)
        edges_after = cv2.Canny(gray_after, 50, 150)
        
        # 计算相位相关性
        (shift_x, shift_y), _ = cv2.phaseCorrelate(
            np.float32(edges_before), 
            np.float32(edges_after)
        )
        
        return shift_x if direction == 'horizontal' else shift_y
    
    def _calculate_duration(self, x1, y1, x2, y2):
        """动态计算滑动时间"""
        distance = np.sqrt( (x2-x1)**2 + (y2-y1)**2 )
        return int( 300 + distance * 0.4 )  # 经验公式：0.4ms/
    
   



# 平均亮度获取
def calculate_average_brightness(image_path, brightness = 40, path = True, print_result = None):
    """
    计算并返回图像的平均亮度。
    :param image_path: 图片文件路径
    :param brightness: 亮度阈值
    :return: 图像的平均亮度值
    """
    if path:
        filePath = os.path.join(ST.LOG_DIR, image_path)
        img = cv2.imread(filePath)
    else:
        img = image_path
    # 将图像转换为灰度图像
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 计算所有像素的平均值，这将给出图像的平均亮度
    average_brightness = np.mean(gray_image)
    if print_result is not None:
        monitor_print(f"---{print_result} calculate average brightness value is: {average_brightness}")
    print("\033[1;33m", f"<平均亮度: {average_brightness}>".center(100, "="), "\033[0m", sep="")
    if average_brightness < brightness:
        return True
    else:
        return False
# 横向边框检测
def check_grap_edges(img, second_check_ocr = True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图，有利于边缘检测
    edges = cv2.Canny(gray, 50, 150)  # Canny边缘检测
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    if lines is not None:
        horizontal_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi  # 计算线段的角度
            if abs(angle) < 10:  # 根据实际情况调整这个角度阈值
                horizontal_lines.append([(x1, y1),(x2, y2)])
        return horizontal_lines
    else:
        if second_check_ocr:
            # 二次校验 判断是否存在内容 增强检测
            second_check = ocr_keyword_return_pos_with_image_np(img)
            if second_check:
                return second_check
            else:
                return lines
        else:
            return lines

def resize_image(img_np, scale_percent):
    """
    打开图片并按比例缩小
    :param img_np: 图片数组
    :param scale_percent: 缩放比例（百分比）
    :return: 缩放后的图片
    """
    # 获取图片的宽度和高度
    width = int(img_np.shape[1] * scale_percent[0] / 100)
    height = int(img_np.shape[0] * scale_percent[1] / 100)
    dim = (width, height)
    return dim

def image_write_text(title_image, text, text_color, font_size=None, textPoint=None, text_bg_color=None, offset = (0,0)):
    
    # 将图像转换为PIL格式
    image_pil = Image.fromarray(cv2.cvtColor(title_image, cv2.COLOR_BGR2RGB))

    # 创建绘图对象
    draw = ImageDraw.Draw(image_pil)

    ttf_path = ENV.rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'
    the_font_size = 60
    if font_size is not None:
        the_font_size = font_size
    font = ImageFont.truetype(ttf_path, size=the_font_size)
    text_lenth = draw.textlength(text, font=font)
    # # 计算文字的居中位置
    title_image_height, title_image_width, _ = title_image.shape
    text_position = None
    if textPoint is not None:
        
        if textPoint[0] is None:
            text_x = ((title_image_width - text_lenth) // 2 ) + offset[0]
            text_position = (text_x, textPoint[1])
        elif textPoint[0] == 'right':
            text_x = int(title_image_width - text_lenth) + offset[0]
            text_position = (text_x, textPoint[1])
        elif textPoint[0] == 'left':
            text_x =  text_lenth + offset[0]
            text_position = (text_x, textPoint[1])
        else:
            text_position = textPoint
    else:
        
        text_x = (title_image_width - text_lenth) // 2
        text_y = (title_image_height - the_font_size) // 2 - 5

        text_position = (text_x, text_y)  # 文字位置 (x, y)

    if text_bg_color:
        small_bg_image = Image.new('RGB', (int(text_lenth), the_font_size), color=text_bg_color)
        small_bg_draw = ImageDraw.Draw(small_bg_image)
        small_bg_draw.text((0, -5), text, font=font, fill=text_color)
        image_pil.paste(small_bg_image, text_position)
    else:
        draw.text(text_position, text, font=font, fill=text_color)


    # 将PIL图像转换回OpenCV格式
    title_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return title_image

# 将指定坐标区域替换为指定颜色
def image_replace_with_color(img, top_left, bottom_right, rbg = (0, 0, 0)):
    # 获取指定区域的坐标
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # 遍历指定区域内的每一个像素
    for y in range(y1, y2):
        for x in range(x1, x2):
            # 将白色像素替换为黑色
            img[y, x] = [rbg[0], rbg[1], rbg[2]]

    return img

# 账号总览
def accentOverview(img_list, overview_list,template_path, target_area = None, spacing=0, wrap_by_list = False, is_adaptive = False, text_color = (233, 220, 228),font_size = 30, suffix = '0'):
    '''
        @param img_comp_ratio: 图片压缩比例
        @param wrap_by_list: 强制换行
        @param is_adaptive: 是否自适应
        @param img_list: 
            - region_xywh: (x, y, w, h)，指定区域在背景图上的位置和大小
                x, y 为区域左上角坐标w, h 为区域宽高
            - image_paths: 要放置的图片路径列表
            - cols: 该区域内一行多少个（列数）
            - rows: 该区域内一列多少个（行数）
            - max_count: 该区域内最大放置多少个图片
                        None 或 <=0 时，默认允许放满 cols*rows 个
            - keep_ratio: 是否保持图片原始宽高比例自适应缩放到每个格子内

    '''
    monitor_task_status_v2("账号总览合成", "预处理阶段")
    try:
        template_image = cv2.imread(template_path)
        template_image_size = (template_image.shape[1], template_image.shape[0])
        # 创建一个新的图片用于放置小图
        overlay = Image.new('RGBA', template_image_size, (0, 0, 0, 0))
        for overview in overview_list:
            if 'font_size' in overview.keys():
                font_size = overview['font_size']
            if 'text_color' in overview.keys():
                text_color = overview['text_color']
            rename_img = image_write_text(template_image, text = str(overview['value']), text_color=text_color,font_size = font_size, textPoint = overview['pos'])
            template_image = rename_img
        wirte_path = os.path.join(ST.LOG_DIR, "template.jpg")
        cv2.imwrite(wirte_path, template_image)
        template_img_np = Image.open(wirte_path).convert('RGBA')
        # 计算指定区域的宽度和高度
        target_left, target_upper, target_right, target_lower = target_area
        target_width = target_right - target_left
        target_height = target_lower - target_upper
        
        # 初始化图片的当前左上角位置
        current_x = target_left
        current_y = target_upper
        max_height = 0
        if not is_adaptive:
            for img_one_list in img_list:
                for img in img_one_list:
                    if img is None:
                        continue
                    # 打开并获取单个图片的尺寸
                    img_width, img_height = img.shape[1],img.shape[0]
                    # 如果当前位置加上图片尺寸超过目标区域，则换行
                    if current_x + img_width > target_right:
                        current_x = target_left  # 重置x坐标到起始位置
                        current_y += max_height + spacing  # 增加y坐标
                        max_height = 0
                    if img_height > max_height:
                        max_height = img_height
                    wirte_path_img_small = os.path.join(ST.LOG_DIR, f"tmp_{str(int(time.time()*1000000))}.jpg")
                    cv2.imwrite(wirte_path_img_small, img)
                    # 打开小图片
                    thumbnail = Image.open(wirte_path_img_small).convert('RGBA')
                    # 粘贴图片到背景图
                    overlay.paste(thumbnail, (current_x, current_y))
                    # 更新x坐标准备粘贴下一张图片
                    current_x += img_width + spacing
                # --------- 子列表结束后的“强制换行”逻辑 -----------
                if wrap_by_list:
                    current_x = target_left
                    current_y += max_height + spacing
                    max_height = 0
                # （可选）如果超过目标区域下边界，就停止
                if current_y > target_lower:
                    print("超过目标区域，下方图片将被忽略")
        else:
            for data_one in img_list:
                x_region, y_region = data_one['region_xywh'][0], data_one['region_xywh'][1]
                region_w, region_h = data_one['region_xywh'][2] - x_region, data_one['region_xywh'][3] - y_region
                cols, rows = data_one['cols'], data_one['rows']
                spacing_x, spacing_y = data_one['spacing_x'] if 'spacing_x' in data_one.keys() else 0, data_one['spacing_y'] if 'spacing_y' in data_one.keys() else 0
                if cols <= 0 or rows <= 0:
                    raise ValueError("cols 和 rows 必须为正整数")
                total_slots = cols * rows
                max_count = data_one['max_count']
                if max_count is None or max_count <= 0:
                    max_count = total_slots
                else:
                    max_count = min(max_count, total_slots)
                images = data_one['img_list'][:max_count]
                # 计算“内容区域”的宽高（扣除间隔）
                # 水平方向：cols 个格子，中间有 (cols-1) 个间隔
                total_spacing_x = spacing_x * (cols - 1)
                total_spacing_y = spacing_y * (rows - 1)
                # 可用于内容的总宽 / 高
                content_w = region_w - total_spacing_x
                content_h = region_h - total_spacing_y
                if content_w <= 0 or content_h <= 0:
                    raise ValueError("区域太小或 spacing 太大，导致内容区域为 0 无法布局")

                # 单个格子的宽高（浮点，后面转 int）
                cell_w = content_w / cols
                cell_h = content_h / rows
                for idx, img in enumerate(images):
                    wirte_path_img_small = os.path.join(ST.LOG_DIR, f"tmp_{str(int(time.time()*1000000))}.jpg")
                    cv2.imwrite(wirte_path_img_small, img)
                    try:
                        img = Image.open(wirte_path_img_small).convert("RGBA")
                    except Exception as e:
                        continue
                    if 'radius' in data_one.keys():
                        img = make_rounded(img, radius=data_one['radius'])
                    # 当前图片所在的行列
                    row = idx // cols  # 第几行
                    col = idx % cols   # 第几列

                    # 当前格子左上角在背景图中的坐标
                    cell_x0 = x_region + int(round(col * (cell_w + spacing_x)))
                    cell_y0 = y_region + int(round(row * (cell_h + spacing_y)))

                    # 当前格子的实际像素宽高
                    cell_w_int = int(round(cell_w))
                    cell_h_int = int(round(cell_h))

                    # 拉伸到格子大小（可能会变形）
                    img_resized = img.resize((cell_w_int, cell_h_int), Image.LANCZOS)
                    paste_x = cell_x0
                    paste_y = cell_y0

                    # 粘贴到背景图上，使用自身 alpha 作为 mask
                    overlay.paste(img_resized, (paste_x, paste_y), mask=img_resized)
        # 将overlay和模版合并
        composed_image = Image.alpha_composite(template_img_np, overlay)
        # 保存结果图片
        # 转换为无透明度的 RGB 格式
        composed_image_rgb = composed_image.convert("RGB")
        composed_image_rgb.save(os.path.join(ST.LOG_DIR, f"adc_result_overview_{suffix}.jpg"),"JPEG")
    except Exception as e:
        error_traceback = traceback.format_exc()
        monitor_task_status(ENV,"账号总览合成失败", f"{error_traceback}")

    monitor_task_status_v2("账号总览合成-结束", "完成")

def make_rounded(img: Image.Image, radius: int) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    r = min(radius, min(w, h) // 2)
    draw.rounded_rectangle((0, 0, w, h), radius=r, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask=mask)
    return out

# 横向边框检测
def kit_check_grap_edges(img, minLineLength = 100, threshold1 = 50, threshold2 = 150, threshold = 100, maxLineGap = 10, min_x = None, max_x = None, min_y = None, max_y = None):
    '''
        threshold1 : 用于边缘检测的低阈值。Canny 边缘检测算法使用两个阈值，较低的阈值用于连接边缘
        threshold2 : 用于边缘检测的高阈值。如果图像梯度强度高于这个值，则被认为是边缘
        threshold : 累积平面中投票数的阈值。只有得到足够 "票数" 的直线才会被检测出。这个值越低，会检测出越多的直线（一些可能是噪声）；这个值越高，则可能遗漏一些直线。根据你的应用需求进行调整
        minLineLength : 可被认为是一条直线的最小长度。任何短于此长度的线段都会被舍弃。
        maxLineGap : 可以帮助你控制断线段的连接程度，适当的值可以连接那些你希望实际连接在一起的断线。
        中心区域计算 可传值决定起点值 默认为空
            min_x: 最小x坐标值
            min_y: 最小y坐标值
            max_x: 最大x坐标值
            max_y: 最大y坐标值
    '''
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图，有利于边缘检测
    edges = cv2.Canny(gray, threshold1, threshold2)  # Canny边缘检测
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)
    central_area = {
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y
    }
    if lines is not None:
        horizontal_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi  # 计算线段的角度
            if abs(angle) < 10:  # 根据实际情况调整这个角度阈值
                horizontal_lines.append([(x1, y1),(x2, y2)])
                if central_area['min_x']:
                    if x1 < central_area['min_x']:
                        central_area['min_x'] = x1
                else:
                    central_area['min_x'] = x1
                if central_area['max_x']:
                    if x2 > central_area['max_x']:
                        central_area['max_x'] = x2
                else:
                    central_area['max_x'] = x2
                if central_area['min_y']:
                    if y2 < central_area['min_y']:
                        central_area['min_y'] = y2
                else:
                    central_area['min_y'] = y2
                if central_area['max_y']:
                    if y2 > central_area['max_y']:
                        central_area['max_y'] = y2
                else:
                    central_area['max_y'] = y2
        return horizontal_lines, img, central_area
    return lines, img, central_area

def kit_ocr_checkout(pos, name = '', keywords = [], name_type = catch_file_name, det = True):
    '''
        pos: 坐标
        name: 名称
        type: 1 中英文 2 数字
        keywords: 关键字
    '''
    if isinstance(pos, np.ndarray):
        ocr_result = ocr_keyword_return_pos_with_image_np(pos, remote_ocr_type=(2,1), name=name, name_type = name_type, det = det)
    else:
        ocr_result = ocr_keyword_with_img_np(pos, remote_ocr_type=(2,1), name=name, name_type = name_type, det = det)
    for ocr_one in ocr_result:
        for keyword in keywords:
            if keyword in ocr_one[0]:
                return ocr_one[1]
    else:
        return False

def kit_mask_image_np(image_np, point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    # 从原始图像中裁剪出想要模糊的区域
    roi = image_np[y1:y2, x1:x2]

    # 对该区域应用高斯模糊
    blurred_roi = cv2.GaussianBlur(roi, (99, 99), 0)

    # 将模糊后的区域替换回原始图像
    image_np[y1:y2, x1:x2] = blurred_roi
    return image_np

def check_hsv(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h = int(hsv[..., 0].mean() * 2)  # Hue 平均色相
    s = int(hsv[..., 1].mean() / 255 * 100)  # Saturation 平均饱和度
    b = int(hsv[..., 2].mean() / 255 * 100)  # Brightness 平均亮度
    return (h,s,b)

def kit_get_screen_rbg(rbg_pos):
    screen = streamSnapshot()
    b, g, r = screen[rbg_pos[1], rbg_pos[0]]
    return (r, g, b)

# **********************************远端识别模型接口*******************************************
# 注意type的类型对应不同的识别模型
# 1是旧的包含异形字的ocr模型，
# 2是中英数综合模型，通用的识别模型，实测针对标准字体类型2的识别率高很多
# 3是英文数字模型
# 4是中英数轻量模型（中文识别精度高，识别快，如果ocr_ch识别不到，可以尝试该模型）

def kit_ocr_chinese_by_eas(crop_pos_img_path, upload_image_log_tag=None, det = True):
     ocr_result_1 = kit_ocr_image_by_eas(crop_pos_img_path, type=2, upload_image_log_tag = upload_image_log_tag, det = det)
     if ocr_result_1 is not None and len(ocr_result_1) > 0:
         monitor_print(f'---kit_ocr_chinese_by_eas: {ocr_result_1}, type:2, image_path:{crop_pos_img_path}')
         return ocr_result_1

     ocr_result_2 = kit_ocr_image_by_eas(crop_pos_img_path, type=4, upload_image_log_tag = upload_image_log_tag, det = det)
     if ocr_result_2 is not None and len(ocr_result_2) > 0:
         monitor_print(f'---kit_ocr_chinese_by_eas: {ocr_result_2}, type:4, image_path:{crop_pos_img_path}')
         return ocr_result_2

     ocr_result_3 = kit_ocr_image_by_eas(crop_pos_img_path, type=1, upload_image_log_tag = upload_image_log_tag, det = det)
     if ocr_result_3 is not None and len(ocr_result_3) > 0:
         monitor_print(f'---kit_ocr_chinese_by_eas: {ocr_result_3}, type:1, image_path:{crop_pos_img_path}')
         return ocr_result_3

def kit_ocr_num_by_eas(crop_pos_img_path, upload_image_log_tag=None, det = True):
    ocr_result_1 = kit_ocr_image_by_eas(crop_pos_img_path, type=3, upload_image_log_tag = upload_image_log_tag, det = det)

    if ocr_result_1 is not None and len(ocr_result_1) > 0:
        monitor_print(f'---kit_ocr_num_by_eas: {ocr_result_1}, type:3, image_path:{crop_pos_img_path}')
        return ocr_result_1

    ocr_result_2 = kit_ocr_image_by_eas(crop_pos_img_path, type=2, upload_image_log_tag = upload_image_log_tag, det = det)
    if ocr_result_2 is not None and len(ocr_result_2) > 0:
        monitor_print(f'---kit_ocr_num_by_eas: {ocr_result_2}, type:2, image_path:{crop_pos_img_path}')
        return ocr_result_2

    ocr_result_3 = kit_ocr_image_by_eas(crop_pos_img_path, type=4, upload_image_log_tag = upload_image_log_tag, det = det)
    if ocr_result_3 is not None and len(ocr_result_3) > 0:
        monitor_print(f'---kit_ocr_num_by_eas: {ocr_result_3}, type:4, image_path:{crop_pos_img_path}')
        return ocr_result_3

    ocr_result_4 = kit_ocr_image_by_eas(crop_pos_img_path, type=1, upload_image_log_tag = upload_image_log_tag, det = det)
    if ocr_result_4 is not None and len(ocr_result_4) > 0:
        monitor_print(f'---kit_ocr_num_by_eas: {ocr_result_4}, type:1, image_path:{crop_pos_img_path}')
        return ocr_result_4

# 注意type的类型对应不同的识别模型
# 1是旧的包含异形字的ocr模型，
# 2是中英数综合模型，通用的识别模型，实测针对标准字体类型2的识别率高很多
# 3是英文数字模型
# 4是中英数轻量模型（中文识别精度高，识别快，如果ocr_ch识别不到，可以尝试该模型）
def kit_ocr_image_by_eas(crop_pos_img_path, type=1, upload_image_log_tag=None, det = True):
    monitor_print(f'---kit_ocr_image_by_eas: {crop_pos_img_path}, type:{type}')
    env = AppEnv.get_instance()
    
    # cropFileName = f'crop_{cropFileName}' + str(int(time.time() * 1000000)) + '.jpg'
    #
    # crop_pos_img = crop_pos_image_from_snapshot(f"temp.jpg", cropFileName, crop_start, crop_end)

    # item_full_path = os.path.join(ST.LOG_DIR, cropFileName)

    def get_env_ocr_path(env, type =1):
        scriptEnv = env.scriptEnv
        risk_path = ""
        launch_type = env.launchType
        if launch_type == 'localtest':
            scriptEnv = 'local'

        if type == 1:
            if (scriptEnv == 'local'):
                risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
            elif (scriptEnv == 'pre'):
                risk_path = '/api/predict/lingxialgo_vision_adc'
            elif (scriptEnv == 'prod'):
                risk_path = '/api/predict/lingxialgo_vision_adc'
            else:
                risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
        else:
            if (scriptEnv == 'local'):
                risk_path = "/api/predict/lingxialgo_ocr_service_pre"
            elif (scriptEnv == 'pre'):
                risk_path = "/api/predict/lingxialgo_ocr_service_pre"
            elif (scriptEnv == 'prod'):
                risk_path = '/api/predict/lingxialgo_vision_ocr'
            else:
                risk_path = '/api/predict/lingxialgo_ocr_service_pre'

        monitor_print(f'---get_env_ocr_path: {risk_path}, type:{type}, env:{scriptEnv}')
        return risk_path

    def getOCRRequestDataWithURL(url, type=1, det = True):
        resData = {}
        resId = str(int(time.time() * 1000000))
        resData['requestId'] = resId
        resData['imageUrl'] = url
        resData['recoType'] = "ocr"
        resData['det'] = det
        if type == 2:
            resData['model'] = "ocr_ch"
        if type == 3:
            resData['model'] = "ocr_en"
        if type == 4:
            resData['model'] = "ocr_ch_mobile"

        monitor_print(f'---getOCRRequestDataWithURL: {resData}, type:{type}')
        return resData

    if not crop_pos_img_path.startswith("http"):
        localFileList = []
        localFileList.append(crop_pos_img_path)
        _, cdn_url_list = upload_jym_oss_with_pathes(localFileList)
        if cdn_url_list:
            qufu_crop_img_url = cdn_url_list[0]
        else:
            monitor_print(f'图片上传失败: {crop_pos_img_path}')
            return None
    else:
        qufu_crop_img_url = crop_pos_img_path

    if upload_image_log_tag is not None:
        monitor_print(f'---kit_ocr_image_by_eas_url {upload_image_log_tag}: {qufu_crop_img_url}, type: {type}')
    else:
        monitor_print(f'---kit_ocr_image_by_eas_url: {qufu_crop_img_url}, type: {type}')

    data = enhanced_easrequest(get_env_ocr_path(env, type= type), getOCRRequestDataWithURL(qufu_crop_img_url, type = type, det = det), type=type)

    if data is not None and 'message' in data and ('status' in data['message']) and ('data' in data['message']):
        ocrResult = data['message']['data']
        status = data['message']['status']

        if upload_image_log_tag is not None:
            monitor_print(f'---kit_ocr_image_by_eas_result {upload_image_log_tag}: {status},{type},{qufu_crop_img_url},{ocrResult}')
        else:
            monitor_print(f'---kit_ocr_image_by_eas_result: {status},{type},{qufu_crop_img_url},{ocrResult}')
        return ocrResult
    else:
        if upload_image_log_tag is not None:
            monitor_print(f'---kit_ocr_image_by_eas_result_none {upload_image_log_tag}: {type},{qufu_crop_img_url}')
        else:
            monitor_print(f'---kit_ocr_image_by_eas_result_none: {type},{qufu_crop_img_url}')

        return None
# 获取当前设备分辨率
def get_now_displayinfo():
    orientation = G.DEVICE.display_info["orientation"]
    resolution = (2400, 1350)
    if orientation in (1, 3):
        resolution = (1350, 2400)
    return resolution


def detect_horizontal_lines(img, 
                           angle_threshold=5, 
                           y_variation=3,
                           min_length_ratio=0.2,
                           canny_low=50,
                           canny_high=150):
    """
    优化版横线检测算法
    
    参数：
    img : 输入图像 (BGR格式)
    angle_threshold : 横线最大允许角度偏差(度)
    y_variation : Y坐标最大允许变化量(像素)
    min_length_ratio : 线段最小长度比例(相对于图像宽度)
    canny_low : Canny低阈值
    canny_high : Canny高阈值
    """
    # 1. 预处理增强
    height, width = img.shape[:2]
    
    # 自适应高斯模糊
    kernel_size = int(width / 200) * 2 + 1  # 根据图像宽度自动调整
    blurred = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    
    # 2. 边缘检测优化
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, canny_low, canny_high)
    
    # 3. 形态学强化横线特征
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    enhanced = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, horizontal_kernel)
    
    # 4. 动态参数计算
    min_line_length = int(width * min_length_ratio)
    max_line_gap = int(min_line_length * 0.3)
    
    # 5. 霍夫变换检测
    lines = cv2.HoughLinesP(enhanced, 
                          rho=1,
                          theta=np.pi/180,
                          threshold=50,
                          minLineLength=min_line_length,
                          maxLineGap=max_line_gap)
    
    horizontal_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 6. 双条件验证
            # 条件1：角度验证
            dx = x2 - x1
            if dx == 0:  # 避免除零错误
                continue
            angle = np.degrees(np.arctan(abs(y2 - y1) / abs(dx)))
            
            # 条件2：坐标变化量验证
            y_diff = abs(y1 - y2)
            
            if angle < angle_threshold and y_diff <= y_variation:
                # 归一化线段坐标（按从左到右排序）
                if x1 > x2:
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1
                horizontal_lines.append([(x1, (y1+y2)//2), (x2, (y1+y2)//2)])
    
    # 7. 后处理（合并相邻线段）
    return merge_lines(horizontal_lines, merge_threshold=width//50)

def merge_lines(lines, merge_threshold):
    """
    合并相邻线段
    """
    if not lines:
        return []
    
    # 按X坐标排序
    sorted_lines = sorted(lines, key=lambda x: x[0][0])
    merged = [sorted_lines[0]]
    
    for current in sorted_lines[1:]:
        last = merged[-1]
        (x1, y1), (x2, y2) = current
        (lx1, ly1), (lx2, ly2) = last
        
        # 合并条件：Y坐标接近且线段连续
        if abs(y1 - ly1) < merge_threshold and x1 <= lx2 + merge_threshold:
            new_line = [(min(x1, lx1), (y1 + ly1)//2), 
                       (max(x2, lx2), (y2 + ly2)//2)]
            merged[-1] = new_line
        else:
            merged.append(current)
    
    return merged

class ImageCentralContentIdentification:
    """
    图片中心内容识别 
    :param input_img: 输入图片路径(支持jpg/png)/图片数组
    :param output_mode: 输出模式
        1 返回内容所在区域坐标
        2 返回图片数组
        3 返回保存图片地址
    :param iter_count: GrabCut迭代次数(默认5)
    :param area_coords: 指定区域替换掩码区域颜色 例如: [{
        "area_list": [
            ((313,11), (362,62))
        ],
        "area_color": (255,255,255)
    }]
    :param transparency_threshold: 有效内容的透明度阈值 参考值 128
        场景分类	推荐阈值	适用情况	辅助判断方法
        清晰边缘	128	高对比度前景背景分离	直方图双峰明显
        半透明区域	50-100	需要保留渐变透明度	观察alpha通道直方图分布
        抗锯齿处理	192-240	需要抑制边缘半透明像素	配合形态学操作使用
    
    """
    def __init__(self,**kwargs):
        self.input_img = kwargs.get('input_img', None)
        self.output_mode = kwargs.get('output_mode', 1)
        self.iter_count = kwargs.get('iter_count', 5)
        self.area_coords = kwargs.get('area_coords', None)
        self.transparency_threshold = kwargs.get('transparency_threshold', 128)


    def advanced_remove_background(self):
        if self.input_img is None:
            return '输入图片参数不能为空'
        if isinstance(self.input_img, str):
            img_np = cv2.imread(self.input_img)
        else:
            img_np = self.input_img
        if self.area_coords:
            for area_coord in self.area_coords:
                area_list = area_coord.get('area_list', None)
                area_color = area_coord.get('area_color', (255,255,255))
                if area_list:
                    for area in area_list:
                        if isinstance(area, str):
                            template_img_np = cv2.imread(area)
                            match_template = kit_match_in(template_img_np, img_np, threshold=0.7, is_center_pos=False)
                            if match_template:
                                img_np = self.get_mask(match_template, img_np, area_color)
                        else:
                            img_np = self.get_mask(area, img_np, area_color)
        img = cv2.pyrMeanShiftFiltering(img_np, 15, 40)
        h, w = img.shape[:2]
    
        # 自适应ROI选择（改进版）
        rect = self.adaptive_roi_selection(img)
        # 初始化GrabCut参数
        mask = np.zeros(img.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        # 分阶段GrabCut处理
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
        self.refine_with_edge(img, mask)  # 边缘引导优化
        cv2.grabCut(img, mask, None, bgd_model, fgd_model, self.iter_count, cv2.GC_EVAL)
        
        # 生成自适应alpha通道
        alpha = self.generate_alpha(mask, img)
        # 后处理修复
        alpha = self.post_process_alpha(alpha, img)
        bbox = self.get_content_bbox(alpha, threshold= self.transparency_threshold)
        if self.output_mode == 1:
            return bbox
        elif self.output_mode == 2:
            cropped_image = img_np[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            return cropped_image
        elif self.output_mode == 3:
            cropped_image = img_np[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            img_filename = f'{catch_file_name}_center_content_{str(int(time.time() * 1000000))}.jpg'
            image_path = os.path.join(ST.LOG_DIR, img_filename)
            cv2.imwrite(image_path, cropped_image)
            return image_path
    def get_mask(self, area, img, rgb):
        x1, y1 = area[0]
        x2, y2 = area[1]
        rbg = (rgb[0],rgb[2], rgb[1])
        # 遍历指定区域内的每一个像素
        for y in range(y1, y2):
            for x in range(x1, x2):
                img[y, x] = [rbg[0], rbg[1], rbg[2]]
        return img
    
    def adaptive_roi_selection(self, img):
        """ 基于显著区域检测的ROI选择 """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)
            return (max(0,x-15), max(0,y-15), min(img.shape[1],w+30), min(img.shape[0],h+30))
        else:
            h, w = img.shape[:2]
            return (int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8))
    def refine_with_edge(self, img, mask):
        """ 边缘引导的掩模优化 """
        edge_map = cv2.Canny(img, 80, 150)
        edge_mask = cv2.dilate(edge_map, np.ones((3,3)), iterations=1)
        
        # 在边缘区域保持原始图像内容
        mask[edge_mask > 0] = cv2.GC_PR_FGD
    
    def generate_alpha(self, mask, img):
        """ 生成带渐变效果的alpha通道 """
        final_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        
        # 边缘渐变处理
        distance = cv2.distanceTransform(final_mask, cv2.DIST_L2, 3)
        alpha = cv2.normalize(distance, None, 0, 255, cv2.NORM_MINMAX)
        alpha[alpha < 50] = 0  # 强背景区域
        alpha[alpha >= 200] = 255  # 强前景区域
        return alpha.astype(np.uint8)

    def post_process_alpha(self, alpha, img):
        """ 后处理优化 """
        # 连通域分析去除小杂点
        _, labels = cv2.connectedComponents(255 - alpha)
        unique, counts = np.unique(labels, return_counts=True)
        small_components = unique[counts < 500]
        alpha[np.isin(labels, small_components)] = 255
        
        # 色彩保留增强
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        alpha[(hsv[:,:,1] > 80) & (alpha < 250)] = 255  # 保留高饱和度区域
        
        # 自适应形态学处理
        kernel_size = max(1, int(min(img.shape[:2])/300))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        return cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
    def get_content_bbox(self, alpha, threshold=128):
        """
        计算内容区域边界框
        :param alpha: 透明通道矩阵
        :param threshold: 视为有效内容的透明度阈值
        :return: (top, left, bottom, right)
        """
        # 二值化处理
        _, thresh = cv2.threshold(alpha, threshold, 255, cv2.THRESH_BINARY)
        # ---- 新增：形态学开运算去除小噪点 ----
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 合并所有轮廓的边界
        min_x = w = alpha.shape[1]
        min_y = h = alpha.shape[0]
        max_x = 0
        max_y = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)
        # 处理空内容情况
        if max_x <= min_x or max_y <= min_y:
            return (0, 0, alpha.shape[0], alpha.shape[1])  # 返回全图坐标
        
        # 扩展5像素边界保证内容完整
        min_x = max(0, min_x - 5)
        min_y = max(0, min_y - 5)
        max_x = min(alpha.shape[1], max_x + 5)
        max_y = min(alpha.shape[0], max_y + 5)

        return (min_x, min_y, max_x, max_y)


def set_screen_orientation(direction = 1):
    """
    设置屏幕方向
        direction
            0 竖屏
            1 横屏

    """
    device_info = ENV.iOS_session_connect.device
    os_version = device_info["os_version"]
    monitor_task_status_v2("iOS version", os_version)
    if os_version.startswith("14"):
        os.environ.update(rotate_90="true")
    screen_width = device_info["deviceModel"]["screen_width"]
    screen_height = device_info["deviceModel"]["screen_height"]
    display_info = {"width": screen_width, "height": screen_height}
    if direction == 0:
        os.environ.update(screenWidth=str(display_info['width']), screenHeight=str(display_info['height']))
    elif direction == 1:
        os.environ.update(screenWidth=str(display_info['height']), screenHeight=str(display_info['width']))
    else:
        pass


def restartApp(gameName: str, packageName: str, sec=8):
    """
        重启游戏
        :param gameName: 游戏名称
        :param packageName: 包名
        :param sec: 启动后等待
        :return: 无
    """
    monitor_task_status_v2("重启游戏", gameName)
    system = ENV.system_type
    if system == 'android':
        stop_app(packageName)
        sleep(1)
        start_app(packageName)
    else:
        ex = None
        for _ in range(3):
            try:
                ENV.iOS_session_connect.close_app(pkg=packageName)
                sleep(1)
                ENV.iOS_session_connect.open_app(pkg=packageName)
                break
            except Exception:
                ex = traceback.format_exc()
        else:
            monitor_task_status_v2("重启游戏失败", ex)
            raise ex
    sleep(sec)

def kit_wait_touch(v, timeout=None, interval=0.5, threshold=0.7, area_pos = None, touch_time = 0.5):
    '''
    wait后并点击
    :param v: template对象
    :param timeout: 检测时长 单位秒
    :param interval: 检测间隔
    :param threshold: 相似度
    :param area_pos: 区域坐标 左上右下 例如(100, 100, 1000, 1000)
    '''
    check_pos = kit_wait_find(v, timeout, interval, threshold, area_pos)
    if check_pos:
        adc_touch(check_pos, touch_time)
    return check_pos

def kit_ocr_and_match(v, keywords = [], area_pos = None, threshold = 0.7, timeout = None):
    ''' 
    match与ocr同时检测,优先match后ocr兜底
    '''
    check_button = kit_wait_find(v, area_pos=area_pos, timeout=timeout, threshold=threshold)
    if not check_button:
        if keywords and area_pos:
            check_button = kit_ocr_checkout(area_pos, name='check_button', keywords=keywords)
            if not check_button:
                return None
    return check_button


def config_match_service_request_path():
    env = AppEnv.get_instance()
    scriptEnv = env.scriptEnv
    risk_path = ""
    launch_type = env.launchType
    if launch_type == 'localtest':
        scriptEnv = 'local'

    if (scriptEnv == 'local'):
        risk_path = "/api/predict/lingxialgo_vision_match_pre"
    elif (scriptEnv == 'pre'):
        risk_path = "/api/predict/lingxialgo_vision_match_pre"
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_match'
    else:
        risk_path = '/api/predict/lingxialgo_vision_match_pre'

    return risk_path

def createAdcTask(**kwargs):
    '''
        创建新的task任务
    '''
    host = get_env_host(ENV)
    submitTask_url = f"https://{host}/task/submitTask"
    
    default_data = {
        "gameId": '',
        "password": '',
        "taskType": '',
        "gamePlatform": '',
        'bizId': '',
        'userAccount': '',
        'taskContentType': '',
        'transferAccountName': '',
        'accountAttr': '',
        'taskStatus': '',
        'deviceInfo': '',
        'scriptId': '',
        'resultInfo': '',
        'extParams': ''
    }
    for k, v in kwargs.items():
        default_data[k] = v
    monitor_print(f'---create_adc_task_data: {default_data}')
    monitor_print(f'---create_adc_task_url: {submitTask_url}')
    session = requests.session()
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36"}
    session.headers.update(headers)
    try:
        res = session.get(submitTask_url, params=default_data, verify=False)
        monitor_print(f"---create_adc_task_response: {res.text}")
        monitor_print(f"---create_adc_task_response_code: {res.status_code}")
        if res.status_code == 200:
            res_json = res.json()
            monitor_print(f"---create_adc_task_response_json: {res_json}")
            if res_json['success']:
                try:
                    taskId = res_json['data']['taskId']
                    return taskId
                except Exception as e:
                    monitor_print(f'---create_adc_task_data_error: {sys.exc_info()}')
    except Exception as e:
        monitor_print(f'---create_adc_task_error: {sys.exc_info()}')
    return None

def GetAdcTaskStatus(taskId):
    '''
        获取task任务状态
    '''
    host = get_env_host(ENV)
    submitTask_url = f"https://{host}/task/getTaskStatus"
    default_data = {
        "taskId": taskId
    }
    monitor_print(f'---get_adc_task_data: {default_data}')
    monitor_print(f'---get_adc_task_url: {submitTask_url}')
    session = requests.session()
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36"}
    session.headers.update(headers)
    try:
        res = session.get(submitTask_url, params=default_data, verify=False)
        monitor_print(f"---get_adc_task_response: {res.text}")
        monitor_print(f"---get_adc_task_response_code: {res.status_code}")
        if res.status_code == 200:
            res_json = res.json()
            monitor_print(f"---get_adc_task_response_json: {res_json}")
            if res_json['success']:
                try:
                    data = res_json['data']
                    return data
                except Exception as e:
                    monitor_print(f'---get_adc_task_data_error: {sys.exc_info()}')
    except Exception as e:
        monitor_print(f'---get_adc_task_error: {sys.exc_info()}')
    return None

def kitGetQueryTask(taskId):
    '''
        获取task任务callback数据
    '''
    host = kit_get_server_host(ENV)
    submitTask_url = f"http://{host}/task/queryTask"
    the_time = int(time.time() * 1000)
    default_data = {
        "taskId": taskId, 
        "timestamp": the_time
    }
    monitor_print(f'---kitGetQueryTask_data: {default_data}')
    monitor_print(f'---kitGetQueryTask_url: {submitTask_url}')
    try:
        response = requests.post(submitTask_url, json=default_data)
        monitor_print(f"---kitGetQueryTask_response: {response.text}")
        monitor_print(f"---kitGetQueryTask_response_code: {response.status_code}")
        if response.status_code == 200:
            res_json = response.json()
            monitor_print(f"---kitGetQueryTask_response_json: {res_json}")
            if res_json['success']:
                try:
                    data = res_json['result']
                    return data
                except Exception as e:
                    monitor_print(f'---kitGetQueryTask_data_error: {sys.exc_info()}')
    except Exception as e:
        monitor_print(f'---kitGetQueryTask_error: {sys.exc_info()}')
    return None

def kit_get_server_host(env, custom_env_type=None, need_prefix=False):
    '''
        获取服务端host
    '''
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
        elif scriptEnv == 'daily':
            host = 'http://lingxi-adc-task-sever.taobao.net'
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
        elif scriptEnv == 'daily':
            host = 'lingxi-adc-task-sever.taobao.net'
        else:
            host = 'pre-lingxi-adc-task-server.alibaba-inc.com'

    return host
def kit_get_latest_file(prefix = 'adc_result', suffix='.jpg', pick="max"):
    """
    在 dir_path 下找：文件名以 prefix 开头（可选再限制 suffix 结尾）
    用 '_' 分割，最后一段当作时间戳(整数)排序，返回最大/最小的文件名(Path)。
    pick: "max" 或 "min"
    """
    p = Path(ST.LOG_DIR)

    items = []
    for f in p.iterdir():
        if not f.is_file():
            continue
        name = f.name
        if not name.startswith(prefix):
            continue
        if suffix and not name.endswith(suffix):
            continue

        last = name.rsplit("_", 1)[-1]              # '_' 最后一段
        ts_part = last.rsplit(".", 1)[0]            # 去掉扩展名（如果有）
        if not ts_part.isdigit():                   # 时间戳必须是纯数字
            continue

        items.append((int(ts_part), f))

    if not items:
        return None
    keyfunc = max if pick == "max" else min
    return keyfunc(items, key=lambda x: x[0])[1]    # 返回 Path

def getAdcMarkettingServerHost(custom_env_type=None, need_prefix=False):
    '''
        获取服务端marketting-server对应host
    
        :param custom_env_type: 强制设置环境
        :param need_prefix: 是否需要前缀
    '''

    scriptEnv = ENV.scriptEnv
    if custom_env_type is not None:
        scriptEnv = custom_env_type
    host=""

    if need_prefix:
        if (scriptEnv == 'local'):
            # host = 'pre-adc-pc.alibaba-inc.com'
            host = 'https://pre-lingxi-adc-marketting-server.alibaba-inc.com'
        elif(scriptEnv == 'pre'):
            host = 'https://pre-lingxi-adc-marketting-server.alibaba-inc.com'
        elif(scriptEnv == 'prod'):
            host = 'https://lingxi-adc-marketting-server.alibaba-inc.com'
        else:
            host = 'https://pre-lingxi-adc-marketting-server.alibaba-inc.com'
    else:
        if (scriptEnv == 'local'):
            # host = 'pre-adc-pc.alibaba-inc.com'
            host = 'pre-lingxi-adc-marketting-server.alibaba-inc.com'
        elif(scriptEnv == 'pre'):
            host = 'pre-lingxi-adc-marketting-server.alibaba-inc.com'
        elif(scriptEnv == 'prod'):
            host = 'lingxi-adc-marketting-server.alibaba-inc.com'
        else:
            host = 'pre-lingxi-adc-marketting-server.alibaba-inc.com'

    return host

def AdcMarkettingServerApiRequest(method = "post", api_path = "", request_params = {}, need_prefix=False, custom_env_type=None, max_retry_count=3):
    '''
        服务端marketting-server接口请求
    '''
    host = getAdcMarkettingServerHost(custom_env_type = custom_env_type,need_prefix = need_prefix)
    if need_prefix:
        request_url = f"{host}{api_path}"
    else:
        request_url = f"{host}"
    monitor_print(f"---AdcMarkettingServerApiRequest_url: {request_url}")
    monitor_print(f"---AdcMarkettingServerApiRequest_data: {request_params}")
    for res_count in range(max_retry_count):
        try:
            if method == 'post':
                response = requests.post(request_url, json=request_params)
            else:
                response = requests.get(request_url, params=request_params)
            monitor_print(f"---AdcMarkettingServerApiRequest_response {res_count}: {response.text}")
            monitor_print(f"---AdcMarkettingServerApiRequest_code {res_count}: {response.status_code}")
            if response.status_code == 200:
                res_json = response.json()
                monitor_print(f"---AdcMarkettingServerApiRequest_json {res_count}: {res_json}")
                if res_json['success']:
                    try:
                        data = res_json['result']
                        return data
                    except Exception as e:
                        monitor_print(f'---AdcMarkettingServerApiRequest_data_error {res_count}: {sys.exc_info()}')
        except Exception as e:
            monitor_print(f'---AdcMarkettingServerApiRequest_error {res_count}: {sys.exc_info()}')
        
    return None


def AdcServerApiRequest(method = "post", api_path = "", request_params = {}, need_prefix=False, custom_env_type=None, max_retry_count=3):
    '''
        服务端server接口请求
    '''
    host = kit_get_server_host(ENV, custom_env_type = custom_env_type,need_prefix = need_prefix)
    if need_prefix:
        request_url = f"{host}{api_path}"
    else:
        request_url = f"{host}"
    monitor_print(f"---AdcServerApiRequest_url: {request_url}")
    monitor_print(f"---AdcServerApiRequest_data: {request_params}")
    for res_count in range(max_retry_count):
        try:
            if method == 'post':
                response = requests.post(request_url, json=request_params)
            else:
                response = requests.get(request_url, params=request_params)
            monitor_print(f"---AdcServerApiRequest_response {res_count}: {response.text}")
            monitor_print(f"---AdcServerApiRequest_code {res_count}: {response.status_code}")
            if response.status_code == 200:
                res_json = response.json()
                monitor_print(f"---AdcServerApiRequest_json {res_count}: {res_json}")
                if res_json['success']:
                    try:
                        data = res_json['result']
                        return data
                    except Exception as e:
                        monitor_print(f'---AdcServerApiRequest_data_error {res_count}: {sys.exc_info()}')
        except Exception as e:
            monitor_print(f'---AdcServerApiRequest_error {res_count}: {sys.exc_info()}')
        
    return None


def compose_canvas_cv(src_cv,
                      canvas_size,
                      img_box,
                      text = None,
                      text_pos = None,
                      font_size = None,
                      canvas_color = (0,0,0,0),
                      align='center',
                      text_color=(255, 255, 255, 255)):
    """
    src_cv        : OpenCV 读入的图像 (BGR / BGRA)
    canvas_size   : (width, height)
    img_box       : (x1, y1, x2, y2) -> 把 src_cv 缩放后贴进去
    text          : 要写的文字（支持换行）
    text_pos      : 文字左上角 (x, y)
    font_path     : 字体文件路径；None 则 Pillow 默认字体
    font_size     : 字号
    canvas_color  : RGBA 画布颜色，默认全透明
    text_color    : RGBA 文字颜色，默认纯白
    return        : 合成完毕后的 BGRA numpy 数组
    """
    font_path =ENV.rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'
    canvas_w, canvas_h = canvas_size
    r, g, b, a = canvas_color
    # 新建透明 BGRA 画布
    canvas = np.full((canvas_h, canvas_w, 4), (b, g, r, a), dtype=np.uint8)

    # ---- 1. 处理并放置图片 ----
    x1, y1, x2, y2 = img_box
    box_w, box_h   = x2 - x1, y2 - y1

    # 若 src 没有 alpha，先加一个不透明 alpha
    if src_cv.shape[2] == 3:
        src_cv = cv2.cvtColor(src_cv, cv2.COLOR_BGR2BGRA)

    resized = cv2.resize(src_cv, (box_w, box_h), interpolation=cv2.INTER_LINEAR)

    # 贴到画布（简单拷贝，因为我们都在 BGRA，且画布背景透明）
    canvas[y1:y2, x1:x2] = resized
    if text:
        # ---- 2. 写文字：转 PIL 方便用 truetype 字体 ----
        canvas_pil = cv_image_to_pil(canvas)  # BGRA -> PIL RGBA
        draw = ImageDraw.Draw(canvas_pil)
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        if align == 'center':
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (canvas_w - tw) // 2
            y =  th // 2
            text_pos = (x, text_pos[1] + y)
        draw.multiline_text(text_pos, text, font=font, fill=text_color, align = align)
        # ---- 3. PIL 回到 OpenCV ----
        canvas = pil_to_cv_image(canvas_pil)   # 转回 BGRA numpy


    return canvas

def draw_text_center(draw: ImageDraw.Draw,
                     canvas_size,
                     text,
                     font,
                     fill=(0, 0, 0, 255)):
    """把 text 居中画到整个画布（多行也居中）。"""
    cw, ch = canvas_size
    # Pillow ≥ 8.0 有 multiline_textbbox，可一次得到多行 bbox
    try:
        bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:               # 老版本退化到手动累加
        lines = text.splitlines() or [""]
        tw = max(font.getlength(line) for line in lines)
        th = sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)
    
    x = (cw - tw) // 2
    draw.multiline_text((x, y), text, font=font, fill=fill, align="center")



def pil_to_cv_image(img_pil: Image.Image) -> np.ndarray:
    """Pillow Image (RGBA/RGB) -> numpy BGRA/BGR"""
    img_rgba = img_pil.convert("RGBA")
    cv_img = cv2.cvtColor(np.array(img_rgba), cv2.COLOR_RGBA2BGRA)
    return cv_img

def cv_image_to_pil(img_cv: np.ndarray) -> Image.Image:
    """BGR/BGRA numpy -> Pillow Image (RGBA)"""
    if img_cv.shape[2] == 3:
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_cv).convert("RGBA")
    else:                              # 4 通道 BGRA
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGRA2RGBA)
        pil_img = Image.fromarray(img_cv)
    return pil_img