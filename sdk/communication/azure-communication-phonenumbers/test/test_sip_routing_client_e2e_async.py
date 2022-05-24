# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio

from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.uri_replacer_processor import URIReplacerProcessor
from _shared.utils import async_create_token_credential, get_http_logging_policy

from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting._generated.models import SipTrunkRoute
from azure.communication.phonenumbers.siprouting._models import SipTrunk
from azure.communication.phonenumbers._shared.utils import parse_connection_str

class TestSipRoutingClientE2EAsync(AsyncCommunicationTestCase):
    TRUNKS = [SipTrunk(fqdn="sbs1.sipconfigtest.com", sip_signaling_port=1122), SipTrunk(fqdn="sbs2.sipconfigtest.com", sip_signaling_port=1123)]
    ROUTES = [SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\+123[0-9]+", trunks=["sbs1.sipconfigtest.com"])]

    def __init__(self, method_name):
        super(TestSipRoutingClientE2EAsync, self).__init__(method_name)
        
    def setUp(self):
        super(TestSipRoutingClientE2EAsync, self).setUp()

        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
        )
        self.recording_processors.extend([URIReplacerProcessor()])
        loop = asyncio.get_event_loop()
        coroutine = self._sip_routing_client.set_routes([])
        loop.run_until_complete(coroutine)
        loop = asyncio.get_event_loop()
        coroutine = self._sip_routing_client.set_trunks(self.TRUNKS)
        loop.run_until_complete(coroutine)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunks(self):
        trunks = await self._sip_routing_client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        self._trunks_are_equal(trunks,self.TRUNKS), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunks_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunks = await client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        self._trunks_are_equal(trunks,self.TRUNKS), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_routes(self):
        await self._sip_routing_client.set_routes(self.ROUTES)
        routes = await self._sip_routing_client.get_routes()
        assert routes is not None, "No routes were returned."
        self._routes_are_equal(routes,self.ROUTES), "Routes are not equal."
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_routes_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        await self._sip_routing_client.set_routes(self.ROUTES)
        routes = await client.get_routes()
        assert routes is not None, "No routes were returned."
        self._routes_are_equal(routes,self.ROUTES), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunks(self):
        new_trunks = [SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)]
        await self._sip_routing_client.set_trunks(new_trunks)
        result_trunks = await self._sip_routing_client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        self._trunks_are_equal(result_trunks,new_trunks), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunks_from_managed_identity(self):
        new_trunks = [SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)]
        client = self._get_sip_client_managed_identity()
        await client.set_trunks(new_trunks)
        result_trunks = await client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        self._trunks_are_equal(result_trunks,new_trunks), "Trunks are not equal."
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_routes(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\+999[0-9]+", trunks=["sbs2.sipconfigtest.com"])]
        await self._sip_routing_client.set_routes(self.ROUTES)
        await self._sip_routing_client.set_routes(new_routes)
        result_routes = await self._sip_routing_client.get_routes()
        assert result_routes is not None, "No routes were returned."
        self._routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_routes_from_managed_identity(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\+999[0-9]+", trunks=["sbs2.sipconfigtest.com"])]
        client = self._get_sip_client_managed_identity()
        await client.set_routes(self.ROUTES)
        await client.set_routes(new_routes)
        result_routes = await client.get_routes()
        assert result_routes is not None, "No routes were returned."
        self._routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_trunk(self):
        trunk_to_delete = self.TRUNKS[1].fqdn
        await self._sip_routing_client.delete_trunk(trunk_to_delete)
        new_trunks = await self._sip_routing_client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0]]), "Trunk was not deleted."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_trunk_from_managed_identity(self):
        trunk_to_delete = self.TRUNKS[1].fqdn
        client = self._get_sip_client_managed_identity()
        await client.delete_trunk(trunk_to_delete)
        new_trunks = await client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0]]), "Trunk was not deleted."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_trunk(self):
        new_trunk = SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)
        await self._sip_routing_client.set_trunk(new_trunk)
        new_trunks = await self._sip_routing_client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],self.TRUNKS[1],new_trunk])
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_trunk_from_managed_identity(self):
        new_trunk = SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)
        client = self._get_sip_client_managed_identity()
        await client.set_trunk(new_trunk)
        new_trunks = await client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],self.TRUNKS[1],new_trunk])
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunk(self):
        trunk = await self._sip_routing_client.get_trunk(self.TRUNKS[0].fqdn)
        assert trunk is not None, "No trunk was returned."
        self._trunks_are_equal([trunk],[self.TRUNKS[0]]), "Returned trunk does not match the required trunk."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunk_from_managed_identity(self):
        client = self._get_sip_client_managed_identity()
        trunk = await client.get_trunk(self.TRUNKS[0].fqdn)
        assert trunk is not None, "No trunk was returned."
        self._trunks_are_equal([trunk],[self.TRUNKS[0]]), "Returned trunk does not match the required trunk."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunk(self):
        modified_trunk = SipTrunk(fqdn=self.TRUNKS[1].fqdn,sip_signaling_port=7777)
        await self._sip_routing_client.set_trunk(modified_trunk)
        new_trunks = await self._sip_routing_client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],modified_trunk])
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunk_from_managed_identity(self):
        modified_trunk = SipTrunk(fqdn=self.TRUNKS[1].fqdn,sip_signaling_port=7777)
        client = self._get_sip_client_managed_identity()
        await client.set_trunk(modified_trunk)
        new_trunks = await client.get_trunks()
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],modified_trunk])

    def _get_sip_client_managed_identity(self):
        endpoint, accesskey = parse_connection_str(self.connection_str)
        credential = async_create_token_credential()
        return SipRoutingClient(endpoint, credential)

    def _trunks_are_equal(self, response_trunks, request_trunks):
        assert len(response_trunks) == len(request_trunks)

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
