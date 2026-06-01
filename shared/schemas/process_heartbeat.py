from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProcessHeartbeat(BaseModel):
    process: Literal["backend", "collector", "worker"]
    status: Literal["online", "degraded", "offline"]
    timestamp: datetime
    metadata: dict = Field(default_factory=dict)
