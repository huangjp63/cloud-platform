from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Cloud-Platform"
    DEBUG: bool = True
    
    DATABASE_URL: str = "mysql+pymysql://root:!Hjp20040915@192.168.0.246:3306/cloud_platform"
    REDIS_URL: str = "!Hjp20040915@redis-8a19618b-0810-40c4-89a8-76721315900f.cn-south-1.dcs.myhuaweicloud.com:6379/0"
    
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "cloud-files"
    MINIO_SECURE: bool = False
    
    # 华为云OBS配置
    OBS_ENDPOINT: str = "obs.cn-south-1.myhuaweicloud.com"
    OBS_ACCESS_KEY: str = "HPUAE0B3GURYV1VT2UHP"
    OBS_SECRET_KEY: str = "OBS_SECRET_KEY=y6h1Nif6G94eGLlRIGSS8sYviOipw5f7KZQxxJ6i"
    OBS_BUCKET: str = "cloud-platform"
    OBS_SECURE: bool = True
    
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]
    
    UPLOAD_CHUNK_SIZE: int = 5 * 1024 * 1024
    MAX_FILE_SIZE: int = 10 * 1024 * 1024 * 1024
    
    RECYCLE_EXPIRE_DAYS: int = 30
    
    SPARK_MASTER: str = "local[*]"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
