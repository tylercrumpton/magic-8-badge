import terminalio
import displayio

from adafruit_display_text.label import Label

from m8b.event import Event
from m8b.hardware.touch import TouchEvent
from m8b.hardware.pins import Touch


class TouchTest:

    def __init__(self):
        print("Touch Test app started")
        self.wants_to_exit = False
        self.event_label = Label(
            terminalio.FONT,
            text="",
            color=(255, 255, 255),
            background_color=(0, 0, 0),
            scale=2,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 120),
            save_text=False,
        )
        self.quit_label = Label(
            terminalio.FONT,
            text="Hold B to quit",
            color=(128, 128, 128),
            background_color=(0, 0, 0),
            scale=1,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 200),
            save_text=False,
        )
        self.just_started = True
        self.needs_redraw = True
        self.event_label.text = "Test out the\ntouch pads!"
        self.root_display_group = displayio.Group()
        self.root_display_group.append(self.event_label)
        self.root_display_group.append(self.quit_label)

    def handle_event(self, event: Event):
        if isinstance(event, TouchEvent):
            self.event_label.scale = 1
            if event.action == "PRESS_START":
                self.event_label.text = f"Pad {event.pad} pressed!"
            elif event.action == "PRESS_END":
                self.event_label.text = f"Pad {event.pad} released!"
            elif event.action == "HOLD_START":
                self.event_label.text = f"Pad {event.pad} held!"
                if event.pad == Touch.B:
                    self.wants_to_exit = True

    def run(self):
        """Run the app's logic here.
        This function will be called every tick of the Run loop.
        """

    def draw(self, display):
        if not self.needs_redraw:
            return

        if self.just_started:
            display.root_group = self.root_display_group
            self.just_started = False

        self.needs_redraw = False

    def stop(self):
        """Run any cleanup code here for when the app is about to exit."""
