import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from dotenv import load_dotenv
from api.routes import router
from api.utils import create_dirs
from api.logger import app_logger, LoggerMiddleware

# 加载环境变量
load_dotenv()

# 创建应用
app = FastAPI(
    title="文本格式转换服务",
    description="根据用户输入的文本和格式转换命令，调用大模型API生成转换脚本并执行",
    version="1.0.0"
)

# 添加日志中间件
app.add_middleware(LoggerMiddleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板配置
templates = Jinja2Templates(directory="templates")

# 注册API路由
app.include_router(router)

# 主页路由
@app.get("/")
async def index(request: Request):
    app_logger.info("访问主页")
    return templates.TemplateResponse("index.html", {"request": request})

# 启动时创建必要的目录
@app.on_event("startup")
async def startup_event():
    app_logger.info("服务启动，创建必要的目录")
    create_dirs()

# 关闭时记录日志
@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("服务关闭")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app_logger.info(f"启动服务器，监听端口: {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 