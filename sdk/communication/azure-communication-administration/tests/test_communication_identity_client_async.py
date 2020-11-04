# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.administration.aio import CommunicationIdentityClient
from azure_devtools.scenario_tests import RecordingProcessor
from devtools_testutils import ResourceGroupPreparer
from _shared.helper import URIIdentityReplacer
from _shared.asynctestcase  import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor
from _shared.communication_service_preparer import CommunicationServicePreparer

class CommunicationIdentityClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTestAsync, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token"]),
            URIIdentityReplacer()])

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()

        assert user.identifier is not None

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_issue_token(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.issue_token(user, scopes=["chat"])

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_revoke_tokens(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.issue_token(user, scopes=["chat"])
            await identity_client.revoke_tokens(user)

        assert user.identifier is not None
        assert token_response.token is not None

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @CommunicationServicePreparer(use_cache=True)
    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_user(self, connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.identifier is not None
