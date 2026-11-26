# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# Declarations describe native signatures; Python never executes their bodies.
# pylint: disable=unused-argument
"""Describe every binding export for Python type checking.

The compiled extension supplies the implementation; these declarations do not
run the operations. _ItemFeedCursor is the binding's feed cursor, not a Python
page iterator. A unit test compares this file with the built module, so an
export added, removed, or changed in Rust must be updated here too.

Each synchronous operation returns the binding's response tuple. Its ``_async``
twin takes the same arguments and returns an awaitable for that tuple.

An operation's ``timeout_seconds`` keyword carries its remaining budget after
Python preparation and driver acquisition. In contrast,
``prepared.settings.timeout_seconds`` carries the configured request timeout
for the driver's policy. These names are retained for binding compatibility;
the keyword must not restart the configured timeout.
"""

from typing import Any, Awaitable
from ._backend.contracts import PreparedRequest
from .runtime import ConnectionPoolOptions

def _validate_runtime_configuration(config: Any = None) -> None:
    """Reject retired client-level network settings without initializing a runtime.

    :param config: Client configuration inspected for retired network settings.
    :type config: Any
    """
    ...

def _runtime_configuration() -> tuple[float, float, float] | None:
    """Inspect the default runtime for tests without initializing it.

    Return connection, data-request and metadata-request timeouts in seconds,
    or None if the default runtime has not been initialized.
    """
    ...

class _CosmosRuntime:
    @property
    def id(self) -> int: ...
    @property
    def timeouts(self) -> tuple[float, float, float]: ...

class _DriverHandle:
    """Own a specific Rust driver independently of its cache membership."""

class _AsyncOperationProbe:
    """Test-build-only export; absent unless built with ``test-probes``.

    Only that build accepts ``read_item_async(..., _debug_lifecycle=probe)``.
    A probe observes one native future, not sockets or service rollback.
    """

    def __init__(self) -> None: ...
    @property
    def status(self) -> str: ...

def acquire_driver_handle(
    endpoint: str, master_key: str | None = None, config: Any = None,
    credential: Any = None, runtime: _CosmosRuntime | None = None,
) -> _DriverHandle: ...

def release_driver_handle(driver_handle: _DriverHandle) -> None:
    """Release this handle's cache acquisition without revoking outstanding references.

    :param driver_handle: Acquired driver handle whose cache reference should be released.
    :type driver_handle: _DriverHandle
    """
    ...

def execute_item_batch(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...

def execute_item_batch_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...

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

def fetch_page_with_cursor(
    driver_handle: _DriverHandle, prepared: PreparedRequest, cursor: _ItemFeedCursor, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def fetch_page_with_cursor_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, cursor: _ItemFeedCursor, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...

def query_items(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *, timeout_seconds: float | None = None,
) -> tuple[Any, ...]: ...
def query_items_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *, timeout_seconds: float | None = None,
) -> Awaitable[tuple[Any, ...]]: ...

def get_container_metadata(
    driver_handle: _DriverHandle, container_link: str, *, timeout_seconds: float | None = None,
    include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def get_container_metadata_async(
    driver_handle: _DriverHandle, container_link: str, *, timeout_seconds: float | None = None,
    include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...

# Test-probes builds also accept include_fault_diagnostics for these operations.
def create_item(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *, timeout_seconds: float | None = None,
    include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def create_item_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *, timeout_seconds: float | None = None,
    include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def read_item(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *, timeout_seconds: float | None = None,
    include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def read_item_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *, timeout_seconds: float | None = None,
    include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]:
    """A ``test-probes`` build also accepts ``_debug_lifecycle``; see _AsyncOperationProbe.

    :param driver_handle: Acquired driver used for the read.
    :type driver_handle: _DriverHandle
    :param prepared: Prepared item request containing identity, partition key and settings.
    :type prepared: ~azure.cosmos._backend.contracts.PreparedRequest
    :keyword timeout_seconds: Remaining operation budget in seconds, or None for no binding deadline.
    :paramtype timeout_seconds: float or None
    :keyword bool include_attempts: Whether to include attempt details in the response diagnostics.
    """
    ...

# Test-probes builds also accept include_fault_diagnostics for upsert.
def upsert_item(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def upsert_item_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
# Remaining operations: (driver_handle, prepared, *, timeout_seconds, include_attempts).
def replace_item(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def replace_item_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def patch_item(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def patch_item_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def delete_item(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def delete_item_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def read_feed_ranges(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def read_feed_ranges_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def feed_range_from_partition_key(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def feed_range_from_partition_key_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def is_feed_range_subset(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def is_feed_range_subset_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def get_throughput(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def get_throughput_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def replace_throughput(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def replace_throughput_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def create_database(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def create_database_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def read_database(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def read_database_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def delete_database(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def delete_database_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def list_databases(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def list_databases_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def query_databases(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def query_databases_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def create_container(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def create_container_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def read_container(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def read_container_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def replace_container(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def replace_container_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def delete_container(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def delete_container_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def list_containers(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def list_containers_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...
def query_containers(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> tuple[Any, ...]: ...
def query_containers_async(
    driver_handle: _DriverHandle, prepared: PreparedRequest, *,
    timeout_seconds: float | None = None, include_attempts: bool = False,
) -> Awaitable[tuple[Any, ...]]: ...

class _DriverTransportError(RuntimeError):
    """A Cosmos driver operation failed without a wire response (transport failure,
    client-side validation, or a pre-HTTP timeout)."""

class _DriverResponseError(RuntimeError):
    """A metadata operation failed; args[0] contains its error response tuple."""

class _UnsupportedQueryFeatureError(RuntimeError):
    """The Cosmos driver cannot execute this query plan."""

# Request settings are available in every build.
def _request_settings_schema() -> dict[str, list[str]]: ...
# Test-build-only exports, absent unless built with test-probes.
def _debug_operation_count() -> int: ...
def _debug_attempt_count() -> int: ...
def _debug_retry_count() -> int: ...
def _debug_fault_injection_rule_hit_count(driver_handle: _DriverHandle, rule_id: str) -> int: ...
def _debug_set_fault_injection_rule_enabled(driver_handle: _DriverHandle, rule_id: str, enabled: bool) -> None: ...
def _debug_cached_account_regions(driver_handle: _DriverHandle) -> tuple[list[str], list[str]] | None: ...

__python_commit__: str
__rust_driver_commit__: str
