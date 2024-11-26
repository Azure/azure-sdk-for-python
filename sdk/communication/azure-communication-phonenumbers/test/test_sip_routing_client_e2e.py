# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError
import pytest
from phone_numbers_testcase import PhoneNumbersTestCase
from _shared.utils import create_token_credential, get_http_logging_policy, get_header_policy
from sip_routing_helper import get_unique_fqdn, assert_trunks_are_equal, assert_routes_are_equal, setup_configuration
from devtools_testutils import recorded_by_proxy

from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipTrunk, SipTrunkRoute
from azure.communication.phonenumbers._shared.utils import parse_connection_str


class TestSipRoutingClientE2E(PhoneNumbersTestCase):
    first_trunk = SipTrunk(fqdn=get_unique_fqdn("sbs1"), sip_signaling_port=1122)
    second_trunk = SipTrunk(fqdn=get_unique_fqdn("sbs2"), sip_signaling_port=1123)
    additional_trunk = SipTrunk(fqdn=get_unique_fqdn("sbs3"), sip_signaling_port=2222)
    first_route = SipTrunkRoute(
        name="First rule", description="Handle numbers starting with '+123'", number_pattern="\\+123[0-9]+", trunks=[]
    )

    def setup_method(self):
        super(TestSipRoutingClientE2E, self).setUp(use_dynamic_resource=True)
        self._sip_routing_client = SipRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
        )
        setup_configuration(self.connection_str, trunks=[self.first_trunk, self.second_trunk])

    @recorded_by_proxy
    def test_get_trunks(self, **kwargs):
        trunks = self._sip_routing_client.list_trunks()
        trunks_list = self._get_as_list(trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk, self.second_trunk])

    @recorded_by_proxy
    def test_get_trunks_from_managed_identity(self, **kwargs):
        client = self._get_sip_client_managed_identity()
        trunks = client.list_trunks()
        trunks_list = self._get_as_list(trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk, self.second_trunk])

    @recorded_by_proxy
    def test_get_routes(self, **kwargs):
        self._sip_routing_client.set_routes([self.first_route])
        routes = self._sip_routing_client.list_routes()
        routes_list = self._get_as_list(routes)
        assert_routes_are_equal(routes_list, [self.first_route])

    @recorded_by_proxy
    def test_get_routes_from_managed_identity(self, **kwargs):
        client = self._get_sip_client_managed_identity()
        client.set_routes([self.first_route])
        routes = client.list_routes()
        routes_list = self._get_as_list(routes)
        assert_routes_are_equal(routes_list, [self.first_route])

    @recorded_by_proxy
    def test_set_trunks(self, **kwargs):
        self._sip_routing_client.set_trunks([self.additional_trunk])
        result_trunks = self._sip_routing_client.list_trunks()
        trunks_list = self._get_as_list(result_trunks)
        assert_trunks_are_equal(trunks_list, [self.additional_trunk])

    @recorded_by_proxy
    def test_set_trunks_from_managed_identity(self, **kwargs):
        client = self._get_sip_client_managed_identity()
        client.set_trunks([self.additional_trunk])
        result_trunks = client.list_trunks()
        trunks_list = self._get_as_list(result_trunks)
        assert_trunks_are_equal(trunks_list, [self.additional_trunk])

    @recorded_by_proxy
    def test_set_trunks_empty_list(self, **kwargs):
        """Verification of bug fix. SDK shouldn't send empty PATCH, otherwise it will receive exception.
        This situation occurs, when sending empty trunks list to already empty trunk configuration."""
        try:
            self._sip_routing_client.set_trunks([])
            self._sip_routing_client.set_trunks([])
        except HttpResponseError as exception:
            assert False, (
                "Trying to set empty trunks list returned Http error: "
                + str(exception.status_code)
                + ", message: "
                + exception.message
            )

    @recorded_by_proxy
    def test_set_routes(self, **kwargs):
        new_routes = [
            SipTrunkRoute(
                name="Alternative rule",
                description="Handle numbers starting with '+999'",
                number_pattern="\\+999[0-9]+",
                trunks=[],
            )
        ]
        self._sip_routing_client.set_routes([self.first_route])
        self._sip_routing_client.set_routes(new_routes)
        result_routes = self._sip_routing_client.list_routes()
        routes_list = self._get_as_list(result_routes)
        assert_routes_are_equal(routes_list, new_routes)

    @recorded_by_proxy
    def test_set_routes_from_managed_identity(self, **kwargs):
        new_routes = [
            SipTrunkRoute(
                name="Alternative rule",
                description="Handle numbers starting with '+999'",
                number_pattern="\\+999[0-9]+",
                trunks=[],
            )
        ]
        client = self._get_sip_client_managed_identity()
        client.set_routes([self.first_route])
        client.set_routes(new_routes)
        result_routes = client.list_routes()
        routes_list = self._get_as_list(result_routes)
        assert_routes_are_equal(routes_list, new_routes)

    @recorded_by_proxy
    def test_delete_trunk(self, **kwargs):
        trunk_to_delete = self.second_trunk.fqdn
        self._sip_routing_client.delete_trunk(trunk_to_delete)
        new_trunks = self._sip_routing_client.list_trunks()
        trunks_list = self._get_as_list(new_trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk])

    @recorded_by_proxy
    def test_delete_trunk_from_managed_identity(self, **kwargs):
        trunk_to_delete = self.second_trunk.fqdn
        client = self._get_sip_client_managed_identity()
        client.delete_trunk(trunk_to_delete)
        new_trunks = client.list_trunks()
        trunks_list = self._get_as_list(new_trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk])

    @recorded_by_proxy
    def test_add_trunk(self, **kwargs):
        self._sip_routing_client.set_trunk(self.additional_trunk)
        new_trunks = self._sip_routing_client.list_trunks()
        trunks_list = self._get_as_list(new_trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk, self.second_trunk, self.additional_trunk])

    @recorded_by_proxy
    def test_add_trunk_from_managed_identity(self, **kwargs):
        client = self._get_sip_client_managed_identity()
        client.set_trunk(self.additional_trunk)
        new_trunks = client.list_trunks()
        trunks_list = self._get_as_list(new_trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk, self.second_trunk, self.additional_trunk])

    @recorded_by_proxy
    def test_get_trunk(self, **kwargs):
        trunk = self._sip_routing_client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        trunk == self.first_trunk

    @recorded_by_proxy
    def test_get_trunk_from_managed_identity(self, **kwargs):
        client = self._get_sip_client_managed_identity()
        trunk = client.get_trunk(self.first_trunk.fqdn)
        assert trunk is not None, "No trunk was returned."
        trunk == self.first_trunk

    @recorded_by_proxy
    def test_get_trunk_not_existing_throws(self, **kwargs):
        with pytest.raises(KeyError):
            self._sip_routing_client.get_trunk("non-existing.fqdn.test")

    @recorded_by_proxy
    def test_set_trunk(self, **kwargs):
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn, sip_signaling_port=7777)
        self._sip_routing_client.set_trunk(modified_trunk)
        new_trunks = self._sip_routing_client.list_trunks()
        trunks_list = self._get_as_list(new_trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk, modified_trunk])

    @recorded_by_proxy
    def test_set_trunk_from_managed_identity(self, **kwargs):
        modified_trunk = SipTrunk(fqdn=self.second_trunk.fqdn, sip_signaling_port=7777)
        client = self._get_sip_client_managed_identity()
        client.set_trunk(modified_trunk)
        new_trunks = client.list_trunks()
        trunks_list = self._get_as_list(new_trunks)
        assert_trunks_are_equal(trunks_list, [self.first_trunk, modified_trunk])

    def _get_sip_client_managed_identity(self):
        endpoint, *_ = parse_connection_str(self.connection_str)
        credential = create_token_credential()
        return SipRoutingClient(
            endpoint, credential, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
        )

    def _get_as_list(self, iter):
        assert iter is not None, "No iterable was returned."
        items = []
        for item in iter:
            items.append(item)
        return items
