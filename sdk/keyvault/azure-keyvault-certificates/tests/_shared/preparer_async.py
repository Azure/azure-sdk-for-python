# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import AioHttpTransport
from azure.identity.aio import EnvironmentCredential

from .preparer import KeyVaultClientPreparer as _KeyVaultClientPreparer
from .helpers_async import get_completed_future


class NoSleepTransport(AioHttpTransport):
    """Prevents the transport from sleeping, e.g. to observe a Retry-After header"""

    async def sleep(self, _):
        return


class KeyVaultClientPreparer(_KeyVaultClientPreparer):
    POLLING_METHOD_PREFIXES = ("create_", "delete_", "recover_")  # type: ignore

    def create_credential(self):
        if self.is_live:
            return EnvironmentCredential()

        return Mock(get_token=lambda *_: get_completed_future(AccessToken("fake-token", 0)))

    def create_transport(self):
        if self.is_live:
            return AioHttpTransport()

        return NoSleepTransport()

    def create_resource(self, _, **kwargs):
        credential = self.create_credential()
        self.client_kwargs["transport"] = self.create_transport()
        client = self.create_client(kwargs.get("vault_uri"), credential)

        return {"client": client}
