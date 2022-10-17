# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from devtools_testutils import AzureRecordedTestCase


class TestConversationAuthoringAsync(AzureRecordedTestCase):

    def test_polling_interval(self, conversation_creds):
        # test default
        client = ConversationAuthoringClient(conversation_creds["endpoint"], AzureKeyCredential(conversation_creds["key"]))
        assert client._config.polling_interval == 5
        # test override
        client = ConversationAuthoringClient(conversation_creds["endpoint"], AzureKeyCredential(conversation_creds["key"]), polling_interval=1)
        assert client._config.polling_interval == 1

    @pytest.mark.asyncio
    async def test_authoring_aad(self, recorded_test, conversation_creds):
        token = self.get_credential(ConversationAuthoringClient, is_async=True)
        client = ConversationAuthoringClient(conversation_creds["endpoint"], token)
        entities = client.list_supported_prebuilt_entities(language="en")
        async for entity in entities:
            assert entity
