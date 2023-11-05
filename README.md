# Magic 8-Badge
_Hardware, software, and other resouces for a fun little CircuitPython-compatible PCB badge!_

**Note:** Lots of information and improvements to be added soon!

## Hardware
All of the hardware design files are included in the [`hardware/`](./hardware) directory. The board was designed with KiCad 7, using mostly components from JLCPCB's [Assembly Parts Library](https://jlcpcb.com/parts).

## Firmware
The Magic 8-Badge was created to utilize [Adafruit's CircuitPython 🐍](https://circuitpython.org), and will hopefully have a board definition available on the CircuitPython website soon. The version of the Magic 8-Badge distrubted at PhreakNIC 24 in Nov 2023 are runnings a slightly-modified version of CircuitPython 8.2.0 that enables software pullup resistors on the I2C lines connected to the 6DoF IMU chip. The diff in changes in available in [`firmware/8.2.x-circuitpython-patch-208ebdf3.diff`](./firmware/8.2.x-circuitpython-patch-208ebdf3.diff).

The CircuitPython `*.py` files used to run the badge are included in [`firmware/circuitpy-code`]. This code is a huge mess, but I have some changes coming soon that will clean up the code, speed up the boot time, improve the UX and graphics a bit, and hopefully add more fun little features! The main application is found in [`firmware/circuitpy-code/code.py`](./firmware/circuitpy-code/code.py), and there are some required libraries that need to be installed from the Adafruit CircuitPython Bundle as well as the Community Bundle:

- Adafruit CircuitPython Bundle requirements:
  - `adafruit_display_text`
  - `adafruit_imageload`
- Community Bundle requirements:
  - `gc9a01`
 
You'll need to copy these libraries from the respective bundles into the `/lib` directory on the `CIRCUITPY` drive that should show up when plugged into a USB port on your computer. 
