import terminalio
from adafruit_display_text.label import Label
import displayio

from m8b.event import Event
from m8b.hardware.touch import TouchEvent, TouchAction
from m8b.hardware.charger import ChargerEvent, ChargingState
from m8b.hardware.pins import Touch


class MainMenu:
    def __init__(self):
        print("Main Menu started")
        self.options = [
            "Magic 8 Ball",
            "Touch Test",
            "IMU Test",
            "Backlight Test",
        ]
        self.current_option_index = 0
        self.animation_frames_remaining = 0
        self.wants_to_exit = False
        self.selected_label = Label(
            terminalio.FONT,
            text="",
            color=(255, 255, 255),
            background_color=(0, 0, 0),
            scale=2,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 120),
            save_text=False,
        )
        self.next_label = Label(
            terminalio.FONT,
            text="",
            color=(128, 128, 128),
            background_color=(0, 0, 0),
            scale=1,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 150),
            save_text=False,
        )
        self.previous_label = Label(
            terminalio.FONT,
            text="",
            color=(128, 128, 128),
            background_color=(0, 0, 0),
            scale=1,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 90),
            save_text=False,
        )
        self.root_display_group = displayio.Group()
        self.root_display_group.append(self.selected_label)
        self.root_display_group.append(self.next_label)
        self.root_display_group.append(self.previous_label)

        self.just_started = True
        self.needs_redraw = True

    def draw(self, display):
        if not self.needs_redraw:
            return

        if self.just_started:
            display.root_group = self.root_display_group
            self.just_started = False

        self.needs_redraw = False
        # Draw each option in the menu
        for i, option in enumerate(self.options):
            if i == self.current_option_index:
                self.selected_label.text = option
            elif i == (self.current_option_index + 1) % len(self.options):
                self.next_label.text = option
            elif i == (self.current_option_index - 1) % len(self.options):
                self.previous_label.text = option

    def handle_event(self, event: Event):
        # print("MainMenu handle_event", event)
        if isinstance(event, TouchEvent):
            # print("MainMenu handle_event TouchEvent", event.action, event.pad)
            if event.action == TouchAction.PRESS_END:
                if event.pad == Touch.A:
                    self.run_option(int(self.current_option_index))
                elif event.pad == Touch.UP:
                    self.animation_frames_remaining = 30
                    self.current_option_index -= 1
                elif event.pad == Touch.DOWN:
                    self.animation_frames_remaining = 30
                    self.current_option_index += 1

                self.current_option_index %= len(self.options)
                self.needs_redraw = True
        elif isinstance(event, ChargerEvent):
            if event.state == ChargingState.CHARGING:
                print("Charging!")
            elif event.state == ChargingState.NOT_CHARGING:
                print("Not charging!")
            elif event.state == ChargingState.FULL:
                print("Charged!")

    def run(self):
        pass

    def run_option(self, index):
        # Launch the app associated with the selected option
        print("Running option", self.options[index])
        self.wants_to_exit = True
        self.app_to_run = self.options[index]

    def stop(self):
        return self.app_to_run
