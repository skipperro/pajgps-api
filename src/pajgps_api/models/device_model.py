from typing import Any, List, Optional

from .base import BaseModel


class DeviceModel(BaseModel):
    """Model representing the device hardware model info embedded in a Device response."""

    model: Optional[str] = None
    model_nr: Optional[int] = None
    alarm_radius: Optional[int] = None
    alarm_erschuetterung: Optional[int] = None
    alarm_geschwindigkeit: Optional[int] = None
    alarm_batteriestand: Optional[int] = None
    alarm_sos: Optional[int] = None
    alarm_drop: Optional[int] = None
    alarm_stromunterbrechung: Optional[int] = None
    alarm_zuendalarm: Optional[int] = None
    service_dns: Optional[str] = None
    service_ip: Optional[str] = None
    service_port: Optional[int] = None
    service_type: Optional[str] = None
    expired: Optional[int] = None
    alarm_turn_off: Optional[int] = None
    alarm_volt: Optional[int] = None
    standalone_battery: Optional[int] = None
    logbook_access: Optional[int] = None
    max_battery: Optional[int] = None
    voice_messages: Optional[bool] = None
    route_profile: Optional[List[str]] = None
    route_accuracy: Optional[int] = None
    manual_link: Optional[str] = None
    step_counter: Optional[int] = None
    app_mode: Optional[str] = None
    geofence_audio_enabled: Optional[int] = None
    alarm_fall: Optional[int] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
