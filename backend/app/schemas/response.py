from pydantic import BaseModel
from typing import Optional, Any


class APIResponse(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None
