# -*- coding: utf-8 -*-
"""
图像识别服务测试脚本
用于验证ImageRecognitionService类的功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_recognition_service import ImageRecognitionService

def test_image_recognition_service():
    """
    测试图像识别服务
    """
    print("=== 测试图像识别服务 ===")
    
    try:
        # 初始化服务
        service = ImageRecognitionService()
        print("✓ 成功初始化图像识别服务")
        
        # 检查API密钥配置
        if service.api_key == "your_dashscope_api_key_here":
            print("⚠️  注意：使用的是示例API密钥，实际调用会失败")
        
        # 检查客户端初始化
        if hasattr(service, 'client') and service.client is not None:
            print("✓ 成功初始化OpenAI客户端")
        
        print("=== 图像识别服务测试完成 ===")
        return True
        
    except ValueError as e:
        if "DASHSCOPE_API_KEY环境变量未设置" in str(e):
            print("✗ 测试失败：" + str(e))
        else:
            print("✗ 测试失败：" + str(e))
    except Exception as e:
        print("✗ 测试失败：" + str(e))
    
    print("=== 图像识别服务测试完成 ===")
    return False

def test_api_call_structure():
    """
    测试API调用结构
    """
    print("\n=== 测试API调用结构 ===")
    
    # 检查代码结构是否正确
    try:
        # 导入必要的模块
        from openai import OpenAI
        print("✓ 成功导入OpenAI模块")
        
        # 模拟客户端初始化（不实际调用API）
        client = OpenAI(
            api_key="test_key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        print("✓ 成功创建OpenAI客户端实例")
        
        print("=== API调用结构测试完成 ===")
        return True
        
    except Exception as e:
        print("✗ 测试失败：" + str(e))
        print("=== API调用结构测试完成 ===")
        return False

if __name__ == "__main__":
    # 运行测试
    test_image_recognition_service()
    test_api_call_structure()
