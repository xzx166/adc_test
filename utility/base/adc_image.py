# -*- encoding=utf8 -*-
import re
import numpy

from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont, ImageStat

from utility.base.adc_api import *
from utility.base.adc_monitor import *


def mask_image_range_tosave(imagePath, point1, point2):
    image = cv2.imread(imagePath)

    # 定义要模糊的区域坐标 (x1, y1, x2, y2)
    # (x1, y1) 是区域的左上角坐标，(x2, y2) 是区域的右下角坐标
    x1, y1 = point1
    x2, y2 = point2

    # 从原始图像中裁剪出想要模糊的区域
    roi = image[y1:y2, x1:x2]

    # 对该区域应用高斯模糊
    blurred_roi = cv2.GaussianBlur(roi, (99, 99), 0)

    # 将模糊后的区域替换回原始图像
    image[y1:y2, x1:x2] = blurred_roi

    # 保存模糊后的图像
    cv2.imwrite(imagePath, image)


def mask_black_image_range_tosave(imagePath, point1, point2):
    # [180,1171], [565,1240]
    img = cv2.imread(imagePath, 1)  # 读取一张图片，彩色
    cha = img.shape
    height, width, deep = cha
    # p1 = [180, 1171]
    # p2 = [565, 1240]

    p1 = point1
    p2 = point2

    x1, y1 = p1
    x2, y2 = p2

    # 确定 x 和 y 的范围
    x_range = range(min(x1, x2), max(x1, x2) + 1)
    y_range = range(min(y1, y2), max(y1, y2) + 1)

    # 遍历所有点
    for y in x_range:
        for x in y_range:
            point = [x, y]
            img[x, y] = (0, 0, 0)

    # save file
    cv2.imwrite(imagePath, img)


###下载图片
def download_cdn_image(url, save_path=None):
    real_save_path = save_path
    if save_path is None:
        # 解析url以提取路径
        parsed_url = urlparse(url)

        # 获取路径部分
        path = parsed_url.path

        # 使用os.path.basename获取文件名
        file_name = os.path.basename(path)

        real_save_path = os.path.join(ST.LOG_DIR, file_name)

    try:
        # 发送HTTP GET请求
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 以二进制写入方式打开文件并保存图片
            with open(real_save_path, 'wb') as f:
                f.write(response.content)
            monitor_print(f"Image_downloaded_and_saved_to:{real_save_path}")
            return real_save_path
        else:
            monitor_print(f"Failed_to_retrieve_image_Status_code: {response.status_code}")
    except Exception as e:
        monitor_print(f"Image_downloaded_An_error_occurred: {e}")
        return None

    return None


def save_image_to_result_path(image, image_part_name, index=None):
    final_path = os.path.join(ST.LOG_DIR, f"adc_result_{image_part_name}_{str(int(time.time() * 1000000))}.jpg")
    if index is not None:
        final_path = os.path.join(ST.LOG_DIR,
                                  f"adc_result_{image_part_name}_{index}_{str(int(time.time() * 1000000))}.jpg")
    cv2.imwrite(final_path, image)


def save_image_to_seller_path(image, image_part_name, index=None):
    final_path = os.path.join(ST.LOG_DIR, f"adc_seller_{image_part_name}_{str(int(time.time() * 1000000))}.jpg")
    if index is not None:
        final_path = os.path.join(ST.LOG_DIR,
                                  f"adc_seller_{image_part_name}_{index}_{str(int(time.time() * 1000000))}.jpg")
    cv2.imwrite(final_path, image)


def calculate(image1, image2):
    # 灰度直方图算法
    # 计算单通道的直方图的相似值
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + \
                     (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    print(f"calculate 相似度: {degree}, {inspect.currentframe().f_back.f_code.co_name}")
    return degree


def classify_hist_with_split(image1, image2, size=(256, 256)):
    # RGB每个通道的直方图相似度
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


def measure_image_similarity(image1Path, image2Path, image1Start=None, image1End=None, image2Start=None, image2End=None,
                             threshold=0.9):
    img_cv_before = cv2.imread(image1Path)
    img_cv_after = cv2.imread(image2Path)

    img1Start = image1Start
    img1End = image1End
    img2Start = image2Start
    img2End = image2End

    if img1Start == None or img1Start == None:
        img1Start = (0, 0)
        width, height = img_cv_before.size
        img1End = (width, height)

    if img2Start == None or img2End == None:
        img2Start = (0, 0)
        width, height = img_cv_after.size
        img2End = (width, height)

    # cropImg= img[20:73, 1500:1620]
    img1 = img_cv_before[img1Start[1]:img1End[1], img1Start[0]:img1End[0]]
    img2 = img_cv_after[img2Start[1]:img2End[1], img2Start[0]:img2End[0]]

    n4 = classify_hist_with_split(img1, img2)
    monitor_print(f"----------swipe_after n4: {n4}")

    isSame = n4 > threshold


def crop_and_calculate_slide_distance(arg, sliderFileName, cropStart=(920, 150), cropEnd=(1700, 750), slide_offset=240,
                                      finalStartPoint=(792, 910), t1=100, t2=200):
    current_directory = ST.LOG_DIR
    print(f'>>>> current_directory: {current_directory}')
    baseName = os.path.basename(arg)

    cropImg = cv2.imread(arg, 1)
    print(f"图片文件大小: {cropImg.shape[0]},{cropImg.shape[1]}")
    # (919,136)  (1731,777)
    if (cropImg.shape[0] != 1350 or cropImg.shape[1] != 2400):
        cropImg = cv2.resize(cropImg, (2400, 1350))

    cropImg = cropImg[cropStart[1]:cropEnd[1], cropStart[0]:cropEnd[0]]
    img_rgb = cv2.cvtColor(cropImg, cv2.COLOR_BGR2RGB)
    # img_rgb = cv2.medianBlur(img_rgb, 5)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    cv2.imwrite(f"{current_directory}/out/{baseName}_swipe_gray.jpeg", gray)
    # 创建锐化核，这里使用一个简单的拉普拉斯核

    slider_img = cv2.imread(sliderFileName, 0)  # 滑块图像

    # 进行Canny边缘检测
    edges = cv2.Canny(gray, threshold1=t1, threshold2=t2)
    edges = cv2.bitwise_not(edges)

    print(f"输出文件：  {current_directory}/out/{baseName}_swipe_edge_{t1}_{t2}.jpeg")
    # 显示结果
    # cv2.imwrite(f"{current_directory}/out/{baseName}_swipe_edge_{t1}_{t2}.jpeg", edges)

    # 模板匹配
    result = cv2.matchTemplate(edges, slider_img, cv2.TM_CCOEFF_NORMED)
    # print(f'result: {result}')
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 计算滑块的起始和结束位置
    start_point = max_loc
    end_point = (max_loc[0] + slider_img.shape[1], max_loc[1] + slider_img.shape[0])

    finalEndPoint = (finalStartPoint[0] + slide_offset + start_point[0], finalStartPoint[1])
    print(f'start_point: {start_point} slideDistanceX={start_point[0] + slide_offset} ')
    print(
        f'adb shell input touchscreen swipe {finalStartPoint[0]} {finalStartPoint[1]} {finalEndPoint[0]} {finalEndPoint[1]} 1000')

    print(f"{current_directory}/out/{baseName}_swipe_edge_matched_{t1}_{t2}.jpeg")
    # 画出匹配的区域
    cv2.rectangle(gray, start_point, end_point, 255, 2)
    cv2.imwrite(f"{current_directory}/out/{baseName}_swipe_edge_matched_{t1}_{t2}.jpeg", gray)

    return (finalStartPoint, finalEndPoint)


def crop_pos_image_from_snapshot(s_file_name, d_file_name, p1, p2, need_snapshot=True, need_write=True):
    #     file_name = f"final_crop_snapshot_{count}.jpg"
    # sleep(AppEnv.get_instance().sleepTime)
    # performance_start_timestamp = int(time.time()*1000000)
    if need_snapshot:
        lx_safe_snapshot(filename=s_file_name, msg="Please fill in the test point.")

    # performance_interval = int(time.time()*1000000) - performance_start_timestamp
    # monitor_task_status(AppEnv.get_instance(), "性能统计", f"snapshot_interval:{str(performance_interval)}")

    path = os.path.join(ST.LOG_DIR, s_file_name)
    # performance_start_timestamp = int(time.time()*1000000)
    img_cv = cv2.imread(path)
    # performance_interval = int(time.time()*1000000) - performance_start_timestamp
    # monitor_task_status(AppEnv.get_instance(), "性能统计", f"imread_interval:{str(performance_interval)}")

    # performance_start_timestamp = int(time.time()*1000000)
    cropped_image = img_cv[p1[1]:p2[1], p1[0]:p2[0]]
    # performance_interval = int(time.time()*1000000) - performance_start_timestamp
    # monitor_task_status(AppEnv.get_instance(), "性能统计", f"img_cv_interval:{str(performance_interval)}")

    if need_write:
        wirte_path = os.path.join(ST.LOG_DIR, d_file_name)
        # performance_start_timestamp = int(time.time()*1000000)
        cv2.imwrite(wirte_path, cropped_image)
    # performance_interval = int(time.time()*1000000) - performance_start_timestamp
    # monitor_task_status(AppEnv.get_instance(), "性能统计", f"imwrite_interval:{str(performance_interval)}")
    return cropped_image


# img是图像数据
def crop_pos_from_image(img, p1, p2):
    cropped_image = img[p1[1]:p2[1], p1[0]:p2[0]]
    return cropped_image


def lx_match_in(match_image, whole_image, threshold=0.7):
    # cropImg=cv2.imread('/Users/chanson.cc/01-code/14-aligame/web/adc-pc/server/tools/adc-sc/netease/juesetujian_combine_all_0.jpg',1)
    # slider_img = cv2.imread('/Users/chanson.cc/01-code/14-aligame/web/adc-pc/server/tools/adc-sc/netease/juesexuanze_crop_match_1.jpg', 1)  # 滑块图像

    result = cv2.matchTemplate(whole_image, match_image, cv2.TM_CCOEFF_NORMED)
    # print(result)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    start_point = max_loc
    end_point = (max_loc[0] + match_image.shape[1], max_loc[1] + match_image.shape[0])
    print(f'start_point: {start_point} slideDistanceX={start_point[0] + 0} ')
    # cv2.rectangle(whole_image, start_point, end_point, (0,0,255), 2)
    # cv2.imwrite(f"/Users/chanson.cc/01-code/14-aligame/web/adc-pc/server/tools/adc-sc/out/out.jpeg", cropImg)
    print(f"x: {start_point[0]} y={end_point[1]} conf={max_val}")
    if max_val > threshold:
        return (start_point[0], end_point[1])
    else:
        return None


def lx_match_res(match_image, whole_image):
    result = cv2.matchTemplate(whole_image, match_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val


def lx_match_in_all(match_image, whole_image, threshold):
    # cropImg=cv2.imread('/Users/chanson.cc/01-code/14-aligame/web/adc-pc/server/tools/adc-sc/netease/juesetujian_combine_all_0.jpg',1)
    # slider_img = cv2.imread('/Users/chanson.cc/01-code/14-aligame/web/adc-pc/server/tools/adc-sc/netease/juesexuanze_crop_match_1.jpg', 1)  # 滑块图像

    result = cv2.matchTemplate(whole_image, match_image, cv2.TM_CCOEFF_NORMED)
    # print(result)

    # 设置阈值
    threshold = 0.7

    # 获取匹配程度大于阈值的位置
    loc = np.where(result >= threshold)

    # 遍历这些位置
    location_list = []
    for pt in zip(*loc[::-1]):  # Switch columns and rows
        # You can use pt which is the top-left corner of the matching area
        # Do something with the matching area, like drawing a rectangle
        location_list.append((pt, (pt[0] + match_image.shape[1], pt[1] + match_image.shape[0])))
        # cv2.rectangle(cropImg, pt, (pt[0] + match_image.shape[1], pt[1] + match_image.shape[0]), (0, 0, 255), 2)
    # cv2.imwrite(f"{out_path}/out-{file}.jpeg", cropImg)
    return location_list


def snapshot_when_exception(file_name_prefix, loop_index=None):
    file_name = file_name_prefix + '_' + str(int(time.time() * 1000000)) + '.jpg'
    if loop_index != None and loop_index >= 0:
        file_name = file_name_prefix + '_' + str(loop_index) + '_' + str(int(time.time() * 1000000)) + '.jpg'
    lx_safe_snapshot(filename=file_name, msg="get a snapshot.")
    final_path = os.path.join(ST.LOG_DIR, file_name)
    return final_path


def resize_image_with_hw(image, resize_height=None, resize_width=None):
    if resize_height == None and resize_width == None:
        return image

    if resize_height != None and resize_width != None:
        print('图片会变形，请自己处理')
        return image

    resized_image = None
    if resize_width != None:
        ratio = resize_width / image.shape[1]

        # 计算新的高度
        new_height = int(image.shape[0] * ratio)

        # 使用cv2.resize()进行缩放
        resized_image = cv2.resize(image, (resize_width, new_height), interpolation=cv2.INTER_AREA)
        return resized_image

    if resize_height != None:
        ratio = resize_height / image.shape[0]

        new_width = int(image.shape[1] * ratio)

        # 使用cv2.resize()进行缩放
        resized_image = cv2.resize(image, (new_width, resize_height), interpolation=cv2.INTER_AREA)
        return resized_image


def resizable_image_with_capInsets(image_path, cap_insets, target_size):
    # 打开原始图像
    image = Image.open(image_path)
    width, height = image.size

    result_width, result_height = target_size

    # 获取保护区域的边界
    left, top, right, bottom = cap_insets

    # 计算拉伸区域的尺寸
    stretch_width = width - left - (width - right)
    stretch_height = height - top - (height - bottom)

    corner_lt = image.crop((0, 0, left, top))
    corner_rt = image.crop((width - right, 0, width, top))
    corner_lb = image.crop((0, height - bottom, left, height))
    corner_rb = image.crop((width - right, height - bottom, width, height))

    border_left = image.crop((0, top, left, height - bottom))
    border_top = image.crop((left, 0, width - right, top))
    border_right = image.crop((width - right, top, width, height - bottom))
    border_bottom = image.crop((left, height - bottom, width - right, height))

    middle_area = image.crop((left, top, width - right, height - bottom))

    middle_area = middle_area.resize((result_width, result_height), Image.LANCZOS)

    border_left = border_left.resize((left, result_height), Image.LANCZOS)
    border_top = border_top.resize((result_width, top), Image.LANCZOS)
    border_right = border_right.resize((right, result_height), Image.LANCZOS)
    border_bottom = border_bottom.resize((result_width, bottom), Image.LANCZOS)

    final_image = Image.new('RGBA', (result_width, result_height))

    # 将图像粘贴回目标图像中
    final_image.paste(middle_area, (0, 0))

    final_image.paste(border_left, (0, 0))
    final_image.paste(border_top, (0, 0))
    final_image.paste(border_right, (result_width - right, 0))
    final_image.paste(border_bottom, (0, result_height - bottom))
    final_image.paste(corner_lt, (0, 0))
    final_image.paste(corner_rt, (result_width - right, 0))
    final_image.paste(corner_lb, (0, result_height - bottom))
    final_image.paste(corner_rb, (result_width - right, result_height - bottom))
    # final_image.paste(bottom_image, (0, height - bottom))

    return final_image


def get_rgb_from_pos(image, pos):
    # 获取指定点的RGB值
    x, y = pos
    b, g, r = image[y, x]  # 获取指定点的BGR值
    return (r, g, b)


# (0, 127) 像素点的灰度值范围是从0到255。其中，0表示黑色，255表示白色。因此，(0, 127)表示灰度值从黑色到中灰色的范围。
def detect_color_image(file, thumb_size=40, MSE_cutoff=22, adjust_color_bias=True):
    pil_img = Image.open(file)
    bands = pil_img.getbands()
    if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
        thumb = pil_img.resize((thumb_size, thumb_size))
        SSE, bias = 0, [0, 0, 0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel) / 3
            SSE += sum((pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2])
        MSE = float(SSE) / (thumb_size * thumb_size)
        if MSE <= MSE_cutoff:
            print("grayscale")
            # 灰色
            return 1
        else:
            print("Color\t\t\t")
            return 0
        print(f"MSE:{MSE}")
    elif len(bands) == 1:
        print(f"Black and white:{bands}")
        # 黑白
        return 1
    else:
        print(f"Don't know...:{bands}")
        return 0


def is_color_similar(color1, color2, threshold):
    # 计算颜色之间的欧氏距离
    distance = np.linalg.norm(np.array(color1) - np.array(color2))
    # print(f"is_color_similar distance:{distance}{color1}{color2}")
    return distance <= threshold


# target_color 是正常的颜色顺序
def is_image_color_similar(image, target_color, threshold):
    print(f"is_image_color_similar: start")
    height, width, _ = image.shape

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    for row in range(height):
        for col in range(width):
            pixel_color = image_rgb[row, col]
            # print(f"is_image_color_similar: {pixel_color},{target_color}")
            if not is_color_similar(pixel_color, target_color, threshold):
                print(f"is_image_color_similar: not similar end")
                return False
    print(f"is_image_color_similar: similar end")
    return True


def is_in_gray_range(image_path, top_left, bottom_right, gray_range=(0, 127)):
    image = cv2.imread(image_path)
    return is_in_gray_range_by_image(image, top_left, bottom_right, gray_range)


def is_in_gray_range_by_image(image, top_left, bottom_right, gray_range=(0, 127)):
    region = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    wirte_path = os.path.join(ST.LOG_DIR, f"gray_crop_12345_{top_left}.jpg")
    cv2.imwrite(wirte_path, region)

    isgray = detect_color_image(wirte_path)
    print(f"isgray:{isgray}")
    return isgray == 1


def merge_text_in_image(title_image, text, text_color, font_size=None, textPoint=None, text_bg_color=None):
    assert title_image is not None, "merge_text_in_image title_image is None"
    # 将图像转换为PIL格式
    image_pil = Image.fromarray(cv2.cvtColor(title_image, cv2.COLOR_BGR2RGB))

    # 创建绘图对象
    draw = ImageDraw.Draw(image_pil)

    ttf_path = AppEnv.get_instance().rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'
    the_font_size = 60
    if font_size is not None:
        the_font_size = font_size
    font = ImageFont.truetype(ttf_path, size=the_font_size)
    text_lenth = draw.textlength(text, font=font)
    print(f"----text_lenth:{text_lenth},{font}")

    text_position = None
    if textPoint is not None:
        text_position = textPoint
    else:
        # # 计算文字的居中位置
        title_image_height, title_image_width, _ = title_image.shape
        text_x = (title_image_width - text_lenth) // 2
        text_y = (title_image_height - the_font_size) // 2 - 5

        text_position = (text_x, text_y)  # 文字位置 (x, y)
        print(f"----text_position:{text_position}")

    if text_bg_color:
        small_bg_image = Image.new('RGB', (int(text_lenth), the_font_size), color=text_bg_color)
        small_bg_draw = ImageDraw.Draw(small_bg_image)
        small_bg_draw.text((0, -7), text, font=font, fill=text_color)
        image_pil.paste(small_bg_image, text_position)
    else:
        draw.text(text_position, text, font=font, fill=text_color)

    # 将PIL图像转换回OpenCV格式
    title_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return title_image


def overlay_imgs_on_image(large_image, overlay_imgs):
    for index, item in enumerate(overlay_imgs):
        (img, pos) = item
        if img is None or pos is None:
            break

        # 确定小图片的宽度和高度
        small_height, small_width, _ = img.shape
        pos_x, pos_y = pos

        # 将小图片复制到大图片的指定位置
        large_image[pos_y:pos_y + small_height, pos_x:pos_x + small_width] = img

    return large_image


# title和tail横向居中展示
# subtitle靠左展示
# left, top, right, bottom = cap_insets
def combine_images_with_bg_and_title(image, bg_path, bg_cap_insets, image_border_info=None, title_info=None,
                                     sub_title_info=None, tail_info=None, subTitleFontSize=60):
    title_bg_path = None
    title_bg_catInsets = None
    title = None
    title_color = None
    if title_info:
        title_bg_path, title_bg_catInsets, title, title_color = title_info

    sub_title_bg_path = None
    sub_title_bg_catInsets = None
    sub_title = None
    sub_title_color = None
    if sub_title_info:
        sub_title_bg_path, sub_title_bg_catInsets, sub_title, sub_title_color = sub_title_info

    tail_bg_path = None
    tail_bg_capInsets = None
    tail_title = None
    tail_title_colo = None
    if tail_info:
        tail_bg_path, tail_bg_capInsets, tail_title, tail_title_color = tail_info

    border_width = 40
    border_height = 40
    pos_internal = 40
    if image_border_info:
        border_width, border_height = image_border_info
        pos_internal = border_height

    if bg_path:
        height, width, _ = image.shape

        title_image = None
        sub_title_image = None
        tail_image = None

        if title_bg_path:
            title_image = cv2.imread(title_bg_path)
            title_image_height, _, _ = title_image.shape
            # title_image = Image.open(title_bg_path)
            if title_bg_catInsets:
                bg_image_pil = resizable_image_with_capInsets(title_bg_path, title_bg_catInsets,
                                                              (width, title_image_height))

                # 将PIL图像对象转换为NumPy数组
                image_np = np.array(bg_image_pil)

                # 将NumPy数组转换为OpenCV图像对象
                title_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            if title:
                title_image = merge_text_in_image(title_image, title, title_color)
            file_path = os.path.join(ST.LOG_DIR, f"merge_text_title_{str(int(time.time() * 1000000))}.jpg")
            cv2.imwrite(file_path, title_image)

        if sub_title_bg_path:
            sub_title_image = cv2.imread(sub_title_bg_path)

            sub_title_image_height, _, _ = sub_title_image.shape
            # title_image = Image.open(title_bg_path)
            if sub_title_bg_catInsets:
                bg_image_pil = resizable_image_with_capInsets(sub_title_bg_path, sub_title_bg_catInsets,
                                                              (width, sub_title_image_height))

                # 将PIL图像对象转换为NumPy数组
                image_np = np.array(bg_image_pil)

                # 将NumPy数组转换为OpenCV图像对象
                sub_title_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            if sub_title:
                sub_title_image = merge_text_in_image(sub_title_image, sub_title, sub_title_color,
                                                      font_size=subTitleFontSize)
            file_path = os.path.join(ST.LOG_DIR, f"merge_text_subtitle_{str(int(time.time() * 1000000))}.jpg")
            cv2.imwrite(file_path, sub_title_image)

        if tail_bg_path:
            tail_image = cv2.imread(tail_bg_path)

            tail_image_height, _, _ = tail_image.shape
            # title_image = Image.open(title_bg_path)
            if tail_bg_capInsets:
                bg_image_pil = resizable_image_with_capInsets(tail_bg_path, tail_bg_capInsets,
                                                              (width, tail_image_height))

                # 将PIL图像对象转换为NumPy数组
                image_np = np.array(bg_image_pil)

                # 将NumPy数组转换为OpenCV图像对象
                tail_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            if tail_title:
                tail_image = merge_text_in_image(tail_image, tail_title, tail_title_color)
            file_path = os.path.join(ST.LOG_DIR, f"merge_text_tailtitle_{str(int(time.time() * 1000000))}.jpg")
            cv2.imwrite(file_path, tail_image)

        title_part_height = (title_image.shape[0] + pos_internal) if title_image is not None else 0
        title_part_width = title_image.shape[1] if title_image is not None else 0

        subtitle_part_height = (sub_title_image.shape[0] + pos_internal) if sub_title_image is not None else 0

        tailtitle_part_height = (tail_image.shape[0] + pos_internal) if tail_image is not None else 0

        # pos_x, pos_y = (40,40)

        real_resize_width = 0
        if title_part_width > width:
            real_resize_width = title_part_width
        else:
            real_resize_width = width
        resize_width = real_resize_width + border_width * 2
        resize_height = border_height + title_part_height + subtitle_part_height + height + tailtitle_part_height + border_height
        bg_image_pil = resizable_image_with_capInsets(bg_path, bg_cap_insets, (resize_width, resize_height))

        # 将PIL图像对象转换为NumPy数组
        image_np = np.array(bg_image_pil)

        # 将NumPy数组转换为OpenCV图像对象
        bg_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        canvas = np.zeros((resize_height, resize_width, 3), dtype=np.uint8)
        canvas[0:0 + bg_image.shape[0], 0:0 + bg_image.shape[1]] = bg_image

        real_image_y = border_height
        # 将图像粘贴回目标图像中
        if title_image is not None:
            canvas[real_image_y:real_image_y + title_image.shape[0],
            (real_resize_width - title_image.shape[1]) // 2 + border_width:(real_resize_width - title_image.shape[
                1]) // 2 + border_width + title_image.shape[1]] = title_image
            real_image_y = real_image_y + title_image.shape[0] + pos_internal
            # content_image.paste(title_image, ((pend_width - title_image.size[0]) // 2,0))

        if sub_title_image is not None:
            bg_color = (0, 0, 0)

            canvas[real_image_y:real_image_y + sub_title_image.shape[0],
            border_width:border_width + sub_title_image.shape[1]] = sub_title_image
            real_image_y = real_image_y + sub_title_image.shape[0] + pos_internal

        canvas[real_image_y:real_image_y + image.shape[0], border_width:border_width + image.shape[1]] = image

        if tail_image is not None:
            real_image_y = real_image_y + image.shape[0] + pos_internal
            bg_color = (0, 0, 0)

            canvas[real_image_y:real_image_y + tail_image.shape[0],
            (real_resize_width - tail_image.shape[1]) // 2 + border_width:(real_resize_width - title_image.shape[
                1]) // 2 + border_width + tail_image.shape[1]] = tail_image

        f = os.path.join(ST.LOG_DIR, f"merge_content_{str(int(time.time() * 1000000))}.jpg")
        cv2.imwrite(f, canvas)

        return canvas


# 这里要注意max_rows_count == 0表示是无限行
def combine_images_with_outerspacing(combine_images_arr, one_row_count=1, max_rows_count=10, spacing=0,
                                     spacing_color=(1, 1, 1), out_spacing=0):
    item_height, item_width = combine_images_arr[0].shape[:2]
    whole_width = item_width * one_row_count + spacing * (one_row_count - 1) + out_spacing * 2

    origin_x = out_spacing
    origin_y = out_spacing

    page_count = 1
    if max_rows_count == 0:
        page_count = 1
    else:
        temp = (len(combine_images_arr) - 1) // (one_row_count * max_rows_count)
        page_count = temp + 1
        # whole_height = item_height * max_rows_count + spacing * (max_rows_count - 1)

    monitor_print(
        f"---combine_images_with_outerspacing_page_count:{len(combine_images_arr)},{one_row_count},{max_rows_count},{temp},{page_count}")
    result_com_imgs = []

    whole_height = 0
    if page_count == 1:
        total_rows = (len(combine_images_arr) - 1) // one_row_count + 1
        whole_height = item_height * total_rows + spacing * (total_rows - 1) + out_spacing * 2

        canvas = np.zeros((whole_height, whole_width, 3), dtype=np.uint8)
        canvas[:] = spacing_color

        for paste_index, paste_img in enumerate(combine_images_arr):
            y_offset = origin_y + paste_index // one_row_count * (item_height + spacing)
            y_height = item_height
            x_offset = origin_x + paste_index % one_row_count * (item_width + spacing)
            x_width = item_width
            canvas[y_offset: y_offset + y_height, x_offset:x_offset + x_width] = paste_img
        result_com_imgs.append(canvas)
        return result_com_imgs
    elif page_count > 1:

        canvas = None
        for i in range(page_count):
            start_index = 0 + i * (one_row_count * max_rows_count)
            end_index = start_index + (one_row_count * max_rows_count) - 1

            total_rows = max_rows_count
            whole_height = item_height * total_rows + spacing * (total_rows - 1) + out_spacing * 2
            canvas = np.zeros((whole_height, whole_width, 3), dtype=np.uint8)

            if i == page_count - 1:
                left_total_count = len(combine_images_arr) - i * one_row_count * max_rows_count
                total_rows = (left_total_count - 1) // one_row_count + 1
                whole_height = item_height * total_rows + spacing * (total_rows - 1) + out_spacing * 2
                canvas = np.zeros((whole_height, whole_width, 3), dtype=np.uint8)

                monitor_print(
                    f"---combine_images_with_outerspacing_page_count:{left_total_count},{total_rows},{whole_height}")

                end_index = start_index + (
                        len(combine_images_arr) - (one_row_count * max_rows_count * (page_count - 1))) - 1

            canvas[:] = spacing_color
            print(f"----test:{start_index}::{end_index}")
            for real_index in range(end_index - start_index + 1):
                find_index = real_index + start_index
                paste_img = combine_images_arr[find_index]
                paste_index = real_index
                y_offset = origin_y + paste_index // one_row_count * (item_height + spacing)
                y_height = item_height
                x_offset = origin_x + paste_index % one_row_count * (item_width + spacing)
                x_width = item_width
                canvas[y_offset: y_offset + y_height, x_offset:x_offset + x_width] = paste_img
            result_com_imgs.append(canvas)
        return result_com_imgs
    else:
        return None


# spacing_color 这个参数是反的顺序
def combine_images(combine_images_arr, one_row_count=1, max_rows_count=10, spacing=0, spacing_color=(1, 1, 1),
                   is_adjust=False, title=None, title_color=(0, 0, 0), text_size=30):
    final_count = len(combine_images_arr)
    monitor_print(f"*****combine_images*******{final_count}")
    if final_count <= 0:
        return None
    spaceing_color_1, spaceing_color_2, spaceing_color_3 = spacing_color
    # =============================图片补齐START=============================#
    # is_adjust=True,对图片进行居中补齐,保证图片大小一样
    if is_adjust:
        max_height = 0
        max_width = 0
        for item_image in combine_images_arr:
            item_height, item_width = item_image.shape[:2]
            max_width = item_width if item_width > max_width else max_width
            max_height = item_height if item_height > max_height else max_height
        # 图片补齐
        combine_images_arr_new = []
        for item_image in combine_images_arr:
            item_height, item_width = item_image.shape[:2]
            item_image = cv2.copyMakeBorder(item_image, 0, 0, 0, spacing, cv2.BORDER_CONSTANT,
                                            value=(spaceing_color_1, spaceing_color_2, spaceing_color_3))
            width_diff = max_width - item_width
            height_diff = max_height - item_height
            item_image = cv2.copyMakeBorder(item_image, top=height_diff // 2, bottom=0,
                                            left=width_diff // 2, right=0, borderType=cv2.BORDER_CONSTANT,
                                            value=(spaceing_color_1, spaceing_color_2, spaceing_color_3))
            item_image = cv2.copyMakeBorder(item_image, top=0, bottom=height_diff - height_diff // 2,
                                            left=0, right=width_diff - width_diff // 2, borderType=cv2.BORDER_CONSTANT,
                                            value=(spaceing_color_1, spaceing_color_2, spaceing_color_3))
            combine_images_arr_new.append(item_image)
        combine_images_arr = combine_images_arr_new
    # =============================图片补齐END=============================#
    item_height, item_width = combine_images_arr[0].shape[:2]
    whole_width = item_width * one_row_count + spacing * (one_row_count - 1)
    if final_count > 0:
        row_imgs = []
        colomn_imgs = []
        for i in range(final_count):
            img = combine_images_arr[i]

            if (i + 1) % one_row_count > 0:
                img = cv2.copyMakeBorder(img, 0, 0, 0, spacing, cv2.BORDER_CONSTANT,
                                         value=(spaceing_color_1, spaceing_color_2, spaceing_color_3))

            row_imgs.append(img)
            if (i + 1) % one_row_count == 0:

                final_img = cv2.hconcat(row_imgs)

                colomn_imgs.append(final_img)
                row_imgs = []
            elif i == final_count - 1:
                final_img = cv2.hconcat(row_imgs)

                color = (1, 1, 1)
                padding_height, padding_width = final_img.shape[:2]
                # 生成指定尺寸和颜色的背景图像
                background = np.zeros((item_height, whole_width - padding_width, 3), dtype=np.uint8)
                background[:] = spacing_color

                final_img = cv2.hconcat([final_img, background])

                # cv2.imwrite(final_path,final_img)
                colomn_imgs.append(final_img)
                # cv2.imwrite(f"write_path_hconcat_{i}.jpg",final_img)
                row_imgs = []
        # result_img = np.vstack(colomn_imgs)
        print(f"*****combine_images_colomn_imgs*******{len(colomn_imgs)}")
        item_imgs = []
        result_imgs = []
        size_width = None
        for i in range(len(colomn_imgs)):
            img = colomn_imgs[i]

            if i != len(colomn_imgs) - 1 and (i + 1) % max_rows_count > 0:
                img = cv2.copyMakeBorder(img, 0, spacing, 0, 0, cv2.BORDER_CONSTANT,
                                         value=(spaceing_color_1, spaceing_color_2, spaceing_color_3))

            if size_width is None:
                size_width = img.shape[1]
            new_size = (size_width, img.shape[0])
            img = cv2.resize(img, new_size)
            item_imgs.append(img)

            if (i + 1) % max_rows_count == 0 or i == len(colomn_imgs) - 1:
                if title:
                    width, height = item_imgs[0].shape[1], text_size + 20
                    image = Image.new("RGB", (width, height), (spaceing_color_3, spaceing_color_2, spaceing_color_1))
                    # 在图片中间写字
                    draw = ImageDraw.Draw(image)
                    ttf_path = AppEnv.get_instance().rootHome + '/utility/resource' + '/AlibabaPuHuiTi-3-85-Bold.ttf'
                    font = ImageFont.truetype(ttf_path, text_size)
                    text_width = draw.textlength(title, font)
                    text_x = (width - text_width) / 2
                    text_y = 5
                    draw.text((text_x, text_y), title, font=font, fill=title_color)
                    img = cv2.cvtColor(numpy.asarray(image), cv2.COLOR_RGB2BGR)
                    item_imgs.insert(0, img)
                concat_img = cv2.vconcat(item_imgs)
                result_imgs.append(concat_img)
                item_imgs = []

        return result_imgs
    else:
        return None


def lx_snapshot(env, name, mask_pos=[], crop_pos=(), path=False, rectangle_pos=(), save_return_img=False):
    """
    截图+打码+剪切
    :param env
    :param name: 图片名 eg: adc_result_gerenxinxi
    :param mask_pos: [(x1, y1, x2, y2)]
    :param crop_pos: (x1, y1, x2, y2)
    :return:
    """
    name = name + "_" + str(int(time.time() * 1000000)) + '.jpg'
    lx_safe_snapshot(filename=name, msg="get a snapshot.")
    image_path = env.logPath + '/' + name
    for pos in mask_pos:
        mask_image_range_tosave(image_path, (pos[0], pos[1]), (pos[2], pos[3]))
    image_path = env.logPath + '/' + name
    image = cv2.imread(image_path)
    if crop_pos:
        image = image[crop_pos[1]: crop_pos[3], crop_pos[0]: crop_pos[2]]
    if rectangle_pos:
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        draw.rectangle(rectangle_pos, fill=None,
                       outline='red', width=5)
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        cv2.imwrite(image_path, image)
    if path:
        cv2.imwrite(image_path, image)
        return image_path
    if save_return_img:
        cv2.imwrite(image_path, image)
        return image
    return image


def combine_images_fiexd(combine_images_arr, flex_direction="row", justify_content="start", background=None,
                         interval=None):
    """
    固定图片数量简单拼图
    :param combine_images_arr: 图片列表
    :param flex_direction: 主轴方向，row 水平  column 垂直
    :param justify_content: 对其方式 start 上对齐  center 中对齐  end 下对齐
    :param background： 颜色默认取边缘颜色
    :param interval: 间隔
    :return:
    """
    result_images = []
    if not combine_images_arr:
        return np.array(0)
    if flex_direction == "row":
        max_height = 0
        for item_image in combine_images_arr:
            item_height, _ = item_image.shape[:2]
            max_height = item_height if item_height > max_height else max_height
        for idx, item_image in enumerate(combine_images_arr):
            if idx == len(combine_images_arr) - 1:
                interval = None
            height, width = item_image.shape[:2]
            # if height >= max_height:
            #     result_images.append(item_image)
            #     continue
            if justify_content == "start":
                color = item_image[height - 1, width - 1] if not background else background
                color = tuple([int(c) for c in color])
                height_diff = max_height - height
                item_image = cv2.copyMakeBorder(item_image, top=0, bottom=height_diff,
                                                left=0, right=0 if not interval else interval,
                                                borderType=cv2.BORDER_CONSTANT, value=color)
                result_images.append(item_image)
            elif justify_content == "center":
                color1 = item_image[0, 0] if not background else background
                color1 = tuple([int(c) for c in color1])
                color2 = item_image[height - 1, width - 1] if not background else background
                color2 = tuple([int(c) for c in color2])
                height_diff = max_height - height
                item_image = cv2.copyMakeBorder(item_image, top=height_diff // 2, bottom=0,
                                                left=0, right=0 if not interval else interval,
                                                borderType=cv2.BORDER_CONSTANT, value=color1)
                item_image = cv2.copyMakeBorder(item_image, top=0, bottom=height_diff - height_diff // 2,
                                                left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=color2)
                result_images.append(item_image)
            elif justify_content == "end":
                color = item_image[0, 0] if not background else background
                color = tuple([int(c) for c in color])
                height_diff = max_height - height
                item_image = cv2.copyMakeBorder(item_image, top=height_diff, bottom=0,
                                                left=0, right=0 if not interval else interval,
                                                borderType=cv2.BORDER_CONSTANT, value=color)
                result_images.append(item_image)
        return cv2.hconcat(result_images)
    elif flex_direction == "column":
        max_width = 0
        for item_image in combine_images_arr:
            _, item_width = item_image.shape[:2]
            max_width = item_width if item_width > max_width else max_width
        for idx, item_image in enumerate(combine_images_arr):
            # if idx == len(combine_images_arr) - 1:
            #     interval = None
            height, width = item_image.shape[:2]
            # if width >= max_width:
            #     result_images.append(item_image)
            #     continue
            if justify_content == "start":
                color = item_image[height - 1, width - 1] if not background else background
                color = tuple([int(c) for c in color])
                width_diff = max_width - width
                item_image = cv2.copyMakeBorder(item_image, top=0, bottom=0 if not interval else interval,
                                                left=0, right=width_diff, borderType=cv2.BORDER_CONSTANT, value=color)
                result_images.append(item_image)
            elif justify_content == "center":
                color1 = item_image[0, 0] if not background else background
                color1 = tuple([int(c) for c in color1])
                color2 = item_image[height - 1, width - 1] if not background else background
                color2 = tuple([int(c) for c in color2])
                width_diff = max_width - width
                item_image = cv2.copyMakeBorder(item_image, top=0, bottom=0 if not interval else interval,
                                                left=width_diff // 2, right=0, borderType=cv2.BORDER_CONSTANT,
                                                value=color1)
                item_image = cv2.copyMakeBorder(item_image, top=0, bottom=0,
                                                left=0, right=width_diff - width_diff // 2,
                                                borderType=cv2.BORDER_CONSTANT, value=color2)
                result_images.append(item_image)
            elif justify_content == "end":
                color = item_image[0, 0] if not background else background
                color = tuple([int(c) for c in color])
                width_diff = max_width - width
                item_image = cv2.copyMakeBorder(item_image, top=0, bottom=0 if not interval else interval,
                                                left=width_diff, right=0, borderType=cv2.BORDER_CONSTANT, value=color)
                result_images.append(item_image)
        return cv2.vconcat(result_images)
    return np.zeros(0)


def set_current_time_to_image(image_name_list):
    # f"adc_result_{image_part_name}_{str(int(time.time()*1000000))}.jpg"
    new_image_name_list = []
    for item in image_name_list:
        image_name = item

        image_name_path = os.path.join(ST.LOG_DIR, image_name)

        # 给定的字符串
        input_string = image_name

        # 正则表达式模式，用于匹配特定的数字序列
        pattern = r'(.*)_(\d+)\.jpg$'

        # 执行正则表达式匹配
        match = re.match(pattern, input_string)

        new_image_name = None

        if match:
            # 提取数字之前的部分和数字本身
            before_numbers = match.group(1)
            numbers = match.group(2)
            monitor_print(f"图片名中的时间戳数字之前的字符串:{before_numbers}")
            monitor_print(f"图片名中的时间戳数字:{numbers}")
            new_image_name = f"{before_numbers}_{str(int(time.time() * 1000000))}.jpg"
            monitor_print(f"新的图片名:{new_image_name}")
            os.rename(image_name_path, os.path.join(ST.LOG_DIR, new_image_name))
        else:
            monitor_print("未找到图片名中匹配的时间戳，直接添加新的时间戳")
            # 使用 rfind() 获取'.jpg'前的字符串
            index = input_string.rfind('.jpg')
            if index != -1:
                before_jpg = input_string[:index]
                new_image_name = f"{before_jpg}_{str(int(time.time() * 1000000))}.jpg"
                monitor_print(f"新的图片名:{new_image_name}")
            else:
                monitor_print(f"未找到jpg，直接返回")
                new_image_name = input_string  # 如果没有找到 '.jpg'，返回整个字符串

        if new_image_name is None or len(new_image_name) == 0:
            new_image_name_list.append(image_name)
        else:
            new_image_name_list.append(new_image_name)

    return new_image_name_list


# 获取图片的hsb
def get_image_hsb(image):
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h = int(image_hsv[..., 0].mean() * 2)  # Hue 平均色相
    s = int(image_hsv[..., 1].mean() / 255 * 100)  # Saturation 平均饱和度
    b = int(image_hsv[..., 2].mean() / 255 * 100)  # Brightness 平均亮度
    result = dict(h=h, s=s, b=b)
    print(f"image_hsb: {result}")
    return result


# 打码相关

def mask_image_range_tosave(imagePath, point1, point2):
    image = cv2.imread(imagePath)

    # 定义要模糊的区域坐标 (x1, y1, x2, y2)
    # (x1, y1) 是区域的左上角坐标，(x2, y2) 是区域的右下角坐标
    x1, y1 = point1
    x2, y2 = point2

    # 从原始图像中裁剪出想要模糊的区域
    roi = image[y1:y2, x1:x2]

    # 对该区域应用高斯模糊
    blurred_roi = cv2.GaussianBlur(roi, (99, 99), 0)

    # 将模糊后的区域替换回原始图像
    image[y1:y2, x1:x2] = blurred_roi

    # 保存模糊后的图像
    cv2.imwrite(imagePath, image)

    # # [180,1171], [565,1240]
    # img = cv2.imread(imagePath,1)  #读取一张图片，彩色
    # cha=img.shape
    # height,width,deep=cha
    # # p1 = [180, 1171]
    # # p2 = [565, 1240]

    # p1 = point1
    # p2 = point2

    # x1, y1 = p1
    # x2, y2 = p2

    # # 确定 x 和 y 的范围
    # x_range = range(min(x1, x2), max(x1, x2) + 1)
    # y_range = range(min(y1, y2), max(y1, y2) + 1)

    # # 遍历所有点
    # for y in x_range:
    #     for x in y_range:
    #         point = [x, y]

    #         if x%10==0 and y%10==0 :
    #             for i in range(10):
    #                 for j in range(10):
    #                     b,g,r=img[x,y]
    #                     img[x+i,y+j]=(b,g,r)

    # # save file
    # cv2.imwrite(imagePath,img)


def mask_black_image_range_tosave(imagePath, point1, point2):
    # [180,1171], [565,1240]
    img = cv2.imread(imagePath, 1)  # 读取一张图片，彩色
    cha = img.shape
    height, width, deep = cha
    # p1 = [180, 1171]
    # p2 = [565, 1240]

    p1 = point1
    p2 = point2

    x1, y1 = p1
    x2, y2 = p2

    # 确定 x 和 y 的范围
    x_range = range(min(x1, x2), max(x1, x2) + 1)
    y_range = range(min(y1, y2), max(y1, y2) + 1)

    # 遍历所有点
    for y in x_range:
        for x in y_range:
            point = [x, y]
            img[x, y] = (0, 0, 0)

    # save file
    cv2.imwrite(imagePath, img)
