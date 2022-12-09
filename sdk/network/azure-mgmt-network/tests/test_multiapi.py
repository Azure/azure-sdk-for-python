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
    assert "2015-06-15 does not have operation group 'express_route_ports_locations'" in str(ex.value)

def test_operation_group_removed():
    _passes(get_client().interface_endpoints.get, "1", "2")  # passes bc of profile logic
    with pytest.raises(ValueError) as ex:
        get_client(api_version="2022-05-01").interface_endpoints.get("1", "2")
    assert "2022-05-01 does not have operation group 'interface_endpoints'" in str(ex.value)

def test_operation_group_operation_not_added_yet():
    ...

def test_operation_group_operation_valid():
    ...

def test_operation_group_operation_removed():
    ...

def test_mixin_operation_not_added_yet():
    ...

def test_mixin_operation_valid():
    ...

def test_mixin_operation_removed():
    ...
