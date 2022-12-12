from azure.mgmt.network import NetworkManagementClient
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import pytest

def get_client(api_version: Optional[str] = None):
    return NetworkManagementClient("1", DefaultAzureCredential(), api_version=api_version)

def _passes(callable, *params):
    with pytest.raises(HttpResponseError) as ex:
        callable(*params)
    assert ex.value.status_code == 400


def test_operation_group_valid():
    _passes(get_client().express_route_ports_locations.get, "1")

def test_operation_group_not_added_yet():
    with pytest.raises(ValueError) as ex:
        get_client("2015-06-15").express_route_ports_locations.get("1")
    assert "'express_route_ports_locations' is not available in API version 2015-06-15. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

def test_operation_group_removed():
    _passes(get_client().interface_endpoints.get, "1", "2")  # passes bc of profile logic
    with pytest.raises(ValueError) as ex:
        get_client(api_version="2022-05-01").interface_endpoints.get("1", "2")
    assert "'interface_endpoints' is not available in API version 2022-05-01. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

def test_operation_group_operation_not_added_yet():
    ...

def test_operation_group_operation_valid():
    ...

def test_operation_group_operation_removed():
    ...

def test_mixin_operation_not_added_yet():
    with pytest.raises(ValueError) as ex:
        get_client(api_version="2018-07-01").supported_security_providers("1", "2")
    assert str(ex.value) == "'supported_security_providers' is not available in API version 2018-07-01. Pass service API version 2018-08-01 or newer to your client."

def test_mixin_operation_valid():
    ...

def test_mixin_operation_removed():
    ...
