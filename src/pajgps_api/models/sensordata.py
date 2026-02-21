from .base import BaseModel


class SensorData(BaseModel):
    """Model representing device sensor data."""

    ts = None
    volt = None
    did = None
    date_unix = None
    date_iso = None
