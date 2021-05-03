import pytest
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException


class NETDEVICEconfig(object):
    """ for NETTEST specific config / runtime """
    pass


def pytest_addoption(parser):
    parser.addoption("--device",
                     required=True,
                     help='device name or IP address')


def pytest_sessionstart(session):
    config = session.config
    config._net_device = NETDEVICEconfig()

    device_name = config.getoption("--device")
    net_devices = get_devices()

    try:
        net_device = net_devices[device_name]
    except KeyError:
        pytest.exit("Unknown device")

    try:
        remote_conn = ConnectHandler(device_type=net_device['device_type'],
                                    host=net_device['host'],
                                    username=net_device['username'],
                                    password=net_device['password'],
                                    port=22,
                                    secret=net_device['secret'],
                                    fast_cli=False
                                    )
        if net_device['secret']:
            remote_conn.enable()

    except NetMikoTimeoutException as e:
        pytest.exit("Connection Timeout")

    except NetMikoAuthenticationException as e:
        pytest.exit("Authentication problem")

    config._net_device.remote_conn = remote_conn
    config._net_device.platform = net_device['device_type']
    config._net_device.host = net_device['host']
    config._net_device.data = {}


def pytest_sessionfinish(session):
    config = session.config
    config._net_device.remote_conn.disconnect()


@pytest.fixture(scope='session')
def device(request):
    return request.config._net_device


def get_devices():

    devices = ['192.168.204.101','192.168.204.102','192.168.204.103','192.168.204.104']

    net_devices = {}
    for hostname in devices:
        net_device={}
        net_device['host']=hostname
        net_device['device_type']='cisco_ios'
        net_device['username']='fred'
        net_device['password']='bedrock'
        net_device['secret']=''
        net_device['data']={}
        net_devices[hostname]=net_device

    return net_devices

