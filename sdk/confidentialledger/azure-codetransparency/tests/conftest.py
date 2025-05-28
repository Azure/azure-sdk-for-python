# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy

from azure.codetransparency import CodeTransparencyClient
from azure.codetransparency._version import VERSION

from devtools_testutils import (
    AzureRecordedTestCase,
    AzurePreparer
)

CREDENTIAL = AzureKeyCredential(key="test-api-key")

class FakeTokenCredential:
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = "Bearer fake-token"

    def get_token(self, *args, **kwargs):
        from azure.core.credentials import AccessToken
        return AccessToken(token=self.token, expires_on=42)


class CodeTransparencyClientPreparer(AzurePreparer):
    def __init__(self):
        super(CodeTransparencyClientPreparer, self).__init__(name_prefix="codetransparency")
        self.endpoint = os.getenv("CODETRANSPARENCY_ENDPOINT", "https://fake-endpoint.confidentialledger.azure.com")

    def create_code_transparency_client(self, **kwargs):
        """Create a CodeTransparencyClient client for testing."""
        credential = kwargs.pop("credential", CREDENTIAL)
        endpoint = kwargs.pop("endpoint", self.endpoint)
        kwargs.setdefault("api_version", "2025-01-31-preview")
        client = CodeTransparencyClient(
            endpoint=endpoint,
            credential=credential,
            **kwargs
        )
        return client


@pytest.fixture
def client():
    """Create a CodeTransparencyClient client fixture."""
    return CodeTransparencyClientPreparer().create_code_transparency_client()
