import cv2
import numpy as np


def stitch_image_sequence(image_list, direction='horizontal'):
    """
    将图像序列按顺序拼接成一张长图。

    参数:
        image_list: list of np.ndarray, 图像列表 (BGR or Grayscale)
        direction: 'horizontal' or 'vertical'

    返回:
        stitched: np.ndarray, 拼接后的图像
    """
    if len(image_list) == 0:
        raise ValueError("image_list 不能为空")

    # 统一转换为三通道图像（便于处理）
    def to_bgr(img):
        if len(img.shape) == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 1:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 3:
            return img.copy()

    images = [to_bgr(img) for img in image_list]

    # 如果是纵向拼接，先将所有图像顺时针旋转90度，横向拼接后再转回来
    if direction == 'vertical':
        images = [cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) for img in images]

    # 初始化结果图像
    result = images[0]

    # SIFT 特征检测器
    sift = cv2.SIFT_create()
    # FLANN 匹配器
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    for i in range(1, len(images)):
        print(f"正在拼接第 {i} 张图像...")
        img1 = result
        img2 = images[i]

        # 转为灰度图提取特征
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        kp1, des1 = sift.detectAndCompute(gray1, None)
        kp2, des2 = sift.detectAndCompute(gray2, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            print(f"特征点不足，跳过第 {i} 张")
            # 直接水平拼接（备用）
            result = np.hstack([result, img2])
            continue

        # 特征匹配
        matches = flann.knnMatch(des1, des2, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)

        if len(good_matches) < 4:
            print(f"匹配点不足，跳过第 {i} 张")
            result = np.hstack([result, img2])
            continue

        # 提取匹配点
        pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches])

        # 估计单应性矩阵（使用 RANSAC）
        H, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC, 4.0)

        if H is None:
            print(f"单应矩阵估计失败，跳过第 {i} 张")
            result = np.hstack([result, img2])
            continue

        # 计算 warp 后的尺寸
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        corners = np.array([
            [0, 0],
            [w2, 0],
            [w2, h2],
            [0, h2]
        ], dtype=np.float32).reshape(-1, 1, 2)
        warped_corners = cv2.perspectiveTransform(corners, H)
        all_corners = np.concatenate((warped_corners, np.array([[0, 0], [w1, 0], [w1, h1], [0, h1]]).reshape(-1, 1, 2)),
                                     axis=0)

        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)

        # 平移矩阵
        translation_dist = [-x_min, -y_min]
        H_trans = np.array([[1, 0, translation_dist[0]],
                            [0, 1, translation_dist[1]],
                            [0, 0, 1]])

        # warp 图像2
        warped = cv2.warpPerspective(img2, H_trans @ H, (x_max - x_min, y_max - y_min))

        # 将原图 result 放到 warp 后的画布上
        result_width = result.shape[1] + translation_dist[0]
        result_height = result.shape[0] + translation_dist[1]
        if warped.shape[0] < result_height or warped.shape[1] < result_width:
            # 扩展 warped 尺寸
            h, w = max(warped.shape[0], result_height), max(warped.shape[1], result_width)
            temp = np.zeros((h, w, 3), dtype=np.uint8)
            temp[:warped.shape[0], :warped.shape[1]] = warped
            warped = temp

        # 将 result 放到 warped 画布上
        warped[translation_dist[1]:translation_dist[1] + result.shape[0],
        translation_dist[0]:translation_dist[0] + result.shape[1]] = result

        # 更新 result
        result = warped

        # 可选：裁剪黑边（可注释掉以提高速度）
        result = crop_black_borders(result)

    # 如果是纵向拼接，最后旋转回来
    if direction == 'vertical':
        result = cv2.rotate(result, cv2.ROTATE_90_COUNTERCLOCKWISE)

    return result


def crop_black_borders(img):
    """裁剪图像黑边"""
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    coords = cv2.findNonZero(gray)
    if coords is None:
        return img
    x, y, w, h = cv2.boundingRect(coords)
    return img[y:y + h, x:x + w]
