# -*- coding: utf-8 -*-
"""
路由文件
定义应用的所有路由，包括页面路由和API路由
使用蓝图（Blueprint）组织路由，分为主路由和API路由
"""

from flask import Blueprint, render_template, request, jsonify, current_app, session, send_from_directory
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


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    服务上传的文件
    """
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# ------------------------------ API路由 ------------------------------

@api_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    图片上传API
    
    接收用户上传的图片，保存到服务器，并调用图像识别服务进行分析
    如果提供了location_id，还会根据天气生成穿搭推荐
    
    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Body: 
            - file: 图片文件
            - location_id: 城市ID (可选)
    
    Response:
        - Success: {
            "success": true,
            "file_path": "图片保存路径",
            "analysis": {
                "clothing_items": [],
                "body_features": {}, 
                "overall_style": "",
                "recommendation": {}
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
    location_id = request.form.get('location_id', '').strip()
    
    # 检查文件是否被选择
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # 保存上传的文件
        file_path = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        
        # 获取天气数据（如果提供了location_id）
        weather_data = None
        if location_id:
            try:
                from services.weather_service import WeatherService
                weather_service = WeatherService()
                weather_data = weather_service.get_weather_now(location_id)
            except Exception as e:
                print(f"获取天气失败: {str(e)}")
        
        # 调用图像识别服务
        from services.image_recognition_service import ImageRecognitionService
        image_service = ImageRecognitionService()
        # 传入天气数据进行分析和推荐
        analysis_result = image_service.analyze_image(file_path, weather_data)
        
        # 获取文件名用于生成URL
        filename = os.path.basename(file_path)
        file_url = f"/uploads/{filename}"
        
        # --- 优化：自动上传模特图到 OSS 并缓存 ---
        oss_url = None
        try:
            from services.virtual_tryon_service import VirtualTryonService
            tryon_service = VirtualTryonService()
            print(f"Auto-uploading model to OSS: {file_path}")
            oss_url = tryon_service._upload_file_to_oss(file_path)
            
            if oss_url:
                # 存入 Session，供后续试穿复用
                session['model_image_oss_url'] = oss_url
                session['model_image_local_path'] = file_url
                session.permanent = True  # 确保 Session 持久化
                print(f"Model cached in session: {oss_url}")
        except Exception as oss_e:
            print(f"Auto-upload model failed: {str(oss_e)}")
            # 不阻断主流程，前端可以降级处理
        # ---------------------------------------
        
        # 返回成功响应
        return jsonify({
            'success': True,
            'file_path': file_path,
            'file_url': file_url,
            'oss_url': oss_url, # 返回 OSS URL
            'analysis': analysis_result
        })
    except Exception as e:
        # 捕获并返回所有异常
        return jsonify({'error': str(e)}), 500


@api_bp.route('/current-model', methods=['GET'])
def get_current_model():
    """获取当前 Session 中的模特信息"""
    oss_url = session.get('model_image_oss_url')
    local_url = session.get('model_image_local_path')
    
    if oss_url:
        return jsonify({
            'success': True,
            'oss_url': oss_url,
            'local_url': local_url
        })
    else:
        return jsonify({'success': False, 'message': 'No model set'})


@api_bp.route('/city-lookup', methods=['GET'])
def city_lookup():
    """
    城市搜索API
    
    根据关键词搜索城市
    
    Request:
        - Method: GET
        - Query: keyword=搜索关键词
        
    Response:
        - Success: {
            "success": true,
            "cities": [城市列表]
        }
    """
    keyword = request.args.get('keyword', '').strip()
    adm = request.args.get('adm', '').strip()
    
    print(f"API Request: keyword='{keyword}', adm='{adm}'")  # 添加日志
    
    if not keyword:
        return jsonify({'success': True, 'cities': []})
        
    try:
        from services.weather_service import WeatherService
        weather_service = WeatherService()
        cities = weather_service.search_city(keyword, adm)
        print(f"API Response: found {len(cities)} cities") # 添加日志
        return jsonify({'success': True, 'cities': cities})
    except Exception as e:
        print(f"API Error: {str(e)}") # 添加日志
        return jsonify({'success': False, 'error': str(e)})


@api_bp.route('/weather', methods=['GET'])
def get_weather():
    """
    实时天气API
    
    获取指定城市ID的实时天气
    
    Request:
        - Method: GET
        - Query: location_id=城市ID
        
    Response:
        - Success: {
            "success": true,
            "weather": {天气数据}
        }
    """
    location_id = request.args.get('location_id', '').strip()
    if not location_id:
        return jsonify({'error': 'Location ID is required'}), 400
        
    try:
        from services.weather_service import WeatherService
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_now(location_id)
        
        if weather_data:
            return jsonify({'success': True, 'weather': weather_data})
        else:
            return jsonify({'error': 'Failed to fetch weather data'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/image-search', methods=['GET'])
def image_search():
    """
    图片搜索API
    
    根据分类、风格和颜色搜索相似衣物
    
    Request:
        - Method: GET
        - Query: 
            - category: 类别 (top/bottom/etc)
            - style: 风格
            - color: 颜色
            
    Response:
        - Success: {
            "success": true,
            "results": [衣物列表]
        }
    """
    category = request.args.get('category', 'top')
    style = request.args.get('style', '')
    color = request.args.get('color', '')
    
    try:
        from services.image_search_service import ImageSearchService
        service = ImageSearchService()
        results = service.search_similar_garments(category, style, color)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/upload-to-oss', methods=['POST'])
def upload_to_oss_route():
    """
    专门的 OSS 上传接口
    Request: { "local_path": "c:/..." }
    Response: { "success": true, "url": "https://..." }
    """
    try:
        data = request.json
        if not data:
            print("OSS Upload: No JSON data received")
            return jsonify({'success': False, 'error': 'No JSON data'}), 400
             
        local_path = data.get('local_path')
        print(f"OSS Upload: Requested upload for local_path: {local_path}")
        
        if not local_path:
            return jsonify({'success': False, 'error': 'No local_path provided'}), 400
            
        from services.virtual_tryon_service import VirtualTryonService
        service = VirtualTryonService()
        
        # 确保路径是绝对路径
        if not os.path.isabs(local_path):
            original_path = local_path
            local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(local_path))
            print(f"OSS Upload: Resolved relative path '{original_path}' to absolute path: {local_path}")
        else:
            print(f"OSS Upload: Path is already absolute: {local_path}")
             
        # 检查文件是否存在
        if not os.path.exists(local_path):
            print(f"OSS Upload: File not found at {local_path}")
            return jsonify({'success': False, 'error': f'File not found: {local_path}'}), 404
        
        # 打印文件大小
        file_size = os.path.getsize(local_path)
        print(f"OSS Upload: File exists. Size: {file_size} bytes")
             
        oss_url = service._upload_file_to_oss(local_path)
        
        if oss_url:
            print(f"OSS Upload: Success! URL: {oss_url}")
            return jsonify({'success': True, 'url': oss_url})
        else:
            print("OSS Upload: Failed (service returned None)")
            return jsonify({'success': False, 'error': 'Upload to OSS failed (Check server logs)'}), 500
            
    except Exception as e:
        import traceback
        print(f"OSS Upload Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/try-on', methods=['POST'])
def try_on():
    """
    虚拟试穿API - 提交任务
    Request:
        - Method: POST
        - Body: {
            "person_image_url": "人物图片URL",
            "clothing_image_url": "衣物图片URL" (单件试穿用),
            "top_garment_url": "上装URL" (全身试穿用),
            "bottom_garment_url": "下装URL" (全身试穿用),
            "clothing_type": "top/bottom/full"
        }
    """
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
    person_image_url = data.get('person_image_url')
    clothing_type = data.get('clothing_type', 'top')
    
    # 根据模式检查参数
    clothing_image_url = data.get('clothing_image_url')
    top_garment_url = data.get('top_garment_url')
    bottom_garment_url = data.get('bottom_garment_url')
    
    if not person_image_url:
        return jsonify({'success': False, 'error': 'Missing person image URL'}), 400
        
    if clothing_type == 'full':
        if not top_garment_url or not bottom_garment_url:
             return jsonify({'success': False, 'error': 'Missing top or bottom garment URL for full try-on'}), 400
    else:
        if not clothing_image_url and not top_garment_url and not bottom_garment_url:
             # 兼容逻辑：如果没有 clothing_image_url，尝试用 top/bottom 填充
             if clothing_type == 'top' and top_garment_url:
                 clothing_image_url = top_garment_url
             elif clothing_type == 'bottom' and bottom_garment_url:
                 clothing_image_url = bottom_garment_url
             else:
                return jsonify({'success': False, 'error': 'Missing clothing image URL'}), 400
        
    try:
        from services.virtual_tryon_service import VirtualTryonService
        service = VirtualTryonService()
        
        # 此时前端传来的应该是已经是 OSS URL 了，但为了保险，service 内部还是保留了 _resolve_local_url 逻辑
        # 不过主要依赖前端传正确的 URL
        
        result = service.generate_tryon(
            person_image_url=person_image_url,
            clothing_image_url=clothing_image_url,
            clothing_type=clothing_type,
            top_garment_url=top_garment_url,
            bottom_garment_url=bottom_garment_url
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/upload-garment', methods=['POST'])
def upload_garment():
    """
    衣物上传API
    上传衣物图片并返回URL
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
        
    if file:
        # 修正文件名处理逻辑：不依赖secure_filename处理中文名
        original_filename = file.filename
        if not original_filename:
            original_filename = "unnamed.jpg"
            
        # 仅保留扩展名，其余部分重命名
        ext = os.path.splitext(original_filename)[1]
        if not ext:
            ext = ".jpg"
            
        # 加上时间戳生成新文件名
        filename = f"garment_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        
        # 确保目录存在
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(file_path)
            file_url = f"/uploads/{filename}"
            
            # --- 优化：自动上传衣物到 OSS ---
            oss_url = None
            try:
                from services.virtual_tryon_service import VirtualTryonService
                service = VirtualTryonService()
                print(f"Auto-uploading garment to OSS: {file_path}")
                oss_url = service._upload_file_to_oss(file_path)
            except Exception as oss_e:
                print(f"Auto-upload garment failed: {str(oss_e)}")
            # --------------------------------
            
            return jsonify({
                'success': True,
                'file_path': file_path,
                'file_url': file_url,
                'oss_url': oss_url
            })
        except Exception as e:
            print(f"Upload failed: {str(e)}")
            return jsonify({'success': False, 'error': f"Save failed: {str(e)}"}), 500


@api_bp.route('/try-on/status/<task_id>', methods=['GET'])
def try_on_status(task_id):
    """
    虚拟试穿API - 查询状态
    
    查询虚拟试穿任务的状态
    
    Request:
        - Method: GET
        
    Response:
        - Success: {
            "success": true,
            "status": "SUCCEEDED/FAILED/RUNNING",
            "result_url": "结果图片URL" (如果成功)
        }
    """
    try:
        from services.virtual_tryon_service import VirtualTryonService
        service = VirtualTryonService()
        result = service.check_task_status(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
