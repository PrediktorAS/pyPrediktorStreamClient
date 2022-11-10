import pydantic
from datetime import datetime, timedelta
from typing import List, Optional
import re
import pytz

utc_tz = pytz.timezone('UTC')

class VQT2Payload(pydantic.BaseModel):
    k: str
    v: float | int
    q: Optional[int]
    t: Optional[datetime]

    @pydantic.validator("t")
    @classmethod
    def validating_timestamp(cls, value):
        if value.tzinfo is None:
            raise ValueError("datetime must contain timezone information")
        elif value.tzname() != 'UTC':
            tz = value.tzname().replace('UTC', '').replace(':', '')
            sign, hours, minutes = re.match(r'([+\-]?)(\d{2})(\d{2})', tz).groups()
            sign = -1 if sign == '-' else 1
            utc_offset = sign * timedelta(hours=int(hours), minutes=int(minutes))
            value = value + utc_offset if sign == -1 else value - utc_offset
            return value.replace(tzinfo=utc_tz).isoformat(timespec='milliseconds')
        return value.isoformat(timespec='milliseconds')


class VQT2(pydantic.BaseModel):
    messagetype: str
    version: int
    payload: List[VQT2Payload]

    @pydantic.validator("messagetype")
    @classmethod
    def validating_messagetype(cls, value):
        if value != "vqt":
            raise ValueError("messagetype field should be 'vqt' to write timeseries values")


message = {
    "messagetype": "vqt",
    "version": 2,
    "payload":
        [
            {
                "k": "tag1",
                "v": 0.8,
                "q": 192,
                "t": "2022-09-25T12:00:00.000-04:00"
            }
        ]
}

VQTmessage = VQT2(**message)

