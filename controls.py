"""Physical controls"""
import time
from lib.debounce import DebouncedSwitch
from common import PINS, SETTINGS_FILE
from utils import AppVars, save_current_schedule
import micropython

micropython.alloc_emergency_exception_buf(100)


def init_controls():
    """Initialize controls"""
    but1 = DebouncedSwitch(PINS["temp_up"], temp_up, 1, delay=100)
    but2 = DebouncedSwitch(PINS["temp_down"], temp_down, 1, delay=100)
    but3 = DebouncedSwitch(PINS["toggle"], toggle_use_schedule, delay=100)


def temp_up(amount):
    """button irq callback function to raise target_temp by amount"""
    print("temp_up button")
    AppVars.update_trigger = time.time()
    AppVars.manual_temp.set(AppVars.manual_temp.value + amount)


def temp_down(amount):
    """button irq callback function to raise target_temp by amount"""
    print("temp_down button")
    AppVars.update_trigger = time.time()
    AppVars.manual_temp.set(AppVars.manual_temp.value - amount)


def toggle_use_schedule(_arg):
    """Toggle use_heatschedule"""
    print("toggle_use_schedule button")
    AppVars.update_trigger = time.time()
    tog = not AppVars.use_heatschedule.value
    print(f"use_heatschedule toggled from {AppVars.use_heatschedule.value} to {tog}")
    AppVars.use_heatschedule.set(tog)
    save_current_schedule(SETTINGS_FILE)
