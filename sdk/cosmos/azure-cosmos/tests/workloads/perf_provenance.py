# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Backend provenance for the perf drill, derived from the rows, not the env flag.

Each results row is tagged ``config_backend`` from the ``COSMOS_BACKEND`` variable,
which is a label, not a measurement. A row that says "rust" could have run the
core-python path if the driver failed to load or an operation fell back. This
module records what actually ran so the label can be checked.

The item helpers run an operation through the Rust driver only when
``backend.execute(prepared)`` returns a non-None response; otherwise they fall back
to core-python. The harness wraps ``execute`` with a counter (see
``workload._wrap_backend_for_provenance``), and the reporter stamps two fields on
every row:

  * ``runtime_backend``    -- the class name of the backend object the client built.
  * ``rust_execute_calls`` -- operations the Rust driver handled this window (0 on a
                              core-python run, which has no backend object).

From those, ``perf_validate.py`` can confirm a "rust"-tagged row really ran on Rust.
The counter adds one lock-guarded increment per Rust operation, which is negligible
next to the network round trip.
"""

import threading

_lock = threading.Lock()
_execute_calls = 0
_runtime_backend = "core-python"


def record_execute(n: int = 1) -> None:
    """Count ``n`` operations actually fulfilled by the Rust driver."""
    global _execute_calls
    with _lock:
        _execute_calls += n


def execute_count() -> int:
    """Cumulative operations the Rust driver has fulfilled in this process."""
    with _lock:
        return _execute_calls


def set_runtime_backend(name: str) -> None:
    """Record the class name of the backend the client really built."""
    global _runtime_backend
    _runtime_backend = name or "core-python"


def runtime_backend() -> str:
    """The concrete backend identity of the live client (not the env flag)."""
    return _runtime_backend


def binding_operation_count():
    """Operations the Rust binding itself has counted (``_rust.operation_count``).

    A non-zero value is proof the binding ran, independent of COSMOS_BACKEND and the
    Python-side wrapper. Returns None when the extension is not importable or has no
    counter (an older build), so callers can fall back to the Python-side signals.
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
    fn = getattr(module, "operation_count", None)
    if fn is None:
        return None
    try:
        return int(fn())
    except Exception:
        return None
