from typing import Any, Optional, Union

from .base import BaseModel


class SensorData(BaseModel):
    """Model representing device sensor data."""

    ts: Optional[Union[str, dict]] = None
    volt: Optional[int] = None
    did: Optional[int] = None
    date_unix: Optional[Union[str, dict]] = None
    date_iso: Optional[str] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
