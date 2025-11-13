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
    Callable,
    Dict,
    IO,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
)

from typing_extensions import Self

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._file_client import ShareFileClient
from ._lease import ShareLeaseClient
from ._models import (
    ContentSettings,
    DirectoryProperties,
    FileProperties,
    Handle,
    NTFSAttributes,
)
from ._shared.base_client import StorageAccountHostsMixin

class ShareDirectoryClient(StorageAccountHostsMixin):
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
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
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
    @classmethod
    def from_directory_url(
        cls,
        directory_url: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
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
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    def close(self) -> None: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        share_name: str,
        directory_path: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
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
    def get_subdirectory_client(self, directory_name: str, **kwargs: Any) -> Self: ...
    @distributed_trace
    def create_directory(
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
    @distributed_trace
    def delete_directory(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def rename_directory(
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
    ) -> ItemPaged[Union[DirectoryProperties, FileProperties]]: ...
    @distributed_trace
    def list_handles(
        self, recursive: bool = False, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> ItemPaged[Handle]: ...
    @distributed_trace
    def close_handle(
        self, handle: Union[str, Handle], *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, int]: ...
    @distributed_trace
    def close_all_handles(
        self, recursive: bool = False, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, int]: ...
    @distributed_trace
    def get_directory_properties(self, *, timeout: Optional[int] = None, **kwargs: Any) -> DirectoryProperties: ...
    @distributed_trace
    def set_directory_metadata(
        self, metadata: Dict[str, Any], *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace
    def set_http_headers(
        self,
        file_attributes: Optional[Union[str, NTFSAttributes]] = None,
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
    @distributed_trace
    def create_subdirectory(
        self,
        directory_name: str,
        *,
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def delete_subdirectory(self, directory_name: str, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def upload_file(
        self,
        file_name: str,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        length: Optional[int] = None,
        *,
        metadata: Optional[Dict[str, str]] = None,
        content_settings: Optional[ContentSettings] = None,
        validate_content: Optional[bool] = None,
        max_concurrency: Optional[int] = None,
        progress_hook: Optional[Callable[[int, Optional[int]], None]] = None,
        encoding: str = "UTF-8",
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ShareFileClient: ...
    @distributed_trace
    def delete_file(self, file_name: str, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
