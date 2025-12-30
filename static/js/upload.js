/**
 * 上传页面JavaScript
 * 处理图片上传、预览和分析结果展示
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadSpinner = document.getElementById('uploadSpinner');
    const uploadBtnText = document.getElementById('uploadBtnText');
    const analysisResult = document.getElementById('analysisResult');
    const analysisContent = document.getElementById('analysisContent');

    /**
     * 图片预览功能
     * 当用户选择图片时，实时显示预览
     */
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // 创建FileReader对象，用于读取文件内容
            const reader = new FileReader();
            
            // 读取文件完成后的回调
            reader.onload = function(e) {
                // 设置预览图片的src属性
                imagePreview.src = e.target.result;
                // 显示预览容器
                previewContainer.style.display = 'block';
            };
            
            // 以DataURL格式读取文件
            reader.readAsDataURL(file);
        }
    });

    /**
     * 表单提交处理
     * 处理图片上传和分析请求
     */
    uploadForm.addEventListener('submit', async function(e) {
        // 阻止表单默认提交行为
        e.preventDefault();
        
        // 获取上传的文件
        const file = imageInput.files[0];
        
        // 验证文件是否存在
        if (!file) {
            alert('请选择照片');
            return;
        }

        // 创建FormData对象，用于发送文件数据
        const formData = new FormData();
        formData.append('file', file);

        // 显示加载状态
        uploadBtn.disabled = true;
        uploadSpinner.classList.remove('d-none');
        uploadBtnText.textContent = '分析中...';

        try {
            // 发送POST请求到上传API
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            // 解析响应数据
            const data = await response.json();

            // 检查响应是否成功
            if (data.success) {
                // 显示分析结果
                displayAnalysisResult(data.analysis);
                analysisResult.style.display = 'block';
            } else {
                // 显示错误信息
                alert('上传失败: ' + data.error);
            }
        } catch (error) {
            // 捕获网络错误
            alert('上传失败: ' + error.message);
        } finally {
            // 恢复按钮状态
            uploadBtn.disabled = false;
            uploadSpinner.classList.add('d-none');
            uploadBtnText.textContent = '上传并分析';
        }
    });

    /**
     * 显示分析结果
     * 将API返回的分析结果渲染到页面上
     * @param {Object} analysis - 分析结果对象
     */
    function displayAnalysisResult(analysis) {
        let html = '';

        // 显示识别到的衣物
        if (analysis.clothing_items && analysis.clothing_items.length > 0) {
            html += '<h6 class="mb-3">识别到的衣物</h6>';
            html += '<ul class="list-unstyled">';
            
            // 遍历衣物数组
            analysis.clothing_items.forEach(item => {
                html += `
                    <li class="mb-2">
                        <strong>${item.type}</strong> - ${item.style}<br>
                        <small>颜色: ${item.color} | 材质: ${item.material}</small>
                    </li>
                `;
            });
            
            html += '</ul>';
        }

        // 显示人物特征
        if (analysis.body_features) {
            html += '<h6 class="mb-3">人物特征</h6>';
            html += '<div class="row">';
            
            // 遍历人物特征对象
            for (const [key, value] of Object.entries(analysis.body_features)) {
                html += `
                    <div class="col-md-6 mb-2">
                        <strong>${key}:</strong> ${value}
                    </div>
                `;
            }
            
            html += '</div>';
        }

        // 显示整体风格
        if (analysis.overall_style) {
            html += `<h6 class="mt-3 mb-2">整体风格: ${analysis.overall_style}</h6>`;
        }

        // 将生成的HTML插入到分析结果容器中
        analysisContent.innerHTML = html;
    }
});
