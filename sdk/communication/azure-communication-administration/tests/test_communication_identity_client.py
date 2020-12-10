# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.administration import CommunicationIdentityClient
from _shared.helper import URIIdentityReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)
from devtools_testutils import ResourceGroupPreparer
from _shared.communication_service_preparer import CommunicationServicePreparer 
from azure.identity import DefaultAzureCredential

class CommunicationIdentityClientTest(CommunicationTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer()])
    
    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_create_user_from_managed_identity(self, connection_string):
        endpoint = self.get_endpoint_from_connection_string(connection_string)
        identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
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
    def test_issue_token(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        token_response = identity_client.issue_token(user, scopes=["chat"])

        assert user.identifier is not None
        assert token_response.token is not None
    
    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_revoke_tokens(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        token_response = identity_client.issue_token(user, scopes=["chat"])
        identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None
    
    @ResourceGroupPreparer(random_name_enabled=True)
    @CommunicationServicePreparer()
    def test_delete_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.identifier is not None
    
    def get_endpoint_from_connection_string(self, connection_string):
        return connection_string.split("=")[1].split("/;")[0]
