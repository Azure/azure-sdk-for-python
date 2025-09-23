# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from types import TracebackType
from typing import (
    Any,
    Dict,
    Optional,
    Union,
)
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._data_lake_lease import DataLakeLeaseClient
from ._data_lake_directory_client import DataLakeDirectoryClient
from ._data_lake_file_client import DataLakeFileClient
from ._file_system_client import FileSystemClient
from ._models import (
    AnalyticsLogging,
    CorsRule,
    DirectoryProperties,
    EncryptionScopeOptions,
    FileProperties,
    FileSystemProperties,
    Metrics,
    PublicAccess,
    RetentionPolicy,
    StaticWebsite,
    UserDelegationKey,
)
from ._shared.base_client import StorageAccountHostsMixin

class DataLakeServiceClient(StorageAccountHostsMixin):
    url: str
    primary_endpoint: str
    primary_hostname: str
    def __init__(
        self,
        account_url: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    def close(self) -> None: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def get_user_delegation_key(
        self, key_start_time: datetime, key_expiry_time: datetime, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> UserDelegationKey: ...
    @distributed_trace
    def list_file_systems(
        self,
        name_starts_with: Optional[str] = None,
        include_metadata: bool = False,
        *,
        results_per_page: Optional[int] = None,
        include_deleted: Optional[bool] = None,
        include_system: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[FileSystemProperties]: ...
    @distributed_trace
    def create_file_system(
        self,
        file_system: Union[FileSystemProperties, str],
        metadata: Optional[Dict[str, str]] = None,
        public_access: Optional[PublicAccess] = None,
        *,
        encryption_scope_options: Optional[Union[EncryptionScopeOptions, Dict[str, Any]]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> FileSystemClient: ...
    def _rename_file_system(
        self,
        name: str,
        new_name: str,
        *,
        lease: Optional[Union[str, DataLakeLeaseClient]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> FileSystemClient: ...
    @distributed_trace
    def undelete_file_system(
        self, name: str, deleted_version: str, timeout: Optional[int] = None, **kwargs: Any
    ) -> FileSystemClient: ...
    @distributed_trace
    def delete_file_system(
        self,
        file_system: Union[FileSystemProperties, str],
        *,
        lease: Optional[Union[str, DataLakeLeaseClient]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> FileSystemClient: ...
    def get_file_system_client(self, file_system: Union[FileSystemProperties, str]) -> FileSystemClient: ...
    def get_directory_client(
        self, file_system: Union[FileSystemProperties, str], directory: Union[DirectoryProperties, str]
    ) -> DataLakeDirectoryClient: ...
    def get_file_client(
        self,
        file_system: Union[FileSystemProperties, str],
        file_path: Union[FileProperties, str],
    ) -> DataLakeFileClient: ...
    @distributed_trace
    def set_service_properties(
        self,
        *,
        analytics_logging: Optional[AnalyticsLogging] = None,
        hour_metrics: Optional[Metrics] = None,
        minute_metrics: Optional[Metrics] = None,
        cors: Optional[list[CorsRule]] = None,
        target_version: Optional[str] = None,
        delete_retention_policy: Optional[RetentionPolicy] = None,
        static_website: Optional[StaticWebsite] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def get_service_properties(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]: ...
