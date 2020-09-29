# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.administration import CommunicationIdentityClient
from helper import URIIdentityReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)

class CommunicationIdentityClientTest(CommunicationTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer()])
        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)

    @pytest.mark.live_test_only
    def test_create_user(self):
        user = self.identity_client.create_user()

        assert user.identifier is not None

    @pytest.mark.live_test_only
    def test_issue_token(self):
        user = self.identity_client.create_user()

        token_response = self.identity_client.issue_token(user, scopes=["chat"])

        assert user.identifier is not None
        assert token_response.token is not None
    
    @pytest.mark.live_test_only
    def test_revoke_tokens(self):
        user = self.identity_client.create_user()

        token_response = self.identity_client.issue_token(user, scopes=["chat"])
        self.identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None
    
    @pytest.mark.live_test_only
    def test_delete_user(self):
        user = self.identity_client.create_user()

        self.identity_client.delete_user(user)

        assert user.identifier is not None
