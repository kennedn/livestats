#!/usr/bin/env python3
import psutil


def get():
    percent_list = psutil.cpu_percent(interval=0.1, percpu=True)
    cpu_per = sum(percent_list) / len(percent_list) / 100
    return (cpu_per, '{:.2f}%'.format(cpu_per * 100))


if __name__ == '__main__':
    print(get())
