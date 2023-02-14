# pylint: disable=import-outside-toplevel, global-statement
"""Display sensor data on OLED or print to console"""
from machine import SoftI2C
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

    # def display_off(self):
    #     """Function to turn oled off"""
    #     if oled_present():
    #         self.oled.fill(0)
    #         self.oled.poweroff()


# def oled_present():
#     """Function to test if oled device is present at address"""
#     if oled:
#         l = [hex(da) for da in oled.i2c.scan()]
#         return len(l) > 0 and l[0] == I2C_ADDR
#     else:
#         return False


# def display_init():
#     """Initialize the OLED display"""
#     global oled
#     if oled is None:
#         try:
#             oled = Oled_Display(PINS["oled_scl"], PINS["oled_sda"])
#         except Exception as e:
#             print(f"oled device not found at I2C addr {I2C_ADDR}: {e}")
#             print("will not use oled display")
#             blink_led(5, 0.05)
#             oled = None
#             AppVars.use_oled.set(False)


# def display_info(readings):
#     # probably too many lines in here just to check if the oled device is connected
#     # how can I simplify this detection test?
#     """Display sensor data on OLED or print to console"""
#     global oled

#     if AppVars.use_oled.value:
#         display_init()

#         if oled_present():
#             oled.display_text(readings)
#         else:
#             print("oled device not found")
#             blink_led(5, 0.05)

#     else:
#         if oled_present():
#             print("turning off oled device")
#             oled.display_off()
#             oled = None
#         print(f"temp: {readings['temp']}°F humidity: {readings['humidity']}%")


# def display_image(file, inverted):
#     """Display an image"""
#     # print(f"display_image, file:{file}, inverted:{inverted}")
#     global oled
#     if AppVars.use_oled.value:
#         display_init()

#         if oled_present():
#             print("oled is present")
#             oled.display_image(file, inverted)
#         else:
#             print("oled device not found")
#             blink_led(5, 0.05)
