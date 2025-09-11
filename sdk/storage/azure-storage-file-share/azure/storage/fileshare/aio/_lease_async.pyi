# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from types import TracebackType
from typing import Union, Optional, Any

from typing_extensions import Self

from azure.core.tracing.decorator_async import distributed_trace_async
from ._file_client_async import ShareFileClient
from ._share_client_async import ShareClient


class ShareLeaseClient:
    id: str
    etag: Optional[str]
    last_modified: Optional[datetime]
    def __init__(
        self, client: Union[ShareFileClient, ShareClient],
        lease_id: Optional[str] = None
    ) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    @distributed_trace_async
    async def acquire(
        self,
        *,
        lease_duration: int = -1,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def renew(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace_async
    async def release(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace_async
    async def change(self, proposed_lease_id: str, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace_async
    async def break_lease(
        self,
        *,
        lease_break_period: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> int: ...
