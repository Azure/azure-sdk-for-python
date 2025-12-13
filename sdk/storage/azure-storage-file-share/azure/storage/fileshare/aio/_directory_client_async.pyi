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
    AnyStr,
    AsyncIterable,
    Awaitable,
    Callable,
    Dict,
    IO,
    List,
    Literal,
    Iterable,
    Optional,
    Union,
)

from typing_extensions import Self

from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from ._file_client_async import ShareFileClient
from ._lease_async import ShareLeaseClient
from ._models import Handle
from .._models import (
    ContentSettings,
    DirectoryProperties,
    FileProperties,
    NTFSAttributes,
)
from .._shared.base_client import StorageAccountHostsMixin
from .._shared.base_client_async import AsyncStorageAccountHostsMixin

class ShareDirectoryClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin):  # type: ignore [misc]
    share_name: str
    directory_path: str
    snapshot: Optional[str]
    allow_trailing_dot: Optional[bool]
    allow_source_trailing_dot: Optional[bool]
    file_request_intent: Optional[Literal["backup"]]
    def __init__(
        self,
        account_url: str,
        share_name: str,
        directory_path: str,
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
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    async def close(self) -> None: ...
    @classmethod
    def from_directory_url(
        cls,
        directory_url: str,
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
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        share_name: str,
        directory_path: str,
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
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    def get_file_client(self, file_name: str, **kwargs: Any) -> ShareFileClient: ...
    def get_subdirectory_client(self, directory_name: str, **kwargs) -> Self: ...
    @distributed_trace_async
    async def create_directory(
        self,
        *,
        file_attributes: Optional[Union[str, NTFSAttributes]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_change_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        file_permission_key: Optional[str] = None,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        metadata: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        file_mode: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def delete_directory(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace_async
    async def rename_directory(
        self,
        new_name: str,
        *,
        overwrite: Optional[bool] = None,
        ignore_read_only: Optional[bool] = None,
        file_permission: Optional[str] = None,
        file_permission_key: Optional[str] = None,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        file_attributes: Optional[Union[str, NTFSAttributes]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_change_time: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, str]] = None,
        destination_lease: Optional[Union[str, ShareLeaseClient]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def list_directories_and_files(
        self,
        name_starts_with: Optional[str] = None,
        *,
        include: Optional[List[str]] = None,
        include_extended_info: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Union[DirectoryProperties, FileProperties]]: ...
    @distributed_trace
    def list_handles(
        self, recursive: bool = False, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> AsyncItemPaged[Handle]: ...
    @distributed_trace_async
    async def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace_async
    async def close_handle(
        self, handle: Union[str, Handle], *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, int]: ...
    @distributed_trace_async
    async def close_all_handles(
        self, recursive: bool = False, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, int]: ...
    @distributed_trace_async
    async def get_directory_properties(
        self, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> DirectoryProperties: ...
    @distributed_trace_async
    async def set_directory_metadata(
        self, metadata: Dict[str, Any], *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def set_http_headers(
        self,
        file_attributes: Optional[Union[str, "NTFSAttributes"]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        *,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        file_change_time: Optional[Union[str, datetime]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        file_mode: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def create_subdirectory(
        self,
        directory_name: str,
        *,
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace_async
    async def delete_subdirectory(
        self, directory_name: str, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def upload_file(
        self,
        file_name: str,
        data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]],
        length: Optional[int] = None,
        *,
        metadata: Optional[Dict[str, str]] = None,
        content_settings: Optional[ContentSettings] = None,
        validate_content: Optional[bool] = None,
        max_concurrency: Optional[int] = None,
        progress_hook: Optional[Callable[[int, Optional[int]], Awaitable[None]]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ShareFileClient: ...
    @distributed_trace_async
    async def delete_file(self, file_name: str, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
