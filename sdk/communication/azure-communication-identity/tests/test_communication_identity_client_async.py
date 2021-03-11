# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.credentials import AccessToken
from azure.communication.identity.aio import CommunicationIdentityClient
from azure.communication.identity import CommunicationTokenScope
from azure.communication.identity._shared.utils import parse_connection_str
from azure_devtools.scenario_tests import RecordingProcessor
from devtools_testutils import ResourceGroupPreparer
from _shared.helper import URIIdentityReplacer
from _shared.asynctestcase  import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor
from _shared.communication_service_preparer import CommunicationServicePreparer
from azure.identity import DefaultAzureCredential

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token
class CommunicationIdentityClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTestAsync, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer()])
    
    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_create_user_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential)
        async with identity_client:
            user = await identity_client.create_user()

        assert user.identifier is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_create_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()

        assert user.identifier is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_create_user_and_token(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_get_token_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential) 
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_get_token(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_revoke_tokens_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential) 
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_revoke_tokens(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_delete_user_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential) 
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.identifier is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    async def test_delete_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.identifier is not None
