# -*- coding: utf-8 -*-
"""
虚拟试穿服务
调用阿里云百炼OutfitAnyone API，实现衣物虚拟试穿功能
"""

import os
import requests
import base64
import json
from typing import Dict


class VirtualTryonService:
    """
    虚拟试穿服务类
    提供衣物虚拟试穿功能，调用阿里云百炼OutfitAnyone API
    """
    
    def __init__(self):
        """
        初始化虚拟试穿服务，加载API密钥和配置
        """
        # 从环境变量获取API密钥
        self.api_key = os.environ.get('BAILIAN_API_KEY', '')
        
        # 阿里云百炼API URL
        self.api_url = 'https://bailian.cn-beijing.aliyuncs.com/v2/services/aigc/image-generation/generation'
    
    def generate_tryon(self, person_image_path: str, clothing_image_path: str) -> Dict:
        """
        生成虚拟试穿效果图
        
        Args:
            person_image_path: 人物照片文件路径
            clothing_image_path: 服装照片文件路径
            
        Returns:
            Dict: 虚拟试穿结果，包含成功状态和结果图片URL
            结构：
            {
                "success": true,
                "image_url": "试穿结果图片URL",
                "task_id": "任务ID"
            }
        """
        try:
            # 1. 将人物图片转换为base64格式
            with open(person_image_path, 'rb') as f:
                person_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # 2. 将服装图片转换为base64格式
            with open(clothing_image_path, 'rb') as f:
                clothing_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # 3. 构建API请求参数
            payload = {
                'model': 'outfit-anyone',  # 使用的模型名称
                'input': {
                    'person_image': f'data:image/jpeg;base64,{person_base64}',  # 人物图片
                    'clothing_image': f'data:image/jpeg;base64,{clothing_base64}',  # 服装图片
                    'prompt': 'high quality, realistic, natural fitting',  # 生成提示词
                    'n': 1,  # 生成结果数量
                    'size': '1024x1024'  # 生成图片尺寸
                }
            }
            
            # 4. 设置请求头
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'  # 认证信息
            }
            
            # 5. 发送POST请求调用API
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60  # 虚拟试穿可能需要较长时间，设置超时为60秒
            )
            
            # 6. 处理API响应
            if response.status_code == 200:
                result = response.json()
                # 检查API返回结果
                if 'output' in result and 'results' in result['output']:
                    # 返回成功结果
                    return {
                        'success': True,
                        'image_url': result['output']['results'][0]['url'],
                        'task_id': result.get('request_id', '')
                    }
            
            # 7. API调用失败，返回错误信息
            return {
                'success': False,
                'error': '虚拟试穿生成失败'
            }
            
        except Exception as e:
            # 捕获所有异常，记录日志并返回错误信息
            print(f'虚拟试穿错误: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        查询虚拟试穿任务状态（适用于异步调用场景）
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务状态信息
            结构：
            {
                "status": "running",  # 任务状态：running, done, failed
                "result": {}  # 任务结果（如果任务已完成）
            }
        """
        try:
            # 构建查询URL
            url = f'{self.api_url}/{task_id}'
            
            # 设置请求头
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # 发送GET请求查询任务状态
            response = requests.get(url, headers=headers, timeout=10)
            
            # 处理API响应
            if response.status_code == 200:
                return response.json()
            
            # API调用失败，返回默认状态
            return {'status': 'failed'}
            
        except Exception as e:
            # 捕获所有异常，记录日志并返回错误状态
            print(f'获取任务状态错误: {str(e)}')
            return {'status': 'failed'}
