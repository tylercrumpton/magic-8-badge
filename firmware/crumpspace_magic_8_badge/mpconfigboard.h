#define MICROPY_HW_BOARD_NAME "CrumpSpace Magic 8 Badge"
#define MICROPY_HW_MCU_NAME "rp2040"

#define MICROPY_HW_LED_STATUS (&pin_GPIO5)

#define CIRCUITPY_BOARD_I2C         (1)
#define CIRCUITPY_BOARD_I2C_PIN     {{.scl = &pin_GPIO7, .sda = &pin_GPIO6}}
