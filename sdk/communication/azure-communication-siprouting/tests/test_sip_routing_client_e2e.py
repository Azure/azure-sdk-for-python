# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

from testcases.communication_testcase import CommunicationTestCase
from testcases.request_replacer_processor import RequestReplacerProcessor
from azure.communication.siprouting import SIPRoutingClient


class TestSIPRoutingClientE2E(CommunicationTestCase):
    def __init__(self, method_name):
        super(TestSIPRoutingClientE2E, self).__init__(method_name)
        os.environ[
            "COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING"
        ] = "endpoint=https://resource3.int.communication.azure.net/;accesskey=ot8jPBj4/+uWeh0mLH88/RpTz46gcCZf879nTZ+UH2GsYWHVfX75i78sYxL3aAdVpv+jkd/kcpYs15LN2GPIMg=="

    def setUp(self):
        super(TestSIPRoutingClientE2E, self).setUp()

        self._sip_routing_client = SIPRoutingClient.from_connection_string(
            self.connection_str, http_logging_policy=self._get_http_logging_policy()
        )
        self.recording_processors.extend([RequestReplacerProcessor()])

    def test_get_sip_configuration(self):
        raised = False

        try:
            configuration = self._sip_routing_client.get_sip_configuration()
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        assert configuration.trunks is not None, "Configuration returned no trunks."
        assert configuration.routes is not None, "Configuration returned no routes."

    def test_update_sip_configuration(self):
        raised = False
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

        try:
            new_configuration = self._sip_routing_client.update_sip_configuration(
                new_trunks, new_routes
            )
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        self._trunks_are_equal(
            new_configuration.trunks, new_trunks
        ), "Configuration trunks were not updated."
        self._routes_are_equal(
            new_configuration.routes, new_routes
        ), "Configuration routes were not updated."

    def test_update_sip_trunks(self):
        raised = False
        new_trunks = {
            "sbs1.contoso.com": {"sipSignalingPort": 1122},
            "sbs2.contoso.com": {"sipSignalingPort": 8888},
        }

        try:
            new_configuration = self._sip_routing_client.update_sip_trunks(new_trunks)
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
        self._trunks_are_equal(
            new_configuration.trunks, new_trunks
        ), "Configuration trunks were not updated."

    def test_update_sip_routes(self):
        raised = False
        new_routes = [
            {
                "description": "Handle all other numbers''",
                "name": "Updated rule",
                "numberPattern": "\\+[1-9][0-9]{3,23}",
                "trunks": ["sbs1.contoso.com", "sbs2.contoso.com"],
            }
        ]

        try:
            new_configuration = self._sip_routing_client.update_sip_routes(new_routes)
        except Exception as e:
            raised = True
            ex = str(e)

        assert raised is False, "Exception:" + ex + " was thrown."
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
