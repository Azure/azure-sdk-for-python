# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import HttpResponseError
from phone_numbers_testcase import PhoneNumbersTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from _shared.utils import async_create_token_credential, get_http_logging_policy
from sip_routing_helper import get_unique_fqdn, assert_trunks_are_equal, assert_routes_are_equal, setup_configuration
import os

from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting._models import SipTrunk, SipTrunkRoute
from azure.communication.phonenumbers._shared.utils import parse_connection_str


@pytest.mark.asyncio
class TestSipRoutingClientE2EAsync(PhoneNumbersTestCase):   
    
    first_trunk = SipTrunk(fqdn=get_unique_fqdn("sbs1"), sip_signaling_port=1122)
    second_trunk = SipTrunk(fqdn=get_unique_fqdn("sbs2"), sip_signaling_port=1123)
    additional_trunk = SipTrunk(fqdn=get_unique_fqdn("sbs3"), sip_signaling_port=2222)
    first_route = SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\\+123[0-9]+", trunks=[])
            
    def setup_method(self):
        super(TestSipRoutingClientE2EAsync, self).setUp()
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
        )
        setup_configuration(self.connection_str,trunks=[self.first_trunk, self.second_trunk])

    @recorded_by_proxy_async
    async def test_get_trunks(self):
        async with self._sip_routing_client:
            trunks = await self._sip_routing_client.list_trunks()
        assert trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(trunks,[self.first_trunk, self.second_trunk]), "Trunks are not equal."
    
    @recorded_by_proxy_async
    async def test_get_trunks_from_managed_identity(self):
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            trunks = await self._sip_routing_client.list_trunks()
        assert trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(trunks,[self.first_trunk, self.second_trunk]), "Trunks are not equal."

    @recorded_by_proxy_async
    async def test_get_routes(self):
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            routes = await self._sip_routing_client.list_routes()
        assert routes is not None, "No routes were returned."
        assert_routes_are_equal(routes,[self.first_route]), "Routes are not equal."

    @recorded_by_proxy_async
    async def test_get_routes_from_managed_identity(self):
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            routes = await self._sip_routing_client.list_routes()
        assert routes is not None, "No routes were returned."
        assert_routes_are_equal(routes,[self.first_route]), "Routes are not equal."

    @recorded_by_proxy_async
    async def test_set_trunks(self):
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunks([self.additional_trunk])
            result_trunks = await self._sip_routing_client.list_trunks()
        assert result_trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(result_trunks,[self.additional_trunk]), "Trunks are not equal."

    @recorded_by_proxy_async
    async def test_set_trunks_from_managed_identity(self):
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunks([self.additional_trunk])
            result_trunks = await self._sip_routing_client.list_trunks()
        assert result_trunks is not None, "No trunks were returned."
        assert_trunks_are_equal(result_trunks,[self.additional_trunk]), "Trunks are not equal."

    @recorded_by_proxy_async
    async def test_set_trunks_empty_list(self):
        """Verification of bug fix. SDK shouldn't send empty PATCH, otherwise it will receive exception.
        This situation occurs, when sending empty trunks list to already empty trunk configuration."""
        async with self._sip_routing_client:
            try: 
                await self._sip_routing_client.set_trunks([])
                await self._sip_routing_client.set_trunks([])
            except HttpResponseError as exception:
                assert False, "Trying to set empty trunks list returned Http error: " + str(exception.status_code) + ", message: " + exception.message
    
    @recorded_by_proxy_async
    async def test_set_routes(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[])]
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            await self._sip_routing_client.set_routes(new_routes)
            result_routes = await self._sip_routing_client.list_routes()
        assert result_routes is not None, "No routes were returned."
        assert_routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @recorded_by_proxy_async
    async def test_set_routes_from_managed_identity(self):
        new_routes = [SipTrunkRoute(name="Alternative rule", description="Handle numbers starting with '+999'", number_pattern="\\+999[0-9]+", trunks=[])]
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_routes([self.first_route])
            await self._sip_routing_client.set_routes(new_routes)
            result_routes = await self._sip_routing_client.list_routes()
        assert result_routes is not None, "No routes were returned."
        assert_routes_are_equal(result_routes,new_routes), "Routes are not equal."

    @recorded_by_proxy_async
    async def test_delete_trunk(self):
        trunk_to_delete = self.second_trunk.fqdn
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_trunk(trunk_to_delete)
            new_trunks = await self._sip_routing_client.list_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk]), "Trunk was not deleted."

    @recorded_by_proxy_async
    async def test_delete_trunk_from_managed_identity(self):
        trunk_to_delete = self.second_trunk.fqdn
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_trunk(trunk_to_delete)
            new_trunks = await self._sip_routing_client.list_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk]), "Trunk was not deleted."

    @recorded_by_proxy_async
    async def test_add_trunk(self):
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(self.additional_trunk)
            new_trunks = await self._sip_routing_client.list_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,self.second_trunk,self.additional_trunk])
    
    @recorded_by_proxy_async
    async def test_add_trunk_from_managed_identity(self):
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(self.additional_trunk)
            new_trunks = await self._sip_routing_client.list_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,self.second_trunk,self.additional_trunk])

    @recorded_by_proxy_async
    async def test_get_trunk(self):
        async with self._sip_routing_client:
            trunk = await self._sip_routing_client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        assert_trunks_are_equal([trunk],[self.first_trunk]), "Returned trunk does not match the required trunk."

    @recorded_by_proxy_async
    async def test_get_trunk_from_managed_identity(self):
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            trunk = await self._sip_routing_client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        assert_trunks_are_equal([trunk],[self.first_trunk]), "Returned trunk does not match the required trunk."
        
    @recorded_by_proxy_async
    async def test_set_trunk(self):
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn,sip_signaling_port=7777)
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(modified_trunk)
            new_trunks = await self._sip_routing_client.list_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,modified_trunk])
    
    @recorded_by_proxy_async
    async def test_set_trunk_from_managed_identity(self):
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn,sip_signaling_port=7777)
        self._sip_routing_client = self._get_sip_client_managed_identity()
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(modified_trunk)
            new_trunks = await self._sip_routing_client.list_trunks()
        assert_trunks_are_equal(new_trunks,[self.first_trunk,modified_trunk])

    def _get_sip_client_managed_identity(self):
        endpoint, *_ = parse_connection_str(self.connection_str)
        credential = async_create_token_credential()
        return SipRoutingClient(endpoint, credential, http_logging_policy=get_http_logging_policy())
