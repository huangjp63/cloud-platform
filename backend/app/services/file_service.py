from sqlalchemy.orm import Session
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from app.models.file import File
from app.models.recycle import RecycleItem
from app.utils.minio_client import minio_client
from app.utils.redis_client import redis_client
from app.utils.md5_utils import calculate_md5
from app.utils.file_utils import get_file_extension, format_file_size
from datetime import datetime
import io
import os
import zipfile


class FileService:
    def check_file_md5(self, db: Session, md5: str) -> bool:
        """检查文件 MD5 是否存在（秒传功能）"""
        return db.query(File).filter(File.md5 == md5, File.is_deleted == 0).first() is not None
    
    def get_file_by_md5(self, db: Session, md5: str) -> File:
        """根据 MD5 获取文件信息"""
        return db.query(File).filter(File.md5 == md5, File.is_deleted == 0).first()
    
    def check_file_owner(self, db: Session, file_id: int, user_id: int) -> bool:
        """检查文件是否属于指定用户"""
        file = db.query(File).filter(File.id == file_id, File.is_deleted == 0).first()
        return file and file.user_id == user_id
    
    async def upload_single_file(self, db: Session, file: UploadFile, parent_id: int, user_id: int):
        """上传单个文件"""
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 计算 MD5
        file_md5 = calculate_md5(content)
        
        # 检查是否已存在（秒传）
        existing_file = self.get_file_by_md5(db, file_md5)
        if existing_file:
            # 创建新的文件记录，指向同一个存储文件
            new_file = File(
                name=file.filename,
                md5=file_md5,
                size=file_size,
                file_type=get_file_extension(file.filename),
                storage_path=existing_file.storage_path,
                user_id=user_id,
                folder_id=parent_id
            )
            db.add(new_file)
            db.commit()
            db.refresh(new_file)
            return new_file
        
        # 生成存储路径
        storage_path = f"{user_id}/{datetime.now().strftime('%Y/%m/%d')}/{file_md5}_{file.filename}"
        
        # 上传到 MinIO
        minio_client.upload_file(
            storage_path,
            io.BytesIO(content),
            file_size,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # 创建文件记录
        new_file = File(
            name=file.filename,
            md5=file_md5,
            size=file_size,
            file_type=get_file_extension(file.filename),
            storage_path=storage_path,
            user_id=user_id,
            folder_id=parent_id
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        
        return new_file
    
    def get_uploaded_chunks(self, user_id: int, md5: str) -> list:
        """获取已上传的分片列表"""
        key = f"chunks:{user_id}:{md5}"
        chunks = redis_client.lrange(key, 0, -1)
        return [int(chunk) for chunk in chunks] if chunks else []
    
    async def upload_chunk_file(self, db: Session, md5: str, index: int, total: int, chunk: UploadFile, user_id: int):
        """上传文件分片"""
        # 读取分片内容
        content = await chunk.read()
        
        # 生成临时存储路径
        temp_path = f"temp/{user_id}/{md5}/{index}"
        
        # 上传分片到 MinIO
        minio_client.upload_file(
            temp_path,
            io.BytesIO(content),
            len(content)
        )
        
        # 记录已上传的分片
        key = f"chunks:{user_id}:{md5}"
        redis_client.lpush(key, index)
        redis_client.set(f"{key}:total", total, expire=3600)  # 1小时过期
        
        return {"index": index, "status": "success"}
    
    def merge_chunks(self, db: Session, md5: str, filename: str, total: int, parent_id: int, user_id: int):
        """合并分片文件"""
        # 检查所有分片是否都已上传
        uploaded_chunks = self.get_uploaded_chunks(user_id, md5)
        if len(uploaded_chunks) != total:
            raise Exception(f"分片不完整，已上传 {len(uploaded_chunks)}/{total}")
        
        # 合并分片
        merged_content = io.BytesIO()
        total_size = 0
        
        for i in range(total):
            temp_path = f"temp/{user_id}/{md5}/{i}"
            chunk_data = minio_client.download_file(temp_path)
            chunk_content = chunk_data.read()
            merged_content.write(chunk_content)
            total_size += len(chunk_content)
            
            # 删除临时分片
            minio_client.delete_file(temp_path)
        
        merged_content.seek(0)
        
        # 生成存储路径
        storage_path = f"{user_id}/{datetime.now().strftime('%Y/%m/%d')}/{md5}_{filename}"
        
        # 上传合并后的文件到 MinIO
        minio_client.upload_file(
            storage_path,
            merged_content,
            total_size
        )
        
        # 创建文件记录
        new_file = File(
            name=filename,
            md5=md5,
            size=total_size,
            file_type=get_file_extension(filename),
            storage_path=storage_path,
            user_id=user_id,
            folder_id=parent_id
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        
        # 清理 Redis 缓存
        redis_client.delete(f"chunks:{user_id}:{md5}")
        redis_client.delete(f"chunks:{user_id}:{md5}:total")
        
        return new_file
    
    def download_file(self, db: Session, file_id: int):
        """下载单个文件"""
        file = db.query(File).filter(File.id == file_id, File.is_deleted == 0).first()
        if not file:
            return None
        
        # 增加下载次数
        file.download_count += 1
        db.commit()
        
        # 从 MinIO 下载文件
        file_data = minio_client.download_file(file.storage_path)
        
        return {
            "file": file,
            "data": file_data
        }
    
    def download_batch_files(self, db: Session, file_ids: list, user_id: int, role: str):
        """批量下载文件（打包为 ZIP）"""
        files = []
        for file_id in file_ids:
            if role == "admin":
                file = db.query(File).filter(File.id == file_id, File.is_deleted == 0).first()
            else:
                file = db.query(File).filter(
                    File.id == file_id, 
                    File.user_id == user_id,
                    File.is_deleted == 0
                ).first()
            
            if file:
                files.append(file)
        
        if not files:
            return None
        
        # 创建 ZIP 文件
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                file_data = minio_client.download_file(file.storage_path)
                zip_file.writestr(file.name, file_data.read())
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def delete_file(self, db: Session, file_id: int, user_id: int):
        """删除文件（移动到回收站）"""
        file = db.query(File).filter(File.id == file_id, File.is_deleted == 0).first()
        if not file:
            return None
        
        # 检查权限
        if file.user_id != user_id:
            return None
        
        # 移动到回收站
        recycle_item = RecycleItem(
            item_type="file",
            item_id=file.id,
            name=file.name,
            size=file.size,
            user_id=user_id,
            original_path=file.storage_path
        )
        db.add(recycle_item)
        
        # 标记文件为已删除
        file.is_deleted = 1
        db.commit()
        
        return file
    
    def rename_file(self, db: Session, file_id: int, name: str, user_id: int) -> File:
        """重命名文件"""
        file = db.query(File).filter(File.id == file_id, File.is_deleted == 0).first()
        if not file:
            return None
        
        # 检查权限
        if file.user_id != user_id:
            return None
        
        file.name = name
        db.commit()
        db.refresh(file)
        return file
    
    def preview_file(self, db: Session, file_id: int, user_id: int, role: str):
        """预览文件（获取临时访问 URL）"""
        if role == "admin":
            file = db.query(File).filter(File.id == file_id, File.is_deleted == 0).first()
        else:
            file = db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id,
                File.is_deleted == 0
            ).first()
        
        if not file:
            return None
        
        # 获取临时访问 URL
        url = minio_client.get_file_url(file.storage_path, expires=3600)
        
        return {
            "file": file,
            "url": url
        }
    
    def get_file_list(self, db: Session, user_id: int, folder_id: int = 0, role: str = "user"):
        """获取文件列表"""
        query = db.query(File).filter(File.is_deleted == 0)
        
        if role != "admin":
            query = query.filter(File.user_id == user_id)
        
        if folder_id:
            query = query.filter(File.folder_id == folder_id)
        else:
            query = query.filter(File.folder_id == 0)
        
        files = query.order_by(File.create_time.desc()).all()
        return files
    
    def get_file_statistics(self, db: Session, user_id: int = None):
        """获取文件统计信息"""
        query = db.query(File).filter(File.is_deleted == 0)
        
        if user_id:
            query = query.filter(File.user_id == user_id)
        
        total_files = query.count()
        total_size = db.query(db.func.sum(File.size)).filter(File.is_deleted == 0).scalar() or 0
        
        # 按文件类型统计
        type_stats = db.query(
            File.file_type,
            db.func.count(File.id).label("count"),
            db.func.sum(File.size).label("size")
        ).filter(File.is_deleted == 0).group_by(File.file_type).all()
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "type_statistics": [
                {
                    "type": stat.file_type or "unknown",
                    "count": stat.count,
                    "size": stat.size or 0
                }
                for stat in type_stats
            ]
        }
