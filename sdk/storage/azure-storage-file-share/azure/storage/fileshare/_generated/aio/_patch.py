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
from azure.core.pipeline import AsyncPipeline, PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy

from ._client import FileClient as GeneratedFileClient
from ._configuration import FileClientConfiguration as GeneratedFileClientConfiguration

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class RangeHeaderPolicy(SansIOHTTPPolicy):
    """Policy that converts the 'Range' header to 'x-ms-range'."""

    def on_request(self, request: PipelineRequest) -> None:
        range_value = request.http_request.headers.pop("Range", None)
        if range_value is not None:
            request.http_request.headers["x-ms-range"] = range_value


class FileClientConfiguration(GeneratedFileClientConfiguration):
    """Configuration for FileClient that allows optional credentials.

    This class overrides the generated configuration to allow None credentials
    for anonymous access or when a pre-built pipeline handles auth.

    :param url: The URL of the service account, share, directory or file that is the target of the
     desired operation. Required.
    :type url: str
    :param credential: Credential used to authenticate requests to the service. Can be None.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or None
    :keyword version: Specifies the version of the operation to use for this request.
    :paramtype version: str
    """

    def __init__(self, url: str, credential: Optional["AsyncTokenCredential"] = None, **kwargs: Any) -> None:
        if url is None:
            raise ValueError("Parameter 'url' must not be None.")

        version: str = kwargs.pop("version", "2026-06-06")
        self.url = url
        self.credential = credential
        self.version = version
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://storage.azure.com/.default"])
        from .._version import VERSION

        kwargs.setdefault("sdk_moniker", "storage-file-share/{}".format(VERSION))
        self.polling_interval = kwargs.get("polling_interval", 30)
        self._configure(**kwargs)


class AzureFileStorage(GeneratedFileClient):
    """Subclass of the generated FileClient that allows optional credentials,
    accepts a pre-built pipeline, and injects the RangeHeaderPolicy.

    :param url: The URL of the service account, share, directory or file.
    :type url: str
    :param credential: Credential used to authenticate requests to the service.
     Can be None when a pre-built pipeline is provided.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or None
    :keyword pipeline: A pre-built pipeline to use instead of constructing one.
    :paramtype pipeline: ~azure.core.pipeline.Pipeline
    :keyword version: Specifies the version of the operation to use for this request.
    :paramtype version: str
    """

    def __init__(
        self, url: str, credential: Optional["AsyncTokenCredential"] = None, *, pipeline: Any = None, **kwargs: Any
    ) -> None:
        from azure.core.pipeline import policies

        from .._utils.serialization import Deserializer, Serializer
        from .operations import DirectoryOperations, FileOperations, ServiceOperations, ShareOperations

        _endpoint = "{url}"
        self._config = FileClientConfiguration(url=url, credential=credential, **kwargs)

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
        self.share = ShareOperations(self._client, self._config, self._serialize, self._deserialize)
        self.directory = DirectoryOperations(self._client, self._config, self._serialize, self._deserialize)
        self.file = FileOperations(self._client, self._config, self._serialize, self._deserialize)


# Alias so that `from ._patch import *` overrides the generated FileClient
FileClient = AzureFileStorage


__all__: list[str] = ["FileClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
