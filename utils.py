# pylint: disable=too-few-public-methods, broad-except, line-too-long
"""
Misc utility functions and some globals for the project.
"""
import json
import time
import network
import machine
import ntptime
from common import SENSOR_TYPE

# from umqtt.simple import MQTTClient

# client = MQTTClient("thermosvelteESP32", "192.168.1.35")
# client.connect()


sta_if = network.WLAN(network.STA_IF)
nw_addr = sta_if.ifconfig()[0]


class MyFloat:
    """
    Class to represent a float value
    and call a function when a change is detected
    """

    def __init__(self, value=0.0):
        self.value = value

    def set(self, value):
        """Function to set float value"""
        self.value = float(value)
        time.sleep_ms(1)


class MyBool:
    """Class to represent a boolean"""

    def __init__(self, value=False):
        self.value = value

    def set(self, value):
        """Function to set the value of the boolean."""
        self.value = value
        time.sleep_ms(1)


class AppVars:
    """Class to store app global values"""

    curr_temp = MyFloat()
    curr_hum = MyFloat()
    target_temp = MyFloat()
    manual_temp = MyFloat()
    schedule_temp = MyFloat()
    heater_state = MyBool()
    use_heatschedule = MyBool()
    minimum_temp = MyFloat()
    hysteresis = MyFloat()
    use_oled = MyBool()
    update_trigger = 0


def read_shtc3_sensor(sensor):
    """read the shtc3 sensor"""
    try:
        readings = sensor.get_temperature_humidity()
        return {"temp": c2f(readings["temp"]), "humidity": readings["humidity"]}
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return {"temp": 99, "humidity": 0}

def read_dhtXX_sensor(sensor):
    try:
        sensor.measure()
        return {"temp": c2f(sensor.temperature()), "humidity": sensor.humidity()}
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return {"temp": 99, "humidity": 0}


def read_th_sensor(sensor):
    """read the shtc3 sensor"""
    if SENSOR_TYPE == "shtc3":
        return read_shtc3_sensor(sensor)
    else:
        return read_dhtXX_sensor(sensor)


def load_json(file_name):
    """load json file"""
    with open(file_name, "r") as f:
        data = json.load(f)
    return data


def save_json(file_name, data):
    """write data to json file"""
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f)


def c2f(c):
    """convert celsius to fahrenheit"""
    return c * 1.80 + 32


def f2c(f):
    """convert fahrenheit to celsius"""
    return (f - 32) / 1.80


def save_schedule(file_name, data):
    """write to heating_schedule.json"""
    save_json(file_name, data)
    AppVars.use_heatschedule.value = data["use_heatschedule"]
    AppVars.hysteresis.set(data["hysteresis"])
    AppVars.use_oled.set(data["use_oled"])
    AppVars.minimum_temp.set(data["minimum_temp"])


year = time.localtime()[0]  # get current year
DST_begins = time.mktime(
    (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 2, 0, 0, 0, 0, 0)
)  # Time of March change to PDT
DST_ends = time.mktime(
    (year, 11, (31 - (int(5 * year / 4 + 1)) % 7), 2, 0, 0, 0, 0, 0)
)  # Time of November change to PST

# (year, month, mday, hour, minute, second, weekday, yearday)
def adjusted_time():
    """returns PST time with daylight savings adjustment"""
    # In PST timezone daylight savings starts Sunday March, 12 at 2:00AM and ends Sunday November 5 at 2:00AM
    now = time.time()
    if now < DST_begins:  # we are before second sunday of march
        pst = time.localtime(now - (3600 * 8))  # PST:  UTC-8H
    elif now < DST_ends:  # we are before first sunday of november
        pst = time.localtime(now - (3600 * 7))  # PDT: UTC-7H
    else:  # we are after first sunday of november
        pst = time.localtime(now - (3600 * 8))  # PST:  UTC-8H
    return pst



def formatted_date(st):
    return f"{st[0]}-{st[1]:02d}-{st[2]:02d} {st[3]:2}:{st[4]:02d}:{st[5]:02d}"


def formatted_time(st):
    """format time object to string"""
    hour = st[3]
    minutes = st[4]
    ampm = "AM" if hour < 12 else "PM"
    hour %= 12
    return f"12:{minutes} {ampm}" if hour == 0 else f"{hour}:{minutes} {ampm}"
    # return f"{st[0]}-{st[1]:02d}-{st[2]:02d} {st[3]:2}:{st[4]:02d}:{st[5]:02d}"


# def convert12(hour, minutes):
#     ampm = "AM" if hour < 12 else "PM"
#     hour %= 12
#     return f"12:{minutes} {ampm}" if hour == 0 else f"{hour}:{minutes} {ampm}"


def set_ntptime():
    """Set NTP time"""
    ntptime.timeout = 2
    try:
        ntptime.settime()
    except Exception as e:
        # """ERROR - ntptime.settime() error: [Errno 116] ETIMEDOUT"""
        print(f"ERROR - ntptime.settime() error: {e}")
        set_ntptime()


def print_pins():
    allpins = [2, 3, 4, 5, 6, 7, 21, 20, 8, 9, 10]
    mypins = []
    for pin in allpins:
        mypins.append(machine.Pin(pin))

    for pin in mypins:
        print(f"{pin} is {pin.value()}", end=" ")

    for pin in mypins:
        print(f"{pin.value()}", end=" ")
    print("---")
