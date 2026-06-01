from __future__ import annotations

from datetime import datetime
from typing import Literal, Union
from uuid import uuid4

from pydantic import BaseModel, Field

SensorQuality = Literal["good", "uncertain", "bad", "stale", "missing"]
SensorValue = Union[float, bool]


class SensorEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    site_id: str
    zone_id: str
    device_id: str
    sensor_id: str
    protocol: str
    value: SensorValue
    unit: str
    timestamp: datetime
    quality: SensorQuality
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    metadata: dict = Field(default_factory=dict)
