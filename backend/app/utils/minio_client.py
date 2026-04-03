from minio import Minio
from app.config import settings
import os

class MinioClient:
    def __init__(self):
        # 优先使用OBS配置（如果有）
        self.endpoint = os.getenv("OBS_ENDPOINT")
        self.access_key = os.getenv("OBS_ACCESS_KEY")
        self.secret_key = os.getenv("OBS_SECRET_KEY")
        self.bucket_name = os.getenv("OBS_BUCKET_NAME")

        
        self.client = Minio(
             f"{self.bucket_name}.{self.endpoint}",  # 虚拟主机风格：桶名.端点
             access_key=self.access_key,
             secret_key=self.secret_key,
             secure=True,  # 必须用 HTTPS
             region="cn-south-1"  # 你的 OBS 区域
         )
        
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
    
    def upload_file(self, object_name: str, file_data, length: int, content_type: str = "application/octet-stream"):
        self.client.put_object(
            self.bucket_name,
            object_name,
            file_data,
            length,
            content_type=content_type
        )
    
    def download_file(self, object_name: str):
        return self.client.get_object(self.bucket_name, object_name)
    
    def delete_file(self, object_name: str):
        self.client.remove_object(self.bucket_name, object_name)
    
    def get_file_url(self, object_name: str, expires: int = 3600):
        from datetime import timedelta
        # 生成预签名URL
        url = self.client.presigned_get_object(
            self.bucket_name,
            object_name,
            expires=timedelta(seconds=expires)
        )
        return url


minio_client = MinioClient()
