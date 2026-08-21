# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public API surface tests for ``azure.ai.agentserver.core.tasks``.

: the public ``__all__`` of the ``resilient`` package
is the authoritative developer surface. ``TaskSuspended``, ``TaskOptions``,
and ``TaskInfo`` are demoted to internal symbols. ``Task.get()`` / ``Task.list()``
are renamed to ``Task._get()`` / ``Task._list()`` to mark them internal-only
(the canonical inspection paths are ``manager.provider.get()`` /
``manager.list_tasks()``).

These tests are the GREEN target and are referenced by
``test_contract_completeness.py`` (Constitution Principle XII).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


_PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "azure" / "ai" / "agentserver" / "core"
_RESILIENT_INIT = _PACKAGE_ROOT / "tasks" / "__init__.py"


# Post-Phase-3  + post-SOT-Phase-1 expected exact public
# surface.
#
#: TaskTerminated removed from __all__.
#  /: StreamHandler / QueueStreamHandler /
# StreamHandlerFactory removed from __all__; streaming lives in the
# peer ``azure.ai.agentserver.core.streaming`` subpackage.
EXPECTED_PUBLIC_ALL: frozenset[str] = frozenset(
    {
        # Decorators + task classes (class split)
        "task",
        "multi_turn_task",
        "Task",
        "MultiTurnTask",
        # Enablement switch
        "set_resilient_tasks_enabled",
        "resilient_tasks_enabled",
        "RetryPolicy",
        "TaskContext",
        # Type aliases + TypedDicts
        "JSONValue",
        "TaskErrorDict",
        "TaskExhaustedRetriesErrorDict",
        # ----- Legacy surface (still in __all__ during transition) -----
        "TaskRun",
        "TaskFailed",
        "TaskCancelled",
        "TaskDeferred",  # NEW
        "TaskConflictError",
        "LastInputIdPreconditionFailed",
        "SteeringQueueFull",
        "EntryMode",
        #  /   — developer-facing size errors.
        "InputTooLarge",
        # Typed "no resilient-task subsystem installed" failure.
        "TaskManagerNotInitialized",
    }
)


RETIRED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        "TaskSuspended",
        "TaskOptions",
        "TaskInfo",
        #: dropped from __all__ as preparatory Phase 9 work.
        "TaskTerminated",
        #   /  — removed from public, internal-only.
        "TaskNotFound",
        "TaskPreconditionFailed",
        "OutputTooLarge",
        #   /  — fully deleted from package.
        "TaskResult",
        "TaskSnapshot",
        #   /  — removed from public surface.
        "Suspended",
        "TaskStatus",
        #   /  — attachment-vocabulary errors are
        # internal implementation details (developers never name attachments).
        "AttachmentTooLarge",
        "AttachmentLimitExceeded",
    }
)


def _parse_all_from_init() -> set[str]:
    """Return the ``__all__`` list defined in ``tasks/__init__.py``.

    Uses AST parsing to avoid triggering imports.
    """
    tree = ast.parse(_RESILIENT_INIT.read_text(encoding="utf-8"))
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
    raise AssertionError("__all__ not found in tasks/__init__.py")


def test_public_all_matches_expected_set() -> None:
    """: ``__all__`` exactly equals the post-cleanup expected set.

    Drift in either direction is a contract change and must be reviewed
    via  successor process.
    """
    actual = _parse_all_from_init()
    extra = actual - EXPECTED_PUBLIC_ALL
    missing = EXPECTED_PUBLIC_ALL - actual

    assert not (extra or missing), (
        f"resilient.__all__ drift detected.\n"
        f"  extra (in __all__ but not expected): {sorted(extra)}\n"
        f"  missing (expected but not in __all__): {sorted(missing)}"
    )


def test_retired_symbols_absent_from_all() -> None:
    """: TaskSuspended / TaskOptions / TaskInfo must NOT be re-exported."""
    actual = _parse_all_from_init()
    leaked = RETIRED_PUBLIC_SYMBOLS & actual

    assert not leaked, (
        f"Retired symbols leaked back into resilient.__all__: {sorted(leaked)}. "
        f"These were demoted to internal in   and "
        f"must not be re-exported."
    )


# --------------------------------------------------------------------- #
#  — T017: HostedTaskProvider.__init__ credential typing
# --------------------------------------------------------------------- #


def test_hosted_provider_credential_typed_as_async_token_credential() -> None:
    """: ``HostedTaskProvider.__init__``'s ``credential``
    parameter MUST be annotated as ``AsyncTokenCredential`` (or a
    compatible type). The legacy ``Any`` annotation hid type errors
    at construction sites.

    Asserted by inspecting the runtime annotation; an
    isinstance check on actual credentials is intentionally NOT done
    here because :class:`AsyncTokenCredential` is a structural type
    (Protocol-like).
    """
    import inspect

    from azure.ai.agentserver.core.tasks._client import HostedTaskProvider

    sig = inspect.signature(HostedTaskProvider.__init__)
    cred_param = sig.parameters.get("credential")
    assert cred_param is not None, "HostedTaskProvider.__init__ has no `credential` parameter"

    annotation = cred_param.annotation
    # Either the real azure.core.credentials_async.AsyncTokenCredential class
    # or a string annotation (PEP 563) referring to it. Both are acceptable.
    annotation_str = annotation.__name__ if hasattr(annotation, "__name__") else str(annotation)
    assert "AsyncTokenCredential" in annotation_str, (
        f"`credential` parameter must be typed as `AsyncTokenCredential` " f"; got {annotation_str!r}."
    )


# --------------------------------------------------------------------- #
#  — T018: httpx import readiness (lands RED until T024 lands)
# --------------------------------------------------------------------- #


def test_httpx_absent_from_production_resilient_package() -> None:
    """+ T024: ``import httpx`` MUST not appear anywhere
    under the resilient subpackage's production source tree. The
    transport migration to ``azure.core.AsyncPipelineClient`` removes
    the dependency entirely.

    Per the test_dev_guide_review pattern, this scan only inspects
    the resilient subpackage — we do NOT walk the broader package because
    other modules (host, base) may legitimately retain httpx during
    the rollout window.
    """
    import re

    resilient_dir = _PACKAGE_ROOT / "tasks"
    offenders: list[tuple[str, int]] = []
    pattern = re.compile(r"^\s*(?:import\s+httpx\b|from\s+httpx\b)", re.MULTILINE)
    for py_file in resilient_dir.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        matches = list(pattern.finditer(text))
        if matches:
            line_no = text[: matches[0].start()].count("\n") + 1
            offenders.append((str(py_file.relative_to(_PACKAGE_ROOT)), line_no))

    assert not offenders, (
        f"httpx imports still present under resilient subpackage ("
        f"T024 /): {offenders}. Migrate the call site to "
        f"`azure.core.rest.HttpRequest` / `AsyncPipelineClient.send_request` "
        f"and remove the import."
    )


# --------------------------------------------------------------------- #
#   / SC-001 — T026: stale_timeout / _is_stale absence
# --------------------------------------------------------------------- #


def test_task_options_has_no_stale_timeout_slot() -> None:
    """SC-001: the (internal) TaskOptions slot for ``stale_timeout`` is gone.

    Asserted via slot inspection — the slot is no longer part of the
    TaskOptions __slots__ tuple. Constructing TaskOptions with
    ``stale_timeout=...`` would fail with the same TypeError as any
    other unknown kwarg.
    """
    from azure.ai.agentserver.core.tasks._decorator import TaskOptions

    assert (
        "stale_timeout" not in TaskOptions.__slots__
    ), "TaskOptions.__slots__ must NOT contain 'stale_timeout' (" " /). Found: {}".format(TaskOptions.__slots__)

    # Also assert the slot is not an instance attribute (catches subclass
    # or runtime monkey-patching attempts to add it back).
    sample = TaskOptions(name="test")
    assert not hasattr(sample, "stale_timeout"), "TaskOptions instance must NOT expose a 'stale_timeout' attribute " "."


def test_is_stale_not_importable_from_resilient_subpackage() -> None:
    """SC-001: ``_is_stale`` MUST NOT be importable from any module under
    ``azure/ai/agentserver/core/tasks/``.

    Per 's "any helper named after staleness" qualifier, the
    helper itself is removed (not just dropped from a public list).
    Phase 6 of  (T053-T058) replaces the staleness concept
    entirely with the  /  lease-based reclaim path
    (``_reclaim_one`` + ``_lease_is_dead``).
    """
    import re

    resilient_dir = _PACKAGE_ROOT / "tasks"
    offenders: list[tuple[str, int]] = []
    # Match ``def _is_stale(`` or ``_is_stale =``, plus literal
    # ``from .... import ... _is_stale`` / ``import _is_stale``. We
    # intentionally permit prose mentions in comments so the
    # transitional ``_in_progress_was_abandoned_legacy`` docstring can
    # cite the predecessor by name.
    pattern = re.compile(
        r"^\s*(?:def\s+_is_stale\b|_is_stale\s*=|from\s+\S+\s+import.*\b_is_stale\b|import\s+_is_stale\b)", re.MULTILINE
    )
    for py_file in resilient_dir.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            offenders.append((str(py_file.relative_to(_PACKAGE_ROOT)), line_no))

    assert not offenders, (
        f"_is_stale name still defined / importable under resilient subpackage "
        f": {offenders}. Replace with the transitional "
        f"`_in_progress_was_abandoned_legacy` (Phase 4) or the Phase-6 lease-"
        f"based reclaim (`_reclaim_one` + `_lease_is_dead`)."
    )
