import network
import ntptime
from HeaterControl import HeaterControl


def set_ntptime():
    """Set NTP time"""
    try:
        ntptime.settime()
    except Exception as e:
        # """ERROR - ntptime.settime() error: [Errno 116] ETIMEDOUT"""
        print(f"ERROR - ntptime.settime() error: {e}")
        set_ntptime()


sta_if = network.WLAN(network.STA_IF)
if sta_if.isconnected():
    set_ntptime()
    thermostat = HeaterControl()
    thermostat.start()
else:
    print("NO NETWORK CONNECTION. WILL NOT RUN")
    print("Check WIFI_SSID and WIFI_PASSWORD are correct in secret.py")
