# -*- coding: utf-8 -*-
"""
推荐服务测试脚本
用于验证RecommendationService类的功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.recommendation_service import RecommendationService

def test_recommendation_service():
    """
    测试推荐服务
    """
    print("=== 测试推荐服务 ===")
    
    try:
        # 初始化服务
        service = RecommendationService()
        print("✓ 成功初始化推荐服务")
        
        # 测试推荐逻辑
        # 模拟用户画像
        user_profile = {
            "body_type": "沙漏形",
            "skin_tone": "白皙",
            "style_preference": "休闲"
        }
        
        # 模拟衣物列表
        clothing_items = [
            {
                "item_name": "白色T恤",
                "type": "上衣",
                "style": "休闲",
                "color": "白色",
                "material": "棉",
                "brand": "优衣库",
                "match_score": 0.8
            },
            {
                "item_name": "蓝色牛仔裤",
                "type": "下装",
                "style": "休闲",
                "color": "蓝色",
                "material": "牛仔布",
                "brand": "Levi's",
                "match_score": 0.8
            },
            {
                "item_name": "黑色运动鞋",
                "type": "鞋子",
                "style": "运动",
                "color": "黑色",
                "material": "皮革",
                "brand": "Nike",
                "match_score": 0.8
            }
        ]
        
        # 模拟场景
        scene = "casual"
        
        # 模拟天气数据
        weather_data = {
            "temperature": 22,
            "condition": "晴",
            "humidity": 50,
            "wind_speed": 10,
            "location": "北京"
        }
        
        # 测试生成推荐
        recommendations = service.generate_recommendations(
            user_profile, clothing_items, scene, weather_data
        )
        
        if recommendations is not None and isinstance(recommendations, list):
            print("✓ 成功生成推荐")
            print(f"  生成了 {len(recommendations)} 条推荐")
            if recommendations:
                print(f"  第一条推荐：{recommendations[0]['item_name']} (分数：{recommendations[0]['match_score']:.2f})")
        
        print("=== 推荐服务测试完成 ===")
        return True
        
    except Exception as e:
        print("✗ 测试失败：" + str(e))
    
    print("=== 推荐服务测试完成 ===")
    return False

def test_recommendation_utils():
    """
    测试推荐服务工具方法
    """
    print("\n=== 测试推荐服务工具方法 ===")
    
    try:
        # 初始化服务
        service = RecommendationService()
        
        # 测试价格预估
        test_item = {
            "brand": "Nike",
            "type": "鞋子"
        }
        price = service._estimate_price(test_item)
        if price > 0:
            print(f"✓ 成功预估价格：{price} 元")
        
        # 测试推荐理由生成
        test_item = {
            "item_name": "白色T恤",
            "type": "上衣"
        }
        reason = service._generate_recommendation_reason(test_item, "casual", {"temperature": 22})
        if reason:
            print(f"✓ 成功生成推荐理由：{reason}")
        
        print("=== 推荐服务工具方法测试完成 ===")
        return True
        
    except Exception as e:
        print("✗ 测试失败：" + str(e))
    
    print("=== 推荐服务工具方法测试完成 ===")
    return False

if __name__ == "__main__":
    # 运行测试
    test_recommendation_service()
    test_recommendation_utils()
