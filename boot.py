"""BOOT"""
import time
from ConnectWiFi import connect
from sdcard_init import sdcard_init
from utils import print_pins

print_pins()
connect()
sdcard_init()
time.sleep(0.5)
print_pins()
