from typing import Any, Optional, Union

from .base import BaseModel


class TrackPoint(BaseModel):
    """Model representing a tracking data point."""

    id: Optional[Union[int, str]] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    direction: Optional[int] = None
    dateunix: Optional[int] = None
    battery: Optional[int] = None
    speed: Optional[int] = None
    iddevice: Optional[int] = None
    steps: Optional[int] = None
    heartbeat: Optional[int] = None
    accuracy: Optional[int] = None
    wifi: Optional[str] = None
    note: Optional[str] = None
    upt: Optional[str] = None
    wzp: Optional[bool] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
