/**
 * 上传页面JavaScript
 * 处理图片上传、预览、分析结果展示以及虚拟试穿
 */

document.addEventListener('DOMContentLoaded', function() {
    // --- 原有DOM元素 ---
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadSpinner = document.getElementById('uploadSpinner');
    const uploadBtnText = document.getElementById('uploadBtnText');
    const analysisResult = document.getElementById('analysisResult');
    const analysisContent = document.getElementById('analysisContent');
    
    // --- 级联选择器 ---
    const provinceSelect = document.getElementById('provinceSelect');
    const citySelect = document.getElementById('citySelect');
    const districtSelect = document.getElementById('districtSelect');
    const locationStatus = document.getElementById('locationStatus');
    
    const weatherInfo = document.getElementById('weatherInfo');
    const timeDisplay = document.getElementById('timeDisplay');
    
    let selectedCityId = null;
    let cityData = []; 
    let currentPersonImageUrl = ''; 

    // --- 新增：虚拟试穿部分DOM元素 ---
    const virtualTryOnSection = document.getElementById('virtualTryOnSection');
    const currentModelPreview = document.getElementById('currentModelPreview');
    const modelOssUrlInput = document.getElementById('modelOssUrl');
    const topOssUrlInput = document.getElementById('topOssUrl');
    const bottomOssUrlInput = document.getElementById('bottomOssUrl');
    
    const topGarmentInput = document.getElementById('topGarmentInput');
    const bottomGarmentInput = document.getElementById('bottomGarmentInput');
    const topGarmentStatus = document.getElementById('topGarmentStatus');
    const bottomGarmentStatus = document.getElementById('bottomGarmentStatus');
    
    const startAutoTryOnBtn = document.getElementById('startAutoTryOnBtn');
    
    // 模式选择
    const modeRadios = document.querySelectorAll('input[name="tryonMode"]');
    let currentMode = 'top';

    // --- 初始化检查 Session ---
    checkCachedModel();

    async function checkCachedModel() {
        try {
            const res = await fetch('/api/current-model');
            const data = await res.json();
            if (data.success && data.oss_url) {
                // 如果 Session 中有模特，直接显示试穿区域（如果不需要重新上传）
                // 但这里我们还是等用户操作，或者可以在页面顶部提示“检测到上次模特”
                // 为了逻辑简单，我们只在后台记录，等用户分析完或者重新上传时覆盖
                console.log("Cached model found:", data.oss_url);
            }
        } catch (e) {
            console.error("Session check failed", e);
        }
    }

    /**
     * 加载城市数据
     */
    async function loadCityData() {
        try {
            const response = await fetch('/static/js/city_data.js');
            cityData = await response.json();
            initProvinceSelect();
        } catch (error) {
            console.error('加载城市数据失败:', error);
            locationStatus.innerHTML = '<span class="text-danger">城市数据加载失败，请刷新页面重试</span>';
        }
    }

    /**
     * 初始化省份选择
     */
    function initProvinceSelect() {
        let html = '<option value="">省份</option>';
        cityData.forEach((province, index) => {
            html += `<option value="${index}">${province.name}</option>`;
        });
        provinceSelect.innerHTML = html;
    }

    /**
     * 省份改变事件
     */
    provinceSelect.addEventListener('change', function() {
        const provinceIndex = this.value;
        citySelect.innerHTML = '<option value="">城市</option>';
        citySelect.disabled = !provinceIndex;
        districtSelect.innerHTML = '<option value="">区县</option>';
        districtSelect.disabled = true;
        selectedCityId = null;
        weatherInfo.innerHTML = '<small class="text-muted">请继续选择城市和区县</small>';
        
        if (provinceIndex) {
            const cities = cityData[provinceIndex].children;
            let html = '<option value="">城市</option>';
            cities.forEach((city, index) => {
                html += `<option value="${index}">${city.name}</option>`;
            });
            citySelect.innerHTML = html;
        }
    });

    /**
     * 城市改变事件
     */
    citySelect.addEventListener('change', function() {
        const provinceIndex = provinceSelect.value;
        const cityIndex = this.value;
        districtSelect.innerHTML = '<option value="">区县</option>';
        districtSelect.disabled = !cityIndex;
        selectedCityId = null;
        weatherInfo.innerHTML = '<small class="text-muted">请继续选择区县</small>';
        
        if (provinceIndex && cityIndex) {
            const districts = cityData[provinceIndex].children[cityIndex].children;
            let html = '<option value="">区县</option>';
            districts.forEach((district, index) => {
                html += `<option value="${index}">${district.name}</option>`;
            });
            districtSelect.innerHTML = html;
        }
    });

    /**
     * 区县改变事件 - 触发天气查询
     */
    districtSelect.addEventListener('change', async function() {
        const provinceIndex = provinceSelect.value;
        const cityIndex = citySelect.value;
        const districtIndex = this.value;
        
        if (provinceIndex && cityIndex && districtIndex) {
            const provinceName = cityData[provinceIndex].name;
            const cityName = cityData[provinceIndex].children[cityIndex].name;
            const districtName = cityData[provinceIndex].children[cityIndex].children[districtIndex].name;
            
            let adm = cityName;
            if (cityName === '市辖区' || cityName === '县' || cityName === '省直辖县级行政区划' || cityName === provinceName) {
                adm = provinceName;
                if (adm.endsWith('市')) {
                    adm = adm.substring(0, adm.length - 1);
                }
            }
            
            locationStatus.innerHTML = `<span class="text-primary">正在定位: ${provinceName} ${cityName} ${districtName}...</span>`;
            await searchCityAndGetWeather(districtName, adm);
        }
    });

    /**
     * 搜索城市ID并获取天气
     */
    async function searchCityAndGetWeather(keyword, adm) {
        try {
            let searchKeyword = keyword;
            if (keyword.endsWith('区') || keyword.endsWith('县')) {
                 searchKeyword = keyword.substring(0, keyword.length - 1);
            }
            
            const response = await fetch(`/api/city-lookup?keyword=${encodeURIComponent(searchKeyword)}&adm=${encodeURIComponent(adm)}`);
            const data = await response.json();
            
            if (data.success && data.cities.length > 0) {
                const city = data.cities[0];
                selectedCityId = city.id;
                locationStatus.innerHTML = `<span class="text-success">已定位: ${city.name}</span>`;
                getWeather(selectedCityId);
            } else {
                selectedCityId = null;
                locationStatus.innerHTML = '<span class="text-danger">未找到该地区天气信息</span>';
                weatherInfo.innerHTML = '<small class="text-muted">暂无天气数据</small>';
            }
        } catch (error) {
            console.error('搜索城市失败:', error);
            locationStatus.innerHTML = '<span class="text-danger">定位服务暂时不可用</span>';
        }
    }

    /**
     * 更新时间显示
     */
    function updateTime() {
        const now = new Date();
        const options = { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit',
            hour12: false 
        };
        timeDisplay.textContent = now.toLocaleTimeString('zh-CN', options);
    }
    
    loadCityData();
    setInterval(updateTime, 1000);
    updateTime();

    /**
     * 获取天气信息
     */
    async function getWeather(locationId) {
        weatherInfo.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 获取天气中...';
        try {
            const response = await fetch(`/api/weather?location_id=${locationId}`);
            const data = await response.json();
            if (data.success) {
                renderWeather(data.weather);
            } else {
                weatherInfo.innerHTML = '<span class="text-danger">获取天气失败</span>';
            }
        } catch (error) {
            console.error('获取天气错误:', error);
            weatherInfo.innerHTML = '<span class="text-danger">网络错误</span>';
        }
    }

    /**
     * 渲染天气信息
     */
    function renderWeather(weather) {
        const iconMap = {
            '100': '☀️', '101': '☁️', '102': '☁️', '103': '⛅', '104': '☁️',
            '300': '🌧️', '301': '🌧️', '305': '🌧️', '306': '🌧️', '307': '🌧️',
            '400': '🌨️', '401': '🌨️', '402': '🌨️', '403': '🌨️',
            '500': '🌫️', '501': '🌫️', '502': '🌫️'
        };
        const icon = iconMap[weather.icon] || '🌡️';
        weatherInfo.innerHTML = `
            <span class="fs-4 me-2">${icon}</span>
            <div>
                <strong>${weather.text} ${weather.temp}°C</strong><br>
                <small class="text-muted">体感 ${weather.feels_like}°C | 湿度 ${weather.humidity}%</small>
            </div>
        `;
    }

    /**
     * 图片预览功能
     */
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                previewContainer.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });

    /**
     * 表单提交处理 - 关键修改点
     */
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = imageInput.files[0];
        if (!file) {
            alert('请选择照片');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        if (selectedCityId) {
            formData.append('location_id', selectedCityId);
        }

        uploadBtn.disabled = true;
        uploadSpinner.classList.remove('d-none');
        uploadBtnText.textContent = '分析中...';

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // 保存图片URL
                currentPersonImageUrl = data.file_url;
                
                // 显示分析结果 (保留原有逻辑)
                displayAnalysisResult(data.analysis);
                analysisResult.style.display = 'block';
                
                // --- 新增逻辑：处理自动上传的模特 OSS URL ---
                if (data.oss_url) {
                    modelOssUrlInput.value = data.oss_url;
                    currentModelPreview.src = data.file_url; // 使用本地预览更快
                    virtualTryOnSection.style.display = 'block'; // 显示试穿区域
                    checkTryOnReady(); // 检查是否就绪
                } else {
                    console.warn("未获取到 OSS URL，无法进行自动试穿");
                }
                
                // 隐藏旧的OSS工具
                const oldTool = document.getElementById('oldOssTool');
                if (oldTool) oldTool.style.display = 'none';

            } else {
                alert('上传失败: ' + data.error);
            }
        } catch (error) {
            alert('上传失败: ' + error.message);
        } finally {
            uploadBtn.disabled = false;
            uploadSpinner.classList.add('d-none');
            uploadBtnText.textContent = '上传并分析';
        }
    });

    /**
     * 显示分析结果
     */
    function displayAnalysisResult(analysis) {
        let html = '';
        if (analysis.clothing_items && analysis.clothing_items.length > 0) {
            html += '<h6 class="mb-3">识别到的衣物</h6><ul class="list-unstyled">';
            analysis.clothing_items.forEach(item => {
                html += `<li class="mb-2"><strong>${item.type}</strong> - ${item.style}<br><small>颜色: ${item.color} | 材质: ${item.material}</small></li>`;
            });
            html += '</ul>';
        }
        if (analysis.body_features) {
            html += '<h6 class="mb-3">人物特征</h6><div class="row">';
            for (const [key, value] of Object.entries(analysis.body_features)) {
                html += `<div class="col-md-6 mb-2"><strong>${key}:</strong> ${value}</div>`;
            }
            html += '</div>';
        }
        if (analysis.overall_style) {
            html += `<h6 class="mt-3 mb-2">整体风格: ${analysis.overall_style}</h6>`;
        }
        if (analysis.recommendation && Object.keys(analysis.recommendation).length > 0) {
            html += '<hr class="my-4"><h5 class="text-primary mb-3">🌤️ 智能穿搭推荐</h5>';
            const rec = analysis.recommendation;
            if (rec.outfit_suggestion) {
                html += `<div class="alert alert-success mb-3"><strong>✨ 推荐搭配：</strong><br>${rec.outfit_suggestion}</div>`;
            }
            html += '<div class="row">';
            if (rec.weather_advice) html += `<div class="col-md-4 mb-3"><div class="card h-100 border-info"><div class="card-header bg-info text-white">天气建议</div><div class="card-body"><p class="card-text small">${rec.weather_advice}</p></div></div></div>`;
            if (rec.style_advice) html += `<div class="col-md-4 mb-3"><div class="card h-100 border-warning"><div class="card-header bg-warning text-dark">风格建议</div><div class="card-body"><p class="card-text small">${rec.style_advice}</p></div></div></div>`;
            if (rec.color_advice) html += `<div class="col-md-4 mb-3"><div class="card h-100 border-danger"><div class="card-header bg-danger text-white">色彩建议</div><div class="card-body"><p class="card-text small">${rec.color_advice}</p></div></div></div>`;
            html += '</div>';
        }
        analysisContent.innerHTML = html;
    }

    // --- 虚拟试穿逻辑 ---

    // 监听模式切换
    modeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentMode = this.value;
            updateTryOnUI(currentMode);
            checkTryOnReady();
        });
    });

    function updateTryOnUI(mode) {
        const topContainer = document.getElementById('topUploadContainer');
        const bottomContainer = document.getElementById('bottomUploadContainer');
        
        if (mode === 'top') {
            topContainer.style.display = 'block';
            bottomContainer.style.display = 'none';
        } else if (mode === 'bottom') {
            topContainer.style.display = 'none';
            bottomContainer.style.display = 'block';
        } else if (mode === 'full') {
            topContainer.style.display = 'block';
            bottomContainer.style.display = 'block';
        }
    }
    
    // 初始化试穿UI
    updateTryOnUI('top');

    // 自动上传衣物
    topGarmentInput.addEventListener('change', (e) => handleGarmentUpload(e.target.files[0], 'top'));
    bottomGarmentInput.addEventListener('change', (e) => handleGarmentUpload(e.target.files[0], 'bottom'));

    async function handleGarmentUpload(file, type) {
        if (!file) return;
        
        const statusEl = type === 'top' ? topGarmentStatus : bottomGarmentStatus;
        const urlInput = type === 'top' ? topOssUrlInput : bottomOssUrlInput;
        
        statusEl.style.display = 'block';
        statusEl.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 上传中...';
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const res = await fetch('/api/upload-garment', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            
            if (data.success && data.oss_url) {
                urlInput.value = data.oss_url;
                statusEl.innerHTML = `<span class="text-success"><i class="fa fa-check"></i> 上传成功</span>`;
                checkTryOnReady();
            } else {
                throw new Error(data.error || '上传失败');
            }
        } catch (e) {
            console.error(e);
            statusEl.innerHTML = `<span class="text-danger">上传失败: ${e.message}</span>`;
            urlInput.value = ''; // 清空无效值
        }
    }

    function checkTryOnReady() {
        const hasModel = !!modelOssUrlInput.value;
        const hasTop = !!topOssUrlInput.value;
        const hasBottom = !!bottomOssUrlInput.value;
        
        let ready = false;
        
        if (currentMode === 'top') ready = hasModel && hasTop;
        else if (currentMode === 'bottom') ready = hasModel && hasBottom;
        else if (currentMode === 'full') ready = hasModel && hasTop && hasBottom;
        
        startAutoTryOnBtn.disabled = !ready;
    }

    startAutoTryOnBtn.addEventListener('click', async function() {
        startAutoTryOnBtn.disabled = true;
        const tryonResult = document.getElementById('tryonResult');
        const tryonStatus = document.getElementById('tryonStatus');
        const tryonImageContainer = document.getElementById('tryonImageContainer');
        
        tryonResult.style.display = 'block';
        tryonStatus.style.display = 'block';
        tryonStatus.className = 'alert alert-info';
        tryonStatus.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 正在提交试穿任务...';
        tryonImageContainer.style.display = 'none';
        
        tryonResult.scrollIntoView({ behavior: 'smooth' });

        try {
            const payload = {
                person_image_url: modelOssUrlInput.value,
                clothing_type: currentMode
            };
            
            if (currentMode === 'top' || currentMode === 'full') {
                payload.top_garment_url = topOssUrlInput.value;
            }
            if (currentMode === 'bottom' || currentMode === 'full') {
                payload.bottom_garment_url = bottomOssUrlInput.value;
            }

            const res = await fetch('/api/try-on', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (data.success) {
                tryonStatus.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 任务已提交，正在生成 (预计15-30秒)...';
                pollTryOnStatus(data.task_id);
            } else {
                throw new Error(data.error);
            }
        } catch (e) {
            console.error(e);
            tryonStatus.className = 'alert alert-danger';
            tryonStatus.textContent = '提交失败: ' + e.message;
            startAutoTryOnBtn.disabled = false;
        }
    });

    /**
     * 轮询试穿任务状态
     */
    async function pollTryOnStatus(taskId) {
        const tryonStatus = document.getElementById('tryonStatus');
        const tryonImageContainer = document.getElementById('tryonImageContainer');
        const tryonImage = document.getElementById('tryonImage');
        
        let attempts = 0;
        const maxAttempts = 60; 
        
        const poll = async () => {
            if (attempts >= maxAttempts) {
                tryonStatus.className = 'alert alert-warning';
                tryonStatus.textContent = '生成超时，请稍后重试';
                startAutoTryOnBtn.disabled = false;
                return;
            }
            attempts++;
            
            try {
                const response = await fetch(`/api/try-on/status/${taskId}`);
                const data = await response.json();
                
                if (data.success) {
                    if (data.status === 'SUCCEEDED') {
                        tryonStatus.style.display = 'none';
                        tryonImageContainer.style.display = 'block';
                        tryonImage.src = data.result_url;
                        startAutoTryOnBtn.disabled = false;
                    } else if (data.status === 'FAILED') {
                        tryonStatus.className = 'alert alert-danger';
                        tryonStatus.textContent = '试穿失败: ' + (data.error || '未知错误');
                        startAutoTryOnBtn.disabled = false;
                    } else {
                        setTimeout(poll, 2000);
                    }
                } else {
                    tryonStatus.className = 'alert alert-danger';
                    tryonStatus.textContent = '查询状态失败: ' + data.error;
                }
            } catch (error) {
                console.error('轮询失败:', error);
                setTimeout(poll, 2000);
            }
        };
        poll();
    }
});
