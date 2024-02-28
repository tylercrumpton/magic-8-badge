from digitalio import DigitalInOut, Direction, Pull

from m8b.hardware.pins import CHARGING_PIN, STANDBY_PIN
from m8b.event import Event


class ChargingState:
    CHARGING = "CHARGING"
    FULL = "FULL"
    NOT_CHARGING = "NOT_CHARGING"


class ChargerEvent(Event):
    def __init__(self, state):
        self.state = state


class Charger:
    def __init__(self):
        self._charging = DigitalInOut(CHARGING_PIN)
        self._charging.direction = Direction.INPUT
        self._charging.pull = Pull.UP
        self._standby = DigitalInOut(STANDBY_PIN)
        self._standby.direction = Direction.INPUT
        self._standby.pull = Pull.UP
        self._previous_state = None

    @property
    def charging_state(self):
        charging_status = not self._charging.value  # Inverted
        standby_status = not self._standby.value  # Inverted
        if charging_status:
            charging_state = ChargingState.CHARGING
        elif standby_status:
            charging_state = ChargingState.FULL
        else:
            charging_state = ChargingState.NOT_CHARGING

        return charging_state

    def get_events(self) -> list[ChargerEvent]:
        events = []

        new_charging_state = self.charging_state
        if new_charging_state != self._previous_state:
            events.append(ChargerEvent(state=new_charging_state))
            self._previous_state = new_charging_state

        return events


charger = Charger()
