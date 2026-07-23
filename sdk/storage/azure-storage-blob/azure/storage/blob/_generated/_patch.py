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
from azure.core.pipeline import Pipeline

from .._shared.policies import RangeHeaderPolicy
from ._utils.serialization import Deserializer, Serializer
from .operations import (
    AppendBlobOperations,
    BlobOperations,
    BlockBlobOperations,
    ContainerOperations,
    PageBlobOperations,
    ServiceOperations,
)
from ._client import BlobClient as GeneratedBlobClient
from ._configuration import BlobClientConfiguration as GeneratedBlobClientConfiguration

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


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

        self.url = url
        self.credential = credential
        self.version: str = kwargs.pop("version", "2026-12-06")


class AzureBlobStorage(GeneratedBlobClient):
    """Subclass of the generated BlobClient that allows optional credentials
    and uses a pre-built pipeline.

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

        if pipeline is None:
            raise ValueError("Parameter 'pipeline' must not be None.")

        _endpoint = "{url}"
        self._config = BlobClientConfiguration(url=url, credential=credential, **kwargs)
        _impl_policies = list(pipeline._impl_policies)  # pylint: disable=protected-access
        # ``_impl_policies`` holds ``_SansIOHTTPPolicyRunner`` wrappers, not the raw
        # policies, so unwrap ``_policy`` before checking to avoid inserting a duplicate.
        if not any(
            isinstance(getattr(policy, "_policy", policy), RangeHeaderPolicy)  # pylint: disable=protected-access
            for policy in _impl_policies
        ):
            _impl_policies.insert(0, RangeHeaderPolicy())
        _wrapped_pipeline = Pipeline(
            transport=pipeline._transport,  # pylint: disable=protected-access
            policies=_impl_policies,
        )
        self._client = PipelineClient(base_url=_endpoint, pipeline=_wrapped_pipeline)

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
