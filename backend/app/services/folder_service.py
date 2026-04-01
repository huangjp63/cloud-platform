from sqlalchemy.orm import Session
from app.models.folder import Folder


class FolderService:
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
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if folder:
            folder.is_deleted = 1
            db.commit()
    
    def rename_folder(self, db: Session, folder_id: int, name: str) -> Folder:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if folder:
            folder.name = name
            db.commit()
            db.refresh(folder)
        return folder
