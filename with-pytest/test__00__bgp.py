import pytest
from genie.utils import Dq


def name_test(item):
    return f"bgp neighbor {item}"


def pytest_generate_tests(metafunc):

    device = metafunc.config._net_device
    output = device.remote_conn.send_command('show bgp ipv4 unicast summary', use_genie=True)
    device.data['bgp_ipv4_unicast_summary'] = output

    metafunc.parametrize('neighbor',
                         Dq(output).get_values('neighbor'),
                         ids=name_test
                         )


def test_bgp_summary(device,neighbor):
    
    bgp_ipv4_unicast_summary = device.data['bgp_ipv4_unicast_summary']
    state_pfxrcd = Dq(bgp_ipv4_unicast_summary).contains(neighbor).get_values('state_pfxrcd')[0]

    if state_pfxrcd in ['Idle','Active']:
        pytest.fail(f'Inactive neighbor.')

    elif state_pfxrcd == '0':
        pytest.fail(f'Neighbor up, but no prefixes received.')
        
    return True
    
