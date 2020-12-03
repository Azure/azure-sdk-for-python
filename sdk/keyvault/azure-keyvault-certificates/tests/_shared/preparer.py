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
from devtools_testutils import AzureMgmtPreparer, CachedResourceGroupPreparer, KeyVaultPreparer


class KeyVaultClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, name_prefix="vault", random_name_enabled=True, **kwargs):
        super(KeyVaultClientPreparer, self).__init__(name_prefix, 24, random_name_enabled=random_name_enabled, **kwargs)
        self._client_cls = client_cls

    def create_credential(self):
        if self.is_live:
            return EnvironmentCredential()

        return Mock(get_token=lambda *_: AccessToken("fake-token", 0))

    def create_resource(self, _, **kwargs):
        credential = self.create_credential()
        client = self._client_cls(kwargs.get("vault_uri"), credential, **self.client_kwargs)
        return {"client": client}


class CachedKeyVaultPreparer(KeyVaultPreparer):
    def __init__(self, *args, **kwargs):
        super(CachedKeyVaultPreparer, self).__init__(*args, **kwargs)
        self.set_cache(True, self.parameter_name)

    def create_resource(self, name, **kwargs):
        if self.is_live and self.resource_group_parameter_name not in kwargs:
            rg_preparer = CachedResourceGroupPreparer()
            _, kwargs = rg_preparer._prepare_create_resource(self.test_class_instance, **kwargs)
        return super(CachedKeyVaultPreparer, self).create_resource(name, **kwargs)
