# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Concrete, data-derived backend provenance for the perf drill.

WHY THIS EXISTS (plain English):
  Every results row is tagged ``config_backend`` from the ``COSMOS_BACKEND``
  environment variable -- a LABEL we declare, not a fact we measured. That is the
  single biggest source of error in the whole drill: a row that says "rust" could
  actually have run the core-python (azure-core) path -- the requested driver
  failed to load, the factory was misconfigured, or an individual operation fell
  back to the legacy pipeline -- and every number on that row would then describe
  the wrong engine while looking perfectly healthy.

  This module replaces "trust the flag" with "derive it from the rows". The
  azure-cosmos item helpers run an operation through the Rust driver ONLY when
  ``self._backend.execute(prepared)`` returns a non-None response; on ``None``
  (or when no backend object exists at all) the very same call silently falls
  back to ``client_connection.<Op>`` -- the pure core-python path. So the
  concrete, measurable truth is: *how many operations did the Rust driver
  actually fulfil?*

  The perf harness wraps the live ``_backend.execute`` with a counter (see
  ``workload._wrap_backend_for_provenance``) that increments once per operation
  the Rust driver actually returned a response for. The reporter then stamps two
  fields on every window row:

    * ``runtime_backend``    -- the class name of the backend object the client
                               REALLY built (``AsyncRustBackend`` / ``RustBackend``
                               for Rust, ``core-python`` when the object is None),
                               read off the live client, not the env var.
    * ``rust_execute_calls`` -- operations the Rust driver fulfilled in THIS
                               window. For a genuine Rust run this tracks
                               ``count``; for a core-python run it is 0 because the
                               wrapper is never installed (there is no backend
                               object to wrap).

  From those two fields anyone can DERIVE the real outcome straight from the
  results container, independent of the label: a "rust"-tagged cell whose
  ``rust_execute_calls`` is ~0 while it did real work was NOT actually running on
  Rust, and ``perf_validate.py`` fails the run on exactly that mismatch.

  Counting is harness-only (it wraps the backend object the test created); it adds
  one lock-guarded integer increment per operation on the Rust path, which already
  performs an FFI hop plus a network round trip, so it does not bias the numbers.
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

    This is the deepest provenance signal: a counter incremented INSIDE the Rust
    extension on every operation it runs, so a non-zero value is proof the binding
    code executed -- independent of the COSMOS_BACKEND flag and of the Python-side
    wrapper. Returns None when the extension is not importable or predates the
    counter (an older build), so callers can degrade gracefully to the Python-side
    signals rather than crash.
    """
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
