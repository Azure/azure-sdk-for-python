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
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy

from ._client import BlobClient as GeneratedBlobClient
from ._configuration import BlobClientConfiguration as GeneratedBlobClientConfiguration

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class RangeHeaderPolicy(SansIOHTTPPolicy):
    """Policy that converts the 'Range' header to 'x-ms-range'."""

    def on_request(self, request: PipelineRequest) -> None:
        range_value = request.http_request.headers.pop("Range", None)
        if range_value is not None:
            request.http_request.headers["x-ms-range"] = range_value


class BlobClientConfiguration(GeneratedBlobClientConfiguration):
    """Configuration for BlobClient that allows optional credentials.

    This class overrides the generated configuration to allow None credentials
    for anonymous access to public blobs.

    :param url: The host name of the blob storage account, e.g. accountName.blob.core.windows.net.
     Required.
    :type url: str
    :param credential: Credential used to authenticate requests to the service. Can be None for
     anonymous access.
    :type credential: ~azure.core.credentials.TokenCredential or None
    :keyword version: Specifies the version of the operation to use for this request.
    :paramtype version: str
    """

    def __init__(self, url: str, credential: Optional["TokenCredential"] = None, **kwargs: Any) -> None:
        if url is None:
            raise ValueError("Parameter 'url' must not be None.")

        version: str = kwargs.pop("version", "2026-04-06")
        self.url = url
        self.credential = credential
        self.version = version
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://storage.azure.com/.default"])
        from ._version import VERSION

        kwargs.setdefault("sdk_moniker", "storage-blob/{}".format(VERSION))
        self.polling_interval = kwargs.get("polling_interval", 30)
        self._configure(**kwargs)


class AzureBlobStorage(GeneratedBlobClient):
    """Subclass of the generated BlobClient that allows optional credentials,
    accepts a pre-built pipeline, and injects the RangeHeaderPolicy.

    :param url: The host name of the blob storage account.
    :type url: str
    :param credential: Credential used to authenticate requests to the service.
     Can be None for anonymous access.
    :type credential: ~azure.core.credentials.TokenCredential or None
    :keyword pipeline: A pre-built pipeline to use instead of constructing one.
    :paramtype pipeline: ~azure.core.pipeline.Pipeline
    :keyword version: Specifies the version of the operation to use for this request.
    :paramtype version: str
    """

    def __init__(
        self, url: str, credential: Optional["TokenCredential"] = None, *, pipeline: Any = None, **kwargs: Any
    ) -> None:
        from azure.core.pipeline import policies

        from ._utils.serialization import Deserializer, Serializer
        from .operations import (
            AppendBlobOperations,
            BlobOperations,
            BlockBlobOperations,
            ContainerOperations,
            PageBlobOperations,
            ServiceOperations,
        )

        _endpoint = "{url}"
        self._config = BlobClientConfiguration(url=url, credential=credential, **kwargs)

        if pipeline is not None:
            self._client = PipelineClient(base_url=_endpoint, pipeline=pipeline)
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
            self._client = PipelineClient(base_url=_endpoint, policies=_policies, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        self.service = ServiceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.container = ContainerOperations(self._client, self._config, self._serialize, self._deserialize)
        self.blob = BlobOperations(self._client, self._config, self._serialize, self._deserialize)
        self.append_blob = AppendBlobOperations(self._client, self._config, self._serialize, self._deserialize)
        self.block_blob = BlockBlobOperations(self._client, self._config, self._serialize, self._deserialize)
        self.page_blob = PageBlobOperations(self._client, self._config, self._serialize, self._deserialize)


__all__: list[str] = ["AzureBlobStorage"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
