import alarm

from countio import Counter
from digitalio import Pull

from m8b.hardware.pins import SHAKE_PIN
from m8b.event import Event


class ShakeEvent(Event):
    def __init__(self):
        pass


class Shake:
    def __init__(self):
        self.shake_counter = Counter(SHAKE_PIN, pull=Pull.UP)
     

    def get_events(self) -> list[ShakeEvent]:
        if self.shake_counter.count > 0:
            self.shake_counter.reset()
            return [ShakeEvent()]
        return []
    
    def get_pin_alarm(self):
        # Need to release the pin from the counter to use it as an alarm pin
        self.shake_counter.deinit()
        return alarm.pin.PinAlarm(SHAKE_PIN, pull=Pull.UP, value=False)
        


shake = Shake()
