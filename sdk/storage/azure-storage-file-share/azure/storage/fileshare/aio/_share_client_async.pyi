# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from types import TracebackType
from typing import Any, Dict, List, Literal, Optional, Union

from typing_extensions import Self

from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from ._directory_client_async import ShareDirectoryClient
from ._file_client_async import ShareFileClient
from ._lease_async import ShareLeaseClient
from .._generated.models import (
    ShareAccessTier,
    ShareRootSquash,
)
from .._models import (
    AccessPolicy,
    DirectoryProperties,
    FileProperties,
    ShareProperties,
    ShareProtocols,
)
from .._shared.base_client import StorageAccountHostsMixin
from .._shared.base_client_async import AsyncStorageAccountHostsMixin

class ShareClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin):  # type: ignore[misc]
    share_name: str
    snapshot: Optional[str]
    allow_trailing_dot: Optional[bool]
    allow_source_trailing_dot: Optional[bool]
    file_request_intent: Optional[Literal["backup"]]
    def __init__(
        self,
        account_url: str,
        share_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        token_intent: Optional[Literal["backup"]] = None,
        allow_trailing_dot: Optional[bool] = None,
        allow_source_trailing_dot: Optional[bool] = None,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        max_range_size: int = 4 * 1024 * 1024,
        **kwargs: Any
    ) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    async def close(self) -> None: ...
    @classmethod
    def from_share_url(
        cls,
        share_url: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        token_intent: Optional[Literal["backup"]] = None,
        allow_trailing_dot: Optional[bool] = None,
        allow_source_trailing_dot: Optional[bool] = None,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        max_range_size: int = 4 * 1024 * 1024,
        **kwargs: Any
    ) -> Self: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        share_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        token_intent: Optional[Literal["backup"]] = None,
        allow_trailing_dot: Optional[bool] = None,
        allow_source_trailing_dot: Optional[bool] = None,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        max_range_size: int = 4 * 1024 * 1024,
        **kwargs: Any
    ) -> Self: ...
    def get_directory_client(self, directory_path: Optional[str] = None) -> ShareDirectoryClient: ...
    def get_file_client(self, file_path: str) -> ShareFileClient: ...
    @distributed_trace_async
    async def acquire_lease(
        self,
        *,
        lease_duration: Optional[int] = None,
        lease_id: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ShareLeaseClient: ...
    @distributed_trace_async
    async def create_share(
        self,
        *,
        metadata: Optional[Dict[str, str]] = None,
        quota: Optional[int] = None,
        access_tier: Optional[Union[str, ShareAccessTier]] = None,
        protocols: Optional[Union[str, ShareProtocols]] = None,
        root_squash: Optional[Union[str, ShareRootSquash]] = None,
        paid_bursting_enabled: Optional[bool] = None,
        paid_bursting_bandwidth_mibps: Optional[int] = None,
        paid_bursting_iops: Optional[int] = None,
        provisioned_iops: Optional[int] = None,
        provisioned_bandwidth_mibps: Optional[int] = None,
        enable_smb_directory_lease: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def create_snapshot(
        self, *, metadata: Optional[Dict[str, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def delete_share(
        self,
        delete_snapshots: Optional[Union[bool, Literal["include", "include-leased"]]] = False,
        *,
        lease: Optional[Union[str, ShareLeaseClient]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def get_share_properties(
        self, *, lease: Optional[Union[str, ShareLeaseClient]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> ShareProperties: ...
    @distributed_trace_async
    async def set_share_quota(
        self,
        quota: int,
        *,
        lease: Optional[Union[str, ShareLeaseClient]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def set_share_properties(
        self,
        *,
        access_tier: Optional[Union[str, ShareAccessTier]] = None,
        quota: Optional[int] = None,
        root_squash: Optional[Union[str, ShareRootSquash]] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        paid_bursting_enabled: Optional[bool] = None,
        paid_bursting_bandwidth_mibps: Optional[int] = None,
        paid_bursting_iops: Optional[int] = None,
        provisioned_iops: Optional[int] = None,
        provisioned_bandwidth_mibps: Optional[int] = None,
        enable_smb_directory_lease: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def set_share_metadata(
        self,
        metadata: Dict[str, str],
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def get_share_access_policy(
        self, *, lease: Optional[Union[str, ShareLeaseClient]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def set_share_access_policy(
        self,
        signed_identifiers: Dict[str, "AccessPolicy"],
        *,
        lease: Optional[Union[str, ShareLeaseClient]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def get_share_stats(
        self, *, lease: Optional[Union[str, ShareLeaseClient]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> int: ...
    @distributed_trace
    def list_directories_and_files(
        self,
        directory_name: Optional[str] = None,
        name_starts_with: Optional[str] = None,
        marker: Optional[str] = None,
        *,
        include: Optional[List[str]] = None,
        include_extended_info: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Union[DirectoryProperties, FileProperties]]: ...
    @distributed_trace_async
    async def create_permission_for_share(
        self,
        file_permission: str,
        *,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Optional[str]: ...
    @distributed_trace_async
    async def get_permission_for_share(
        self,
        permission_key: str,
        *,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> str: ...
    @distributed_trace_async
    async def create_directory(
        self,
        directory_name: str,
        *,
        metadata: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        file_mode: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ShareDirectoryClient: ...
    @distributed_trace_async
    async def delete_directory(self, directory_name: str, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
