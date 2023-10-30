import busio
from digitalio import DigitalInOut, Direction, Pull
from microcontroller import Pin

# -- I2C Device Addresses --
I2C_ADDRESS_L = 0x6B
I2C_ADDRESS_H = 0x6A

# -- Registers --
# General Purpose Registers
REG_WHO_AM_I = 0x00
REG_REVISION_ID = 0x01

# Setup and Control Registers
REG_CTRL1 = 0x02
REG_CTRL2 = 0x03
REG_CTRL3 = 0x04
# <reserved> = 0x05
REG_CTRL5 = 0x06
# <reserved> = 0x07
REG_CTRL7 = 0x08
REG_CTRL8 = 0x09
REG_CTRL9 = 0x0A

# Host Controlled Calibration Registers
REG_CAL1_L = 0x0B
REG_CAL1_H = 0x0C
REG_CAL2_L = 0x0D
REG_CAL2_H = 0x0E
REG_CAL3_L = 0x0F
REG_CAL3_H = 0x10
REG_CAL4_L = 0x11
REG_CAL4_H = 0x12

# FIFO Registers
REG_FIFO_WTM_TH = 0x13
REG_FIFO_CTRL = 0x14
REG_FIFO_SMPL_CNT = 0x15
REG_FIFO_STATUS = 0x16
REG_FIFO_DATA = 0x17

# Status Registers
REG_STATUSINT = 0x2D
REG_STATUS0 = 0x2E
REG_STATUS1 = 0x2F

# Timestamp Registers
REG_TIMESTAMP_LOW = 0x30
REG_TIMESTAMP_MID = 0x31
REG_TIMESTAMP_HIGH = 0x32

# Data Output Registers
REG_TEMP_L = 0x33
REG_TEMP_H = 0x34
REG_AX_L = 0x35
REG_AX_H = 0x36
REG_AY_L = 0x37
REG_AY_H = 0x38
REG_AZ_L = 0x39
REG_AZ_H = 0x3A
REG_GX_L = 0x3B
REG_GX_H = 0x3C
REG_GY_L = 0x3D
REG_GY_H = 0x3E
REG_GZ_L = 0x3F
REG_GZ_H = 0x40

# COD Indication and General Purpose Registers
REG_COD_STATUS = 0x46
REG_DQW_L = 0x49
REG_DQW_H = 0x4A
REG_DQX_L = 0x4B
REG_DQX_H = 0x4C
REG_DQY_L = 0x4D
REG_DQY_H = 0x4E
REG_DQZ_L = 0x4F
REG_DQZ_H = 0x50
REG_DVX_L = 0x51
REG_DVX_H = 0x52
REG_DVY_L = 0x53
REG_DVY_H = 0x54
REG_DVZ_L = 0x55
REG_DVZ_H = 0x56

# Activity Detection Output Registers
REG_TAP_STATUS = 0x59
REG_STEP_CNT_LOW = 0x5A
REG_STEP_CNT_MID = 0x5B
REG_STEP_CNT_HIGH = 0x5C

# Reset Register
REG_RESET = 0x60

# -- CTRL9 Commands --
CTRL_CMD_ACK = 0x00
CTRL_CMD_COPY_USID = 0x10
CTRL_CMD_AHB_CLOCK_GATING = 0x12

# -- Values --
VALUE_WHO_AM_I = 0x05
VALUE_RESET_DEFAULT = 0xB0

# -- Masks --
MASK_AUTO_INCREMENT = 0b0100_0000
MASK_ACCEL_ENABLE = 0b0000_0001
MASK_GYRO_ENABLE = 0b0000_0010
MASK_STATUSINT_CTRL9DONE = 0b1000_0000
MASK_STATUSINT_AVAIL = 0b0000_0001
MASK_STATUSINT_LOCKED = 0b1000_0010
MASK_REG_CTRL7_SYNC_SAMPLE = 0b1000_0000
MASK_ACCEL_FULL_SCALE = 0b0111_0000
MASK_GYRO_FULL_SCALE = 0b0111_0000


def _twos_complement_to_int(val: int) -> int:
    """Convert a two's complement value to a signed integer."""
    if val & (1 << (15)) != 0:
        val -= 1 << 16
    return val


class QMI8658:
    def __init__(
        self,
        i2c: busio.I2C,
        int1: Pin | None = None,
        int2: Pin | None = None,
        address: int = I2C_ADDRESS_H,
    ):
        self.i2c = i2c
        self.address = address
        self.int1 = int1
        self.int2 = int2

        if self.int1 is not None:
            self.int1 = DigitalInOut(int1)
            self.int1.direction = Direction.INPUT
            self.int1.pull = Pull.UP
        if self.int2 is not None:
            self.int2 = DigitalInOut(int2)
            self.int2.direction = Direction.INPUT
            self.int2.pull = Pull.UP

        self._accel_enabled = False
        self._gyro_enabled = False
        self._accel_scale = 2
        self._gyro_scale = 16
        self._ahb_clock_gated = True

        while not self.i2c.try_lock():
            pass
        self._verify_whoami()
        self.reset()
        self.auto_increment = True
        self.ahb_clock_gated = False
        self.enable_sync_sample_mode()

    def _verify_whoami(self):
        if self.read_register(REG_WHO_AM_I, 1)[0] != VALUE_WHO_AM_I:
            raise RuntimeError("Failed to find QMI8658.")

    def read_register(self, register: int, length: int) -> bytearray:
        self.i2c.writeto(self.address, bytearray([register]))
        result = bytearray(length)
        self.i2c.readfrom_into(self.address, result)
        return result

    def write_register(self, register: int, data: int):
        self.i2c.writeto(self.address, bytearray([register, data]))

    def send_command(self, command: int):
        # Write command to CTRL9 and wait for the status bit to go high
        self.write_register(REG_CTRL9, command)
        status = self.read_register(REG_STATUSINT, 1)[0]
        while status & MASK_STATUSINT_CTRL9DONE == 0:
            status = self.read_register(REG_STATUSINT, 1)[0]

        # Write ACK to CTRL9 and wait for the status bit to go low
        self.write_register(REG_CTRL9, CTRL_CMD_ACK)
        status = self.read_register(REG_STATUSINT, 1)[0]
        while status & MASK_STATUSINT_CTRL9DONE != 0:
            status = self.read_register(REG_STATUSINT, 1)[0]

    def set_register_bits(self, register: int, bits: int):
        self.write_register(register, self.read_register(register, 1)[0] | bits)

    def clear_register_bits(self, register: int, bits: int):
        self.write_register(register, self.read_register(register, 1)[0] & ~bits)

    def reset(self):
        self.write_register(REG_RESET, VALUE_RESET_DEFAULT)
        # NB: This takes about 15ms to complete?

    @property
    def auto_increment(self) -> bool:
        return (
            self.read_register(REG_CTRL1, 1)[0] & MASK_AUTO_INCREMENT
            == MASK_AUTO_INCREMENT
        )

    @auto_increment.setter
    def auto_increment(self, value: bool):
        if value:
            self.set_register_bits(REG_CTRL1, MASK_AUTO_INCREMENT)
        else:
            self.clear_register_bits(REG_CTRL1, MASK_AUTO_INCREMENT)

    @property
    def ahb_clock_gated(self) -> bool:
        return self._ahb_clock_gated

    @ahb_clock_gated.setter
    def ahb_clock_gated(self, value: bool):
        if not value:
            self.write_register(REG_CAL1_L, 0x01)
        else:
            self.clear_register_bits(REG_CAL1_L, 0x00)
        self.send_command(CTRL_CMD_AHB_CLOCK_GATING)
        self._ahb_clock_gated = value

    def enable_sync_sample_mode(self):
        self.set_register_bits(REG_CTRL7, MASK_REG_CTRL7_SYNC_SAMPLE)

    @property
    def accel_enabled(self) -> bool:
        return (
            self.read_register(REG_CTRL7, 1)[0] & MASK_ACCEL_ENABLE == MASK_ACCEL_ENABLE
        )

    @accel_enabled.setter
    def accel_enabled(self, value):
        if value:
            self.set_register_bits(REG_CTRL7, MASK_ACCEL_ENABLE)
            # -- HACK: Why do I need to enable gyro to get accel data? --
            self.gyro_enabled = True
            # -----------------------------------------------------------
        else:
            self.clear_register_bits(REG_CTRL7, MASK_ACCEL_ENABLE)
        self._accel_enabled = value

    @property
    def gyro_enabled(self) -> bool:
        return (
            self.read_register(REG_CTRL7, 1)[0] & MASK_GYRO_ENABLE == MASK_GYRO_ENABLE
        )

    @gyro_enabled.setter
    def gyro_enabled(self, value):
        if value:
            self.set_register_bits(REG_CTRL7, MASK_GYRO_ENABLE)
        else:
            self.clear_register_bits(REG_CTRL7, MASK_GYRO_ENABLE)
            # -- HACK: Why do I need to enable gyro to get accel data? --
            self.accel_enabled = False
            # -----------------------------------------------------------
        self._gyro_enabled = value

    @property
    def accel_raw(self) -> tuple(int, int, int):
        if not self._accel_enabled:
            raise RuntimeError("Accelerometer is not enabled.")
        # Read STATUSINT register until STATUSINT.Avail = 1 and STATUSINT.Locked = 1
        status = self.read_register(REG_STATUSINT, 1)[0]
        while status & MASK_STATUSINT_AVAIL == 0 or status & MASK_STATUSINT_LOCKED != 0:
            status = self.read_register(REG_STATUSINT, 1)[0]

        if self._gyro_enabled:
            # Need to read all the way through the gyro (if enabled) data to clear the
            #   STATUSINT.Locked bit
            val = self.read_register(REG_AX_L, 12)
        else:
            val = self.read_register(REG_AX_L, 6)

        x = _twos_complement_to_int(val[0] + 256 * val[1])
        y = _twos_complement_to_int(val[2] + 256 * val[3])
        z = _twos_complement_to_int(val[4] + 256 * val[5])
        return (x, y, z)

    @property
    def accel(self) -> tuple(float, float, float):
        (x, y, z) = self.accel_raw
        ticks_per_g = 2**15 // self.accel_scale
        return (x / ticks_per_g, y / ticks_per_g, z / ticks_per_g)

    @property
    def gyro_raw(self) -> tuple(int, int, int):
        if not self._gyro_enabled:
            raise RuntimeError("Gyro is not enabled.")
        # Read STATUSINT register until STATUSINT.Avail = 1 and STATUSINT.Locked = 1
        status = self.read_register(REG_STATUSINT, 1)[0]
        while status & MASK_STATUSINT_AVAIL == 0 or status & MASK_STATUSINT_LOCKED != 0:
            status = self.read_register(REG_STATUSINT, 1)[0]

        val = self.read_register(REG_GX_L, 6)
        x = _twos_complement_to_int(val[0] + 256 * val[1])
        y = _twos_complement_to_int(val[2] + 256 * val[3])
        z = _twos_complement_to_int(val[4] + 256 * val[5])
        return (x, y, z)

    @property
    def gyro(self) -> tuple(float, float, float):
        (x, y, z) = self.gyro_raw
        ticks_per_dps = 2**15 // self.gyro_scale
        return (x / ticks_per_dps, y / ticks_per_dps, z / ticks_per_dps)

    @property
    def temperature_c(self) -> int:
        val = self.read_register(REG_TEMP_L, 2)
        temp = val[0] + 256 * val[1]

        return _twos_complement_to_int(temp) / 256

    @property
    def temperature_f(self) -> int:
        return self.temperature_c * 9 / 5 + 32

    @property
    def revision_id(self) -> int:
        return self.read_register(REG_REVISION_ID, 1)[0]

    @property
    def firmware_version(self) -> int:
        return self.read_register(REG_DQW_L, 3)

    @property
    def usid(self) -> int:
        return self.read_register(REG_DVX_L, 6)

    @property
    def accel_scale(self) -> int:
        scale = (self.read_register(REG_CTRL2, 1)[0] & MASK_ACCEL_FULL_SCALE) >> 4
        return 2 << scale

    @accel_scale.setter
    def accel_scale(self, value: 2 | 4 | 8 | 16):
        if value == 2:
            self.clear_register_bits(REG_CTRL2, 0b0111_0000)
        elif value == 4:
            self.clear_register_bits(REG_CTRL2, 0b0110_0000)
            self.set_register_bits(REG_CTRL2, 0b0001_0000)
        elif value == 8:
            self.clear_register_bits(REG_CTRL2, 0b0101_0000)
            self.set_register_bits(REG_CTRL2, 0b0010_0000)
        elif value == 16:
            self.clear_register_bits(REG_CTRL2, 0b0100_0000)
            self.set_register_bits(REG_CTRL2, 0b0011_0000)
        else:
            raise RuntimeError(
                "Invalid accelerometer scale value. Valid values are 2, 4, 8, or 16."
            )

    @property
    def gyro_scale(self) -> int:
        scale = (self.read_register(REG_CTRL3, 1)[0] & MASK_GYRO_FULL_SCALE) >> 4
        return (1 << scale) * 16

    @gyro_scale.setter
    def gyro_scale(self, value: 16 | 32 | 64 | 128 | 256 | 512 | 1024 | 2048):
        if value == 16:
            self.clear_register_bits(REG_CTRL3, 0b0111_0000)
        elif value == 32:
            self.clear_register_bits(REG_CTRL3, 0b0110_0000)
            self.set_register_bits(REG_CTRL3, 0b0001_0000)
        elif value == 64:
            self.clear_register_bits(REG_CTRL3, 0b0101_0000)
            self.set_register_bits(REG_CTRL3, 0b0010_0000)
        elif value == 128:
            self.clear_register_bits(REG_CTRL3, 0b0100_0000)
            self.set_register_bits(REG_CTRL3, 0b0011_0000)
        elif value == 256:
            self.clear_register_bits(REG_CTRL3, 0b0011_0000)
            self.set_register_bits(REG_CTRL3, 0b0100_0000)
        elif value == 512:
            self.clear_register_bits(REG_CTRL3, 0b0010_0000)
            self.set_register_bits(REG_CTRL3, 0b0101_0000)
        elif value == 1024:
            self.clear_register_bits(REG_CTRL3, 0b0001_0000)
            self.set_register_bits(REG_CTRL3, 0b0110_0000)
        elif value == 2048:
            self.set_register_bits(REG_CTRL3, 0b0111_0000)
        else:
            raise RuntimeError(
                "Invalid gyro scale value. Valid values are 16, 32, 64, 128, 256, 512, 1024, or 2048."
            )

    def self_test_accel(self) -> tuple:
        # Disable sensors (CTRL7 = 0x00)
        self.write_register(REG_CTRL7, 0x00)

        # Set proper accelerometer ODR (CTRL2.aODR) and bit CTRL2.aST (bit7) to 1
        # NB: Currently hardcoded to 1kHz (0b0011)
        self.write_register(REG_CTRL2, 0b1000_0011)

        # Wait for STATUSINT.bit0 to go High
        status = self.read_register(REG_STATUSINT, 1)[0]
        while status & 0b0000_0001 == 0:
            status = self.read_register(REG_STATUSINT, 1)[0]

        # Set CTRL2.aST(bit7) to 0 to clear STATUSINT1.bit0
        self.clear_register_bits(REG_CTRL2, 0b1000_0000)

        # Wait fo STATUSINT1.bit0 to go Low
        status = self.read_register(REG_STATUSINT, 1)[0]
        while status & 0b0000_0001 != 0:
            status = self.read_register(REG_STATUSINT, 1)[0]

        # Read the Accel Self-Test result:
        #     X channel: dVX_L and dVX_H (registers 0x51 and 0x52)
        #     Y  channel: dVY_L and dVY_H (registers 0x53 and 0x54)
        #     Z channel: dVZ_L and dVZ_H (registers 0x55 and 0x56)
        (xl, xh, yl, yh, zl, zh) = self.read_register(REG_DVX_L, 6)
        x = xl + 256 * xh
        y = yl + 256 * yh
        z = zl + 256 * zh
        if x < 400 or y < 400 or z < 400:
            raise RuntimeError(
                "Failed accelerometer self-test.", {"x": x, "y": y, "z": z, "min": 400}
            )
        return (x, y, z)
