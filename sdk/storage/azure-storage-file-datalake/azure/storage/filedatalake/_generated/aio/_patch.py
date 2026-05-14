# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, TYPE_CHECKING

from azure.core import AsyncPipelineClient
from azure.core.pipeline import AsyncPipeline

from ._client import DataLakeClient as GeneratedDataLakeClient
from .._patch import DataLakeClientConfiguration, RangeHeaderPolicy

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class DataLakeClient(GeneratedDataLakeClient):
    """Async subclass of the generated DataLakeClient that allows optional credentials,
    accepts a pre-built pipeline, and injects the RangeHeaderPolicy.
    """

    def __init__(
        self, url: str, credential: Optional["AsyncTokenCredential"] = None, *, pipeline: Any = None, **kwargs: Any
    ) -> None:
        from azure.core.pipeline import policies

        from .._utils.serialization import Deserializer, Serializer
        from .operations import FileSystemOperations, PathOperations, ServiceOperations

        _endpoint = "{url}"
        self._config = DataLakeClientConfiguration(url=url, credential=credential, **kwargs)

        if pipeline is not None:
            _wrapped_pipeline = AsyncPipeline(
                transport=pipeline._transport,
                policies=[RangeHeaderPolicy()] + list(pipeline._impl_policies),
            )
            self._client = AsyncPipelineClient(base_url=_endpoint, pipeline=_wrapped_pipeline)
        else:
            _policies = kwargs.pop("policies", None)
            if _policies is None:
                _policies = [
                    RangeHeaderPolicy(),
                    policies.RequestIdPolicy(**kwargs),
                    self._config.headers_policy,
                    self._config.user_agent_policy,
                    self._config.proxy_policy,
                    policies.ContentDecodePolicy(**kwargs),
                    self._config.redirect_policy,
                    self._config.retry_policy,
                    self._config.authentication_policy,
                    self._config.custom_hook_policy,
                    self._config.logging_policy,
                    policies.DistributedTracingPolicy(**kwargs),
                    policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                    self._config.http_logging_policy,
                ]
            self._client = AsyncPipelineClient(base_url=_endpoint, policies=_policies, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False
        self.service = ServiceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.file_system = FileSystemOperations(self._client, self._config, self._serialize, self._deserialize)
        self.path = PathOperations(self._client, self._config, self._serialize, self._deserialize)


__all__: list[str] = ["DataLakeClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
