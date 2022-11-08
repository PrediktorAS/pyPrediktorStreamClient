from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class VQT2Payload(BaseModel):
    k: str
    v: float
    q: Optional[int]
    t: Optional[datetime]

class VQT2(BaseModel):
    messagetype: str
    version: int
    payload: List[VQT2Payload]
