from pydantic import BaseModel, Field
from typing import Optional

class APIConfig(BaseModel):
    """API配置模型"""
    api_key: str = Field(..., description="API密钥")
    api_url: str = Field(..., description="API URL")
    model_name: str = Field(..., description="模型名称")

class TextFormatRequest(BaseModel):
    """文本格式转换请求模型"""
    content: Optional[str] = Field(None, description="文本内容，若不提供则必须上传文件")
    format_instruction: str = Field(..., description="格式转换要求")
    api_config: APIConfig = Field(..., description="API配置")

class FormatResponse(BaseModel):
    """格式转换响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    output_content: Optional[str] = Field(None, description="转换后的内容")
    script_content: Optional[str] = Field(None, description="生成的Python脚本内容")
    
class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str = Field(..., description="错误消息") 