import cv2
import numpy as np
from biz_utils import air_swipe_fast,snapshot_write,monitor_task_status_v2
from skimage.metrics import structural_similarity as ssim
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
    判底逻辑：基于灰度图的SSIM相似度判断。拼接使用原始彩色图像。

    Args:
        start_pos：滑动起始坐标 (x, y)
        direction: 'vertical' 或 'horizontal'
        write_name: 截图保存路径（会被覆盖）
        LT: 裁剪区域左上角 (x1, y1)
        RB: 裁剪区域右下角 (x2, y2)
        delta_pos：滑动增量（垂直为y变化，水平为x变化）
        duration: 滑动持续时间（毫秒）
        hold_sec: 滑动结束后的停留时间（秒）
        sec: 滑动之间的等待时间（秒）
        ssim_threshold：相似度阈值，默认0.95
        max_images: 最大截图数量，默认20

    Returns:
        stitched_image (np.ndarray): 拼接后的彩色长图
    """
    image_list = []  # 存储原始彩色图像用于拼接

    try:
        while len(image_list) < max_images:
            # 截图并裁剪
            img = snapshot_write(write_name, LT=LT, RB=RB)
            if img is None or not isinstance(img, np.ndarray):
                print("snapshot_write 返回无效图像，跳过...")
                continue

            # 确保是合法图像
            if img.size == 0:
                print("截图图像为空，跳过...")
                continue

            # 保存原始彩色图像（用于后续拼接）
            image_list.append(img.copy())
            print(f"已获取第 {len(image_list)} 张截图")

            # 只有在有至少两张图时才判断是否触底
            if len(image_list) >= 2:
                prev_img = image_list[-2]
                curr_img = image_list[-1]

                # 🔍 使用灰度图进行相似度判断
                gray_prev = cv2.cvtColor(prev_img, cv2.COLOR_BGR2GRAY)
                gray_curr = cv2.cvtColor(curr_img, cv2.COLOR_BGR2GRAY)

                # 计算 SSIM（结构相似性），基于灰度
                score, _ = cv2.SSIM(gray_prev, gray_curr)
                if score >= ssim_threshold:
                    monitor_task_status_v2("触底检测", f"检测到图像重复 (SSIM={score:.4f})，已触底，停止滑动。")
                    # 删除最后一张重复图（避免冗余）
                    image_list.pop()
                    break

            # 执行滑动（本次截图后触发下一次滑动）
            if direction == "vertical":
                air_swipe_fast(start_pos, delta_y=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)
            elif direction == "horizontal":
                air_swipe_fast(start_pos, delta_x=delta_pos, duration=duration, hold_sec=hold_sec, sec=sec)
            else:
                raise ValueError("direction 必须是 'vertical' 或 'horizontal'")

    except Exception as e:
        print(f"捕获过程中发生异常: {e}")
        # 出错时也尝试拼接已有图像
        pass

    # 确保至少有一张图
    if len(image_list) == 0:
        raise ValueError("未能获取任何有效截图")

    print(f"已完成采集，共 {len(image_list)} 张有效截图，开始拼接...")

    # 使用原始彩色图像进行拼接
    stitched_image = stitch_images_del_replic(image_list, direction=direction)
    return stitched_image






def stitch_images_del_replic(image_list, direction='vertical', sim_threshold=0.95):
    """
    对图像列表进行去重后拼接。

    去重依据：相邻图像的灰度 SSIM 相似度
    拼接依据：原始彩色图像

    Args:
        image_list (list of np.ndarray): 彩色图像列表（BGR）
        direction (str): 'vertical' 或 'horizontal'
        sim_threshold (float): SSIM 相似度阈值，超过则认为是重复帧

    Returns:
        stitched_image (np.ndarray): 拼接后的彩色长图
    """
    if not image_list:
        raise ValueError("图像列表为空，无法拼接")

    if len(image_list) == 1:
        return image_list[0].copy()

    # 存储去重后的彩色图像
    unique_images = [image_list[0]]

    # 转为灰度图用于比较
    prev_gray = cv2.cvtColor(image_list[0], cv2.COLOR_BGR2GRAY)

    for i in range(1, len(image_list)):
        curr_img = image_list[i]
        curr_gray = cv2.cvtColor(curr_img, cv2.COLOR_BGR2GRAY)

        # 计算 SSIM
        score = ssim(prev_gray, curr_gray)

        # 判断是否不重复
        if score < sim_threshold:
            unique_images.append(curr_img)
            prev_gray = curr_gray  # 更新上一帧灰度图
        else:
            print(f"[stitch] 第 {i + 1} 张图与前一张相似 (SSIM={score:.4f})，已跳过（去重）")
            continue

    if not unique_images:
        # 安全兜底
        unique_images = [image_list[0]]

    print(f"去重完成：原始 {len(image_list)} 张，保留 {len(unique_images)} 张")

    # 开始拼接
    if direction == "vertical":
        # 上下拼接：沿 axis=0 堆叠
        stitched_image = np.vstack(unique_images)
    elif direction == "horizontal":
        # 左右拼接：沿 axis=1 堆叠
        stitched_image = np.hstack(unique_images)
    else:
        raise ValueError("direction 必须是 'vertical' 或 'horizontal'")

    return stitched_image
