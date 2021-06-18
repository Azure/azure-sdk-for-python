# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import datetime
from azure.core.credentials import AccessToken
from azure.communication.identity.aio import CommunicationIdentityClient
from azure.communication.identity import CommunicationTokenScope
from azure.communication.identity._shared.utils import parse_connection_str
from azure_devtools.scenario_tests import RecordingProcessor
from devtools_testutils import ResourceGroupPreparer
from _shared.helper import URIIdentityReplacer
from _shared.asynctestcase  import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor
from _shared.communication_service_preparer import CommunicationPreparer
from _shared.utils import get_http_logging_policy
from azure.identity.aio import DefaultAzureCredential

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    async def get_token(self, *args):
        return self.token
class CommunicationIdentityClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTestAsync, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer()])
    
    @CommunicationPreparer()
    async def test_create_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint, 
            credential,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    async def test_create_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    async def test_create_user_and_token(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    async def test_get_token_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint, 
            credential,
            http_logging_policy=get_http_logging_policy()
        ) 
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    async def test_get_token(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    async def test_revoke_tokens_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint, 
            credential,
            http_logging_policy=get_http_logging_policy()
        ) 
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    async def test_revoke_tokens(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    async def test_delete_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint, 
            credential,
            http_logging_policy=get_http_logging_policy()
        ) 
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    async def test_delete_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.properties.get('id') is not None
    
    @CommunicationPreparer()
    async def test_create_user_and_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user, token_response = await identity_client.create_user_and_token(scopes=None)

    @CommunicationPreparer()
    async def test_delete_user_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.delete_user(user=None)

    @CommunicationPreparer()
    async def test_revoke_tokens_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.revoke_tokens(user=None)
    
    @CommunicationPreparer()
    async def test_get_token_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token(user=None, scopes=[CommunicationTokenScope.CHAT])
    
    @CommunicationPreparer()
    async def test_get_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user = await identity_client.create_user()
                token_response = await identity_client.get_token(user, scopes=None)
