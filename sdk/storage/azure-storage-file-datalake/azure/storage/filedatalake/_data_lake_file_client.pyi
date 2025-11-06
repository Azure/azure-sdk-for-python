# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from typing import (
    Any,
    AnyStr,
    Callable,
    Dict,
    IO,
    Iterable,
    Literal,
    Optional,
    Union,
)
from types import TracebackType
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace
from ._data_lake_lease import DataLakeLeaseClient
from ._download import StorageStreamDownloader
from ._models import (
    ArrowDialect,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    DataLakeFileQueryError,
    DelimitedJsonDialect,
    DelimitedTextDialect,
    FileProperties,
    QuickQueryDialect,
)
from ._path_client import PathClient
from ._quick_query_helper import DataLakeFileQueryReader

class DataLakeFileClient(PathClient):
    url: str
    primary_endpoint: str
    primary_hostname: str
    def __init__(
        self,
        account_url: str,
        file_system_name: str,
        file_path: str,
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
        file_path: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def create_file(
        self,
        content_settings: Optional[ContentSettings] = None,
        metadata: Optional[Dict[str, str]] = None,
        *,
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
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_context: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def delete_file(
        self,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> None: ...
    @distributed_trace
    def get_file_properties(
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
        **kwargs
    ) -> FileProperties: ...
    @distributed_trace
    def set_file_expiry(
        self,
        expiry_options: str,
        expires_on: Optional[Union[datetime, int]] = None,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def upload_data(
        self,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        length: Optional[int] = None,
        overwrite: Optional[bool] = False,
        *,
        content_settings: Optional[ContentSettings] = None,
        metadata: Optional[Dict[str, str]] = None,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        umask: Optional[str] = None,
        permissions: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        validate_content: Optional[bool] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: Optional[int] = None,
        chunk_size: Optional[int] = None,
        encryption_context: Optional[str] = None,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def append_data(
        self,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        offset: int,
        length: Optional[int] = None,
        *,
        flush: Optional[bool] = None,
        validate_content: Optional[bool] = None,
        lease_action: Optional[Literal["acquire", "auto-renew", "release", "acquire-release"]] = None,
        lease_duration: int = -1,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def flush_data(
        self,
        offset: int,
        retain_uncommitted_data: Optional[bool] = False,
        *,
        content_settings: Optional[ContentSettings] = None,
        close: bool = False,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        lease_action: Optional[Literal["acquire", "auto-renew", "release", "acquire-release"]] = None,
        lease_duration: int = -1,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def download_file(
        self,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: Optional[int] = None,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> StorageStreamDownloader: ...
    @distributed_trace
    def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace
    def rename_file(
        self,
        new_name: str,
        *,
        content_settings: Optional[ContentSettings] = None,
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
    ) -> "DataLakeFileClient": ...
    @distributed_trace
    def query_file(
        self,
        query_expression: str,
        *,
        on_error: Optional[Callable[[DataLakeFileQueryError], None]] = None,
        file_format: Optional[Union[DelimitedJsonDialect, DelimitedTextDialect, QuickQueryDialect, str]] = None,
        output_format: Optional[
            Union[ArrowDialect, DelimitedJsonDialect, DelimitedTextDialect, QuickQueryDialect, str]
        ] = None,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> DataLakeFileQueryReader: ...
