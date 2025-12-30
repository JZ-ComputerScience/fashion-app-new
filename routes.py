# -*- coding: utf-8 -*-
"""
路由文件
定义应用的所有路由，包括页面路由和API路由
使用蓝图（Blueprint）组织路由，分为主路由和API路由
"""

from flask import Blueprint, render_template, request, jsonify, current_app, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# 创建蓝图实例
main_bp = Blueprint('main', __name__)  # 主路由蓝图，处理页面请求
api_bp = Blueprint('api', __name__)  # API路由蓝图，处理API请求


# ------------------------------ 主路由（页面） ------------------------------

@main_bp.route('/')
def index():
    """
    首页路由
    返回应用的首页HTML
    """
    return render_template('index.html')


@main_bp.route('/upload')
def upload():
    """
    上传页面路由
    返回图片上传页面HTML
    """
    return render_template('upload.html')


@main_bp.route('/recommendation')
def recommendation():
    """
    推荐页面路由
    返回穿搭推荐页面HTML
    """
    return render_template('recommendation.html')


@main_bp.route('/tryon')
def tryon():
    """
    虚拟试穿页面路由
    返回虚拟试穿页面HTML
    """
    return render_template('tryon.html')


# ------------------------------ API路由 ------------------------------

@api_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    图片上传API
    
    接收用户上传的图片，保存到服务器，并调用图像识别服务进行分析
    
    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Body: 包含名为'file'的文件字段
    
    Response:
        - Success: {
            "success": true,
            "file_path": "图片保存路径",
            "analysis": {
                "clothing_items": [衣物识别结果数组],
                "body_features": {人物特征}, 
                "overall_style": "整体风格"
            }
        }
        - Error: {
            "error": "错误信息"
        }
    """
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # 检查文件是否被选择
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # 保存上传的文件
        file_path = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        
        # 调用图像识别服务
        from services.image_recognition_service import ImageRecognitionService
        image_service = ImageRecognitionService()
        analysis_result = image_service.analyze_image(file_path)
        
        # 返回成功响应
        return jsonify({
            'success': True,
            'file_path': file_path,
            'analysis': analysis_result
        })
    except Exception as e:
        # 捕获并返回所有异常
        return jsonify({'error': str(e)}), 500


@api_bp.route('/recommend', methods=['POST'])
def get_recommendation():
    """
    穿搭推荐API
    
    根据用户特征、场景、天气等信息生成个性化穿搭推荐
    
    Request:
        - Method: POST
        - Content-Type: application/json
        - Body: {
            "user_profile": {"body_type": "体型", "skin_tone": "肤色", ...},
            "scene": "使用场景",
            "location": "城市",
            "clothing_items": [现有衣物数组]
        }
    
    Response:
        - Success: {
            "success": true,
            "recommendations": [推荐结果数组],
            "weather": {天气数据}
        }
        - Error: {
            "error": "错误信息"
        }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 提取请求参数
        user_profile = data.get('user_profile', {})
        scene = data.get('scene', 'casual')
        location = data.get('location', 'Beijing')
        clothing_items = data.get('clothing_items', [])
        
        # 获取天气数据
        from services.weather_service import WeatherService
        weather_service = WeatherService()
        weather_data = weather_service.get_weather(location)
        
        # 生成穿搭推荐
        from services.recommendation_service import RecommendationService
        recommendation_service = RecommendationService()
        recommendations = recommendation_service.generate_recommendations(
            user_profile,
            clothing_items,
            scene,
            weather_data
        )
        
        # 获取淘宝购买链接
        from services.taobao_service import TaobaoService
        taobao_service = TaobaoService()
        for item in recommendations:
            # 为每个推荐项添加淘宝链接
            item['taobao_links'] = taobao_service.search_items(
                item['item_name'],
                item['color']
            )
        
        # 返回成功响应
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'weather': weather_data
        })
    except Exception as e:
        # 捕获并返回所有异常
        return jsonify({'error': str(e)}), 500


@api_bp.route('/virtual-tryon', methods=['POST'])
def virtual_tryon():
    """
    虚拟试穿API
    
    调用阿里云百炼API生成虚拟试穿效果图
    
    Request:
        - Method: POST
        - Content-Type: application/json
        - Body: {
            "person_image": "人物图片路径",
            "clothing_image": "服装图片路径"
        }
    
    Response:
        - Success: {
            "success": true,
            "result_image": "试穿结果图片路径"
        }
        - Error: {
            "error": "错误信息"
        }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 提取请求参数
        person_image = data.get('person_image')
        clothing_image = data.get('clothing_image')
        
        # 调用虚拟试穿服务
        from services.virtual_tryon_service import VirtualTryonService
        tryon_service = VirtualTryonService()
        result = tryon_service.generate_tryon(person_image, clothing_image)
        
        # 返回成功响应
        return jsonify({
            'success': True,
            'result_image': result
        })
    except Exception as e:
        # 捕获并返回所有异常
        return jsonify({'error': str(e)}), 500


@api_bp.route('/weather', methods=['GET'])
def get_weather():
    """
    天气查询API
    
    获取指定城市的实时天气数据
    
    Request:
        - Method: GET
        - Query Parameters: location=城市名
    
    Response:
        - Success: {
            "success": true,
            "weather": {天气数据}
        }
        - Error: {
            "error": "错误信息"
        }
    """
    try:
        # 获取查询参数
        location = request.args.get('location', 'Beijing')
        
        # 调用天气服务
        from services.weather_service import WeatherService
        weather_service = WeatherService()
        weather_data = weather_service.get_weather(location)
        
        # 返回成功响应
        return jsonify({
            'success': True,
            'weather': weather_data
        })
    except Exception as e:
        # 捕获并返回所有异常
        return jsonify({'error': str(e)}), 500


# ------------------------------ 工具函数 ------------------------------

def allowed_file(filename):
    """
    检查文件名是否为允许的图片类型
    
    Args:
        filename: 文件名
        
    Returns:
        bool: True表示允许，False表示不允许
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, upload_folder):
    """
    保存上传的文件到指定目录
    
    Args:
        file: 上传的文件对象
        upload_folder: 保存目录
        
    Returns:
        str: 保存的文件路径
    """
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    # 添加时间戳前缀，避免文件名冲突
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{filename}'
    
    # 拼接完整的文件路径
    file_path = os.path.join(upload_folder, filename)
    # 保存文件
    file.save(file_path)
    
    return file_path
