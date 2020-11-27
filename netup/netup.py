from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback


def net_wrapper(net_task, a_device):

    a_result = {}
    a_result['host'] = a_device['host']

    try:
        a_result['result'] = net_task(a_device)

    except Exception as e:
        a_result['exception'] = e
        a_result['traceback'] = traceback.format_exc()

    return a_result


def net_runner(net_task, net_devices):
    results = []  
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(net_wrapper, net_task, a_device): a_device for a_device in net_devices.values()}
        for future in as_completed(futures):
            a_result = future.result() 
            results.append(a_result) 
            if 'exception' in a_result:
                print(f"{a_result['host']} - {a_result['traceback']}")
            else:
                print(f"{a_result['host']} - complete")

    return results


def get_devices():

    devices = ['no.suchdomain','192.168.204.101','192.168.204.102','192.168.204.103','192.168.204.104']
    #devices = ['no.suchdomain','192.168.204.101']

    net_devices = {}
    for hostname in devices:
        a_device={}

        c = {}
        c['host']=hostname
        c['device_type']='cisco_ios'
        c['username']='fred'
        c['password']='bedrock'
        c['secret']=''
        c['port']=22

        a_device['data']={}
        a_device['conn']=c
        a_device['host']=hostname

        net_devices[hostname]=a_device

    return net_devices

