import os
import dashscope
from dashscope import ImageSynthesis
from http import HTTPStatus
import time
import logging
import requests
from pathlib import Path
from flask import current_app
from urllib.parse import unquote
import mimetypes
import oss2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VirtualTryonService:
    def __init__(self):
        self.api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not self.api_key:
            logger.warning("DASHSCOPE_API_KEY is not set. Virtual Try-on will fail.")
        else:
            dashscope.api_key = self.api_key
        
        # OSS Config
        self.oss_access_key_id = os.environ.get('ALIYUN_OSS_ACCESS_KEY_ID')
        self.oss_access_key_secret = os.environ.get('ALIYUN_OSS_ACCESS_KEY_SECRET')
        self.oss_bucket_name = os.environ.get('ALIYUN_OSS_BUCKET_NAME')
        self.oss_endpoint = os.environ.get('ALIYUN_OSS_ENDPOINT')

    def _upload_file_to_oss(self, file_path):
        """将文件上传到阿里云OSS"""
        try:
            print(f"DEBUG: Starting OSS upload for {file_path}")
            if not os.path.exists(file_path):
                logger.error(f"File not found for upload: {file_path}")
                print(f"DEBUG: File not found: {file_path}")
                return None
            
            if not all([self.oss_access_key_id, self.oss_access_key_secret, self.oss_bucket_name, self.oss_endpoint]):
                logger.error("OSS credentials not fully configured.")
                print("DEBUG: OSS credentials missing")
                return None

            # Initialize OSS Bucket
            endpoint = self.oss_endpoint
            if not endpoint.startswith('http'):
                endpoint = f"https://{endpoint}"
            
            print(f"DEBUG: OSS Endpoint: {endpoint}, Bucket: {self.oss_bucket_name}")
            
            auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
            bucket = oss2.Bucket(auth, endpoint, self.oss_bucket_name)

            file_name = Path(file_path).name
            # Use a 'temp/' prefix to keep bucket organized
            key = f"temp/{int(time.time())}_{file_name}"
            
            # Determine Content-Type
            content_type, _ = mimetypes.guess_type(file_path)
            headers = {}
            if content_type:
                headers['Content-Type'] = content_type
                logger.info(f"Detected Content-Type: {content_type}")
            
            logger.info(f"Uploading {file_path} to OSS bucket {self.oss_bucket_name} with key {key}")
            print(f"DEBUG: Uploading to key {key} with headers {headers}")
            
            # Upload with headers
            result = bucket.put_object_from_file(key, file_path, headers=headers)
            print(f"DEBUG: Upload finished. Status: {result.status}")
            
            if result.status != 200:
                print(f"DEBUG: Upload failed with status {result.status}")
                return None
            
            # Construct public URL
            # Standard OSS URL format: https://bucket-name.endpoint/key
            # Note: Since the bucket is now Public Read, we can use the direct URL without signing.
            # This is simpler and avoids any URL encoding/decoding issues with DashScope.
            
            # Remove protocol from endpoint if present to ensure clean construction
            clean_endpoint = self.oss_endpoint.replace("http://", "").replace("https://", "")
            oss_url = f"https://{self.oss_bucket_name}.{clean_endpoint}/{key}"
            
            # 兼容代码：如果用户改回私有 Bucket，这里可以取消注释恢复签名逻辑
            # oss_url = bucket.sign_url('GET', key, 172800)
            # if '%' in oss_url: ...
            
            logger.info(f"File uploaded successfully: {oss_url}")
            print(f"DEBUG: OSS URL generated: {oss_url}")
            return oss_url
        except Exception as e:
            logger.error(f"Error uploading file to OSS: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            print(f"DEBUG: Exception in _upload_file_to_oss: {str(e)}")
            traceback.print_exc()
            return None

    def _resolve_local_url(self, url):
        """
        Resolve a URL to a local file path if it's a local URL.
        Returns the OSS URL if uploaded, or the original URL if not local/upload failed.
        """
        if not url:
            return url
            
        logger.info(f"Resolving URL: {url}")
        print(f"DEBUG: Resolving URL: {url}")
        
        # Check if it's a local URL (e.g., /uploads/xxx or http://localhost...)
        local_path = None
        
        try:
            # 简化逻辑：只要包含 /uploads/，就尝试去查找本地文件
            if '/uploads/' in url:
                # Extract filename from URL
                filename = unquote(url.split('/uploads/')[-1])
                # Remove query parameters if any
                if '?' in filename:
                    filename = filename.split('?')[0]
                
                candidate_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                print(f"DEBUG: Candidate local path: {candidate_path}")
                
                if os.path.exists(candidate_path):
                    local_path = candidate_path
            
            if local_path:
                logger.info(f"Identified local path: {local_path}")
                print(f"DEBUG: Identified local file: {local_path}")
                
                # Check if we should upload
                print(f"DEBUG: Uploading local file to OSS...")
                oss_url = self._upload_file_to_oss(local_path)
                
                if oss_url:
                    print(f"DEBUG: Resolved to OSS URL: {oss_url}")
                    return oss_url
                else:
                    logger.warning("Failed to upload local file, using original URL (likely will fail)")
                    print("DEBUG: Upload failed, returning original URL")
                    return url
            else:
                # Not a local file or file not found
                # If it's a remote URL (http/https), we assume it's accessible or already on OSS
                return url
                    
        except Exception as e:
             logger.error(f"Error resolving local url: {str(e)}")
             print(f"DEBUG: Error resolving local url: {str(e)}")
             import traceback
             traceback.print_exc()
        
        return url

    def generate_tryon(self, person_image_url, clothing_image_url=None, clothing_type='top', top_garment_url=None, bottom_garment_url=None):
        """
        Submit a virtual try-on task to Aliyun OutfitAnyone.
        """
        try:
            # Check if API key is set
            if not self.api_key:
                return {"success": False, "error": "API Key missing"}

            logger.info(f"Submitting OutfitAnyone task. Type: {clothing_type}")
            
            # Resolve local URLs to OSS URLs
            person_image_url = self._resolve_local_url(person_image_url)
            
            if clothing_image_url:
                clothing_image_url = self._resolve_local_url(clothing_image_url)
            
            if top_garment_url:
                top_garment_url = self._resolve_local_url(top_garment_url)
                
            if bottom_garment_url:
                bottom_garment_url = self._resolve_local_url(bottom_garment_url)

            # 构造参数
            # 使用原生 HTTP 请求替代 SDK，以确保 Header 正确传递
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-OssResourceResolve": "enable",
                "X-DashScope-Async": "enable"
            }
            
            payload = {
                "model": "aitryon-plus",
                "input": {
                    "person_image_url": person_image_url
                },
                "parameters": {
                    "resolution": -1,
                    "restore_face": True,
                    "prompt": "virtual try on"
                }
            }
            
            if clothing_type == 'top':
                payload["input"]["top_garment_url"] = clothing_image_url
            elif clothing_type == 'bottom':
                payload["input"]["bottom_garment_url"] = clothing_image_url
            elif clothing_type == 'full':
                payload["input"]["top_garment_url"] = top_garment_url
                payload["input"]["bottom_garment_url"] = bottom_garment_url
            
            logger.info(f"Sending request to DashScope API: {url}")
            # print(f"DEBUG: Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == HTTPStatus.OK:
                resp_data = response.json()
                if 'output' in resp_data and 'task_id' in resp_data['output']:
                    task_id = resp_data['output']['task_id']
                    logger.info(f"Task submitted successfully. Task ID: {task_id}")
                    return {
                        "success": True, 
                        "task_id": task_id,
                        "status": "PENDING"
                    }
                else:
                    logger.error(f"Unexpected response format: {resp_data}")
                    return {"success": False, "error": "Unknown response format from API"}
            else:
                logger.error(f"Failed to submit task: {response.status_code}, {response.text}")
                return {
                    "success": False, 
                    "error": f"{response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Exception in generate_tryon: {str(e)}")
            return {"success": False, "error": str(e)}

    def check_task_status(self, task_id):
        """
        Check the status of a submitted task.
        """
        if task_id == "direct_result":
             return {"success": True, "status": "SUCCEEDED"}

        try:
            url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == HTTPStatus.OK:
                resp_data = response.json()
                task_status = resp_data.get('output', {}).get('task_status', 'UNKNOWN')
                
                logger.info(f"Task status check: {task_status}")
                result = {
                    "success": True,
                    "status": task_status,
                }
                
                if task_status == 'SUCCEEDED':
                    output = resp_data.get('output', {})
                    # 优先获取 image_url (官方文档标准字段)
                    # 其次尝试 result_image_url (部分旧模型字段)
                    # 最后尝试 results 列表 (通用格式)
                    result["result_url"] = (
                        output.get('image_url') or 
                        output.get('result_image_url') or 
                        (output.get('results', [{}])[0].get('url'))
                    )
                    logger.info(f"Task succeeded. Result URL: {result['result_url']}")
                elif task_status == 'FAILED':
                    result["error"] = resp_data.get('output', {}).get('message', 'Unknown error')
                    
                return result
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Exception in check_task_status: {str(e)}")
            return {"success": False, "error": str(e)}
