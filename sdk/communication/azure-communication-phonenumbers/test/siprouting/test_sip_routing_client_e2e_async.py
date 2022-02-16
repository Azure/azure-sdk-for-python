# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from .._shared.asynctestcase import AsyncCommunicationTestCase
from .._shared.uri_replacer_processor import URIReplacerProcessor
from .._shared.utils import get_http_logging_policy

from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting._generated.models import SipTrunkRoute
from azure.communication.phonenumbers.siprouting._models import SipTrunk

class TestSipRoutingClientE2EAsync(AsyncCommunicationTestCase):
    TRUNKS = [SipTrunk(fqdn="sbs1.sipconfigtest.com", sip_signaling_port=1122), SipTrunk(fqdn="sbs2.sipconfigtest.com", sip_signaling_port=1123)]
    ROUTES = [SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\+123[0-9]+", trunks=["sbs1.sipconfigtest.com"])]


    def __init__(self, method_name):
        os.environ["COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING"] = "endpoint=https://e2e_test.communication.azure.com/;accesskey=qGUv+J0z5Xv8TtjC0qZhy34sodSOMKG5HS7NfsjhqxaB/ZP4UnuS4FspWPo3JowuqAb+75COGi4ErREkB76/UQ=="
        os.environ["AZURE_TEST_RUN_LIVE"] = "True"

        super(TestSipRoutingClientE2EAsync, self).__init__(method_name)
        
    def setUp(self):
        super(TestSipRoutingClientE2EAsync, self).setUp()

        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
        )
        self.recording_processors.extend([URIReplacerProcessor()])
        loop = asyncio.get_event_loop()
        coroutine = self._sip_routing_client.replace_routes([])
        loop.run_until_complete(coroutine)
        loop = asyncio.get_event_loop()
        coroutine = self._sip_routing_client.replace_trunks(self.TRUNKS)
        loop.run_until_complete(coroutine)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunks(self):
        raised = False

        try:
            trunks = await self._sip_routing_client.get_trunks()
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        assert trunks is not None, "No trunks were returned."
        self._trunks_are_equal(trunks,self.TRUNKS), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_routes(self):
        raised = False
        await self._sip_routing_client.replace_routes(self.ROUTES)

        try:
            routes = await self._sip_routing_client.get_routes()
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        assert routes is not None, "No routes were returned."
        self._routes_are_equal(routes,self.ROUTES), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_replace_trunks(self):
        raised = False
        new_trunks = [SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)]

        try:
            await self._sip_routing_client.replace_trunks(new_trunks)
            result_trunks = await self._sip_routing_client.get_trunks()
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        assert result_trunks is not None, "No trunks were returned."
        self._trunks_are_equal(result_trunks,new_trunks), "Trunks are not equal."
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_replace_routes(self):
        raised = False
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\+999[0-9]+", trunks=["sbs2.sipconfigtest.com"])]

        try:
            await self._sip_routing_client.replace_routes(self.ROUTES)
            routes = await self._sip_routing_client.replace_routes(new_routes)
            result_routes = await self._sip_routing_client.get_routes()
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        assert routes is not None, "No routes were returned."
        self._routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_route(self):
        raised = False
        route_to_delete = self.ROUTES[0].name
        await self._sip_routing_client.replace_routes(self.ROUTES)

        try:
            await self._sip_routing_client.delete_route(route_to_delete)
        except Exception as e:
            raised = True
            ex = str(e)

        new_routes = await self._sip_routing_client.get_routes()

        assert raised is False, "Exception:" + ex + " was thrown."
        self._routes_are_equal(new_routes,[]), "Route was not deleted."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_trunk(self):
        raised = False
        trunk_to_delete = self.TRUNKS[1].fqdn

        try:
            await self._sip_routing_client.delete_trunk(trunk_to_delete)
        except Exception as e:
            raised = True
            ex = str(e)

        new_trunks = await self._sip_routing_client.get_trunks()

        assert raised is False, "Exception:" + ex + " was thrown."
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0]]), "Trunk was not deleted."
    
    async def test_add_route(self):
        raised = False
        new_route = SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\+999[0-9]+", trunks=["sbs2.sipconfigtest.com"])
        
        try:
            await self._sip_routing_client.set_route(self.ROUTES[0])
            await self._sip_routing_client.set_route(new_route)
            new_routes = await self._sip_routing_client.get_routes()
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        self._routes_are_equal(new_routes,[self.ROUTES[0],new_route])

    async def test_add_trunk(self):
        raised = False
        new_trunk = SipTrunk(fqdn="sbs3.sipconfigtest.com", sip_signaling_port=2222)

        try:
            await self._sip_routing_client.set_trunk(new_trunk)
        except Exception as e:
            raised = True
            ex = str(e)

        new_trunks = await self._sip_routing_client.get_trunks()

        assert raised is False, "Exception:" + ex + " was thrown."
        self._trunks_are_equal(new_trunks,[self.TRUNKS[0],self.TRUNKS[1],new_trunk])

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
