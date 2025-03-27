import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志目录
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 日志级别映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# 默认日志级别
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
LOG_LEVEL = LOG_LEVELS.get(DEFAULT_LOG_LEVEL, logging.INFO)

# 日志格式
LOG_FORMAT = os.getenv(
    "LOG_FORMAT", 
    "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
)

# 日志文件最大大小（字节）和备份数量
MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", 10 * 1024 * 1024))  # 默认10MB
BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", 5))  # 默认保留5个备份

# 是否在控制台输出日志
CONSOLE_OUTPUT = os.getenv("CONSOLE_OUTPUT", "true").lower() == "true"

# 是否使用按时间轮转的日志文件
TIME_ROTATING = os.getenv("TIME_ROTATING", "false").lower() == "true"
ROTATE_WHEN = os.getenv("ROTATE_WHEN", "midnight")  # 默认每天午夜轮转


def get_logger(name, log_file=None):
    """
    获取配置好的日志记录器
    
    参数:
        name: 记录器名称，通常使用模块名称
        log_file: 日志文件路径，如果不提供则使用name作为文件名
        
    返回:
        logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # 清除之前的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 设置日志文件名
    if log_file is None:
        log_file = f"{name}.log"
    
    # 如果日志文件不是绝对路径，则放在日志目录下
    if not os.path.isabs(log_file):
        log_file = os.path.join(LOG_DIR, log_file)
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT)
    
    # 添加文件处理器
    if TIME_ROTATING:
        # 使用按时间轮转的文件处理器
        file_handler = TimedRotatingFileHandler(
            log_file, 
            when=ROTATE_WHEN,
            backupCount=BACKUP_COUNT
        )
    else:
        # 使用按大小轮转的文件处理器
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=MAX_LOG_SIZE, 
            backupCount=BACKUP_COUNT
        )
    
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 如果配置要求，添加控制台处理器
    if CONSOLE_OUTPUT:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# 应用日志记录器
app_logger = get_logger("app", "application.log")

# API日志记录器
api_logger = get_logger("api", "api.log")

# 脚本执行日志记录器
script_logger = get_logger("script", "script_execution.log")

# 访问日志记录器（类似于Web服务器的访问日志）
access_logger = get_logger("access", "access.log")


class LoggerMiddleware:
    """FastAPI中间件，用于记录请求访问日志"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start_time = time.time()
        
        # 在这里不能直接调用receive()，因为这样会导致请求处理程序无法获取请求体
        # 这里处理请求信息
        method = scope.get("method", "")
        path = scope.get("path", "")
        client = scope.get("client", ("", ""))[0]
        
        # 调用应用并获取响应
        async def _send(message):
            if message["type"] == "http.response.start":
                # 在这里捕获响应状态码
                status_code = message.get("status", 0)
                process_time = time.time() - start_time
                # 记录访问日志
                access_logger.info(
                    f"{client} - {method} {path} {status_code} - {process_time:.4f}s"
                )
            
            await send(message)
        
        await self.app(scope, receive, _send) 