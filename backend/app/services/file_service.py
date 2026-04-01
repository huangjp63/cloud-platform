from sqlalchemy.orm import Session
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from app.models.file import File
from app.utils.minio_client import minio_client
from app.utils.redis_client import redis_client
import io


class FileService:
    def check_file_md5(self, db: Session, md5: str) -> bool:
        return db.query(File).filter(File.md5 == md5, File.is_deleted == 0).first() is not None
    
    def check_file_owner(self, db: Session, file_id: int, user_id: int) -> bool:
        file = db.query(File).filter(File.id == file_id).first()
        return file and file.user_id == user_id
    
    async def upload_single_file(self, db: Session, file: UploadFile, parent_id: int, user_id: int):
        pass
    
    def get_uploaded_chunks(self, db: Session, md5: str, user_id: int) -> list:
        chunks = redis_client.get(f"chunks:{user_id}:{md5}")
        return chunks if chunks else []
    
    async def upload_chunk_file(self, db: Session, md5: str, index: int, total: int, chunk: UploadFile, user_id: int):
        pass
    
    def merge_chunks(self, db: Session, md5: str, filename: str, total: int, parent_id: int, user_id: int):
        pass
    
    def download_file(self, db: Session, file_id: int):
        pass
    
    def download_batch_files(self, db: Session, file_ids: list, user_id: int, role: str):
        pass
    
    def delete_file(self, db: Session, file_id: int, user_id: int):
        file = db.query(File).filter(File.id == file_id).first()
        if file:
            file.is_deleted = 1
            db.commit()
    
    def rename_file(self, db: Session, file_id: int, name: str) -> File:
        file = db.query(File).filter(File.id == file_id).first()
        if file:
            file.name = name
            db.commit()
            db.refresh(file)
        return file
    
    def preview_file(self, db: Session, file_id: int):
        pass
