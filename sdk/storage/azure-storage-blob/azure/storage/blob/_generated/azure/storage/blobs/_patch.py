# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, TYPE_CHECKING

from azure.core import PipelineClient
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse

from ._operations import (
    _AppendBlobClientOperationsMixin,
    _BlobClientOperationsMixin,
    _BlockBlobClientOperationsMixin,
    _ContainerClientOperationsMixin,
    _PageBlobClientOperationsMixin,
    _ServiceClientOperationsMixin,
)
from ._utils.serialization import Deserializer, Serializer

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class _ServiceOperationsWrapper(_ServiceClientOperationsMixin):
    """Wrapper to provide service operations with shared pipeline client."""

    def __init__(self, config: Any, client: PipelineClient, serialize: Serializer, deserialize: Deserializer) -> None:
        self._config = config
        self._client = client
        self._serialize = serialize
        self._deserialize = deserialize

    # Alias for backward compatibility
    def filter_blobs(self, *args: Any, **kwargs: Any) -> Any:
        """Alias for find_blobs_by_tags for backward compatibility."""
        return self.find_blobs_by_tags(*args, **kwargs)


class _ContainerOperationsWrapper(_ContainerClientOperationsMixin):
    """Wrapper to provide container operations with shared pipeline client."""

    def __init__(self, config: Any, client: PipelineClient, serialize: Serializer, deserialize: Deserializer) -> None:
        self._config = config
        self._client = client
        self._serialize = serialize
        self._deserialize = deserialize

    # Alias for backward compatibility
    def filter_blobs(self, *args: Any, **kwargs: Any) -> Any:
        """Alias for find_blobs_by_tags for backward compatibility."""
        return self.find_blobs_by_tags(*args, **kwargs)


class _BlobOperationsWrapper(_BlobClientOperationsMixin):
    """Wrapper to provide blob operations with shared pipeline client."""

    def __init__(self, config: Any, client: PipelineClient, serialize: Serializer, deserialize: Deserializer) -> None:
        self._config = config
        self._client = client
        self._serialize = serialize
        self._deserialize = deserialize

    # Aliases for backward compatibility
    def set_http_headers(self, *args: Any, **kwargs: Any) -> Any:
        """Alias for set_properties for backward compatibility."""
        return self.set_properties(*args, **kwargs)

    def get_account_info(self, *args: Any, **kwargs: Any) -> Any:
        """Wrapper for get_account_info - already exists in mixin."""
        return super().get_account_info(*args, **kwargs)

    # Forward query calls directly since method exists in mixin
    def query(self, *args: Any, **kwargs: Any) -> Any:
        """Query blob contents using SQL-like syntax."""
        return super().query(*args, **kwargs)


class _PageBlobOperationsWrapper(_PageBlobClientOperationsMixin):
    """Wrapper to provide page blob operations with shared pipeline client."""

    def __init__(self, config: Any, client: PipelineClient, serialize: Serializer, deserialize: Deserializer) -> None:
        self._config = config
        self._client = client
        self._serialize = serialize
        self._deserialize = deserialize

    # Alias for backward compatibility
    def update_sequence_number(self, *args: Any, **kwargs: Any) -> Any:
        """Alias for set_sequence_number for backward compatibility."""
        return self.set_sequence_number(*args, **kwargs)


class _AppendBlobOperationsWrapper(_AppendBlobClientOperationsMixin):
    """Wrapper to provide append blob operations with shared pipeline client."""

    def __init__(self, config: Any, client: PipelineClient, serialize: Serializer, deserialize: Deserializer) -> None:
        self._config = config
        self._client = client
        self._serialize = serialize
        self._deserialize = deserialize


class _BlockBlobOperationsWrapper(_BlockBlobClientOperationsMixin):
    """Wrapper to provide block blob operations with shared pipeline client."""

    def __init__(self, config: Any, client: PipelineClient, serialize: Serializer, deserialize: Deserializer) -> None:
        self._config = config
        self._client = client
        self._serialize = serialize
        self._deserialize = deserialize

    # Alias for backward compatibility
    def put_blob_from_url(self, *args: Any, **kwargs: Any) -> Any:
        """Alias for upload_blob_from_url for backward compatibility."""
        return self.upload_blob_from_url(*args, **kwargs)


class CombinedBlobClient:
    """Combined client that exposes all blob storage operations as attributes.

    This class wraps the individual operation mixins and exposes them as attributes
    to maintain backward compatibility with the previous autorest-generated client structure.

    :param url: The host name of the blob storage account.
    :type url: str
    :param credential: Credential used to authenticate requests to the service.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword version: Specifies the version of the operation to use for this request.
    :paramtype version: str
    """

    def __init__(
        self,
        url: str,
        credential: "TokenCredential",
        *,
        base_url: str = None,  # type: ignore
        pipeline: Any = None,
        **kwargs: Any
    ) -> None:
        from ._configuration import BlobClientConfiguration

        _endpoint = "{url}"
        self._config = BlobClientConfiguration(url=url, credential=credential, **kwargs)

        from azure.core.pipeline import policies

        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
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

        # Create operation wrappers as attributes
        self.service = _ServiceOperationsWrapper(self._config, self._client, self._serialize, self._deserialize)
        self.container = _ContainerOperationsWrapper(self._config, self._client, self._serialize, self._deserialize)
        self.blob = _BlobOperationsWrapper(self._config, self._client, self._serialize, self._deserialize)
        self.page_blob = _PageBlobOperationsWrapper(self._config, self._client, self._serialize, self._deserialize)
        self.append_blob = _AppendBlobOperationsWrapper(self._config, self._client, self._serialize, self._deserialize)
        self.block_blob = _BlockBlobOperationsWrapper(self._config, self._client, self._serialize, self._deserialize)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CombinedBlobClient":
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)


# Add all objects you want publicly available to users at this package level
__all__: list[str] = ["CombinedBlobClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
