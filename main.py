import time
import network
import uasyncio as asyncio
from machine import SoftI2C

from common import PINS, SETTINGS_FILE, SENSOR_TYPE
import utils
from utils import AppVars

import oled
import lib.shtc3 as shtc3
import controls

from check_schedule import check_schedule
import webserver

DELAY = 5


i2c = SoftI2C(scl=PINS["scl"], sda=PINS["sda"])
oled = oled.Oled_Display(i2c)

if SENSOR_TYPE == "shtc3":
    th_sensor = shtc3.SHTC3_I2C(i2c)
elif SENSOR_TYPE == "dhtXX":
    import dht
    th_sensor = dht.DHT11(PINS["dht11"])



def set_target_temperature():
    """Function to set target temperature"""
    if AppVars.use_heatschedule.value:
        check = check_schedule(utils.load_json(SETTINGS_FILE)["days"])
        AppVars.schedule_temp.set(check if check else AppVars.minimum_temp.value)
        temp = AppVars.schedule_temp.value
    else:
        temp = AppVars.manual_temp.value
    AppVars.target_temp.set(temp)


def load_settings():
    """Function to load and assign some values from settings file"""
    print(f"Loading {SETTINGS_FILE}...")
    data = utils.load_json(SETTINGS_FILE)
    AppVars.use_heatschedule.set(data["use_heatschedule"])
    AppVars.hysteresis.set(data["hysteresis"])
    AppVars.use_oled.set(data["use_oled"])
    AppVars.minimum_temp.set(data["minimum_temp"])
    AppVars.manual_temp.set(data["saved_manual_temp"])

    initial_readings = utils.read_th_sensor(th_sensor)
    AppVars.curr_temp.set(initial_readings["temp"])
    AppVars.curr_hum.set(initial_readings["humidity"])

    set_target_temperature()

    print(f"initial temp: {AppVars.curr_temp.value}")
    print(f"initial humidity: {AppVars.curr_hum.value}")
    print(f"initial target temp: {AppVars.target_temp.value}")
    oled.display_image("imgs/e.pbm", False)
    time.sleep(0.1)


def update_heater_state(curr_temp, target_temp):
    """Update heater state"""
    hyst = AppVars.hysteresis.value

    if curr_temp >= target_temp + hyst:
        state = 0
    elif curr_temp <= target_temp - hyst:
        state = 1
    else:
        state = AppVars.heater_state.value

    AppVars.heater_state.set(state)
    # PINS["board_led"].value(state)
    PINS["relay"].value(state)

    print("*** change in temp or target")
    print(f"curr_temp:{AppVars.curr_temp.value} ", end=" ")
    print(f"target_temp:{AppVars.target_temp.value} ", end=" ")
    print(f"heater_state:{AppVars.heater_state.value} ***")


async def update_loop2():
    """update heater state if change is detected"""
    prev_temp_reading = 0
    prev_target = 0
    while True:
        await asyncio.sleep(DELAY)
        changed = False
        readings = utils.read_th_sensor(th_sensor)
        AppVars.curr_hum.set(readings["humidity"])

        if abs(readings["temp"] - prev_temp_reading) > 0.5:
            changed = True
            prev_temp_reading = readings["temp"]
            AppVars.curr_temp.set(readings["temp"])

        set_target_temperature()
        if AppVars.target_temp.value != prev_target:
            changed = True
            prev_target = AppVars.target_temp.value

        if changed:
            changed = False
            update_heater_state(AppVars.curr_temp.value, AppVars.target_temp.value)
            webserver.wssensor(readings)
            oled.display_text(readings)


async def main():
    """Start async tasks"""
    controls.init_controls()
    task = asyncio.create_task(update_loop2())
    webserver.webserver_start()
    await task


def start():
    """Start heater controller"""
    load_settings()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("ctrl-c pressed, shutting down...")
    finally:
        print("FINALLY")
        PINS["relay"].value(0)
        oled.oled.poweroff()


sta_if = network.WLAN(network.STA_IF)
if sta_if.isconnected():
    utils.set_ntptime()
    start()
else:
    print("NO NETWORK CONNECTION. WILL NOT RUN")
    print("Check WIFI_SSID and WIFI_PASSWORD are correct in secret.py")
