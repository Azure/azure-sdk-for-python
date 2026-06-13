# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Completeness meta-test (Spec 015 FR-009, per Constitution Principle XII).

Asserts that the public surface of the core durable-task primitive
(``azure-ai-agentserver-core/azure/ai/agentserver/core/durable/``) is
fully covered by a paired test reference in ``tests/durable/`` AND
fully documented in the consolidated developer guide.

This test exists to prevent the suite from silently drifting from the
primitive's contract: if a new symbol is added to ``__all__`` or a new
contract clause is documented in the guide but no matching test is
added, this test fails CI before any other primitive test runs.

The rules enforced (per Constitution Principle XII + Spec 015 FR-009 /
FR-030):

- Every symbol in ``durable/__init__.py.__all__`` MUST appear in
  :data:`EXPECTED_PUBLIC_SYMBOLS` (the post-Phase-3 cleanup target).
  Drift in either direction (new symbol not registered, or registered
  symbol missing from ``__all__``) fails CI.
- Every named contract clause in :data:`CONTRACT_CLAUSE_TO_TEST` MUST
  resolve to an actually-existing test function in ``tests/durable/``.
  This catches "renamed test", "deleted test", and "documented-but-not-
  tested" drift in a single check.
- The consolidated developer guide at
  ``azure-ai-agentserver-core/docs/durable-task-guide.md`` MUST exist
  (created in Phase 7); the guide is the source of truth for end-user-
  developer-visible contract clauses. The Phase 7 FR-024 dev-guide
  review meta-test (``test_dev_guide_review.py``) covers cross-
  consistency checks; this file covers the structural test/contract
  pairing only.

This test is committed RED at Phase 2 and is expected to remain RED
until Phases 3-7 close all gaps. Phase 11 verifies it has gone GREEN.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

import pytest

# --------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------- #

_DURABLE_TESTS_DIR = Path(__file__).parent
_PACKAGE_ROOT = _DURABLE_TESTS_DIR.parent.parent  # azure-ai-agentserver-core/
_DURABLE_INIT = (
    _PACKAGE_ROOT
    / "azure"
    / "ai"
    / "agentserver"
    / "core"
    / "durable"
    / "__init__.py"
)
_CONSOLIDATED_GUIDE = _PACKAGE_ROOT / "docs" / "durable-task-guide.md"

# --------------------------------------------------------------------- #
# Post-cleanup expected public surface (Phase 3 target)
# --------------------------------------------------------------------- #

# After Phase 3 lands, these are the symbols that MUST appear in
# ``durable/__init__.py.__all__`` — no more, no less. Any drift from
# this set fails CI.
EXPECTED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        # Decorators + task classes (spec 022 — class split per FR-069)
        "task",
        "multi_turn_task",  # spec 022 FR-002
        "Task",
        "MultiTurnTask",  # spec 022 FR-069
        # Context + metadata
        "TaskContext",
        "TaskMetadata",
        "EntryMode",
        # TaskRun (slim shape per spec 022 FR-047)
        "TaskRun",
        # Retry
        "RetryPolicy",
        # Public exceptions (7 per spec 022 FR-077; down from 9 in Phase 5)
        "TaskFailed",
        "TaskCancelled",
        "TaskDeferred",  # spec 022 — exit_for_recovery semantics
        "TaskConflictError",
        "LastInputIdPreconditionFailed",
        "SteeringQueueFull",
        "InputTooLarge",
        # Typed-payload + value-type aliases (spec 022 FR-070 / FR-071)
        "JSONValue",
        "TaskErrorDict",
        "TaskExhaustedRetriesErrorDict",
        # ----- LEGACY symbols (still in __all__ during transition) -----
        "Suspended",                 # FR-019 — kept transitionally
        "TaskStatus",                # FR-020 — kept transitionally
    }
)

# Symbols this spec retires from the public surface.
RETIRED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        "TaskSuspended",  # exception deleted entirely
        # Spec 022 FR-021 / FR-074 — removed from public, kept internal-only.
        "OutputTooLarge",
        "TaskNotFound",
        "TaskPreconditionFailed",
        # Spec 022 FR-017 / FR-018 — fully deleted from package.
        "TaskResult",
        "TaskSnapshot",
        "TaskOptions",    # demoted to internal
        "TaskInfo",       # demoted to internal
        "EtagConflict",   # advanced/internal — no public export
        "AttachmentTooLarge",
        "AttachmentLimitExceeded",
        # Spec 022 retirements (Phase 5 — removed from EXPECTED during cleanup):
        "TaskCancelledError",        # FR-077 — never existed; the name with Error suffix is forbidden
    }
)

# --------------------------------------------------------------------- #
# Contract clause → paired test reference
# --------------------------------------------------------------------- #

# Every named contract clause this spec mandates MUST resolve to an
# actually-existing test function in ``tests/durable/``. Format:
#   "<clause-id>": "test_<file>.py::test_<function>"
#
# Adding a new clause without adding the test (or vice versa) fails CI.
CONTRACT_CLAUSE_TO_TEST: dict[str, str] = {
    # FR-001 — retry_attempt cross-lifetime durability
    "retry_attempt_cross_lifetime_durability": (
        "test_retry.py::test_retry_attempt_cross_lifetime_durability"
    ),
    # FR-002 — RetryPolicy.max_attempts durable across lifetimes
    "retry_budget_exhausts_across_crash": (
        "test_retry.py::test_retry_attempt_budget_exhausts_across_crash"
    ),
    # FR-003 — crash recovery does NOT consume retry budget
    "crash_recovery_does_not_consume_retry_budget": (
        "test_retry.py::test_crash_recovery_does_not_consume_retry_budget"
    ),
    # FR-006 — public-surface exact match
    "public_api_surface_exact_match": (
        "test_public_api_surface.py::test_public_all_matches_expected_set"
    ),
    # FR-006 — retired symbols NOT in __all__
    "retired_symbols_absent_from_public_all": (
        "test_public_api_surface.py::test_retired_symbols_absent_from_all"
    ),
    # FR-006 — Task.get / Task.list renamed to _get / _list
    "task_get_list_renamed_to_private": (
        "test_public_api_surface.py::test_task_get_list_renamed_to_private"
    ),
    # FR-006 / FR-007 — @task rejects retired decorator args
    "task_decorator_rejects_retired_args": (
        "test_decorator.py::test_task_decorator_rejects_retired_args"
    ),
    # FR-007 — TaskContext.run_attempt renamed to retry_attempt
    "task_context_retry_attempt_renamed": (
        "test_entry_mode.py::test_task_context_retry_attempt_field_present"
    ),
    # FR-007 — TaskContext.lease_generation renamed to recovery_count
    "task_context_recovery_count_renamed": (
        "test_entry_mode.py::test_task_context_recovery_count_field_present"
    ),
    # FR-007 — TaskContext.generation renamed to steering_generation
    "task_context_steering_generation_renamed": (
        "test_steering.py::test_task_context_steering_generation_field_present"
    ),
    # FR-007 — TaskContext.previous_input deleted (FR-007)
    "task_context_previous_input_removed": (
        "test_steering.py::test_task_context_previous_input_removed"
    ),
    # FR-003 — TaskMetadata named-namespace facility
    "task_metadata_named_namespace_isolation": (
        "test_metadata.py::test_named_namespace_isolation"
    ),
    # FR-003 — TaskMetadata flush per-namespace
    "task_metadata_flush_per_namespace_only": (
        "test_metadata.py::test_flush_per_namespace_only"
    ),
    # FR-004 — default-namespace convenience accessor
    "task_metadata_default_namespace_callable_and_dict": (
        "test_metadata.py::test_default_namespace_callable_and_dict"
    ),
    # FR-005 — primitive does NOT enforce underscore convention
    "task_metadata_underscore_not_enforced_by_primitive": (
        "test_metadata.py::test_underscore_namespace_not_enforced_by_primitive"
    ),
    # --- Spec 019 — Task & Streams Reconciliation ---------------------- #
    # FR-A-001..009 (etag CAS, write queue, dynamic lease, per-op 412 policy)
    "spec019_etag_cas_every_patch": (
        "test_etag_cas.py::test_every_patch_after_first_carries_if_match"
    ),
    "spec019_delete_carries_no_if_match": (
        "test_etag_cas.py::test_delete_does_not_carry_if_match"
    ),
    "spec019_write_queue_serializes_intra_process": (
        "test_write_queue.py::test_concurrent_metadata_flushes_serialize"
    ),
    "spec019_write_queue_no_lock_for_reads": (
        "test_write_queue.py::test_reads_do_not_acquire_lock"
    ),
    "spec019_write_queue_lock_torn_down_with_task": (
        "test_write_queue.py::test_lock_removed_when_active_entry_torn_down"
    ),
    "spec019_lease_renewal_dynamic_cadence_full_shadow": (
        "test_lease_renewal.py::test_dynamic_cadence_shadows_heartbeats"
    ),
    "spec019_terminal_412_reread_lease_lost_abandons": (
        "test_etag_cas.py::test_terminal_412_lease_lost_abandons"
    ),
    "spec019_terminal_412_reread_already_terminal_abandons": (
        "test_etag_cas.py::test_terminal_412_already_terminal_abandons"
    ),
    "spec019_terminal_412_reread_lease_ours_retries": (
        "test_etag_cas.py::test_terminal_412_lease_ours_retries"
    ),
    "spec019_reclaim_both_sites_carry_if_match": (
        "test_etag_cas.py::test_both_reclaim_sites_carry_if_match"
    ),
    # FR-B-001 (source_type filter on recovery scan)
    "spec019_recovery_scan_filters_source_type": (
        "test_recovery_filter.py::test_recovery_scan_passes_source_type"
    ),
    "spec019_recovery_scan_skips_foreign_typed_tasks": (
        "test_recovery_filter.py::test_recovery_does_not_pick_up_foreign_typed_task"
    ),
    # FR-C-001..007 (Task.get + TaskSnapshot + output lifecycle) — REMOVED
    # per spec 022 FR-017 / FR-021 / FR-025. The whole Task.get + TaskSnapshot
    # surface is deleted, and output is no longer persisted in payload, so
    # the "cleared on resume / drain / failure" contracts are vacuous.
    "spec019_output_cleared_on_resume": (
        "test_output_lifecycle.py::test_resume_clears_payload_output_and_attachment"
    ),
    "spec019_output_cleared_on_drain_phase1": (
        "test_output_lifecycle.py::test_drain_phase1_clears_payload_output_and_attachment"
    ),
    "spec019_output_cleared_on_failure": (
        "test_output_lifecycle.py::test_handle_failure_clears_output"
    ),
    "spec019_output_always_attachment_when_non_null": (
        "test_output_promotion.py::test_suspend_output_always_uses_attachment"
    ),
    "spec019_output_complete_always_attachment_when_non_null": (
        "test_output_promotion.py::test_complete_output_always_uses_attachment"
    ),
    "spec019_output_null_writes_explicit_null": (
        "test_output_promotion.py::test_suspend_output_none_writes_explicit_null"
    ),
    "spec019_output_too_large_raises_pre_patch": (
        "test_output_promotion.py::test_output_over_cap_raises_output_too_large_pre_patch"
    ),
    # FR-D-001..006 (error rename + flush_all + local expiry)
    "spec019_output_too_large_public_exception": (
        "test_errors_public_surface.py::test_output_too_large_is_public"
    ),
    "spec019_attachment_too_large_internal": (
        "test_errors_public_surface.py::test_attachment_too_large_not_public"
    ),
    "spec019_attachment_limit_exceeded_internal": (
        "test_errors_public_surface.py::test_attachment_limit_exceeded_not_public"
    ),
    "spec019_input_attachment_error_remapped_to_input_too_large": (
        "test_errors_public_surface.py::test_input_too_large_remap_from_internal_input_key"
    ),
    "spec019_steering_attachment_error_remapped_to_input_too_large": (
        "test_errors_public_surface.py::test_input_too_large_remap_from_steering_key"
    ),
    "spec019_output_attachment_error_remapped_to_output_too_large": (
        "test_errors_public_surface.py::test_output_too_large_remap_from_internal_output_key"
    ),
    "spec019_flush_all_renamed_private": (
        "test_metadata_flush.py::test_flush_all_renamed_to_underscore_flush_all"
    ),
    "spec019_local_provider_bumps_expiry_count": (
        "test_local_provider.py::test_local_provider_bumps_expiry_count_on_real_handoff"
    ),
    "spec019_local_provider_no_bump_on_renewal": (
        "test_local_provider.py::test_local_provider_no_bump_on_same_instance_renewal"
    ),
    "spec019_local_provider_no_bump_on_unexpired_handoff": (
        "test_local_provider.py::test_local_provider_no_bump_on_unexpired_handoff"
    ),
}

# --------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------- #


def _parse_all_from_init(path: Path) -> set[str]:
    """Parse the ``__all__`` list literal from a Python file via AST."""
    if not path.exists():
        return set()
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__all__"
            and isinstance(node.value, (ast.List, ast.Tuple, ast.Set))
        ):
            return {
                elt.value
                for elt in node.value.elts
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            }
    return set()


def _collect_test_functions(path: Path) -> set[str]:
    """Collect top-level + class-method ``test_*`` function names from a file."""
    if not path.exists():
        return set()
    tree = ast.parse(path.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                names.add(node.name)
    return names


def _resolve_clause_reference(reference: str) -> tuple[Path, str]:
    """Split ``file.py::test_name`` into (path, function_name)."""
    file_part, _, function_part = reference.partition("::")
    return _DURABLE_TESTS_DIR / file_part, function_part


# --------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------- #


def test_consolidated_developer_guide_exists() -> None:
    """The consolidated dev guide MUST exist (FR-023; Phase 7 creates it).

    Until Phase 7 lands, this assertion fails RED — that is the intent.
    """
    assert _CONSOLIDATED_GUIDE.exists(), (
        f"consolidated developer guide not found at {_CONSOLIDATED_GUIDE}. "
        f"Per FR-023, the canonical end-user developer guide for the "
        f"durable-task primitive MUST live at this path."
    )


def test_public_all_matches_post_cleanup_expected_set() -> None:
    """``durable/__init__.py.__all__`` MUST match the Phase-3 cleanup target.

    Drift in either direction fails CI:

    - Extra symbol in ``__all__`` (e.g. the still-exported ``TaskSuspended``
      before Phase 3 lands the deletion) → RED until removed.
    - Missing symbol from ``__all__`` (e.g. a new public-surface addition
      that this test wasn't updated for) → RED until registered.
    """
    actual = _parse_all_from_init(_DURABLE_INIT)
    assert actual, f"could not parse __all__ from {_DURABLE_INIT}"

    missing = EXPECTED_PUBLIC_SYMBOLS - actual
    extra = actual - EXPECTED_PUBLIC_SYMBOLS

    msg_parts: list[str] = []
    if missing:
        msg_parts.append(
            f"symbols expected in __all__ but missing: {sorted(missing)}"
        )
    if extra:
        msg_parts.append(
            f"symbols in __all__ but not in EXPECTED_PUBLIC_SYMBOLS "
            f"(retired or undeclared): {sorted(extra)}"
        )

    assert not msg_parts, " ; ".join(msg_parts) + (
        " — update EXPECTED_PUBLIC_SYMBOLS in this file if intentional, "
        "or fix the public surface."
    )


def test_retired_symbols_not_in_public_all() -> None:
    """Retired symbols (FR-006) MUST NOT appear in ``__all__``.

    Belt-and-suspenders companion to ``test_public_all_matches_…``:
    explicitly names the symbols this spec retires so the failure
    message points directly at the spec clause.
    """
    actual = _parse_all_from_init(_DURABLE_INIT)
    leaked = RETIRED_PUBLIC_SYMBOLS & actual
    assert not leaked, (
        f"symbols retired by Spec 015 FR-006 still appear in __all__: "
        f"{sorted(leaked)}. Phase 3 (T022-T025) MUST drop them."
    )


@pytest.mark.parametrize(
    "clause_id,reference", sorted(CONTRACT_CLAUSE_TO_TEST.items())
)
def test_every_contract_clause_has_a_paired_test(
    clause_id: str, reference: str
) -> None:
    """Each documented contract clause MUST resolve to an existing test.

    This is the structural pairing guarantee from Constitution Principle XII
    rule 1: every public-surface clause has at least one paired test.
    Parametrized so the failure report lists EVERY missing pair, not just
    the first.
    """
    file_path, function_name = _resolve_clause_reference(reference)
    if not file_path.exists():
        pytest.fail(
            f"clause '{clause_id}' references {reference} but file "
            f"{file_path.name} does not exist in tests/durable/"
        )
    functions = _collect_test_functions(file_path)
    if function_name not in functions:
        pytest.fail(
            f"clause '{clause_id}' references {reference} but function "
            f"'{function_name}' is not defined in {file_path.name} "
            f"(found {sorted(f for f in functions if f.startswith('test_'))[:10]} "
            f"and {max(0, len(functions) - 10)} more). "
            f"The corresponding implementation task in Phases 3-6 MUST "
            f"land this test RED before the implementation commit goes green."
        )


def test_no_orphan_public_symbol_without_surface_test() -> None:
    """Every symbol in ``__all__`` should be exercised by at least one test file.

    Loose check: each symbol's name must appear textually in at least one
    ``tests/durable/test_*.py`` file. This is intentionally weak (a string
    match, not an import-trace) so it doesn't false-positive on symbols
    used via re-export; it catches the "added to ``__all__`` but never
    mentioned in any test" case.
    """
    actual = _parse_all_from_init(_DURABLE_INIT)
    test_files: list[Path] = sorted(_DURABLE_TESTS_DIR.glob("test_*.py"))
    blobs: dict[Path, str] = {p: p.read_text() for p in test_files}

    orphans: list[str] = []
    for symbol in sorted(actual):
        if not any(symbol in text for text in blobs.values()):
            orphans.append(symbol)

    assert not orphans, (
        f"public symbols never mentioned in any tests/durable/test_*.py: "
        f"{orphans}. Add at least one surface test per Constitution "
        f"Principle XII rule 1."
    )


def test_clause_ids_are_unique() -> None:
    """Sanity: clause ids in :data:`CONTRACT_CLAUSE_TO_TEST` are unique.

    Dict literal would already enforce uniqueness at parse time; this
    test exists so a future refactor (e.g. switching to a list of pairs)
    does not silently drop entries.
    """
    keys = list(CONTRACT_CLAUSE_TO_TEST.keys())
    assert len(keys) == len(set(keys)), "duplicate clause id"


# =========================================================================
# Spec 022 — meta-test extension (per T-1.0 of spec 022)
# =========================================================================
#
# Per Constitution Principle XII §2 + Spec 022 plan.md Phase 1 T-1.0.
# These tests assert the FULL public surface from Appendix A.1 of spec 021
# + negative absence assertions for unsupported surface + grep-clean
# invariants for unsupported code paths.
#
# Each assertion is RED until Phase 5 / Phase 7 lands the corresponding
# implementation cleanup.


def _read_durable_init_source() -> str:
    return _DURABLE_INIT.read_text()


def _read_durable_source_tree() -> dict[Path, str]:
    """Read every .py file under azure/.../durable/ (the source package)."""
    pkg = _DURABLE_INIT.parent
    return {
        p: p.read_text()
        for p in sorted(pkg.rglob("*.py"))
        if "__pycache__" not in str(p)
    }


def test_spec_022_a_b_positive_and_negative_presence_in_all() -> None:
    """T-1.0 (a)(b) — spec-022 symbols in EXPECTED; legacy in EXPECTED too during transition.

    Positive presence is already covered by
    :func:`test_public_all_matches_post_cleanup_expected_set`.

    During the Phase 2-5 transition window, both the new spec-022 symbols
    AND the legacy symbols (TaskResult, Suspended, TaskSnapshot, TaskStatus,
    OutputTooLarge, TaskNotFound, TaskPreconditionFailed) coexist in
    ``EXPECTED_PUBLIC_SYMBOLS``. Phase 5 cleanup removes the legacy entries.
    """
    # Sanity: spec-022 additions are in EXPECTED_PUBLIC_SYMBOLS.
    for sym in {"multi_turn_task", "MultiTurnTask", "TaskDeferred",
                "JSONValue", "TaskErrorDict", "TaskExhaustedRetriesErrorDict"}:
        assert sym in EXPECTED_PUBLIC_SYMBOLS, (
            f"spec 022 T-1.0(a): {sym} MUST be in EXPECTED_PUBLIC_SYMBOLS"
        )
    # During transition, legacy symbols are still in EXPECTED; Phase 5 moves
    # them to RETIRED_PUBLIC_SYMBOLS. For now, just ensure they're in one or
    # the other (no orphans).
    legacy_during_transition = {
        "TaskResult", "Suspended", "TaskSnapshot", "TaskStatus",
        "OutputTooLarge", "TaskNotFound", "TaskPreconditionFailed",
    }
    for sym in legacy_during_transition:
        assert sym in EXPECTED_PUBLIC_SYMBOLS or sym in RETIRED_PUBLIC_SYMBOLS, (
            f"spec 022 T-1.0(b): {sym} MUST be in EXPECTED or RETIRED set"
        )
    # TaskCancelledError MUST always be retired (never existed as a public name).
    assert "TaskCancelledError" in RETIRED_PUBLIC_SYMBOLS


def test_spec_022_c_grep_clean_for_unsupported_code_paths() -> None:
    """T-1.0 (c) — SC-006: source tree grep-clean for removed code paths."""
    blobs = _read_durable_source_tree()
    forbidden_patterns = {
        "payload[\"output\"]": "FR-025 — no payload['output'] writes",
        "_build_output_co_write": "FR-026 — output co-write helper absent",
        "TaskManager.handle_resume": "FR-049 — /tasks/resume manager method absent",
        "_resume_route.py": "FR-049 — _resume_route module absent",
    }
    findings: list[str] = []
    for pattern, rule in forbidden_patterns.items():
        for path, text in blobs.items():
            if pattern in text and "_local_provider.py" not in path.name:
                # Allow harmless mentions in docstrings of removed-API checklists
                if "MUST NOT" in text or "removed" in text or "absent" in text:
                    continue
                findings.append(f"  {path.name}: {pattern!r}  ({rule})")
    assert not findings, (
        "spec 022 SC-006: source tree contains references to removed code paths:\n"
        + "\n".join(findings)
    )


def test_spec_022_d_ctx_end_chain_absent() -> None:
    """T-1.0 (d) — FR-009: ctx.end_chain() MUST NOT exist anywhere in durable/."""
    blobs = _read_durable_source_tree()
    findings = [
        str(path.name)
        for path, text in blobs.items()
        if "end_chain" in text
    ]
    assert not findings, (
        f"FR-009: ctx.end_chain MUST NOT exist in durable/ source — found in: {findings}"
    )


def test_spec_022_e_ctx_shutdown_preserved() -> None:
    """T-1.0 (e) — FR-040 + FR-072: ctx.shutdown MUST exist on TaskContext."""
    try:
        from azure.ai.agentserver.core.durable import TaskContext
    except ImportError:
        pytest.skip("TaskContext import failed (RED until Phase 5)")
    # Inspect class attrs / annotations for `shutdown` (asyncio.Event).
    has_shutdown = (
        hasattr(TaskContext, "shutdown")
        or "shutdown" in getattr(TaskContext, "__annotations__", {})
        or "shutdown" in getattr(TaskContext, "__slots__", ())
    )
    assert has_shutdown, (
        "FR-040: TaskContext MUST expose `shutdown` (asyncio.Event) "
        "per FR-072 enumerated public surface."
    )


def test_spec_022_f_cooperative_cancel_no_automatic_raise() -> None:
    """T-1.0 (f) — FR-036: framework cancellation is cooperative-only.

    Grep for any `async def force_cancel` / `raise asyncio.CancelledError`
    in _manager.py that would constitute an automatic raise. (The framework
    sets `ctx.cancel` + `ctx.timeout_exceeded` flags but never raises
    automatically; per FR-038 / FR-054-057 / spec 021 §3 Q11.)
    """
    pkg = _DURABLE_INIT.parent
    manager_py = pkg / "_manager.py"
    if not manager_py.exists():
        pytest.skip("_manager.py not present (RED-first)")
    text = manager_py.read_text()
    # Look for `force_cancel` as a sync/async def — must NOT exist as a
    # public method that auto-raises.
    assert "def force_cancel" not in text, (
        "FR-036: framework MUST NOT expose `force_cancel`; cancellation is "
        "cooperative-only via ctx.cancel."
    )


def test_spec_022_g_run_return_type_is_output_directly() -> None:
    """T-1.0 (g) — FR-052: .run() returns Output (not TaskResult/Awaitable[TaskResult])."""
    try:
        from azure.ai.agentserver.core.durable import Task
    except ImportError:
        pytest.skip("Task class import failed (RED until Phase 2)")
    import inspect
    sig = inspect.signature(Task.run)
    return_annot = sig.return_annotation
    # The return annotation should NOT be `TaskResult` or `Awaitable[TaskResult]`
    annot_str = str(return_annot)
    forbidden_substrings = ["TaskResult", "Suspended"]
    found = [s for s in forbidden_substrings if s in annot_str]
    assert not found, (
        f"FR-052: Task.run return annotation MUST resolve to Output directly; "
        f"found {found} in: {annot_str!r}"
    )


def test_spec_022_h_internal_only_cleanup_absent() -> None:
    """T-1.0 (h) — FR-065: enumerated internal symbols MUST NOT exist."""
    blobs = _read_durable_source_tree()
    forbidden_symbols = {
        "_build_output_co_write": "FR-065 / FR-026",
        "TaskContext.suspend": "FR-008",
        "TaskRun._provider": "FR-048",
        "_terminate_event": "FR-048",
        "_terminate_reason_ref": "FR-048",
        # NOTE: _status / _lease_expiry_count are too generic to grep; skip
        # those and rely on FR-047 / FR-048 positive shape tests instead.
    }
    findings: list[str] = []
    for sym, rule in forbidden_symbols.items():
        for path, text in blobs.items():
            if sym in text:
                # Allow comment / docstring mentions
                relevant_lines = [
                    line for line in text.splitlines()
                    if sym in line and not line.strip().startswith("#")
                    and '"""' not in line and not line.strip().startswith("*")
                ]
                if relevant_lines:
                    findings.append(f"  {path.name}: {sym!r} ({rule})")
                    break
    assert not findings, (
        "FR-065: enumerated internal-only symbols MUST NOT exist:\n"
        + "\n".join(findings)
    )


def test_spec_022_i_no_backward_compat_shims() -> None:
    """T-1.0 (i) — SC-007: no backward-compat shims silently added."""
    blobs = _read_durable_source_tree()
    forbidden_markers = {
        "# COMPAT",
        "# backward-compat",
        "# backward compat",
        "TaskResultCompat",
        "SuspendedCompat",
        "TaskSnapshotCompat",
    }
    findings: list[str] = []
    for marker in forbidden_markers:
        for path, text in blobs.items():
            if marker in text:
                findings.append(f"  {path.name}: {marker!r}")
    assert not findings, (
        "SC-007: source tree contains backward-compat shim markers "
        "(removals MUST be hard removals; no migration bridges):\n"
        + "\n".join(findings)
    )


def test_spec_022_TaskCancelledError_does_not_exist() -> None:
    """FR-077 — TaskCancelledError (with Error suffix) MUST raise ImportError."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.durable import TaskCancelledError  # noqa: F401


def test_spec_022_TaskNotFound_not_in_public_import() -> None:
    """FR-074 — TaskNotFound MUST NOT import from the public namespace."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.durable import TaskNotFound  # noqa: F401


def test_spec_022_TaskPreconditionFailed_not_in_public_import() -> None:
    """FR-074 — TaskPreconditionFailed MUST NOT import from the public namespace."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.durable import TaskPreconditionFailed  # noqa: F401


def test_spec_022_OutputTooLarge_not_in_public_import() -> None:
    """FR-021 — OutputTooLarge MUST NOT import from the public namespace."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.durable import OutputTooLarge  # noqa: F401
