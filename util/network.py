import psutil
import subprocess as shell
device = None
# Try to derive mac address from default route, will work on linux.
try:
    p = shell.Popen(["ip", "route", "list", "0/0"], stdout=shell.PIPE)
    device = shell.check_output(["grep", "-v", "tun"], stdin=p.stdout).split()[4].decode()
except Exception:
    print("Couldn't detect default device")
    exit(1)

link_speed = psutil.net_if_stats()[device].speed


def get(download=0, upload=0):
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[device]
    download_new = net_stat.bytes_recv
    upload_new = net_stat.bytes_sent

    net_in = ((download_new - download) / 1024 / 1024 * 8)
    net_out = ((upload_new - upload) / 1024 / 1024 * 8)
    net_in_per = min(1.00, net_in / link_speed)
    net_out_per = min(1.00, net_out / link_speed)
    if download != 0:
        return (download_new, upload_new, net_in_per, net_out_per,
                '{:.2f}Mb / {:.2f}Mb ({:.0f}%)'.format(net_in, link_speed, net_in_per * 100),
                '{:.2f}Mb / {:.2f}Mb ({:.0f}%)'.format(net_out, link_speed, net_out_per * 100))
    else:
        return (download_new, upload_new, 0, 0, '0 / 0 (0%)', '0 / 0 (0%)')


if __name__ == '__main__':
    print(*get())
