from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
import board
import busio
from qmi8658 import QMI8658
import terminalio
import random
import math
import displayio
from touchio import TouchIn
from adafruit_display_text.bitmap_label import Label
import adafruit_imageload
from gc9a01 import GC9A01
from time import sleep
import time
import countio


ambient_light = AnalogIn(board.LIGHT_SENSOR)
touch_r = TouchIn(board.TOUCH_RIGHT)
touch_u = TouchIn(board.TOUCH_UP)
touch_d = TouchIn(board.TOUCH_DOWN)
touch_l = TouchIn(board.TOUCH_LEFT)
touch_b = TouchIn(board.TOUCH_B)
touch_a = TouchIn(board.TOUCH_A)
charging = DigitalInOut(board.CHARGING)
charging.direction = Direction.INPUT
charging.pull = Pull.UP
standby = DigitalInOut(board.STANDBY)
standby.direction = Direction.INPUT
standby.pull = Pull.UP
shake = countio.Counter(board.SHAKE, pull=Pull.UP)


# Set up the display --------------------------------
displayio.release_displays()
spi = busio.SPI(clock=board.LCD_SCL, MOSI=board.LCD_SDA)
display_bus = displayio.FourWire(
    spi,
    command=board.LCD_DC,
    chip_select=board.LCD_CS,
    reset=board.LCD_RESET,
    baudrate=48000000,
)
# ---------------------------------------------------

# Set up the accel+gyro -----------------------------
imu = QMI8658(board.IMU_I2C())
imu.accel_enabled = True
imu.gyro_enabled = True
# ---------------------------------------------------

print("Initializing display...")
display = GC9A01(
    display_bus, width=240, height=240, rotation=180, backlight_pin=board.LCD_BACKLIGHT
)
print("Initialized!")


def polar_to_cartesian(r, theta_deg):
    theta_rad = math.radians(theta_deg)
    x = math.floor(r * math.cos(theta_rad)) + 120
    y = math.floor(r * math.sin(theta_rad)) + 120
    return (x, y)


# Load the sprite sheet (bitmap)
sprite_sheet, palette = adafruit_imageload.load(
    "/cp_sprite_sheet.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)

# Find white and make transparent:
for index, color in enumerate(palette):
    if color == 0xFFFFFF:
        palette.make_transparent(index)
        break

# Make the display context
STATUS_BAR_ICON_SIZE = 16
center = displayio.Group(x=120, y=120)


status_bar = displayio.Group()
main_group = displayio.Group()
main_group.append(status_bar)
main_group.append(center)


display.root_group = main_group


icons = [
    displayio.TileGrid(
        sprite_sheet,
        pixel_shader=palette,
        width=1,
        height=1,
        tile_width=STATUS_BAR_ICON_SIZE,
        tile_height=STATUS_BAR_ICON_SIZE,
        default_tile=i,
        x=-STATUS_BAR_ICON_SIZE // 2,
        y=-STATUS_BAR_ICON_SIZE // 2,
    )
    for i in range(5)
]


class Icon:
    BLINKA = 0
    ROBOT = 1
    RESISTOR = 2
    CAPACITOR = 3
    HEART = 4


status_bar_icons = [
    {"show": False, "current": (92, -90), "target": (92, -90)},
    {"show": False, "current": (92, -90), "target": (92, -90)},
    {"show": False, "current": (92, -90), "target": (92, -90)},
    {"show": False, "current": (92, -90), "target": (92, -90)},
    {"show": False, "current": (92, -90), "target": (92, -90)},
]


def update_targets():
    spacing_deg = 20
    shown_icons = [i for i in status_bar_icons if i["show"]]
    for index, icon in enumerate(shown_icons):
        theta = -90 - (len(shown_icons) - 1) * spacing_deg / 2 + index * spacing_deg
        # icons[index].x, icons[index].y = polar_to_cartesian(92, theta)
        icon["target"] = (92, theta)


starting_location = (140, -90)


def load_icons():
    for index in range(len(status_bar_icons)):
        icons[index].x, icons[index].y = polar_to_cartesian(*starting_location)
        status_bar.append(icons[index])


def show_icon(icon):
    if not status_bar_icons[icon]["show"]:
        status_bar_icons[icon]["current"] = starting_location
        status_bar_icons[icon]["show"] = True
        # icons[icon].hidden = False
        icons[icon].x, icons[icon].y = polar_to_cartesian(*starting_location)
        # status_bar.append(icons[icon])
        update_targets()


def hide_icon(icon):
    if status_bar_icons[icon]["show"]:
        status_bar_icons[icon]["show"] = False
        status_bar_icons[icon]["target"] = starting_location
        # icons[icon].hidden = True
        # status_bar.remove(icons[icon])
        update_targets()


def update_current():
    for index in range(len(status_bar_icons)):
        current = status_bar_icons[index]["current"]
        target = status_bar_icons[index]["target"]
        if current != target:
            current = (
                current[0] + (target[0] - current[0]) // 2,
                current[1] + (target[1] - current[1]) // 2,
            )
            status_bar_icons[index]["current"] = current
            icons[index].x, icons[index].y = polar_to_cartesian(*current)


load_icons()
iterations = 0
# while True:
#     update_current()
#     sleep(0.04)
#     iterations += 1
#     if iterations > 20:
#         random_icon = random.randint(0, 4)
#         if status_bar_icons[random_icon]["show"]:
#             hide_icon(random_icon)
#         else:
#             show_icon(random_icon)
#         iterations = 0


my_label = Label(
    terminalio.FONT,
    text="",
    color=(255, 255, 255),
    background_color=(0, 0, 0),
    scale=2,
    anchor_point=(0.5, 0.5),
    anchored_position=(0, 0),
    save_text=False,
)

center.append(my_label)
answers = [
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

i = 0
message = None
r = 0
theta = 0
dot_pos_x = 0
dot_pos_y = 0
dot_vel_x = 0
dot_vel_y = 0
last_physics_tick = time.monotonic_ns()
while True:
    new_message = ""
    # Magic 8 Ball answers ---------------------------
    # sleep(3)
    # for _ in range(30):
    #     my_label.text = random.choice(answers)
    # my_label.text = answers[i % len(answers)]
    # i += 1
    # -----------------------------------------------

    # Blink the status bar icons ---------------------
    # icons[1].hidden = True
    # sleep(0.5)
    # icons[1].hidden = False
    # sleep(0.5)
    # -----------------------------------------------

    # Wiggle the status bar icons --------------------
    # icons[1].x, icons[1].y = polar(i, 10)
    # i += 130
    # -----------------------------------------------

    # Touchpad test ----------------------------------
    # new_message = ""
    # new_message += "R" if touch_r.value else " "
    # new_message += "U" if touch_u.value else " "
    # new_message += "D" if touch_d.value else " "
    # new_message += "L" if touch_l.value else " "
    # new_message += "B" if touch_b.value else " "
    # new_message += "A" if touch_a.value else " "

    # -----------------------------------------------

    # Move Blinka around the screen with the D-pad ---
    # if touch_r.value:
    #     icons[0].x += 1
    # if touch_l.value:
    #     icons[0].x -= 1
    # if touch_u.value:
    #     icons[0].y -= 1
    # if touch_d.value:
    #     icons[0].y += 1
    # -----------------------------------------------

    # Move other around in polar coordinates ---------
    # if touch_r.value:
    #     r += 1
    # if touch_l.value:
    #     r -= 1
    # if touch_u.value:
    #     theta += 1
    # if touch_d.value:
    #     theta -= 1
    # icons[4].x, icons[4].y = polar_to_cartesian(r, theta)
    # new_message = f"r: {r}\ntheta: {theta}"
    # -----------------------------------------------

    # Adjust the brightness with the light sensor ----
    # print(ambient_light.value)
    display.brightness = min(ambient_light.value * 10 / 65535, 1.0)
    # print(display.brightness)
    # -----------------------------------------------

    # Display the charging status --------------------
    # charging_status = charging.value
    # charge_message = "Charging" if not charging.value else "Not charging"
    # standby_status = standby.value
    # standby_message = "\nStandby" if not standby.value else "\nNot standby"
    # new_message = charge_message + standby_message
    # count_message = f"\n{shake.count}"
    # new_message += count_message
    # -----------------------------------------------

    # Roll dots around the screen using the accel ---
    # (x, y, z) = imu.accel
    # # adjust the velocity based on the accel, capped at 1
    # dot_vel_x = max(min(dot_vel_x + x / 100, 1), -1)
    # dot_vel_y = max(min(dot_vel_y + y / 100, 1), -1)
    # # adjust the position based on the velocity, capped at 120
    # dot_pos_x = max(min(dot_pos_x + dot_vel_x, 120), -120)
    # dot_pos_y = max(min(dot_pos_y + dot_vel_y, 120), -120)
    # icons[0].x = 120 - math.floor(dot_pos_x)
    # icons[0].y = 120 - math.floor(dot_pos_y)
    # print(icons[0].x, icons[0].y)
    # -----------------------------------------------
    # Simpler version
    (x, y, z) = imu.accel
    if x > 0.1 and y > 0.1:
        icons[0].y -= 1
    elif x < -0.1 and y < -0.1:
        icons[0].y += 1
    elif x > 0.1 and y < -0.1:
        icons[0].x += 1
    elif x < -0.1 and y > 0.1:
        icons[0].x -= 1

    if message != new_message:
        message = new_message
        my_label.text = message
