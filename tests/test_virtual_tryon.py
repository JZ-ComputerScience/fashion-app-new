# -*- coding: utf-8 -*-
"""
虚拟试衣服务测试脚本
用于验证VirtualTryonService类的功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.virtual_tryon_service import VirtualTryonService

def test_virtual_tryon_service():
    """
    测试虚拟试衣服务
    """
    print("=== 测试虚拟试衣服务 ===")
    
    try:
        # 初始化服务
        service = VirtualTryonService()
        print("✓ 成功初始化虚拟试衣服务")
        
        # 检查API密钥配置
        if hasattr(service, 'api_key') and service.api_key == "your_bailian_api_key_here":
            print("⚠️  注意：使用的是示例API密钥，实际调用会失败")
        
        # 检查客户端初始化
        if hasattr(service, 'client') and service.client is not None:
            print("✓ 成功初始化虚拟试衣客户端")
        
        print("=== 虚拟试衣服务测试完成 ===")
        return True
        
    except ValueError as e:
        if "BAILIAN_API_KEY环境变量未设置" in str(e):
            print("✗ 测试失败：" + str(e))
        else:
            print("✗ 测试失败：" + str(e))
    except Exception as e:
        print("✗ 测试失败：" + str(e))
    
    print("=== 虚拟试衣服务测试完成 ===")
    return False

if __name__ == "__main__":
    # 运行测试
    test_virtual_tryon_service()
