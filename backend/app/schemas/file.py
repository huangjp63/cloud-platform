from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileCreate(BaseModel):
    name: str
    md5: str
    size: int
    file_type: Optional[str] = None
    storage_path: str
    folder_id: int = 0


class FileResponse(BaseModel):
    id: int
    name: str
    size: int
    file_type: Optional[str]
    create_time: datetime
    
    class Config:
        from_attributes = True
