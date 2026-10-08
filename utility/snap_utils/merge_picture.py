import numpy as np
import cv2
import time
import re

from utility.biz_utils.biz_utils import monitor_task_status_v2,snapshot_write,monitor_catch,\
    monitor_print,snapshot_matchAll
from utility.app.service.adc_ocr import ocr_image_by_eas
from utility.base.adc_environment import AppEnv
from utility.biz_utils.LLM import remote_ds_r1_reasoning_copy, parse_model_output_to_json_copy
from PIL import Image, ImageDraw, ImageFont, ImageStat
from utility.app.service.adc_oss import upload_jym_oss_with_pathes

# from utility.biz_utils.base_module import *
from airtest.core.api import Template,ST, using







class long_snap_picture(object):
    def __init__(self, scale_list = [0.2, 0.175, 0.15, 0.125, 0.1, 0.08, 0.05,0.02], match =0.95):
        self.scale_list = scale_list
        self.match = match

    def smooth_concat_vertical(self, img1, img2, overlap=20):
        """
        gpt生成
        将 img1 和 img2 在垂直方向拼接，同时在交界的 overlap 区域做平滑处理
        img1: 上半部分 (H1,W,C)
        img2: 下半部分 (H2,W,C)
        overlap: 交界平滑像素高度
        """
        # 确保数据类型为 float32 （混合时避免溢出）
        img1 = img1.astype(np.float32)
        img2 = img2.astype(np.float32)

        if overlap > 0:
            # 上图的处理部分（最后 overlap 行）
            blend_top = img1[-overlap:, :, :]
            # 下图的处理部分（最前 overlap 行）
            blend_bottom = img2[:overlap, :, :]

            # 创建渐变权重 alpha: (overlap, 1, 1)
            alpha = np.linspace(1, 0, overlap).reshape(-1, 1, 1)

            # 混合
            blended = blend_top * alpha + blend_bottom * (1 - alpha)

            # 组合拼接
            result = np.vstack([
                img1[:-overlap, :, :],
                blended,
                img2[overlap:, :, :]
            ])
        else:
            # 没有平滑
            result = np.vstack([img1, img2])

        return np.clip(result, 0, 255).astype(np.uint8)


    def merge_with_param(self, img1, img2, roi_scale):
        img1 = img1.copy()
        img2 = img2.copy()
        h1, w1, _ = img1.shape
        h2, w2, _ = img2.shape
        if w1 != w2:
            raise Exception("Image merge: different width")
        roi_y = int(h2 * roi_scale)
        roi = img1[(h1 - roi_y):h1, :, :]
        # # 保存图像
        # import time
        # time = time.time()
        # cv2.imwrite(f"./testimage/roi_{time}.png", roi)
        # print(f"roi_{time}.png保存成功")
        
        res = cv2.matchTemplate(img2, roi, cv2.TM_CCOEFF_NORMED)
        timeStamp = str(int(time.time() * 10 ** 6))
        cv2.imwrite(ST.LOG_DIR + f"/adc_catch_roi_{timeStamp}.jpg", roi)
        # snapshot_write(write_name='catch_roi',image=roi)

        # 获取左上角坐标
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        monitor_task_status_v2("长截图模版匹配结果",f"模版匹配的最大值{max_val}, 坐标为：{max_loc}")
        # print(f"模版匹配的最大值{max_val}, 坐标为：{max_loc}")
        std = np.std(roi)
        if std < 10:
            max_val = self.match
        cut_point = (max_loc[0], max_loc[1] + roi_y)
        img = self.smooth_concat_vertical(img1, img2, cut_point[1])
        # img = np.vstack((img1, img2[cut_point[1]:h2, :, :]))
        return img, max_val

    def img_merge(self, img1, img2, merge=True):
        scale_list = self.scale_list
        match = self.match
        img_list = []
        score_list = []
        print("开始进行图像拼接")
        
        if merge:
            for idx in range(len(scale_list)):
                img, score = self.merge_with_param(img1, img2, scale_list[idx])
                # img_list.append(img)
                # score_list.append(score)
                if score > match:
                    break
                # 处理找不到的情况
                if idx == len(scale_list) - 1:
                    img = np.vstack((img1, img2))
        else:
            img = np.vstack((img1, img2))
        return img

    def image_merge(self, img_list, name, merge=True, is_read = False):
        """
        :param name: 图像保存路径
        :param merge: 是否进行长截图操作
        :param is_read: True 读取图片,传入的是路径，False 传入的是图像numpy
        :return: 图像路径名称
        """
        name = name
        if len(img_list) < 2:
            if is_read:
                cv2.imwrite(name, cv2.imread(img_list[0]))
            else:
                cv2.imwrite(name, img_list[0])
        else:
            img1 = img_list[0]
            for idx, img in enumerate(img_list[1:], start=1):
                if idx == 1:
                    if is_read:
                        img1 = cv2.imread(img1)
                        img = cv2.imread(img)
                    img1 = self.img_merge(img1, img, merge)
                    # img1 = self.img_merge(cv2.imread(img1), cv2.imread(img), merge)
                else:
                    if is_read:
                        img = cv2.imread(img)
                    # img1 = self.img_merge(img1, cv2.imread(img), merge)
                    img1 = self.img_merge(img1, img, merge)
            img_merge = img1
            cv2.imwrite(name, img_merge)
        return name



class LongSnapPicturev2(object):
    # 相比
    def __init__(self, scale_list = [0.2, 0.175, 0.15, 0.125, 0.1, 0.08, 0.05,0.02], match =0.95):
        self.scale_list = scale_list
        self.match = match

    def smooth_concat_vertical(self, img1, img2, overlap=20):
        """
        gpt生成
        将 img1 和 img2 在垂直方向拼接，同时在交界的 overlap 区域做平滑处理
        img1: 上半部分 (H1,W,C)
        img2: 下半部分 (H2,W,C)
        overlap: 交界平滑像素高度
        """
        # 确保数据类型为 float32 （混合时避免溢出）
        img1 = img1.astype(np.float32)
        img2 = img2.astype(np.float32)

        if overlap > 0:
            # 上图的处理部分（最后 overlap 行）
            blend_top = img1[-overlap:, :, :]
            # 下图的处理部分（最前 overlap 行）
            blend_bottom = img2[:overlap, :, :]

            # 创建渐变权重 alpha: (overlap, 1, 1)
            alpha = np.linspace(1, 0, overlap).reshape(-1, 1, 1)

            # 混合
            blended = blend_top * alpha + blend_bottom * (1 - alpha)

            # 组合拼接
            result = np.vstack([
                img1[:-overlap, :, :],
                blended,
                img2[overlap:, :, :]
            ])
        else:
            # 没有平滑
            result = np.vstack([img1, img2])

        return np.clip(result, 0, 255).astype(np.uint8)


    def merge_with_param(self, img1, img2, roi_scale, cut_width):
        img1 = img1.copy()
        img2 = img2.copy()
        h1, w1, _ = img1.shape
        h2, w2, _ = img2.shape
        if w1 != w2:
            raise Exception("Image merge: different width")
        roi_y = int(h2 * roi_scale)
        roi = img1[(h1 - roi_y):h1, 0:cut_width, :]
        # # 保存图像
        # import time
        # time = time.time()
        # cv2.imwrite(f"./testimage/roi_{time}.png", roi)
        # print(f"roi_{time}.png保存成功")
        
        res = cv2.matchTemplate(img2, roi, cv2.TM_CCOEFF_NORMED)
        timeStamp = str(int(time.time() * 10 ** 6))
        cv2.imwrite(ST.LOG_DIR + f"/adc_catch_roi_{timeStamp}.jpg", roi)
        # snapshot_write(write_name='catch_roi',image=roi)

        # 获取左上角坐标
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        monitor_task_status_v2("长截图模版匹配结果",f"模版匹配的最大值{max_val}, 坐标为：{max_loc}")
        # print(f"模版匹配的最大值{max_val}, 坐标为：{max_loc}")
        std = np.std(roi)
        if std < 10:
            max_val = self.match
        cut_point = (max_loc[0], max_loc[1] + roi_y)
        img = self.smooth_concat_vertical(img1, img2, cut_point[1])
        # img = np.vstack((img1, img2[cut_point[1]:h2, :, :]))
        return img, max_val

    def img_merge(self, img1, img2, merge=True, cut_width = None):
        scale_list = self.scale_list
        match = self.match
        img_list = []
        score_list = []
        print("开始进行图像拼接")
        
        if merge:
            for idx in range(len(scale_list)):
                img, score = self.merge_with_param(img1, img2, scale_list[idx], cut_width)
                # img_list.append(img)
                # score_list.append(score)
                if score > match:
                    break
                # 处理找不到的情况
                if idx == len(scale_list) - 1:
                    img = np.vstack((img1, img2))
        else:
            img = np.vstack((img1, img2))
        return img

    def image_merge(self, img_list, name, cut_width = None, merge=True, is_read = False):
        """
        :param name: 图像保存路径
        :param merge: 是否进行长截图操作
        :param is_read: True 读取图片,传入的是路径，False 传入的是图像numpy
        :return: 图像路径名称
        """
        name = name
        if len(img_list) < 2:
            if is_read:
                cv2.imwrite(name, cv2.imread(img_list[0]))
            else:
                cv2.imwrite(name, img_list[0])
        else:
            img1 = img_list[0]
            for idx, img in enumerate(img_list[1:], start=1):
                if idx == 1:
                    if is_read:
                        img1 = cv2.imread(img1)
                        img = cv2.imread(img)
                    img1 = self.img_merge(img1, img, merge, cut_width = cut_width)
                    # img1 = self.img_merge(cv2.imread(img1), cv2.imread(img), merge)
                else:
                    if is_read:
                        img = cv2.imread(img)
                    # img1 = self.img_merge(img1, cv2.imread(img), merge)
                    img1 = self.img_merge(img1, img, merge, cut_width)
            img_merge = img1
            cv2.imwrite(name, img_merge)
        return name


class long_snap_picturev2_fei(object):
    def __init__(self, match =0.96, min_overlap = 30):
        self.match = match
        self.min_overlap = min_overlap
    def find_vertical_overlapv2(self,img1, img2):
        """
        二分查找重叠区域，通过模板匹配查找两张竖向相邻图片的重复高度
        :param img1, img2: RGB 图片 (numpy.ndarray)
        :param min_overlap: 最小检查的重叠高度
        :param similarity: 匹配相似度阈值，1.0 表示像素级完全一致，需要自己微调
        """
        similarity= self.match
        min_overlap = self.min_overlap
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        assert w1 == w2, "两张图宽度必须一致"

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY).astype(np.float32)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY).astype(np.float32)

        max_check = min(h1, h2)
        lo, hi = min_overlap, max_check
        best_overlap = 0

        while lo <= hi:
            mid = (lo + hi) // 2
            part1 = gray1[h1-mid:h1, :]

            # max_val = cv2.matchTemplate(part1, gray2, cv2.TM_CCOEFF_NORMED).max()
            max_val = cv2.matchTemplate(gray2, part1, cv2.TM_CCOEFF_NORMED).max()
            if max_val >= similarity:
                best_overlap = mid
                lo = mid + 1  # 继续找更大的
                # similarity = max_val
            else:
                # lo = mid + 1
                hi = mid - 1  # 缩小范围

        print("best_overlap:",best_overlap)
        return best_overlap
    

    def find_vertical_overlapv3(self, img1, img2):
        similarity= self.match
        min_overlap = self.min_overlap

        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        assert w1 == w2, "宽度必须一致"

        g1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        max_check = min(h1, h2)
        for overlap in range(max_check, min_overlap, -1):
            rows1 = g1[h1-overlap:h1, :].ravel()
            rows2 = g2[0:overlap, :].ravel()

            # 归一化互相关
            corr = np.corrcoef(rows1, rows2)[0, 1]
            if corr >= similarity:
                print("best_overlap:",overlap)
                return overlap
        return 0

    def image_merge(self, img_list, name, merge=True, is_read = False):
        """
        :param name: 图像保存路径
        :param merge: 是否进行长截图操作
        :param is_read: True 读取图片,传入的是路径，False 传入的是图像numpy
        :return: 图像路径名称
        """
        name = name
        if len(img_list) < 2:
            if is_read:
                cv2.imwrite(name, cv2.imread(img_list[0]))
            else:
                cv2.imwrite(name, img_list[0])
        else:
            if is_read:
                res = cv2.imread(img_list[0])
                pre_image = res
            else:
                res = img_list[0]
                pre_image = img_list[0]
            for img in img_list[1:]:
                if is_read:
                    img = cv2.imread(img)
                # img1 = self.img_merge(img1, cv2.imread(img), merge)
                overlap = self.find_vertical_overlapv2(pre_image, img)
                if merge:
                    res = np.vstack((res, img[overlap:, :]))
                else:
                    res = np.vstack((res, img))
                pre_image = img
            cv2.imwrite(name, res)
        return name

    

#v2——0.16714906692504883
#v3——0.8626260757446289
#v1——0.11216473579406738

import os

def img_sort_del_overlap(ENV, name_order):
    """
    通用图片排序
    :param env:
    :param name_order:
    :return:
    """
    img_list = []
    for file_name in os.listdir(ENV.logPath):
        if file_name.startswith("adc_result"):
            img_list.append(file_name)
    result = list(filter(lambda x: x.split("_")[2] in name_order, img_list))
    result.sort(key=lambda item: (name_order.index(item.split("_")[2]), item.split("_")[-1].split(".")[0]))
    monitor_task_status_v2("图像排序",f"图像为：{result}")

    res_pop = []
    for i in range(len(result) -1):
        if "_".join(result[i].split("_")[:-1]) == "_".join(result[i+1].split("_")[:-1]):
            os.remove(os.path.join(ENV.logPath, result[i]))
            res_pop.append(i)
    
    for i in range(len(res_pop)-1,-1,-1):
        result.pop(res_pop[i])


    for item in result:
        new_file_name = "_".join(item.split("_")[0:-1]) + "_" + str(int(time.time() * 1000000)) + "." + item.split(".")[
            -1]
        os.rename(os.path.join(ENV.logPath, item), os.path.join(ENV.logPath, new_file_name))



def ocr_from_img_path(img_path, img_size=(0,0), remote_ocr_type=(2, 1, 3), fault_tolerant_map={}):
    #使用路径进行ocr识别

    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            ocr_res = [[item["txts"], ((item["box"][0][0]+item["box"][1][0])/2+img_size[0], (item["box"][0][1]+item["box"][2][1])/2
                                        + img_size[1])] for item in res]
            if ocr_res:
                for item in ocr_res:
                    if item[0] in fault_tolerant_map:
                        item[0] = fault_tolerant_map[item[0]]
                return ocr_res

def ocr_from_img_path_return_all_pos(img_path, img_size=(0,0), remote_ocr_type=(2, 1, 3), fault_tolerant_map={}, return_centre = True):

    for type in remote_ocr_type:
        res = ocr_image_by_eas(img_path, type=type)
        if res:
            if return_centre:
                ocr_res = [[item["txts"], ((item["box"][0][0]+item["box"][1][0])/2+img_size[0], (item["box"][0][1]+item["box"][2][1])/2
                                            + img_size[1])] for item in res]
            else:
                ocr_res = [[item["txts"], (item["box"][0][0] +img_size[0], item["box"][0][1] + img_size[1], item["box"][1][0]+img_size[0], item["box"][2][1] + img_size[1])] 
                           for item in res]
            if ocr_res:
                for item in ocr_res:
                    if item[0] in fault_tolerant_map:
                        item[0] = fault_tolerant_map[item[0]]
                return ocr_res
            

def in_ranges(h, h_list):
    assert len(h_list) % 2 == 0, "h_list 必须是偶数个元素"
    
    for low, high in zip(h_list[0::2], h_list[1::2]):  # 每两个配成一对
        if low <= h <= high:
            return True
    return False

def dwarf_get_hsv(img):
    """"
    获取图片主色的hsv
    HSV颜色模型‌由三个参数组成：色相（Hue, H）、饱和度（Saturation, S）和亮度（Value, V）。
    ‌色相（H）‌：表示颜色的种类，取值范围为0°到360°，常见的色相与数值对应关系如下：
    红色：0°
    绿色：120°
    蓝色：240°
    黄色：60°
    青色：180°
    紫色：300°
    它们的补色相差180°‌12。
    ‌饱和度（S）‌：表示颜色的纯度，取值范围为0.0到1.0。饱和度越高，颜色越鲜艳；饱和度越低，颜色越黯淡‌12。
    ‌亮度（V）‌：表示颜色的明亮程度，取值范围为0.0（黑色）到1.0（白色）。亮度越高，颜色越亮；亮度越低，颜色越暗‌
    """
    import colorsys
    from colorthief import ColorThief
    # 加载图片
    # image = None
    img_path = None
    if isinstance(img, str):
        img_path = img
    elif isinstance(img, np.ndarray):
        img_path = os.path.join(ST.LOG_DIR, "temp.jpg")
        cv2.imwrite(img_path, img)
    elif isinstance(img, Image.Image):
        img_path = os.path.join(ST.LOG_DIR, "temp.jpg")
        img.save(img_path)
    color_thief = ColorThief(img_path)
    # 获取主颜色
    dominant_color = color_thief.get_color(quality=1)
    # 获取调色板
    palette = color_thief.get_palette(color_count=6)
    # 将 RGB 从 0-255 范围转换到 0-1 范围
    r, g, b = [x / 255.0 for x in dominant_color]
    # 使用 colorsys 转换 RGB 到 HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    monitor_print(f"dwarf_get_hsv: h: {h} s: {s} v: {v}")
    return h, s, v

# 强化长截图使用
def detect_have_goods(img_path: str, have_goods_img: Template, 
                      shift_pos: list, pattern_str = "",
                      return_centre_pos = True, h_list = [], 
                      phase_name = "", filter_flag = False,
                      fault_tolerant_map = {}, remote_information_map = {}):
    """
    :param img_path: 图像路径
    :param have_goods_img: 模版图像，用于判断是否解锁商品
    :param shift_pos: (上边界，下边界)， 边框边界值，需要自己计算出来
    :param pattern_str: 正则匹配模式，去除不要的内容，如"[0-9]+"
    :param return_centre_pos: ocr识别是否放回中心坐标，是代表不用筛除特定颜色的装备；否进行颜色筛选，需要给出h_list的颜色范围
    :param h_list: 颜色范围，用于筛选颜色,可以给多个
    :param phase_name 阶段名称
    :param filter_flag 是否进行颜色筛选
    :param fault_tolerant_map: 容错字典，用于容错识别结果
    :param remote_information_map: 远程多子信息字典，用于获取远程信息
    :return res: 商品内容
    :return properties_list: 新增多子属性列表
    :return cdn_url_list: 新增的cdn图片列表
    流程：先识别所有商品，之后根据颜色筛选高品质商品，最后看商品是否有解锁
    改为对字体进行偏移： -34 + 98
    """
    properties_list = []
    cdn_url_list = []
    # 后续需要修改为正则匹配
    # 强化的内容
    # pattern = re.compile(r'.*(\d|战|饰|穿戴|龙|[A-Za-z]).*')
    pattern = re.compile(pattern_str)
    # res = [i for [i,j] in ocr_for_img_path(img_path, remote_ocr_type=(1,2,3))]
    # pos = [j for [i,j] in ocr_for_img_path(img_path, remote_ocr_type=(1,2,3))]
    
    # 获取 OCR 结果 (i=文字, j=坐标)
    pairs = ocr_from_img_path_return_all_pos(img_path, remote_ocr_type=(1, 2, 3),return_centre=return_centre_pos, fault_tolerant_map=fault_tolerant_map)
    if not pattern_str:
        res, pos = map(list, zip(*pairs)) if pairs else ([], [])
    else:
        filtered_pairs = [(i, j) for i, j in pairs if not pattern.match(i)]
        res, pos = map(list, zip(*filtered_pairs)) if filtered_pairs else ([], [])
    
    # pos = [tuple(map(int, t)) for t in pos]
    monitor_task_status_v2(f"{phase_name}界面phase", f"识别商品：{res}，识别位置：{pos}")

            
    
    if not shift_pos:
        return res
    if return_centre_pos:
        pos_y = [(j - shift_pos[0], j + shift_pos[1]) for (i,j) in pos]
    else:
        pos_y = [((y1+y2)//2 - shift_pos[0], (y1+y2)//2 + shift_pos[1]) for (_,y1,_,y2) in pos]
    
    if not have_goods_img:
        # res = [i for i in res if len(i)>=4]
        return res
    pop_list = []
    # 装备品质筛选
    # 筛除特定颜色的装备
    pos = [tuple(map(int, t)) for t in pos]
    for i in range(len(pos)):
        # 这里应该是对img进行裁图操作. 宠物img传入参数不对, 不能是float
        timeStamp = str(int(time.time() * 10 ** 6))
        _, temp_pos_path = snapshot_write(f'adc_catch_{phase_name}_{i}_{timeStamp}',LT=(pos[i][0],pos[i][1]),RB=(pos[i][2],pos[i][3]), needPath=True,image=cv2.imread(img_path))
        
        # temp
        h,s,v = dwarf_get_hsv(temp_pos_path)
        # 橙色+红色。h 范围 0-25 ， 156-180
        # 紫色 125-155
        if not in_ranges(int(h * 180), h_list):
            pop_list.append(i)
    pop_list.sort(reverse=True)
    for i in pop_list:
        res.pop(i)
        pos_y.pop(i)
        pos.pop(i)
    pop_list.clear()

    # 增加多子更新
    if phase_name:
        for j in range(len(res)):
            if res[j] not in remote_information_map[phase_name]:
                name = phase_name + "_" + str(j) + str(int(time.time() * 1000000)) + '.jpg'
                image_path = ST.LOG_DIR + '/' + name

                # snapshot_write(name, LT= [pos[j][0], pos[j][1]], RB= [pos[j][2], pos[j][3]], image = cv2.imread(img_path))
                cv2.imwrite(image_path, cv2.imread(img_path)[ pos[j][1]: pos[j][3], pos[j][0]: pos[j][2]] )

                _, cdn_url = upload_jym_oss_with_pathes([image_path])
                temp2 = {
                        "propertyName": phase_name,
                        "propertyValueName": res[j]
                    }
                properties_list.append(temp2)
                cdn_url_list.append(cdn_url)


    
    # 需要判断位置， 应该需要得到多个值[(x,y),(x,y)]
    # 传入numpy数组，image
    pos_goods = snapshot_matchAll(image = cv2.imread(img_path), 
                                  match_image= have_goods_img,
                                  threshold= 0.8
                                  )
    # （x1，y1），（x2，y2） 得到中心坐标
    pos_goods_y = [y for (x,y) in pos_goods]

    # 未解锁筛除
    if not pos_goods_y:
        return res
    for y_i in pos_goods_y:
        for i,(y_start,y_end) in enumerate(pos_y):
            if (y_start-1) <= y_i <= (y_end+1):
                pop_list.append(i)
                # pop_list.append(pos_y.index((y_start,y_end)))
                break
    if not pop_list:
        return res
    pop_list.sort(reverse=True)
    for i in pop_list:
        res.pop(i)
    # if not filter_flag:
    #     return res
    
    return res, properties_list, cdn_url_list
    # 查看图片中pos的颜色



def fuzzy_replace(source_list, target_list, threshold=75):
    from rapidfuzz import fuzz, process
    """
    模糊匹配替换函数
    :param source_list: 需要替换的原列表（list[str]）
    :param target_list: 匹配来源列表（list[str]）
    :param threshold: 相似度阈值 (0~100)，默认 75
    :return: 替换后的新列表
    """
    result = []
    for item in source_list:
        match = process.extractOne(item, target_list, scorer=fuzz.ratio)
        if match:
            if match[1] >= threshold:
                result.append(match[0])
            elif match[1] >= 50:
                result.append(item)
    return result


def append_adc_catch(env, prefix, name1):
    """
    通用图片排序
    :param env:
    :param prefix: 前缀名
    :return:
    """
    for file_name in os.listdir(env.logPath):
        if file_name.startswith(name1):

            old_path = os.path.join(env.logPath, file_name)
            new_path = os.path.join(env.logPath, prefix + file_name)
            os.rename(old_path, new_path)


def get_name_large_model_copyv2(image_url,user_prompt) -> str:
    """
    获取武器名称，并以json的形式返回
    :return:
    """
    system_prompt = """
    你是一个游戏游戏名称识别助手，可以帮助用户精准识别道游戏的藏品名称，并按照用户意愿，将区服名称整理成指定的数据格式，
    """

    message = [
        {"role": "system",
         "content": [
             {"text": system_prompt}
         ]
         },
        {
            "role": "user",
            "content": [
                {"image": image_url},
                {"text": user_prompt}
            ]
        }
    ]
    area_server_res = remote_ds_r1_reasoning_copy(input_content=message,
                                             model="qwen-vl-max")
    area_server_dict = parse_model_output_to_json_copy(area_server_res)
    name = area_server_dict.get("name", "")
    monitor_task_status_v2("获取名称",f"通过大模型获取藏品名称：{name}")
    return name



# import time
# time1 = time.time()
# # image_path = ['qianghua_1.jpg','qianghua_2.jpg','qianghua_3.jpg']
# import os

# folder_path = "/Users/skybrid/code/adc-sc/utility/snap_utils"  # 比如 r"C:\Users\xxx\Pictures"
# image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')  # 支持的图片类型

# image_paths = []
# for filename in os.listdir(folder_path):
#     if filename.lower().endswith(image_extensions):
#         image_paths.append(os.path.join(folder_path, filename))

# image_paths.sort()
# print(image_paths)

# merge_obj = long_snap_picture([0.2,0.15,0.1,0.08,0.05,0.02], match= 0.88)
# merge_obj.image_merge(image_paths,'merge5.jpg',is_read=True)
# time2 = time.time()
# print(time2-time1)
