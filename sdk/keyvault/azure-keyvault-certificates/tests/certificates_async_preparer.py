# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import AioHttpTransport
from azure.identity.aio import EnvironmentCredential

from multidict import CIMultiDict, CIMultiDictProxy

from certificates_preparer import VaultClientPreparer

from certificates_vault_client_async import VaultClient


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """

    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class NoSleepTransport(AiohttpTestTransport):
    """Prevents the transport from sleeping, e.g. to observe a Retry-After header"""

    async def sleep(self, _):
        return


class AsyncVaultClientPreparer(VaultClientPreparer):
    def create_vault_client(self, vault_uri):
        if self.is_live:
            credential = EnvironmentCredential()
            transport = AiohttpTestTransport()
        else:
            credential = Mock(get_token=asyncio.coroutine(lambda _: AccessToken("fake-token", 0)))
            transport = NoSleepTransport()

        return VaultClient(vault_uri, credential, transport=transport, is_live=self.is_live, **self.client_kwargs)
