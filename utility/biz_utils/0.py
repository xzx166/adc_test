# LEFT = 0
# RIGHT = 0
#
#
#
# LEFT_TOP     = (34, 200)    # 左上角坐标
# RIGHT_BOTTOM = (373, 970)   # 右下角坐标
# LEFT2LEFT    = 411 - LEFT_TOP[0]    # 单列左侧到下一列左侧距离
# TOP2TOP      = 1040 - LEFT_TOP[1]   # 单列顶部到下一列顶部距离
# # 开始滑动接触点
# START_POINT = (2120, 1150)
# # 滑动距离
# SWIPE_DELTA = -1048.15
# width = RIGHT_BOTTOM[0] - LEFT_TOP[0]
# height = RIGHT_BOTTOM[1] - LEFT_TOP[1]
# spacing_x = LEFT2LEFT - width
# spacing_y = TOP2TOP - height
#
#
#
#
#
# model2 = CropIndividualModel(
#     swipe_start_pos = START_POINT,
#     swipe_end_pos = (START_POINT[0], START_POINT[1] + SWIPE_DELTA),
#     # check_bottom_start, check_bottom_end  用于确定底部的截图坐标
#     check_bottom_start = (LEFT_TOP[0], LEFT_TOP[1] + TOP2TOP),
#     check_bottom_end = (LEFT_TOP[0] + LEFT2LEFT * 4 + width, 1350),
#     # crop_data 每个单独截图的对象的信息，包括：x坐标，y坐标，宽，高，间隔x，间隔y，横向的数量，纵向滑动的数量
#     crop_data = (LEFT_TOP[0], LEFT_TOP[1], width, height, spacing_x, spacing_y, 5, 1),
#     # bottom_origin_pos 滑动到底部后的可能的第一行的x,y坐标（底部可能的第一行指：底部的纵向滑动数量的倒数行）
#     bottom_origin_pos = (LEFT_TOP[0], 560),
#     # combine_part_name  用于区分不同组截图的名称
#     combine_part_name = "Fashion2",
#     # check_normal_image_func 用于判断截图是否正常,入参是img对象，返回值是bool值
#     check_normal_image_func = ,
#     check_normal_image_continue = Flase,
#     # seperate_count  用于确定需要几次完成一个纵向滑动的数量
#     seperate_count = 1,
#     max_swipe_count = None,
#     bottom_confidence = None
# )
# swipe_crop_individual_by_model(model2)

# import itertools
#
#
# def image_split_generator(LT, L2L=0, T2T=0, width=1, height=1, cols=0, rows=0):
#     for row in range(rows) if rows else itertools.count():
#         top = LT[1] + T2T * row
#         # if top > size[1]: break
#         for col in range(cols) if cols else itertools.count():
#             left = LT[1] + L2L * col
#             # if left > size[0]: break
#             lt = (left, top)
#             rb = (lt[0] + width, lt[1] + height)
#             # if rb[0] <= size[0] and rb[1] <= size[1]:
#             print(lt, rb)
#             # else: break
#             if not L2L: break
#         if not T2T: break
#
# image_split_generator((0, 0), L2L=50, T2T=50, width=10, height=10, cols=5, rows=1)

# for row, col in itertools.product(itertools.count(), itertools.count()):
#     print(col, row)


# 图像增强
# import numpy as np
# import cv2
#
# def ComputeMinLevel(hist, pnum):
#     index = np.add.accumulate(hist)
#     return np.argwhere(index>pnum * 8.3 * 0.01)[0][0]
#
# def ComputeMaxLevel(hist, pnum):
#     hist_0 = hist[::-1]
#     Iter_sum = np.add.accumulate(hist_0)
#     index = np.argwhere(Iter_sum > (pnum * 2.2 * 0.01))[0][0]
#     return 255-index
#
# def LinearMap(minlevel, maxlevel):
#     if minlevel >= maxlevel:
#         return []
#     else:
#         index = np.array(list(range(256)))
#         screenNum = np.where(index<minlevel,0,index)
#         screenNum = np.where(screenNum> maxlevel,255,screenNum)
#         for i in range(len(screenNum)):
#             if 0 < screenNum[i] < 255:
#                 screenNum[i] = (i - minlevel) / (maxlevel - minlevel) * 255
#         return screenNum
#
# def CreateNewImg(img):
#     h, w, d = img.shape
#     newimg = np.zeros([h, w, d])
#     for i in range(d):
#         imghist = np.bincount(img[:, :, i].reshape(1, -1)[0])
#         minlevel = ComputeMinLevel(imghist,  h * w)
#         maxlevel = ComputeMaxLevel(imghist, h * w)
#         screenNum = LinearMap(minlevel, maxlevel)
#         if screenNum.size == 0:
#             continue
#         for j in range(h):
#             newimg[j, :, i] = screenNum[img[j, :, i]]
#     return newimg


# if __name__ == '__main__':
#     img = cv2.imread('/Users/vip/Downloads/1722277576089.png')
#     newimg = CreateNewImg(img)
#     cv2.imshow('original_img', img)
#     cv2.imshow('new_img', newimg / 255)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()


# img = cv2.imread('/Users/vip/Downloads/1722277576089.png', 0)
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
# cl1 = clahe.apply(img)
#
# cv2.imshow('img',img)
# cv2.imshow('cl1',cl1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# img = cv2.imread('/Users/vip/Downloads/1722277576089.png', 0)
# equ = cv2.equalizeHist(img) # 只能传入灰度图
#
# res = np.hstack((img,equ))  # 图像列拼接（用于显示）
#
# cv2.imshow('res',res)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# image = cv2.imread('/Users/vip/Downloads/1722277576089.png')
# image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
# image = np.power(image / 255, 10) * 255
# image = cv2.convertScaleAbs(image, alpha=5, beta=30)
#
# cv2.imwrite('/Users/vip/Downloads/1.png', image)

# cv2.namedWindow("image", cv2.WINDOW_NORMAL)
# cv2.imshow("O", image)
# cv2.waitKey(10000)
# cv2.destroyAllWindows()
"""
╔═══════════════════════════════╗
║                               ║
║                               ║
║                               ║
║                               ║
║                               ║
║                               ║
║                               ║
║                               ║
║                               ║
╚═══════════════════════════════╝
"""