# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Area D — ``TaskMetadata.flush_all`` becomes internal
(, SC-12).

Verifies that ``TaskMetadata.flush_all`` is renamed
``_flush_all`` — the leading underscore is the Python convention
for "package-private; not part of the documented developer
surface." The framework's manager call sites switch over to the
underscored name. Direct user calls on the public attribute MUST
raise ``AttributeError``.

Reference: docs/task-and-streaming-spec.md §37, §59 C-MET-4.
"""

from __future__ import annotations

import pytest


def test_flush_all_renamed_to_underscore_flush_all() -> None:
    """/ SC-12 — ``TaskMetadata.flush_all`` MUST be absent;
    the rename target ``_flush_all`` MUST exist and remain async.

    The leading underscore signals "framework-internal" — direct
    user code should never reach for this; per-namespace ``flush()``
    is the developer-facing fence primitive.
    """
    from azure.ai.agentserver.core.tasks import TaskMetadata

    assert not hasattr(TaskMetadata, "flush_all"), (
        "TaskMetadata.flush_all must be removed; the " "rename target is the leading-underscore _flush_all."
    )
    assert hasattr(TaskMetadata, "_flush_all"), (
        "TaskMetadata._flush_all (the framework-internal lifecycle " "helper) MUST exist."
    )
    import inspect

    assert inspect.iscoroutinefunction(TaskMetadata._flush_all), (
        "_flush_all MUST remain a coroutine function " "(its semantics are unchanged from the public flush_all)."
    )
