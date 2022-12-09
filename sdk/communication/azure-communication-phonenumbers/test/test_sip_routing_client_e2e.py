# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from _shared.testcase import CommunicationTestCase, CommunicationTestResourceType
from _shared.helper import URIReplacerProcessor
from _shared.utils import create_token_credential, get_http_logging_policy
from sip_routing_helper import get_user_domain, assert_trunks_are_equal, assert_routes_are_equal
from domain_replacer_processor import DomainReplacerProcessor

from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipTrunk, SipTrunkRoute
from azure.communication.phonenumbers._shared.utils import parse_connection_str

class TestSipRoutingClientE2E(CommunicationTestCase):
    user_domain = get_user_domain()

    first_trunk = SipTrunk(fqdn="sbs1." + user_domain, sip_signaling_port=1122)
    second_trunk = SipTrunk(fqdn="sbs2." + user_domain, sip_signaling_port=1123)
    additional_trunk = SipTrunk(fqdn="sbs3." + user_domain, sip_signaling_port=2222)
    first_route = SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\\+123[0-9]+", trunks=["sbs1." + user_domain])
    
    def __init__(self, method_name):
        super(TestSipRoutingClientE2E, self).__init__(method_name)
        
    def setUp(self):
        super(TestSipRoutingClientE2E, self).setUp(resource_type=CommunicationTestResourceType.DYNAMIC)
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
            )
        self.recording_processors.extend([URIReplacerProcessor(),DomainReplacerProcessor()])
        self._sip_routing_client.set_routes([])
        self._sip_routing_client.set_trunks([self.first_trunk,self.second_trunk])
    
    def test_get_trunks_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunks = client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(trunks,[self.first_trunk,self.second_trunk])

    def test_get_trunks(self):
        trunks = self._sip_routing_client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(trunks,[self.first_trunk,self.second_trunk])

    def test_get_trunks_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunks = client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(trunks,[self.first_trunk,self.second_trunk])

    def test_get_routes(self):
        self._sip_routing_client.set_routes([self.first_route])
        routes = self._sip_routing_client.get_routes()
        assert routes is not None, "No routes were returned."
        assert_routes_are_equal(routes,[self.first_route])

    def test_get_routes_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        client.set_routes([self.first_route])
        routes = client.get_routes()
        assert routes is not None, "No routes were returned."
        assert_routes_are_equal(routes,[self.first_route])

    def test_set_trunks(self):
        self._sip_routing_client.set_trunks([self.additional_trunk])
        result_trunks = self._sip_routing_client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(result_trunks,[self.additional_trunk])

    def test_set_trunks_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        client.set_trunks([self.additional_trunk])
        result_trunks = client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(result_trunks,[self.additional_trunk])

    def test_set_routes(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[self.second_trunk.fqdn])]
        self._sip_routing_client.set_routes([self.first_route])
        self._sip_routing_client.set_routes(new_routes)
        result_routes = self._sip_routing_client.get_routes()
        assert result_routes is not None, "No routes were returned."
        assert_routes_are_equal(result_routes,new_routes)

    def test_set_routes_from_managed_identity(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[self.second_trunk.fqdn])]
        client = self._get_sip_client_managed_identity()
        client.set_routes([self.first_route])
        client.set_routes(new_routes)
        result_routes = client.get_routes()
        assert result_routes is not None, "No routes were returned."
        assert_routes_are_equal(result_routes,new_routes)

    def test_delete_trunk(self):
        trunk_to_delete = self.second_trunk.fqdn
        self._sip_routing_client.delete_trunk(trunk_to_delete)
        new_trunks = self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk])

    def test_delete_trunk_from_managed_identity(self):
        trunk_to_delete = self.second_trunk.fqdn
        client = self._get_sip_client_managed_identity()
        client.delete_trunk(trunk_to_delete)
        new_trunks = client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk])

    def test_add_trunk(self):
        self._sip_routing_client.set_trunk(self.additional_trunk)
        new_trunks = self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,self.second_trunk,self.additional_trunk])

    def test_add_trunk_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        client.set_trunk(self.additional_trunk)
        new_trunks = client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,self.second_trunk,self.additional_trunk])

    def test_get_trunk(self):
        trunk = self._sip_routing_client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        trunk == self.first_trunk

    def test_get_trunk_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunk = client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        trunk == self.first_trunk

    def test_set_trunk(self):
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn,sip_signaling_port=7777)
        self._sip_routing_client.set_trunk(modified_trunk)
        new_trunks = self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,modified_trunk])
    
    def test_set_trunk_from_managed_identity(self):
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn,sip_signaling_port=7777)
        client = self._get_sip_client_managed_identity()
        client.set_trunk(modified_trunk)
        new_trunks = client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,modified_trunk])

    def _get_sip_client_managed_identity(self):
        endpoint, accesskey = parse_connection_str(self.connection_str)
        credential = create_token_credential()
        return SipRoutingClient(endpoint, credential)
