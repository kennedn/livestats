from kubernetes import client, config
import json
from datetime import datetime, timezone
from math import floor

try:
    config.load_incluster_config()
except config.ConfigException:
    try:
        config.load_kube_config()
    except config.ConfigException:
        raise Exception("Could not configure kubernetes python client")

core = client.CoreV1Api()
default_interface = 'enp0s25'
default_interface_speed = 1000.00

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




def get_cpu(stats_json, max_json, last_data=None):
    time = stats_json['cpu']['time']
    
    if last_data is not None and time == last_data['time']:
        return last_data

    max_cpu = int(max_json['cpu']) * 1000000000  # Convert to nanocores
    cpu = stats_json['cpu']['usageNanoCores']

    return {
            'float': cpu / max_cpu, 
            'str': f"{cpu / max_cpu * 100:.02f}%", 
            'time': time
           }
    

def get_memory(stats_json, max_json, last_data=None):
    time = stats_json['memory']['time']
    
    if last_data is not None and time == last_data['time']:
        return last_data
        
    max_memory = int(max_json['memory'][:-2]) * 1024  # Convert to B
    memory = stats_json['memory']['workingSetBytes']

    return {
            'float': memory / max_memory,
            'str': f"{memory / 1024 / 1024 / 1024:.02f}GB / {max_memory / 1024 / 1024 / 1024:.02f}GB ({memory / max_memory * 100:.0f}%)",
            'time': time
           }
    
def get_network(stats_json, max_json, last_data=None):
    time = stats_json['network']['time']

    if last_data is not None and time == last_data['time']:
        return last_data

    interface = next(i for i in stats_json['network']['interfaces'] if i['name'] == default_interface)
    download = interface['rxBytes']
    upload  = interface['txBytes']

    if last_data is None:
        return {
                 'download': {
                     'float': 0.00,
                     'str': "0.00Mb / 1000.00Mb (0%)",
                     'prev': download
                  },
                 'upload': {
                     'float': 0.00,
                     'str': "0.00Mb / 1000.00Mb (0%)",
                     'prev': upload
                  },
                 'time': time
               }

    t1 = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z")
    t2 = datetime.strptime(last_data['time'], "%Y-%m-%dT%H:%M:%S%z")
    time_delta = (t1 - t2).seconds

    download_delta = (interface['rxBytes'] - last_data['download']['prev']) / 1024 / 1024 * 8 / time_delta
    download_str = f"{download_delta:.02f}Mb / {default_interface_speed:.02f}Mb ({download_delta / default_interface_speed * 100:.0f}%)"
    upload_delta = (interface['txBytes'] - last_data['upload']['prev'])/ 1024 / 1024 * 8 / time_delta
    upload_str = f"{upload_delta:.02f}Mb / {default_interface_speed:.02f}Mb ({upload_delta / default_interface_speed * 100:.0f}%)"

    return {
            'download': {
                 'float': download_delta / default_interface_speed,
                 'str': download_str,
                 'prev': download
              },
            'upload': {
                 'float': upload_delta / default_interface_speed,
                 'str': upload_str,
                 'prev': upload
              },
             'time': time
           }

def get_uptime(stats_json):
    d1 = datetime.strptime(stats_json['startTime'], "%Y-%m-%dT%H:%M:%S%z")
    d2 = datetime.now(timezone.utc)
    format_td = _format_timedelta(d2 - d1)

    uptime =  " ".join('{}{}'.format(v, k) for k, v in format_td.items() if v != 0)
    return {
             'str': uptime
           }

def get_node_stats(last_data=None, node=None):
    if node is None:
        node_json = json.loads(core.list_node(_preload_content=False).data)['items'][0]
        node = node_json['metadata']['name']

    if last_data is None:
        last_data = {}

    max_json = json.loads(core.read_node(name=node, _preload_content=False).data)['status']['allocatable']
    summary_json = json.loads(core.connect_get_node_proxy_with_path(name=node, path='stats/summary', _preload_content=False).data)
    stats_json = summary_json['node']
    
    return {
            "cpu": get_cpu(stats_json, max_json, last_data.get("cpu", None)),
            "memory": get_memory(stats_json, max_json, last_data.get("memory", None)),
            "network": get_network(stats_json, max_json, last_data.get("network", None)),
            "uptime": get_uptime(stats_json),
            "pods": {"str": len([p for p in summary_json['pods'] if p['podRef']['namespace'] == 'default'])}
           }
    
if __name__ == "__main__":
    from time import sleep
    last_data = None
    while True:
        last_data = get_node_stats(last_data=last_data)

        status_data = {'cpu': last_data['cpu']['float'],
                       'cpu_h': last_data['cpu']['str'],
                       'memory': last_data['memory']['float'],
                       'memory_h': last_data['memory']['str'],
                       'uptime': last_data['uptime']['str'],
                       'pods': last_data['pods']['str'],
                       'download': last_data['network']['download']['float'],
                       'download_h': last_data['network']['download']['str'],
                       'upload': last_data['network']['upload']['float'],
                       'upload_h':last_data['network']['upload']['str']
                       }


        print(json.dumps(status_data, indent=2))
        sleep(10)

