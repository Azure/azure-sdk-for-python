# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import aiounittest
import json
import pytest

from azure.communication.siprouting.aio import SipRoutingClient
from azure.core.credentials import AccessToken
from azure.communication.siprouting._generated.models import Trunk, TrunkRoute, SipConfiguration
from testcases.fake_token_credential import FakeTokenCredential

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


class TestSipRoutingClientAsync(aiounittest.AsyncTestCase):
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
    
    @pytest.mark.asyncio
    @patch("azure.communication.siprouting._generated.aio._azure_communication_sip_routing_service.AzureCommunicationSIPRoutingServiceOperationsMixin.get_sip_configuration",
           return_value={"trunks": {"trunk_1": Trunk(sip_signaling_port=4001)}, "routes": [TrunkRoute(
               name= "route_1",
               number_pattern= "x",
               trunks= ["trunk_1"])
               ]})
    async def test_get_sip_configuration(self, mock):
        test_client = self.get_simple_test_client()

        response = await test_client.get_sip_configuration()

        self.assertEqual(response['trunks'], self.test_trunks)
        self.assertEqual(response['routes'], self.test_routes)

    @pytest.mark.asyncio
    @patch("azure.communication.siprouting._generated.aio._azure_communication_sip_routing_service.AzureCommunicationSIPRoutingService.patch_sip_configuration")
    async def test_update_sip_configurationn(self, mock):
        test_client = self.get_simple_test_client()

        await test_client.update_sip_configuration(
            SipConfiguration(trunks=self.test_trunks, routes=self.test_routes))

        self.assertEqual(mock.call_args[1]['body'].trunks, self.test_trunks)
        self.assertEqual(mock.call_args[1]['body'].routes, self.test_routes)

    @pytest.mark.asyncio
    @patch("azure.communication.siprouting._generated.aio._azure_communication_sip_routing_service.AzureCommunicationSIPRoutingService.patch_sip_configuration")
    async def test_update_sip_trunks(self, mock):
        test_client = self.get_simple_test_client()

        await test_client.update_sip_trunks(self.test_trunks)

        self.assertEqual(mock.call_args[1]['body'].trunks, self.test_trunks)

    @pytest.mark.asyncio
    @patch("azure.communication.siprouting._generated.aio._azure_communication_sip_routing_service.AzureCommunicationSIPRoutingService.patch_sip_configuration")
    async def test_update_sip_routes(self, mock):
        test_client = self.get_simple_test_client()

        await test_client.update_sip_routes(self.test_routes)

        self.assertEqual(mock.call_args[1]['body'].routes, self.test_routes)

    @pytest.mark.asyncio
    async def test_update_sip_configuration_no_sip_trunks_raises_value_error(self):
        test_client = self.get_simple_test_client()

        try:
            await test_client.update_sip_configuration(SipConfiguration(routes=self.test_routes))
            raised = False
        except ValueError:
            raised = True

        self.assertTrue(raised)

    @pytest.mark.asyncio
    @patch("azure.communication.siprouting._generated.aio._azure_communication_sip_routing_service.AzureCommunicationSIPRoutingService.patch_sip_configuration")
    async def test_update_sip_configuration_no_sip_trunks_raises_value_error(self,mock):
        test_client = self.get_simple_test_client()
        trunk = {"trunk_1": None}

        try:
            await test_client.update_sip_configuration(SipConfiguration(trunks=trunk,routes=self.test_routes))
            raised = False
        except ValueError:
            raised = True

        self.assertFalse(raised)

    @pytest.mark.asyncio
    async def test_update_sip_configuration_no_sip_routes_raises_value_error(self):
        test_client = self.get_simple_test_client()

        try:
            await test_client.update_sip_configuration(SipConfiguration(trunks=self.test_trunks))
            raised = False
        except ValueError:
            raised = True

        self.assertTrue(raised)

    @pytest.mark.asyncio
    async def test_update_sip_trunks_no_gateways_raises_value_error(self):
        test_client = self.get_simple_test_client()

        try:
            await test_client.update_sip_trunks(None)
        except ValueError:
            raised = True

        self.assertTrue(raised)

    @pytest.mark.asyncio
    async def test_update_sip_routes_no_routting_raises_value_error(self):
        test_client = self.get_simple_test_client()

        try:
            await test_client.update_sip_routes(None)
        except ValueError:
            raised = True

        self.assertTrue(raised)
