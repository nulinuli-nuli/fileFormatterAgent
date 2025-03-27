document.addEventListener('DOMContentLoaded', function() {
    // 获取标签页元素
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // 切换标签页功能
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 移除所有active类
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 添加active类到当前标签和对应内容
            tab.classList.add('active');
            const target = tab.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });
    
    // 文件上传显示文件名
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');
    
    if (fileInput) {
        fileInput.addEventListener('change', (event) => {
            const fileName = event.target.files[0] ? event.target.files[0].name : '未选择文件';
            fileNameDisplay.textContent = fileName;
        });
    }
    
    // 文本转换表单提交
    const textForm = document.getElementById('text-form');
    if (textForm) {
        textForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await handleTextFormSubmit();
        });
    }
    
    // 文件转换表单提交
    const fileForm = document.getElementById('file-form');
    if (fileForm) {
        fileForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await handleFileFormSubmit();
        });
    }
    
    // 下载转换后的文本
    const downloadTextBtn = document.getElementById('download-text-btn');
    if (downloadTextBtn) {
        downloadTextBtn.addEventListener('click', () => {
            downloadFormattedText();
        });
    }
    
    // 下载转换后的文件
    const downloadFileBtn = document.getElementById('download-file-btn');
    if (downloadFileBtn) {
        downloadFileBtn.addEventListener('click', () => {
            downloadFormattedFile();
        });
    }
});

// 处理文本表单提交
async function handleTextFormSubmit() {
    const content = document.getElementById('text-content').value;
    const formatInstruction = document.getElementById('text-format-instruction').value;
    const apiKey = document.getElementById('api-key').value;
    const apiUrl = document.getElementById('api-url').value;
    const modelName = document.getElementById('model-name').value;
    const textResultContainer = document.getElementById('text-result-container');
    const textLoader = document.getElementById('text-loader');
    const textResult = document.getElementById('text-result');
    const scriptContent = document.getElementById('script-content');
    const downloadTextBtn = document.getElementById('download-text-btn');
    
    if (!content || !formatInstruction || !apiKey || !apiUrl || !modelName) {
        alert('请填写所有必填字段');
        return;
    }
    
    try {
        textLoader.style.display = 'block';
        textResultContainer.style.display = 'none';
        
        const response = await fetch('/api/format-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content,
                format_instruction: formatInstruction,
                api_config: {
                    api_key: apiKey,
                    api_url: apiUrl,
                    model_name: modelName
                }
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 限制展示的文本长度
            const MAX_DISPLAY_LENGTH = 5000;
            const originalContent = data.output_content;
            let displayContent = originalContent;
            
            if (originalContent.length > MAX_DISPLAY_LENGTH) {
                displayContent = originalContent.substring(0, MAX_DISPLAY_LENGTH) + 
                    `\n\n... 内容过长，仅显示前${MAX_DISPLAY_LENGTH}个字符，完整内容请点击下载按钮 ...`;
            }
            
            // 存储完整内容，但只显示部分
            textResult.setAttribute('data-full-content', originalContent);
            textResult.textContent = displayContent;
            
            scriptContent.textContent = data.script_content;
            textResultContainer.style.display = 'block';
            downloadTextBtn.style.display = 'block';
        } else {
            alert(`错误: ${data.message}`);
        }
    } catch (error) {
        alert(`请求失败: ${error.message}`);
    } finally {
        textLoader.style.display = 'none';
    }
}

// 处理文件表单提交
async function handleFileFormSubmit() {
    const fileInput = document.getElementById('file-input');
    const formatInstruction = document.getElementById('file-format-instruction').value;
    const apiKey = document.getElementById('file-api-key').value;
    const apiUrl = document.getElementById('file-api-url').value;
    const modelName = document.getElementById('file-model-name').value;
    const fileResultContainer = document.getElementById('file-result-container');
    const fileLoader = document.getElementById('file-loader');
    const fileResult = document.getElementById('file-result');
    const fileScriptContent = document.getElementById('file-script-content');
    const downloadFileBtn = document.getElementById('download-file-btn');
    
    if (!fileInput.files[0] || !formatInstruction || !apiKey || !apiUrl || !modelName) {
        alert('请选择文件并填写所有必填字段');
        return;
    }
    
    try {
        fileLoader.style.display = 'block';
        fileResultContainer.style.display = 'none';
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('format_instruction', formatInstruction);
        formData.append('api_key', apiKey);
        formData.append('api_url', apiUrl);
        formData.append('model_name', modelName);
        
        const response = await fetch('/api/format-file', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 限制展示的文本长度
            const MAX_DISPLAY_LENGTH = 5000;
            const originalContent = data.output_content;
            let displayContent = originalContent;
            
            if (originalContent.length > MAX_DISPLAY_LENGTH) {
                displayContent = originalContent.substring(0, MAX_DISPLAY_LENGTH) + 
                    `\n\n... 内容过长，仅显示前${MAX_DISPLAY_LENGTH}个字符，完整内容请点击下载按钮 ...`;
            }
            
            // 存储完整内容，但只显示部分
            fileResult.setAttribute('data-full-content', originalContent);
            fileResult.textContent = displayContent;
            
            fileScriptContent.textContent = data.script_content;
            fileResultContainer.style.display = 'block';
            downloadFileBtn.style.display = 'block';
        } else {
            alert(`错误: ${data.message}`);
        }
    } catch (error) {
        alert(`请求失败: ${error.message}`);
    } finally {
        fileLoader.style.display = 'none';
    }
}

// 下载转换后的文本
function downloadFormattedText() {
    const textResult = document.getElementById('text-result');
    const outputContent = textResult.getAttribute('data-full-content') || textResult.textContent;
    
    if (!outputContent) {
        alert('没有可下载的内容，请先进行转换');
        return;
    }
    
    // 创建一个Blob对象
    const blob = new Blob([outputContent], { type: 'text/plain' });
    // 创建一个URL对象
    const url = URL.createObjectURL(blob);
    
    // 创建一个a标签
    const a = document.createElement('a');
    a.href = url;
    a.download = 'formatted_output.txt';
    a.style.display = 'none';
    
    // 添加到DOM并触发点击
    document.body.appendChild(a);
    a.click();
    
    // 清理
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

// 下载转换后的文件
function downloadFormattedFile() {
    const fileResult = document.getElementById('file-result');
    const outputContent = fileResult.getAttribute('data-full-content') || fileResult.textContent;
    const fileInput = document.getElementById('file-input');
    
    if (!outputContent) {
        alert('没有可下载的内容，请先进行转换');
        return;
    }
    
    // 获取原始文件名
    let fileName = 'formatted_output.txt';
    if (fileInput.files[0]) {
        const originalName = fileInput.files[0].name;
        const name = originalName.substring(0, originalName.lastIndexOf('.')) || originalName;
        const ext = originalName.substring(originalName.lastIndexOf('.')) || '.txt';
        fileName = `${name}_formatted${ext}`;
    }
    
    // 创建一个Blob对象
    const blob = new Blob([outputContent], { type: 'text/plain' });
    // 创建一个URL对象
    const url = URL.createObjectURL(blob);
    
    // 创建一个a标签
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.style.display = 'none';
    
    // 添加到DOM并触发点击
    document.body.appendChild(a);
    a.click();
    
    // 清理
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
} 