# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from typing import (
    Any, Optional, Union,
)
from types import TracebackType
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace
from ._file_system_client import FileSystemClient
from ._data_lake_directory_client import DataLakeDirectoryClient
from ._data_lake_file_client import DataLakeFileClient


class DataLakeLeaseClient:
    id: str
    etag: Optional[str]
    last_modified: Optional[datetime]
    def __init__(
        self,
        client: Union[FileSystemClient, DataLakeDirectoryClient, DataLakeFileClient],
        lease_id: Optional[str] = None
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    def close(self) -> None: ...
    @distributed_trace
    def acquire(
        self,
        lease_duration: int = -1,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def renew(
        self,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def release(
        self,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def change(
        self,
        proposed_lease_id: str,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def break_lease(
        self,
        lease_break_period: Optional[int] = None,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> int: ...
