from pydantic import BaseModel
from datetime import datetime


class RecycleItemResponse(BaseModel):
    id: int
    item_type: str
    name: str
    size: int
    delete_time: datetime
    
    class Config:
        from_attributes = True
