# -*- coding: utf-8 -*-
"""
推荐引擎服务
根据用户特征、场景、天气等信息生成个性化穿搭推荐
"""

from typing import Dict, List
import random


class RecommendationService:
    """
    推荐引擎服务类
    提供基于用户特征、场景、天气等信息的个性化穿搭推荐
    """
    
    def __init__(self):
        """
        初始化推荐服务，加载推荐规则和模型
        """
        # 加载推荐规则
        self.style_rules = self._load_style_rules()
        self.color_matching = self._load_color_matching_rules()
        self.weather_rules = self._load_weather_rules()
    
    def generate_recommendations(
        self,
        user_profile: Dict,
        clothing_items: List[Dict],
        scene: str,
        weather_data: Dict
    ) -> List[Dict]:
        """
        生成个性化穿搭推荐
        
        Args:
            user_profile: 用户档案，包含体型、肤色、风格偏好等
                {
                    "body_type": "体型",
                    "skin_tone": "肤色",
                    "style_preference": "风格偏好"
                }
            clothing_items: 用户现有衣物列表
            scene: 使用场景，如'casual'（休闲）、'business'（商务）等
            weather_data: 天气数据
                {
                    "temperature": 温度,
                    "condition": 天气状况,
                    "humidity": 湿度,
                    "wind_speed": 风速,
                    "location": 地点
                }
        
        Returns:
            List[Dict]: 推荐结果列表，每个元素包含推荐衣物的详细信息
        """
        # 从天气数据中提取关键信息
        temperature = weather_data.get('temperature', 20)
        weather_condition = weather_data.get('condition', 'sunny')
        
        # 从用户档案中提取关键特征
        body_type = user_profile.get('body_type', 'standard')
        skin_tone = user_profile.get('skin_tone', 'medium')
        
        # 1. 根据天气过滤推荐项
        suitable_items = self._filter_by_weather(clothing_items, temperature, weather_condition)
        
        # 2. 根据场景过滤推荐项
        scene_items = self._filter_by_scene(suitable_items, scene)
        
        # 3. 根据体型匹配推荐项
        matched_items = self._match_body_type(scene_items, body_type)
        
        # 4. 根据肤色协调颜色
        color_coordinated = self._coordinate_colors(matched_items, skin_tone)
        
        # 5. 为每个推荐项生成详细信息
        recommendations = []
        for item in color_coordinated:
            recommendation = {
                'item_name': item.get('item_name', ''),
                'item_type': item.get('type', ''),
                'color': item.get('color', ''),
                'brand': item.get('brand', ''),
                'price': self._estimate_price(item),
                'match_score': item.get('match_score', 0.8),
                'reason': self._generate_recommendation_reason(item, scene, weather_data)
            }
            recommendations.append(recommendation)
        
        # 6. 按匹配分数排序，返回前10个推荐项
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:10]
    
    def _filter_by_weather(self, items: List[Dict], temperature: float, condition: str) -> List[Dict]:
        """
        根据天气过滤推荐项
        
        Args:
            items: 衣物列表
            temperature: 温度（℃）
            condition: 天气状况
        
        Returns:
            List[Dict]: 符合天气条件的衣物列表
        """
        filtered = []
        for item in items:
            item_type = item.get('type', '')
            
            # 根据温度选择合适的衣物类型
            if temperature < 10:  # 寒冷天气
                if item_type in ['外套', '毛衣', '羽绒服', '大衣']:
                    filtered.append(item)
            elif temperature < 20:  # 凉爽天气
                if item_type in ['外套', '长袖', '毛衣']:
                    filtered.append(item)
            else:  # 温暖/炎热天气
                if item_type in ['T恤', '短袖', '衬衫', '连衣裙']:
                    filtered.append(item)
            
            # 雨天优先推荐外套
            if condition == 'rainy' and item_type in ['外套', '雨衣']:
                filtered.append(item)
        
        # 如果过滤后为空，返回原始列表
        return filtered if filtered else items
    
    def _filter_by_scene(self, items: List[Dict], scene: str) -> List[Dict]:
        """
        根据场景过滤推荐项
        
        Args:
            items: 衣物列表
            scene: 使用场景
        
        Returns:
            List[Dict]: 符合场景的衣物列表
        """
        # 场景与风格的映射关系
        scene_styles = {
            'casual': ['休闲', '运动', '简约'],      # 日常休闲
            'business': ['商务', '正式', '简约'],     # 商务会议
            'date': ['时尚', '优雅', '浪漫'],         # 休闲约会
            'party': ['时尚', '潮流', '个性'],        # 聚会派对
            'work': ['商务', '简约', '正式']         # 工作通勤
        }
        
        # 获取当前场景对应的目标风格
        target_styles = scene_styles.get(scene, ['休闲'])
        filtered = []
        
        # 过滤出符合目标风格的衣物
        for item in items:
            item_style = item.get('style', '')
            if any(style in item_style for style in target_styles):
                filtered.append(item)
        
        # 如果过滤后为空，返回原始列表
        return filtered if filtered else items
    
    def _match_body_type(self, items: List[Dict], body_type: str) -> List[Dict]:
        """
        根据体型匹配推荐项
        
        Args:
            items: 衣物列表
            body_type: 体型类型
        
        Returns:
            List[Dict]: 符合体型的衣物列表，带有匹配分数
        """
        # 体型与穿搭规则的映射关系
        body_type_rules = {
            'pear': {'avoid': ['紧身裤', '包臀裙'], 'prefer': ['A字裙', '阔腿裤']},  # 梨形身材
            'apple': {'avoid': ['紧身衣', '高腰裤'], 'prefer': ['宽松上衣', '直筒裤']},  # 苹果形身材
            'hourglass': {'avoid': ['宽松长裙'], 'prefer': ['收腰连衣裙', '合身上衣']},  # 沙漏形身材
            'rectangle': {'avoid': ['直筒裙'], 'prefer': ['有腰线的衣服', 'A字裙']}  # 矩形身材
        }
        
        # 获取当前体型对应的规则
        rules = body_type_rules.get(body_type, {})
        avoid = rules.get('avoid', [])
        prefer = rules.get('prefer', [])
        
        matched = []
        for item in items:
            item_name = item.get('item_name', '')
            # 初始化匹配分数
            match_score = item.get('match_score', 0.8)
            
            # 如果包含避免的元素，降低匹配分数
            if any(a in item_name for a in avoid):
                match_score *= 0.7
            # 如果包含推荐的元素，提高匹配分数
            if any(p in item_name for p in prefer):
                match_score *= 1.2
            
            item['match_score'] = match_score
            matched.append(item)
        
        return matched
    
    def _coordinate_colors(self, items: List[Dict], skin_tone: str) -> List[Dict]:
        """
        根据肤色协调颜色
        
        Args:
            items: 衣物列表
            skin_tone: 肤色类型
        
        Returns:
            List[Dict]: 颜色协调后的衣物列表，带有更新的匹配分数
        """
        # 肤色与适合颜色的映射关系
        color_rules = {
            'fair': {'good': ['蓝色', '粉色', '紫色', '绿色'], 'avoid': ['黄色', '橙色']},  # 白皙肤色
            'medium': {'good': ['红色', '蓝色', '白色', '黑色'], 'avoid': []},  # 中等肤色
            'dark': {'good': ['白色', '米色', '浅蓝', '浅粉'], 'avoid': ['黑色', '深棕色']}  # 深色肤色
        }
        
        # 获取当前肤色对应的规则
        rules = color_rules.get(skin_tone, {})
        good_colors = rules.get('good', [])
        avoid_colors = rules.get('avoid', [])
        
        for item in items:
            color = item.get('color', '')
            match_score = item.get('match_score', 0.8)
            
            # 如果是适合的颜色，提高匹配分数
            if any(c in color for c in good_colors):
                match_score *= 1.1
            # 如果是需要避免的颜色，降低匹配分数
            if any(c in color for c in avoid_colors):
                match_score *= 0.8
            
            item['match_score'] = match_score
        
        return items
    
    def _estimate_price(self, item: Dict) -> float:
        """
        预估衣物价格
        
        Args:
            item: 衣物信息
        
        Returns:
            float: 预估价格
        """
        # 基础价格
        base_price = 200.0
        
        # 根据品牌调整价格
        brand = item.get('brand', '')
        brand_factor = 1.0
        if brand in ['ZARA', 'H&M', '优衣库']:
            brand_factor = 1.0
        elif brand in ['Gucci', 'Prada', 'Chanel']:
            brand_factor = 5.0
        elif brand in ['Nike', 'Adidas', 'PUMA']:
            brand_factor = 1.5
        
        # 根据类型调整价格
        item_type = item.get('type', '')
        if item_type in ['外套', '羽绒服']:
            base_price = 500.0
        elif item_type in ['鞋子']:
            base_price = 400.0
        
        # 添加随机波动（±20%）
        price = base_price * brand_factor * random.uniform(0.8, 1.2)
        
        return round(price, 2)
    
    def _generate_recommendation_reason(self, item: Dict, scene: str, weather: Dict) -> str:
        """
        生成推荐理由
        
        Args:
            item: 推荐项
            scene: 使用场景
            weather: 天气数据
        
        Returns:
            str: 推荐理由
        """
        reasons = []
        
        # 添加天气相关理由
        temperature = weather.get('temperature', 20)
        if temperature < 10:
            reasons.append(f'当前气温{temperature}°C，适合保暖穿搭')
        elif temperature > 25:
            reasons.append(f'当前气温{temperature}°C，适合轻薄透气')
        
        # 添加场景相关理由
        scene_reasons = {
            'casual': '适合日常休闲场合',
            'business': '符合商务着装要求',
            'date': '展现优雅气质',
            'party': '时尚潮流风格',
            'work': '专业得体'
        }
        reasons.append(scene_reasons.get(scene, ''))
        
        # 移除空理由并合并
        return '；'.join([r for r in reasons if r])
    
    def _load_style_rules(self) -> Dict:
        """
        加载风格规则
        
        Returns:
            Dict: 风格规则
        """
        return {}
    
    def _load_color_matching_rules(self) -> Dict:
        """
        加载颜色匹配规则
        
        Returns:
            Dict: 颜色匹配规则
        """
        return {}
    
    def _load_weather_rules(self) -> Dict:
        """
        加载天气规则
        
        Returns:
            Dict: 天气规则
        """
        return {}
