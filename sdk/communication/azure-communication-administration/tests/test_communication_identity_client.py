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

class CommunicationIdentityClientTest(CommunicationTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer()])

    @pytest.mark.live_test_only
    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    def test_create_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        assert user.identifier is not None

    @pytest.mark.live_test_only
    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    def test_issue_token(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        token_response = identity_client.issue_token(user, scopes=["chat"])

        assert user.identifier is not None
        assert token_response.token is not None
    
    @pytest.mark.live_test_only
    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    def test_revoke_tokens(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        token_response = identity_client.issue_token(user, scopes=["chat"])
        identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None
    
    @pytest.mark.live_test_only
    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    def test_delete_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            connection_string)
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.identifier is not None
