# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from typing import TYPE_CHECKING, Dict, Any, Optional

from azure.core.pipeline.transport import HttpTransport

from ._authentication_policy import ContainerRegistryChallengePolicy
from ._generated import ContainerRegistry
from ._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential



class ContainerRegistryApiVersion(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta
    """Container Registry API version supported by this package"""

    V0_PREVIEW = ""


class ContainerRegistryBaseClient(object): # pylint: disable=client-accepts-api-version-keyword
    """Base class for ContainerRegistryClient

    :param str endpoint: Azure Container Registry endpoint
    :param credential: AAD Token for authenticating requests with Azure
    :type credential: ~azure.identity.DefaultTokenCredential
    :keyword credential_scopes: URL for credential authentication if different from the default
    :paramtype credential_scopes: List[str]
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Optional[TokenCredential], Dict[str, Any]) -> None
        self._auth_policy = ContainerRegistryChallengePolicy(credential, endpoint, **kwargs)
        self._client = ContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=self._auth_policy,
            **kwargs
        )

    def __enter__(self):
        self._client.__enter__()
        self._auth_policy.__enter__()
        return self

    def __exit__(self, *args):
        self._auth_policy.__exit__(*args)
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
