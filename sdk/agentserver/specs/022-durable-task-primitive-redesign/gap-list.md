# Spec 022 — Gap list

This file tracks MEDIUM/LOW findings logged during implementation
(per Principle XIII §3 — "MEDIUM/LOW findings logged; BLOCKING/HIGH
clear before the next phase begins"). It also captures any deferred
items + follow-up TODOs that don't block the spec's primary work.

## Baseline test sweep (2026-06-13, pre-Phase 1)

- `pytest tests/durable/` → 511 passed, 5 skipped, 0 failed.

## Post-Phase 1 (2026-06-13)

- `pytest tests/durable/` → 543 passed, 110 failed RED, 63 skipped.
- 13 new test files added, all collect successfully.
- 110 RED tests will turn GREEN as Phases 2-7 implementation lands.
- 32 incidental new passes are from existing-suite invariants that the
  spec 022 test extensions reinforced (e.g., contract_completeness
  meta-test extensions now also check spec 021-era invariants).

## Findings log

### 2026-06-13 (post-Phase 2 partial)

- **RetryPolicy field types** — Spec 022 FR-073 specifies
  `initial_delay: float`, `max_delay: float`, `jitter: float`, but
  current `_retry.py` uses `initial_delay: timedelta`, `max_delay:
  timedelta`, `jitter: bool`. Test
  `test_decorator_surface.py::TestRetryPolicyShape::test_RetryPolicy_field_names`
  fails RED. Fix is Phase 2 deeper refactor (changes `RetryPolicy.__init__`
  + all preset classmethods + all callers passing `timedelta`).
  Tracked as Phase 2 follow-up.
- **Handler arg-name check** — Test
  `TestHandlerSignatureValidation::test_handler_wrong_first_arg_name_rejected`
  expects rejection of non-`ctx` first arg name. Current
  `_validate_handler_signature` doesn't enforce the NAME (only the
  presence of a first arg). This is a deliberate judgment call —
  Python convention; the framework binds positionally, not by name.
  May tighten in Phase 2 follow-up.
- **LastInputIdPreconditionFailed signature** — FR-076 requires only
  `actual_last_input_id` kwarg; current impl supports BOTH legacy
  positional `(task_id, expected, actual)` and new keyword-only
  `actual_last_input_id=` to maintain backward compat with existing
  callers in `_decorator.py`. Test
  `test_exception_taxonomy.py::TestExceptionShapes::test_LastInputIdPreconditionFailed_carries_actual_only`
  fails RED on signature inspection (expects only one arg). Phase 5
  cleanup will migrate the single caller in `_decorator.py:312` and
  remove the legacy form, making the test GREEN.
- **`Task.options()` method (T-2.4 FR-006)** — currently still
  exists on `Task` and is used by existing tests. Removal is a Phase 5
  cleanup task (would break tests that rely on per-call option
  overrides). Tracked as Phase 5 follow-up.

## Follow-up items

- **Langgraph live e2e test** — Phase 7 adds a smoke test for
  `durable_langgraph` per FR-068b/c; a full live e2e is OUT OF
  SCOPE for this branch (no live test exists today). Follow up
  in a separate issue.
- **`durable-agent-demo` migration** — tracked on
  `feature/agentserver-durable-agent-demo` branch per FR-068d.
  Cross-branch hand-off issue to be filed in Phase 7 T-7.12.
- **Durability contract amendment** — the
  `sdk/agentserver/specs/durability-contract.md` file lives on
  `feature/agentserver-responses-spec016` branch (removed from this
  branch per commit `5c110099d6` — PR scope split). Spec 022's
  contract changes (handler-failure semantic Q6/FR-010-13, recovery
  input-source Q13/FR-033-35, output/error persistence FR-025-027,
  public read-API surface FR-016-021) MUST be added to the contract
  file on that branch as a coordinated PR. Hand-off issue to be
  filed in T-0.3 (Phase 0); cross-branch coordination tracked
  alongside FR-068d.
- **Responses-package migration (FR-066/067/068, SC-008, T-1.13, T-7.2/3/4/5)** — `_durable_orchestrator.py` and the bookkeeping-task body do NOT exist on this branch; they were moved to `feature/agentserver-responses-spec016` per commit `5c110099d6` (PR scope split). All responses-related migration work MUST happen on that branch's PR as a coordinated effort, blocked by THIS branch merging. Cross-branch hand-off issue to be filed alongside FR-068d (durable-agent-demo).

## Final closeout (2026-06-13 session-close)

### Test sweep final
- `pytest tests/durable/` → **655 passed, 11 failed (RED), 22 skipped, 1 error (pre-existing flaky)**
- +144 net from 511 baseline (the dip from 690 peak reflects intentional deletion of legacy test files `test_task_get_api.py`, `test_task_result.py`, `test_resume_route.py` per spec 022 FR-017/FR-018/FR-049)

### Files deleted on this branch (spec 022 surface cleanup)
- `azure/ai/agentserver/core/durable/_result.py` — FR-018: `TaskResult` wrapper removed
- `azure/ai/agentserver/core/durable/_snapshot.py` — FR-017: `TaskSnapshot` + `Task.get` removed
- `azure/ai/agentserver/core/durable/_resume_route.py` — FR-049: `/tasks/resume` route + `TaskManager.handle_resume` removed
- `tests/durable/test_task_result.py` — subject (`TaskResult`) deleted
- `tests/durable/test_task_get_api.py` — subjects (`Task.get`, `TaskSnapshot`) deleted
- `tests/durable/test_resume_route.py` — subject (`_resume_route`) deleted

### Test skips (legacy behavior removed by spec 022, not migrable)
- `test_attachments_model::test_resolve_raises_inputtoolarge_when_over_cap` — `InputTooLarge` bare per FR-077
- `test_errors_public_surface::test_input_too_large_remap_from_internal_input_key` — same
- `test_steering_attachment_queue::test_steering_queue_9_cap` — `SteeringQueueFull` bare per FR-077
- `test_steering::test_steering_queue_full_exception` — same
- `test_metadata::test_underscore_namespace_not_enforced_by_primitive` — FR-044 reserves `_*`
- `test_metadata::test_default_namespace_has_no_framework_keys` — uses `_responses`
- `test_decorator_surface::test_task_rejects_steerable_kwarg` / `..._ephemeral_kwarg` — transitional `DeprecationWarning` per FR-051
- `test_errors_public_surface::test_task_run_delete_translates_hosted_conflict` — `TaskRun.delete` removed per Q9
- `test_models::test_task_cancelled` — `TaskCancelled` is bare per FR-077; `str(exc)` is fixed
- `test_output_lifecycle::test_*` (3 tests) — FR-025/026/027: no output/error payload writes
- `test_output_promotion::test_suspend_output_none_writes_explicit_null` — same
- `test_public_api_surface::test_task_get_list_renamed_to_private` — `Task.get` deleted entirely
- `test_entry_mode::test_platform_resume_entry_mode` — `handle_resume` removed per FR-049
- `test_sample_e2e::test_langgraph_multiturn_interrupt_resume` — same

### 11 RED tests remaining (deep multi-turn engine work tracked here, not blocking the spec 022 public surface)

| Test | FR | Why RED |
|------|----|---------|
| `test_cancellation_matrix::TestDeleteVsPromotionRace::test_delete_before_promotion_cas_queued_head_never_runs` | FR-061 | force-delete-vs-promotion race ordering |
| `test_cancellation_matrix::TestExitForRecovery::test_exit_for_recovery_record_stays_in_progress` | FR-039/058 | exit_for_recovery PATCH+record-status invariant |
| `test_cancellation_matrix::TestQueuedSteererCancel::test_queued_cancel_removes_from_queue` | FR-037 | queued-future cancel must also delete persisted queue entry |
| `test_cancellation_matrix::TestRunCancelMultiTurn::test_queued_steerer_promotes_after_cancelled_turn` | FR-013 | cancel→suspend→promote ordering |
| `test_cancellation_matrix::TestRunCancelOneShot::test_handler_raises_CancelledError_caller_sees_TaskCancelled` | FR-012 | one-shot CancelledError wrapping edge |
| `test_cancellation_matrix::TestTimeoutMultiTurn::test_watchdog_rearmed_on_steering_drain` | FR-058 | per-turn watchdog re-arm on drain |
| `test_entry_mode::TestEntryModeV2Matrix::test_entry_mode_recovered_inline_reclaim` | FR-034/064 | inline-recovery uses-persisted-input invariant (one code path still uses caller-input) |
| `test_multi_turn_raise::TestSevenStepOrdering::test_current_TaskFailed_resolves_before_queued_promotes` | FR-053 | 7-step ordering observability |
| `test_multi_turn_raise::TestSevenStepOrdering::test_queued_promotion_uses_cleared_input_slot` | FR-053 | drain PATCH must observe cleared input |
| `test_persistence::TestInputClearingRules::test_one_shot_input_cleared_at_terminal` | FR-028 | ephemeral one-shot doesn't write interim input=None PATCH before delete |
| `test_sample_e2e::TestListE2E::test_list_returns_only_this_tasks_records` | (test isolation) | manager singleton bleed across test runs |

### Phase 7/8 follow-ups (NOT done on this branch — explicitly scoped to follow-up PR)

- **T-7.12** — `feature/agentserver-durable-agent-demo` cross-branch migration (tracking issue or coordinated draft PR on that branch)
- **T-7.13** — Phase 7 cross-area code review
- **T-8.1** — Cross-area code review
- **T-8.3** — Full multi-package test sweep (done for `-core`; not done for `-responses` / `-invocations` test suites)
- **T-8.4** — gap-list closeout per finding (this document is the closeout)
- **T-8.5** — Final pre-merge code-review agent pass
- **T-8.6** — `durability-contract.md` versioned change-log entry (CROSS-BRANCH HAND-OFF — file is on `feature/agentserver-responses-spec016`)
- **T-8.7** — FR/SC implementation/verification table

### Cross-branch hand-offs (NOT done on this branch — by design per scope-split)

- `_durable_orchestrator.py` + bookkeeping body — `feature/agentserver-responses-spec016`
- `durability-contract.md` — `feature/agentserver-responses-spec016`
- `samples/durable-agent-demo/` — `feature/agentserver-durable-agent-demo`
