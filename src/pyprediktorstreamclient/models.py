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
    payload: List[VQTPayload]
    

test = {
    "messagetype":"vqt",
    "version":2,
    "payload":
    [
        {
            "k":"tag1",
            "v":1.0
        },
        {
            "k":"tag1",
            "v":0.9,
            "t":"2022-09-25T20:00:00.000Z"
        },
        {
            "k":"tag1",
            "v":0.8,
            "q":192,
            "t":"2022-09-25T19:00:00.000Z"
        }
    ]
}