import terminalio
import displayio

from adafruit_display_text.label import Label

from m8b.event import Event
from m8b.hardware.imu import IMUEvent
from m8b.hardware.touch import TouchAction, TouchEvent
from m8b.hardware.pins import Touch


class IMUTest:

    def __init__(self):
        print("IMU Test app started")
        self.wants_to_exit = False
        self.title_label = Label(
            terminalio.FONT,
            text="IMU Data",
            color=(255, 255, 255),
            background_color=(0, 0, 0),
            scale=2,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 90),
            save_text=False,
        )
        self.accel_data_label = Label(
            terminalio.FONT,
            text="",
            color=(255, 255, 255),
            background_color=(0, 0, 0),
            scale=1,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 120),
            save_text=False,
        )
        self.gyro_data_label = Label(
            terminalio.FONT,
            text="",
            color=(255, 255, 255),
            background_color=(0, 0, 0),
            scale=1,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 150),
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
        self.root_display_group = displayio.Group()
        self.root_display_group.append(self.title_label)
        self.root_display_group.append(self.accel_data_label)
        self.root_display_group.append(self.gyro_data_label)
        self.root_display_group.append(self.quit_label)

    def handle_event(self, event: Event):
        if isinstance(event, IMUEvent):
            self.accel_data_label.text = (
                f"Accel: {tuple(round(i, 1) for i in event.acceleration)}"
            )
            self.gyro_data_label.text = (
                f"Gyro: {tuple(round(i, 1) for i in event.gyro)}"
            )
        elif isinstance(event, TouchEvent) and event.pad == Touch.B:
            if event.action == TouchAction.HOLD_START:
                self.quit_label.text = "Release to quit"
            elif event.action == TouchAction.HOLD_END:
                print("Exiting IMU Test app")
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
        return
