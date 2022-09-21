# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from devtools_testutils import AzureRecordedTestCase


class TestConversationAuthoring(AzureRecordedTestCase):

    def test_authoring_aad(self, recorded_test, conversation_creds):
        token = self.get_credential(ConversationAuthoringClient)
        client = ConversationAuthoringClient(conversation_creds["endpoint"], token, api_version="2022-05-01")
        entities = client.list_supported_prebuilt_entities(language="en")
        for entity in entities:
            assert entity
