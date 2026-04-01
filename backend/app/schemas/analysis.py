from pydantic import BaseModel
from typing import Optional, Dict, Any


class AnalysisData(BaseModel):
    result_type: str
    data: Dict[str, Any]
