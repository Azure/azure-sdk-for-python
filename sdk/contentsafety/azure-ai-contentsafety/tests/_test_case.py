# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase, is_live, FakeTokenCredential

from azure.ai.contentsafety import ContentSafetyClient, BlocklistClient


class ClientPreparer(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        self.endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
        self.key = os.environ["CONTENT_SAFETY_KEY"]
        self.use_key_credential = kwargs.pop("use_key_credential", True)
        self.create_content_safety_client = kwargs.pop("create_content_safety_client", True)
        self.create_blocklist_client = kwargs.pop("create_blocklist_client", False)
        if is_live():
            os.environ["AZURE_TENANT_ID"] = os.environ["CONTENT_SAFETY_TENANT_ID"]
            os.environ["AZURE_CLIENT_ID"] = os.environ["CONTENT_SAFETY_CLIENT_ID"]
            os.environ["AZURE_CLIENT_SECRET"] = os.environ["CONTENT_SAFETY_CLIENT_SECRET"]

    def __call__(self, fn):
        def _preparer(test_class, **kwargs):
            content_safety_client = self.create_client(ContentSafetyClient, **kwargs)
            blocklist_client = self.create_client(BlocklistClient, **kwargs)
            if self.create_content_safety_client and self.create_blocklist_client:
                fn(test_class, content_safety_client, blocklist_client)
            elif self.create_blocklist_client:
                fn(test_class, blocklist_client)
            else:
                fn(test_class, content_safety_client)

        return _preparer

    def create_client(self, client_class, **kwargs):
        if self.use_key_credential:
            return self.create_client_from_credential(
                client_class, credential=AzureKeyCredential(self.key), endpoint=self.endpoint, **kwargs
            )
        else:
            if is_live():
                credential = self.get_credential(ContentSafetyClient)
            else:
                credential = FakeTokenCredential()
            return self.create_client_from_credential(
                ContentSafetyClient, credential=credential, endpoint=self.endpoint, **kwargs
            )
