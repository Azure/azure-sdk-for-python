# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.administration.aio import CommunicationIdentityClient
from azure_devtools.scenario_tests import RecordingProcessor
from helper import URIIdentityReplacer
from _shared.asynctestcase  import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor, ResponseReplacerProcessor

class CommunicationIdentityClientTestAsync(AsyncCommunicationTestCase):

    def setUp(self):
        super(CommunicationIdentityClientTestAsync, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer(),
            ResponseReplacerProcessor(keys=[self._resource_name])])

        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_create_user(self):
        async with self.identity_client:
            user = await self.identity_client.create_user()

        assert user.identifier is not None

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_issue_token(self):
        async with self.identity_client:
            user = await self.identity_client.create_user()
            token_response = await self.identity_client.issue_token(user, scopes=["chat"])

        assert user.identifier is not None
        assert token_response.token is not None

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_revoke_tokens(self):
        async with self.identity_client:
            user = await self.identity_client.create_user()
            token_response = await self.identity_client.issue_token(user, scopes=["chat"])
            await self.identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_delete_user(self):
        async with self.identity_client:
            user = await self.identity_client.create_user()
            await self.identity_client.delete_user(user)

        assert user.identifier is not None
