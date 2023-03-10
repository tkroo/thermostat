"""
Function to connect to network
# file secret.py contains:
WIFI_SSID="yourwifinetworkname"
WIFI_PASSWORD="yourwifinetworkpassword"
or you can just set the variables WIFI_SSID and WIFI_PASSWORD in this file
"""
from time import sleep
import network
from secret import WIFI_SSID, WIFI_PASSWORD



def connect():
    """Function to connect to network"""
    c = 0
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to wifi", end=" ")
        sta_if.active(True)
        sleep(0.1)
        sta_if.config(dhcp_hostname="esp32-thermostat")
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            c = c + 1
            print(f"{c}", end=" ")
            if c > 15:
                break
            sleep(1)
    else:
        print("wifi previously connected", end=" ")
    print("Network config:", sta_if.ifconfig())
