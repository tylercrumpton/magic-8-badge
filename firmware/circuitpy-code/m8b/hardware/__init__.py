from m8b.event import Event
from m8b.hardware.touch import touch
from m8b.hardware.imu import imu
from m8b.hardware.shake import shake

enabled_hadware = [touch, imu, shake]


def get_events() -> list[Event]:
    events = []
    for hardware in enabled_hadware:
        events.extend(hardware.get_events())
    return events
