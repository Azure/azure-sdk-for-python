# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from testcase import (
    ConversationTest,
    GlobalConversationAccountPreparer
)
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

class TestConversationAuthoringAsync(ConversationTest):

    @pytest.mark.live_test_only
    @GlobalConversationAccountPreparer()
    async def test_authoring_aad(self, endpoint):
        token = self.get_credential(ConversationAuthoringClient, is_async=True)
        client = ConversationAuthoringClient(endpoint, token, api_version="2022-05-01")
        entities = client.list_supported_prebuilt_entities(language="en")
        async for entity in entities:
            assert entity
