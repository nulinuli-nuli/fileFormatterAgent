import os
import uuid
import importlib.util
import sys
from typing import Dict, Any, Optional, Tuple
import requests
from dotenv import load_dotenv
from .logger import script_logger
from .models import APIConfig

# 加载环境变量
load_dotenv()

# 目录配置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
SCRIPTS_DIR = "scripts"

def create_dirs():
    """创建必要的目录"""
    for dir_path in [UPLOAD_DIR, OUTPUT_DIR, SCRIPTS_DIR]:
        os.makedirs(dir_path, exist_ok=True)
        script_logger.debug(f"创建目录: {dir_path}")

def save_uploaded_file(file_content: bytes, filename: Optional[str] = None) -> str:
    """保存上传的文件并返回文件路径"""
    if not filename:
        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}.txt"
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    script_logger.debug(f"保存上传的文件: {file_path}, 大小: {len(file_content)} 字节")
    return file_path

def save_text_content(text: str) -> str:
    """将文本内容保存为文件并返回文件路径"""
    filename = f"{uuid.uuid4().hex}.txt"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    script_logger.debug(f"保存文本内容到文件: {file_path}, 长度: {len(text)} 字符")
    return file_path

def read_file_content(file_path: str) -> str:
    """读取文件内容"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    script_logger.debug(f"读取文件内容: {file_path}, 长度: {len(content)} 字符")
    return content

def generate_python_script(sample_data: str, format_instruction: str, api_config: APIConfig) -> Tuple[str, str]:
    """
    调用大模型API生成Python脚本
    
    参数:
        sample_data: 示例数据
        format_instruction: 格式转换要求
        api_config: API配置
        
    返回:
        Tuple[str, str]: (脚本路径, 脚本内容)
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config.api_key}"
    }
    
    script_logger.info(f"使用模型 {api_config.model_name} 生成Python脚本")
    # 构建提示词
    prompt = f"""
你是一个专业的文本格式转换专家。请根据用户的格式转换要求，生成一个Python脚本来转换文本。

### 用户提供的示例数据：
```
{sample_data[:500]}  # 限制示例数据大小，防止token过多
```

### 格式转换要求：
{format_instruction}

### 要求：
1. 生成一个完整的Python脚本，脚本接受input_file和output_file两个参数
2. 脚本应该从input_file读取内容，按照格式要求转换，并将结果写入output_file
3. 脚本应该处理可能的异常情况
4. 不要使用任何非标准库
5. 只返回Python代码，不要包含任何解释或其他内容
6. 确保代码可以直接运行

示例函数签名:
```python
def convert_text(input_file: str, output_file: str):
    # 实现转换逻辑
    pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])
```

请只返回完整的Python代码，不包含任何其他解释。
"""
    
    payload = {
        "model": api_config.model_name,
        "messages": [
            {"role": "system", "content": "你是一个专业的Python开发者，擅长文本处理和格式转换。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        script_logger.info("发送API请求生成脚本")
        response = requests.post(api_config.api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # 从响应中提取生成的脚本内容
        script_content = response.json()["choices"][0]["message"]["content"]
        script_logger.info(f"成功接收到脚本内容，长度: {len(script_content)} 字符")
        
        # 删除可能的代码块标记
        script_content = script_content.replace("```python", "").replace("```", "").strip()
        
        # 保存脚本
        script_filename = f"format_script_{uuid.uuid4().hex}.py"
        script_path = os.path.join(SCRIPTS_DIR, script_filename)
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        script_logger.info(f"脚本已保存到: {script_path}")
        return script_path, script_content
        
    except Exception as e:
        script_logger.error(f"调用API生成脚本失败: {str(e)}", exc_info=True)
        raise Exception(f"调用API生成脚本失败: {str(e)}")

def execute_python_script(script_path: str, input_file: str) -> str:
    """
    执行生成的Python脚本进行格式转换
    
    参数:
        script_path: 脚本路径
        input_file: 输入文件路径
        
    返回:
        str: 输出文件路径
    """
    try:
        # 生成输出文件路径
        output_filename = f"output_{uuid.uuid4().hex}.txt"
        output_file = os.path.join(OUTPUT_DIR, output_filename)
        
        script_logger.info(f"准备执行脚本: {script_path}")
        script_logger.info(f"输入文件: {input_file}")
        script_logger.info(f"输出文件: {output_file}")
        
        # 加载脚本模块
        spec = importlib.util.spec_from_file_location("format_module", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 执行转换函数
        script_logger.info("开始执行转换函数")
        module.convert_text(input_file, output_file)
        script_logger.info("转换函数执行完成")
        
        # 验证输出文件是否存在
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            script_logger.info(f"输出文件已生成: {output_file}, 大小: {file_size} 字节")
        else:
            script_logger.warning(f"输出文件不存在: {output_file}")
        
        return output_file
    except Exception as e:
        script_logger.error(f"执行脚本失败: {str(e)}", exc_info=True)
        raise Exception(f"执行脚本失败: {str(e)}")

def get_file_content(file_path: str) -> Tuple[str, str]:
    """
    获取文件内容和文件名
    
    返回:
        Tuple[str, str]: (文件内容, 文件名)
    """
    filename = os.path.basename(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    script_logger.debug(f"获取文件内容: {file_path}, 文件名: {filename}, 内容长度: {len(content)}")
    return content, filename 