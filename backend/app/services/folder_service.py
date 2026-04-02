from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.folder import Folder
from app.models.recycle import RecycleItem
from app.models.file import File


class FolderService:
    def calculate_folder_size(self, db: Session, folder_id: int) -> int:
        """计算文件夹大小（递归）"""
        # 计算当前文件夹下的文件大小
        file_size = db.query(func.sum(File.size)).filter(
            File.folder_id == folder_id,
            File.is_deleted == 0
        ).scalar() or 0
        
        # 递归计算子文件夹的大小
        subfolders = db.query(Folder).filter(
            Folder.parent_id == folder_id,
            Folder.is_deleted == 0
        ).all()
        
        for subfolder in subfolders:
            file_size += self.calculate_folder_size(db, subfolder.id)
        
        return file_size
    
    def create_folder(self, db: Session, name: str, parent_id: int, user_id: int) -> Folder:
        level = 1
        if parent_id > 0:
            parent = db.query(Folder).filter(Folder.id == parent_id).first()
            if parent:
                level = parent.level + 1
        
        folder = Folder(
            name=name,
            parent_id=parent_id,
            user_id=user_id,
            level=level
        )
        db.add(folder)
        db.commit()
        db.refresh(folder)
        return folder
    
    def check_folder_owner(self, db: Session, folder_id: int, user_id: int) -> bool:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        return folder and folder.user_id == user_id
    
    def delete_folder(self, db: Session, folder_id: int, user_id: int):
        folder = db.query(Folder).filter(Folder.id == folder_id, Folder.is_deleted == 0).first()
        if not folder:
            return
        
        # 检查权限
        if folder.user_id != user_id:
            return
        
        # 计算文件夹大小
        size = self.calculate_folder_size(db, folder_id)
        
        # 移动到回收站
        recycle_item = RecycleItem(
            item_type="folder",
            item_id=folder.id,
            name=folder.name,
            size=size,
            user_id=user_id,
            original_path=f"folder/{folder.id}"
        )
        db.add(recycle_item)
        
        # 标记文件夹为已删除
        folder.is_deleted = 1
        db.commit()
    
    def rename_folder(self, db: Session, folder_id: int, name: str) -> Folder:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if folder:
            folder.name = name
            db.commit()
            db.refresh(folder)
        return folder
    
    def get_folder_list(self, db: Session, user_id: int, parent_id: int = 0, role: str = "user"):
        """获取文件夹列表"""
        query = db.query(Folder).filter(Folder.is_deleted == 0)
        
        if role != "admin":
            query = query.filter(Folder.user_id == user_id)
        
        if parent_id:
            query = query.filter(Folder.parent_id == parent_id)
        else:
            query = query.filter(Folder.parent_id == 0)
        
        folders = query.order_by(Folder.create_time.desc()).all()
        
        # 计算每个文件夹的大小
        for folder in folders:
            folder.size = self.calculate_folder_size(db, folder.id)
        
        return folders
