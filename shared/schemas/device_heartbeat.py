from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DeviceHeartbeat(BaseModel):
    device_id: str
    zone_id: str
    status: Literal["online"]
    timestamp: datetime
    uptime_ms: int
