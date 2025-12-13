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
    Tuple,
    Union,
)

from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._download import StorageStreamDownloader
from ._lease import ShareLeaseClient
from ._models import (
    ContentSettings,
    FileProperties,
    Handle,
    NTFSAttributes,
)
from ._shared.base_client import StorageAccountHostsMixin

class ShareFileClient(StorageAccountHostsMixin):
    share_name: str
    file_name: str
    file_path: List[str]
    directory_path: str
    snapshot: Optional[str]
    allow_trailing_dot: Optional[bool]
    allow_source_trailing_dot: Optional[bool]
    file_request_intent: Optional[Literal["backup"]]
    def __init__(
        self,
        account_url: str,
        share_name: str,
        file_path: str,
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
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    def close(self) -> None: ...
    @classmethod
    def from_file_url(
        cls,
        file_url: str,
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
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        share_name: str,
        file_path: str,
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
    @distributed_trace
    def acquire_lease(
        self, lease_id: Optional[str] = None, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> ShareLeaseClient: ...
    @distributed_trace
    def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace
    def create_file(
        self,
        size: int,
        file_attributes: Optional[Union[str, NTFSAttributes]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        *,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        file_change_time: Optional[Union[str, datetime]] = None,
        content_settings: Optional[ContentSettings] = None,
        metadata: Optional[Dict[str, str]] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        file_mode: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def upload_file(
        self,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        length: Optional[int] = None,
        file_attributes: Optional[Union[str, NTFSAttributes]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        *,
        file_change_time: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_settings: Optional[ContentSettings] = None,
        validate_content: bool = False,
        max_concurrency: int = 1,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        progress_hook: Optional[Callable[[int, Optional[int]], None]] = None,
        encoding: str = "UTF-8",
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def start_copy_from_url(
        self,
        source_url: str,
        *,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        file_attributes: Optional[Union[str, NTFSAttributes]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_change_time: Optional[Union[str, datetime]] = None,
        ignore_read_only: Optional[bool] = None,
        set_archive_attribute: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        file_mode: Optional[str] = None,
        file_mode_copy_mode: Optional[Literal["source", "override"]] = None,
        owner_copy_mode: Optional[Literal["source", "override"]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def abort_copy(
        self,
        copy_id: Union[str, FileProperties],
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def download_file(
        self,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        max_concurrency: int = 1,
        validate_content: bool = False,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        progress_hook: Optional[Callable[[int, Optional[int]], None]] = None,
        decompress: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> StorageStreamDownloader: ...
    @distributed_trace
    def delete_file(
        self, *, lease: Optional[Union[ShareLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def rename_file(
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
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        source_lease: Optional[Union[ShareLeaseClient, str]] = None,
        destination_lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> "ShareFileClient": ...
    @distributed_trace
    def get_file_properties(
        self, *, lease: Optional[Union[ShareLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> FileProperties: ...
    @distributed_trace
    def set_http_headers(
        self,
        content_settings: ContentSettings,
        file_attributes: Optional[Union[str, NTFSAttributes]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        *,
        file_permission_format: Optional[Literal["sddl", "binary"]] = None,
        file_change_time: Optional[Union[str, datetime]] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        file_mode: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def set_file_metadata(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def upload_range(
        self,
        data: bytes,
        offset: int,
        length: int,
        *,
        validate_content: bool = False,
        encoding: str = "UTF-8",
        file_last_write_mode: Optional[Literal["preserve", "now"]] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def upload_range_from_url(
        self,
        source_url: str,
        offset: int,
        length: int,
        source_offset: int,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        source_etag: Optional[str] = None,
        source_match_condition: Optional[MatchConditions] = None,
        file_last_write_mode: Optional[Literal["preserve", "now"]] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        source_authorization: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_ranges(
        self,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> List[Dict[str, int]]: ...
    @distributed_trace
    def get_ranges_diff(
        self,
        previous_sharesnapshot: Union[str, Dict[str, Any]],
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        include_renames: Optional[bool] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...
    @distributed_trace
    def clear_range(
        self,
        offset: int,
        length: int,
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def resize_file(
        self,
        size: int,
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def list_handles(self, *, timeout: Optional[int] = None, **kwargs: Any) -> ItemPaged[Handle]: ...
    @distributed_trace
    def close_handle(
        self, handle: Union[str, Handle], *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, int]: ...
    @distributed_trace
    def close_all_handles(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, int]: ...
    @distributed_trace
    def create_hardlink(
        self,
        target: str,
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def create_symlink(
        self,
        target: str,
        *,
        metadata: Optional[Dict[str, str]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_symlink(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]: ...
