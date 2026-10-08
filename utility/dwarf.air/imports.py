from airtest.core.api import *

using("../utility/api.air")
from api import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/monitor.air")
from monitor import *

using("../utility/adc_request.air")
from adc_request import *

using("../utility/upload.air")
from upload import *

using("../utility/ocr.air")
from ocr import *

using("../utility/mask.air")
from mask import *

using("../utility/image.air")
from image import *

using("../utility/upload.air")
from upload import *

using("../utility/swipe.air")
from swipe import *

using("../utility/phase.air")
from phase import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/biz_foundation.air")
from biz_foundation import *

using("../utility/dwarf.air")
from dwarf import *

env = AppEnv.get_instance()
is_fabu = True if env.taskType == 2 else False
package_name = env.get_common_property_with_key('jymPackageName')
platform = AppEnv.get_instance().get_common_property_with_key('gamePlatform')
game_area = AppEnv.get_instance().game_area
username = AppEnv.get_instance().username
phase_list = []


def add_phase(phase_name, task_type=None):
    """加上这个装饰器的Phase才会进入执行流程"""

    def decorator(func):
        if task_type and task_type == "fabu" and is_fabu:
                phase_list.append(Phase(phase_name, lambda: func(AppEnv.get_instance())))
        elif task_type and task_type == "index" and not is_fabu:
                phase_list.append(Phase(phase_name, lambda: func(AppEnv.get_instance())))
        else:
            phase_list.append(Phase(phase_name, lambda: func(AppEnv.get_instance())))

        def wapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wapper

    return decorator


def close_vpn():
    try:
        shell('am start-foreground-service -a "stop" -n com.jym.x.engine.app/com.ssrlive.socksdroid.VpnStarterService')
    except:
        pass