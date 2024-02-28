from m8b.hardware.backlight import backlight
from m8b.hardware.display import display
display.root_group.hidden = True

import time
import alarm

from m8b.apps.mainmenu import MainMenu
from m8b.apps.magic8ball import Magic8Ball
from m8b.apps.touchtest import TouchTest
from m8b.apps.imutest import IMUTest


from m8b.hardware.shake import ShakeEvent, shake
from m8b.hardware.touch import TouchEvent
from m8b.hardware import get_events


APP_LIST = {
    "Main Menu": MainMenu,
    "Magic 8 Ball": Magic8Ball,
    "Touch Test": TouchTest,
    "IMU Test": IMUTest,
}
INTERACTION_EVENTS = [ShakeEvent, TouchEvent]
SLEEP_TIME = 5  # seconds
DIM_TIME = 3  # seconds

last_interaction_time = time.monotonic()


def main_loop():
    print("main_loop started")
    last_draw_time = time.monotonic()
    app = MainMenu()
    # app = IMUTest()

    while True:
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

        # Check if the device is intactive and we should go to sleep
        if (current_time - last_interaction_time) > SLEEP_TIME:
            go_to_sleep()
        elif (current_time - last_interaction_time) > SLEEP_TIME - DIM_TIME:
            # Dim based on time since last interaction
            dim_factor = (current_time - last_interaction_time - (SLEEP_TIME - DIM_TIME)) / DIM_TIME
            backlight.brightness = 1.0 - dim_factor



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
