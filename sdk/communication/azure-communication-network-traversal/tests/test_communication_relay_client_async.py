# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AccessToken
from azure.communication.identity.aio import CommunicationIdentityClient
from azure.communication.network.traversal.aio import CommunicationRelayClient
from azure.communication.network.traversal import CommunicationRelayConfigurationRequest
from _shared.helper import URIIdentityReplacer
from _shared.testcase import (
    BodyReplacerProcessor
)
from _shared.asynctestcase  import AsyncCommunicationTestCase
from _shared.communication_service_preparer import CommunicationPreparer
from _shared.utils import get_http_logging_policy
from _shared.utils import parse_connection_str
from azure.identity.aio import DefaultAzureCredential

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class CommunicationRelayClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(CommunicationRelayClientTestAsync, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "username", "credential", "urls"]),
            URIIdentityReplacer()])

    @CommunicationPreparer()
    async def test_get_relay_configuration(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client: 
            user = await identity_client.create_user()        
        request = CommunicationRelayConfigurationRequest(id = user.properties['id'])

        networkTraversalClient = CommunicationRelayClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with networkTraversalClient:
            print('Getting relay config:\n')
            config = await networkTraversalClient.get_relay_configuration(request)
        
        print('Ice Servers Async:\n')
        for iceServer in config.ice_servers:
            print(iceServer)

        assert config is not None
        