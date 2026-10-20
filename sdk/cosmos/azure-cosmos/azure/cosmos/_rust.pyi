# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Describe selected binding exports for Python type checking.

The compiled extension supplies the implementation; these declarations do not
run the operations. _ItemFeedCursor is the binding's feed cursor, not a Python
page iterator. Other binding exports remain typed as Any through __getattr__.
"""

from typing import Any, Awaitable
from .runtime import ConnectionPoolOptions

def _validate_runtime_configuration(config: Any = None) -> None:
    """Reject retired client-level network settings without initializing a runtime."""
    ...

class _CosmosRuntime:
    @property
    def id(self) -> int: ...
    @property
    def timeouts(self) -> tuple[float, float, float]: ...

class _DriverHandle:
    """Own a specific Rust driver independently of its cache membership."""

def acquire_driver_handle(
    endpoint: str, master_key: str | None = None, config: Any = None,
    credential: Any = None, runtime: _CosmosRuntime | None = None,
) -> _DriverHandle: ...

def release_driver_handle(driver_handle: _DriverHandle) -> None:
    """Release this handle's cache acquisition without revoking outstanding references."""
    ...

def _create_runtime(options: ConnectionPoolOptions | None = None) -> _CosmosRuntime: ...
def _create_runtime_async(options: ConnectionPoolOptions | None = None) -> Awaitable[_CosmosRuntime]: ...

class _ItemFeedCursor:
    """Retain progress between page fetches made through the binding."""

    def __init__(self) -> None:
        """Create an empty feed cursor without acquiring a driver handle or fetching a page."""
        ...
    @property
    def has_more(self) -> bool:
        """Report whether the cursor's recorded progress indicates more results.

        A new cursor starts with False; that does not establish that the feed
        is empty before its first fetch.
        """
        ...
    @property
    def continuation_supported(self) -> bool:
        """Return False if the cursor has marked continuation tokens as unsupported.

        False does not mean iteration is finished. A new cursor starts with
        True, before a query plan has established whether a token is available.
        """
        ...
    @property
    def can_retry_setup(self) -> bool:
        """Report whether setup has not started execution and the cursor is not busy.

        The Python wrapper also checks the error before allowing a later retry;
        this flag alone does not make timeouts or cancellation retryable.
        """
        ...

def __getattr__(name: str) -> Any:
    """Allow other export names during type checking, not guarantee their runtime presence."""
    ...
