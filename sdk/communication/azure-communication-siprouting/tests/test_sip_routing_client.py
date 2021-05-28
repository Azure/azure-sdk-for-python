import unittest
import json

from azure.communication.siprouting import SIPRoutingClient
from azure.core.credentials import AccessToken
from azure.communication.siprouting._generated.models import Trunk, TrunkRoute

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


class TestSIPRoutingClient(unittest.TestCase):
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
        return SIPRoutingClient("https://endpoint", AccessToken("Fake Token", 0))

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

        test_client = SIPRoutingClient(
            "https://endpoint", AccessToken("Fake Token", 0), transport=Mock(send=mock_send))

        response = test_client.get_sip_configuration()

        self.assertEqual(response.trunks, self.test_trunks)
        self.assertEqual(response.routes, self.test_routes)

    def test_update_sip_trunk_configuration(self):
        mock = Mock(send=Mock(return_value=self.response))
        test_client = SIPRoutingClient(
            "https://endpoint", AccessToken("Fake Token", 0), transport=mock)

        test_client.update_sip_trunk_configuration(
            self.test_trunks, self.test_routes)

        payload_string = str(self.payload)
        self.assertEqual(
            mock.send.call_args.args[0].body, payload_string.replace("\'", "\""))

    def test_update_pstn_gateways(self):
        expected_request_body = r'{"trunks": {"trunk_1": {"sipSignalingPort": 4001}}}'
        mock = Mock(send=Mock(return_value=self.response))
        test_client = SIPRoutingClient(
            "https://endpoint", AccessToken("Fake Token", 0), transport=mock)

        test_client.update_pstn_gateways(self.test_trunks)

        self.assertEqual(
            mock.send.call_args.args[0].body, expected_request_body)

    def test_update_routing_settings(self):
        expected_request_body = r'{"routes": [{"name": "route_1", "numberPattern": "x", "trunks": ["trunk_1"]}]}'

        mock = Mock(send=Mock(return_value=self.response))
        test_client = SIPRoutingClient(
            "https://endpoint", AccessToken("Fake Token", 0), transport=mock)

        test_client.update_routing_settings(self.test_routes)

        self.assertEqual(
            mock.send.call_args.args[0].body, expected_request_body)

    def test_update_sip_trunk_configuration_no_online_pstn_gateways_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_sip_trunk_configuration(None, self.test_routes)

    def test_update_sip_trunk_configuration_no_online_pstn_routing_settings_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_sip_trunk_configuration(self.test_trunks, None)

    def test_update_pstn_gateways_no_gateways_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_pstn_gateways(None)

    def test_update_routing_settings_no_routting_raises_value_error(self):
        test_client = self.get_simple_test_client()

        with self.assertRaises(ValueError):
            test_client.update_routing_settings(None)
