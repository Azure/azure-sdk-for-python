# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from types import TracebackType
from typing import Union, Optional, Any, Dict, List, Literal

from typing_extensions import Self

from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from ._share_client_async import ShareClient
from .._models import (
    CorsRule,
    Metrics,
    ShareProperties,
    ShareProtocolSettings,
)
from .._shared.base_client import StorageAccountHostsMixin
from .._shared.base_client_async import AsyncStorageAccountHostsMixin

class ShareServiceClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin):  # type: ignore[misc]
    def __init__(
        self,
        account_url: str,
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
    def from_connection_string(
        cls,
        conn_str: str,
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
    @distributed_trace_async
    async def get_service_properties(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def set_service_properties(
        self,
        hour_metrics: Optional[Metrics] = None,
        minute_metrics: Optional[Metrics] = None,
        cors: Optional[List[CorsRule]] = None,
        protocol: Optional[ShareProtocolSettings] = None,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def list_shares(
        self,
        name_starts_with: Optional[str] = None,
        include_metadata: Optional[bool] = False,
        include_snapshots: Optional[bool] = False,
        *,
        include_deleted: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[ShareProperties]: ...
    @distributed_trace_async
    async def create_share(
        self,
        share_name: str,
        *,
        metadata: Optional[Dict[str, str]] = None,
        quota: Optional[int] = None,
        provisioned_iops: Optional[int] = None,
        provisioned_bandwidth_mibps: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ShareClient: ...
    @distributed_trace_async
    async def delete_share(
        self,
        share_name: Union[ShareProperties, str],
        delete_snapshots: Optional[bool] = False,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def undelete_share(
        self, deleted_share_name: str, deleted_share_version: str, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> ShareClient: ...
    def get_share_client(
        self, share: Union[ShareProperties, str], snapshot: Optional[Union[Dict[str, Any], str]] = None
    ) -> ShareClient: ...
