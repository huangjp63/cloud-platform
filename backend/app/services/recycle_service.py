from sqlalchemy.orm import Session
from app.models.recycle import RecycleItem
from datetime import datetime, timedelta
from app.config import settings
from app.utils.minio_client import minio_client


class RecycleService:
    def get_user_recycle_items(self, db: Session, user_id: int) -> list:
        # 获取用户的所有回收站项目
        all_items = db.query(RecycleItem).filter(RecycleItem.user_id == user_id).all()
        
        # 过滤掉那些是被删除文件夹内的内容的项目
        # 只保留顶级项目（直接被删除的项目）
        top_level_items = []
        for item in all_items:
            # 检查是否有父文件夹也在回收站中
            if item.item_type == 'file':
                # 对于文件，检查它的文件夹是否也在回收站中
                from app.models.file import File
                file = db.query(File).filter(File.id == item.item_id).first()
                if file:
                    # 检查文件夹是否在回收站中
                    folder_in_recycle = db.query(RecycleItem).filter(
                        RecycleItem.item_id == file.folder_id,
                        RecycleItem.item_type == 'folder',
                        RecycleItem.user_id == user_id
                    ).first()
                    # 如果文件夹不在回收站中，或者文件的folder_id为0（根目录），则显示该文件
                    if not folder_in_recycle or file.folder_id == 0:
                        top_level_items.append(item)
            else:
                # 对于文件夹，检查它的父文件夹是否也在回收站中
                from app.models.folder import Folder
                folder = db.query(Folder).filter(Folder.id == item.item_id).first()
                if folder:
                    # 检查父文件夹是否在回收站中
                    parent_in_recycle = db.query(RecycleItem).filter(
                        RecycleItem.item_id == folder.parent_id,
                        RecycleItem.item_type == 'folder',
                        RecycleItem.user_id == user_id
                    ).first()
                    # 如果父文件夹不在回收站中，或者文件夹的parent_id为0（根目录），则显示该文件夹
                    if not parent_in_recycle or folder.parent_id == 0:
                        top_level_items.append(item)
        
        return top_level_items
    
    def get_all_recycle_items(self, db: Session) -> list:
        # 获取所有回收站项目
        all_items = db.query(RecycleItem).all()
        
        # 过滤掉那些是被删除文件夹内的内容的项目
        # 只保留顶级项目（直接被删除的项目）
        top_level_items = []
        for item in all_items:
            if item.item_type == 'file':
                # 对于文件，检查它的文件夹是否也在回收站中
                from app.models.file import File
                file = db.query(File).filter(File.id == item.item_id).first()
                if file:
                    # 检查文件夹是否在回收站中
                    folder_in_recycle = db.query(RecycleItem).filter(
                        RecycleItem.item_id == file.folder_id,
                        RecycleItem.item_type == 'folder'
                    ).first()
                    # 如果文件夹不在回收站中，或者文件的folder_id为0（根目录），则显示该文件
                    if not folder_in_recycle or file.folder_id == 0:
                        top_level_items.append(item)
            else:
                # 对于文件夹，检查它的父文件夹是否也在回收站中
                from app.models.folder import Folder
                folder = db.query(Folder).filter(Folder.id == item.item_id).first()
                if folder:
                    # 检查父文件夹是否在回收站中
                    parent_in_recycle = db.query(RecycleItem).filter(
                        RecycleItem.item_id == folder.parent_id,
                        RecycleItem.item_type == 'folder'
                    ).first()
                    # 如果父文件夹不在回收站中，或者文件夹的parent_id为0（根目录），则显示该文件夹
                    if not parent_in_recycle or folder.parent_id == 0:
                        top_level_items.append(item)
        
        return top_level_items
    
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
                    # 恢复文件到原来的文件夹
                    file.is_deleted = 0
            elif item.item_type == 'folder':
                from app.models.folder import Folder
                from app.models.file import File
                folder = db.query(Folder).filter(Folder.id == item.item_id).first()
                if folder:
                    # 恢复文件夹
                    folder.is_deleted = 0
                    folder.parent_id = 0
                    folder.level = 1
                    
                    # 恢复文件夹内的子文件夹
                    subfolders = db.query(Folder).filter(
                        Folder.parent_id == folder.id,
                        Folder.is_deleted == 1
                    ).all()
                    for subfolder in subfolders:
                        # 找到对应的回收站记录
                        subfolder_recycle = db.query(RecycleItem).filter(
                            RecycleItem.item_id == subfolder.id,
                            RecycleItem.item_type == 'folder'
                        ).first()
                        if subfolder_recycle:
                            subfolder.is_deleted = 0
                            db.delete(subfolder_recycle)
                    
                    # 恢复文件夹内的文件
                    files = db.query(File).filter(
                        File.folder_id == folder.id,
                        File.is_deleted == 1
                    ).all()
                    for file in files:
                        # 找到对应的回收站记录
                        file_recycle = db.query(RecycleItem).filter(
                            RecycleItem.item_id == file.id,
                            RecycleItem.item_type == 'file'
                        ).first()
                        if file_recycle:
                            file.is_deleted = 0
                            db.delete(file_recycle)
            
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
            # 检查是否有其他用户的文件记录引用相同的 MD5
            other_files = db.query(File).filter(
                File.md5 == file.md5,
                File.id != file.id,  # 排除当前文件
                File.is_deleted == 0  # 只检查未删除的文件
            ).count()
            
            # 只有当没有其他引用时，才删除 MinIO 中的实际文件
            if other_files == 0:
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
    
    def get_folder_contents(self, db: Session, folder_id: int, user_id: int, role: str) -> dict:
        """获取回收站中文件夹的内容"""
        from app.models.folder import Folder
        from app.models.file import File
        
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return None
        
        if role != "admin" and folder.user_id != user_id:
            return None
        
        files = db.query(File).filter(
            File.folder_id == folder_id,
            File.is_deleted == 1
        ).all()
        
        subfolders = db.query(Folder).filter(
            Folder.parent_id == folder_id,
            Folder.is_deleted == 1
        ).all()
        
        files_dict = [{
            "id": file.id,
            "name": file.name,
            "size": file.size,
            "file_type": file.file_type,
            "type": "file"
        } for file in files]
        
        subfolders_dict = [{
            "id": folder.id,
            "name": folder.name,
            "type": "folder"
        } for folder in subfolders]
        
        return {
            "folder": {
                "id": folder.id,
                "name": folder.name,
                "parent_id": folder.parent_id
            },
            "contents": files_dict + subfolders_dict
        }
    
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

