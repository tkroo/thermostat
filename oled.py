# pylint: disable=import-outside-toplevel, global-statement
"""Display sensor data on OLED or print to console"""
import network
from common import WEBSERVER_PORT
from utils import AppVars
import lib.ssd1306 as ssd1306
import framebuf


sta_if = network.WLAN(network.STA_IF)
nw_addr = sta_if.ifconfig()[0]

# oled = None
# I2C_ADDR = "0x3c"  # ? trying to detect if OLED is connected


class Oled_Display:
    """use OLED display on ESP32"""

    def __init__(self, i2c):
        self.oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    def display_text(self, message):
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
