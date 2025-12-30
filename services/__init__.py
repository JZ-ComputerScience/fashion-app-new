# -*- coding: utf-8 -*-
"""
服务层包
包含应用的所有业务逻辑服务
"""

# 从各服务模块导入类，方便外部直接调用
from .image_recognition_service import ImageRecognitionService
from .recommendation_service import RecommendationService
from .weather_service import WeatherService
from .virtual_tryon_service import VirtualTryonService
from .taobao_service import TaobaoService


__all__ = [
    'ImageRecognitionService',
    'RecommendationService',
    'WeatherService',
    'VirtualTryonService',
    'TaobaoService'
]
