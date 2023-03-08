# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uuid
import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient
from _shared.utils import get_http_logging_policy

from devtools_testutils import is_live

def get_unique_fqdn(trunkId):
    if(is_live()):
        return trunkId + "-" + uuid.uuid4().hex + "." + _get_root_domain()
    return trunkId + ".sanitized.com"

def assert_trunks_are_equal(response_trunks, request_trunks):
    assert len(response_trunks) == len(request_trunks), "Length of trunk list doesn't match."

    for k in range(len(request_trunks)):
        assert response_trunks[k].fqdn == request_trunks[k].fqdn, "Trunk FQDNs don't match."
        assert (
            response_trunks[k].sip_signaling_port==request_trunks[k].sip_signaling_port
        ), "SIP signaling ports don't match."

def assert_routes_are_equal(response_routes, request_routes):
    assert len(response_routes) == len(request_routes)

    for k in range(len(request_routes)):
        assert request_routes[k].name == response_routes[k].name, "Names don't match."
        assert request_routes[k].description == response_routes[k].description, "Descriptions don't match."
        assert (
            request_routes[k].number_pattern == response_routes[k].number_pattern
        ), "Number patterns don't match."
        assert len(request_routes[k].trunks) == len(response_routes[k].trunks), "Trunk lists length doesn't match."
        for m in range(len(request_routes[k].trunks)):
            assert request_routes[k].trunks[m] == response_routes[k].trunks[m] , "Trunk lists don't match."

def setup_configuration(connection_str,skip_update_trunks=False,trunks=[],routes=[]):
    if is_live():
        client = SipRoutingClient.from_connection_string(connection_str, http_logging_policy=get_http_logging_policy())
        client.set_routes(routes)
        if not skip_update_trunks:
            client.set_trunks(trunks)

def get_test_agent():
    return os.getenv("AZURE_TEST_AGENT","")

def get_agent_specific_connection_string():
    test_agent = get_test_agent()
    return os.environ["COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING_SIP_" + test_agent]

def _get_root_domain():
    test_agent = get_test_agent()
    if test_agent:
        return os.getenv("AZURE_TEST_DOMAIN_" + test_agent,"testdomain.com")
    else:
        return os.getenv("AZURE_TEST_DOMAIN","testdomain.com")
    
