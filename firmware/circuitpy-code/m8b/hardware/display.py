import board
import busio
import displayio
from gc9a01 import GC9A01


displayio.release_displays()
spi = busio.SPI(clock=board.LCD_SCL, MOSI=board.LCD_SDA)
display_bus = displayio.FourWire(
    spi,
    command=board.LCD_DC,
    chip_select=board.LCD_CS,
    reset=board.LCD_RESET,
    baudrate=48000000,
)

display = GC9A01(
    display_bus,
    width=240,
    height=240,
    rotation=180,
)
display.root_group = displayio.Group()
