# -*- coding: utf-8 -*-
"""
天气服务
获取实时天气数据，为穿搭推荐提供天气依据
"""

import os
import requests
from typing import Dict


class WeatherService:
    """
    天气服务类
    提供获取指定地点实时天气数据的功能
    """
    
    def __init__(self):
        """
        初始化天气服务，加载API密钥和配置
        """
        # 从环境变量获取API密钥
        self.api_key = os.environ.get('WEATHER_API_KEY', '')
        
        # 天气API基础URL（使用和风天气API）
        self.base_url = 'https://devapi.qweather.com/v7'
    
    def get_weather(self, location: str) -> Dict:
        """
        获取指定地点的实时天气数据
        
        Args:
            location: 地点名称，如'Beijing'、'上海'等
            
        Returns:
            Dict: 天气数据字典，包含温度、天气状况、湿度、风速等
            结构：
            {
                "temperature": 25.5,  # 温度（℃）
                "condition": "sunny",  # 天气状况
                "humidity": 60,        # 湿度（%）
                "wind_speed": 3.5,      # 风速（m/s）
                "location": "Beijing"   # 地点
            }
        """
        try:
            # 构建API请求URL和参数
            url = f'{self.base_url}/weather/now'
            params = {
                'location': location,
                'key': self.api_key
            }
            
            # 发送GET请求获取天气数据
            response = requests.get(url, params=params, timeout=10)
            
            # 处理API响应
            if response.status_code == 200:
                data = response.json()
                # 检查API返回状态码
                if data.get('code') == '200':
                    now = data.get('now', {})
                    # 提取关键天气信息并返回
                    return {
                        'temperature': float(now.get('temp', 20)),
                        'condition': now.get('text', 'sunny'),
                        'humidity': int(now.get('humidity', 50)),
                        'wind_speed': float(now.get('windSpeed', 0)),
                        'location': location
                    }
            
            # 如果API调用失败，返回默认天气数据
            return self._get_default_weather(location)
            
        except Exception as e:
            # 捕获所有异常，记录日志并返回默认天气数据
            print(f'天气API调用失败: {str(e)}')
            return self._get_default_weather(location)
    
    def _get_default_weather(self, location: str) -> Dict:
        """
        获取默认天气数据（当API调用失败时使用）
        
        Args:
            location: 地点名称
            
        Returns:
            Dict: 默认天气数据
        """
        return {
            'temperature': 20.0,      # 默认温度20℃
            'condition': 'sunny',      # 默认天气晴朗
            'humidity': 50,            # 默认湿度50%
            'wind_speed': 3.0,         # 默认风速3m/s
            'location': location       # 地点
        }
    
    def get_forecast(self, location: str) -> Dict:
        """
        获取指定地点的天气预报（扩展功能）
        
        Args:
            location: 地点名称
            
        Returns:
            Dict: 天气预报数据
        """
        try:
            url = f'{self.base_url}/weather/7d'
            params = {
                'location': location,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '200':
                    return data.get('daily', [])
            
            return []
            
        except Exception as e:
            print(f'天气预报API调用失败: {str(e)}')
            return []
