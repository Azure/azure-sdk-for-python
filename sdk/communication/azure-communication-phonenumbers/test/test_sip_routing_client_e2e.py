# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from _shared.testcase import CommunicationTestCase
from _shared.helper import URIReplacerProcessor
from _shared.utils import create_token_credential, get_http_logging_policy

from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipTrunk, SipTrunkRoute
from azure.communication.phonenumbers._shared.utils import parse_connection_str

class TestSipRoutingClientE2E(CommunicationTestCase):
    TRUNKS = [SipTrunk(fqdn="sbs1.sipconfigtest.com", sip_signaling_port=1122), SipTrunk(fqdn="sbs2.sipconfigtest.com", sip_signaling_port=1123)]
    ROUTES = [SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\\+123[0-9]+", trunks=["sbs1.sipconfigtest.com"])]

    def __init__(self, method_name):
        super(TestSipRoutingClientE2E, self).__init__(method_name)
        
    def setUp(self):
        super(TestSipRoutingClientE2E, self).setUp()

        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
            )
        self.recording_processors.extend([URIReplacerProcessor()])
        self._sip_routing_client.set_routes([])
        self._sip_routing_client.set_trunks(self.TRUNKS)
    
    def test_get_trunks_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunks = client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        self._trunks_are_equal(trunks,self.TRUNKS)

    def test_get_trunks(self):
        trunks = self._sip_routing_client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        self._trunks_are_equal(trunks,self.TRUNKS)

    def test_get_trunks_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunks = client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        self._trunks_are_equal(trunks,self.TRUNKS)

    def test_get_routes(self):
        self._sip_routing_client.set_routes(self.ROUTES)
        routes = self._sip_routing_client.get_routes()
        assert routes is not None, "No routes were returned."
        self._routes_are_equal(routes,self.ROUTES)

    def test_get_routes_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        client.set_routes(self.ROUTES)
        routes = client.get_routes()
        assert routes is not None, "No routes were returned."
        self._routes_are_equal(routes,self.ROUTES)

    def test_set_trunks(self):
        new_trunks = [SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)]
        self._sip_routing_client.set_trunks(new_trunks)
        result_trunks = self._sip_routing_client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        self._trunks_are_equal(result_trunks,new_trunks)

    def test_set_trunks_from_managed_identity(self):
        new_trunks = [SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)]
        client = self._get_sip_client_managed_identity()
        client.set_trunks(new_trunks)
        result_trunks = client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        self._trunks_are_equal(result_trunks,new_trunks)

    def test_set_routes(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=["sbs2.sipconfigtest.com"])]
        self._sip_routing_client.set_routes(self.ROUTES)
        self._sip_routing_client.set_routes(new_routes)
        result_routes = self._sip_routing_client.get_routes()
        assert result_routes is not None, "No routes were returned."
        self._routes_are_equal(result_routes,new_routes)

    def test_set_routes_from_managed_identity(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=["sbs2.sipconfigtest.com"])]
        client = self._get_sip_client_managed_identity()
        client.set_routes(self.ROUTES)
        client.set_routes(new_routes)
        result_routes = client.get_routes()
        assert result_routes is not None, "No routes were returned."
        self._routes_are_equal(result_routes,new_routes)

    def test_delete_trunk(self):
        trunk_to_delete = self.TRUNKS[1].fqdn
        self._sip_routing_client.delete_trunk(trunk_to_delete)
        new_trunks = self._sip_routing_client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0]])

    def test_delete_trunk_from_managed_identity(self):
        trunk_to_delete = self.TRUNKS[1].fqdn
        client = self._get_sip_client_managed_identity()
        client.delete_trunk(trunk_to_delete)
        new_trunks = client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0]])

    def test_add_trunk(self):
        new_trunk = SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)
        self._sip_routing_client.set_trunk(new_trunk)
        new_trunks = self._sip_routing_client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],self.TRUNKS[1],new_trunk])

    def test_add_trunk_from_managed_identity(self):
        new_trunk = SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)
        client = self._get_sip_client_managed_identity()
        client.set_trunk(new_trunk)
        new_trunks = client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],self.TRUNKS[1],new_trunk])

    def test_get_trunk(self):
        trunk = self._sip_routing_client.get_trunk(self.TRUNKS[0].fqdn)
        assert trunk is not None, "No trunk was returned."
        trunk == self.TRUNKS[0]

    def test_get_trunk_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunk = client.get_trunk(self.TRUNKS[0].fqdn)
        assert trunk is not None, "No trunk was returned."
        trunk == self.TRUNKS[0]

    def test_set_trunk(self):
        modified_trunk = SipTrunk(fqdn=self.TRUNKS[1].fqdn,sip_signaling_port=7777)
        self._sip_routing_client.set_trunk(modified_trunk)
        new_trunks = self._sip_routing_client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],modified_trunk])
    
    def test_set_trunk_from_managed_identity(self):
        modified_trunk = SipTrunk(fqdn=self.TRUNKS[1].fqdn,sip_signaling_port=7777)
        client = self._get_sip_client_managed_identity()
        client.set_trunk(modified_trunk)
        new_trunks = client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],modified_trunk])

    def _get_sip_client_managed_identity(self):
        endpoint, accesskey = parse_connection_str(self.connection_str)
        credential = create_token_credential()
        return SipRoutingClient(endpoint, credential)

    def _trunks_are_equal(self, response_trunks, request_trunks):
        assert len(response_trunks) == len(request_trunks), "Trunks have different length."

        for k in range(len(request_trunks)):
            assert response_trunks[k].fqdn==request_trunks[k].fqdn, "Trunk FQDNs don't match."
            assert (
                response_trunks[k].sip_signaling_port==request_trunks[k].sip_signaling_port
            ), "SIP signaling ports don't match."

    def _routes_are_equal(self, response_routes, request_routes):
        assert len(response_routes) == len(request_routes)

        for k in range(len(request_routes)):
            assert request_routes[k].name == response_routes[k].name, "Names don't match."
            assert request_routes[k].description == response_routes[k].description, "Descriptions don't match."
            assert (
                request_routes[k].number_pattern == response_routes[k].number_pattern
            ), "Number patterns don't match."
            assert request_routes[k].trunks == response_routes[k].trunks, "Trunk lists don't match."