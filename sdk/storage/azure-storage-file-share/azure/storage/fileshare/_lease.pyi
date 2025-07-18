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

from azure.core.tracing.decorator import distributed_trace
from ._file_client import ShareFileClient
from ._share_client import ShareClient

class ShareLeaseClient:
    id: str
    etag: Optional[str]
    last_modified: Optional[datetime]
    def __init__(self, client: Union[ShareFileClient, ShareClient], lease_id: Optional[str] = None) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    @distributed_trace
    def acquire(self, *, lease_duration: int = -1, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def renew(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def release(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def change(self, proposed_lease_id: str, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def break_lease(
        self, *, lease_break_period: Optional[int] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> int: ...
