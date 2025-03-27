from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
from typing import Optional

from .models import TextFormatRequest, FormatResponse, ErrorResponse, APIConfig
from .utils import (
    save_uploaded_file, 
    save_text_content, 
    generate_python_script,
    execute_python_script,
    read_file_content,
    get_file_content
)
from .logger import api_logger

router = APIRouter(prefix="/api", tags=["format"])

@router.post(
    "/format-text", 
    response_model=FormatResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def format_text(
    request: TextFormatRequest
):
    """
    通过直接提供文本内容进行格式转换
    """
    api_logger.info(f"接收文本格式转换请求，格式要求: {request.format_instruction[:100]}...")
    try:
        if not request.content or request.content.strip() == "":
            api_logger.warning("文本内容为空")
            return ErrorResponse(message="文本内容不能为空")
        
        # 保存文本内容到文件
        input_file = save_text_content(request.content)
        api_logger.debug(f"文本内容已保存到文件: {input_file}")
        
        # 生成转换脚本
        api_logger.info("正在生成转换脚本...")
        script_path, script_content = generate_python_script(
            request.content, 
            request.format_instruction,
            request.api_config
        )
        api_logger.debug(f"转换脚本已生成: {script_path}")
        
        # 执行脚本进行转换
        api_logger.info("正在执行转换脚本...")
        output_file = execute_python_script(script_path, input_file)
        api_logger.debug(f"转换结果已保存到: {output_file}")
        
        # 读取转换后的内容
        output_content = read_file_content(output_file)
        api_logger.info(f"格式转换成功，输出内容大小: {len(output_content)} 字节")
        
        return FormatResponse(
            success=True,
            message="格式转换成功",
            output_content=output_content,
            script_content=script_content
        )
    
    except Exception as e:
        api_logger.error(f"文本格式转换失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/format-file",
    response_model=FormatResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def format_file(
    file: UploadFile = File(...),
    format_instruction: str = Form(...),
    api_key: str = Form(...),
    api_url: str = Form(...),
    model_name: str = Form(...)
):
    """
    通过上传文件进行格式转换
    """
    api_logger.info(f"接收文件格式转换请求，文件名: {file.filename}, 格式要求: {format_instruction[:100]}...")
    try:
        # 创建API配置
        api_config = APIConfig(
            api_key=api_key,
            api_url=api_url,
            model_name=model_name
        )
        
        # 读取上传的文件内容
        file_content = await file.read()
        file_size = len(file_content)
        api_logger.debug(f"接收到文件大小: {file_size} 字节")
        
        # 保存上传的文件
        input_file = save_uploaded_file(file_content, file.filename)
        api_logger.debug(f"文件已保存到: {input_file}")
        
        # 读取文件内容用于生成脚本
        sample_data = read_file_content(input_file)
        
        # 生成转换脚本
        api_logger.info("正在生成转换脚本...")
        script_path, script_content = generate_python_script(
            sample_data, 
            format_instruction,
            api_config
        )
        api_logger.debug(f"转换脚本已生成: {script_path}")
        
        # 执行脚本进行转换
        api_logger.info("正在执行转换脚本...")
        output_file = execute_python_script(script_path, input_file)
        api_logger.debug(f"转换结果已保存到: {output_file}")
        
        # 读取转换后的内容
        output_content = read_file_content(output_file)
        api_logger.info(f"文件格式转换成功，输出内容大小: {len(output_content)} 字节")
        
        return FormatResponse(
            success=True,
            message="文件格式转换成功",
            output_content=output_content,
            script_content=script_content
        )
    
    except Exception as e:
        api_logger.error(f"文件格式转换失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/download-output",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def download_output(
    content: str = Form(...),
    format_instruction: str = Form(...),
    api_key: str = Form(...),
    api_url: str = Form(...),
    model_name: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    转换文本并下载转换后的文件
    """
    api_logger.info("接收文本转换并下载请求")
    try:
        if not content or content.strip() == "":
            api_logger.warning("文本内容为空")
            raise HTTPException(status_code=400, detail="文本内容不能为空")
        
        # 创建API配置
        api_config = APIConfig(
            api_key=api_key,
            api_url=api_url,
            model_name=model_name
        )
        
        # 保存文本内容到文件
        input_file = save_text_content(content)
        api_logger.debug(f"文本内容已保存到文件: {input_file}")
        
        # 生成转换脚本
        api_logger.info("正在生成转换脚本...")
        script_path, _ = generate_python_script(
            content, 
            format_instruction,
            api_config
        )
        api_logger.debug(f"转换脚本已生成: {script_path}")
        
        # 执行脚本进行转换
        api_logger.info("正在执行转换脚本...")
        output_file = execute_python_script(script_path, input_file)
        api_logger.debug(f"转换结果已保存到: {output_file}")
        
        # 创建下载的文件名
        download_filename = f"formatted_output.txt"
        api_logger.info(f"准备下载文件，文件名: {download_filename}")
        
        # 返回文件
        return FileResponse(
            path=output_file, 
            filename=download_filename,
            media_type="text/plain",
            background=background_tasks
        )
    
    except Exception as e:
        api_logger.error(f"文本转换并下载失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/download-output-file",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def download_output_file(
    file: UploadFile = File(...),
    format_instruction: str = Form(...),
    api_key: str = Form(...),
    api_url: str = Form(...),
    model_name: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    转换上传的文件并下载转换后的文件
    """
    api_logger.info(f"接收文件转换并下载请求，文件名: {file.filename}")
    try:
        # 创建API配置
        api_config = APIConfig(
            api_key=api_key,
            api_url=api_url,
            model_name=model_name
        )
        
        # 读取上传的文件内容
        file_content = await file.read()
        file_size = len(file_content)
        api_logger.debug(f"接收到文件大小: {file_size} 字节")
        
        # 保存上传的文件
        input_file = save_uploaded_file(file_content, file.filename)
        api_logger.debug(f"文件已保存到: {input_file}")
        
        # 读取文件内容用于生成脚本
        sample_data = read_file_content(input_file)
        
        # 生成转换脚本
        api_logger.info("正在生成转换脚本...")
        script_path, _ = generate_python_script(
            sample_data, 
            format_instruction,
            api_config
        )
        api_logger.debug(f"转换脚本已生成: {script_path}")
        
        # 执行脚本进行转换
        api_logger.info("正在执行转换脚本...")
        output_file = execute_python_script(script_path, input_file)
        api_logger.debug(f"转换结果已保存到: {output_file}")
        
        # 创建下载的文件名
        name, ext = os.path.splitext(file.filename)
        download_filename = f"{name}_formatted{ext}"
        api_logger.info(f"准备下载文件，文件名: {download_filename}")
        
        # 返回文件
        return FileResponse(
            path=output_file, 
            filename=download_filename,
            background=background_tasks
        )
    
    except Exception as e:
        api_logger.error(f"文件转换并下载失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 