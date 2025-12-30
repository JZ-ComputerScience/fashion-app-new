/**
 * 虚拟试穿页面JavaScript
 * 处理人物照片和服装照片上传，生成虚拟试穿效果
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const personImage = document.getElementById('personImage');
    const clothingImage = document.getElementById('clothingImage');
    const personPreview = document.getElementById('personPreview');
    const clothingPreview = document.getElementById('clothingPreview');
    const personImagePreview = document.getElementById('personImagePreview');
    const clothingImagePreview = document.getElementById('clothingImagePreview');
    const tryonBtn = document.getElementById('tryonBtn');
    const tryonSpinner = document.getElementById('tryonSpinner');
    const tryonBtnText = document.getElementById('tryonBtnText');
    const tryonResult = document.getElementById('tryonResult');
    const tryonResultImage = document.getElementById('tryonResultImage');

    // 存储图片数据
    let personImageData = null;
    let clothingImageData = null;

    /**
     * 人物照片预览功能
     */
    personImage.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                personImagePreview.src = e.target.result;
                personPreview.style.display = 'block';
                personImageData = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    /**
     * 服装照片预览功能
     */
    clothingImage.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                clothingImagePreview.src = e.target.result;
                clothingPreview.style.display = 'block';
                clothingImageData = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    /**
     * 开始虚拟试穿
     */
    tryonBtn.addEventListener('click', async function() {
        // 验证是否已上传两张照片
        if (!personImageData || !clothingImageData) {
            alert('请上传人物照片和服装照片');
            return;
        }

        // 显示加载状态
        tryonBtn.disabled = true;
        tryonSpinner.classList.remove('d-none');
        tryonBtnText.textContent = '生成中...';
        tryonResult.style.display = 'none';

        try {
            // 发送POST请求到虚拟试穿API
            const response = await fetch('/api/virtual-tryon', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    person_image: personImageData,
                    clothing_image: clothingImageData
                })
            });

            // 解析响应数据
            const data = await response.json();

            if (data.success) {
                // 显示试穿结果
                tryonResultImage.src = data.result_image;
                tryonResult.style.display = 'block';
            } else {
                // 显示错误信息
                alert('虚拟试穿失败: ' + data.error);
            }
        } catch (error) {
            // 捕获网络错误
            alert('虚拟试穿失败: ' + error.message);
        } finally {
            // 恢复按钮状态
            tryonBtn.disabled = false;
            tryonSpinner.classList.add('d-none');
            tryonBtnText.textContent = '开始虚拟试穿';
        }
    });
});
