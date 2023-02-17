# pylint: disable=no-member,import-outside-toplevel
"""initialize sd card module"""
import os
from machine import SoftSPI, SoftI2C
from common import PINS, WEBSERVER_PORT, SENSOR_TYPE
from utils import AppVars
import lib.shtc3 as shtc3
import lib.ssd1306 as ssd1306
import framebuf
from lib.sdcard import SDCard


class i2cDevices:
    """init i2c devices"""

    def __init__(self, scl=PINS["scl"], sda=PINS["sda"]):
        self.scl = scl
        self.sda = sda
        self.i2c = SoftI2C(scl=PINS["scl"], sda=PINS["sda"])
        self.oled = self.init_oled()
        self.th_sensor = self.init_th_sensor()

    def init_th_sensor(self):
        if SENSOR_TYPE == "shtc3":
            th_sensor = shtc3.SHTC3_I2C(self.i2c)
        elif SENSOR_TYPE == "dhtXX":
            import dht

            th_sensor = dht.DHT11(PINS["dht11"])
        return th_sensor

    def init_oled(self):
        return Oled_Display(self.i2c)


def sdcard_init():
    spisd = SoftSPI(
        1, miso=PINS["spi_miso"], mosi=PINS["spi_mosi"], sck=PINS["spi_sck"]
    )
    sd = SDCard(spisd, cs=PINS["spi_cs"])
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    print(f'/sd: {os.listdir("/sd")}')


class Oled_Display:
    """use OLED display on ESP32"""

    def __init__(self, i2c):
        self.oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    def display_text(self, message, nw_addr):
        """display sensor data"""
        # self.oled.poweron()
        t = message["temp"]
        h = message["humidity"]
        hs = "ON" if AppVars.heater_state.value else "OFF"
        us = "USING SCHEDULE" if AppVars.use_heatschedule.value else "MANUAL CONTROL"
        self.oled.invert(False)
        self.oled.fill(0)
        self.oled.text(f"T:{t:.1f}F   H:{h:.1f}%", 0, 0)
        self.oled.text(f"HEAT: {hs}", 0, 9)
        self.oled.text(f"TARGET: {AppVars.target_temp.value:.1f}", 0, 20)
        self.oled.text(f"{us}", 0, 30)
        self.oled.text(f"{nw_addr}", 0, 47)
        self.oled.text(f"PORT {WEBSERVER_PORT}", 0, 56)
        self.oled.show()

    def display_lines(self, lines):
        """display lines of text"""
        self.oled.invert(False)
        self.oled.fill(0)
        positions = [0, 9, 20, 30, 39, 47, 56]
        for i, line in enumerate(lines):
            self.oled.text(line, 0, positions[i])
        self.oled.show()

    def display_image(self, file, inverted):
        """Displays a Single Image.
        Args:
            file: str               Path to file to display.
            inverted: bool          Inverts the black/white pbm file.
        """
        framebuf_type = framebuf.MONO_HLSB
        with open(file, "rb") as f:
            f.readline()
            f.readline()
            data = bytearray(f.read())
        fbuf = framebuf.FrameBuffer(data, 128, 64, framebuf_type)
        self.oled.invert(inverted)
        self.oled.blit(fbuf, 0, 0)
        self.oled.show()
