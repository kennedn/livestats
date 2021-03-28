#!/usr/bin/env python3
from datetime import datetime
from math import floor
import psutil


# Format timedelta into a dictionary that represents each unit of time
# rolling into each other
def _format_timedelta(value):
    # get raw seconds if passed a timedelta object
    if hasattr(value, 'seconds'):
        seconds = value.seconds + value.days * 24 * 3600
    else:
        seconds = int(value)

    minutes = int(floor(seconds / 60))
    seconds -= minutes * 60

    hours = int(floor(minutes / 60))
    minutes -= hours * 60

    days = int(floor(hours / 24))
    hours -= days * 24

    years = int(floor(days / 365))
    days -= years * 365

    return {
        'y': years,
        'd': days,
        'h': hours,
        'm': minutes,
        's': seconds
    }


def get():
    sysd_uptime = datetime.fromtimestamp(psutil.boot_time())
    td = datetime.now() - sysd_uptime
    format_td = _format_timedelta(td)

    return " ".join('{}{}'.format(v, k) for k, v in format_td.items() if v != 0)


if __name__ == '__main__':
    print(get())
