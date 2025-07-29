# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from phone_numbers_testcase import PhoneNumbersTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from _shared.utils import get_http_logging_policy, get_header_policy
from sip_routing_helper import assert_trunks_are_equal, get_async_sip_client_managed_identity, assert_domains_are_equal, setup_configuration, get_test_domain, get_as_list_async

from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting._models import SipDomain

@pytest.mark.asyncio
class TestSipRoutingClientE2EAsync(PhoneNumbersTestCase):
    domain = SipDomain(fqdn=get_test_domain(), enabled=True)
    additional_domain = SipDomain(fqdn="additionaldomain.com", enabled=False)
    second_additional_domain = SipDomain(fqdn="secondadditionaldomain.com", enabled=False)

    def setup_method(self):
        super(TestSipRoutingClientE2EAsync, self).setUp(use_dynamic_resource=True)
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
        )
        setup_configuration(self.connection_str, domains=[self.domain, self.additional_domain])

    @recorded_by_proxy_async
    async def test_list_domains(self, **kwargs):
        async with self._sip_routing_client:
            domains = self._sip_routing_client.list_domains()
            domains_list = await self._get_as_list(domains)

        assert_domains_are_equal(domains_list, [self.domain, self.additional_domain]), "Domains are not equal."

    @recorded_by_proxy_async
    async def test_list_domains_with_managed_identity(self, **kwargs):
        self._sip_routing_client = get_async_sip_client_managed_identity(self.connection_str)
        async with self._sip_routing_client:
            domains = self._sip_routing_client.list_domains()
            domains_list = await self._get_as_list(domains)

        assert_domains_are_equal(domains_list, [self.domain, self.additional_domain]), "Domains are not equal."

    @recorded_by_proxy_async
    async def test_delete_domain(self, **kwargs):
        domain_to_delete = self.additional_domain.fqdn
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_domain(domain_to_delete)
            new_domains = self._sip_routing_client.list_domains()
            domains_list = await self._get_as_list(new_domains)

        assert_domains_are_equal(domains_list, [self.domain]), "Domain was not deleted."

    @recorded_by_proxy_async
    async def test_delete_domain_with_managed_identity(self, **kwargs):
        domain_to_delete = self.additional_domain.fqdn
        self._sip_routing_client = get_async_sip_client_managed_identity(self.connection_str)
        async with self._sip_routing_client:
            await self._sip_routing_client.delete_domain(domain_to_delete)
            new_domains = self._sip_routing_client.list_domains()
            domains_list = await self._get_as_list(new_domains)

        assert_domains_are_equal(domains_list, [self.domain]), "Domain was not deleted."

    async def test_set_trunk_from_managed_identity(self):
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn, sip_signaling_port=7777, enabled=True,
                                  direct_transfer=True, privacy_header="none", ip_address_version="ipv6")
        self._sip_routing_client = get_async_sip_client_managed_identity(self.connection_str)
        async with self._sip_routing_client:
            await self._sip_routing_client.set_trunk(modified_trunk)
            new_trunks = self._sip_routing_client.list_trunks()
            new_trunks_list = await self._get_as_list(new_trunks)
        assert_trunks_are_equal(new_trunks_list, [self.first_trunk, modified_trunk])

    @recorded_by_proxy_async
    async def test_set_domains(self, **kwargs):
        async with self._sip_routing_client:
            await self._sip_routing_client.set_domains([self.second_additional_domain])
            result_domains = self._sip_routing_client.list_domains()
            domains_list =  await self._get_as_list(result_domains)

        assert_domains_are_equal(domains_list, [self.second_additional_domain])

    @recorded_by_proxy_async
    async def test_set_domains_with_managed_identity(self, **kwargs):
        self._sip_routing_client = get_async_sip_client_managed_identity(self.connection_str)
        async with self._sip_routing_client:
            await self._sip_routing_client.set_domains([self.second_additional_domain])
            result_domains =  self._sip_routing_client.list_domains()
            domains_list =  await self.get_as_list(result_domains)
            
        assert_domains_are_equal(domains_list, [self.second_additional_domain])


    async def _get_as_list(self, iter):
        assert iter is not None, "No iterable was returned."
        items = []
        async for item in iter:
            items.append(item)
        return items