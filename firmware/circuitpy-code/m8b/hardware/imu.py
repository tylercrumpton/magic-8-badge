from qmi8658 import QMI8658
from m8b.hardware.pins import IMU_I2C
from m8b.event import Event


class IMUEvent(Event):
    def __init__(self, acceleration, gyro):
        self.acceleration = acceleration
        self.gyro = gyro


class IMU:
    def __init__(self):
        self.imu = QMI8658(IMU_I2C)
        self.imu.accel_enabled = True
        self.imu.gyro_enabled = True

    def get_events(self) -> list[IMUEvent]:
        events = []
        events.append(
            IMUEvent(
                acceleration=self.imu.accel,
                gyro=self.imu.gyro,
            )
        )
        return events


imu = IMU()
