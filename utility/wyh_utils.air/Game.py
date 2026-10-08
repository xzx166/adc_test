from airtest.core.api import *

using("../utility/biz_utils")
from LLM import remote_ds_r1_reasoning_copy, parse_model_output_to_json_copy

using("../utility/monitor.air")
from monitor import *

using("../utility/api.air")
from api import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/mask.air")
from mask import *

using("../utility/swipe.air")
from swipe import *

using("../utility/image.air")
from image import *

using("../utility/ocr.air")
from ocr import *

using("../utility/biz_foundation.air")
from biz_foundation import *

using("../utility/app")
from adc_phase import Phase


class GameMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)

        # 基类不注册Phase
        if name == "Game":
            return cls

        try:
            instance = cls()
        except Exception as exc:
            raise RuntimeError(f"无法实例化 {name}，请检查 __init__ 是否需要额外参数") from exc

        cls.phase_list = []

        # 注册所有带 @phase 的方法
        for attr_name, value in attrs.items():
            if callable(value) and hasattr(value, '_phase_name'):
                method_name = attr_name
                # noinspection PyProtectedMember
                phase_name = value._phase_name
                bound_method = getattr(instance, method_name)

                phase_obj = Phase(phase_name, bound_method)
                cls.phase_list.append(phase_obj)
        return cls


class Game(metaclass=GameMeta):
    """
        游戏自动化基类，所有具体游戏应继承此类。
    """
    def __init__(self, env=None):
        self.env = env if env else AppEnv.get_instance()
        self.sys_prompt = "你是一个ocr助手，可以帮助用户精准识别图片中的文字，并按照用户意愿，将识别出的文字以指定的格式返回，"

    def llm_ocr(self, image_url: str, prompt: str):
        message = [
            {"role": "system", "content": [{"text": self.sys_prompt}]},
            {"role": "user", "content": [{"image": image_url}, {"text": prompt}]}
        ]

        area_server_res = remote_ds_r1_reasoning_copy(input_content=message, model="qwen-vl-max")
        area_server_dict = parse_model_output_to_json_copy(area_server_res)
        return area_server_dict

