from sqlalchemy.orm import Session
from app.models.recycle import RecycleItem
from datetime import datetime, timedelta
from app.config import settings


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
            db.delete(item)
            db.commit()
    
    def delete_permanently(self, db: Session, item_id: int):
        item = db.query(RecycleItem).filter(RecycleItem.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
    
    def clean_expired_items(self, db: Session) -> int:
        expire_date = datetime.now() - timedelta(days=settings.RECYCLE_EXPIRE_DAYS)
        items = db.query(RecycleItem).filter(RecycleItem.delete_time < expire_date).all()
        count = len(items)
        for item in items:
            db.delete(item)
        db.commit()
        return count
