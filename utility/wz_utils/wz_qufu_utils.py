from enum import Enum
from typing import Union

"""
qufu工具包模块：
@作用：提供了一个统一使用的接口工具包，对其他工具包中的代码进行了再封装，以便进行阅读。
@说明：
1.函数前加wz_是为了进行代码提示。
2.对于引入模块的方式:
    a.如果在最上方使用from <module> import <method>的方式会出现，别的包饮用这个工具类，也会显示<method>的情况。
    b.如果在最上方使用import <module>，在使用的时候用<module>.<method>的方式，会出现把module中函数外的变量导入的情况。
    所以，使用的方式是在函数内导入，这样在别的包中引用的时候，就不会出现上述的问题。
3.对于方法中使用is_开头的是bool类型。
@作者: 唯樽
"""

from adc_monitor import PRINT_LEVEL as MONITOR_PRINT_LEVEL
def wz_monitor_print(desc, timestamp=None, level=MONITOR_PRINT_LEVEL.INFO):
    """
    由于底层使用的方法是对比的level，而不是level的value值，所以需要做一个as封装一下，也可以直接使用
    作用：打印日志
    :param desc:打印内容
    :param timestamp:时间戳，如果为空，就使用当前时间戳
    :param level:打印日志级别，默认为INFO，蓝色
    INFO：蓝色；DEBUG：绿色；WARN：黄色；ERROR：红色
    INFO是自己写的代码打印的，DEBUG是框架打印的，后面两个可以自己调整
    :return:
    """
    from adc_monitor import monitor_print
    monitor_print(desc, timestamp, level=level)

def wz_monitor_task_status_print(title, desc="", status=None):
    """
    作用：打印任务日志，级别为INFO，无法调整级别
    :param title:
    :param desc:
    :param status:
    :param level: 日志打印级别，默认为INFO
    :return:无返回结果
    """
    from adc_monitor import monitor_task_status_v2
    monitor_task_status_v2(title, desc, status)

def wz_get_remote_server_information(gameId, pullClientId):
    """
    获取远程区服信息
    :param gameId:
    :param pullClientId:
    :return: 返回的是服务器保存的区服信息
    """
    from biz_utils import download_server_list
    return download_server_list(gameId, pullClientId)

def wz_server_image_upload_to_oss(index, image):
    """
    拼接图的名称，上传图片对象,返回的是oss的url
    里面还会拼接一层，拼接的格式是upload_server-{index}_{timestamp}}.jpg
    :param index:int，指的是截的第几张图
    :param image:np.ndarray
    :return:oss返回的url
    """
    from biz_utils import image_upload
    return image_upload(f"server-{index}", image)[1]

def wz_push_diff_server_name_to_adc(game_id, platform, push_client_id,
                                 format_diff_remote_and_latest_server_name_list,
                                 server_images_oss_urls, status=0):
    """
    推送差异化信息给adc平台，需要审核
    :param game_id: 游戏id
    :param platform: 渠道
    :param push_client_id: 推送的远程客户端id
    :param format_diff_remote_and_latest_server_name_list: 格式化的差异区服信息
        数据说明：字典格式，字段存在serverName，syncAllClient，clientIdList，domainId，syncNewDomainName
            方式一：两个字段。serverName字段代表区服名称，syncAllClient为True代表全渠道同步
            方式二：两个字段。serverName字段代表区服名称，clientIdList为一个有pushClientId的列表
    :param server_images_oss_urls:区服图片oss_url
    :param status:平台状态管理，如果是0，就表示adc平台显示未提交，如果是1，就表示adc平台显示已提交，需要再做一个提交到交易猫平台的请求
    :return:
    """
    from biz_utils import update_server_list
    return update_server_list(
        game_id=game_id,
        # game_id="1000019",
        platform=platform,
        # platform="jiuyou",
        client_id=push_client_id,
        delta_qufu_data=format_diff_remote_and_latest_server_name_list,
        image_list=server_images_oss_urls,
        status=status
    )

def wz_push_diff_server_name_to_jym(game_id, format_diff_remote_and_latest_server_name_list):
    """
    和push_diff_server_name_to_adc相比，不用审核，直接提交到交易猫后台，避免了审核的步骤
    :param game_id: 游戏id
    :param format_diff_remote_and_latest_server_name_list: 格式化的差异区服信息
    :return:
    """
    from biz_utils import update_qufu_list_to_jym
    return update_qufu_list_to_jym(game_id, format_diff_remote_and_latest_server_name_list)

def wz_monitor_catch_image(
        title: str,
        desc="",
        filename="",
        status: Union[str, int] = None,
        image=None,
        is_catch=True,
        is_return_text_image=False,
        is_write_image_to_local=True,
        is_raise_exception=True,
        is_print_log=True,
        break_mode: Union[str, Enum] = None,
        is_hold_game=False,
        ):
    """
    作用：打印业务日志，并捕获当前设备的图片。
    monitor_catch的阅读性不太好，重新封装了一下。
    is_catch和is_raise_exception是两个大分支，后面的参数是在两个为True的情况下的操作。
    如果is_catch和is_raise_exception都是False，就相当什么也没干。
    :param title: 后台的日志文件中，分为title和desc
    :param desc: 后台的日志文件中，分为title和desc
    :param filename: 保存的文件名称
    :param status: 业务状态码
    :param image: 初始的np.array格式的image
    :param is_catch: 如果没有image，可以设置True，捕获当前设备的图片，下面的参数在此参数为True时生效
    :param is_return_text_image: 返回的image是否要带文字
    :param is_write_image_to_local: 是否将image保存本地，以便进行查看
    :param is_raise_exception: 是否检查抛出异常，下面的参数在此参数为True时生效
    :param is_print_log: 为True，就打印一条日志
    :param break_mode: 抛异常处理的类型格式
    :param is_hold_game: 是否设置游戏的动态状态AppDynamicInfo为开启
    :return:返回np.array格式的image
    """
    from biz_utils import monitor_catch
    return monitor_catch(title=title,
                         desc=desc,
                         filename=filename,
                         status=status,
                         image=image,
                         catch=is_catch,
                         return_text_image=is_return_text_image,
                         write_catch_image=is_write_image_to_local,
                         raise_exception=is_raise_exception,
                         printLog=is_print_log,
                         break_mode=break_mode,
                         hold_game=is_hold_game)

def wz_match_image(image_path,threshold=0.7):
    """
    由于使用lx_touch_wait和exist识别的时候会存在识别不准的问题，所以重新封装一个函数
    :param v: Template格式图片
    :param threshold: 匹配度的值，大于才返回
    :return: 找到合适的位置返回pos，找不到返回None
    """
    import time
    from adc_safe_base import lx_safe_snapshot
    import cv2
    import os
    from adc_monitor import monitor_print
    from airtest.core.settings import Settings as ST
    file_name = f'adc_catch_kit_match_in_{str(int(time.time() * 1000000))}.jpg'
    lx_safe_snapshot(filename=file_name, msg="get a snapshot.")
    img_path = os.path.join(ST.LOG_DIR, file_name)
    main_img = cv2.imread(img_path)
    main_img_gray = cv2.cvtColor(main_img, cv2.COLOR_BGR2GRAY)
    # samll_iamage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), v.filename)
    samll_iamage_path = image_path
    monitor_print(f"图片路径{img_path}")
    monitor_print(f"图片路径{samll_iamage_path}")
    small_img = cv2.imread(samll_iamage_path)

    small_img_gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
    # 进行模板匹配
    res = cv2.matchTemplate(main_img_gray, small_img_gray, cv2.TM_CCOEFF_NORMED)
    # 找到最大和最小值及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # 使用最大值位置作为匹配结果
    top_left = max_loc
    h, w = small_img_gray.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    pos = (top_left[0] + int(w / 2), top_left[1] + int(h / 2))
    print(max_val)
    # max_val是计算的匹配度
    if max_val < threshold:
        return None
    return pos


