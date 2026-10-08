import cv2
import numpy as np
import os

def crop_black_borders(img):
    """裁剪图像四周的黑边"""
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    coords = cv2.findNonZero(gray)
    if coords is None or len(coords) == 0:
        return img
    x, y, w, h = cv2.boundingRect(coords)
    return img[y:y+h, x:x+w]

def resize_and_pad(img, target_height):
    """
    将图像垂直居中填充到指定高度
    """
    h, w = img.shape[:2]
    if h == target_height:
        return img
    pad_top = (target_height - h) // 2
    pad_bottom = target_height - h - pad_top
    color = [0, 0, 0]  # 黑色填充
    padded = cv2.copyMakeBorder(img, pad_top, pad_bottom, 0, 0, cv2.BORDER_CONSTANT, value=color)
    return padded

def stitch_group(group_images, direction='horizontal'):
    """
    拼接一组图像（使用 SIFT + Homography）
    """
    if len(group_images) == 0:
        return None
    if len(group_images) == 1:
        return group_images[0].copy()

    def to_bgr(img):
        if len(img.shape) == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 1:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            return img.copy()

    images = [to_bgr(img) for img in group_images]

    # 如果是纵向拼接，先旋转
    if direction == 'vertical':
        images = [cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) for img in images]

    result = images[0].copy()
    sift = cv2.SIFT_create()
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    for i in range(1, len(images)):
        img1 = result
        img2 = images[i]

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        kp1, des1 = sift.detectAndCompute(gray1, None)
        kp2, des2 = sift.detectAndCompute(gray2, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            print(f"[组内] 特征点不足，直接水平拼接第 {i} 张")
            result = np.hstack([result, img2])
            continue

        matches = flann.knnMatch(des1, des2, k=2)
        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]

        if len(good_matches) < 4:
            print(f"[组内] 匹配点不足，直接拼接第 {i} 张")
            result = np.hstack([result, img2])
            continue

        pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches])

        H, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC, 4.0)
        if H is None:
            print(f"[组内] 单应矩阵估计失败，直接拼接第 {i} 张")
            result = np.hstack([result, img2])
            continue

        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        corners = np.array([[0,0], [w2,0], [w2,h2], [0,h2]], dtype=np.float32).reshape(-1, 1, 2)
        warped_corners = cv2.perspectiveTransform(corners, H)
        all_corners = np.concatenate((warped_corners,
                                      np.array([[0,0], [w1,0], [w1,h1], [0,h1]]).reshape(-1,1,2)), axis=0)
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)

        translation_dist = [-x_min, -y_min]
        H_trans = np.eye(3)
        H_trans[0, 2] = translation_dist[0]
        H_trans[1, 2] = translation_dist[1]

        warped = cv2.warpPerspective(img2, H_trans @ H, (x_max - x_min, y_max - y_min))

        # 扩展 warped 空间以放入 result
        h_w, w_w = warped.shape[:2]
        h_r = result.shape[0] + translation_dist[1]
        w_r = result.shape[1] + translation_dist[0]
        if h_w < h_r or w_w < w_r:
            h_new = max(h_w, h_r)
            w_new = max(w_w, w_r)
            temp = np.zeros((h_new, w_new, 3), dtype=np.uint8)
            temp[:h_w, :w_w] = warped
            warped = temp

        warped[translation_dist[1]:translation_dist[1]+result.shape[0],
               translation_dist[0]:translation_dist[0]+result.shape[1]] = result
        result = warped
        result = crop_black_borders(result)

    if direction == 'vertical':
        result = cv2.rotate(result, cv2.ROTATE_90_COUNTERCLOCKWISE)

    return result


def stitch_image_sequence(image_list, direction='horizontal', group_size=5):
    """
    分组拼接图像序列：
    1. 每 group_size 张图拼成一个子图
    2. 所有子图统一高度后拼接成最终图

    参数:
        image_list: list of np.ndarray, 图像列表
        direction: 'horizontal' 或 'vertical'
        group_size: 每组图像数量（默认5）

    返回:
        final_result: 拼接后的长图
    """
    if not image_list:
        raise ValueError("image_list 不能为空")

    # 切分为组
    groups = [image_list[i:i + group_size] for i in range(0, len(image_list), group_size)]
    print(f"共 {len(image_list)} 张图像，分为 {len(groups)} 组，每组最多 {group_size} 张")

    # 第一步：每组内部拼接
    stitched_groups = []
    for idx, group in enumerate(groups):
        print(f"\n👉 正在拼接第 {idx + 1} 组（{len(group)} 张图像）...")
        try:
            group_img = stitch_group(group, direction=direction)
            if group_img is not None and group_img.size > 0:
                stitched_groups.append(group_img)
            else:
                print(f"⚠️ 第 {idx + 1} 组拼接结果为空，跳过")
        except Exception as e:
            print(f"❌ 第 {idx + 1} 组拼接异常: {e}")
            # 备用：直接水平拼接
            if len(group) == 1:
                stitched_groups.append(group[0].copy())
            else:
                fallback = group[0].copy()
                for i in range(1, len(group)):
                    # 补齐高度再拼
                    if fallback.shape[0] != group[i].shape[0]:
                        target_h = max(fallback.shape[0], group[i].shape[0])
                        fallback = resize_and_pad(fallback, target_h)
                        img_i = resize_and_pad(group[i], target_h)
                    else:
                        img_i = group[i]
                    fallback = np.hstack([fallback, img_i])
                stitched_groups.append(fallback)

    if not stitched_groups:
        raise ValueError("所有组拼接均失败")

    # 第二步：统一所有子图高度，然后拼接
    print(f"\n👉 正在拼接 {len(stitched_groups)} 个子图...")

    # 获取最大高度
    max_height = max(img.shape[0] for img in stitched_groups)
    for item in stitched_groups:
        print(f"子图 {item.shape}")

    # 所有子图居中填充到 max_height
    padded_groups = [resize_and_pad(img, max_height) for img in stitched_groups]

    # 水平拼接所有子图
    try:
        # final_result = np.hstack(padded_groups)
        final_result = stitch_group(padded_groups, direction=direction)
    except Exception as e:
        print(f"❌ hstack 拼接失败: {e}")
        # 手动拼接（容错）
        final_result = padded_groups[0]
        for i in range(1, len(padded_groups)):
            if final_result.shape[1] != padded_groups[i].shape[1]:
                print(f"⚠️ 尺寸不匹配，尝试对齐: {final_result.shape} vs {padded_groups[i].shape}")
            final_result = np.hstack([final_result, padded_groups[i]])

    # 最终裁剪黑边
    final_result = crop_black_borders(final_result)
    return final_result
