import time

from m8b.hardware.backlight import backlight


class BacklightController:
    def __init__(self, backlight):
        self.backlight = backlight
        self.setpoint = backlight.brightness  # Current actual brightness
        self.target_setpoint = self.setpoint  # Target brightness
        self.step = 0  # Brightness change per second
        self.duration = 0
        self.last_update_time = time.monotonic()

    def update(self):
        current_time = time.monotonic()
        delta_time = current_time - self.last_update_time

        # Adjust the setpoint if we're ramping
        if delta_time < self.duration:
            delta_setpoint = (
                self.step * delta_time
            )  # Change in brightness proportional to the elapsed time
            self.setpoint += delta_setpoint
            self.setpoint = (
                min(self.setpoint, self.target_setpoint)
                if self.step > 0
                else max(self.setpoint, self.target_setpoint)
            )

        self.backlight.brightness = self.setpoint
        self.last_update_time = current_time

    def ramp_to(self, brightness, duration):
        self.target_setpoint = brightness
        self.step = (self.target_setpoint - self.setpoint) / duration
        self.duration = duration


backlight_controller = BacklightController(backlight)
