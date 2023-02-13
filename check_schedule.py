# pylint: disable=line-too-long
"""
Functions for checking if current time is between start and end of periods in heating_schedule.json
"""
import time
import re
from utils import adjusted_time


def convert_to_24(time_str):
    """convert 12 hour time to 24 hour time"""
    time_str = time_str.strip().lower()
    hm = time_str.split(":")
    hrs = int(hm[0])
    mins = int(re.sub(" *[am|pm]", "", hm[1])) if len(hm) == 2 else 0

    if "am" in time_str:
        if hrs == 12:
            return [0, mins]
        else:
            return [hrs, mins]
    elif "pm" in time_str:
        if hrs == 12:
            return [hrs, mins]
        else:
            return [hrs + 12, mins]
    else:
        return [hrs, mins]


def is_between(start_time, end_time):
    """returns true if now is between start_time and end_time
    time.localtime tuple looks like this:
    (year, month, mday, hour, minute, second, weekday, yearday)
    I think weekday array is
    0=Mon, 1=Tue, 2=Wed, 3=Thur, 4=Fri, 5=Sat, 6=Sun
    """
    nt = adjusted_time()
    now_seconds = time.mktime(nt)
    st24 = convert_to_24(start_time)
    et24 = convert_to_24(end_time)

    st_seconds = time.mktime((nt[0], nt[1], nt[2], st24[0], st24[1], 0, nt[6], nt[7]))
    et_seconds = time.mktime((nt[0], nt[1], nt[2], et24[0], et24[1], 0, nt[6], nt[7]))

    return st_seconds <= now_seconds <= et_seconds


def check_schedule(data):
    """load schedule.json and check if current time is between start and end of periods"""
    # todays_periods = data['days'][adjusted_time()[6]]['periods']
    todays_periods = data[adjusted_time()[6]]["periods"]
    matches = [p["temp"] for p in todays_periods if is_between(p["start"], p["end"])]
    output = float(matches[0]) if len(matches) > 0 else 0
    # print(f"{output=}")
    return output
