# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Union,
)
from types import TracebackType
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.storage.blob import BlobClient
from ._data_lake_lease import DataLakeLeaseClient
from ._generated import AzureDataLakeStorageRESTAPI
from ._models import (
    AccessControlChangeResult,
    AccessControlChanges,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    DirectoryProperties,
    FileProperties,
)
from ._shared.base_client import StorageAccountHostsMixin

class PathClient(StorageAccountHostsMixin):
    file_system_name: str
    path_name: str
    _blob_client: BlobClient
    _datalake_client_for_blob_operation: AzureDataLakeStorageRESTAPI
    _query_str: str
    _raw_credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]]
    def __init__(
        self,
        account_url: str,
        file_system_name: str,
        path_name: str,
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
    def _build_generated_client(self, url: str) -> AzureDataLakeStorageRESTAPI: ...
    def _create(
        self,
        resource_type: str,
        content_settings: Optional["ContentSettings"] = None,
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
    def _delete(
        self,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def set_access_control(
        self,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        permissions: Optional[str] = None,
        acl: Optional[str] = None,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def get_access_control(
        self,
        upn: Optional[bool] = None,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def set_access_control_recursive(
        self,
        acl: str,
        *,
        progress_hook: Optional[Callable[[AccessControlChanges], None]] = None,
        continuation_token: Optional[str] = None,
        batch_size: Optional[int] = None,
        max_batches: Optional[int] = None,
        continue_on_failure: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AccessControlChangeResult: ...
    @distributed_trace
    def update_access_control_recursive(
        self,
        acl: str,
        *,
        progress_hook: Optional[Callable[[AccessControlChanges], None]] = None,
        continuation_token: Optional[str] = None,
        batch_size: Optional[int] = None,
        max_batches: Optional[int] = None,
        continue_on_failure: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AccessControlChangeResult: ...
    @distributed_trace
    def remove_access_control_recursive(
        self,
        acl: str,
        *,
        progress_hook: Optional[Callable[[AccessControlChanges], None]] = None,
        continuation_token: Optional[str] = None,
        batch_size: Optional[int] = None,
        max_batches: Optional[int] = None,
        continue_on_failure: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AccessControlChangeResult: ...
    def _rename_path(
        self,
        rename_source: str,
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
    ) -> Dict[str, Any]: ...
    def _get_path_properties(
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
    ) -> Union[DirectoryProperties, FileProperties]: ...
    def _exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace
    def set_metadata(
        self,
        metadata: Dict[str, str],
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def set_http_headers(
        self,
        content_settings: Optional[ContentSettings] = None,
        *,
        lease: Optional[Union[DataLakeLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def acquire_lease(
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
