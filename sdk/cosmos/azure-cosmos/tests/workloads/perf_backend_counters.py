# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Record configured backend identity and available execution counters.

runtime_backend is the class name recorded from the constructed backend.
The workload wraps non-core execute calls and counts normal returns,
without inspecting the returned value. Errors are not counted there.
These Python counts are not proof of successful service operations.

Native counters are process-wide observations at explicit binding sites.
They can include unrelated work, and do not cover every native path.
Their overhead is not measured by this module.
"""

import threading

_lock = threading.Lock()
_execute_calls = 0
_runtime_backend = "core-python"


def record_execute(n: int = 1) -> None:
    """Add n to the Python wrapper's process-wide normal-return count."""
    global _execute_calls
    with _lock:
        _execute_calls += n


def execute_count() -> int:
    """Read the cumulative Python wrapper count for this process."""
    with _lock:
        return _execute_calls


def set_runtime_backend(name: str) -> None:
    """Record the class name of the backend the client really built."""
    global _runtime_backend
    _runtime_backend = name or "core-python"


def runtime_backend() -> str:
    """The concrete backend identity of the live client (not the env flag)."""
    return _runtime_backend


def _rust_counter(name: str):
    """Read an exposed native counter as an integer.

    Return None if importing the extension, finding the function, calling it,
    or converting its result fails. None therefore means unavailable evidence,
    not just an old build or a missing extension.
    """
    # Imported lazily: the compiled _rust extension is absent on hosts without the
    # Rust build, and importing it at module load would break those hosts.
    module = None
    try:
        from azure.cosmos import _rust as module  # type: ignore[attr-defined]
    except Exception:
        try:
            import _rust as module  # type: ignore
        except Exception:
            return None
    fn = getattr(module, name, None)
    if fn is None:
        return None
    try:
        return int(fn())
    except Exception:
        return None


def binding_operation_count():
    """Read the process-wide count at instrumented binding entry points.

    Entry can precede failure, and local operations can increment it. A delta
    is not a census of successful operations or HTTP requests.
    """
    return _rust_counter("operation_count")


def binding_attempt_count():
    """Read accumulated request_count values from recorded diagnostics contexts.

    Unrecorded contexts and paths are not covered. This is not a universal
    round-trip count, nor does it establish a fixed number of attempts per PATCH.
    Return None when the counter cannot be read.
    """
    return _rust_counter("attempt_count")


def binding_retry_count():
    """Read non-initial request records counted by the binding.

    Only retained records in diagnostics contexts reaching the recorder are
    examined; compaction or unrecorded paths can leave retries uncounted.
    Zero is therefore not proof that no retry occurred.
    """
    return _rust_counter("retry_count")
