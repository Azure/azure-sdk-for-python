# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import RequestsTransport
from azure.identity import EnvironmentCredential

from devtools_testutils import AzureMgmtPreparer


class NoSleepTransport(RequestsTransport):
    """Prevents the transport from sleeping, e.g. to observe a Retry-After header"""

    def sleep(self, _):
        return


class KeyVaultClientPreparer(AzureMgmtPreparer):
    POLLING_METHOD_PREFIXES = ("begin_",)

    def __init__(self, client_cls, name_prefix="vault", random_name_enabled=True, **kwargs):
        super(KeyVaultClientPreparer, self).__init__(name_prefix, 24, random_name_enabled=random_name_enabled, **kwargs)
        self._client_cls = client_cls

    def create_credential(self):
        if self.is_live:
            return EnvironmentCredential()

        return Mock(get_token=lambda *_: AccessToken("fake-token", 0))

    def create_transport(self):
        if self.is_live:
            return RequestsTransport()

        return NoSleepTransport()

    def create_resource(self, _, **kwargs):
        credential = self.create_credential()
        self.client_kwargs["transport"] = self.create_transport()
        client = self.create_client(kwargs.get("vault_uri"), credential)

        return {"client": client}

    def create_client(self, vault_uri, credential):
        client = self._client_cls(vault_uri, credential, **self.client_kwargs)
        if not self.is_live:
            # ensure pollers don't sleep during playback
            for attr in dir(client):
                if any(attr.startswith(prefix) for prefix in self.POLLING_METHOD_PREFIXES):
                    fn = getattr(client, attr)
                    wrapper = functools.partial(fn, _polling_interval=0)
                    setattr(client, attr, wrapper)

        return client
