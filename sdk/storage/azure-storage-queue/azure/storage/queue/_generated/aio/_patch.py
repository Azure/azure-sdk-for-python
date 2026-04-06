# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, TYPE_CHECKING

from azure.core import AsyncPipelineClient

from .._configuration import QueuesClientConfiguration
from .._utils.serialization import Deserializer, Serializer
from .operations import QueueOperations, ServiceOperations
from ._client import QueuesClient as _QueuesClient

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class QueuesClient(_QueuesClient):
    """QueuesClient that supports being instantiated with a pre-built pipeline."""

    def __init__(self, url: str, credential: "AsyncTokenCredential" = None, **kwargs: Any) -> None:
        _pipeline = kwargs.pop("pipeline", None)
        if _pipeline is not None:
            # When a pre-built pipeline is provided, skip the generated credential/policy setup.
            _endpoint = "{url}"
            self._config = QueuesClientConfiguration.__new__(QueuesClientConfiguration)
            version = kwargs.pop("version", "2026-06-06")
            self._config.url = url
            self._config.credential = credential
            self._config.version = version
            self._client: AsyncPipelineClient = AsyncPipelineClient(base_url=_endpoint, pipeline=_pipeline)
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
