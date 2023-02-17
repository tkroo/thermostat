"""Physical controls"""
import time
from common import PINS, SETTINGS_FILE
from utils import AppVars, load_json, save_schedule
from lib.abutton import Pushbutton


def init_controls():
    """initialize physical buttons"""
    but1 = Pushbutton(PINS["temp_up"])
    but2 = Pushbutton(PINS["temp_down"])
    but3 = Pushbutton(PINS["toggle"])
    but1.long_func(temp_up, (4,))
    but1.press_func(temp_up, (1,))
    but2.long_func(temp_down, (4,))
    but2.press_func(temp_down, (1,))
    but3.press_func(toggle_use_schedule, (0,))


def temp_up(amount):
    """button irq callback function to raise target_temp by amount"""
    print(f"temp_up button {amount}")
    AppVars.update_trigger = time.time()
    AppVars.manual_temp.set(AppVars.manual_temp.value + amount)
    save_current_schedule(SETTINGS_FILE)


def temp_down(amount):
    """button irq callback function to raise target_temp by amount"""
    print(f"temp_down button {amount}")
    AppVars.update_trigger = time.time()
    AppVars.manual_temp.set(AppVars.manual_temp.value - amount)
    save_current_schedule(SETTINGS_FILE)


def toggle_use_schedule(_pin):
    """Toggle use_heatschedule"""
    print("toggle_use_schedule button")
    AppVars.update_trigger = time.time()
    tog = not AppVars.use_heatschedule.value
    print(f"use_heatschedule toggled from {AppVars.use_heatschedule.value} to {tog}")
    AppVars.use_heatschedule.set(tog)
    save_current_schedule(SETTINGS_FILE)


def save_current_schedule(file_name):
    """save heating_schdule.json with updated use_heatschedule"""
    data = load_json(file_name)
    data["use_heatschedule"] = AppVars.use_heatschedule.value
    data["saved_manual_temp"] = AppVars.manual_temp.value
    save_schedule(file_name, data)
