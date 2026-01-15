# -*- coding: utf-8 -*-
"""
应用主文件
Flask应用的入口点，负责初始化应用、配置数据库、注册路由蓝图等
"""

from flask import Flask
from flask_cors import CORS  # 处理跨域请求
from flask_migrate import Migrate  # 数据库迁移工具
from config import config  # 导入配置
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def create_app(config_name='default'):
    """
    创建并配置Flask应用实例
    
    Args:
        config_name: 配置名称，可选值：'development', 'production', 'testing', 'default'
        
    Returns:
        Flask应用实例
    """
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化CORS，允许跨域请求
    CORS(app)
    
    # 延迟导入模型，避免循环导入问题
    from database_models import db
    # 初始化数据库
    db.init_app(app)
    # 初始化数据库迁移工具
    migrate = Migrate(app, db)
    
    # 延迟导入路由蓝图，避免循环导入问题
    from api_routes import main_bp, api_bp
    # 注册蓝图
    app.register_blueprint(main_bp)  # 注册主路由蓝图（无前缀）
    app.register_blueprint(api_bp, url_prefix='/api')  # 注册API路由蓝图（/api前缀）
    
    # 显式注册一个 /upload 路由到主蓝图，防止被 api_bp 的 /api/upload 覆盖或混淆
    # 虽然 main_bp 已经注册了 /upload，但为了保险起见，我们确保它工作正常
    # 注意：upload 页面路由已经在 api_routes.py 的 main_bp 中定义了
    
    # 打印所有注册的路由，用于调试
    print("=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> {rule.endpoint}")
    print("=========================")
    
    # 创建上传目录（如果不存在）
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app


if __name__ == '__main__':
    """应用入口点，直接运行此文件时执行"""
    # 创建应用实例
    app = create_app()
    
    # 应用上下文管理器，确保在应用上下文中执行数据库操作
    with app.app_context():
        from database_models import db
        # 创建所有数据库表
        db.create_all()
    
    # 启动应用服务器
    # debug=True：开启调试模式
    # use_reloader=False：禁用自动重启，解决watchdog版本兼容问题
    # host='0.0.0.0'：允许外部访问
    # port=5000：监听端口
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
