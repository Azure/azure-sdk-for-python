# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Process-safety tests for the local FoundryStateStore backend."""

from __future__ import annotations

import asyncio
import json
import multiprocessing
import os
import time
from pathlib import Path
from typing import Any

import pytest
from azure.ai.agentserver.core.storage import (
    FoundryStateStore,
    FoundryStorageConflictError,
    FoundryStorageNotFoundError,
    FoundryStoragePreconditionError,
)

_PROCESS_DEADLINE_SECONDS = 20


def _configure_local_mode(root: str) -> None:
    os.environ.pop("FOUNDRY_HOSTING_ENVIRONMENT", None)
    os.environ["AGENTSERVER_STATE_ROOT"] = root


async def _perform_operation(
    store_name: str,
    operation: str,
    key: str,
    value: int,
    etag: str | None = None,
) -> str:
    if operation == "ensure":
        await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
        return "success"

    store = FoundryStateStore(store_name)
    return await _perform_bound_operation(store, operation, key, value, etag)


async def _perform_bound_operation(
    store: FoundryStateStore,
    operation: str,
    key: str,
    value: int,
    etag: str | None = None,
) -> str:
    if operation == "create":
        await store.create_item(key, {"value": value})
    elif operation == "set":
        await store.set_item(key, {"value": value}, if_match=etag)
    elif operation == "require_exists":
        await store.set_item(key, {"value": value}, require_exists=True)
    elif operation == "delete_item":
        await store.delete_item(key)
    elif operation == "delete_store":
        await store.delete()
    elif operation == "get_item":
        item = await store.get_item(key)
        return "item" if item is not None else "none"
    else:  # pragma: no cover - test helper misuse
        raise AssertionError(f"Unknown operation: {operation}")
    return "success"


def _record_exception(outcomes: Any, exc: Exception) -> None:
    if isinstance(exc, FoundryStoragePreconditionError):
        outcomes.put("precondition")
    elif isinstance(exc, FoundryStorageConflictError):
        outcomes.put("conflict")
    elif isinstance(exc, FoundryStorageNotFoundError):
        outcomes.put("not_found")
    elif isinstance(exc, FileNotFoundError):
        outcomes.put("file_not_found")
    elif isinstance(exc, PermissionError):
        outcomes.put("permission")
    else:
        outcomes.put(type(exc).__name__)


def _operation_process(
    root: str,
    store_name: str,
    operation: str,
    key: str,
    value: int,
    etag: str | None,
    gate: Any | None,
    outcomes: Any,
) -> None:
    _configure_local_mode(root)
    if gate is not None:
        gate.wait()
    try:
        outcome = asyncio.run(
            _perform_operation(store_name, operation, key, value, etag)
        )
        outcomes.put(outcome)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _record_exception(outcomes, exc)


def _blocking_read_process(
    root: str,
    store_name: str,
    operation: str,
    key: str,
    value: int,
    block_on_read: int,
    ready: Any,
    release: Any,
    outcomes: Any | None,
) -> None:
    _configure_local_mode(root)

    async def run() -> str:
        store = FoundryStateStore(store_name)
        backend = store._local_backend  # pylint: disable=protected-access
        assert backend is not None
        original_read = backend._read  # pylint: disable=protected-access
        read_count = 0

        def blocking_read() -> dict[str, Any] | None:
            nonlocal read_count
            document = original_read()
            read_count += 1
            if read_count == block_on_read:
                ready.set()
                assert release.wait(_PROCESS_DEADLINE_SECONDS)
            return document

        backend._read = blocking_read  # type: ignore[method-assign]  # pylint: disable=protected-access
        return await _perform_bound_operation(store, operation, key, value)

    try:
        outcome = asyncio.run(run())
        if outcomes is not None:
            outcomes.put(outcome)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        if outcomes is not None:
            _record_exception(outcomes, exc)


def _waiting_operation_process(
    root: str,
    store_name: str,
    operation: str,
    key: str,
    value: int,
    attempting: Any,
    outcomes: Any | None,
) -> None:
    from azure.ai.agentserver.core.storage import (
        _local_state,
    )  # pylint: disable=import-outside-toplevel

    _configure_local_mode(root)
    original_acquire = (
        _local_state._acquire_file_lock
    )  # pylint: disable=protected-access

    def notifying_acquire(lock_file: Any) -> None:
        attempting.set()
        original_acquire(lock_file)

    _local_state._acquire_file_lock = (
        notifying_acquire  # pylint: disable=protected-access
    )
    try:
        outcome = asyncio.run(_perform_operation(store_name, operation, key, value))
        outcomes.put(outcome)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _record_exception(outcomes, exc)


def _get_during_delete_process(
    root: str,
    store_name: str,
    ready: Any,
    release: Any,
    outcomes: Any,
) -> None:
    _configure_local_mode(root)

    async def run() -> None:
        store = FoundryStateStore(store_name)
        backend = store._local_backend  # pylint: disable=protected-access
        assert backend is not None
        store_path = backend._path  # pylint: disable=protected-access
        original_read_text = Path.read_text

        def blocking_read_text(path: Path, *args: Any, **kwargs: Any) -> str:
            if path == store_path:
                ready.set()
                assert release.wait(_PROCESS_DEADLINE_SECONDS)
            return original_read_text(path, *args, **kwargs)

        Path.read_text = blocking_read_text  # type: ignore[method-assign]
        try:
            await store.get()
        finally:
            Path.read_text = original_read_text  # type: ignore[method-assign]

    try:
        asyncio.run(run())
        outcomes.put("success")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _record_exception(outcomes, exc)


def _read_with_open_file_process(
    root: str,
    store_name: str,
    ready: Any,
    release: Any,
    outcomes: Any,
) -> None:
    _configure_local_mode(root)

    async def run() -> None:
        store = FoundryStateStore(store_name)
        backend = store._local_backend  # pylint: disable=protected-access
        assert backend is not None
        store_path = backend._path  # pylint: disable=protected-access
        original_open = Path.open

        class BlockingReader:
            def __init__(self, opened_file: Any) -> None:
                self._opened_file = opened_file

            def __enter__(self) -> "BlockingReader":
                self._opened_file.__enter__()
                return self

            def __exit__(self, *args: Any) -> Any:
                return self._opened_file.__exit__(*args)

            def read(self, *args: Any, **kwargs: Any) -> str:
                ready.set()
                assert release.wait(_PROCESS_DEADLINE_SECONDS)
                return self._opened_file.read(*args, **kwargs)

        def blocking_open(path: Path, *args: Any, **kwargs: Any) -> Any:
            opened_file = original_open(path, *args, **kwargs)
            return BlockingReader(opened_file) if path == store_path else opened_file

        Path.open = blocking_open  # type: ignore[method-assign]
        try:
            await store.get()
        finally:
            Path.open = original_open  # type: ignore[method-assign]

    try:
        asyncio.run(run())
        outcomes.put("success")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _record_exception(outcomes, exc)


def _collect_process_outcomes(processes: list[Any], outcomes: Any) -> list[str]:
    deadline = time.monotonic() + _PROCESS_DEADLINE_SECONDS
    for process in processes:
        process.join(max(0, deadline - time.monotonic()))
    stuck = [process for process in processes if process.is_alive()]
    for process in stuck:
        process.terminate()
        process.join(5)
    assert not stuck
    assert [process.exitcode for process in processes] == [0] * len(processes)
    return [outcomes.get(timeout=5) for _ in processes]


def _run_local_operations(
    root: Path,
    store_name: str,
    operation: str,
    items: list[tuple[str, int]],
    etag: str | None = None,
) -> list[str]:
    context = multiprocessing.get_context("spawn")
    gate = context.Barrier(len(items))
    outcomes = context.Queue()
    processes = [
        context.Process(
            target=_operation_process,
            args=(str(root), store_name, operation, key, value, etag, gate, outcomes),
        )
        for key, value in items
    ]
    for process in processes:
        process.start()
    return _collect_process_outcomes(processes, outcomes)


def _start_blocked_operation(
    context: Any,
    root: Path,
    store_name: str,
    operation: str,
    key: str,
    value: int,
    outcomes: Any,
    *,
    block_on_read: int = 1,
) -> tuple[Any, Any, Any]:
    ready = context.Event()
    release = context.Event()
    process = context.Process(
        target=_blocking_read_process,
        args=(
            str(root),
            store_name,
            operation,
            key,
            value,
            block_on_read,
            ready,
            release,
            outcomes,
        ),
    )
    process.start()
    assert ready.wait(_PROCESS_DEADLINE_SECONDS)
    return process, release, ready


def _run_ordered_operations(
    root: Path,
    store_name: str,
    holder_operation: str,
    holder_key: str,
    waiter_operation: str,
    waiter_key: str,
    *,
    block_on_read: int = 1,
) -> list[str]:
    context = multiprocessing.get_context("spawn")
    outcomes = context.Queue()
    holder, release, _ = _start_blocked_operation(
        context,
        root,
        store_name,
        holder_operation,
        holder_key,
        0,
        outcomes,
        block_on_read=block_on_read,
    )
    attempting = context.Event()
    waiter = context.Process(
        target=_waiting_operation_process,
        args=(
            str(root),
            store_name,
            waiter_operation,
            waiter_key,
            1,
            attempting,
            outcomes,
        ),
    )
    waiter.start()
    try:
        assert attempting.wait(_PROCESS_DEADLINE_SECONDS)
        release.set()
        return _collect_process_outcomes([holder, waiter], outcomes)
    finally:
        release.set()
        for process in (holder, waiter):
            if process.is_alive():
                process.terminate()
                process.join(5)


@pytest.fixture
def local_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    return tmp_path


@pytest.mark.asyncio
async def test_local_backend_preserves_concurrent_process_updates(
    local_root: Path,
) -> None:
    store = await FoundryStateStore.get_or_create(
        "local-process-updates", item_ttl_seconds=-1
    )
    process_count = 8
    results = _run_local_operations(
        local_root,
        "local-process-updates",
        "set",
        [(f"key-{index}", index) for index in range(process_count)],
    )
    page = await store.list_keys(limit=100)

    assert results == ["success"] * process_count
    assert {item.key for item in page.keys} == {
        f"key-{index}" for index in range(process_count)
    }


@pytest.mark.asyncio
async def test_local_backend_serializes_if_match_across_processes(
    local_root: Path,
) -> None:
    store = await FoundryStateStore.get_or_create(
        "local-process-etag", item_ttl_seconds=-1
    )
    created = await store.create_item("counter", {"value": 0})
    process_count = 8
    results = _run_local_operations(
        local_root,
        "local-process-etag",
        "set",
        [("counter", index) for index in range(process_count)],
        created.etag,
    )

    assert results.count("success") == 1
    assert results.count("precondition") == process_count - 1


@pytest.mark.asyncio
async def test_local_backend_serializes_create_conflicts_across_processes(
    local_root: Path,
) -> None:
    await FoundryStateStore.get_or_create("local-process-create", item_ttl_seconds=-1)
    process_count = 8
    results = _run_local_operations(
        local_root,
        "local-process-create",
        "create",
        [("shared", index) for index in range(process_count)],
    )

    assert results.count("success") == 1
    assert results.count("conflict") == process_count - 1


@pytest.mark.asyncio
async def test_local_backend_serializes_require_exists_across_processes(
    local_root: Path,
) -> None:
    store = await FoundryStateStore.get_or_create(
        "local-process-require-exists", item_ttl_seconds=-1
    )
    await store.set_item("sentinel", {"value": "retained"})
    process_count = 8

    missing = _run_local_operations(
        local_root,
        "local-process-require-exists",
        "require_exists",
        [("shared", index) for index in range(process_count)],
    )
    await store.create_item("shared", {"value": -1})
    existing = _run_local_operations(
        local_root,
        "local-process-require-exists",
        "require_exists",
        [("shared", index) for index in range(process_count)],
    )
    page = await store.list_keys(limit=100)

    assert missing == ["precondition"] * process_count
    assert existing == ["success"] * process_count
    assert {item.key for item in page.keys} == {"sentinel", "shared"}


@pytest.mark.asyncio
async def test_local_backend_initializes_one_lock_byte_across_processes(
    local_root: Path,
) -> None:
    process_count = 8
    results = _run_local_operations(
        local_root,
        "local-process-initialize",
        "ensure",
        [("", index) for index in range(process_count)],
    )
    store = FoundryStateStore("local-process-initialize")
    backend = store._local_backend  # pylint: disable=protected-access
    assert backend is not None
    lock_path = backend._interprocess_lock_path  # pylint: disable=protected-access

    assert results == ["success"] * process_count
    assert lock_path.read_bytes() == b"\0"


@pytest.mark.asyncio
async def test_local_backend_get_during_delete_maps_to_not_found(
    local_root: Path,
) -> None:
    store_name = "local-process-get-delete"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    outcomes = context.Queue()
    process = context.Process(
        target=_get_during_delete_process,
        args=(str(local_root), store_name, ready, release, outcomes),
    )
    process.start()
    try:
        assert ready.wait(_PROCESS_DEADLINE_SECONDS)
        await store.delete()
        release.set()
        results = _collect_process_outcomes([process], outcomes)
    finally:
        release.set()
        if process.is_alive():
            process.terminate()
            process.join(5)

    assert results == ["not_found"]


@pytest.mark.asyncio
async def test_local_backend_reader_with_open_file_allows_replacement(
    local_root: Path,
) -> None:
    store_name = "local-process-open-read-replace"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    outcomes = context.Queue()
    reader = context.Process(
        target=_read_with_open_file_process,
        args=(str(local_root), store_name, ready, release, outcomes),
    )
    reader.start()
    try:
        assert ready.wait(_PROCESS_DEADLINE_SECONDS)
        await store.set_item("replacement", {"value": 1})
        release.set()
        results = _collect_process_outcomes([reader], outcomes)
    finally:
        release.set()
        if reader.is_alive():
            reader.terminate()
            reader.join(5)

    assert results == ["success"]
    assert await store.get_item("replacement") is not None


@pytest.mark.asyncio
async def test_local_backend_reader_with_open_file_allows_delete(
    local_root: Path,
) -> None:
    store_name = "local-process-open-read-delete"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    outcomes = context.Queue()
    reader = context.Process(
        target=_read_with_open_file_process,
        args=(str(local_root), store_name, ready, release, outcomes),
    )
    reader.start()
    try:
        assert ready.wait(_PROCESS_DEADLINE_SECONDS)
        await store.delete()
        release.set()
        results = _collect_process_outcomes([reader], outcomes)
    finally:
        release.set()
        if reader.is_alive():
            reader.terminate()
            reader.join(5)

    assert results == ["success"]
    with pytest.raises(FoundryStorageNotFoundError):
        await store.get()


@pytest.mark.asyncio
async def test_local_backend_ttl_cleanup_preserves_waiting_writer(
    local_root: Path,
) -> None:
    store_name = "local-process-ttl"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    await store.create_item("expired", {"value": 0})
    backend = store._local_backend  # pylint: disable=protected-access
    assert backend is not None
    document = json.loads(
        backend._path.read_text(encoding="utf-8")
    )  # pylint: disable=protected-access
    document["items"]["expired"]["expires_at"] = 0
    backend._path.write_text(  # pylint: disable=protected-access
        json.dumps(document, indent=2, sort_keys=True), encoding="utf-8"
    )

    results = _run_ordered_operations(
        local_root,
        store_name,
        "get_item",
        "expired",
        "set",
        "fresh",
        block_on_read=2,
    )

    assert sorted(results) == ["none", "success"]
    assert await store.get_item("expired") is None
    assert await store.get_item("fresh") is not None


@pytest.mark.asyncio
async def test_local_backend_store_delete_orders_waiter_and_recreation(
    local_root: Path,
) -> None:
    store_name = "local-process-store-delete"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    backend = store._local_backend  # pylint: disable=protected-access
    assert backend is not None
    lock_path = backend._interprocess_lock_path  # pylint: disable=protected-access
    lock_identity = (lock_path.stat().st_dev, lock_path.stat().st_ino)

    results = _run_ordered_operations(
        local_root,
        store_name,
        "delete_store",
        "",
        "set",
        "after-delete",
    )

    assert sorted(results) == ["not_found", "success"]
    with pytest.raises(FoundryStorageNotFoundError):
        await store.get()
    assert lock_path.exists()
    assert (lock_path.stat().st_dev, lock_path.stat().st_ino) == lock_identity

    recreated = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    await recreated.set_item("recreated", {"value": 2})
    assert await recreated.get_item("recreated") is not None
    assert (lock_path.stat().st_dev, lock_path.stat().st_ino) == lock_identity


@pytest.mark.asyncio
async def test_local_backend_failed_missing_store_mutation_leaves_lock_artifact(
    local_root: Path,
) -> None:
    store = FoundryStateStore("local-process-missing-mutation")
    backend = store._local_backend  # pylint: disable=protected-access
    assert backend is not None
    lock_path = backend._interprocess_lock_path  # pylint: disable=protected-access

    with pytest.raises(FoundryStorageNotFoundError):
        await store.set_item("missing", {"value": 1})

    assert not backend._path.exists()  # pylint: disable=protected-access
    assert lock_path.read_bytes() == b"\0"


@pytest.mark.asyncio
async def test_local_backend_item_delete_orders_require_exists_waiter(
    local_root: Path,
) -> None:
    store_name = "local-process-item-delete"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    await store.create_item("shared", {"value": 0})

    results = _run_ordered_operations(
        local_root,
        store_name,
        "delete_item",
        "shared",
        "require_exists",
        "shared",
    )

    assert sorted(results) == ["precondition", "success"]
    assert await store.get_item("shared") is None


@pytest.mark.asyncio
async def test_local_backend_read_only_store_allows_nonmutating_reads(
    local_root: Path,
) -> None:
    if os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0):
        pytest.skip("POSIX non-root permissions required")

    store_name = "local-process-read-only"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    await store.create_item("item", {"value": 1})
    backend = store._local_backend  # pylint: disable=protected-access
    assert backend is not None
    store_path = backend._path  # pylint: disable=protected-access
    lock_path = getattr(backend, "_interprocess_lock_path", None)
    state_directory = store_path.parent

    store_path.chmod(0o400)
    if lock_path is not None:
        lock_path.chmod(0o400)
    state_directory.chmod(0o500)
    try:
        reopened = await FoundryStateStore.get_or_create(store_name)
        assert (await reopened.get()).name == store_name
        assert await reopened.get_item("item") is not None
        assert [item.key for item in (await reopened.list_keys()).keys] == ["item"]
    finally:
        state_directory.chmod(0o700)
        store_path.chmod(0o600)
        if lock_path is not None:
            lock_path.chmod(0o600)


@pytest.mark.asyncio
async def test_local_backend_releases_process_lock_after_termination(
    local_root: Path,
) -> None:
    store_name = "local-process-crash"
    store = await FoundryStateStore.get_or_create(store_name, item_ttl_seconds=-1)
    context = multiprocessing.get_context("spawn")
    process, _, _ = _start_blocked_operation(
        context, local_root, store_name, "set", "interrupted", 1, None
    )
    try:
        process.terminate()
        process.join(10)
        assert not process.is_alive()

        await store.set_item("after-termination", {"value": 2})
        item = await store.get_item("after-termination")
        assert item is not None
        assert item.value == {"value": 2}
    finally:
        if process.is_alive():
            process.terminate()
            process.join(5)
