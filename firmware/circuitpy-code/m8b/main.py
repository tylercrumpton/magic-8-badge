import time
from m8b.apps.mainmenu import MainMenu
from m8b.apps.magic8ball import Magic8Ball
from m8b.hardware.display import display
from m8b.hardware import get_events

app_list = {"Main Menu": MainMenu, "Magic 8 Ball": Magic8Ball}


def main_loop():
    print("main_loop started")
    last_draw_time = time.monotonic()
    app = MainMenu()

    while True:
        # Check for and handle any events (Event Loop)
        events = get_events()
        for event in events:
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
                app = app_list[next_app_to_run]()


# Start the main loop
main_loop()
