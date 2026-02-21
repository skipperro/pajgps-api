from typing import Any, Optional

from .base import BaseModel


class Notification(BaseModel):
    """Notification model."""

    id: int
    iddevice: int
    icon: str
    bezeichnung: str
    meldungtyp: int  # alert_type
    dateunix: int
    lat: float
    lng: float
    isread: int
    radiusin: int
    radiusout: int
    zuendon: int
    zuendoff: int
    push: int
    suppressed: int
    name: Optional[str] = None
    meldung: Optional[str] = None
    imei: Optional[str] = None
    speed: Optional[int] = None
    speederlaubt: Optional[int] = None
    audio_file_name: Optional[str] = None
    email: Optional[str] = None
    deleted_at: Optional[str] = None

    def __init__(
        self,
        id: int,
        iddevice: int,
        icon: str,
        bezeichnung: str,
        meldungtyp: int,
        dateunix: int,
        lat: float,
        lng: float,
        isread: int,
        radiusin: int,
        radiusout: int,
        zuendon: int,
        zuendoff: int,
        push: int,
        suppressed: int,
        name: Optional[str] = None,
        meldung: Optional[str] = None,
        imei: Optional[str] = None,
        speed: Optional[int] = None,
        speederlaubt: Optional[int] = None,
        audio_file_name: Optional[str] = None,
        email: Optional[str] = None,
        deleted_at: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.iddevice = iddevice
        self.name = name
        self.icon = icon
        self.bezeichnung = bezeichnung
        self.meldung = meldung
        self.meldungtyp = meldungtyp
        self.dateunix = dateunix
        self.lat = lat
        self.lng = lng
        self.isread = isread
        self.imei = imei
        self.speed = speed
        self.speederlaubt = speederlaubt
        self.radiusin = radiusin
        self.radiusout = radiusout
        self.zuendon = zuendon
        self.zuendoff = zuendoff
        self.audio_file_name = audio_file_name
        self.email = email
        self.push = push
        self.suppressed = suppressed
        self.deleted_at = deleted_at
        super().__init__(**kwargs)
