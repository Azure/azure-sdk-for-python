# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from typing import TYPE_CHECKING, Optional

from azure.core.pipeline.transport import AsyncHttpTransport

from ._async_authentication_policy import ContainerRegistryChallengePolicy
from .._generated.aio import ContainerRegistry
from .._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class ContainerRegistryApiVersion(str, Enum):
    """Container Registry API version supported by this package"""

    V0_PREVIEW = ""


class ContainerRegistryBaseClient(object):
    """Base class for ContainerRegistryClient, ContainerRepository, and RegistryArtifact

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :param credential: AAD Token for authenticating requests with Azure
    :type credential: :class:`~azure.identity.DefaultTokenCredential`
    :keyword authentication_scope: URL for credential authentication if different from the default
    :paramtype authentication_scope: str
    """

    def __init__(self, endpoint: str, credential: Optional["AsyncTokenCredential"] = None, **kwargs) -> None:
        auth_policy = ContainerRegistryChallengePolicy(credential, endpoint, **kwargs)
        self._client = ContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=auth_policy,
            credential_scopes=kwargs.get("credential_scopes", "https://management.core.windows.net/.default"),
            **kwargs
        )

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        await self._client.close()

    def _is_tag(self, tag_or_digest: str) -> bool:  # pylint: disable=no-self-use
        tag = tag_or_digest.split(":")
        return not (len(tag) == 2 and tag[0].startswith(u"sha"))


class AsyncTransportWrapper(AsyncHttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
    """

    def __init__(self, async_transport):
        self._transport = async_transport

    async def send(self, request, **kwargs):
        return await self._transport.send(request, **kwargs)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):  # pylint: disable=arguments-differ
        pass
