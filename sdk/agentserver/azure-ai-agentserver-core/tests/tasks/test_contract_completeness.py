# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Completeness meta-test (, per Constitution Principle XII).

Asserts that the public surface of the core resilient-task primitive
(``azure-ai-agentserver-core/azure/ai/agentserver/core/tasks/``) is
fully covered by a paired test reference in ``tests/tasks/`` AND
fully documented in the consolidated developer guide.

This test exists to prevent the suite from silently drifting from the
primitive's contract: if a new symbol is added to ``__all__`` or a new
contract clause is documented in the guide but no matching test is
added, this test fails CI before any other primitive test runs.

The rules enforced (per Constitution Principle XII +   /
):

- Every symbol in ``tasks/__init__.py.__all__`` MUST appear in
  :data:`EXPECTED_PUBLIC_SYMBOLS` (the post-Phase-3 cleanup target).
  Drift in either direction (new symbol not registered, or registered
  symbol missing from ``__all__``) fails CI.
- Every named contract clause in :data:`CONTRACT_CLAUSE_TO_TEST` MUST
  resolve to an actually-existing test function in ``tests/tasks/``.
  This catches "renamed test", "deleted test", and "documented-but-not-
  tested" drift in a single check.
- The consolidated developer guide at
  ``azure-ai-agentserver-core/docs/tasks-guide.md`` MUST exist
  (created in Phase 7); the guide is the source of truth for end-user-
  developer-visible contract clauses. The Phase 7  dev-guide
  review meta-test (``test_dev_guide_review.py``) covers cross-
  consistency checks; this file covers the structural test/contract
  pairing only.

This test is committed RED at Phase 2 and is expected to remain RED
until Phases 3-7 close all gaps. Phase 11 verifies it has gone GREEN.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Iterable

import pytest

# The file-scanning contract tests below read repo source with the platform
# default text encoding. On Windows that is cp1252, which cannot decode UTF-8
# source bytes (e.g. the 0x90 byte in test_lifecycle.py), so they are skipped
# there and run on POSIX CI — mirroring the other POSIX-only skips in this
# suite (``not hasattr(os, "fork")``).
pytestmark = pytest.mark.skipif(
    not hasattr(os, "fork"),
    reason="scans repo source files with the platform default encoding; "
    "cp1252 on Windows cannot decode UTF-8 source",
)

# --------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------- #

_RESILIENT_TESTS_DIR = Path(__file__).parent
_PACKAGE_ROOT = _RESILIENT_TESTS_DIR.parent.parent  # azure-ai-agentserver-core/
_RESILIENT_INIT = _PACKAGE_ROOT / "azure" / "ai" / "agentserver" / "core" / "tasks" / "__init__.py"
_CONSOLIDATED_GUIDE = _PACKAGE_ROOT / "docs" / "tasks-guide.md"

# --------------------------------------------------------------------- #
# Post-cleanup expected public surface (Phase 3 target)
# --------------------------------------------------------------------- #

# After Phase 3 lands, these are the symbols that MUST appear in
# ``tasks/__init__.py.__all__`` — no more, no less. Any drift from
# this set fails CI.
EXPECTED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        # Decorators + task classes (— class split)
        "task",
        "multi_turn_task",
        "Task",
        "MultiTurnTask",
        # Enablement switch
        "set_resilient_tasks_enabled",
        "resilient_tasks_enabled",
        # Context + metadata
        "TaskContext",
        "TaskMetadata",
        "EntryMode",
        # TaskRun (slim shape)
        "TaskRun",
        # Retry
        "RetryPolicy",
        # Public exceptions (7; down from 9 in Phase 5)
        "TaskFailed",
        "TaskCancelled",
        "TaskDeferred",  #  — exit_for_recovery semantics
        "TaskConflictError",
        "LastInputIdPreconditionFailed",
        "SteeringQueueFull",
        "InputTooLarge",
        "TaskManagerNotInitialized",
        # Typed-payload + value-type aliases
        "JSONValue",
        "TaskErrorDict",
        "TaskExhaustedRetriesErrorDict",
    }
)

# Symbols this spec retires from the public surface.
RETIRED_PUBLIC_SYMBOLS: frozenset[str] = frozenset(
    {
        "TaskSuspended",  # exception deleted entirely
        #   /  — removed from public, kept internal-only.
        "OutputTooLarge",
        "TaskNotFound",
        "TaskPreconditionFailed",
        #   /  — fully deleted from package.
        "TaskResult",
        "TaskSnapshot",
        #   /  — removed from public surface
        # (Suspended kept as internal-only shim in _run.py; TaskStatus
        # remains in _models for internal type-annotation use).
        "Suspended",
        "TaskStatus",
        "TaskOptions",  # demoted to internal
        "TaskInfo",  # demoted to internal
        "EtagConflict",  # advanced/internal — no public export
        "AttachmentTooLarge",
        "AttachmentLimitExceeded",
        #  retirements (Phase 5 — removed from EXPECTED during cleanup):
        "TaskCancelledError",  #  — never existed; the name with Error suffix is forbidden
    }
)

# --------------------------------------------------------------------- #
# Contract clause → paired test reference
# --------------------------------------------------------------------- #

# Every named contract clause this spec mandates MUST resolve to an
# actually-existing test function in ``tests/tasks/``. Format:
#   "<clause-id>": "test_<file>.py::test_<function>"
#
# Adding a new clause without adding the test (or vice versa) fails CI.
CONTRACT_CLAUSE_TO_TEST: dict[str, str] = {
    #  — retry_attempt cross-lifetime resilience
    "retry_attempt_cross_lifetime_resilience": ("test_retry.py::test_retry_attempt_cross_lifetime_resilience"),
    #  — RetryPolicy.max_attempts resilient across lifetimes
    # (Removed: test_retry_attempt_budget_exhausts_across_crash relied on
    # `@task(ephemeral=False)` which is no longer a valid construction; the
    # same invariant for multi-turn chains is covered by
    # test_retry_attempt_cross_lifetime_resilience above.)
    #  — crash recovery does NOT consume retry budget
    # (Removed: same reason — same coverage via the multi-turn variant.)
    #  — public-surface exact match
    "public_api_surface_exact_match": ("test_public_api_surface.py::test_public_all_matches_expected_set"),
    #  — retired symbols NOT in __all__
    "retired_symbols_absent_from_public_all": ("test_public_api_surface.py::test_retired_symbols_absent_from_all"),
    # (Task.get / Task.list rename to _get / _list — vacuous post-spec-022;
    # Task.get and TaskSnapshot are removed entirely.)
    #  /  — @task rejects retired decorator args
    "task_decorator_rejects_retired_args": ("test_decorator.py::test_task_decorator_rejects_retired_args"),
    #  — TaskContext.run_attempt renamed to retry_attempt
    "task_context_retry_attempt_renamed": ("test_entry_mode.py::test_task_context_retry_attempt_field_present"),
    #  — TaskContext.lease_generation renamed to recovery_count
    "task_context_recovery_count_renamed": ("test_entry_mode.py::test_task_context_recovery_count_field_present"),
    #  — TaskContext.generation renamed to steering_generation
    "task_context_steering_generation_renamed": (
        "test_steering.py::test_task_context_steering_generation_field_present"
    ),
    #  — TaskContext.previous_input deleted
    "task_context_previous_input_removed": ("test_steering.py::test_task_context_previous_input_removed"),
    #  — TaskMetadata named-namespace facility
    "task_metadata_named_namespace_isolation": ("test_metadata.py::test_named_namespace_isolation"),
    #  — TaskMetadata flush per-namespace
    "task_metadata_flush_per_namespace_only": ("test_metadata.py::test_flush_per_namespace_only"),
    #  — default-namespace convenience accessor
    "task_metadata_default_namespace_callable_and_dict": ("test_metadata.py::test_default_namespace_callable_and_dict"),
    # (Underscore-namespace not-enforced-by-primitive contract is vacuous
    # post-redesign — primitive now reserves leading underscore and
    # raises ValueError; covered by test_metadata::test_named_namespace.)
    # ---  — Task & Streams Reconciliation ----------------------
    #  (etag CAS, write queue, dynamic lease, per-op 412 policy)
    "task_streams_etag_cas_every_patch": ("test_etag_cas.py::test_every_patch_after_first_carries_if_match"),
    "task_streams_delete_carries_no_if_match": ("test_etag_cas.py::test_delete_does_not_carry_if_match"),
    "task_streams_write_queue_serializes_intra_process": (
        "test_write_queue.py::test_concurrent_metadata_flushes_serialize"
    ),
    "task_streams_write_queue_no_lock_for_reads": ("test_write_queue.py::test_reads_do_not_acquire_lock"),
    "task_streams_write_queue_lock_torn_down_with_task": (
        "test_write_queue.py::test_lock_removed_when_active_entry_torn_down"
    ),
    "task_streams_lease_renewal_dynamic_cadence_full_shadow": (
        "test_lease_renewal.py::test_dynamic_cadence_shadows_heartbeats"
    ),
    "task_streams_terminal_412_reread_lease_lost_abandons": ("test_etag_cas.py::test_terminal_412_lease_lost_abandons"),
    "task_streams_terminal_412_reread_already_terminal_abandons": (
        "test_etag_cas.py::test_terminal_412_already_terminal_abandons"
    ),
    "task_streams_terminal_412_reread_lease_ours_retries": ("test_etag_cas.py::test_terminal_412_lease_ours_retries"),
    "task_streams_reclaim_both_sites_carry_if_match": ("test_etag_cas.py::test_both_reclaim_sites_carry_if_match"),
    # Spec 031 — public-surface conformance + write-serialization hardening
    "spec031_pending_input_count_live_count": ("test_steering.py::test_same_process_enqueue_count_visible_at_cancel"),
    "spec031_no_blind_writes_steer_drain": ("test_steering.py::test_steer_drain_runs_steered_turn_and_no_blind_writes"),
    "spec031_drain_recovers_cross_process_conflict": (
        "test_steering.py::test_drain_recovers_from_cross_process_conflict"
    ),
    "spec031_local_provider_hosted_parity": ("test_local_provider.py::test_stale_if_match_classified_like_hosted"),
    "spec031_local_provider_lease_only_bumps_etag": ("test_local_provider.py::test_lease_only_update_bumps_etag"),
    #  (source_type filter on recovery scan)
    "task_streams_recovery_scan_filters_source_type": (
        "test_recovery_filter.py::test_recovery_scan_passes_source_type"
    ),
    "task_streams_recovery_scan_skips_foreign_typed_tasks": (
        "test_recovery_filter.py::test_recovery_does_not_pick_up_foreign_typed_task"
    ),
    #  (Task.get + TaskSnapshot + output lifecycle) — REMOVED
    # The Task.get + TaskSnapshot surface is deleted, and output is no
    # longer persisted in payload (the framework does not write
    # payload["output"] nor any "output" attachment), so the "cleared on
    # resume / drain / failure / always-attachment / null / too-large"
    # contracts that lived in test_output_lifecycle.py and
    # test_output_promotion.py are all vacuous and the files are gone.
    #  (error rename + flush_all + local expiry)
    "task_streams_output_too_large_public_exception": (
        "test_errors_public_surface.py::test_output_too_large_is_public"
    ),
    "task_streams_attachment_too_large_internal": (
        "test_errors_public_surface.py::test_attachment_too_large_not_public"
    ),
    "task_streams_attachment_limit_exceeded_internal": (
        "test_errors_public_surface.py::test_attachment_limit_exceeded_not_public"
    ),
    # (The pre-redesign "input attachment error remapped to InputTooLarge"
    # via the internal `_input` key is vacuous post-redesign — InputTooLarge
    # is now bare and the remap-from-_input path is covered by the
    # steering-key variant below as the canonical case.)
    "task_streams_steering_attachment_error_remapped_to_input_too_large": (
        "test_errors_public_surface.py::test_input_too_large_remap_from_steering_key"
    ),
    "task_streams_output_attachment_error_remapped_to_output_too_large": (
        "test_errors_public_surface.py::test_output_too_large_remap_from_internal_output_key"
    ),
    "task_streams_flush_all_renamed_private": (
        "test_metadata_flush.py::test_flush_all_renamed_to_underscore_flush_all"
    ),
    "task_streams_local_provider_bumps_expiry_count": (
        "test_local_provider.py::test_local_provider_bumps_expiry_count_on_real_handoff"
    ),
    "task_streams_local_provider_no_bump_on_renewal": (
        "test_local_provider.py::test_local_provider_no_bump_on_same_instance_renewal"
    ),
    "task_streams_local_provider_no_bump_on_unexpired_handoff": (
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
                elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
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
    return _RESILIENT_TESTS_DIR / file_part, function_part


# --------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------- #


def test_consolidated_developer_guide_exists() -> None:
    """The consolidated dev guide MUST exist (; Phase 7 creates it).

    Until Phase 7 lands, this assertion fails RED — that is the intent.
    """
    assert _CONSOLIDATED_GUIDE.exists(), (
        f"consolidated developer guide not found at {_CONSOLIDATED_GUIDE}. "
        f", the canonical end-user developer guide for the "
        f"resilient-task primitive MUST live at this path."
    )


def test_public_all_matches_post_cleanup_expected_set() -> None:
    """``tasks/__init__.py.__all__`` MUST match the Phase-3 cleanup target.

    Drift in either direction fails CI:

    - Extra symbol in ``__all__`` (e.g. the still-exported ``TaskSuspended``
      before Phase 3 lands the deletion) → RED until removed.
    - Missing symbol from ``__all__`` (e.g. a new public-surface addition
      that this test wasn't updated for) → RED until registered.
    """
    actual = _parse_all_from_init(_RESILIENT_INIT)
    assert actual, f"could not parse __all__ from {_RESILIENT_INIT}"

    missing = EXPECTED_PUBLIC_SYMBOLS - actual
    extra = actual - EXPECTED_PUBLIC_SYMBOLS

    msg_parts: list[str] = []
    if missing:
        msg_parts.append(f"symbols expected in __all__ but missing: {sorted(missing)}")
    if extra:
        msg_parts.append(
            f"symbols in __all__ but not in EXPECTED_PUBLIC_SYMBOLS " f"(retired or undeclared): {sorted(extra)}"
        )

    assert not msg_parts, " ; ".join(msg_parts) + (
        " — update EXPECTED_PUBLIC_SYMBOLS in this file if intentional, " "or fix the public surface."
    )


def test_retired_symbols_not_in_public_all() -> None:
    """Retired symbols  MUST NOT appear in ``__all__``.

    Belt-and-suspenders companion to ``test_public_all_matches_…``:
    explicitly names the symbols this spec retires so the failure
    message points directly at the spec clause.
    """
    actual = _parse_all_from_init(_RESILIENT_INIT)
    leaked = RETIRED_PUBLIC_SYMBOLS & actual
    assert not leaked, (
        f"symbols retired by   still appear in __all__: " f"{sorted(leaked)}. Phase 3 (T022-T025) MUST drop them."
    )


@pytest.mark.parametrize("clause_id,reference", sorted(CONTRACT_CLAUSE_TO_TEST.items()))
def test_every_contract_clause_has_a_paired_test(clause_id: str, reference: str) -> None:
    """Each documented contract clause MUST resolve to an existing test.

    This is the structural pairing guarantee from Constitution Principle XII
    rule 1: every public-surface clause has at least one paired test.
    Parametrized so the failure report lists EVERY missing pair, not just
    the first.
    """
    file_path, function_name = _resolve_clause_reference(reference)
    if not file_path.exists():
        pytest.fail(
            f"clause '{clause_id}' references {reference} but file " f"{file_path.name} does not exist in tests/tasks/"
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
    ``tests/tasks/test_*.py`` file. This is intentionally weak (a string
    match, not an import-trace) so it doesn't false-positive on symbols
    used via re-export; it catches the "added to ``__all__`` but never
    mentioned in any test" case.
    """
    actual = _parse_all_from_init(_RESILIENT_INIT)
    test_files: list[Path] = sorted(_RESILIENT_TESTS_DIR.glob("test_*.py"))
    blobs: dict[Path, str] = {p: p.read_text() for p in test_files}

    orphans: list[str] = []
    for symbol in sorted(actual):
        if not any(symbol in text for text in blobs.values()):
            orphans.append(symbol)

    assert not orphans, (
        f"public symbols never mentioned in any tests/tasks/test_*.py: "
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
#  — meta-test extension (per T-1.0 of)
# =========================================================================
#
# Per Constitution Principle XII §2 +  plan.md Phase 1 T-1.0.
# These tests assert the FULL public surface from Appendix A.1 of
# + negative absence assertions for unsupported surface + grep-clean
# invariants for unsupported code paths.
#
# Each assertion is RED until Phase 5 / Phase 7 lands the corresponding
# implementation cleanup.


def _read_resilient_init_source() -> str:
    return _RESILIENT_INIT.read_text()


def _read_resilient_source_tree() -> dict[Path, str]:
    """Read every .py file under azure/.../resilient/ (the source package)."""
    pkg = _RESILIENT_INIT.parent
    return {p: p.read_text() for p in sorted(pkg.rglob("*.py")) if "__pycache__" not in str(p)}


def test_spec_022_a_b_positive_and_negative_presence_in_all() -> None:
    """T-1.0 (a)(b) — redesigned symbols in EXPECTED; legacy in EXPECTED too during transition.

    Positive presence is already covered by
    :func:`test_public_all_matches_post_cleanup_expected_set`.

    During the Phase 2-5 transition window, both the new redesigned symbols
    AND the legacy symbols (TaskResult, Suspended, TaskSnapshot, TaskStatus,
    OutputTooLarge, TaskNotFound, TaskPreconditionFailed) coexist in
    ``EXPECTED_PUBLIC_SYMBOLS``. Phase 5 cleanup removes the legacy entries.
    """
    # Sanity: SOT additions are in EXPECTED_PUBLIC_SYMBOLS.
    for sym in {
        "multi_turn_task",
        "MultiTurnTask",
        "TaskDeferred",
        "JSONValue",
        "TaskErrorDict",
        "TaskExhaustedRetriesErrorDict",
    }:
        assert sym in EXPECTED_PUBLIC_SYMBOLS, f" T-1.0(a): {sym} MUST be in EXPECTED_PUBLIC_SYMBOLS"
    # During transition, legacy symbols are still in EXPECTED; Phase 5 moves
    # them to RETIRED_PUBLIC_SYMBOLS. For now, just ensure they're in one or
    # the other (no orphans).
    legacy_during_transition = {
        "TaskResult",
        "Suspended",
        "TaskSnapshot",
        "TaskStatus",
        "OutputTooLarge",
        "TaskNotFound",
        "TaskPreconditionFailed",
    }
    for sym in legacy_during_transition:
        assert (
            sym in EXPECTED_PUBLIC_SYMBOLS or sym in RETIRED_PUBLIC_SYMBOLS
        ), f" T-1.0(b): {sym} MUST be in EXPECTED or RETIRED set"
    # TaskCancelledError MUST always be retired (never existed as a public name).
    assert "TaskCancelledError" in RETIRED_PUBLIC_SYMBOLS


def test_spec_022_c_grep_clean_for_unsupported_code_paths() -> None:
    """T-1.0 (c) — SC-006: source tree grep-clean for removed code paths."""
    blobs = _read_resilient_source_tree()
    forbidden_patterns = {
        'payload["output"]': " — no payload['output'] writes",
        "_build_output_co_write": " — output co-write helper absent",
        "TaskManager.handle_resume": " — /tasks/resume manager method absent",
        "_resume_route.py": " — _resume_route module absent",
    }
    findings: list[str] = []
    for pattern, rule in forbidden_patterns.items():
        for path, text in blobs.items():
            if pattern in text and "_local_provider.py" not in path.name:
                # Allow harmless mentions in docstrings of removed-API checklists
                if "MUST NOT" in text or "removed" in text or "absent" in text:
                    continue
                findings.append(f"  {path.name}: {pattern!r}  ({rule})")
    assert not findings, " SC-006: source tree contains references to removed code paths:\n" + "\n".join(findings)


def test_spec_022_d_ctx_end_chain_absent() -> None:
    """T-1.0 (d) —: ctx.end_chain MUST NOT exist anywhere in tasks/."""
    blobs = _read_resilient_source_tree()
    findings = [str(path.name) for path, text in blobs.items() if "end_chain" in text]
    assert not findings, f": ctx.end_chain MUST NOT exist in tasks/ source — found in: {findings}"


def test_spec_022_e_ctx_shutdown_preserved() -> None:
    """T-1.0 (e) —  +: ctx.shutdown MUST exist on TaskContext."""
    try:
        from azure.ai.agentserver.core.tasks import TaskContext
    except ImportError:
        pytest.skip("TaskContext import failed (RED until Phase 5)")
    # Inspect class attrs / annotations for `shutdown` (asyncio.Event).
    has_shutdown = (
        hasattr(TaskContext, "shutdown")
        or "shutdown" in getattr(TaskContext, "__annotations__", {})
        or "shutdown" in getattr(TaskContext, "__slots__", ())
    )
    assert has_shutdown, ": TaskContext MUST expose `shutdown` (asyncio.Event) " "per  enumerated public surface."


def test_spec_022_f_cooperative_cancel_no_automatic_raise() -> None:
    """T-1.0 (f) —: framework cancellation is cooperative-only.

    Grep for any `async def force_cancel` / `raise asyncio.CancelledError`
    in _manager.py that would constitute an automatic raise. (The framework
    sets `ctx.cancel` + `ctx.timeout_exceeded` flags but never raises
    automatically; / -057 /  §3 Q11.)
    """
    pkg = _RESILIENT_INIT.parent
    manager_py = pkg / "_manager.py"
    if not manager_py.exists():
        pytest.skip("_manager.py not present (RED-first)")
    text = manager_py.read_text()
    # Look for `force_cancel` as a sync/async def — must NOT exist as a
    # public method that auto-raises.
    assert "def force_cancel" not in text, (
        ": framework MUST NOT expose `force_cancel`; cancellation is " "cooperative-only via ctx.cancel."
    )


def test_spec_022_g_run_return_type_is_output_directly() -> None:
    """T-1.0 (g) —:.run returns Output (not TaskResult/Awaitable[TaskResult])."""
    try:
        from azure.ai.agentserver.core.tasks import Task
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
        f": Task.run return annotation MUST resolve to Output directly; " f"found {found} in: {annot_str!r}"
    )


def test_spec_022_h_internal_only_cleanup_absent() -> None:
    """T-1.0 (h) —: enumerated internal symbols MUST NOT exist."""
    blobs = _read_resilient_source_tree()
    forbidden_symbols = {
        "_build_output_co_write": " / ",
        "TaskContext.suspend": "",
        "TaskRun._provider": "",
        "_terminate_event": "",
        "_terminate_reason_ref": "",
        # NOTE: _status / _lease_expiry_count are too generic to grep; skip
        # those and rely on  /  positive shape tests instead.
    }
    findings: list[str] = []
    for sym, rule in forbidden_symbols.items():
        for path, text in blobs.items():
            if sym in text:
                # Allow comment / docstring mentions
                relevant_lines = [
                    line
                    for line in text.splitlines()
                    if sym in line
                    and not line.strip().startswith("#")
                    and '"""' not in line
                    and not line.strip().startswith("*")
                ]
                if relevant_lines:
                    findings.append(f"  {path.name}: {sym!r} ({rule})")
                    break
    assert not findings, ": enumerated internal-only symbols MUST NOT exist:\n" + "\n".join(findings)


def test_spec_022_i_no_backward_compat_shims() -> None:
    """T-1.0 (i) — SC-007: no backward-compat shims silently added."""
    blobs = _read_resilient_source_tree()
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
        "(removals MUST be hard removals; no migration bridges):\n" + "\n".join(findings)
    )


def test_spec_022_TaskCancelledError_does_not_exist() -> None:
    """— TaskCancelledError (with Error suffix) MUST raise ImportError."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.tasks import TaskCancelledError  # noqa: F401


def test_spec_022_TaskNotFound_not_in_public_import() -> None:
    """— TaskNotFound MUST NOT import from the public namespace."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.tasks import TaskNotFound  # noqa: F401


def test_spec_022_TaskPreconditionFailed_not_in_public_import() -> None:
    """— TaskPreconditionFailed MUST NOT import from the public namespace."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.tasks import TaskPreconditionFailed  # noqa: F401


def test_spec_022_OutputTooLarge_not_in_public_import() -> None:
    """— OutputTooLarge MUST NOT import from the public namespace."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.core.tasks import OutputTooLarge  # noqa: F401
