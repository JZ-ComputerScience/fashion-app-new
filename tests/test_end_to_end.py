# -*- coding: utf-8 -*-
"""
端到端测试脚本
用于验证整个应用的功能
"""

import os
import sys
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoints():
    """
    测试API端点
    """
    print("=== 测试API端点 ===")
    
    base_url = "http://127.0.0.1:5000"
    
    # 测试页面路由
    test_pages = [
        "/",
        "/upload"
    ]
    
    # 测试API路由
    test_api = [
        "/api/upload"
    ]
    
    print("测试页面路由：")
    for page in test_pages:
        try:
            response = requests.get(f"{base_url}{page}")
            if response.status_code == 200:
                print(f"✓ {page} - 成功访问")
            else:
                print(f"✗ {page} - 访问失败，状态码：{response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ {page} - 无法连接到服务器，请确保Flask应用正在运行")
        except Exception as e:
            print(f"✗ {page} - 访问失败：{str(e)}")
    
    print("\n测试API路由：")
    for api in test_api:
        try:
            # 对于POST请求的API，使用GET请求会返回405 Method Not Allowed
            # 或者如果是上传API，可能需要构造Multipart请求
            # 这里简单测试端点是否存在
            response = requests.get(f"{base_url}{api}")
            if response.status_code in [200, 400, 405]:
                print(f"✓ {api} - 成功访问")
            else:
                print(f"✗ {api} - 访问失败，状态码：{response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ {api} - 无法连接到服务器，请确保Flask应用正在运行")
        except Exception as e:
            print(f"✗ {api} - 访问失败：{str(e)}")
    
    print("=== API端点测试完成 ===")
    return True

def test_application_structure():
    """
    测试应用结构
    """
    print("\n=== 测试应用结构 ===")
    
    # 检查关键目录是否存在
    key_directories = [
        "services",
        "utils",
        "templates",
        "static",
        "uploads",
        "tests"
    ]
    
    for directory in key_directories:
        if os.path.exists(directory):
            print(f"✓ {directory} - 目录存在")
        else:
            print(f"✗ {directory} - 目录不存在")
    
    # 检查关键文件是否存在
    key_files = [
        "app.py",
        "config.py",
        "models.py",
        "routes.py",
        "requirements.txt",
        ".env",
        ".env.example"
    ]
    
    for file in key_files:
        if os.path.exists(file):
            print(f"✓ {file} - 文件存在")
        else:
            print(f"✗ {file} - 文件不存在")
    
    print("=== 应用结构测试完成 ===")
    return True

if __name__ == "__main__":
    # 运行端到端测试
    test_application_structure()
    test_api_endpoints()
