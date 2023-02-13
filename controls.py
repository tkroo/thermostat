"""Physical controls"""
import time
from common import SETTINGS_FILE
from utils import AppVars, save_current_schedule


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
