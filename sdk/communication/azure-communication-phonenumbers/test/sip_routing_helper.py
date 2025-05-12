# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uuid
import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient
from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient as AsyncSipRoutingClient
from _shared.utils import get_http_logging_policy, get_header_policy, parse_connection_str, async_create_token_credential, create_token_credential

from devtools_testutils import is_live

def get_test_domain():
    if is_live():
        return _get_root_domain()
    return "sanitized.com"

def get_unique_fqdn(trunkId):
    if is_live():
        return trunkId + "-" + uuid.uuid4().hex + "." + _get_root_domain()
    return trunkId + ".sanitized.com"

def assert_domains_are_equal(response_domains, request_domains):
    assert len(response_domains) == len(request_domains), "Length of domain list doesn't match."

    for k in range(len(request_domains)):
        assert response_domains[k].fqdn == request_domains[k].fqdn, "Domain FQDNs don't match."
        assert (
            response_domains[k].enabled == request_domains[k].enabled
        ), "Enabled fields don't match."

def assert_trunks_are_equal(response_trunks, request_trunks):
    assert len(response_trunks) == len(request_trunks), "Length of trunk list doesn't match."

    for k in range(len(request_trunks)):
        assert response_trunks[k].fqdn == request_trunks[k].fqdn, "Trunk FQDNs don't match."
        assert (
            response_trunks[k].sip_signaling_port == request_trunks[k].sip_signaling_port
        ), "SIP signaling ports don't match."
        assert (
            response_trunks[k].enabled == request_trunks[k].enabled
        ), "Enabled fields don't match."
        assert (
            response_trunks[k].direct_transfer == request_trunks[k].direct_transfer
        ), "DirectTransfer fields don't match."
        assert (
            response_trunks[k].privacy_header == request_trunks[k].privacy_header
        ), "PrivacyHeader fields don't match."
        assert (
            response_trunks[k].ip_address_version == request_trunks[k].ip_address_version
        ), "IpAddressVersion fields don't match."
        
def assert_routes_are_equal(response_routes, request_routes):
    assert len(response_routes) == len(request_routes)

    for k in range(len(request_routes)):
        assert request_routes[k].name == response_routes[k].name, "Names don't match."
        assert request_routes[k].description == response_routes[k].description, "Descriptions don't match."
        assert request_routes[k].number_pattern == response_routes[k].number_pattern, "Number patterns don't match."
        assert len(request_routes[k].trunks) == len(response_routes[k].trunks), "Trunk lists length doesn't match."
        for m in range(len(request_routes[k].trunks)):
            assert request_routes[k].trunks[m] == response_routes[k].trunks[m], "Trunk lists don't match."


def setup_configuration(connection_str, trunks=[], routes=[]):
    if is_live():
        client = SipRoutingClient.from_connection_string(
            connection_str, http_logging_policy=get_http_logging_policy(), header_policy=get_header_policy()
        )
        client.set_routes(routes)
        client.set_trunks(trunks)


def _get_root_domain():
    return os.getenv("AZURE_TEST_DOMAIN", "testdomain.com")

def get_async_sip_client_managed_identity(connection_str):
    endpoint, *_ = parse_connection_str(connection_str)
    credential = async_create_token_credential()
    return AsyncSipRoutingClient(
        endpoint, credential, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
)
    
def get_sip_client_managed_identity(connection_str):
    endpoint, *_ = parse_connection_str(connection_str)
    credential = create_token_credential()
    return SipRoutingClient(
        endpoint, credential, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
)
    
async def get_as_list_async(iter):
    assert iter is not None, "No iterable was returned."
    items = []
    async for item in iter:
        items.append(item)
    return items

def get_as_list(iter):
    assert iter is not None, "No iterable was returned."
    items = []
    for item in iter:
        items.append(item)
    return items
