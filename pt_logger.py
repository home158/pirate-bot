# pt_logger.py
import logging
import os
from datetime import datetime
import pt_config

# 設定 logs 目錄
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 取得當前日期作為日誌檔名
log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# 設置日誌級別，從環境變數中讀取
LOG_LEVEL = pt_config.LOG_LEVEL.upper()
numeric_level = getattr(logging, LOG_LEVEL, logging.INFO)

# 設置 Logger
logger = logging.getLogger("bot")
logger.setLevel(numeric_level)

# 設定日誌文件處理器，並指定 UTF-8 編碼
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(numeric_level)

# 設定日誌格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 將處理器加入 logger
logger.addHandler(file_handler)

# 控制台日誌配置
ENABLE_CONSOLE_LOGGING = pt_config.ENABLE_CONSOLE_LOGGING.lower() in ("true", "1", "t")

if ENABLE_CONSOLE_LOGGING:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
