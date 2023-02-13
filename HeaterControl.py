"""
Heater control class. Should just be functions in main.py and not a class?
"""
import time
import uasyncio as asyncio
from machine import SoftI2C

from common import PINS, SETTINGS_FILE
import display
import lib.shtc3 as shtc3
from lib.abutton import Pushbutton
import controls

from utils import (
    AppVars,
    read_shtc3_sensor,
    load_json,
)
from check_schedule import check_schedule
import webserver

i2c = SoftI2C(scl=PINS["scl"], sda=PINS["sda"])
display = display.Oled_Display(i2c)
th_sensor = shtc3.SHTC3_I2C(i2c)
th_sensor.shtc3_init()


class HeaterControl:
    """Class representing heater controller"""

    def __init__(self):
        self.delay = 5
        self.prev_temp_reading = 0
        self.prev_target = 0

    async def update_loop2(self):
        """update heater state if change is detected"""
        while True:
            await asyncio.sleep(self.delay)
            changed = False
            readings = read_shtc3_sensor(th_sensor)
            AppVars.curr_hum.set(readings["humidity"])

            if abs(readings["temp"] - self.prev_temp_reading) > 0.5:
                changed = True
                self.prev_temp_reading = readings["temp"]
                AppVars.curr_temp.set(readings["temp"])

            HeaterControl.set_target_temperature()
            if AppVars.target_temp.value != self.prev_target:
                changed = True
                self.prev_target = AppVars.target_temp.value

            if changed:
                changed = False
                HeaterControl.update_heater_state(
                    AppVars.curr_temp.value, AppVars.target_temp.value
                )
                display.display_text(readings)


    @staticmethod
    def update_heater_state(curr_temp, target_temp):
        """Update heater state"""
        h = AppVars.hysteresis.value

        if curr_temp >= target_temp + h:
            state = 0
        elif curr_temp <= target_temp - h:
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

    @staticmethod
    def set_target_temperature():
        """Function to set target temperature"""
        if AppVars.use_heatschedule.value:
            check = check_schedule(load_json(SETTINGS_FILE)["days"])
            AppVars.schedule_temp.set(check if check else AppVars.minimum_temp.value)
            temp = AppVars.schedule_temp.value
        else:
            temp = AppVars.manual_temp.value
        AppVars.target_temp.set(temp)

    @staticmethod
    def load_settings():
        """Function to load and assign some values from settings file"""
        print(f"Loading {SETTINGS_FILE}...")
        data = load_json(SETTINGS_FILE)
        AppVars.use_heatschedule.set(data["use_heatschedule"])
        AppVars.hysteresis.set(data["hysteresis"])
        AppVars.use_oled.set(data["use_oled"])
        AppVars.minimum_temp.set(data["minimum_temp"])
        AppVars.manual_temp.set(data["saved_manual_temp"])

        initial_readings = read_shtc3_sensor(th_sensor)
        AppVars.curr_temp.set(initial_readings["temp"])
        AppVars.curr_hum.set(initial_readings["humidity"])

        HeaterControl.set_target_temperature()

        print(f"initial temp: {AppVars.curr_temp.value}")
        print(f"initial humidity: {AppVars.curr_hum.value}")
        print(f"initial target temp: {AppVars.target_temp.value}")
        display.display_image("imgs/e.pbm", False)
        time.sleep(0.1)

    @staticmethod
    def init_controls():
        """initialize physical buttons"""
        but1 = Pushbutton(PINS["temp_up"])
        but2 = Pushbutton(PINS["temp_down"])
        but3 = Pushbutton(PINS["toggle"])
        but1.long_func(controls.temp_up, (4,))
        but1.press_func(controls.temp_up, (1,))
        but2.long_func(controls.temp_down, (4,))
        but2.press_func(controls.temp_down, (1,))
        but3.press_func(controls.toggle_use_schedule, (0,))


    async def main(self):
        """Start async tasks"""
        HeaterControl.init_controls()
        task = asyncio.create_task(self.update_loop2())
        webserver.webserver_start()
        await task

    def start(self):
        """Start heater controller"""
        HeaterControl.load_settings()
        try:
            asyncio.run(self.main())
        except KeyboardInterrupt:
            print("ctrl-c pressed, shutting down...")
        finally:
            print("FINALLY")
            PINS["relay"].value(0)
            display.oled.poweroff()
