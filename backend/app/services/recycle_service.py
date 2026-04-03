from sqlalchemy.orm import Session
from app.models.recycle import RecycleItem
from datetime import datetime, timedelta
from app.config import settings
from app.utils.minio_client import minio_client


class RecycleService:
    def get_user_recycle_items(self, db: Session, user_id: int) -> list:
        return db.query(RecycleItem).filter(RecycleItem.user_id == user_id).all()
    
    def get_all_recycle_items(self, db: Session) -> list:
        return db.query(RecycleItem).all()
    
    def check_item_owner(self, db: Session, item_id: int, user_id: int) -> bool:
        item = db.query(RecycleItem).filter(RecycleItem.id == item_id).first()
        return item and item.user_id == user_id
    
    def recover_item(self, db: Session, item_id: int):
        item = db.query(RecycleItem).filter(RecycleItem.id == item_id).first()
        if item:
            # 根据item_type恢复对应的文件或文件夹
            if item.item_type == 'file':
                from app.models.file import File
                file = db.query(File).filter(File.id == item.item_id).first()
                if file:
                    # 恢复文件到根目录
                    file.is_deleted = 0
                    file.folder_id = 0
            elif item.item_type == 'folder':
                from app.models.folder import Folder
                folder = db.query(Folder).filter(Folder.id == item.item_id).first()
                if folder:
                    # 恢复文件夹到根目录
                    folder.is_deleted = 0
                    folder.parent_id = 0
                    folder.level = 1
            
            # 删除回收站记录
            db.delete(item)
            db.commit()
    
    def delete_permanently(self, db: Session, item_id: int):
        """彻底删除文件或文件夹"""
        item = db.query(RecycleItem).filter(RecycleItem.id == item_id).first()
        if item:
            if item.item_type == 'file':
                self._delete_file_permanently(db, item)
            elif item.item_type == 'folder':
                self._delete_folder_permanently(db, item)
            
            # 删除回收站记录
            db.delete(item)
            db.commit()
    
    def _delete_file_permanently(self, db: Session, item: RecycleItem):
        """彻底删除文件"""
        from app.models.file import File
        file = db.query(File).filter(File.id == item.item_id).first()
        if file:
            # 从MinIO中删除文件
            try:
                minio_client.delete_file(file.storage_path)
            except Exception as e:
                print(f"从MinIO删除文件失败: {e}")
            
            # 从数据库中删除文件记录
            db.delete(file)
    
    def _delete_folder_permanently(self, db: Session, item: RecycleItem):
        """彻底删除文件夹（递归删除文件夹内的所有内容）"""
        from app.models.folder import Folder
        from app.models.file import File
        
        folder = db.query(Folder).filter(Folder.id == item.item_id).first()
        if folder:
            # 递归删除子文件夹
            subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()
            for subfolder in subfolders:
                subfolder_item = db.query(RecycleItem).filter(
                    RecycleItem.item_id == subfolder.id,
                    RecycleItem.item_type == 'folder'
                ).first()
                if subfolder_item:
                    self._delete_folder_permanently(db, subfolder_item)
                else:
                    # 如果子文件夹不在回收站中，直接删除
                    self._delete_folder_contents(db, subfolder.id)
                    db.delete(subfolder)
            
            # 删除文件夹内的所有文件
            self._delete_folder_contents(db, folder.id)
            
            # 从数据库中删除文件夹记录
            db.delete(folder)
    
    def _delete_folder_contents(self, db: Session, folder_id: int):
        """删除文件夹内的所有文件"""
        from app.models.file import File
        
        files = db.query(File).filter(File.folder_id == folder_id).all()
        for file in files:
            # 从MinIO中删除文件
            try:
                minio_client.delete_file(file.storage_path)
            except Exception as e:
                print(f"从MinIO删除文件失败: {e}")
            
            # 从数据库中删除文件记录
            db.delete(file)
    
    def clean_expired_items(self, db: Session) -> int:
        """清理过期的回收站项目"""
        expire_date = datetime.now() - timedelta(days=settings.RECYCLE_EXPIRE_DAYS)
        items = db.query(RecycleItem).filter(RecycleItem.delete_time < expire_date).all()
        count = len(items)
        
        for item in items:
            # 彻底删除文件或文件夹
            if item.item_type == 'file':
                self._delete_file_permanently(db, item)
            elif item.item_type == 'folder':
                self._delete_folder_permanently(db, item)
            
            # 删除回收站记录
            db.delete(item)
        
        db.commit()
        return count


recycle_service = RecycleService()
