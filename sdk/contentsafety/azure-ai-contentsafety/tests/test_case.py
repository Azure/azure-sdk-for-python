# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase, is_live, FakeTokenCredential, EnvironmentVariableLoader

from azure.ai.contentsafety import ContentSafetyClient, BlocklistClient


class ContentSafetyTest(AzureRecordedTestCase):
    def create_content_safety_client_from_key(self, endpoint, key):
        return self._create_client_from_key(ContentSafetyClient, endpoint, key)

    def create_blocklist_client_from_key(self, endpoint, key):
        return self._create_client_from_key(BlocklistClient, endpoint, key)

    def create_content_safety_client_from_entra_id(self, endpoint):
        return self._create_client_from_entra_id(ContentSafetyClient, endpoint)

    def create_blocklist_client_from_entra_id(self, endpoint):
        return self._create_client_from_entra_id(BlocklistClient, endpoint)

    def _create_client_from_key(self, client_class, endpoint, key):
        return self.create_client_from_credential(client_class, credential=AzureKeyCredential(key), endpoint=endpoint)

    def _create_client_from_entra_id(self, client_class, endpoint):
        if is_live():
            credential = self.get_credential(client_class)
        else:
            credential = FakeTokenCredential()
        return self.create_client_from_credential(client_class, credential=credential, endpoint=endpoint)


ContentSafetyPreparer = functools.partial(
    EnvironmentVariableLoader,
    "content_safety",
    content_safety_endpoint="https://fake_cs_resource.cognitiveservices.azure.com",
    content_safety_key="00000000000000000000000000000000",
    content_safety_client_id="00000000000000000000000000000000",
    content_safety_client_secret="00000000000000000000000000000000",
    content_safety_tenant_id="00000000000000000000000000000000",
)
