# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from phone_numbers_testcase import PhoneNumbersTestCase
from _shared.utils import get_http_logging_policy, get_header_policy
from sip_routing_helper import get_sip_client_managed_identity, get_test_domain, assert_domains_are_equal, setup_configuration, get_as_list
from devtools_testutils import recorded_by_proxy

from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipDomain

class TestSipRoutingClientE2E(PhoneNumbersTestCase):
    domain = SipDomain(fqdn=get_test_domain(), enabled=True)
    additional_domain = SipDomain(fqdn="additionaldomain.com", enabled=False)
    second_additional_domain = SipDomain(fqdn="secondadditionaldomain.com", enabled=False)

    def setup_method(self):
        super(TestSipRoutingClientE2E, self).setUp(use_dynamic_resource=True)
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
        )
        setup_configuration(self.connection_str, domains=[self.domain, self.additional_domain])

    @recorded_by_proxy
    def test_set_domain(self, **kwargs):
        self._sip_routing_client.set_domain(self.second_additional_domain)
        result_domains = self._sip_routing_client.list_domains()
        domains_list = get_as_list(result_domains)
        assert_domains_are_equal(domains_list, [self.domain, self.additional_domain, self.second_additional_domain])

    @recorded_by_proxy
    def test_set_domain_with_managed_identity(self, **kwargs):
        client = get_sip_client_managed_identity(self.connection_str)
        client.set_domain(self.second_additional_domain)
        result_domains = client.list_domains()
        domains_list = get_as_list(result_domains)
        assert_domains_are_equal(domains_list, [self.domain, self.additional_domain, self.second_additional_domain])


    @recorded_by_proxy
    def test_list_domains(self, **kwargs):
        domains = self._sip_routing_client.list_domains()
        domains_list = get_as_list(domains)
        assert_domains_are_equal(domains_list, [self.domain, self.additional_domain])
    
    @recorded_by_proxy
    def test_list_domains_with_managed_identity(self, **kwargs):
        client = get_sip_client_managed_identity(self.connection_str)
        domains = client.list_domains()
        domains_list = get_as_list(domains)
        assert_domains_are_equal(domains_list, [self.domain, self.additional_domain])

    @recorded_by_proxy
    def test_delete_domain(self, **kwargs):
        domain_to_delete = self.additional_domain.fqdn
        self._sip_routing_client.delete_domain(domain_to_delete)
        new_domains = self._sip_routing_client.list_domains()
        domains_list = get_as_list(new_domains)
        assert_domains_are_equal(domains_list, [self.domain])

    @recorded_by_proxy
    def test_delete_domain_with_managed_identity(self, **kwargs):
        domain_to_delete = self.additional_domain.fqdn
        client = get_sip_client_managed_identity(self.connection_str)
        client.delete_domain(domain_to_delete)
        new_domains = client.list_domains()
        domains_list = get_as_list(new_domains)
        assert_domains_are_equal(domains_list, [self.domain])

    