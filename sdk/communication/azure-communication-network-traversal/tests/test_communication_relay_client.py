# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AccessToken
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.network.traversal import CommunicationRelayClient, CommunicationRelayConfigurationRequest
from _shared.helper import URIIdentityReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)
from _shared.communication_service_preparer import CommunicationPreparer
from _shared.utils import get_http_logging_policy
from azure.identity import DefaultAzureCredential
from azure.communication.identity._shared.utils import parse_connection_str

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class CommunicationRelayClientTest(CommunicationTestCase):
    def setUp(self):
        super(CommunicationRelayClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "expiresOn", "username", "credential", "urls"]),
            URIIdentityReplacer()])

    @CommunicationPreparer()
    def test_get_relay_configuration(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()
        request = CommunicationRelayConfigurationRequest(id = user.properties['id'])

        relay_client = CommunicationRelayClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        print('Getting relay config:\n')
        config = relay_client.get_relay_configuration(request)
        
        print('Ice Servers: \n')
        for iceServer in config.ice_servers:
            print(iceServer)

        assert config is not None
        