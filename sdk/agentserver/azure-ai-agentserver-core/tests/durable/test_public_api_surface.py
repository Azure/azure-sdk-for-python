# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public API surface tests for ``azure.ai.agentserver.core.durable``.

Spec 015 Phase 3 (FR-006): the public ``__all__`` of the ``durable`` package
is the authoritative developer surface. ``TaskSuspended``, ``TaskOptions``,
and ``TaskInfo`` are demoted to internal symbols. ``Task.get()`` / ``Task.list()``
are renamed to ``Task._get()`` / ``Task._list()`` to mark them internal-only
(the canonical inspection paths are ``manager.provider.get()`` /
``manager.list_tasks()``).

These tests are the GREEN target for Spec 015 Phase 3 and are referenced by
``test_contract_completeness.py`` (Constitution Principle XII).
"""

from __future__ import annotations

import ast
from pathlib import Path


_PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "azure" / "ai" / "agentserver" / "core"
_DURABLE_INIT = _PACKAGE_ROOT / "durable" / "__init__.py"


# Post-Phase-3 expected exact public surface (FR-006).
EXPECTED_PUBLIC_ALL: frozenset[str] = frozenset(
    {
        "task",
        "Task",
        "QueueStreamHandler",
        "RetryPolicy",
        "StreamHandler",
        "StreamHandlerFactory",
        "TaskContext",
        "TaskMetadata",
        "TaskResult",
        "TaskRun",
        "Suspended",
        "TaskStatus",
        "TaskFailed",
        "TaskCancelled",
        "TaskNotFound",
        "TaskConflictError",
        "TaskTerminated",
        "LastInputIdPreconditionFailed",
        "SteeringQueueFull",
        "TaskPreconditionFailed",
        "EntryMode",
    }
)


RETIRED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        "TaskSuspended",
        "TaskOptions",
        "TaskInfo",
    }
)


def _parse_all_from_init() -> set[str]:
    """Return the ``__all__`` list defined in ``durable/__init__.py``.

    Uses AST parsing to avoid triggering imports.
    """
    tree = ast.parse(_DURABLE_INIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    value = node.value
                    if isinstance(value, (ast.List, ast.Tuple)):
                        return {
                            elt.value
                            for elt in value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        }
    raise AssertionError("__all__ not found in durable/__init__.py")


def test_public_all_matches_expected_set() -> None:
    """FR-006: ``__all__`` exactly equals the post-cleanup expected set.

    Drift in either direction is a contract change and must be reviewed
    via Spec 015 successor process.
    """
    actual = _parse_all_from_init()
    extra = actual - EXPECTED_PUBLIC_ALL
    missing = EXPECTED_PUBLIC_ALL - actual

    assert not (extra or missing), (
        f"durable.__all__ drift detected.\n"
        f"  extra (in __all__ but not expected): {sorted(extra)}\n"
        f"  missing (expected but not in __all__): {sorted(missing)}"
    )


def test_retired_symbols_absent_from_all() -> None:
    """FR-006: TaskSuspended / TaskOptions / TaskInfo must NOT be re-exported."""
    actual = _parse_all_from_init()
    leaked = RETIRED_PUBLIC_SYMBOLS & actual

    assert not leaked, (
        f"Retired symbols leaked back into durable.__all__: {sorted(leaked)}. "
        f"These were demoted to internal in Spec 015 Phase 3 (FR-006) and "
        f"must not be re-exported."
    )


def test_task_get_list_renamed_to_private() -> None:
    """FR-006: ``Task.get`` / ``Task.list`` are renamed to ``Task._get`` / ``Task._list``.

    The public ``.get()`` / ``.list()`` methods on the ``Task`` decorator
    are demoted to internal. The canonical inspection paths are
    ``manager.provider.get()`` and ``manager.list_tasks()``.
    """
    from azure.ai.agentserver.core.durable import Task

    assert not hasattr(Task, "get") or not callable(getattr(Task, "get", None)), (
        "Task.get must be renamed to Task._get in Spec 015 Phase 3 (FR-006). "
        "Public-surface inspection should go through manager.provider.get()."
    )
    assert not hasattr(Task, "list") or not callable(getattr(Task, "list", None)), (
        "Task.list must be renamed to Task._list in Spec 015 Phase 3 (FR-006). "
        "Public-surface listing should go through manager.list_tasks()."
    )
    assert hasattr(Task, "_get") and callable(Task._get), (
        "Task._get (internal rename) must remain callable."
    )
    assert hasattr(Task, "_list") and callable(Task._list), (
        "Task._list (internal rename) must remain callable."
    )
