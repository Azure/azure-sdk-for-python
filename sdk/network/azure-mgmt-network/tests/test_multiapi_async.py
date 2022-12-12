from azure.mgmt.network import aio, models
from typing import Optional
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import pytest

def get_client(api_version: Optional[str] = None):
    return aio.NetworkManagementClient("1", DefaultAzureCredential(), api_version=api_version)

@pytest.mark.asyncio
async def _passes(callable, *params, **kwargs):
    with pytest.raises(HttpResponseError) as ex:
        await callable(*params, **kwargs)
    assert ex.value.status_code == 400

@pytest.mark.asyncio
async def test_operation_group_valid():
    async with get_client() as client:
        await _passes(client.express_route_ports_locations.get, "1")

@pytest.mark.asyncio
async def test_operation_group_not_added_yet():
    async with get_client("2015-06-15") as client:
        with pytest.raises(ValueError) as ex:
            await client.express_route_ports_locations.get("1")
        assert "'express_route_ports_locations' is not available in API version 2015-06-15. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

@pytest.mark.asyncio
async def test_operation_group_removed():
    async with get_client() as client:
        await _passes(client.interface_endpoints.get, "1", "2")  # passes bc of profile logic

    async with get_client(api_version="2022-05-01") as client:
        with pytest.raises(ValueError) as ex:
            await client.interface_endpoints.get("1", "2")
        assert "'interface_endpoints' is not available in API version 2022-05-01. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

@pytest.mark.asyncio
async def test_operation_group_operation_not_added_yet():
    async with get_client() as client:
        await _passes(client.application_gateways.list_available_request_headers)

    async with get_client(api_version="2015-06-15") as client:
        with pytest.raises(ValueError) as ex:
            await client.application_gateways.list_available_request_headers()
        assert str(ex.value) == "'list_available_request_headers' is not available in API version 2015-06-15. Pass service API version 2018-11-01 or newer to your client."
@pytest.mark.asyncio
async def test_operation_group_operation_valid():
    ...

@pytest.mark.asyncio
async def test_operation_group_operation_removed():
    async with get_client() as client:
        with pytest.raises(ValueError) as ex:
            await client.application_gateways.begin_update_tags("1", "2")
        assert str(ex.value) == "'begin_update_tags' is not available in API version 2022-05-01. Pass service API version 2017-10-01 or newer to your client."

    async with get_client(api_version="2017-10-01") as client:
        await _passes(client.application_gateways.begin_update_tags, "1", "2", models.TagsObject())

@pytest.mark.asyncio
async def test_mixin_operation_not_added_yet():
    async with get_client(api_version="2018-07-01") as client:
        with pytest.raises(ValueError) as ex:
            await client.supported_security_providers("1", "2")
        assert str(ex.value) == "'supported_security_providers' is not available in API version 2018-07-01. Pass service API version 2018-08-01 or newer to your client."

    async with get_client() as client:
        await _passes(client.supported_security_providers, "1", "2")

@pytest.mark.asyncio
async def test_mixin_operation_valid():
    async with get_client() as client:
        await _passes(client.check_dns_name_availability, "1", domain_name_label="2")
    async with get_client(api_version="2015-06-15") as client:
        await _passes(client.check_dns_name_availability, "1", domain_name_label="2")
