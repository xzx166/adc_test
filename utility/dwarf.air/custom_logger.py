import logging
import os
from logging import FileHandler, StreamHandler, Formatter

def setup_logger(task_id: str, log_dir: str):
    # 创建 logger
    logger = logging.getLogger(task_id)
    logger.setLevel(logging.DEBUG)

    # 如果 logger 已有 handler，先移除（避免重复添加）
    if logger.hasHandlers():
        logger.handlers.clear()

    # 控制台 handler
    # console_handler = StreamHandler()
    # console_handler.setLevel(logging.INFO)

    # 文件 handler（使用任务 ID 作为文件名）
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"task_{task_id}.log")
    file_handler = FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # 设置日志格式
    formatter = Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    # console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加 handler
    # logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
# 使用示例
if __name__ == "__main__":
    task_id = "123456"  # 示例任务 ID
    logger = setup_logger(task_id)
    logger.debug(f"任务 {task_id} 启动")
    logger.info(f"任务 {task_id} 正在运行")