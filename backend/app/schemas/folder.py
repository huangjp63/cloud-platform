from pydantic import BaseModel
from typing import Optional


class FolderCreate(BaseModel):
    name: str
    parent_id: int = 0


class FolderResponse(BaseModel):
    id: int
    name: str
    parent_id: int
    
    class Config:
        from_attributes = True
