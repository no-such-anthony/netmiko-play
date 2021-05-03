import pytest
from genie.utils import Dq


@pytest.fixture(scope='module')
def bgp_ipv4_unicast_summary(device):
    return device.remote_conn.send_command('show bgp ipv4 unicast summary', use_genie=True)


def name_test(item):
    return f"bgp neighbor {item}"


def pytest_generate_tests(metafunc):
    #Not sure how best to do this, using wrapped as suggested at
    #https://github.com/pytest-dev/pytest/issues/6374

    b = bgp_ipv4_unicast_summary.__wrapped__(metafunc.config._net_device)

    metafunc.parametrize('neighbor',
                         Dq(b).get_values('neighbor'),
                         ids=name_test
                         )


def test_bgp_summary(device,bgp_ipv4_unicast_summary,neighbor):
    state_pfxrcd = Dq(bgp_ipv4_unicast_summary).contains(neighbor).get_values('state_pfxrcd')[0]

    if state_pfxrcd in ['Idle','Active']:
        pytest.fail(f'Inactive neighbor.')

    elif state_pfxrcd == '0':
        pytest.fail(f'Neighbor up, but no prefixes received.')
        
    return True
    
