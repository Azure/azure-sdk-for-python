# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from typing import Any, Callable, Mapping, TYPE_CHECKING
from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline.transport import AsyncioRequestsTransport, HttpTransport
from msrest.serialization import Model

from azure.keyvault.secrets._shared import AsyncKeyVaultClientBase
from azure.keyvault.secrets.aio import SecretClient

if TYPE_CHECKING:
    try:
        from azure.core.credentials import TokenCredential
    except ImportError:
        # TokenCredential is a typing_extensions.Protocol; we don't depend on that package
        pass

KEY_VAULT_SCOPE = "https://vault.azure.net/.default"


class VaultClient(AsyncKeyVaultClientBase):
    def __init__(
        self,
        vault_url: str,
        credential: "TokenCredential",
        transport: HttpTransport = None,
        api_version: str = None,
        is_live: bool = True,
        **kwargs: Any
    ) -> None:
        super(VaultClient, self).__init__(vault_url, credential, transport=transport, api_version=api_version, **kwargs)
        self._secrets = SecretClient(self.vault_url, credential, generated_client=self._client, **kwargs)
        if not is_live:
            # ensure pollers don't sleep during playback
            self._secrets.delete_secret = functools.partial(self._secrets.delete_secret, _polling_interval=0)
            self._secrets.recover_deleted_secret = functools.partial(
                self._secrets.recover_deleted_secret, _polling_interval=0
            )

    @property
    def secrets(self):
        return self._secrets
