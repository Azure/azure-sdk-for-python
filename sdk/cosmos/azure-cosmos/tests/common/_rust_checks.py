# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Checks that a call really ran through the Rust binding.

Standalone Rust behavior tests (modules carrying the ``# Rust behavior test``
header) use these helpers instead of the retiring parity framework.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Mapping, Sequence, TypeVar

from config.diagnostics import _binding_operation_count, _rust_fallback_count

T = TypeVar("T")


def assert_live_page_headers(snapshots: Sequence[Mapping[str, Any]]) -> None:
    """Require charged, diagnosed service pages with distinct activity IDs."""
    assert snapshots, "no page headers were captured"
    activity_ids = []
    for headers in snapshots:
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
    """Run ``call`` and fail unless it entered the binding without falling back.

    Counters are process-wide, so keep the checked call isolated from
    unrelated concurrent work.
    """
    assert_rust_client(client)
    before = _binding_operation_count()
    fallback_before = _rust_fallback_count()
    try:
        return call()
    finally:
        assert _binding_operation_count() > before, "call did not enter the Rust binding"
        assert _rust_fallback_count() == fallback_before, "call fell back to core-python"


async def run_on_rust_async(client: Any, call: Callable[[], Awaitable[T]]) -> T:
    """Async twin of :func:`run_on_rust`."""
    assert_rust_client(client)
    before = _binding_operation_count()
    fallback_before = _rust_fallback_count()
    try:
        return await call()
    finally:
        assert _binding_operation_count() > before, "call did not enter the Rust binding"
        assert _rust_fallback_count() == fallback_before, "call fell back to core-python"
