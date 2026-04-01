from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    md5 = Column(String(32), nullable=False, index=True)
    size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=True)
    storage_path = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), default=0)
    download_count = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now, nullable=False)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_deleted = Column(Integer, default=0)
