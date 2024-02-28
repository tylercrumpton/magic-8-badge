from m8b.hardware.backlight import backlight
from m8b.hardware.display import display

display.root_group.hidden = True

import time
import alarm

from m8b.apps.mainmenu import MainMenu
from m8b.apps.magic8ball import Magic8Ball
from m8b.apps.touchtest import TouchTest
from m8b.apps.imutest import IMUTest
from m8b.apps.backlighttest import BacklightTest

from m8b.hardware.shake import ShakeEvent, shake
from m8b.hardware.touch import TouchEvent
from m8b.hardware import get_events

from m8b.helpers.backlightcontroller import backlight_controller

APP_LIST = {
    "Main Menu": MainMenu,
    "Magic 8 Ball": Magic8Ball,
    "Touch Test": TouchTest,
    "IMU Test": IMUTest,
    "Backlight Test": BacklightTest,
}
INTERACTION_EVENTS = [ShakeEvent, TouchEvent]
SLEEP_TIME = 30  # seconds

last_interaction_time = time.monotonic()


def main_loop():
    print("main_loop started")
    last_draw_time = time.monotonic()
    app = MainMenu()
    backlight_controller.ramp_to(1.0, 1)

    while True:
        # Update the backlight
        backlight_controller.update()

        # Check for and handle any events (Event Loop)
        events = get_events()
        for event in events:
            if type(event) in INTERACTION_EVENTS:
                feed_sleep_dog()
            app.handle_event(event)

        # Run the app's logic (Run Loop)
        app.run()

        # Perform rendering (Draw Loop)
        current_time = time.monotonic()
        if (current_time - last_draw_time) > 1 / 30:  # 30 FPS
            # print("Actual draw loop FPS:", 1 / (current_time - last_draw_time))
            app.draw(display)
            last_draw_time = current_time

        # Check if the app has requested to exit
        if app.wants_to_exit:
            next_app_to_run = app.stop()
            if next_app_to_run is None:
                app = MainMenu()
            else:
                app = APP_LIST[next_app_to_run]()

        # Check if the device is inactive and we should go to sleep
        if (current_time - last_interaction_time) > SLEEP_TIME:
            go_to_sleep()


def feed_sleep_dog():
    global last_interaction_time
    last_interaction_time = time.monotonic()


def go_to_sleep():
    print("Sleeping, wake on shake")
    backlight.brightness = 0.0
    display.root_group.hidden = True

    alarm.exit_and_deep_sleep_until_alarms(shake.get_pin_alarm())


# Start the main loop
main_loop()
