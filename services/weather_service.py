# -*- coding: utf-8 -*-
"""
天气服务
集成和风天气API，提供城市搜索和实时天气查询功能
"""

import os
import requests
from flask import current_app


class WeatherService:
    """
    和风天气服务类
    """
    
    def __init__(self):
        """
        初始化服务，加载API密钥
        """
        # 1. 优先从配置中获取（Config类已经处理了兼容性）
        self.api_key = current_app.config.get('QWEATHER_API_KEY')
        
        # 2. 如果配置中没有，尝试直接从环境变量获取 WEATHER_API_KEY
        if not self.api_key:
             self.api_key = os.environ.get('WEATHER_API_KEY')
             
        # 3. 最后尝试 QWEATHER_API_KEY
        if not self.api_key:
            self.api_key = os.environ.get('QWEATHER_API_KEY', '')
            
        if not self.api_key:
            print('严重警告: 未找到任何天气API密钥 (WEATHER_API_KEY/QWEATHER_API_KEY)')
            
        # API基础URL
        # 用户使用的是私有/商业版Host: k94jab77cb.yun.qweatherapi.com
        user_host = "k94jab77cb.yun.qweatherapi.com"
        self.geo_base_url = f"https://{user_host}/geo/v2"
        self.weather_base_url = f"https://{user_host}/v7"
        
        print(f"WeatherService initialized with Key: {self.api_key[:6]}****** if self.api_key else 'None'") # 调试日志
        
    def search_city(self, keyword, adm=None):
        """
        搜索城市
        
        Args:
            keyword: 搜索关键词（中文/英文/拼音）
            adm: 上级行政区划（可选，用于过滤重名城市）
            
        Returns:
            list: 城市列表
        """
        if not keyword or not self.api_key:
            return []
            
        try:
            url = f"{self.geo_base_url}/city/lookup"
            params = {
                'location': keyword,
                'key': self.api_key,
                'range': 'cn',  # 限制在中国范围内，根据需求可调整
                'number': 10
            }
            
            # 如果提供了adm参数，添加到请求中
            if adm:
                params['adm'] = adm
            
            print(f"WeatherService Request: URL={url}, Params={params}") # 详细调试日志
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            print(f"WeatherService Response: Code={data.get('code')}, LocationCount={len(data.get('location', []))}") # 详细调试日志
            
            if data.get('code') == '200':
                cities = []
                for item in data.get('location', []):
                    # 格式化城市名称：城市-省份 (上级行政区)
                    display_name = item['name']
                    if item.get('adm1') and item['adm1'] != item['name']:
                        display_name = f"{item['name']}, {item['adm1']}"
                        
                    cities.append({
                        'id': item['id'],
                        'name': display_name,
                        'lat': item['lat'],
                        'lon': item['lon']
                    })
                return cities
            else:
                print(f"城市搜索API返回错误代码: {data.get('code')}")
                return []
                
        except Exception as e:
            print(f"城市搜索失败: {str(e)}")
            return []
            
    def get_weather_now(self, location_id):
        """
        获取实时天气
        
        Args:
            location_id: 城市ID
            
        Returns:
            dict: 天气数据
        """
        if not location_id or not self.api_key:
            return None
            
        try:
            url = f"{self.weather_base_url}/weather/now"
            params = {
                'location': location_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('code') == '200':
                now = data.get('now', {})
                return {
                    'temp': now.get('temp'),
                    'text': now.get('text'),
                    'icon': now.get('icon'),
                    'feels_like': now.get('feelsLike'),
                    'humidity': now.get('humidity'),
                    'wind_dir': now.get('windDir'),
                    'obs_time': now.get('obsTime')
                }
            else:
                print(f"实时天气API返回错误代码: {data.get('code')}")
                return None
                
        except Exception as e:
            print(f"获取天气失败: {str(e)}")
            return None
