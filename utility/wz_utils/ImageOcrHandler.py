from airtest.core.api import *
using("../utility/biz_utils")
from biz_utils import (ST,OPJ,timeStamp,ocr_num_by_eas,ocr_image_by_eas,ocr_chinese_by_eas,box2pos,
                       monitor_task_status_v2,lx_break_runloop,traceback,image_size,np,screenshot,
                       SCREENSIZE,EditImage,cv2,sleep)


class ImageAllOcrRemote:
    """
    OCR识别Remote，返回结果格式[ocr_result:pos,...]
    根据biz_utils.py中的ImageOcrRemote修改
    由于原有的只能根据屏幕大小处理，如果不是，就截图，但是我的需求只要大面积识别的内容
    所以进行修改，并改名为ImageAllOcrRemote，修改代码，只要图片即可，不过返回的pos不准，没法使用
    同时，如果没传image，就会截图使用
    """
    def __init__(self, LT=None, RB=None, area=None, image=None, en_ocr=False, model=None):
        """
        OCR识别Remote
        :param LT:
        :param RB:
        :param image:
        :param en_ocr:
        """
        self.LT = LT
        self.RB = RB
        self.area = area
        self.IMAGE = image
        self.EN_OCR = en_ocr
        self.model = model
        self.wirte_path = OPJ(ST.LOG_DIR, f'image_ocr_remote_{timeStamp()}.jpg')

        if not (self.LT or self.RB) and self.area:
            self.LT = self.area[0], self.area[1]
            self.RB = self.area[2], self.area[3]

    def image_ocr_remote(self):
        for i in range(3):
            try:
                if self.EN_OCR:
                    ocrResult = ocr_num_by_eas(self.wirte_path)
                elif self.model:
                    ocrResult = ocr_image_by_eas(self.wirte_path, self.model)
                else:
                    ocrResult = ocr_chinese_by_eas(self.wirte_path)
                result = []
                LT = self.LT or (0, 0)
                for j in ocrResult or []:
                    pos = box2pos(j["box"][0], j["box"][2])
                    result.append((j["txts"], (pos[0] + LT[0], pos[1] + LT[1])))
                # os.remove(self.wirte_path)
                return result
            except Exception:
                if i == 2:
                    monitor_task_status_v2("Remote ocr failed", f"{traceback.format_exc()}", status=10127)
                    lx_break_runloop(desc="Remote ocr failed")
                else:
                    sleep(2)

    def __call__(self):
        if self.LT and self.RB:
            if isinstance(self.IMAGE, np.ndarray):
                image = self.IMAGE
            else:
                image = screenshot()
            cropped_image = EditImage(image)(self.LT, self.RB)
            cv2.imwrite(self.wirte_path, cropped_image)
            return self.image_ocr_remote()

        elif isinstance(self.IMAGE, np.ndarray):
            cv2.imwrite(self.wirte_path, self.IMAGE)
            return self.image_ocr_remote()