# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AccessToken
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.networktraversal import RouteType
from azure.communication.identity._api_versions import ApiVersion
from azure.communication.networktraversal import CommunicationRelayClient
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
            BodyReplacerProcessor(keys=["id", "token", "username", "credential"]),
            URIIdentityReplacer()])

    @CommunicationPreparer()
    def test_get_relay_configuration(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        relay_client = CommunicationRelayClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        print('Getting relay config:\n')
        config = relay_client.get_relay_configuration(user)
        
        print(config.ice_servers)

        for iceServer in config.ice_servers:
            assert iceServer.username is not None
            print('Username: ' + iceServer.username)

            assert iceServer.credential is not None
            print('Credential: ' + iceServer.credential)
            
            assert iceServer.urls is not None
            
            for url in iceServer.urls:
                print('Url: ' + url)
            
            print(iceServer.route_type)
            assert iceServer.route_type is not None

        assert config is not None
    
    @CommunicationPreparer()
    def test_get_relay_configuration_without_identity(self, communication_livetest_dynamic_connection_string):
        
        relay_client = CommunicationRelayClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        print('Getting relay config:\n')
        config = relay_client.get_relay_configuration()
        
        print('Ice Servers: \n')
        for iceServer in config.ice_servers:
            assert iceServer.username is not None
            print('Username: ' + iceServer.username)

            assert iceServer.credential is not None
            print('Credential: ' + iceServer.credential)
            
            assert iceServer.urls is not None
            for url in iceServer.urls:
                print('Url: ' + url)

        assert config is not None

    @CommunicationPreparer()
    def test_get_relay_configuration_with_route_type_nearest(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        relay_client = CommunicationRelayClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        print('Getting relay config with route type nearest:\n')
        config = relay_client.get_relay_configuration(user, RouteType.NEAREST)

        for iceServer in config.ice_servers:
            assert iceServer.username is not None
            print('Username: ' + iceServer.username)

            assert iceServer.credential is not None
            print('Credential: ' + iceServer.credential)
            
            assert iceServer.urls is not None
            for url in iceServer.urls:
                print('Url: ' + url)

            print(iceServer.route_type)
            assert iceServer.route_type == RouteType.NEAREST

        assert config is not None
    
    @CommunicationPreparer()
    def test_get_relay_configuration_with_route_type_any(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        relay_client = CommunicationRelayClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        print('Getting relay config with route type nearest:\n')
        config = relay_client.get_relay_configuration(user, RouteType.ANY)

        for iceServer in config.ice_servers:
            assert iceServer.username is not None
            print('Username: ' + iceServer.username)

            assert iceServer.credential is not None
            print('Credential: ' + iceServer.credential)
            
            assert iceServer.urls is not None
            for url in iceServer.urls:
                print('Url: ' + url)

            print(iceServer.route_type)
            assert iceServer.route_type == RouteType.ANY

        assert config is not None