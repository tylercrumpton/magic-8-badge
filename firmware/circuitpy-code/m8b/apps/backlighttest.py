import terminalio
import displayio

from adafruit_display_text.label import Label

from m8b.event import Event
from m8b.hardware.touch import TouchEvent
from m8b.hardware.pins import Touch
from m8b.helpers.backlightcontroller import backlight_controller


class BacklightTest:

    def __init__(self):
        print("Backlight Control app started")

        self.wants_to_exit = False
        self.instruction_label = Label(
            terminalio.FONT,
            text="Tap Up/Down to\nadjust backlight",
            color=(255, 255, 255),
            background_color=(0, 0, 0),
            scale=2,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 120),
            save_text=False,
        )
        self.quit_label = Label(
            terminalio.FONT,
            text="Tap B to quit",
            color=(128, 128, 128),
            background_color=(0, 0, 0),
            scale=1,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 200),
            save_text=False,
        )
        self.just_started = True
        self.needs_redraw = True
        self.root_display_group = displayio.Group()
        self.root_display_group.append(self.instruction_label)
        self.root_display_group.append(self.quit_label)

    def handle_event(self, event: Event):
        if isinstance(event, TouchEvent) and event.pad == Touch.UP:
            print("Increasing backlight")
            backlight_controller.ramp_to(1.0, 1)
        elif isinstance(event, TouchEvent) and event.pad == Touch.DOWN:
            print("Decreasing backlight")
            backlight_controller.ramp_to(0.0, 1)
        elif isinstance(event, TouchEvent) and event.pad in [Touch.A, Touch.B]:
            print("Exiting Backlight Control app")
            self.wants_to_exit = True

    def run(self):
        """Run the app's logic here.
        This function will be called every tick of the Run loop."""

    def draw(self, display):
        if self.just_started:
            display.root_group = self.root_display_group
            self.just_started = False

    def stop(self):
        pass  # Nothing to clean up in this app
