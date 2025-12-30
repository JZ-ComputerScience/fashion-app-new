# -*- coding: utf-8 -*-
"""
图像识别服务
调用阿里云千问VL模型（Qwen3-VL）进行图像分析，识别衣物和人物特征
"""

import os
import json
import base64
from openai import OpenAI


class ImageRecognitionService:
    """
    图像识别服务类
    使用阿里云通义千问VL模型（Qwen3-VL）提供图片分析功能
    """
    
    def __init__(self):
        """
        初始化服务，加载API密钥
        """
        # 从环境变量获取API密钥
        self.api_key = os.environ.get('DASHSCOPE_API_KEY', '')
        if not self.api_key:
            raise ValueError('DASHSCOPE_API_KEY环境变量未设置')
        
        # 初始化OpenAI客户端（使用兼容模式）
        self.client = OpenAI(
            api_key=self.api_key,
            # 北京地域base_url
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    def analyze_image(self, image_path):
        """
        分析图片，识别衣物和人物特征
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            dict: 包含衣物识别结果、人物特征和整体风格的字典
            结构：
            {
                "clothing_items": [衣物识别结果数组],
                "body_features": {人物特征}, 
                "overall_style": "整体风格"
            }
        """
        try:
            # 将图片转换为base64格式，用于API调用
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 构建API请求消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """请分析这张照片中人物的穿搭，提取以下信息：
1. 衣物识别：上衣、下装、外套、鞋子的款式、颜色、材质、风格
2. 人物特征：体型（如梨形、苹果形、沙漏形等）、身高比例、肤色类型
3. 体态特点：姿态、气质等
4. 整体风格：休闲、商务、运动、复古等

请以JSON格式返回结果，包含以下字段：
{
    "clothing_items": [
        {
            "type": "上衣/下装/外套/鞋子",
            "style": "款式",
            "color": "颜色",
            "material": "材质",
            "brand": "品牌（如果可见）",
            "confidence": 0.95
        }
    ],
    "body_features": {
        "body_type": "体型",
        "height_proportion": "身高比例",
        "skin_tone": "肤色类型",
        "posture": "体态特点"
    },
    "overall_style": "整体风格"
}"""
                        }
                    ]
                }
            ]
            
            # 调用阿里云通义千问VL模型
            completion = self.client.chat.completions.create(
                model="qwen3-vl-plus",  # 使用的模型
                messages=messages      # 请求消息
            )
            
            # 处理API响应
            result_text = completion.choices[0].message.content
            # 解析JSON响应
            result_json = self._parse_json_response(result_text)
            return result_json
                
        except Exception as e:
            print(f'图像识别错误: {str(e)}')
            raise
    
    def _parse_json_response(self, response_text):
        """
        解析API返回的JSON响应
        
        Args:
            response_text: API返回的文本
            
        Returns:
            dict: 解析后的JSON字典
        """
        try:
            # 提取JSON部分（处理可能的非JSON前缀或后缀）
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            return json.loads(json_str)
        except Exception as e:
            # 如果解析失败，返回包含原始响应的默认结构
            print(f'JSON解析错误: {str(e)}')
            return {
                'clothing_items': [],
                'body_features': {},
                'overall_style': '',
                'raw_response': response_text
            }
