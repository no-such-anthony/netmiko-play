#!/usr/bin/env python

#from netmiko import ConnectHandler
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException

from datetime import datetime
from pprint import pprint
#import sys
#import time
#import re
#import os

from netup import net_runner, get_devices


def another_task(a_device):

    # grab the netmiko object if required
    #remote_conn = a_device['netmiko']
    return None


def run_task(a_device):

    host = a_device['host']
    a_result = {}
    a_result['result'] = 'happy as larry'

    # do this when ever you are ready to open connection
    remote_conn = ConnectHandler(**a_device['conn'])
    a_device['netmiko'] = remote_conn

    #remote_conn.enable()
    data = remote_conn.send_command('show running-config')

    another_task(a_device)

    a_device['data']['fred'] = 'fred was here!'
    a_device['config'] = data

    remote_conn.disconnect()

    return a_result



def main():

    net_devices = get_devices()

    start_time = datetime.now()

    results = net_runner(run_task, net_devices)
    
    elapsed_time = datetime.now() - start_time

    print(f"\nTotal Elapsed time: {format(elapsed_time)}")
    print('\n--- Host task times ---')
    for a_result in results:
        if 'exception' in a_result:
            print(f"{a_result['host']} - Failed")
        else:
            print(f"{a_result['host']} - {a_result['result']}")   
    print(f"\nTotal Elapsed time: {format(elapsed_time)}")

    #pprint(results)
    #pprint(net_devices)


if __name__ == "__main__":
    main()
