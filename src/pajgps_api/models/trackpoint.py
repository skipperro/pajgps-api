from .base import BaseModel


class TrackPoint(BaseModel):
    """Model representing a tracking data point."""

    id = None
    lat = None
    lng = None
    direction = None
    dateunix = None
    battery = None
    speed = None
    iddevice = None
    steps = None
    heartbeat = None
    accuracy = None
    wifi = None
    note = None
    upt = None
    wzp = None
