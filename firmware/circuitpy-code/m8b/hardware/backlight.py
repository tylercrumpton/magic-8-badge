from pwmio import PWMOut

from m8b.hardware.pins import BACKLIGHT_PIN

class Backlight:
    def __init__(self):
        self._backlight = PWMOut(BACKLIGHT_PIN, frequency=1000, duty_cycle=0)

    @property
    def brightness(self):
        return self._backlight.duty_cycle / 65535
    
    @brightness.setter
    def brightness(self, value:float):
        duty_cycle = int(value * 65535)
        duty_cycle = max(0, min(duty_cycle, 65535))
        self._backlight.duty_cycle = duty_cycle


backlight = Backlight()