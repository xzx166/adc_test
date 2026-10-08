from enum import Enum
from typing import List, Union
import numpy as np
from skimage.metrics import structural_similarity as ssim
import cv2
from utility.biz_utils.biz_utils import air_swipe_fast,snapshot_write,monitor_task_status_v2
# from StitchImageNew3 import stitch_image_sequence
from utility.wz_utils.StitchImageNew4 import stitch_image_sequence
"""
方法解释：
swipeCrop_and_bottomJudgePic_and_concatPic
    滑动截图裁剪，自动检测触底，拼接长图。这个不会返回第二个参数滑动的次数
swipeCrop_and_bottomJudgePic_and_concatPic_v2
    滑动截图裁剪，自动检测触底，拼接长图。这个会返回第二个参数滑动的次数
swipeCrop_and_bottomJudgePic_and_concatPic_v3
    滑动截图裁剪，自动检测触底，拼接长图。这个不会返回第二个参数滑动的次数
    在swipeCrop_and_bottomJudgePic_and_concatPic的基础上修改，因为遇到拼接导致线程停止的问题，
    换了一个函数进行拼接
"""

def swipeCrop_and_bottomJudgePic_and_concatPic(
                       start_pos,
                       direction,
                       write_name,
                       LT,
                       RB,
                       delta_pos,
                       duration,
                       hold_sec,
                       sec,
                       ssim_threshold=0.95,
                       max_images=20):
    """
    滑动截图裁剪，自动检测触底，拼接长图。
    判底逻辑：是根据前后两张图的相似度判断的，如果有很多物品

    Args:
        start_pos：滑动起始坐标
        direction: 滑动和拼接方向。可以直接用字符串，或者用Direction枚举类
            'vertical' 表示从上下滑动，上下拼接，
            ”horizontal' 表示从左右滑动，左右拼接
        write_name: 临时保存的截图名称，会被覆盖。
        LT: 截图左上角坐标，元组格式
        RB: 截图右下角坐标，元组格式
        delta_pos：滑动增量
        duration: 滑动持续时间
        hold_sec: 滑动结尾保持时间
        sec：滑动结束后等待时间
        sec: 滑动间隔
        ssim_threshold：触底判断的域值，默认0.95
        max_images: 最大截图数量，防止无限循环，默认20

    Returns:
        拼接后的长图 (np.ndarray)
    """
    image_list = []

    try:
        while len(image_list) < max_images:
            # 截图并裁剪
            img = snapshot_write(write_name, LT=LT, RB=RB)
            if img is None or not isinstance(img, np.ndarray):
                print("snapshot_write 返回无效图像，跳过...")
                continue
            image_list.append(img)
            print(f"已获取第 {len(image_list)} 张截图")

            # 滑动
            if direction == "vertical":
                # 执行滑动，竖直方向
                air_swipe_fast(start_pos, delta_y=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)
            elif direction == "horizontal":
                # 执行滑动，水平方向
                air_swipe_fast(start_pos, delta_x=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)

            # 当有至少两张图时，开始判断是否重复（触底）
            if len(image_list) >= 2:
                prev_img = image_list[-2]
                curr_img = image_list[-1]
                # 判断是否为相同图像
                if is_images_similar(prev_img, curr_img, threshold=ssim_threshold):
                    # print("检测到图像重复，已触底，停止滑动。")
                    monitor_task_status_v2("触底检测", "检测到图像重复，已触底，停止滑动。")
                    # 删除最后一张重复图
                    image_list.pop()
                    break

    except Exception as e:
        print(f"捕获过程中发生异常: {e}")
        # 出错时也尝试拼接已有图像
        pass

    # 确保至少有一张图
    if len(image_list) == 0:
        raise ValueError("未能获取任何有效截图")


    # 调用拼接函数
    print(f"已获取 {len(image_list)} 张截图")
    stitched_image = stitch_images_del_replic(image_list, direction=direction)
    return stitched_image


def swipeCrop_and_bottomJudgePic_and_concatPic_v2(
                       start_pos,
                       direction,
                       write_name,
                       LT,
                       RB,
                       delta_pos,
                       duration,
                       hold_sec,
                       sec,
                       ssim_threshold=0.95,
                       max_images=20):
    """
    滑动截图裁剪，自动检测触底，拼接长图。
    判底逻辑：是根据前后两张图的相似度判断的，如果有很多物品

    Args:
        start_pos：滑动起始坐标
        direction: 滑动和拼接方向。可以直接用字符串，或者用Direction枚举类
            'vertical' 表示从上下滑动，上下拼接，
            ”horizontal' 表示从左右滑动，左右拼接
        write_name: 临时保存的截图名称，会被覆盖。
        LT: 截图左上角坐标，元组格式
        RB: 截图右下角坐标，元组格式
        delta_pos：滑动增量
        duration: 滑动持续时间
        hold_sec: 滑动结尾保持时间
        sec：滑动结束后等待时间
        sec: 滑动间隔
        ssim_threshold：触底判断的域值，默认0.95
        max_images: 最大截图数量，防止无限循环，默认20

    Returns:
        拼接后的长图 (np.ndarray)
        len_image_list: 截图数量，即滑动的次数
    """
    image_list = []

    try:
        while len(image_list) < max_images:
            # 截图并裁剪
            img = snapshot_write(write_name, LT=LT, RB=RB)
            if img is None or not isinstance(img, np.ndarray):
                print("snapshot_write 返回无效图像，跳过...")
                continue
            image_list.append(img)
            print(f"已获取第 {len(image_list)} 张截图")

            # 滑动
            if direction == "vertical":
                # 执行滑动，竖直方向
                air_swipe_fast(start_pos, delta_y=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)
            elif direction == "horizontal":
                # 执行滑动，水平方向
                air_swipe_fast(start_pos, delta_x=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)

            # 当有至少两张图时，开始判断是否重复（触底）
            if len(image_list) >= 2:
                prev_img = image_list[-2]
                curr_img = image_list[-1]
                # 判断是否为相同图像
                if is_images_similar(prev_img, curr_img, threshold=ssim_threshold):
                    # print("检测到图像重复，已触底，停止滑动。")
                    monitor_task_status_v2("触底检测", "检测到图像重复，已触底，停止滑动。")
                    # 删除最后一张重复图
                    image_list.pop()
                    break

    except Exception as e:
        print(f"捕获过程中发生异常: {e}")
        # 出错时也尝试拼接已有图像
        pass

    # 确保至少有一张图
    if len(image_list) == 0:
        raise ValueError("未能获取任何有效截图")


    # 调用拼接函数
    stitched_image = stitch_images_del_replic(image_list, direction=direction)
    return stitched_image,len(image_list)

def swipeCrop_and_bottomJudgePic_and_concatPic_v3(
                       start_pos,
                       direction,
                       write_name,
                       LT,
                       RB,
                       delta_pos,
                       duration,
                       hold_sec,
                       sec,
                       ssim_threshold=0.95,
                       max_images=20):
    """
    滑动截图裁剪，自动检测触底，拼接长图。
    判底逻辑：是根据前后两张图的相似度判断的，如果有很多物品

    Args:
        start_pos：滑动起始坐标
        direction: 滑动和拼接方向。可以直接用字符串，或者用Direction枚举类
            'vertical' 表示从上下滑动，上下拼接，
            ”horizontal' 表示从左右滑动，左右拼接
        write_name: 临时保存的截图名称，会被覆盖。
        LT: 截图左上角坐标，元组格式
        RB: 截图右下角坐标，元组格式
        delta_pos：滑动增量
        duration: 滑动持续时间
        hold_sec: 滑动结尾保持时间
        sec：滑动结束后等待时间
        sec: 滑动间隔
        ssim_threshold：触底判断的域值，默认0.95
        max_images: 最大截图数量，防止无限循环，默认20

    Returns:
        拼接后的长图 (np.ndarray)
    """
    image_list = []

    try:
        while len(image_list) < max_images:
            # 截图并裁剪
            img = snapshot_write(write_name, LT=LT, RB=RB)
            if img is None or not isinstance(img, np.ndarray):
                print("snapshot_write 返回无效图像，跳过...")
                continue
            image_list.append(img)
            print(f"已获取第 {len(image_list)} 张截图")

            # 滑动
            if direction == "vertical":
                # 执行滑动，竖直方向
                air_swipe_fast(start_pos, delta_y=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)
            elif direction == "horizontal":
                # 执行滑动，水平方向
                air_swipe_fast(start_pos, delta_x=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)

            # 当有至少两张图时，开始判断是否重复（触底）
            if len(image_list) >= 2:
                prev_img = image_list[-2]
                curr_img = image_list[-1]
                # 判断是否为相同图像
                if is_images_similar(prev_img, curr_img, threshold=ssim_threshold):
                    # print("检测到图像重复，已触底，停止滑动。")
                    monitor_task_status_v2("触底检测", "检测到图像重复，已触底，停止滑动。")
                    # 删除最后一张重复图
                    image_list.pop()
                    break

    except Exception as e:
        print(f"捕获过程中发生异常: {e}")
        # 出错时也尝试拼接已有图像
        pass

    # 确保至少有一张图
    if len(image_list) == 0:
        raise ValueError("未能获取任何有效截图")

    # 调用拼接函数

    stitched_image = stitch_image_sequence(image_list, direction)

    return stitched_image


def swipe_and_return_count(
                       start_pos,
                       direction,
                       write_name,
                       LT,
                       RB,
                       delta_pos,
                       duration,
                       hold_sec,
                       sec,
                       ssim_threshold=0.95,
                       max_images=40):
    """
    滑动截图裁剪，自动检测触底，拼接长图。
    判底逻辑：是根据前后两张图的相似度判断的，如果有很多物品

    Args:
        start_pos：滑动起始坐标
        direction: 滑动和拼接方向。可以直接用字符串，或者用Direction枚举类
            'vertical' 表示从上下滑动，上下拼接，
            ”horizontal' 表示从左右滑动，左右拼接
        write_name: 临时保存的截图名称，会被覆盖。
        LT: 截图左上角坐标，元组格式
        RB: 截图右下角坐标，元组格式
        delta_pos：滑动增量
        duration: 滑动持续时间
        hold_sec: 滑动结尾保持时间
        sec：滑动结束后等待时间
        sec: 滑动间隔
        ssim_threshold：触底判断的域值，默认0.95
        max_images: 最大截图数量，防止无限循环，默认20

    Returns:
        拼接后的长图 (np.ndarray)
        len_image_list: 截图数量，即滑动的次数
    """
    image_list = []

    try:
        while len(image_list) < max_images:
            # 截图并裁剪
            img = snapshot_write(write_name, LT=LT, RB=RB)
            if img is None or not isinstance(img, np.ndarray):
                print("snapshot_write 返回无效图像，跳过...")
                continue
            image_list.append(img)
            print(f"已获取第 {len(image_list)} 张截图")

            # 滑动
            if direction == "vertical":
                # 执行滑动，竖直方向
                air_swipe_fast(start_pos, delta_y=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)
            elif direction == "horizontal":
                # 执行滑动，水平方向
                air_swipe_fast(start_pos, delta_x=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)

            # 当有至少两张图时，开始判断是否重复（触底）
            if len(image_list) >= 2:
                prev_img = image_list[-2]
                curr_img = image_list[-1]
                # 判断是否为相同图像
                if is_images_similar(prev_img, curr_img, threshold=ssim_threshold):
                    # print("检测到图像重复，已触底，停止滑动。")
                    monitor_task_status_v2("触底检测", "检测到图像重复，已触底，停止滑动。")
                    # 删除最后一张重复图
                    image_list.pop()
                    break

    except Exception as e:
        print(f"捕获过程中发生异常: {e}")
        # 出错时也尝试拼接已有图像
        pass
    # 确保至少有一张图
    if len(image_list) == 0:
        raise ValueError("未能获取任何有效截图")

    return len(image_list)



# =======================================================================
# 以下函数是为上面函数服务的
class Direction(Enum):
    """
    滑动和拼接方向
    """
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


def is_images_similar(img1: np.ndarray, img2: np.ndarray, threshold: float = 0.95) -> bool:
    """
    判断两张图像是否高度相似（基于灰度 SSIM）

    Args:
        img1, img2: np.ndarray, BGR 或灰度图
        threshold: SSIM 阈值，> threshold 认为相似

    Returns:
        bool: 是否相似
    """
    # 转为灰度图
    if len(img1.shape) == 3:
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    else:
        gray1 = img1

    if len(img2.shape) == 3:
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    else:
        gray2 = img2

    # 调整大小一致（防止因裁剪微小差异导致错误）
    if gray1.shape != gray2.shape:
        h = min(gray1.shape[0], gray2.shape[0])
        w = min(gray1.shape[1], gray2.shape[1])
        gray1 = cv2.resize(gray1, (w, h))
        gray2 = cv2.resize(gray2, (w, h))

    # 计算 SSIM
    score, _ = ssim(gray1, gray2, full=True)
    return score >= threshold

def stitch_images_del_replic(image_list: List[np.ndarray], direction: str = 'horizontal') -> np.ndarray:
    """
    拼接一组有序图像，自动去除重叠区域，实现无缝拼接。

    Args:
        image_list: list of np.ndarray, 有序图像列表
        direction: 'horizontal' 或 'vertical'

    Returns:
        拼接后的图像 (np.ndarray)
    """
    if len(image_list) == 0:
        raise ValueError("image_list 不能为空")
    if len(image_list) == 1:
        return image_list[0]

    # 确保所有图像为三通道（便于处理）
    def to_bgr(img):
        if len(img.shape) == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 1:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img.copy()

    images = [to_bgr(img) for img in image_list]

    # 转换方向为 OpenCV 拼接方向（默认支持左右）
    if direction == 'vertical':
        # 将每张图转置，拼接完再转回来
        images = [cv2.transpose(img) for img in images]
    elif direction != 'horizontal':
        print("direction 必须是 'horizontal' 或 'vertical'")

    stitched = images[0]
    sift = cv2.SIFT_create()
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    print("测试点1")
    for i in range(1, len(images)):
        prev_gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY)

        # 提取特征点
        kp1, des1 = sift.detectAndCompute(prev_gray, None)
        kp2, des2 = sift.detectAndCompute(curr_gray, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            print(f"第 {i} 对图像特征点不足，尝试直接拼接（无去重叠）")
            # 回退：简单水平拼接
            stitched = np.hstack([stitched, images[i]])
            continue

        # 匹配特征点
        matches = bf.knnMatch(des1, des2, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)

        if len(good_matches) < 4:
            print(f"匹配点不足，使用简单拼接")
            stitched = np.hstack([stitched, images[i]])
            continue
        print("测试点2")
        # 提取匹配点坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])

        # 计算单应矩阵（变换关系）
        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        if H is None:
            stitched = np.hstack([stitched, images[i]])
            continue
        print("测试点3")
        # 获取当前图像的四个角点
        h, w = images[i].shape[:2]
        corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        warped_corners = cv2.perspectiveTransform(corners, H)

        # 计算目标画布大小
        stitched_shape = stitched.shape
        min_x = min(0, warped_corners[:, 0, 0].min())
        max_x = max(stitched_shape[1], warped_corners[:, 0, 0].max())
        min_y = min(0, warped_corners[:, 0, 1].min())
        max_y = max(stitched_shape[0], warped_corners[:, 0, 1].max())
        print("测试点4")
        translation = np.array([[1, 0, -min_x],
                                [0, 1, -min_y],
                                [0, 0, 1]])
        H_translated = translation @ H

        # 透视变换当前图像
        warped = cv2.warpPerspective(images[i], H_translated,
                                     (int(max_x - min_x), int(max_y - min_y)))

        # 创建新的 stitched 图像画布
        new_stitched = np.zeros((int(max_y - min_y), int(max_x - min_x), 3), dtype=np.uint8)
        roi_h, roi_w = stitched.shape[:2]
        new_stitched[int(-min_y):int(-min_y) + roi_h, int(-min_x):int(-min_x) + roi_w] = stitched
        print("测试点5")
        # 融合两张图像（简单加权融合或最大值）
        mask1 = new_stitched > 0
        mask2 = warped > 0
        overlap = mask1 & mask2

        # 简单融合：重叠区域取平均
        fused = new_stitched.astype(np.float32)
        fused[overlap] = 0.5 * new_stitched[overlap] + 0.5 * warped[overlap]
        fused[~mask1 & mask2] = warped[~mask1 & mask2]
        print("测试点6")
        stitched = np.clip(fused, 0, 255).astype(np.uint8)
        print("测试点6-5")
    print("测试点7")
    # 如果是 vertical 模式，转置回来
    if direction == 'vertical':
        stitched = cv2.transpose(stitched)
    print("拼接成功")
    return stitched

def stitch_images_without_del_replic(image_list, direction='vertical'):
    """
    将图像列表按指定方向拼接成一张大图

    :param image_list: list of np.ndarray, 每个元素是一张图像 (H, W, C) 或 (H, W)
    :param direction: str, 'horizontal' 或 'vertical'
    :return: np.ndarray, 拼接后的图像
    """
    if not image_list:
        raise ValueError("image_list 不能为空")

    if not isinstance(image_list, (list, tuple)):
        raise TypeError("image_list 必须是列表或元组")

    # 确保所有图像都是 np.ndarray
    for img in image_list:
        if not isinstance(img, np.ndarray):
            raise TypeError("image_list 中的每个元素都必须是 np.ndarray")

    # 统一维度：将灰度图 (H, W) 扩展为 (H, W, 1)
    expanded_images = []
    for img in image_list:
        if img.ndim == 2:
            img = np.expand_dims(img, axis=-1)  # (H, W) -> (H, W, 1)
        expanded_images.append(img)

    # 获取通道数（取第一张图的通道数作为参考）
    C = expanded_images[0].shape[2]

    # 检查所有图像通道数是否兼容（至少能广播）
    for i, img in enumerate(expanded_images):
        if img.shape[2] != C:
            # 如果通道数不同，尝试广播（比如 1 vs 3）
            if img.shape[2] == 1:
                expanded_images[i] = np.repeat(img, C, axis=2)
            elif C == 1:
                C = img.shape[2]
                expanded_images = [
                    np.repeat(img, C, axis=2) if img.shape[2] == 1 else img
                    for img in expanded_images
                ]
            else:
                raise ValueError(f"图像 {i} 的通道数 {img.shape[2]} 与其他图像不兼容")

    # 获取最大高度和宽度
    max_h = max(img.shape[0] for img in expanded_images)
    max_w = max(img.shape[1] for img in expanded_images)

    # 对齐图像尺寸：填充到相同大小（黑色填充）
    aligned_images = []
    for img in expanded_images:
        h, w, c = img.shape
        # 创建一个黑色背景（0 填充）
        aligned = np.zeros((max_h, max_w, c), dtype=img.dtype)
        aligned[:h, :w, :] = img
        aligned_images.append(aligned)

    # 拼接
    if direction == 'horizontal':
        # 水平拼接：左右排列
        stitched = np.concatenate(aligned_images, axis=1)  # 沿宽度方向拼接
    elif direction == 'vertical':
        # 垂直拼接：上下排列
        stitched = np.concatenate(aligned_images, axis=0)  # 沿高度方向拼接
    else:
        raise ValueError("direction 必须是 'horizontal' 或 'vertical'")

    return stitched


if __name__ == '__main__':
    image1 = cv2.imread('/Users/weizun/logs/test1.png')
    image2 = cv2.imread('/Users/weizun/logs/test2.png')
    image3 = cv2.imread('/Users/weizun/logs/test3.png')
    image4 = cv2.imread('/Users/weizun/logs/test4.png')
    image5 = cv2.imread('/Users/weizun/logs/test5.png')
    image6 = cv2.imread('/Users/weizun/logs/test6.png')
    # result = stitch_images([image1, image2,image3,image4,image5,image6], direction='vertical')
    # cv2.imwrite('seamless_result.png', result)