# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from devtools_testutils import AzureRecordedTestCase


class TestConversationAuthoringAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    async def test_authoring_aad(self, recorded_test, conversation_creds):
        token = self.get_credential(ConversationAuthoringClient, is_async=True)
        client = ConversationAuthoringClient(conversation_creds["endpoint"], token, api_version="2022-05-01")
        entities = client.list_supported_prebuilt_entities(language="en")
        async for entity in entities:
            assert entity
