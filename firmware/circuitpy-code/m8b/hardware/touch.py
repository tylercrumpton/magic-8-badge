import time
from touchio import TouchIn
from m8b.hardware.pins import TOUCH_PINS
from m8b.event import Event

DOUBLE_PRESS_TIME = 0.5
HOLD_TIME = 1.0


class TouchAction:
    # SINGLE_PRESS = "SINGLE_PRESS"
    # DOUBLE_PRESS = "DOUBLE_PRESS"
    PRESS_START = "PRESS_START"
    PRESS_END = "PRESS_END"
    HOLD_START = "HOLD_START"
    HOLD_END = "HOLD_END"


class TouchPad:
    def __init__(self, pin):
        self.pin = pin
        self.input = TouchIn(pin)
        self.state = False
        self.last_time = 0
        self.hold_start = False


class TouchEvent(Event):
    def __init__(self, action, pad):
        self.action = action
        self.pad = pad


class Touch:
    def __init__(self):
        self.touch_pads = [TouchPad(pin) for pin in TOUCH_PINS]

    def get_events(self) -> list[TouchEvent]:
        events = []
        for touch_pad in self.touch_pads:
            # If the pad is touched and wasn't before:
            if touch_pad.input.value and not touch_pad.state:
                touch_pad.state = True
                events.append(TouchEvent(TouchAction.PRESS_START, touch_pad.pin))
                touch_pad.last_time = time.monotonic()

            # If the pad is not touched but was before:
            elif not touch_pad.input.value and touch_pad.state:
                touch_pad.state = False
                events.append(TouchEvent(TouchAction.PRESS_END, touch_pad.pin))

            # If the pad is touched and time since last touch is
            # more than given threshold, then it's a press and hold
            elif (
                touch_pad.input.value
                and touch_pad.state
                and (time.monotonic() - touch_pad.last_time) > HOLD_TIME
            ):
                if not touch_pad.hold_start:
                    events.append(TouchEvent(TouchAction.HOLD_START, touch_pad.pin))
                    touch_pad.hold_start = True
            else:
                if touch_pad.hold_start:
                    events.append(TouchEvent(TouchAction.HOLD_END, touch_pad.pin))
                    touch_pad.hold_start = False
        return events


touch = Touch()
