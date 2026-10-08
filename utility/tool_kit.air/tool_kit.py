
import difflib
import time
import traceback
from PIL import Image, ImageDraw, ImageFont,ImageStat
import numpy as np
import requests

from airtest.core.api import *
import cv2

using("../utility/api.air")
from api import *
using("../utility/monitor.air")
from monitor import *
using("../utility/phase.air")
from phase import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/mask.air")
from mask import *

using("../utility/swipe.air")
from swipe import *

using("../utility/image.air")
from image import *

using("../utility/ocr.air")
from ocr import *

using("../utility/upload.air")
from upload import *

from airtest import aircv
png_file_name = 'adc_result'
catch_file_name = 'adc_catch'
tmp_file_name = 'tmp'
ENV = AppEnv.get_instance()

def streamSnapshot(filename = None, msg = None, is_try = True):
    try:
        device = ENV.device
        data = device.screen_proxy.get_frame_from_stream()
        frame = aircv.utils.string_2_img(data)
        
        frame = resize_by_max(frame, 2400)
        if filename is not None:
            path = os.path.join(ST.LOG_DIR, filename)
            cv2.imwrite(path, frame)
        return frame
    except Exception as e:
        error_traceback = traceback.format_exc()
        monitor_print(f'---kit stream snapshot error({ENV.gameDir}): {error_traceback}')
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

def snapshotImg(name, type_name = tmp_file_name, mask = None, LT = None, RB = None, path=False):
    """
        截图
    """
    img_filename = f'{type_name}_{name}_{str(int(time.time() * 1000000))}.jpg'
    streamSnapshot(filename = img_filename, msg="get a snapshot.")
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
                pos = kit_match_in(file_np, screen, threshold)
                if pos:
                    if area_pos is not None:
                        pos = (pos[0] + area_pos[0], pos[1] + area_pos[1])
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
        
def kit_match_in(small_img_np, main_img_np = None, threshold=0.57):
    small_img_gray = cv2.cvtColor(small_img_np, cv2.COLOR_BGR2GRAY)
    if main_img_np is not None:
        main_img_gray = cv2.cvtColor(main_img_np, cv2.COLOR_BGR2GRAY)
    else:
        file_name = f'{catch_file_name}_kit_match_in_{str(int(time.time()*1000000))}.jpg'
        snapshot(filename=file_name, msg="get a snapshot.")
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
    if max_val > threshold:
        return pos
    else:
        return None

# ocr某个区域
def ocr_keyword_with_img_np(ocr_region, remote_ocr_type=(2, 1, 3), fault_tolerant_map={}):
    img_path = snapshotImg('ocr', catch_file_name,LT=(ocr_region[0], ocr_region[1]),RB=(ocr_region[2], ocr_region[3]),path=True)
    for type in remote_ocr_type:
        if type in [2, 1]:
            res = ocr_chinese_by_eas(img_path)
        else:
            res = ocr_num_by_eas(img_path)
        if res:
            ocr_res = [(item["txts"], ((item["box"][0][0]+item["box"][1][0])/2+ocr_region[0], (item["box"][0][1]+item["box"][1][1])/2
                                       + ocr_region[1])) for item in res]
            if ocr_res:
                for item in ocr_res:
                    if item[0] in fault_tolerant_map:
                        item[0] = fault_tolerant_map[item[0]]
                return ocr_res
    return []


def ocr_keyword_return_pos_with_image_np(img, remote_ocr_type=(2, 1), fault_tolerant_map={}):

    img_path = None
    if isinstance(img, str):
        if img.startswith("http"):
            # 从URL获取图像内容
            response = requests.get(img)
            img_path = os.path.join(ST.LOG_DIR, f"{catch_file_name}_ocr_{str(int(time.time() * 1000000))}.jpg")
            with open(img_path, "wb") as f:
                f.write(response.content)
        else:
            img_path = img
    elif isinstance(img, np.ndarray):
        img_path = os.path.join(ST.LOG_DIR, f"{catch_file_name}_ocr_{str(int(time.time() * 1000000))}.jpg")
        cv2.imwrite(img_path, img)
    elif isinstance(img, Image.Image):
        img_path = os.path.join(ST.LOG_DIR, f"{catch_file_name}_ocr_{str(int(time.time() * 1000000))}.jpg")
        img.save(img_path)
    if not img_path:
        return []
    # for type in remote_ocr_type:
    res = ocr_chinese_by_eas(img_path)
    if res:
        ocr_res = [(item["txts"], ((item["box"][0][0]+item["box"][1][0])/2, (item["box"][0][1]+item["box"][1][1])/2)) for item in res]
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
def long_snapshot_comp(img_np_list, name, one_row_count = 1, max_rows_count = 6, spacing = 10, spacing_color = (196, 175, 153), bg_path = None, title_info = None):
    if img_np_list != []:
        
        combine_imgs = combine_images(img_np_list, one_row_count = one_row_count, max_rows_count = max_rows_count, spacing = spacing, spacing_color = spacing_color)
        for idx, image in enumerate(combine_imgs):
            if bg_path and title_info:
                combine_final_image =  combine_images_with_bg_and_title(image, bg_path, (10,10,10,10), sub_title_info = title_info)
                write_path = os.path.join(ST.LOG_DIR, f"{png_file_name}_{name}_{idx}_" + str(int(time.time()*1000000)) + ".jpg")
                cv2.imwrite(write_path, combine_final_image)
            else:
                write_path = os.path.join(ST.LOG_DIR, f"{png_file_name}_{name}_{idx}_" + str(int(time.time()*1000000)) + ".jpg")
                cv2.imwrite(write_path, image)

       

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
        while swipe_status:
            if count > 100:
                lx_break_runloop(desc='长截图失败失败')
                break
            if self.try_snapshot_func:
                for try_count in range(5):
                    snap_file_name = f"{catch_file_name}_swipe_{self.combine_part_name}_{count}_{str(int(time.time() * 1000000))}.jpg"
                    snapshot(filename=snap_file_name, msg="get a snapshot.")
                    img_status = self.try_snapshot_func(snap_file_name)
                    if not img_status:
                        break
                    else:
                        monitor_task_status(ENV, f"{self.combine_part_name} 截图校验检测到异常", "重新截取图片")
            else:
                snap_file_name = f"{catch_file_name}_swipe_{self.combine_part_name}_{count}_{str(int(time.time() * 1000000))}.jpg"
                snapshot(filename=snap_file_name, msg="get a snapshot.")
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
                    is_same = lx_match_in(judge_bottom_img, now_bottom_img)
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
                        monitor_print(f'---{self.combine_part_name} swipe snapshot ocr result is none')
                    # print("\033[1;33m", f"最后名称: {last_img_ocr_name}>".center(100, "="), "\033[0m", sep="")
                    # if ocr_result:
                elif self.same_type in [6, 7, 8]:
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
                                    else:
                                        crop_imgs.clear()
                            else:
                                del crop_imgs[-1]
                else:
                    judge_bottom_img = crop_pos_image_from_snapshot(snap_file_name, f"tmp_judge_bottom_img_{self.combine_part_name}.jpg", self.check_bottom_start,self.check_bottom_end, False)
            if self.crop_data:
                # if count > 0:
                #     first_index = count_x * (count_y - 1)
                # else:  
                first_index = 0
                end_index = None
                if self.img_num:
                    if not swipe_status:
                        # 余数 
                        remainder = self.img_num % all_num
                        if count_x != 1:
                            # 结束前空格子数
                            blank = count_x - (remainder % count_x)
                        else:
                            blank = 0
                        first_index = all_num - remainder - blank
                        end_index = all_num - blank - 1
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
                    
                    crop_start_pos_x = origin_x + (column_index-1) * (interval_x+width)
                    crop_start_pos_y = origin_y + (row_index-1) * (interval_y+heigt)
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
                                    ssim_compare = compare_ssim_func(result_img, img)
                                    if ssim_compare:
                                        is_continue = True
                                        break
                                if is_continue:
                                    continue
                    if self.check_normal_image_func is not None:
                        check_pos = (crop_start_pos_x + width / 2, crop_start_pos_y + heigt / 2)
                            
                        verify_func = self.check_normal_image_func(result_img, self.combine_part_name, check_pos)
                        
                        if verify_func:
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
                if self.same_type not in [6, 7, 8]:
                # dwarf_swipe(swipe_start_pos, swipe_end_pos)
                    if self.swipe_durations:
                        swipe_duration(self.swipe_start_pos,self.swipe_end_pos, duration = self.swipe_durations)
                    else:
                        swipe_with_seperate(startPos=self.swipe_start_pos,endPos=self.swipe_end_pos)
                else:
                    snap_befor_file_name = f"{catch_file_name}_{self.combine_part_name}_befor_swipe_{count}_{str(int(time.time() * 1000000))}.jpg"
                    if self.swipe_durations:
                        swipe_duration(self.swipe_start_pos, self.swipe_end_pos, sleep_time=0, duration = self.swipe_durations, snapshot_name = snap_befor_file_name)
                    else:
                        swipe_duration(self.swipe_start_pos, self.swipe_end_pos, sleep_time=0, snapshot_name = snap_befor_file_name)
                    check_bottom_file_name = f"{catch_file_name}__{self.combine_part_name}_befor_swipe_check_{count}_{str(int(time.time() * 1000000))}.jpg"
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
            count += 1
        if self.last_repeat_check:
            if len(crop_imgs) >= 2:
                last_first_line, last_first_img, last_first_central_area = kit_check_grap_edges(crop_imgs[-1])
                last_second_line, last_second_img, last_second_central_area = kit_check_grap_edges(crop_imgs[-2])
                last_first_central_img = crop_imgs[-1][last_first_central_area['min_y']:last_first_central_area['max_y'], last_first_central_area['min_x']:last_first_central_area['max_x']]
                last_second_central_img = crop_imgs[-2][last_second_central_area['min_y']:last_second_central_area['max_y'], last_second_central_area['min_x']:last_second_central_area['max_x']]
                check_img = kit_match_in(last_first_central_img, last_second_central_img, threshold = 0.9)
                if check_img:
                    crop_imgs = crop_imgs[:-1]
        return crop_imgs

#默认支持纵向滑动
def swipe_duration(p1, p2, duration=0.5, steps=5, sleep_time = 0.5, snapshot_name = False):
    # actionDevice.touch_proxy.touch(p1)
    device = ENV.device
    from_x, from_y = p1
    to_x, to_y = p2
    # swipe_along_func([p1, (to_x, to_y)], duration = duration)
    device.touch_proxy.swipe_along([(from_x, from_y), (to_x, to_y-2), (to_x, to_y)], duration=duration)
    if snapshot_name:
        snapshot(filename = snapshot_name, msg="get a snapshot.")
        time.sleep(0.5)
    if sleep_time != 0:
        time.sleep(sleep_time)

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
def check_grap_edges(img):
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
        # 二次校验 判断是否存在内容 增强检测
        second_check = ocr_keyword_return_pos_with_image_np(img)
        if second_check:
            return second_check
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


# 账号总览
def accentOverview(img_list, overview_list,template_path, target_area, spacing=0):
    '''
        img_comp_ratio: 图片压缩比例
    
    '''
    monitor_task_status_v2("账号总览合成", "预处理阶段")
    try:
        template_image = cv2.imread(template_path)
        template_image_size = (template_image.shape[1], template_image.shape[0])
        # 创建一个新的图片用于放置小图
        overlay = Image.new('RGBA', template_image_size, (0, 0, 0, 0))
        for overview in overview_list:
            rename_img = image_write_text(template_image, text = str(overview['value']), text_color=(233, 220, 228),font_size = 30, textPoint = overview['pos'])
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
        for img_one_list in img_list:
            for img in img_one_list:
                if img is None:
                    continue
                # 打开并获取单个图片的尺寸
                img_width, img_height = img.shape[1],img.shape[0]
                if img_height > max_height:
                    max_height = img_height
                # 如果当前位置加上图片尺寸超过目标区域，则换行
                if current_x + img_width > target_right:
                    current_x = target_left  # 重置x坐标到起始位置
                    current_y += max_height + spacing  # 增加y坐标
                    max_height = 0
                
                wirte_path_img_small = os.path.join(ST.LOG_DIR, f"tmp_{str(int(time.time()*1000000))}.jpg")
                cv2.imwrite(wirte_path_img_small, img)
                # 打开小图片
                thumbnail = Image.open(wirte_path_img_small).convert('RGBA')
                # 粘贴图片到背景图
                overlay.paste(thumbnail, (current_x, current_y))
                # 更新x坐标准备粘贴下一张图片
                current_x += img_width + spacing
        # 将overlay和模版合并
        composed_image = Image.alpha_composite(template_img_np, overlay)
        # 保存结果图片
        # 转换为无透明度的 RGB 格式
        composed_image_rgb = composed_image.convert("RGB")
        composed_image_rgb.save(os.path.join(ST.LOG_DIR, f"adc_result_overview_0.jpg"),"JPEG")
    except Exception as e:
        error_traceback = traceback.format_exc()
        monitor_task_status(ENV,"账号总览合成失败", f"{error_traceback}")

    monitor_task_status_v2("账号总览合成-结束", "完成")

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