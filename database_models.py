# -*- coding: utf-8 -*-
"""
数据库模型文件
定义应用的数据库结构，包括用户、档案、上传历史、衣物识别、推荐结果等模型
"""

from flask_sqlalchemy import SQLAlchemy  # 导入SQLAlchemy ORM
from datetime import datetime  # 导入日期时间模块

# 创建SQLAlchemy实例，用于数据库操作
db = SQLAlchemy()


class User(db.Model):
    """用户模型
    存储用户的基本信息
    """
    __tablename__ = 'users'  # 数据库表名
    
    id = db.Column(db.Integer, primary_key=True)  # 用户ID，主键
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名，唯一，不能为空
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱，唯一，不能为空
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间，默认当前UTC时间
    
    # 关系定义（一对多）
    user_profiles = db.relationship('UserProfile', backref='user', lazy=True, cascade='all, delete-orphan')  # 用户档案
    upload_history = db.relationship('UploadHistory', backref='user', lazy=True, cascade='all, delete-orphan')  # 上传历史
    recommendations = db.relationship('Recommendation', backref='user', lazy=True, cascade='all, delete-orphan')  # 推荐记录


class UserProfile(db.Model):
    """用户档案模型
    存储用户的详细信息和偏好设置
    """
    __tablename__ = 'user_profiles'  # 数据库表名
    
    id = db.Column(db.Integer, primary_key=True)  # 档案ID，主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户ID，外键
    
    # 用户身体特征
    body_type = db.Column(db.String(50))  # 体型：梨形、苹果形、沙漏形等
    height = db.Column(db.Float)  # 身高（cm）
    weight = db.Column(db.Float)  # 体重（kg）
    skin_tone = db.Column(db.String(50))  # 肤色：白皙、中等、深色等
    style_preference = db.Column(db.String(100))  # 风格偏好：休闲、商务、时尚等
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间


class UploadHistory(db.Model):
    """上传历史模型
    存储用户上传的照片记录
    """
    __tablename__ = 'upload_history'  # 数据库表名
    
    id = db.Column(db.Integer, primary_key=True)  # 上传记录ID，主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户ID，外键
    image_path = db.Column(db.String(255), nullable=False)  # 图片保存路径
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # 上传时间
    
    # 关系定义（一对多）
    clothing_items = db.relationship('ClothingItem', backref='upload_history', lazy=True, cascade='all, delete-orphan')  # 识别出的衣物


class ClothingItem(db.Model):
    """衣物项目模型
    存储从图片中识别出的衣物信息
    """
    __tablename__ = 'clothing_items'  # 数据库表名
    
    id = db.Column(db.Integer, primary_key=True)  # 衣物ID，主键
    upload_id = db.Column(db.Integer, db.ForeignKey('upload_history.id'), nullable=False)  # 关联上传记录ID，外键
    
    # 衣物属性
    item_type = db.Column(db.String(50))  # 衣物类型：上衣、下装、外套、鞋子等
    color = db.Column(db.String(50))  # 颜色
    style = db.Column(db.String(100))  # 风格：休闲、商务、运动等
    material = db.Column(db.String(50))  # 材质：棉、麻、丝等
    brand = db.Column(db.String(100))  # 品牌（如果识别出）
    confidence = db.Column(db.Float)  # 识别置信度（0-1）
    attributes = db.Column(db.JSON)  # 其他属性，JSON格式存储


class Recommendation(db.Model):
    """推荐记录模型
    存储系统生成的穿搭推荐
    """
    __tablename__ = 'recommendations'  # 数据库表名
    
    id = db.Column(db.Integer, primary_key=True)  # 推荐记录ID，主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户ID，外键
    
    # 推荐上下文
    scene = db.Column(db.String(100))  # 使用场景：日常、商务、约会等
    weather = db.Column(db.String(50))  # 天气状况：晴天、雨天、雪天等
    temperature = db.Column(db.Float)  # 温度（℃）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    # 关系定义（一对多）
    recommended_items = db.relationship('RecommendedItem', backref='recommendation', lazy=True, cascade='all, delete-orphan')  # 推荐的衣物
    virtual_tryon_result = db.relationship('VirtualTryonResult', backref='recommendation', uselist=False, cascade='all, delete-orphan')  # 虚拟试穿结果（一对一）


class RecommendedItem(db.Model):
    """推荐衣物模型
    存储每个推荐的具体衣物信息
    """
    __tablename__ = 'recommended_items'  # 数据库表名
    
    id = db.Column(db.Integer, primary_key=True)  # 推荐衣物ID，主键
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendations.id'), nullable=False)  # 关联推荐记录ID，外键
    
    # 衣物信息
    item_name = db.Column(db.String(200))  # 衣物名称
    item_type = db.Column(db.String(50))  # 衣物类型
    color = db.Column(db.String(50))  # 颜色
    brand = db.Column(db.String(100))  # 品牌
    price = db.Column(db.Float)  # 预估价格
    taobao_url = db.Column(db.String(500))  # 淘宝购买链接
    image_url = db.Column(db.String(500))  # 衣物图片URL
    match_score = db.Column(db.Float)  # 匹配分数（0-1）


class VirtualTryonResult(db.Model):
    """虚拟试穿结果模型
    存储虚拟试穿的结果信息
    """
    __tablename__ = 'virtual_tryon_results'  # 数据库表名
    
    id = db.Column(db.Integer, primary_key=True)  # 试穿结果ID，主键
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendations.id'), nullable=False)  # 关联推荐记录ID，外键
    
    # 试穿相关图片路径
    original_image_path = db.Column(db.String(255))  # 原始人物图片路径
    clothing_image_path = db.Column(db.String(255))  # 服装图片路径
    result_image_path = db.Column(db.String(255))  # 试穿结果图片路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    status = db.Column(db.String(20), default='pending')  # 试穿状态：pending（待处理）、processing（处理中）、completed（已完成）、failed（失败）
