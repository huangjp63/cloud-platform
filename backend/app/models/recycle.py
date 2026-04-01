from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class RecycleItem(Base):
    __tablename__ = "recycle_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_type = Column(String(20), nullable=False)
    item_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    size = Column(BigInteger, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_path = Column(String(500), nullable=True)
    delete_time = Column(DateTime, default=datetime.now, nullable=False)
