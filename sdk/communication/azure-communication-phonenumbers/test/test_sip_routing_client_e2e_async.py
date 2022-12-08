# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.helper import URIReplacerProcessor
from _shared.utils import async_create_token_credential, get_http_logging_policy
from sip_routing_helper import get_user_domain, assert_trunks_are_equal, assert_routes_are_equal
from domain_replacer_processor import DomainReplacerProcessor

from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting._generated.models import SipTrunkRoute
from azure.communication.phonenumbers.siprouting._models import SipTrunk
from azure.communication.phonenumbers._shared.utils import parse_connection_str

class TestSipRoutingClientE2EAsync(AsyncCommunicationTestCase):
    user_domain = get_user_domain()
    
    first_trunk = SipTrunk(fqdn="sbs1." + user_domain, sip_signaling_port=1122)
    second_trunk = SipTrunk(fqdn="sbs2." + user_domain, sip_signaling_port=1123)
    additional_trunk = SipTrunk(fqdn="sbs3." + user_domain, sip_signaling_port=2222)
    first_route = SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\\+123[0-9]+", trunks=["sbs1." + user_domain])
    
    def __init__(self, method_name):
        super(TestSipRoutingClientE2EAsync, self).__init__(method_name)
        
    def setUp(self):
        super(TestSipRoutingClientE2EAsync, self).setUp(use_dynamic_resource=True)
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
        )
        self.recording_processors.extend([URIReplacerProcessor(), DomainReplacerProcessor()])

    async def _prepare_test(self):
        await self._sip_routing_client.set_routes([])
        await self._sip_routing_client.set_trunks([self.first_trunk, self.second_trunk])

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunks(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            trunks = await self._sip_routing_client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(trunks,[self.first_trunk, self.second_trunk]), "Trunks are not equal."
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunks_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            trunks = await self._sip_routing_client.get_trunks()
        assert trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(trunks,[self.first_trunk, self.second_trunk]), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_routes(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            routes = await self._sip_routing_client.get_routes()
        assert routes is not None, "No routes were returned."
        assert_routes_are_equal(routes,[self.first_route]), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_routes_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            routes = await self._sip_routing_client.get_routes()
        assert routes is not None, "No routes were returned."
        assert_routes_are_equal(routes,[self.first_route]), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunks(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunks([self.additional_trunk])
            result_trunks = await self._sip_routing_client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(result_trunks,[self.additional_trunk]), "Trunks are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunks_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunks([self.additional_trunk])
            result_trunks = await self._sip_routing_client.get_trunks()
        assert result_trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(result_trunks,[self.additional_trunk]), "Trunks are not equal."
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_routes(self):
        await self._prepare_test()
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[self.second_trunk.fqdn])]
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            await self._sip_routing_client.set_routes(new_routes)
            result_routes = await self._sip_routing_client.get_routes()
        assert result_routes is not None, "No routes were returned."
        assert_routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_routes_from_managed_identity(self):
        await self._prepare_test()
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[self.second_trunk.fqdn])]
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            await self._sip_routing_client.set_routes(new_routes)
            result_routes = await self._sip_routing_client.get_routes()
        assert result_routes is not None, "No routes were returned."
        assert_routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_trunk(self):
        await self._prepare_test()
        trunk_to_delete = self.second_trunk.fqdn
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_trunk(trunk_to_delete)
            new_trunks = await self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk]), "Trunk was not deleted."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_trunk_from_managed_identity(self):
        await self._prepare_test()
        trunk_to_delete = self.second_trunk.fqdn
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_trunk(trunk_to_delete)
            new_trunks = await self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk]), "Trunk was not deleted."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_trunk(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(self.additional_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,self.second_trunk,self.additional_trunk])
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_trunk_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(self.additional_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,self.second_trunk,self.additional_trunk])

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunk(self):
        await self._prepare_test()
        async with self._sip_routing_client:
            trunk = await self._sip_routing_client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        assert_trunks_are_equal([trunk],[self.first_trunk]), "Returned trunk does not match the required trunk."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_trunk_from_managed_identity(self):
        await self._prepare_test()
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            trunk = await self._sip_routing_client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        assert_trunks_are_equal([trunk],[self.first_trunk]), "Returned trunk does not match the required trunk."
        
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunk(self):
        await self._prepare_test()
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn,sip_signaling_port=7777)
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(modified_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,modified_trunk])
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_set_trunk_from_managed_identity(self):
        await self._prepare_test()
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn,sip_signaling_port=7777)
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(modified_trunk)
            new_trunks = await self._sip_routing_client.get_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,modified_trunk])

    def _get_sip_client_managed_identity(self):
        endpoint, accesskey = parse_connection_str(self.connection_str)
        credential = async_create_token_credential()
        return SipRoutingClient(endpoint, credential, http_logging_policy=get_http_logging_policy())
