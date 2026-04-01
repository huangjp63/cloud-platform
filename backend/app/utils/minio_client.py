from minio import Minio
from app.config import settings


class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
    
    def upload_file(self, object_name: str, file_data, length: int, content_type: str = "application/octet-stream"):
        self.client.put_object(
            self.bucket,
            object_name,
            file_data,
            length,
            content_type=content_type
        )
    
    def download_file(self, object_name: str):
        return self.client.get_object(self.bucket, object_name)
    
    def delete_file(self, object_name: str):
        self.client.remove_object(self.bucket, object_name)
    
    def get_file_url(self, object_name: str, expires: int = 3600):
        from datetime import timedelta
        return self.client.presigned_get_object(
            self.bucket,
            object_name,
            expires=timedelta(seconds=expires)
        )


minio_client = MinioClient()
