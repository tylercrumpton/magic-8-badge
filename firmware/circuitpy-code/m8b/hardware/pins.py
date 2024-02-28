import board


class Touch:
    A = board.TOUCH_A
    B = board.TOUCH_B
    UP = board.TOUCH_UP
    DOWN = board.TOUCH_DOWN
    LEFT = board.TOUCH_LEFT
    RIGHT = board.TOUCH_RIGHT


TOUCH_PINS = [Touch.A, Touch.B, Touch.UP, Touch.DOWN, Touch.LEFT, Touch.RIGHT]

LIGHT_SENSOR_PIN = board.LIGHT_SENSOR
CHARGING_PIN = board.CHARGING
STANDBY_PIN = board.STANDBY
SHAKE_PIN = board.SHAKE
BACKLIGHT_PIN = board.LCD_BACKLIGHT

IMU_I2C = board.IMU_I2C()
