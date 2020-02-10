# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

from azure.core.credentials import AccessToken
from azure.identity import EnvironmentCredential

from devtools_testutils import AzureMgmtPreparer

from keys_vault_client import VaultClient


class VaultClientPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        enable_soft_delete=None,
        name_prefix="vault",
        parameter_name="vault_client",
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True
    ):
        super(VaultClientPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled
        )
        self.parameter_name = parameter_name

    def create_resource(self, name, **kwargs):
        client = self.create_vault_client(kwargs.get("vault_uri"))
        return {self.parameter_name: client}

    def create_vault_client(self, vault_uri):
        if self.is_live:
            credential = EnvironmentCredential()
        else:
            credential = Mock(get_token=lambda _: AccessToken("fake-token", 0))
        return VaultClient(vault_uri, credential, is_live=self.is_live, **self.client_kwargs)
