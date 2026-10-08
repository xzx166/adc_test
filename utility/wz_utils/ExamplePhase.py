


from airtest.core.api import *
using("../utility/biz_utils")
from biz_utils import air_exists,monitor_catch,BreakModeEnum,monitor_task_status_v2


class ExamplePhase:
    def __init__(self):
        pass

    def __call__(self, *args, **kwds):
        if self.judge_in_scene():
            pass
        else:
            monitor_catch("场景进入结果", "检测到为进入--场景失败",
                          break_mode=BreakModeEnum.runloop, status=10168)

    def judge_in_scene(self):
        if air_exists(Template()):
            return True
        return False

# 踢登类装饰器-有参数
# @decorate(params)cls: 等价于 decorate(params)(cls)
class TiDengJudge:
    def __init__(self, phase_name, template):
        """
        :param phase_name: phase的名称
        :param template: 判断踢登的图片
        """
        self.phase_name = phase_name
        self.template = template

    def __call__(self, cls):
        monitor_task_status_v2("踢登判断", f"{self.phase_name}踢登判断")
        # 类装饰器，这个func指的是类
        # 判断如果有踢登，就停止；如果没有，就正常返回类的实例
        def wrapper(*args, **kwds):
            if self.judge_is_tideng():
                monitor_catch(f"{self.phase_name}踢登判断", "检测到为踢登",
                              break_mode=BreakModeEnum.runloop, status=10010)
            else:
                return cls(*args, **kwds)
        return wrapper

    def judge_is_tideng(self):
        if air_exists(self.template):
            return True
        return False



# ===================装饰器示例===========================
# 注意：多个装饰器，包装是由下向上包装，执行是由上到下执行
# 规则：装饰器参数（可选）-> 函数名/类名 -> 函数参数/类参数（必填）
# @decorate 等价于 decorate(func)
# @decorate(params) 等价于 decorate(params)(func)
# 无参数函数装饰器-作用于函数
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper
# 有参数函数装饰器-作用于函数
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
# 无参数函数装饰器-作用于类
def add_hello_method(cls):
    cls.say_hello = lambda self: print(f"Hello from {self}")
    return cls
# 有参数函数装饰器-作用于类
def add_greeting(greeting="Hi"):
    def decorator(cls):
        def greet(self):
            print(f"{greeting}, I'm {self.name}")
        cls.greet = greet
        return cls
    return decorator
# 无参数类装饰器-作用于函数
class MyDecorator:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print("Before function call (class)")
        result = self.func(*args, **kwargs)
        print("After function call (class)")
        return result
# 有参数类装饰器-作用于函数
class Repeat:
    def __init__(self, times):
        self.times = times

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            for _ in range(self.times):
                result = func(*args, **kwargs)
            return result
        return wrapper
# 无参数类装饰器-作用于类
class AddStringMethod:
    def __init__(self, cls):
        self.cls = cls
        # 动态添加一个方法
        if not hasattr(self.cls, '__str__'):
            self.cls.__str__ = lambda self: f"Instance of {self.__class__.__name__}"

    def __call__(self, *args, **kwargs):
        # 返回原始类的实例（不做实例化过程的修改）
        return self.cls(*args, **kwargs)
# 有参数类装饰器-作用于类
class AddRepresentation:
    def __init__(self, include_attrs=None):
        self.include_attrs = include_attrs or []

    def __call__(self, cls):
        def __str__(self):
            attrs = ', '.join(f"{attr}={getattr(self, attr)}" for attr in self.include_attrs if hasattr(self, attr))
            return f"{cls.__name__}({attrs})"

        cls.__str__ = __str__
        return cls