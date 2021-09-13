# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
import json

from azure.communication.siprouting import SipRoutingClient
from azure.communication.siprouting._generated.models import SipConfiguration, Trunk, TrunkRoute
from testcases.fake_token_credential import FakeTokenCredential

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


class TestSipRoutingClient(unittest.TestCase):
    @classmethod
    def mock_response(self, status_code=200, headers=None, json_payload=None):
        response = Mock(status_code=status_code, headers=headers or {})
        if json_payload is not None:
            response.text = lambda encoding=None: json.dumps(json_payload)
            response.headers["content-type"] = "application/json"
            response.content_type = "application/json"
        else:
            response.text = lambda encoding=None: ""
            response.headers["content-type"] = "text/plain"
            response.content_type = "text/plain"
        return response

    def get_simple_test_client(self):
        return SipRoutingClient("https://endpoint", FakeTokenCredential())

    def setUp(self):
        sip_trunk = Trunk(sip_signaling_port=4001)
        self.test_trunks = {"trunk_1": sip_trunk}
        self.test_routes = [TrunkRoute(
            name="route_1", number_pattern="x", trunks=["trunk_1"])]

        self.payload = {
            "trunks": {
                "trunk_1": {"sipSignalingPort": 4001}
            },
            "routes": [{
                "name": "route_1",
                "numberPattern": "x",
                "trunks": [
                    "trunk_1"
                ]
            }]
        }

        self.response = self.mock_response(
            status_code=200, json_payload=self.payload)

    def test_get_sip_configuration(self):
        def mock_send(*_, **__):
            return self.response

        test_client = SipRoutingClient(
            "https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = test_client.get_sip_configuration()

        self.assertEqual(response.trunks, self.test_trunks)
        self.assertEqual(response.routes, self.test_routes)

    def test_update_sip_configuration(self):
        mock = Mock(send=Mock(return_value=self.response))
        test_client = SipRoutingClient(
            "https://endpoint", FakeTokenCredential(), transport=mock)

        test_client.update_sip_configuration(
            SipConfiguration(trunks=self.test_trunks, routes=self.test_routes))

        captured_request = mock.send.call_args[0][0]
        self.assertEqual(
            json.loads(captured_request.body), self.payload)

    def test_update_sip_trunks(self):
        expected_request_body = {"trunks": {
            "trunk_1": {"sipSignalingPort": 4001}}}
        mock = Mock(send=Mock(return_value=self.response))
        test_client = SipRoutingClient(
            "https://endpoint", FakeTokenCredential(), transport=mock)

        test_client.update_sip_trunks(self.test_trunks)

        captured_request = mock.send.call_args[0][0]
        self.assertEqual(
            json.loads(captured_request.body), expected_request_body)

    def test_update_sip_routes(self):
        expected_request_body = {"routes": [
            {"name": "route_1", "numberPattern": "x", "trunks": ["trunk_1"]}]}

        mock = Mock(send=Mock(return_value=self.response))
        test_client = SipRoutingClient(
            "https://endpoint", FakeTokenCredential(), transport=mock)

        test_client.update_sip_routes(self.test_routes)

        captured_request = mock.send.call_args[0][0]
        self.assertEqual(
            json.loads(captured_request.body), expected_request_body)

    def test_update_sip_configuration_no_sip_trunks_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_sip_configuration(None)

    def test_update_sip_configuration_no_sip_trunks_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_sip_configuration(SipConfiguration(routes=self.test_routes))

    def test_update_sip_configuration_no_sip_routes_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_sip_configuration(SipConfiguration(trunks=self.test_trunks))

    def test_update_sip_trunks_no_gateways_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_sip_trunks(None)

    def test_update_sip_routes_no_routting_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_sip_routes(None)
