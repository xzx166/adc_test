from typing import List, Iterable
from utility.app.service.adc_ocr import ocr_image_by_eas
from utility.base.adc_monitor import monitor_print


# def image_upload(write_name="image", image: np.ndarray=None, LT: Union[Tuple, List]=None, RB: Union[Tuple, List]=None, local_save=False):
#     """
#     上传图片对象
#     :param write_name: 写入名称
#     :param image: 图片对象
#     :param LT: 左上裁剪
#     :param RB: 右下裁剪
#     :param local_save: 本地测试时不上传oss
#     :return: [0]：不含http；[1]：含http
#     """
#     filepath = ""
#     if isinstance(image, np.ndarray):
#         write_name, ext = OP.splitext(write_name)
#         filepath = OPJ(ST.LOG_DIR, f"upload_{write_name}_{timeStamp()}{ext or '.jpg'}")
#         # 把图片又保存的一份在log下
#         cv2.imwrite(filepath, EditImage(image)(LT, RB))
#     else:
#         lx_break_runloop(desc="image upload empty")
#
#     for i in range(3):
#         try:
#             if not (local_save and localRun):
#                 oss_pathes, cdn_url_list = upload_jym_oss_with_pathes([filepath])
#                 return oss_pathes[0], cdn_url_list[0]
#             else:
#                 return filepath, filepath
#         except Exception:
#             if i == 2:
#                 monitor_task_status_v2("Image upload failed", f"{traceback.format_exc()} - {write_name}", status=10011)
#                 lx_break_runloop(desc="Image upload failed")
#             else:
#                 sleep(2)

# 注意type的类型对应不同的识别模型
# 1是旧的包含异形字的ocr模型，
# 2是中英数综合模型，通用的识别模型，实测针对标准字体类型2的识别率高很多
# 3是英文数字模型
# 4是中英数轻量模型（中文识别精度高，识别快，如果ocr_ch识别不到，可以尝试该模型）
# def ocr_image_by_eas(crop_pos_img_path, type=1, upload_image_log_tag=None):
#     monitor_print(f'---ocr_image_by_eas: {crop_pos_img_path}, type:{type}')
#     env = AppEnv.get_instance()
#
#     # cropFileName = f'crop_{cropFileName}' + str(int(time.time() * 1000000)) + '.jpg'
#     #
#     # crop_pos_img = crop_pos_image_from_snapshot(f"temp.jpg", cropFileName, crop_start, crop_end)
#
#     # item_full_path = os.path.join(ST.LOG_DIR, cropFileName)
#
#     def get_env_ocr_path(env, type=1):
#         scriptEnv = env.scriptEnv
#         risk_path = ""
#         launch_type = env.launchType
#         if launch_type == 'localtest':
#             scriptEnv = 'local'
#
#         if type == 1:
#             if (scriptEnv == 'local'):
#                 risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
#             elif (scriptEnv == 'pre'):
#                 risk_path = '/api/predict/lingxialgo_vision_adc'
#             elif (scriptEnv == 'prod'):
#                 risk_path = '/api/predict/lingxialgo_vision_adc'
#             else:
#                 risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
#         else:
#             if (scriptEnv == 'local'):
#                 risk_path = "/api/predict/lingxialgo_ocr_service_pre"
#             elif (scriptEnv == 'pre'):
#                 risk_path = "/api/predict/lingxialgo_ocr_service_pre"
#             elif (scriptEnv == 'prod'):
#                 risk_path = '/api/predict/lingxialgo_vision_ocr'
#             else:
#                 risk_path = '/api/predict/lingxialgo_ocr_service_pre'
#
#         monitor_print(f'---get_env_ocr_path: {risk_path}, type:{type}, env:{scriptEnv}')
#         return risk_path


def ocr_result_list2str(ocr_result_list, *args):
    text = "".join(map(lambda x: x["txts"], ocr_result_list or [])).strip()
    monitor_print(f"---ocr_result_list2str: {text} {''.join(map(str, args))}".strip())
    return text

def multi_model_ocr(imageurl: str, options, match_func=None):
    """
    多模型文字识别
    :param imageurl: 图片链接
    :param options: 匹配项
    :param match_func: 匹配方法
    :return: 识别结果
    状态码说明:
    1: 识别正确
    2: 模型识别一致, 但是结果不在匹配项中
    0: 模型识别不一致
    -1: 识别结果为空
    """
    wrong_list = []
    match_item = None
    for model in [2, 1, 4]:
        ocr_result_list = ocr_image_by_eas(imageurl, type=model)
        ocr_result = ocr_result_list2str(ocr_result_list)
        # if not ocr_result:
        #     continue
        if ocr_result in options:
            return {"status": 1, "result": ocr_result}
        elif callable(match_func):
            match_item = match_func(ocr_result)
            if isinstance(match_item, str):
                if match_item in options:
                    return {"status": 1, "result": match_item}
                elif match_item != ocr_result:
                    return {"status": 2, "result": match_item}

            elif isinstance(match_item, Iterable):
                for i in match_item:
                    if i in options:
                        return {"status": 1, "result": i}

        if ocr_result and ocr_result not in wrong_list:
            wrong_list.append(ocr_result)

    if wrong_list:
        # 使用替换匹配项
        if isinstance(match_item, str):
            return {"status": 2, "result": match_item}
        # 模型识别一致
        elif len(wrong_list) == 1:
            return {"status": 2, "result": wrong_list[0]}
        # 模型识别不一致
        else:
            return {"status": 0, "result": wrong_list[0], "wrong_list": wrong_list}
    else:
        return {"status": -1, "result": "", "wrong_list": []}
