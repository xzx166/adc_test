import datetime
import itertools
import json
import math
import re
import time
from glob import glob
from typing import Iterable, List, Tuple, Union, Dict
import urllib
import random
import base64
import gzip
from io import BytesIO


# print字体颜色
font_red     = "\033[1;91m"  # 红色
font_green   = "\033[1;92m"  # 绿色
font_yellow  = "\033[1;93m"  # 黄色
font_blue    = "\033[1;94m"  # 蓝色
font_magenta = "\033[1;95m"  # 品红色
font_cyan    = "\033[1;96m"  # 青色
font_gray    = "\033[1;37m"  # 灰色
font_white   = "\033[1;97m"  # 白色
font_reset   = "\033[0;92m"  # 重置

# 时间戳
timeStamp = lambda: str(int(time.time() * 10 ** 6))
# 日期时间字符串
timeNowStr = lambda: datetime.datetime.now().strftime('%Y-%-m-%-d %-H:%M:%S')
# 日期时间对象
timeNow = lambda: datetime.datetime.now()

# 数字正则
digit_pattern = re.compile(r"-\d+|\d+")
# 汉字正则
chinese_pattern = re.compile('[一-龥]+')
# 文件名特殊字符正则
filename_special_char_pattern = re.compile(r"[\\/:*?<>|,]")
# 手机号正则
phone_pattern = re.compile(r"^1[3-9]\d{9}$")

# catch名称格式化
catch_name = lambda write_name: f"adc_catch_{write_name}_{timeStamp()}"

class CounterBase:
    def __init__(self, start=1):
        """
        计数器
        :param start: 起始值
        :return: 下一个值
        """
        self.counter = itertools.count(start)
        self.currentValue = start

    def reset(self, start=1):
        """重置计数器"""
        self.counter = itertools.count(start)

    @property
    def current(self):
        """当前值"""
        return self.currentValue

    def __call__(self):
        self.currentValue = next(self.counter)
        return self.currentValue
single_counter = CounterBase()

def extract_digit(text: str, default=""):
    """从字符串提取数字"""
    if regex_result := digit_pattern.search(str(text)):
        return regex_result.group()
    return default

def extract_datetime(text):
    """从字符串中提取日期时间，统一输出为 xxxx年xx月xx日 格式"""
    date_str = ""
    now = datetime.datetime.now()
    current_year = now.year

    # 1. 处理相对时间
    # "刚刚"
    if "刚刚" in text:
        date_str = now.strftime("%Y年%m月%d日")

    # "X分钟前"
    minute_match = re.search(r'(\d+)\s*分钟前', text)
    if minute_match:
        minutes = int(minute_match.group(1))
        result_date = now - datetime.timedelta(minutes=minutes)
        date_str = result_date.strftime("%Y年%m月%d日")

    # "X小时前"
    hour_match = re.search(r'(\d+)\s*小时前', text)
    if hour_match:
        hours = int(hour_match.group(1))
        result_date = now - datetime.timedelta(hours=hours)
        date_str = result_date.strftime("%Y年%m月%d日")

    # "X天前"
    day_match = re.search(r'(\d+)\s*天前', text)
    if day_match:
        days = int(day_match.group(1))
        result_date = now - datetime.timedelta(days=days)
        date_str = result_date.strftime("%Y年%m月%d日")

    # "X周前"
    week_match = re.search(r'(\d+)\s*周前', text)
    if week_match:
        weeks = int(week_match.group(1))
        result_date = now - datetime.timedelta(weeks=weeks)
        date_str = result_date.strftime("%Y年%m月%d日")

    # 2. 处理具体日期格式
    # "YYYY年MM月DD日" 或 "YYYY年M月D日"
    year_month_day_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
    if year_month_day_match:
        year, month, day = year_month_day_match.groups()
        date_str = f"{year}年{int(month):02d}月{int(day):02d}日"

    # "MM月DD日" 或 "M月D日"（无年份，使用当前年）
    month_day_match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
    if month_day_match:
        month, day = month_day_match.groups()
        date_str = f"{current_year}年{int(month):02d}月{int(day):02d}日"

    # "YYYY-MM-DD"
    iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if iso_match:
        year, month, day = iso_match.groups()
        date_str = f"{year}年{month}月{day}日"

    # "YYYY/MM/DD"
    slash_match = re.search(r'(\d{4})/(\d{2})/(\d{2})', text)
    if slash_match:
        year, month, day = slash_match.groups()
        date_str = f"{year}年{month}月{day}日"

    # 3. 原有的完整日期时间格式（提取日期部分）
    patterns = [
        r'(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
        r'(\d{4})/(\d{2})/(\d{2}) \d{2}:\d{2}:\d{2}',  # YYYY/MM/DD HH:MM:SS
        r'(\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}',  # ISO 8601
        r'(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}',        # YYYY-MM-DD HH:MM
        r'(\d{4})/(\d{2})/(\d{2}) \d{2}:\d{2}'         # YYYY/MM/DD HH:MM
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            year, month, day = match.groups()
            date_str = f"{year}年{month}月{day}日"

    return date_str

def add_space_simple(text):
    """在中文和英文之间添加空格"""
    return re.sub(r'(?<=[\u4e00-\u9fff])(?=[A-Za-z0-9])|(?<=[A-Za-z0-9])(?=[\u4e00-\u9fff])', ' ', text)

def format_print(obj):
    """格式化打印"""
    if isinstance(obj, (str, int, float)): return str(obj)
    return re.sub(r"[\"']", "", str(obj))

def json_dumps(data, is_indent=False):
    """json序列化"""
    if isinstance(data, (List, Dict)):
        indent = 4 if is_indent else None
        return json.dumps(data, ensure_ascii=False, indent=indent)
    return str(data)

def create_poses(LT, L2L=0, T2T=0, cols=1, rows=1, limit=0):
    """
    创建一组二维位置点（用于图像拼接、阵列布局等场景）
    :param LT: tuple (x, y)，表示左上角（Left-Top）起始位置
    :param L2L: (可选) 列与列之间的水平间距（Left to Left），即列间距
    :param T2T: (可选) 行与行之间的垂直间距（Top to Top），即行间距
    :param cols: 一共多少列
    :param rows: 一共多少行
    :param limit: (可选) 限制返回的位置数量（用于只取前 N 个）
    :return: 返回一个包含多个 (x, y) 坐标元组的列表
    """
    product = itertools.product(range(rows), range(cols))
    poses = list(map(lambda row_col: (int(LT[0] + L2L * row_col[1]), int(LT[1] + T2T * row_col[0])), product))
    return poses if not limit else poses[:limit]

def create_boxes(LT, L2L=0, T2T=0, width=1, height=1, cols=1, rows=1, limit=0):
    """
    创建一组盒子
    :param LT:
    :param L2L:
    :param T2T:
    :param width:
    :param height:
    :param cols:
    :param rows:
    :param limit:
    :return:
    """
    boxes = []
    for row, col in itertools.product(range(rows), range(cols)):
        lt = (LT[0] + L2L * col, LT[1] + T2T * row)
        rb = (lt[0] + width, lt[1] + height)
        boxes.append((lt, rb))
    return boxes if not limit else boxes[:limit]

def create_areas(LT, L2L=0, T2T=0, width=1, height=1, cols=1, rows=1, limit=0):
    """
    创建一组区域
    :param LT:
    :param L2L:
    :param T2T:
    :param width:
    :param height:
    :param cols:
    :param rows:
    :param limit:
    :return:
    """
    areas = []
    for row, col in itertools.product(range(rows), range(cols)):
        lt = (LT[0] + L2L * col, LT[1] + T2T * row)
        rb = (lt[0] + width, lt[1] + height)
        areas.append((*lt, *rb))
    return areas if not limit else areas[:limit]

def area2pos(area):
    """
    区域转坐标
    :param area:
    :return:
    """
    return math.ceil((area[0] + area[2]) / 2), math.ceil((area[1] + area[3]) / 2)

def box2pos(LT, RB=None):
    """
    盒子转坐标
    :param LT:
    :param RB:
    :return:
    """
    if isinstance(LT[0], Iterable): LT, RB = LT
    return math.ceil((LT[0] + RB[0]) / 2), math.ceil((LT[1] + RB[1]) / 2)

def pos2box(pos, padding):
    """
    坐标转盒子
    :param pos:
    :param padding:
    :return:
    """
    width_half, height_half = math.ceil(padding / 2), math.ceil(padding / 2)
    return (pos[0] - width_half, pos[1] - height_half), (pos[0] + width_half, pos[1] + height_half)

def point2line(point: int, lenth: int, align="center"):
    """
    点到线
    :param point: 一维点
    :param lenth: 长度
    :param align: 对齐, 可选项[left, center, right]
    :return:
    """
    if align == "left":
        return point + lenth
    elif align == "right":
        return lenth - point
    else:
        return point + lenth / 2

def select_numbers(string):
    """用于sorted key参数, 字符串数字排序"""
    pieces = re.compile(r"(\d+)").split(string)
    pieces[1::2] = map(int, pieces[1::2])
    return pieces

def default_dict(obj):
    """使用setdefault将对象转换为字典"""
    dict_data = {}
    for key, value in obj:
        dict_data.setdefault(key, value)
    return dict_data

def first_match(items, s):
    """输出列表匹配到的第一个值"""
    for item in items:
        if item in s:
            return item
    else:
        return ""

def pos_in_area(pos, area):
    """判断坐标是否在区域内"""
    if pos and area and \
        isinstance(area, (List, Tuple)) and \
        len(area) == 4 and \
        all(map(lambda x: isinstance(x, (int, float)), area)) and \
        area[0] < area[2] and \
        area[1] < area[3]:
        return area[0] < pos[0] < area[2] and area[1] < pos[1] < area[3]

def url_parse(url):
    """url解析"""
    return urllib.parse.urlparse(url)  # noqa

def files_list_sorted(pathname):
    """返回文件列表"""
    return sorted(glob(pathname), key=select_numbers)

def data_pagination(data, page_size=50):
    """数据分页"""
    data_list = []
    for page_num in range(1, math.ceil(len(data) / page_size) + 1):
        start_index = (page_num - 1) * page_size
        end_index = page_num * page_size
        data_list.append(data[start_index:end_index])

    return data_list

def random_pos(x: Union[int, Tuple, List], y: int=None, pm: Union[int, Tuple, List]=10):
    """
    生成随机位置
    :param y: x pos
    :param x: y pos
    :param pm: x & y pos plus or minus (±)
    """
    if isinstance(pm, int) and pm > 0:
        xpm = ypm = pm
    elif isinstance(pm, (List, Tuple)) and len(pm) >= 2:
        xpm, ypm = pm
    else:
        xpm = ypm = 0

    if isinstance(x, (list, tuple)) and len(x) >= 2:
        x, y = x
    elif not y:
        return int(random.randint(int(x) - xpm, x + xpm))

    x_pos = random.randint(int(x) - xpm, x + xpm)
    y_pos = random.randint(y - ypm, y + ypm)
    x_pos = 1 if x_pos < 0 else x_pos
    y_pos = 1 if y_pos < 0 else y_pos

    return int(x_pos), int(y_pos)

def gzip_text(text: str) -> str:
    """
    gzip压缩
    :param text:
    :return:
    """
    if not text or text.isspace():
        return ""

    with BytesIO() as bytes_out:
        with gzip.GzipFile(fileobj=bytes_out, mode='wb') as gzip_out:
            gzip_out.write(text.encode('utf-8'))
        compressed_bytes = bytes_out.getvalue()
        return base64.b64encode(compressed_bytes).decode('ascii')

def ungzip_text(text: str) -> str:
    """
    gzip解压
    :param text:
    :return:
    """
    if not text or text.isspace():
        return ""

    with BytesIO(base64.b64decode(text)) as bytes_in:
        with gzip.GzipFile(fileobj=bytes_in, mode='rb') as gzip_in:
            decompressed_bytes = gzip_in.read()
            return decompressed_bytes.decode('utf-8')

def digit_pair(x):
    """相邻数字配对"""
    # [1,3,5,7] -> [(1,3),(3,5),(5,7)]
    return [(x[i], x[i + 1]) for i in range(len(x) - 1)]

def find_range_index(between, value):
    """数字区间"""
    # ([(1,3),(3,5),(5,7)], 4) -> 1
    return next((i for i, (start, end) in enumerate(between) if start <= value < end), -1)

def is_work_time(dt: datetime.datetime = None) -> bool:
    """
    判断给定时间是否在工作时间内
    :param dt: datetime对象，默认为当前时间
    :return: 在工作时间内返回True，否则返回False
    """
    if dt is None:
        dt = datetime.datetime.now()

    # 获取星期几（周一=0，周日=6）
    weekday = dt.weekday()
    # 检查是否是周一到周五
    if weekday > 4:  # 周六或周日
        return False

    time_obj = dt.time()
    # 上午时段
    am_start = datetime.time(9, 30, 0)
    am_end = datetime.time(12, 0, 0)
    # 下午时段
    pm_start = datetime.time(14, 00, 0)
    pm_end = datetime.time(18, 30, 0)

    return (am_start <= time_obj <= am_end) or (pm_start <= time_obj <= pm_end)


if __name__ == '__main__':
    for _ in range(100):
        print(random_pos(30, pm=1))