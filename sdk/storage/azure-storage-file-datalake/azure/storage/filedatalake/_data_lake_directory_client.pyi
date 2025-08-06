# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from typing import (
    Any,
    Dict,
    Optional,
    Union,
)
from types import TracebackType
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._data_lake_lease import DataLakeLeaseClient
from ._data_lake_file_client import DataLakeFileClient
from ._models import ContentSettings, CustomerProvidedEncryptionKey, DirectoryProperties, FileProperties, PathProperties
from ._path_client import PathClient

class DataLakeDirectoryClient(PathClient):
    url: str
    primary_endpoint: str
    primary_hostname: str
    def __init__(
        self,
        account_url: str,
        file_system_name: str,
        directory_name: str,
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
        file_system_name: str,
        directory_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def create_directory(
        self,
        metadata: Optional[Dict[str, str]] = None,
        *,
        content_settings: Optional[ContentSettings] = None,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        umask: Optional[str] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        acl: Optional[str] = None,
        lease_id: Optional[str] = None,
        lease_duration: Optional[int] = None,
        permissions: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def delete_directory(
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
    @distributed_trace
    def get_directory_properties(
        self,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        upn: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DirectoryProperties: ...
    @distributed_trace
    def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace
    def rename_directory(
        self,
        new_name: str,
        *,
        source_lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        source_if_modified_since: Optional[datetime] = None,
        source_if_unmodified_since: Optional[datetime] = None,
        source_etag: Optional[str] = None,
        source_match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> "DataLakeDirectoryClient": ...
    @distributed_trace
    def create_sub_directory(
        self,
        sub_directory: Union[DirectoryProperties, str],
        metadata: Optional[Dict[str, str]] = None,
        *,
        content_settings: Optional[ContentSettings] = None,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        umask: Optional[str] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        acl: Optional[str] = None,
        lease_id: Optional[str] = None,
        lease_duration: Optional[int] = None,
        permissions: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> "DataLakeDirectoryClient": ...
    @distributed_trace
    def delete_sub_directory(
        self,
        sub_directory: Union[DirectoryProperties, str],
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> "DataLakeDirectoryClient": ...
    @distributed_trace
    def create_file(
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
        lease_duration: Optional[int] = None,
        expires_on: Optional[Union[datetime, int]] = None,
        permissions: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DataLakeFileClient: ...
    @distributed_trace
    def get_paths(
        self,
        *,
        recursive: bool = True,
        max_results: Optional[int] = None,
        upn: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[PathProperties]: ...
    def get_file_client(self, file: Union[FileProperties, str]) -> DataLakeFileClient: ...
    def get_sub_directory_client(self, sub_directory: Union[DirectoryProperties, str]) -> "DataLakeDirectoryClient": ...
