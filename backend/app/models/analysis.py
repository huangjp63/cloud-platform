from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text
from datetime import datetime
from app.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    result_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    data = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.now, nullable=False)
