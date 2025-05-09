# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from phone_numbers_testcase import PhoneNumbersTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from _shared.utils import get_http_logging_policy, get_header_policy
from sip_routing_helper import get_async_sip_client_managed_identity, assert_domains_are_equal, setup_configuration, get_test_domain, get_as_list_async

from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting._models import SipDomain

@pytest.mark.asyncio
class TestSipRoutingClientE2EAsync(PhoneNumbersTestCase):
    domain = SipDomain(fqdn=get_test_domain(), enabled=True)
    additional_domain = SipDomain(fqdn="additionaldomain.com", enabled=False)
    second_additional_domain = SipDomain(fqdn="secondadditionaldomain.com", enabled=False)

    def setup_method(self):
        super(TestSipRoutingClientE2EAsync, self).setUp(use_dynamic_resource=True)
        setup_configuration(self.connection_str, trunks=[])

    @recorded_by_proxy_async
    async def test_domains(self):
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
        )
        await self._run_test()               

    @recorded_by_proxy_async
    async def test_domains_with_managed_identity(self):
        self._sip_routing_client = get_async_sip_client_managed_identity(self.connection_str)
        await self._run_test()               

    async def _run_test(self):
        await self._sip_routing_client.set_domains([self.domain,self.additional_domain])
        new_domains = self._sip_routing_client.list_domains()
        new_domains_list = await get_as_list_async(new_domains)
        assert_domains_are_equal(new_domains_list, [self.domain, self.additional_domain])
        await self._sip_routing_client.set_domain(self.second_additional_domain)
        new_domain_retrieved = await self._sip_routing_client.get_domain(self.second_additional_domain.fqdn)
        assert_domains_are_equal([new_domain_retrieved], [self.second_additional_domain])
        await self._sip_routing_client.delete_domain(self.second_additional_domain.fqdn)
        final_domains = self._sip_routing_client.list_domains()
        final_domains_list = await get_as_list_async(final_domains)
        assert_domains_are_equal(final_domains_list, [self.domain, self.additional_domain])