# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum

from azure.core.pipeline.policies import (
    BearerTokenCredentialPolicy,
)

from ._generated import AzureContainerRegistry
from ._helpers import get_authentication_policy
from ._user_agent import USER_AGENT


class ContainerRegistryApiVersion(str, Enum):
    """Container Registry API version supported by this package"""

    V0_PREVIEW = ""


class ContainerRegistryBaseClient(object):
    def __init__(self, endpoint, credential, **kwargs):
        self._client = AzureContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=BearerTokenCredentialPolicy,
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
