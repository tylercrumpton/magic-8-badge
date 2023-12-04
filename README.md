# Magic 8-Badge

_Hardware, software, and other resouces for a fun little CircuitPython-compatible PCB badge!_

**Note:** Lots of information and improvements to be added soon!

## Hardware

All of the hardware design files are included in the [`hardware/`](./hardware) directory. The board was designed with KiCad 7, using mostly components from JLCPCB's [Assembly Parts Library](https://jlcpcb.com/parts).

## Firmware

The Magic 8-Badge was created to utilize [Adafruit's CircuitPython 🐍](https://circuitpython.org), and will hopefully have a board definition available on the CircuitPython website soon. The v1 version of the Magic 8-Badge distrbuted at PhreakNIC 24 in Nov 2023 are runnings a slightly-modified version of CircuitPython 8.2.0 that enables software pullup resistors on the I2C lines connected to the 6DoF IMU chip. The diff in changes in available in [`firmware/8.2.x-circuitpython-patch-208ebdf3.diff`](./firmware/8.2.x-circuitpython-patch-208ebdf3.diff).

The CircuitPython `*.py` files used to run the badge are included in [`firmware/circuitpy-code`](./firmware/circuitpy-code). This code is a huge mess, but I have some changes coming soon that will clean up the code, speed up the boot time, improve the UX and graphics a bit, and hopefully add more fun little features! The main application is found in [`firmware/circuitpy-code/code.py`](./firmware/circuitpy-code/code.py), and there are some required libraries that need to be installed from the Adafruit CircuitPython Bundle as well as the Community Bundle:

- Adafruit CircuitPython Bundle requirements:
  - `adafruit_display_text`
  - `adafruit_imageload`
- Community Bundle requirements:
  - `gc9a01`

You'll need to copy these libraries from the respective bundles into the `/lib` directory on the `CIRCUITPY` drive that should show up when plugged into a USB port on your computer.

## Errata

I will include notes her about board bugs, things to consider when making code changes, and whatever else little idiosyncasies are present in various versions of the Magic 8-Badge.

### v1

Version v1 of the Magic 8-Badge has a couple of issues that are mostly worked around in software and hardware re-work:

- The QMC6308 magnetometer chip (U9) has been removed from all v1 boards because the power and ground connections are reversed. If the chip is placed, the board will fail to start, effectively shorting the 3v3 power rail. Don't do this!
- There are no external pullups on the I2C lines connected to the QMI8658C accelerometer/gyroscope chip (U7). CircuitPython doesn't currently support setting internal pullup resistors for I2C pins, and the internal pullup resistors on the RP2040 are technically out of spec for I2C communications (50-80kohms). The patch to the CircuitPython core described above manually enables the internal pullup resistors, and I've not seen any issues reading from the QMI8658C with those. I'm going to try to submit a pull request to allow compile-time enabling of these internal resistors so that a custom build of CircuitPython is no longer neccessary. If you want to try a different version of CircuitPython that doesn't include that patch, no harm will be done, but CircuitPython will throw an error when trying to connect to the QMI8658C.
- There is no low-voltage cut-off for the Li-ion battery used for the Magic 8-Badge. The battery selected does offer low-voltage protection to keep the battery from discharging to dangerous levels, but the threshold voltage is lower than I would have liked. I recommend disconnecting the Li-ion battery if it is not going to be used in order preserve the capacity and health of the battery.

## License

The hardware and its design files are licensed under the [CERN Open Hardware Licence v2 - Permissive](./hardware/LICENSE.TXT).

The firmware/software is licensed under the [MIT License](./firmware/LICENSE.TXT).

The CrumpSpace logo is a trademark of CrumpSpace and should not be used in association with hardware or software that is sold or distributed by others.
