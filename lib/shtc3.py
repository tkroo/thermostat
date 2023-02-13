# pylint: disable=missing-function-docstring
"""interface for SHTC3 temperature sensor I2C module"""

import time


class SHTC3_I2C:
    """Class representing the SHTC3 temperature sensor I2C module"""

    def __init__(self, i2c_obj):
        self.i2c = i2c_obj

    # shtc3 init addr-0x70
    def shtc3_init(self):
        buf0 = bytearray([0x35, 0x17])
        self.i2c.writeto(0x70, buf0)
        time.sleep_ms(500)
        buf = bytearray([0xEF, 0xC8])
        self.i2c.writeto(0x70, buf)
        self.i2c.readfrom_into(0x70, buf)
        num = int.from_bytes(buf, "big")
        print("I2C device shtc3 init and id is %d" % num)

    def get_temperature_humidity(self, echo=False, ret=True):
        buf = bytearray([0x7C, 0xA2])
        self.i2c.writeto(0x70, buf)
        buf2 = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.i2c.readfrom_into(0x70, buf2)
        temp = (buf2[1] | (buf2[0] << 8)) * 175 / 65536.0 - 45.0
        humi = (buf2[4] | (buf2[3] << 8)) * 100 / 65536.0
        # echo_Arg = "shtc3: Temperature=" + str(temp) + ", Humidity=" + str(humi)
        # print(echo_Arg)
        ret_Arg = {}
        ret_Arg["humidity"] = humi
        ret_Arg["temp"] = temp
        return ret_Arg
