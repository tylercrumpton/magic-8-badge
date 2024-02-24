import random
import time
import terminalio

from adafruit_display_text.label import Label

from m8b.event import Event
from m8b.hardware.touch import TouchEvent
from m8b.hardware.shake import ShakeEvent
from m8b.hardware.pins import Touch

SHAKE_DURATION = 2.0  # seconds

NORMAL_ANSWERS = [
    "It is\ncertain",
    "It is\ndecidedly so",
    "Without\na doubt",
    "Yes\ndefinitely",
    "You may\nrely on it",
    "Concentrate\nand ask again",
    "Very\ndoubtful",
    "As I see\nit, yes",
    "Most\nlikely",
    "Outlook\ngood",
    "Yes",
    "Signs point\nto yes",
    "Reply hazy,\ntry again",
    "Ask again\nlater",
    "Better not\ntell you now",
    "Cannot\npredict now",
    "Don't count\non it",
    "My reply\nis no",
    "My sources\nsay no",
    "Outlook not\nso good",
]

HACKER_ANSWERS = [
    "404 response:\nnot found",
    "Turn it off\nand on again",
    "Patches\nwelcome",
    "It's a\nfeature",
    "It's a\nbug",
    "It's a\nhack",
    "Password:",
    "Permission\ndenied",
    "Segmentation\nfault",
    "Unexpected\nEOF",
    "Type 'cookie'\nyou idiot",
    "command not\nfound: m8b",
]


class Magic8Ball:

    def __init__(self):
        print("Magic 8 Ball app started")
        self.answers = HACKER_ANSWERS

        self.selected_answer = ""
        self.is_shaking = False
        self.wants_to_exit = False
        self.label = Label(
            terminalio.FONT,
            text="",
            color=(255, 255, 255),
            background_color=(0, 0, 0),
            scale=2,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, 120),
            save_text=False,
        )
        self.just_started = True
        self.needs_redraw = True
        self.label.text = "Shake me!"

    def handle_event(self, event: Event):
        if isinstance(event, ShakeEvent) or (
            isinstance(event, TouchEvent)
            and event.pad in [Touch.UP, Touch.DOWN, Touch.LEFT, Touch.RIGHT]
        ):
            print("Shaking!")
            self.is_shaking = True
            self.start_shake_time = time.monotonic()
            self.label.scale = 1
        elif isinstance(event, TouchEvent) and event.pad in [Touch.A, Touch.B]:
            print("Exiting Magic8Ball app")
            self.wants_to_exit = True

    def run(self):
        current_time = time.monotonic()

        # "Animate" the shake by displaying a different answer every frame.
        # Stop the shake animation after it's been shaking for a specific amount of time.
        if self.is_shaking:
            self.selected_answer = random.choice(self.answers)
            self.needs_redraw = True
            if current_time - self.start_shake_time > SHAKE_DURATION:
                self.label.scale = 2
                self.is_shaking = False

    def draw(self, display):
        if self.just_started:
            display.root_group = self.label
            self.just_started = False

        if not self.needs_redraw:
            return

        self.needs_redraw = False
        if self.is_shaking:
            self.label.text = self.selected_answer

    def stop(self):
        pass  # Nothing to clean up in this app
