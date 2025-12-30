# -*- coding: utf-8 -*-
"""
文件工具函数
提供文件处理相关的辅助功能
"""

import os
from werkzeug.utils import secure_filename
from datetime import datetime


def allowed_file(filename: str) -> bool:
    """
    检查文件名是否为允许的图片类型
    
    Args:
        filename: 文件名，包含扩展名
        
    Returns:
        bool: True表示文件类型允许，False表示不允许
    """
    # 允许的文件扩展名列表
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # 检查文件名是否包含点号，且扩展名在允许列表中
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, upload_folder: str) -> str:
    """
    保存上传的文件到指定目录
    
    Args:
        file: 上传的文件对象（Flask request.files['file']返回的对象）
        upload_folder: 文件保存目录
        
    Returns:
        str: 保存后的文件路径
    """
    # 生成安全的文件名（去除特殊字符，避免安全问题）
    filename = secure_filename(file.filename)
    
    # 添加时间戳前缀，避免文件名冲突
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{filename}'
    
    # 拼接完整的文件路径
    file_path = os.path.join(upload_folder, filename)
    
    # 保存文件到指定路径
    file.save(file_path)
    
    return file_path


def get_file_extension(filename: str) -> str:
    """
    获取文件名的扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名，小写
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def ensure_directory_exists(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        None
    """
    os.makedirs(directory, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小，单位为字节
    """
    return os.path.getsize(file_path)
