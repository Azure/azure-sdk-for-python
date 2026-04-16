# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, TYPE_CHECKING

from azure.core import PipelineClient

from ._configuration import QueuesClientConfiguration as QueuesClientConfigurationInternal
from ._utils.serialization import Deserializer, Serializer
from .operations import QueueOperations, ServiceOperations
from ._client import QueuesClient as QueuesClientInternal
from ._version import VERSION

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

class QueuesClientConfiguration(QueuesClientConfigurationInternal):
    """Configuration for QueuesClient.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param url: The host name of the queue storage account, e.g.
     accountName.queue.core.windows.net. Required.
    :type url: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword version: Specifies the version of the operation to use for this request. Known values
     are "2026-04-06". Default value is "2026-04-06". Note that overriding this default value may
     result in unsupported behavior.
    :paramtype version: str
    """

    def __init__(self, url: str, credential: Optional["TokenCredential"] = None, **kwargs: Any) -> None:
        version: str = kwargs.pop("version", "2026-04-06")

        if url is None:
            raise ValueError("Parameter 'url' must not be None.")
        
        self.url = url
        self.credential = credential
        self.version = version
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://storage.azure.com/.default"])
        kwargs.setdefault("sdk_moniker", "storage-queue/{}".format(VERSION))
        self.polling_interval = kwargs.get("polling_interval", 30)
        self._configure(**kwargs)

class QueuesClient(QueuesClientInternal):
    """QueuesClient that supports being instantiated with a pre-built pipeline."""

    def __init__(self, url: str, credential: Optional["TokenCredential"] = None, **kwargs: Any) -> None:
        _pipeline = kwargs.pop("pipeline", None)
        if _pipeline is not None:
            self._config = QueuesClientConfiguration(url=url, credential=credential, **kwargs)
            self._client: PipelineClient = PipelineClient(base_url="{url}", pipeline=_pipeline)
            self._serialize = Serializer()
            self._deserialize = Deserializer()
            self._serialize.client_side_validation = False
            self.service = ServiceOperations(self._client, self._config, self._serialize, self._deserialize)
            self.queue = QueueOperations(self._client, self._config, self._serialize, self._deserialize)
        else:
            super().__init__(url, credential, **kwargs)


__all__: list[str] = ["QueuesClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
