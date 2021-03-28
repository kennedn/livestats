#!/usr/bin/env python3
import psutil


def get():
    used = psutil.virtual_memory().used / (1024 ** 3)
    total = psutil.virtual_memory().total / (1024 ** 3)
    percent = used / total
    # return "{:.1f}GB / {:.1f}GB ({:.2f}%)".format(used, total, percent)
    return (percent, "{:.2f}GB / {:.2f}GB ({:.0f}%)".format(used, total, int(percent * 100)))


if __name__ == '__main__':
    print(get())
