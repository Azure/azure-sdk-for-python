from azure.mgmt.network import NetworkManagementClient, models
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import pytest

def get_client(api_version: Optional[str] = None):
    return NetworkManagementClient("1", DefaultAzureCredential(), api_version=api_version)

def _passes(callable, *params, **kwargs):
    with pytest.raises(HttpResponseError) as ex:
        callable(*params, **kwargs)
    assert ex.value.status_code == 400

def test_operation_group_valid():
    with get_client() as client:
        _passes(client.express_route_ports_locations.get, "1")

def test_operation_group_not_added_yet():
    with get_client("2015-06-15") as client:
        with pytest.raises(ValueError) as ex:
            client.express_route_ports_locations.get("1")
        assert "'express_route_ports_locations' is not available in API version 2015-06-15. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

def test_operation_group_removed():
    with get_client() as client:
        _passes(client.interface_endpoints.get, "1", "2")  # passes bc of profile logic

    with get_client(api_version="2022-05-01") as client:
        with pytest.raises(ValueError) as ex:
            client.interface_endpoints.get("1", "2")
        assert "'interface_endpoints' is not available in API version 2022-05-01. Pass service API version 2018-08-01 or newer to your client." in str(ex.value)

def test_operation_group_operation_not_added_yet():
    with get_client() as client:
        _passes(client.application_gateways.list_available_request_headers)

    with get_client(api_version="2015-06-15") as client:
        with pytest.raises(ValueError) as ex:
            client.application_gateways.list_available_request_headers()
        assert str(ex.value) == "'list_available_request_headers' is not available in API version 2015-06-15. Pass service API version 2018-11-01 or newer to your client."

def test_operation_group_operation_valid():
    with get_client() as client:
        _passes(client.application_gateways.get, "1", "2")

def test_operation_group_operation_removed():
    with get_client() as client:
        with pytest.raises(ValueError) as ex:
            client.application_gateways.begin_update_tags("1", "2")
        assert str(ex.value) == "'begin_update_tags' is not available in API version 2022-05-01. Pass service API version 2017-10-01 or newer to your client."

    with get_client(api_version="2017-10-01") as client:
        _passes(client.application_gateways.begin_update_tags, "1", "2", models.TagsObject())

def test_mixin_operation_not_added_yet():
    with get_client(api_version="2018-07-01") as client:
        with pytest.raises(ValueError) as ex:
            client.supported_security_providers("1", "2")
        assert str(ex.value) == "'supported_security_providers' is not available in API version 2018-07-01. Pass service API version 2018-08-01 or newer to your client."
    with get_client() as client:
        _passes(client.supported_security_providers, "1", "2")

def test_mixin_operation_valid():
    with get_client() as client:
        _passes(client.check_dns_name_availability, "1", domain_name_label="2")
    with get_client(api_version="2015-06-15") as client:
        _passes(client.check_dns_name_availability, "1", domain_name_label="2")

def test_mixin_operation_removed():
    with get_client() as client:
        _passes(client.check_dns_name_availability, "1", domain_name_label="2")

    with get_client(api_version="2021-02-01-preview") as client:
        with pytest.raises(ValueError) as ex:
            client.check_dns_name_availability("1", domain_name_label="2")
        assert str(ex.value) == "'check_dns_name_availability' is not available in API version 2021-02-01-preview. Pass service API version 2015-06-15 or newer to your client."

def test_parameter_not_added_yet():
    with get_client() as client:
        _passes(client.virtual_network_peerings.begin_create_or_update, "1", "2", "3", models.VirtualNetworkPeering(), sync_remote_address_space="4")

    with get_client(api_version="2015-06-15") as client:
        with pytest.raises(ValueError) as ex:
            client.virtual_network_peerings.begin_create_or_update("1", "2", "3", models.VirtualNetworkPeering(), sync_remote_address_space="4")
        assert str(ex.value) == "'virtual_network_peerings' is not available in API version 2015-06-15. Pass service API version 2016-09-01 or newer to your client."

def test_parameter_valid():
    ...
