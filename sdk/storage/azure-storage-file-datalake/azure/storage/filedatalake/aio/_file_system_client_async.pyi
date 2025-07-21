# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from types import TracebackType
from typing import Any, Dict, Optional, Union
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from .._models import (
    AccessPolicy,
    ContentSettings,
    DeletedPathProperties,
    DirectoryProperties,
    EncryptionScopeOptions,
    FileProperties,
    FileSystemProperties,
    PathProperties,
    PublicAccess,
)
from .._shared.base_client import StorageAccountHostsMixin
from .._shared.base_client_async import AsyncStorageAccountHostsMixin
from ._data_lake_directory_client_async import DataLakeDirectoryClient
from ._data_lake_file_client_async import DataLakeFileClient
from ._data_lake_lease_async import DataLakeLeaseClient

class FileSystemClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin):  # type: ignore [misc]
    file_system_name: str
    def __init__(
        self,
        account_url: str,
        file_system_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    async def close(self) -> None: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        file_system_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace_async
    async def acquire_lease(
        self,
        lease_duration: int = -1,
        lease_id: Optional[str] = None,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DataLakeLeaseClient: ...
    @distributed_trace_async
    async def create_file_system(
        self,
        metadata: Optional[Dict[str, str]] = None,
        public_access: Optional[PublicAccess] = None,
        *,
        encryption_scope_options: Optional[Union[Dict[str, Any], EncryptionScopeOptions]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace_async
    async def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace_async
    async def _rename_file_system(
        self,
        new_name: str,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> "FileSystemClient": ...
    @distributed_trace_async
    async def delete_file_system(
        self,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def get_file_system_properties(
        self, *, lease: Optional[Union[DataLakeLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> FileSystemProperties: ...
    @distributed_trace_async
    async def set_file_system_metadata(
        self,
        metadata: Dict[str, str],
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace_async
    async def set_file_system_access_policy(
        self,
        signed_identifiers: Dict[str, AccessPolicy],
        public_access: Optional[Union[str, PublicAccess]] = None,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace_async
    async def get_file_system_access_policy(
        self, *, lease: Optional[Union[DataLakeLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_paths(
        self,
        path: Optional[str] = None,
        recursive: Optional[bool] = True,
        max_results: Optional[int] = None,
        *,
        upn: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[PathProperties]: ...
    @distributed_trace_async
    async def create_directory(
        self,
        directory: Union[DirectoryProperties, str],
        metadata: Optional[Dict[str, str]] = None,
        *,
        content_settings: Optional[ContentSettings] = None,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        umask: Optional[str] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        acl: Optional[str] = None,
        lease_id: Optional[str] = None,
        lease_duration: int = -1,
        permissions: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DataLakeDirectoryClient: ...
    @distributed_trace_async
    async def delete_directory(
        self,
        directory: Union[DirectoryProperties, str],
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DataLakeDirectoryClient: ...
    @distributed_trace_async
    async def create_file(
        self,
        file: Union[FileProperties, str],
        *,
        content_settings: Optional[ContentSettings] = None,
        metadata: Optional[Dict[str, str]] = None,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        umask: Optional[str] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        acl: Optional[str] = None,
        lease_id: Optional[str] = None,
        lease_duration: int = -1,
        expires_on: Optional[Union[datetime, int]] = None,
        permissions: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DataLakeFileClient: ...
    @distributed_trace_async
    async def delete_file(
        self,
        file: Union[FileProperties, str],
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DataLakeFileClient: ...
    @distributed_trace_async
    async def _undelete_path(
        self, deleted_path_name: str, deletion_id: str, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Union[DataLakeDirectoryClient, DataLakeFileClient]: ...
    def _get_root_directory_client(self) -> DataLakeDirectoryClient: ...
    def get_directory_client(self, directory: Union[DirectoryProperties, str]) -> DataLakeDirectoryClient: ...
    def get_file_client(self, file_path: Union[FileProperties, str]) -> DataLakeFileClient: ...
    @distributed_trace
    def list_deleted_paths(
        self,
        *,
        path_prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[DeletedPathProperties]: ...
