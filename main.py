import time
import network
import uasyncio as asyncio

from common import PINS, SETTINGS_FILE, WEBSERVER_PORT, MQTT_BROKER_ADDRESS, LOG_FILE, EPOCH_ADJUSTMENT
import utils
from utils import AppVars

import devices
import controls
from umqtt.simple import MQTTClient

from check_schedule import check_schedule
import webserver

DELAY = 5
devices = devices.i2cDevices()


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

    initial_readings = utils.read_th_sensor(devices.th_sensor)
    AppVars.curr_temp.set(initial_readings["temp"])
    AppVars.curr_hum.set(initial_readings["humidity"])

    set_target_temperature()

    print(f"initial temp: {AppVars.curr_temp.value}")
    print(f"initial humidity: {AppVars.curr_hum.value}")
    print(f"initial target temp: {AppVars.target_temp.value}")
    devices.oled.display_image("imgs/e.pbm", False)
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


async def update_loop():
    """update heater state if change is detected"""
    prev_temp_reading = 0
    prev_target = 0
    while True:
        await asyncio.sleep(DELAY)
        changed = False
        readings = utils.read_th_sensor(devices.th_sensor)
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
            # devices.oled.display_text(readings, nw_addr=sta_if.ifconfig()[0])
            mqtt_publish()
            update_display()
            await log_append(LOG_FILE, f"{time.time()+EPOCH_ADJUSTMENT},{readings['temp']:.1f},{readings['humidity']:.1f}")


# self.oled.text(f"T:{t:.1f}F   H:{h:.1f}%", 0, 0)
# self.oled.text(f"HEAT: {hs}", 0, 9)
# self.oled.text(f"TARGET: {AppVars.target_temp.value:.1f}", 0, 20)
# self.oled.text(f"{us}", 0, 30)
# self.oled.text(f"{nw_addr}", 0, 47)
# self.oled.text(f"PORT {WEBSERVER_PORT}", 0, 56)


def mqtt_publish():
    mqtt_client.publish(
        "esp32c3_thermostat/temperature", msg=b"%f" % AppVars.curr_temp.value
    )
    mqtt_client.publish(
        "esp32c3_thermostat/humidity", msg=b"%f" % AppVars.curr_hum.value
    )
    mqtt_client.publish(
        "esp32c3_thermostat/target_temp", msg=b"%f" % AppVars.target_temp.value
    )


def update_display():
    """max 16 characters wide"""
    hs = " HEAT:ON" if AppVars.heater_state.value else "HEAT:OFF"
    s_or_m = "SCHEDULE" if AppVars.use_heatschedule.value else "  MANUAL"
    lines = [
        f"T:{AppVars.curr_temp.value:.1f}F {hs}",
        f"H:{AppVars.curr_hum.value:.1f}% {utils.formatted_time(utils.adjusted_time())}",
        f"SET:{AppVars.target_temp.value:.0f}  {s_or_m}",
        "",
        "",
        f"{utils.nw_addr}",
        f"PORT {WEBSERVER_PORT}",
    ]
    devices.oled.display_lines(lines)


async def log_append(file, msg):
    with open(file, "a") as f:
        f.write(f"{msg}\n")
    print(f"log_append({msg})")
    await asyncio.sleep(0.1)


async def main():
    """Start async tasks"""
    controls.init_controls()
    event_loop = asyncio.get_event_loop()

    event_loop.create_task(update_loop())
    webserver.webserver_start()
    event_loop.run_forever()


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
        devices.oled.oled.poweroff()


mqtt_client = MQTTClient("thermosvelteESP32", MQTT_BROKER_ADDRESS)
sta_if = network.WLAN(network.STA_IF)
if sta_if.isconnected():
    utils.set_ntptime()
    mqtt_client.connect()
    start()
else:
    print("NO NETWORK CONNECTION. WILL NOT RUN")
    print("Check WIFI_SSID and WIFI_PASSWORD are correct in secret.py")
