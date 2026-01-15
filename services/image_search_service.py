import random

class ImageSearchService:
    def __init__(self):
        # In a real implementation, this would connect to an image search API or database
        pass

    def search_similar_garments(self, category, style, color):
        """
        Mock implementation of searching for similar garments.
        Returns a list of mock image URLs and details.
        """
        # Mock data based on category
        mock_results = []
        
        base_urls = {
            "top": [
                "https://img.alicdn.com/imgextra/i4/2206622432320/O1CN01S5k5Xh1Tj2j5Xh1Tj_!!2206622432320.jpg",
                "https://img.alicdn.com/imgextra/i2/2206622432320/O1CN01x4y6z81Tj2j3w7x5y_!!2206622432320.jpg"
            ],
            "bottom": [
                "https://img.alicdn.com/imgextra/i3/2206622432320/O1CN01a2b3c41Tj2j5Xh1Tj_!!2206622432320.jpg",
                "https://img.alicdn.com/imgextra/i1/2206622432320/O1CN01d5e6f71Tj2j5Xh1Tj_!!2206622432320.jpg"
            ],
            "outerwear": [
                "https://img.alicdn.com/imgextra/i4/2206622432320/O1CN01g8h9i01Tj2j5Xh1Tj_!!2206622432320.jpg"
            ]
        }
        
        # 使用稳定的占位图作为备选，防止淘宝链接失效或防盗链
        placeholder_urls = {
            "top": [
                "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500&auto=format&fit=crop&q=60",
                "https://images.unsplash.com/photo-1503342394128-c104d54dba01?w=500&auto=format&fit=crop&q=60"
            ],
            "bottom": [
                "https://images.unsplash.com/photo-1542272454315-4c01d7abdf4a?w=500&auto=format&fit=crop&q=60",
                "https://images.unsplash.com/photo-1475178626620-a4d074967452?w=500&auto=format&fit=crop&q=60"
            ],
            "outerwear": [
                "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500&auto=format&fit=crop&q=60"
            ]
        }
        
        # 优先使用 Unsplash 的稳定图片
        urls = placeholder_urls.get(category, placeholder_urls['top'])
        
        for i, url in enumerate(urls):
            mock_results.append({
                "id": f"item_{i}",
                "title": f"Fashion {style} {color} {category}",
                "image_url": url,
                "price": f"¥{random.randint(100, 500)}",
                "shop_name": "Fashion Store"
            })
            
        return mock_results
