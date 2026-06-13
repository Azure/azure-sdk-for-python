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

import pytest


_PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "azure" / "ai" / "agentserver" / "core"
_DURABLE_INIT = _PACKAGE_ROOT / "durable" / "__init__.py"


# Post-Phase-3 (Spec 015) + post-Spec-017-Phase-1 expected exact public
# surface.
#
# Spec 016 FR-022 (US6): TaskTerminated removed from __all__.
# Spec 017 FR-014/FR-015: StreamHandler / QueueStreamHandler /
# StreamHandlerFactory removed from __all__; streaming lives in the
# peer ``azure.ai.agentserver.core.streaming`` subpackage.
EXPECTED_PUBLIC_ALL: frozenset[str] = frozenset(
    {
        # Decorators + task classes (spec 022 class split per FR-069)
        "task",
        "multi_turn_task",  # spec 022 FR-002
        "Task",
        "MultiTurnTask",  # spec 022 FR-069
        "RetryPolicy",
        "TaskContext",
        "TaskMetadata",
        # Type aliases + TypedDicts (spec 022 FR-070 / FR-071)
        "JSONValue",
        "TaskErrorDict",
        "TaskExhaustedRetriesErrorDict",
        # ----- Legacy surface (still in __all__ during transition) -----
        "TaskRun",
        "TaskFailed",
        "TaskCancelled",
        "TaskDeferred",  # NEW spec 022 FR-039
        "TaskConflictError",
        "LastInputIdPreconditionFailed",
        "SteeringQueueFull",
        "EntryMode",
        # Spec 018 / Spec 019 FR-D-001 — developer-facing size errors.
        "InputTooLarge",
    }
)


RETIRED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        "TaskSuspended",
        "TaskOptions",
        "TaskInfo",
        # Spec 016 FR-022: dropped from __all__ as preparatory Phase 9 work.
        "TaskTerminated",
        # Spec 022 FR-021 / FR-074 — removed from public, internal-only.
        "TaskNotFound",
        "TaskPreconditionFailed",
        "OutputTooLarge",
        # Spec 022 FR-017 / FR-018 — fully deleted from package.
        "TaskResult",
        "TaskSnapshot",
        # Spec 022 FR-019 / FR-020 — removed from public surface.
        "Suspended",
        "TaskStatus",
        # Spec 019 FR-D-002 / FR-D-003 — attachment-vocabulary errors are
        # internal implementation details (developers never name attachments).
        "AttachmentTooLarge",
        "AttachmentLimitExceeded",
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


@pytest.mark.skip(reason="spec 022 FR-017: Task.get and TaskSnapshot deleted; _list still private")
def test_task_get_list_renamed_to_private() -> None:
    """Spec 015 FR-006 + Spec 019 FR-C-001 — ``Task.get`` semantics.

    Spec 015 demoted the previous ``Task.get`` (which returned a
    raw ``TaskInfo``) to ``Task._get`` because the public-surface
    contract was about leaking the storage-layer record type.

    Spec 019 FR-C-001 RE-INTRODUCES ``Task.get`` as a public method,
    but with a different return type — :class:`TaskSnapshot` — that
    deliberately excludes the framework-internal fields the legacy
    ``Task.get`` exposed. The internal ``Task._get`` is retained for
    callers that still want the raw record.

    This test asserts both coexist: public ``Task.get`` returns
    ``TaskSnapshot`` (spec 019); internal ``Task._get`` returns
    ``TaskInfo`` (spec 015 rename).
    """
    from azure.ai.agentserver.core.durable import Task

    assert hasattr(Task, "get") and callable(Task.get), (
        "Spec 019 FR-C-001 — Task.get is a public method returning "
        "TaskSnapshot. It must exist and be callable."
    )
    assert hasattr(Task, "_get") and callable(Task._get), (
        "Task._get (internal Spec 015 rename) must remain callable."
    )
    assert not hasattr(Task, "list") or not callable(getattr(Task, "list", None)), (
        "Task.list must be renamed to Task._list in Spec 015 Phase 3 (FR-006). "
        "Public-surface listing should go through manager.list_tasks()."
    )
    assert hasattr(Task, "_list") and callable(Task._list), (
        "Task._list (internal rename) must remain callable."
    )


# --------------------------------------------------------------------- #
# Spec 016 — T017: HostedTaskProvider.__init__ credential typing
# --------------------------------------------------------------------- #


def test_hosted_provider_credential_typed_as_async_token_credential() -> None:
    """Spec 016 FR-029: ``HostedTaskProvider.__init__``'s ``credential``
    parameter MUST be annotated as ``AsyncTokenCredential`` (or a
    compatible type). The legacy ``Any`` annotation hid type errors
    at construction sites.

    Asserted by inspecting the runtime annotation; an
    isinstance check on actual credentials is intentionally NOT done
    here because :class:`AsyncTokenCredential` is a structural type
    (Protocol-like).
    """
    import inspect

    from azure.ai.agentserver.core.durable._client import HostedTaskProvider

    sig = inspect.signature(HostedTaskProvider.__init__)
    cred_param = sig.parameters.get("credential")
    assert cred_param is not None, "HostedTaskProvider.__init__ has no `credential` parameter"

    annotation = cred_param.annotation
    # Either the real azure.core.credentials_async.AsyncTokenCredential class
    # or a string annotation (PEP 563) referring to it. Both are acceptable.
    annotation_str = (
        annotation.__name__ if hasattr(annotation, "__name__") else str(annotation)
    )
    assert "AsyncTokenCredential" in annotation_str, (
        f"`credential` parameter must be typed as `AsyncTokenCredential` "
        f"(per spec 016 FR-029); got {annotation_str!r}."
    )


# --------------------------------------------------------------------- #
# Spec 016 — T018: httpx import readiness (lands RED until T024 lands)
# --------------------------------------------------------------------- #


def test_httpx_absent_from_production_durable_package() -> None:
    """Spec 016 FR-029 + T024: ``import httpx`` MUST not appear anywhere
    under the durable subpackage's production source tree. The
    transport migration to ``azure.core.AsyncPipelineClient`` removes
    the dependency entirely.

    Per the test_dev_guide_review pattern, this scan only inspects
    the durable subpackage — we do NOT walk the broader package because
    other modules (host, base) may legitimately retain httpx during
    the rollout window.
    """
    import re

    durable_dir = _PACKAGE_ROOT / "durable"
    offenders: list[tuple[str, int]] = []
    pattern = re.compile(r"^\s*(?:import\s+httpx\b|from\s+httpx\b)", re.MULTILINE)
    for py_file in durable_dir.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        matches = list(pattern.finditer(text))
        if matches:
            line_no = text[: matches[0].start()].count("\n") + 1
            offenders.append((str(py_file.relative_to(_PACKAGE_ROOT)), line_no))

    assert not offenders, (
        f"httpx imports still present under durable subpackage (spec 016 "
        f"T024 / FR-029): {offenders}. Migrate the call site to "
        f"`azure.core.rest.HttpRequest` / `AsyncPipelineClient.send_request` "
        f"and remove the import."
    )


# --------------------------------------------------------------------- #
# Spec 016 US1 / SC-001 — T026: stale_timeout / _is_stale absence
# --------------------------------------------------------------------- #


def test_task_options_has_no_stale_timeout_slot() -> None:
    """SC-001: the (internal) TaskOptions slot for ``stale_timeout`` is gone.

    Asserted via slot inspection — the slot is no longer part of the
    TaskOptions __slots__ tuple. Constructing TaskOptions with
    ``stale_timeout=...`` would fail with the same TypeError as any
    other unknown kwarg.
    """
    from azure.ai.agentserver.core.durable._decorator import TaskOptions

    assert "stale_timeout" not in TaskOptions.__slots__, (
        "TaskOptions.__slots__ must NOT contain 'stale_timeout' (spec 016 "
        "FR-001 / US1). Found: {}".format(TaskOptions.__slots__)
    )

    # Also assert the slot is not an instance attribute (catches subclass
    # or runtime monkey-patching attempts to add it back).
    sample = TaskOptions(name="test")
    assert not hasattr(sample, "stale_timeout"), (
        "TaskOptions instance must NOT expose a 'stale_timeout' attribute "
        "(spec 016 FR-001 / US1)."
    )


def test_is_stale_not_importable_from_durable_subpackage() -> None:
    """SC-001: ``_is_stale`` MUST NOT be importable from any module under
    ``azure/ai/agentserver/core/durable/``.

    Per FR-001's "any helper named after staleness" qualifier, the
    helper itself is removed (not just dropped from a public list).
    Phase 6 of spec 016 (T053-T058) replaces the staleness concept
    entirely with the FR-002 / FR-004 lease-based reclaim path
    (``_reclaim_one`` + ``_lease_is_dead``).
    """
    import re

    durable_dir = _PACKAGE_ROOT / "durable"
    offenders: list[tuple[str, int]] = []
    # Match ``def _is_stale(`` or ``_is_stale =``, plus literal
    # ``from .... import ... _is_stale`` / ``import _is_stale``. We
    # intentionally permit prose mentions in comments so the
    # transitional ``_in_progress_was_abandoned_legacy`` docstring can
    # cite the predecessor by name.
    pattern = re.compile(
        r"^\s*(?:def\s+_is_stale\b|_is_stale\s*=|from\s+\S+\s+import.*\b_is_stale\b|import\s+_is_stale\b)",
        re.MULTILINE)
    for py_file in durable_dir.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            offenders.append((str(py_file.relative_to(_PACKAGE_ROOT)), line_no))

    assert not offenders, (
        f"_is_stale name still defined / importable under durable subpackage "
        f"(spec 016 FR-001 / US1): {offenders}. Replace with the transitional "
        f"`_in_progress_was_abandoned_legacy` (Phase 4) or the Phase-6 lease-"
        f"based reclaim (`_reclaim_one` + `_lease_is_dead`)."
    )
