# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.identity import CommunicationTokenScope
from azure.core.credentials import AccessToken
from _shared.helper import URIIdentityReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)
from devtools_testutils import ResourceGroupPreparer
from _shared.communication_service_preparer import CommunicationServicePreparer 
from azure.identity import DefaultAzureCredential
from azure.communication.identity._shared.utils import parse_connection_str

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class CommunicationIdentityClientTest(CommunicationTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer()])
    
    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_create_user_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential)
        user = identity_client.create_user()

        assert user.identifier is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_create_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        assert user.identifier is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_create_user_and_token(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        user, token_response = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_get_token_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential)
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_get_token(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_revoke_tokens_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential)
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_revoke_tokens(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_delete_user_from_managed_identity(self, connection_string):
        endpoint, access_key = parse_connection_str(connection_string)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(endpoint, credential)
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.identifier is not None

    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_delete_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.identifier is not None
