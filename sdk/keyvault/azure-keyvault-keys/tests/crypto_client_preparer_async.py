# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.keys.aio import KeyClient

from _shared.preparer_async import KeyVaultClientPreparer


class CryptoClientPreparer(KeyVaultClientPreparer):
    def __init__(self, *args, **kwargs):
        super().__init__(KeyClient, *args, **kwargs)

    def create_resource(self, _, **kwargs):
        resource = super().create_resource(_, **kwargs)
        credential = self.create_credential()

        return {"key_client": resource["client"], "credential": credential}
