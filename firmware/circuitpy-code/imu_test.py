# SPDX-FileCopyrightText: 2023 Tyler Crumpton for CrumpSpace
#
# SPDX-License-Identifier: MIT

from time import sleep
from math import floor
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from qmi8658 import QMI8658, REG_CTRL7

# Set up the accel+gyro -----------------------------
imu = QMI8658(board.IMU_I2C())
print("revision:", imu.revision_id, 0x7C)
print("firmware:", imu.firmware_version)
print("usid:", imu.usid)
imu.accel_enabled = True
imu.gyro_enabled = True
imu.accel_scale = 16
# imu.gyro_scale = 2048

print(imu.read_register(REG_CTRL7, 1))


while True:
    print("accel:", imu.accel)
    print("gyro:", imu.gyro)
    #     print("temp_f", imu.temperature_f)
    sleep(0.1)

# print(imu.self_test_accel())
