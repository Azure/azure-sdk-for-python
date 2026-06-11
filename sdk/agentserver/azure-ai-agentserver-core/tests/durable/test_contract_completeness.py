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
        # Decorator + task handle
        "task",
        "Task",
        # Context + metadata
        "TaskContext",
        "TaskMetadata",
        "EntryMode",
        # Results + runs + statuses
        "TaskResult",
        "TaskRun",
        "TaskStatus",
        "Suspended",
        # Spec 019 FR-C-002: read-only snapshot of any non-deleted task,
        # returned by Task.get(task_id).
        "TaskSnapshot",
        # Retry
        "RetryPolicy",
        # Spec 017 FR-014/FR-015: Streaming moved to peer
        # `azure.ai.agentserver.core.streaming` subpackage. The old
        # StreamHandler/QueueStreamHandler/StreamHandlerFactory surface
        # is REMOVED from durable __all__.
        # Exceptions
        "TaskFailed",
        "TaskCancelled",
        "TaskNotFound",
        "TaskConflictError",
        # Spec 016 FR-022 (US6): TaskTerminated removed from __all__.
        "LastInputIdPreconditionFailed",
        "SteeringQueueFull",
        "TaskPreconditionFailed",
        # Spec 018 — input size violation (developer-facing).
        "InputTooLarge",
        # Spec 019 FR-D-001: developer-facing output size violation
        # (parallels InputTooLarge for the output channel).
        "OutputTooLarge",
    }
)

# Symbols this spec retires from the public surface (FR-006 + FR-007).
# These MUST NOT appear in ``__all__`` after Phase 3 lands.
RETIRED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        "TaskSuspended",  # exception deleted entirely (FR-006)
        "TaskOptions",    # demoted to internal (FR-006)
        "TaskInfo",       # demoted to internal (FR-006)
        # Spec 015 Phase 11 closeout (user feedback 2026-05-30):
        # EtagConflict is an advanced/internal exception (custom storage
        # adapters only). Application code does not handle it — the
        # framework retries internally on optimistic-concurrency conflicts.
        # Importable, but no longer advertised via ``__all__``.
        "EtagConflict",
        # Spec 019 FR-D-002 + FR-D-003: attachment-vocabulary errors are
        # internal implementation details (attachments are a framework
        # concept developers never name). Renamed to leading-underscore
        # equivalents and absent from public __all__. Framework re-raises
        # InputTooLarge / OutputTooLarge based on attachment-key prefix.
        "AttachmentTooLarge",
        "AttachmentLimitExceeded",
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
    # FR-C-001..007 (Task.get + TaskSnapshot + output lifecycle)
    "spec019_task_get_returns_snapshot": (
        "test_task_get_api.py::test_task_get_returns_snapshot_for_each_status"
    ),
    "spec019_task_get_returns_none_for_missing": (
        "test_task_get_api.py::test_task_get_returns_none_for_missing"
    ),
    "spec019_task_get_raises_without_manager": (
        "test_task_get_api.py::test_task_get_raises_runtime_error_without_manager"
    ),
    "spec019_task_snapshot_field_exclusions": (
        "test_task_get_api.py::test_task_snapshot_exposes_only_documented_fields"
    ),
    "spec019_task_snapshot_resolves_output_ref": (
        "test_task_get_api.py::test_task_snapshot_resolves_output_ref"
    ),
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
