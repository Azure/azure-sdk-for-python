# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

from testcases.async_communication_testcase import AsyncCommunicationTestCase
from testcases.uri_replacer_processor import URIReplacerProcessor
from azure.communication.siprouting.aio import SIPRoutingClient


class TestSIPRoutingClientE2EAsync(AsyncCommunicationTestCase):
    def __init__(self, method_name):
        super(TestSIPRoutingClientE2EAsync, self).__init__(method_name)

    def setUp(self):
        super(TestSIPRoutingClientE2EAsync, self).setUp()

        self._sip_routing_client = SIPRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=self._get_http_logging_policy()
        )
        self.recording_processors.extend([URIReplacerProcessor()])

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_sip_configuration(self):
        async with self._sip_routing_client as client:
            configuration = await client.get_sip_configuration()
            assert configuration.trunks is not None, "Configuration returned no trunks."
            assert configuration.routes is not None, "Configuration returned no routes."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_sip_configuration(self):
        new_trunks = {
            "sbs1.contoso.com": {"sipSignalingPort": 1122},
            "sbs2.contoso.com": {"sipSignalingPort": 8888},
        }
        new_routes = [
            {
                "description": "Handle all other numbers''",
                "name": "Updated rule",
                "numberPattern": "\\+[1-9][0-9]{3,23}",
                "trunks": ["sbs1.contoso.com", "sbs2.contoso.com"],
            }
        ]

        async with self._sip_routing_client as client:
            new_configuration = await client.update_sip_configuration(
                new_trunks, new_routes
            )
            assert new_configuration is not None
            assert (
                new_configuration.trunks is not None
            ), "Configuration returned no trunks."
            assert (
                new_configuration.routes is not None
            ), "Configuration returned no routes."

            self._trunks_are_equal(
                new_configuration.trunks, new_trunks
            ), "Configuration trunks were not updated."
            self._routes_are_equal(
                new_configuration.routes, new_routes
            ), "Configuration routes were not updated."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_sip_trunks(self):
        new_trunks = {
            "sbs1.contoso.com": {"sipSignalingPort": 1122},
            "sbs2.contoso.com": {"sipSignalingPort": 8888},
        }

        async with self._sip_routing_client as client:
            new_configuration = await client.update_sip_trunks(
                new_trunks
            )
            assert new_configuration is not None
            assert (
                new_configuration.trunks is not None
            ), "Configuration returned no trunks."

            self._trunks_are_equal(
                new_configuration.trunks, new_trunks
            ), "Configuration trunks were not updated."

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_sip_routes(self):
        new_routes = [
            {
                "description": "Handle all other numbers''",
                "name": "Updated rule",
                "numberPattern": "\\+[1-9][0-9]{3,23}",
                "trunks": ["sbs1.contoso.com", "sbs2.contoso.com"],
            }
        ]

        async with self._sip_routing_client as client:
            new_configuration = await client.update_sip_routes(
                new_routes
            )
            assert new_configuration is not None
            assert (
                new_configuration.routes is not None
            ), "Configuration returned no routes."

            self._routes_are_equal(
                new_configuration.routes, new_routes
            ), "Configuration routes were not updated."

    def _trunks_are_equal(self, response_trunks, request_trunks):
        assert len(response_trunks) == len(request_trunks)

        for k in request_trunks.keys():
            assert (
                response_trunks[k].sip_signaling_port
                == request_trunks[k]["sipSignalingPort"]
            )

    def _routes_are_equal(self, response_routes, request_routes):
        assert len(response_routes) == len(request_routes)

        for k in range(len(request_routes)):
            assert request_routes[k]["description"] == response_routes[k].description
            assert request_routes[k]["name"] == response_routes[k].name
            assert (
                request_routes[k]["numberPattern"] == response_routes[k].number_pattern
            )
            assert request_routes[k]["trunks"] == response_routes[k].trunks