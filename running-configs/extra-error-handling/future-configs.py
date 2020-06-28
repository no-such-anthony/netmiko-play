#!/usr/bin/env python
from concurrent.futures import ThreadPoolExecutor
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException
from datetime import datetime
import traceback
import sys
import time
import re
import os


def config_filter_cisco_ios(cfg):
    """Filter unneeded items that change from the config."""

    # Strip the header line
    header_line1_re = r"^Building configuration.*$"
    header_line2_re = r"^Current configuration.*$"
    header_line3_re = r"^!Running configuration.*$"

    # Strip the service timestamps comments
    service_timestamps1_re = r"^! Last configuration change at.*$"
    service_timestamps2_re = r"^! NVRAM config last updated at.*$"
    service_timestamps3_re = r"^! No configuration change since last restart.*$"

    # Strip misc
    misc1_re = r'^ntp clock-period.*$'
    misc2_re = r'^!Time.*$'

    for pattern in [header_line1_re, header_line2_re, header_line3_re,
                    service_timestamps1_re, service_timestamps2_re, 
                    service_timestamps3_re, misc1_re, misc2_re]:
        cfg = re.sub(pattern, "", cfg, flags=re.M).lstrip()

    return cfg


def run_task(a_device):

    try:
        host = a_device['host']
        a_result = {}
        a_result['host'] = host
        remote_conn = None
        last_exception = None
        redo_enable = False

        start_time = datetime.now()
        
        retries = 0
        while retries <= 2:
            try:
                if remote_conn is None:
                    remote_conn = ConnectHandler(device_type=a_device['device_type'],
                                            host=a_device['host'],
                                            username=a_device['username'],
                                            password=a_device['password'],
                                            port=22,
                                            secret=a_device['secret'],
                                            #fast_cli=True
                                            )
                    remote_conn.enable()

                if redo_enable == True:
                    remote_conn.enable()

                remote_conn.fast_cli = False
                data = remote_conn.send_command('show running-config')

                if len(data) < 100:
                    raise ValueError('Config unexpectedly short')

                break

            except ValueError as e:
                last_exception = e
                if 'unexpectedly short' or 'enable mode' in str(e):
                    if retries == 2:
                        raise e
                    if 'enable mode' in str(e):
                        redo_enable = True
                else:
                    raise e  

            except NetMikoTimeoutException as e:
                last_exception = e
                if 'reading channel' in str(e):
                    if retries == 2:
                        raise e         
                else:
                    raise e

            except NetMikoAuthenticationException as e:
                #Looking for cisco_nxos
                last_exception = e
                if 'cisco_nxos' in str(e):
                    if retries == 2:
                        raise e         
                else:
                    raise e

            except OSError as e:
                last_exception = e
                if 'Search pattern' in str(e):
                    if retries == 2:
                        raise e         
                else:
                    raise e

            except EOFError as e:
                last_exception = e
                if 'closed by remote device' in str(e):
                    if retries == 2:
                        raise e         
                else:
                    raise e

            except Exception as e:
                raise e         

            print(f'** {host} hit error {last_exception} - retrying...')
            time.sleep(5)
            retries += 1

        remote_conn.disconnect()

        elapsed_time_ssh = datetime.now() - start_time
        a_result['ssh_runtime'] = elapsed_time_ssh

        data = config_filter_cisco_ios(data)
        if a_device['device_type'] == 'cisco_ios':
            data = re.sub(r'^\s*$', "", data, flags=re.M)

        with open(f"configs/{host}.cfg","w") as f:
            f.write(data)

        return a_result

    except Exception as e:
        print(f'** {host} task closing with error {e}')
        a_result['exception'] = e
        a_result['traceback'] = traceback.format_exc()
        
        return a_result


def get_devices():

    devices = ['no.suchdomain','192.168.204.101','192.168.204.102','192.168.204.103','192.168.204.104']
    #devices = ['no.suchdomain','192.168.204.101']

    net_devices = {}
    for hostname in devices:
        a_device={}
        a_device['host']=hostname
        a_device['device_type']='cisco_ios'
        a_device['username']='fred'
        a_device['password']='bedrock'
        a_device['secret']=''
        net_devices[hostname]=a_device

    return net_devices


def main():

    net_devices = get_devices()
    start_time = datetime.now()

    results = []
    with ThreadPoolExecutor(4) as pool:
        results = pool.map(run_task, (a_device for a_device in net_devices.values()))

    elapsed_time = datetime.now() - start_time

    print('\n--- Host task times ---')
    for a_result in results:
        if 'exception' in a_result:
            print(f"{a_result['host']} - {a_result['exception']}")
            #print(a_result['traceback'])
        else:
            print(f"{a_result['host']} - {a_result['ssh_runtime']}")
    print(f"\nTotal Elapsed time: {format(elapsed_time)}")


if __name__ == "__main__":
    main()

