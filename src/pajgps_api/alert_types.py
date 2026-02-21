from enum import IntEnum


class AlertType(IntEnum):
    """Alert type constants documented by the PAJ GPS API.

    The API mentions a range of 1..22, but only the values below are documented.
    """

    SHOCK = 1
    BATTERY = 2
    RADIUS = 3
    SOS = 4
    SPEED = 5
    POWER_CUT_OFF = 6
    IGNITION = 7
    DROP = 9
    AREA_ENTER = 10
    AREA_LEAVE = 11
    VOLTAGE = 13
    TURN_OFF = 22


# Convenience constants for direct imports
ALERT_TYPE_SHOCK = AlertType.SHOCK
ALERT_TYPE_BATTERY = AlertType.BATTERY
ALERT_TYPE_RADIUS = AlertType.RADIUS
ALERT_TYPE_SOS = AlertType.SOS
ALERT_TYPE_SPEED = AlertType.SPEED
ALERT_TYPE_POWER_CUT_OFF = AlertType.POWER_CUT_OFF
ALERT_TYPE_IGNITION = AlertType.IGNITION
ALERT_TYPE_DROP = AlertType.DROP
ALERT_TYPE_AREA_ENTER = AlertType.AREA_ENTER
ALERT_TYPE_AREA_LEAVE = AlertType.AREA_LEAVE
ALERT_TYPE_VOLTAGE = AlertType.VOLTAGE
ALERT_TYPE_TURN_OFF = AlertType.TURN_OFF
