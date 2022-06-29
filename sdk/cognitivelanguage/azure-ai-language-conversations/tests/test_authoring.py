# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import (
    ConversationTest,
    GlobalConversationAccountPreparer
)
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

class TestConversationAuthoring(ConversationTest):

    @pytest.mark.live_test_only
    @GlobalConversationAccountPreparer()
    def test_authoring_aad(self, endpoint, key, conv_project_name, conv_deployment_name):
        token = self.get_credential(ConversationAuthoringClient)
        client = ConversationAuthoringClient(endpoint, token)
        entities = client.list_supported_prebuilt_entities(language="en")
        for entity in entities:
            assert entity
