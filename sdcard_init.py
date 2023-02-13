"""initialize sd card module"""
import os
from machine import SoftSPI
from lib.sdcard import SDCard
from common import PINS


def sdcard_init():
    spisd = SoftSPI(
        1, miso=PINS["spi_miso"], mosi=PINS["spi_mosi"], sck=PINS["spi_sck"]
    )
    sd = SDCard(spisd, cs=PINS["spi_cs"])
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    print(f'/sd: {os.listdir("/sd")}')
