# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Helpers that tests use to check two things: that an SDK call really ran in
the SDK's compiled code, and that pages returned by the live service carry the
expected headers.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Mapping, Sequence, TypeVar

from config.diagnostics import _binding_operation_count

T = TypeVar("T")


def assert_live_page_headers(page_headers: Sequence[Mapping[str, Any]]) -> None:
    """Helper for paging tests: check that every page came from its own request
    to the live service.

    ``page_headers`` holds the response headers of each page, usually collected
    with ``response_hook``. Every page must have an activity ID, a request
    charge above zero and SDK diagnostics, and no two pages can share an
    activity ID.

    Example::

        assert_live_page_headers(page_headers)
    """
    assert page_headers, "no page headers were captured"
    activity_ids = []
    for headers in page_headers:
        assert headers["x-ms-activity-id"]
        assert float(headers["x-ms-request-charge"]) > 0
        assert headers["x-ms-cosmos-sdk-diagnostics"]
        activity_ids.append(headers["x-ms-activity-id"])
    assert len(set(activity_ids)) == len(activity_ids), "page activity IDs were reused"


def backend_name(client: Any) -> str:
    """Return the backend (``"core-python"`` or ``"rust"``) ``client`` was built on."""
    connection = getattr(client, "client_connection", None)
    name = getattr(getattr(connection, "_backend", None), "name", None)
    assert name in ("core-python", "rust"), "client has an unexpected backend: {!r}".format(name)
    return name


def assert_rust_client(client: Any) -> None:
    """Fail unless ``client`` was constructed on the Rust backend."""
    connection = getattr(client, "client_connection", None)
    name = getattr(getattr(connection, "_backend", None), "name", None)
    assert name == "rust", "expected a Rust-backed client, got {!r}".format(name)


def run_on_rust(client: Any, call: Callable[[], T]) -> T:
    """Helper for tests: run ``call``, return its result, and fail the test if
    ``call`` did not start an operation in the SDK's compiled code.

    Example::

        run_on_rust(client, lambda: orders.read_item(item_id, partition_key="b"))

    The check compares an operation counter before and after ``call``. The
    counter is shared by the whole Python process, so the test must not make
    other SDK calls from another thread or async task while ``call`` runs.
    """
    assert_rust_client(client)
    before = _binding_operation_count()
    try:
        return call()
    finally:
        assert _binding_operation_count() > before, "call did not enter the Rust binding"


async def run_on_rust_async(client: Any, call: Callable[[], Awaitable[T]]) -> T:
    """Async twin of :func:`run_on_rust`."""
    assert_rust_client(client)
    before = _binding_operation_count()
    try:
        return await call()
    finally:
        assert _binding_operation_count() > before, "call did not enter the Rust binding"
