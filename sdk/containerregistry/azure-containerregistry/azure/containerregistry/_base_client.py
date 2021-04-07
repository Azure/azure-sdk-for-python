# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from typing import TYPE_CHECKING

from azure.core.pipeline.transport import HttpTransport

from ._authentication_policy import ContainerRegistryChallengePolicy
from ._generated import ContainerRegistry
from ._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class ContainerRegistryApiVersion(str, Enum):
    """Container Registry API version supported by this package"""

    V0_PREVIEW = ""


class ContainerRegistryBaseClient(object):
    """Base class for ContainerRegistryClient and ContainerRepositoryClient

    :param str endpoint: Azure Container Registry endpoint
    :param credential: AAD Token for authenticating requests with Azure
    :type credential: :class:`azure.identity.DefaultTokenCredential`
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, TokenCredential, Dict[str, Any]) -> None
        auth_policy = ContainerRegistryChallengePolicy(credential, endpoint)
        self._client = ContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=auth_policy,
            credential_scopes="https://management.core.windows.net/.default",
            **kwargs
        )

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self):
        # type: () -> None
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()


class TransportWrapper(HttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
    """

    def __init__(self, transport):
        self._transport = transport

    def send(self, request, **kwargs):
        return self._transport.send(request, **kwargs)

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *args):  # pylint: disable=arguments-differ
        pass
