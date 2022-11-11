import pydantic
from datetime import datetime, timedelta
from typing import List, Optional, ClassVar
import re
import pytz

utc_tz = pytz.timezone('UTC')


def validating_timestamp(value: datetime):
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


class VQT2Payload(pydantic.BaseModel):
    k: str
    v: float
    q: Optional[int]
    t: Optional[datetime]

    check_timestamp = pydantic.validator("t", allow_reuse=True)(validating_timestamp)


class VQT2(pydantic.BaseModel):
    messagetype: str
    version: int
    payload: List[VQT2Payload]

    @pydantic.validator("messagetype")
    @classmethod
    def validating_messagetype(cls, value) -> str:
        if value != "vqt":
            raise ValueError("messagetype field should be 'vqt' to write timeseries values")
        return value


class HistoricalVQT(pydantic.BaseModel):
    v: float
    q: int
    t: datetime

    check_timestamp = pydantic.validator("t", allow_reuse=True)(validating_timestamp)


class HistoricalPayload(pydantic.BaseModel):
    k: str
    v: List[HistoricalVQT]
    overwrite: pydantic.StrictBool

    @pydantic.validator("v")
    @classmethod
    def checking_timestamp_order(cls, values) -> List:
        if len(values) > 1:
            for i in range(1, len(values)):
                if values[i].t < values[i - 1].t:
                    raise ValueError("VQTs must be arranged with timestamps in the 'oldest to newest' order")
                return values
        return values


class Historical(pydantic.BaseModel):
    messagetype: str
    version: int
    payload: List[HistoricalPayload]

    @pydantic.validator("messagetype")
    @classmethod
    def validating_messagetype(cls, value) -> str:
        if value != "historical":
            raise ValueError("messagetype field should be 'historical' to write historical values")
        return value


class EventPayload(pydantic.BaseModel):
    type: str
    source: str
    severity: int
    time: datetime
    state: str
    currentvalue: float
    message: Optional[str]
    activetime: Optional[datetime]
    lastquality: Optional[int]


    check_time = pydantic.validator("time", allow_reuse=True)(validating_timestamp)
    check_activetime = pydantic.validator("activetime", allow_reuse=True)(validating_timestamp)

    @pydantic.validator("state")
    @classmethod
    def validating_source(cls, value) -> str:
        states= [None, 'Enabled', 'Active', 'Acked', 'AckRequired', 'Confirmed',
                                       'Suppressed', 'Shelved', 'Subsates', 'Low', 'High', 'HighHigh', 'LowLow']
        states_entered= value.replace(' ','').split(',')
        for state in states_entered:
            if state not in states:
                raise ValueError('Invalid event state entered')
        if ' ' in value:
            value = value.replace(' ', '')
            return value
        return value


class Event(pydantic.BaseModel):
    messagetype: str
    version: int
    payload: List[EventPayload]

    @pydantic.validator('messagetype')
    @classmethod
    def validating_messagetype(cls, value) -> str:
        if value != 'event':
            raise ValueError('messagetype field should be "events" to write to events to the server')
        return value



