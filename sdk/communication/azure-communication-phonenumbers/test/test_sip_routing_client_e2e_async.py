# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.helper import URIReplacerProcessor
from _shared.utils import async_create_token_credential, get_http_logging_policy
from sip_routing_helper import get_randomised_domain, get_trunk_with_actual_domain, trunks_are_equal, routes_are_equal

from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting._generated.models import SipTrunkRoute
from azure.communication.phonenumbers.siprouting._models import SipTrunk
from azure.communication.phonenumbers._shared.utils import parse_connection_str

class TestSipRoutingClientE2EAsync(AsyncCommunicationTestCase):
    # Tests have to use randomised domain, because of domain name collision check on BE. It returns errror, if trunk domain is already used with any other ACS resource.
    randomisedDomain = get_randomised_domain()
    additionalTrunkFqdn = "sbs3" + randomisedDomain
    TRUNKS = [SipTrunk(fqdn="sbs1" + randomisedDomain, sip_signaling_port=1122), SipTrunk(fqdn="sbs2" + randomisedDomain, sip_signaling_port=1123)]
    ROUTES = [SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\\+123[0-9]+", trunks=["sbs1" + randomisedDomain])]

    def __init__(self, method_name):
        super(TestSipRoutingClientE2EAsync, self).__init__(method_name)
        
    def setUp(self):
        super(TestSipRoutingClientE2EAsync, self).setUp()
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
        )
        self.recording_processors.extend([URIReplacerProcessor()])

    async def _prepare_test(self):
        await self._sip_routing_client.set_routes([])
        await self._sip_routing_client.set_trunks(self.TRUNKS)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunks(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            trunks = await self._sip_routing_client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        trunks_are_equal(trunks,self.TRUNKS), "Trunks are not equal."
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunks_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            trunks = await self._sip_routing_client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        trunks_are_equal(trunks,self.TRUNKS), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_routes(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes(self.ROUTES)
            routes = await self._sip_routing_client.get_routes()
        assert routes is not None, "No routes were returned."
        routes_are_equal(routes,self.ROUTES), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_routes_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes(self.ROUTES)
            routes = await self._sip_routing_client.get_routes()
        assert routes is not None, "No routes were returned."
        routes_are_equal(routes,self.ROUTES), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunks(self):
        await self._prepare_test()
        new_trunks = [SipTrunk(fqdn=self.additionalTrunkFqdn, sip_signaling_port=2222)]
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunks(new_trunks)
            result_trunks = await self._sip_routing_client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        trunks_are_equal(result_trunks,new_trunks), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunks_from_managed_identity(self):
        await self._prepare_test()
        new_trunks = [SipTrunk(fqdn=self.additionalTrunkFqdn, sip_signaling_port=2222)]
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunks(new_trunks)
            result_trunks = await self._sip_routing_client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        trunks_are_equal(result_trunks,new_trunks), "Trunks are not equal."
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_routes(self):
        await self._prepare_test()
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[self.TRUNKS[1].fqdn])]
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes(self.ROUTES)
            await self._sip_routing_client.set_routes(new_routes)
            result_routes = await self._sip_routing_client.get_routes()
        assert result_routes is not None, "No routes were returned."
        routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_routes_from_managed_identity(self):
        await self._prepare_test()
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[self.TRUNKS[1].fqdn])]
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes(self.ROUTES)
            await self._sip_routing_client.set_routes(new_routes)
            result_routes = await self._sip_routing_client.get_routes()
        assert result_routes is not None, "No routes were returned."
        routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_trunk(self):
        await self._prepare_test()
        trunk_to_delete = self.TRUNKS[1].fqdn
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_trunk(trunk_to_delete)
            new_trunks = await self._sip_routing_client.get_trunks()
        trunks_are_equal(new_trunks,[self.TRUNKS[0]]), "Trunk was not deleted."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_trunk_from_managed_identity(self):
        await self._prepare_test()
        trunk_to_delete = self.TRUNKS[1].fqdn
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_trunk(trunk_to_delete)
            new_trunks = await self._sip_routing_client.get_trunks()
        trunks_are_equal(new_trunks,[self.TRUNKS[0]]), "Trunk was not deleted."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_trunk(self):
        await self._prepare_test()
        new_trunk = SipTrunk(fqdn=self.additionalTrunkFqdn, sip_signaling_port=2222)
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(new_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        trunks_are_equal(new_trunks,[self.TRUNKS[0],self.TRUNKS[1],new_trunk])
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_trunk_from_managed_identity(self):
        await self._prepare_test()
        new_trunk = SipTrunk(fqdn=self.additionalTrunkFqdn, sip_signaling_port=2222)
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(new_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        trunks_are_equal(new_trunks,[self.TRUNKS[0],self.TRUNKS[1],new_trunk])

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunk(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            actual_trunks = await self._sip_routing_client.get_trunks()
            trunk_actual_domain = get_trunk_with_actual_domain(self.TRUNKS[0].fqdn, actual_trunks[0].fqdn)
            trunk = await self._sip_routing_client.get_trunk(trunk_actual_domain)
        assert trunk is not None, "No trunk was returned."
        trunks_are_equal([trunk],[self.TRUNKS[0]]), "Returned trunk does not match the required trunk."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunk_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            actual_trunks = await self._sip_routing_client.get_trunks()
            trunk_actual_domain = get_trunk_with_actual_domain(self.TRUNKS[0].fqdn, actual_trunks[0].fqdn)
            trunk = await self._sip_routing_client.get_trunk(trunk_actual_domain)
        assert trunk is not None, "No trunk was returned."
        trunks_are_equal([trunk],[self.TRUNKS[0]]), "Returned trunk does not match the required trunk."
        
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunk(self):
        await self._prepare_test()
        modified_trunk = SipTrunk(fqdn=self.TRUNKS[1].fqdn,sip_signaling_port=7777)
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(modified_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        trunks_are_equal(new_trunks,[self.TRUNKS[0],modified_trunk])
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunk_from_managed_identity(self):
        await self._prepare_test()
        modified_trunk = SipTrunk(fqdn=self.TRUNKS[1].fqdn,sip_signaling_port=7777)
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(modified_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        trunks_are_equal(new_trunks,[self.TRUNKS[0],modified_trunk])

    def _get_sip_client_managed_identity(self):
        endpoint, accesskey = parse_connection_str(self.connection_str)
        credential = async_create_token_credential()
        return SipRoutingClient(endpoint, credential, http_logging_policy=get_http_logging_policy())
