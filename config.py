# -*- coding: utf-8 -*-
"""
配置文件
定义应用的所有配置参数，包括数据库、API密钥、文件上传等
"""

import os
from datetime import timedelta


class Config:
    """基础配置类，定义所有环境共享的配置"""
    # 应用密钥，用于加密会话、CSRF保护等
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 项目根目录路径
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'fashion_ai.db')
    # 禁用SQLAlchemy的修改跟踪，提高性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 是否在控制台输出SQL语句（开发调试用）
    SQLALCHEMY_ECHO = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')  # 上传文件保存目录
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传文件大小：16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的文件扩展名
    
    # Redis和Celery配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # 外部API密钥配置
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')  # 阿里云千问API密钥
    # 兼容两种环境变量命名：QWEATHER_API_KEY 或 WEATHER_API_KEY
    QWEATHER_API_KEY = os.environ.get('QWEATHER_API_KEY') or os.environ.get('WEATHER_API_KEY', '')
    # 阿里云OSS配置
    ALIYUN_OSS_ACCESS_KEY_ID = os.environ.get('ALIYUN_OSS_ACCESS_KEY_ID', '')
    ALIYUN_OSS_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_OSS_ACCESS_KEY_SECRET', '')
    ALIYUN_OSS_BUCKET_NAME = os.environ.get('ALIYUN_OSS_BUCKET_NAME', '')
    ALIYUN_OSS_ENDPOINT = os.environ.get('ALIYUN_OSS_ENDPOINT', '')

    # 和风天气API Host（新版用户需要配置，例如：xxx.qweatherapi.com）
    QWEATHER_API_HOST = os.environ.get('QWEATHER_API_HOST', '')
    
    # Session配置
    SESSION_COOKIE_HTTPONLY = True  # Session Cookie仅HTTP可用
    SESSION_COOKIE_SAMESITE = 'Lax'  # Session Cookie SameSite策略
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Session有效期


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True  # 开启调试模式
    SQLALCHEMY_ECHO = True  # 输出SQL语句用于调试


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False  # 关闭调试模式
    # 生产环境建议使用更安全的配置
    SESSION_COOKIE_SECURE = True  # 仅HTTPS传输Session Cookie


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True  # 开启测试模式
    # 使用内存数据库，每次测试后自动清理
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # 测试环境禁用CSRF保护


# 配置映射字典，用于根据环境选择不同的配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}