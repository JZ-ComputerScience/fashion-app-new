/**
 * 推荐页面JavaScript
 * 处理推荐表单提交、天气显示和推荐结果展示
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const recommendationForm = document.getElementById('recommendationForm');
    const recommendBtn = document.getElementById('recommendBtn');
    const recommendSpinner = document.getElementById('recommendSpinner');
    const recommendBtnText = document.getElementById('recommendBtnText');
    const weatherInfo = document.getElementById('weatherInfo');
    const weatherContent = document.getElementById('weatherContent');
    const recommendationResult = document.getElementById('recommendationResult');
    const recommendationItems = document.getElementById('recommendationItems');

    /**
     * 推荐表单提交处理
     * 收集用户输入，发送推荐请求
     */
    recommendationForm.addEventListener('submit', async function(e) {
        // 阻止表单默认提交行为
        e.preventDefault();

        // 收集表单数据
        const location = document.getElementById('location').value;
        const scene = document.getElementById('scene').value;
        const bodyType = document.getElementById('bodyType').value;
        const skinTone = document.getElementById('skinTone').value;
        const stylePreference = document.getElementById('stylePreference').value;

        // 构建用户档案对象
        const user_profile = {
            body_type: bodyType,
            skin_tone: skinTone,
            style_preference: stylePreference
        };

        // 显示加载状态
        recommendBtn.disabled = true;
        recommendSpinner.classList.remove('d-none');
        recommendBtnText.textContent = '生成推荐中...';

        try {
            // 发送POST请求到推荐API
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'  // 设置请求头为JSON
                },
                body: JSON.stringify({
                    user_profile: user_profile,
                    scene: scene,
                    location: location,
                    clothing_items: []  // 当前没有现有衣物，为空数组
                })
            });

            // 解析响应数据
            const data = await response.json();

            if (data.success) {
                // 显示天气信息
                displayWeather(data.weather);
                // 显示推荐结果
                displayRecommendations(data.recommendations);
            } else {
                // 显示错误信息
                alert('获取推荐失败: ' + data.error);
            }
        } catch (error) {
            // 捕获网络错误
            alert('获取推荐失败: ' + error.message);
        } finally {
            // 恢复按钮状态
            recommendBtn.disabled = false;
            recommendSpinner.classList.add('d-none');
            recommendBtnText.textContent = '获取推荐';
        }
    });

    /**
     * 显示天气信息
     * 将天气数据渲染到页面上
     * @param {Object} weather - 天气数据对象
     */
    function displayWeather(weather) {
        // 天气图标映射
        const weatherIcons = {
            'sunny': '☀️',
            'cloudy': '☁️',
            'rainy': '🌧️',
            'snowy': '❄️'
        };

        // 获取天气图标
        const icon = weatherIcons[weather.condition] || '🌤️';
        
        // 生成天气HTML
        weatherContent.innerHTML = `
            <div class="weather-info">
                <div class="weather-icon">${icon}</div>
                <div>
                    <h4>${weather.temperature}°C</h4>
                    <p class="mb-0">${weather.condition}</p>
                </div>
                <div class="weather-details">
                    <div><strong>湿度:</strong> ${weather.humidity}%</div>
                    <div><strong>风速:</strong> ${weather.wind_speed} m/s</div>
                    <div><strong>地点:</strong> ${weather.location}</div>
                </div>
            </div>
        `;
        
        // 显示天气信息卡片
        weatherInfo.style.display = 'block';
    }

    /**
     * 显示推荐结果
     * 将推荐数据渲染到页面上
     * @param {Array} recommendations - 推荐结果数组
     */
    function displayRecommendations(recommendations) {
        let html = '';
        
        // 遍历推荐结果
        recommendations.forEach(item => {
            // 生成淘宝链接HTML
            let taobaoLinksHtml = '';
            if (item.taobao_links && item.taobao_links.length > 0) {
                taobaoLinksHtml = `
                    <h6>购买链接</h6>
                    <ul class="list-unstyled">
                        ${item.taobao_links.map(link => `
                            <li>
                                <a href="${link.url}" target="_blank" class="taobao-link">
                                    ${link.title} - ¥${link.price}
                                </a>
                                <small class="text-muted d-block">${link.shop} | ${link.sales}</small>
                            </li>
                        `).join('')}
                    </ul>
                `;
            }
            
            // 生成单个推荐项HTML
            html += `
                <div class="col-md-6 mb-4">
                    <div class="card recommendation-item h-100">
                        <div class="card-body">
                            <h5 class="card-title">${item.item_name}</h5>
                            <p class="card-text">
                                <strong>类型:</strong> ${item.item_type}<br>
                                <strong>颜色:</strong> ${item.color}<br>
                                <strong>品牌:</strong> ${item.brand || '未知'}
                            </p>
                            <p class="card-text">
                                <strong>匹配度:</strong> 
                                <span class="match-score">${(item.match_score * 100).toFixed(0)}%</span>
                            </p>
                            <p class="card-text">
                                <strong>预估价格:</strong> 
                                <span class="price">¥${item.price}</span>
                            </p>
                            <p class="card-text text-muted">
                                <small>${item.reason}</small>
                            </p>
                            ${taobaoLinksHtml}
                        </div>
                    </div>
                </div>
            `;
        });

        // 插入推荐结果HTML
        recommendationItems.innerHTML = html;
        // 显示推荐结果容器
        recommendationResult.style.display = 'block';
    }
});
