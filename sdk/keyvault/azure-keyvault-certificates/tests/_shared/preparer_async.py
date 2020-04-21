# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.identity.aio import DefaultAzureCredential
from azure.identity import KnownAuthorities

from .preparer import KeyVaultClientPreparer as _KeyVaultClientPreparer
from .helpers_async import get_completed_future


class KeyVaultClientPreparer(_KeyVaultClientPreparer):
    def create_credential(self):
        if self.is_live:
            return DefaultAzureCredential(authority=os.environ.get('AZURE_AUTHORITY_HOST', KnownAuthorities.AZURE_PUBLIC_CLOUD))

        return Mock(get_token=lambda *_: get_completed_future(AccessToken("fake-token", 0)))
