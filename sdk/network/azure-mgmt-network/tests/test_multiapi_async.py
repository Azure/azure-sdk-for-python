from azure.mgmt.network.aio import NetworkManagementClient
from typing import Optional
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import pytest

def get_client(api_version: Optional[str] = None):
    return NetworkManagementClient("1", DefaultAzureCredential(), api_version=api_version)

@pytest.mark.asyncio
async def _passes(callable, *params):
    with pytest.raises(HttpResponseError) as ex:
        await callable(*params)
    assert ex.value.status_code == 400

@pytest.mark.asyncio
async def test_operation_group_valid():
    await _passes(get_client().express_route_ports_locations.get, "1")

@pytest.mark.asyncio
async def test_operation_group_not_added_yet():
    with pytest.raises(ValueError) as ex:
        await get_client("2015-06-15").express_route_ports_locations.get("1")
    assert "'express_route_ports_locations' is not available in API version 2015-06-15. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

@pytest.mark.asyncio
async def test_operation_group_removed():
    await _passes(get_client().interface_endpoints.get, "1", "2")  # passes bc of profile logic
    with pytest.raises(ValueError) as ex:
        await get_client(api_version="2022-05-01").interface_endpoints.get("1", "2")
    assert "'interface_endpoints' is not available in API version 2022-05-01. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

@pytest.mark.asyncio
async def test_operation_group_operation_not_added_yet():
    ...

@pytest.mark.asyncio
async def test_operation_group_operation_valid():
    ...

@pytest.mark.asyncio
async def test_operation_group_operation_removed():
    ...

@pytest.mark.asyncio
async def test_mixin_operation_not_added_yet():
    with pytest.raises(ValueError) as ex:
        await get_client(api_version="2018-07-01").supported_security_providers("1", "2")
    assert str(ex.value) == "'supported_security_providers' is not available in API version 2018-07-01. Pass service API version 2018-08-01 or newer to your client."
    await _passes(get_client().supported_security_providers, "1", "2")

@pytest.mark.asyncio
async def test_mixin_operation_valid():
    ...

@pytest.mark.asyncio
async def test_mixin_operation_removed():
    ...
