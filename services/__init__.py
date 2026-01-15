# -*- coding: utf-8 -*-
"""
服务层包
包含应用的所有业务逻辑服务
"""

# 从各服务模块导入类，方便外部直接调用
from .image_recognition_service import ImageRecognitionService
from .weather_service import WeatherService


__all__ = [
    'ImageRecognitionService',
    'WeatherService'
]
