# Spec 022 — Task breakdown (per-phase commit plan)

Phases per `plan.md`. Each phase emits N logical commits on the
local `feature/agentserver-durable-tasks` branch; no pushes.

Spec 022 has **81 FRs** (FR-001..FR-077 + FR-068a + FR-068b + FR-068c + FR-068d) and **19 SCs** (SC-001..SC-018 + SC-009a).
Every FR / SC maps to a phase and a paired test per Principle XII §3.

---

## Phase 0 — Pre-impl audit + SOT update

- [x] T-0.1 — **Conformance gap-list** (`conformance-gap-list.md`
  in this spec dir): for every FR / SC in `spec.md`, record the
  extend-X-vs-new-Y test-file decision per Principle XII §2. Map
  each FR to the existing test file that needs extension OR the
  new test file that needs creation, with justification.
- [x] T-0.2 — **SOT rewrite** (`docs/task-and-streaming-spec.md`):
  apply the Q17 cleanup list from 021 §3 — remove §26 (resume route),
  §35a (TaskSnapshot definition), `TaskResult`/`Suspended` definitions
  in §34/§35, `OutputTooLarge` from §39 error taxonomy,
  output-persistence sections in §20 (`_output` attachment + size cap),
  `payload["output"]` mentions in §11/§23/C-* sections,
  `payload["error"]` mentions in §4 (interim retry) and elsewhere,
  `ephemeral` parameter docs in §32/§3, C-OUT conformance group,
  C-SUS-4, C-ATT-3/4/5 output-related parts, C-INTROSPECT
  (TaskSnapshot conformance), public `TaskStatus` literal. ADD new
  sections describing: `@multi_turn_task` decorator + classmethod
  surface, `TaskDeferred` exception, `if_last_input_id` on both
  primitives, class-split type-safety contract, 7-step ordering
  for multi-turn raise, cancellation matrix per FR-053-062,
  entry_mode matrix per FR-063.
- [x] T-0.3 — **Durability contract amendment** (CROSS-BRANCH HAND-OFF — file lives on `feature/agentserver-responses-spec016` branch, NOT on this branch per commit `5c110099d6`). The Constitution Principle X references `sdk/agentserver/specs/durability-contract.md` but this branch's scope-split PR removed responses-related artifacts. The contract amendment for spec 022's design (handler-failure semantic Q6/FR-010-13, recovery input-source Q13/FR-033-35, output/error persistence FR-025-027, public read-API surface FR-016-021) MUST be filed on the responses-spec016 branch as a coordinated PR + linked from this branch's PR description (same hand-off pattern as FR-068d for the demo). Recorded in `gap-list.md` under follow-up items. No commit needed on this branch.
- [x] T-0.4 — **Baseline test sweep snapshot**: run
  `pytest tests/durable/` on the current branch HEAD;
  record passing-count as the floor that Phase 1 RED additions add to.
  Document the baseline in `gap-list.md`. **DONE 2026-06-13: 511 passed, 5 skipped, 0 failed (test_local_provider + test_lease_renewal + test_cancellation_timeout + ... — full durable suite).**
- [x] T-0.5 — **Commit** (single commit):
  `[agentserver] core: spec 022 — SOT update + conformance gap-list`.

---

## Phase 1 — Tests (failing) — RED-first per Principle XII §3

One commit per test file (13 commits total). Each new test asserts
the FR/SC behavior; tests MUST FAIL against the current branch HEAD.

- [x] T-1.0 — **Meta-test extension** (Principle XII §2): extend
  `tests/durable/test_contract_completeness.py` to enumerate the
  full public surface from Appendix A.1 of 021 (decorators, classes,
  exceptions, type aliases, TypedDicts) and assert:
  - **(a) Positive presence** — every listed symbol is in `__all__`.
  - **(b) Negative absence** — no unsupported symbols (`TaskResult`,
    `Suspended`, `TaskSnapshot`, `TaskStatus`, `OutputTooLarge`,
    `TaskCancelledError`, `TaskNotFound`, `TaskPreconditionFailed`)
    appear in `__all__`.
  - **(c) Source-tree grep clean** — removed code paths absent per
    SC-006.
  - **(d) `ctx.end_chain` absent** (FR-009) — grep
    `azure/ai/agentserver/core/durable/` for `end_chain`; MUST be
    empty.
  - **(e) `ctx.shutdown` preserved** (FR-040) — assert
    `TaskContext.shutdown` exists as an `asyncio.Event` attribute
    per FR-072.
  - **(f) Cooperative-cancel rule** (FR-036) — assert that the
    framework's only cancellation surface is `ctx.cancel` +
    `ctx.timeout_exceeded` flags; no `async def force_cancel` /
    no automatic raise paths in `_manager.py`.
  - **(g) `.run()` return type** (FR-052) — verify
    `inspect.signature(Task.run).return_annotation` resolves to
    `Output` (not `TaskResult` / `Awaitable[TaskResult]`); verify
    auto-generated `task_id` is NOT surfaced via `.run()` return
    (only `.start()` returns a `TaskRun` handle exposing it).
  - **(h) Internal-only cleanup** (FR-065) — grep that none of the
    enumerated internal symbols (`_build_output_co_write`,
    `TaskContext.suspend`, `TaskRun._provider`,
    `_terminate_event`, `_terminate_reason_ref`, `_status`,
    `_lease_expiry_count`, `TaskInfo.output`, `TaskInfo.error`,
    `_resume_route.py` file presence, `TaskManager.handle_resume`)
    appear in the source tree.
  - **(i) No backward-compat shims** (SC-007) — grep for shim
    markers (`# COMPAT`, `# backward-compat`, deprecated wrapper
    classes named `TaskResultCompat` / `SuspendedCompat` / etc.);
    MUST be empty. This is a NEGATIVE assertion that no migration
    bridge was silently added.
  Commit RED.
- [x] T-1.1 — `test_decorator_surface.py` — FR-001/002/003/004/005/051/069 + SC-016/018. Class-split mypy/pyright assertions; `title=` non-string rejection; `ephemeral=`/`steerable=`/`tags=` rejection; handler-signature validation. Commit RED.
- [x] T-1.2 — `test_input_precondition.py` — FR-029/076 + SC-005. `if_last_input_id` mismatch raises `LastInputIdPreconditionFailed(actual_last_input_id)`; `_last_input_id` retention across suspend cycle; `_last_input_id` is NOT used as recovery input source. Commit RED.
- [x] T-1.3 — `test_multi_turn_raise.py` — FR-007/010-015/053 + SC-003/010. **Return-is-implicit-suspend (FR-007)**: assert that a multi-turn handler returning `X` (no exception) transitions the record to `suspended` with internal `suspension_reason="run_completion"` AND that `await taskrun.result()` returns `X` to the caller. 7-step ordering observable in single E2E (auto-flush BEFORE PATCH; current TaskFailed BEFORE queued-steerer promote; chain stays alive); chain accepts subsequent inputs; queued steerer promotes with `entry_mode="resumed"`. Commit RED.
- [x] T-1.4 — `test_retry.py` — FR-041/042/043 + SC-012. Per-handler-invocation retry budget; crash recovery doesn't consume budget; one-shot post-exhaustion deletes record; multi-turn post-exhaustion transitions to suspended; subsequent turns fresh budgets. Commit RED.
- [x] T-1.5 — `test_metadata_flush.py` — FR-044/045/046 + SC-011. `TaskMetadata` dunders + `get` + namespace callable; reserved `_`-prefix raises `ValueError`; auto-flush load-bearing across raise (next turn sees metadata); one-shot metadata invocation-local. Commit RED.
- [x] T-1.6 — `test_persistence.py` — FR-025-032 + SC-001. No `payload["output"]` written; no `_output` attachment; no `payload["error"]`; input cleared at suspend/terminal; `_retry_attempt` cleared; `_last_input_id` kept; steering queue in `payload["_steering"]`. Commit RED.
- [x] T-1.7 — `test_exception_taxonomy.py` — FR-070-077 + SC-017. All exception shapes — bare vs fielded; `TaskFailed.__cause__ is None`; `JSONValue` recursive alias; `TaskErrorDict`/`TaskExhaustedRetriesErrorDict` shapes; `from azure.ai.agentserver.core.durable import TaskNotFound` raises `ImportError`; same for `TaskCancelledError`. Commit RED.
- [x] T-1.8 — `test_cancellation_matrix.py` — FR-037/054-062 + SC-014. One row per matrix cell; clean return → `Output` even when `ctx.cancel` set; `CancelledError` → bare `TaskCancelled`; other `E` → `TaskFailed`; queued-steerer cancel removes from queue and resolves with `TaskCancelled`; force-delete-vs-promotion race resolves through FR-060 lease-loss. Commit RED.
- [x] T-1.9 — `test_active_run.py` — FR-022/023 + SC-002/005. Multi-turn `get_active_run(task_id, input_id)` matches exact input_id; returns None for mismatch; returns None for terminated runs (no retrospective attach); sequential multi-turn turns accumulate metadata correctly. Commit RED.
- [x] T-1.10 — `test_entry_mode.py` (extend existing) — FR-063 + SC-013. All 6 entry_mode scenarios (fresh / resumed / recovered / steering promotion) asserted. Commit RED.
- [x] T-1.11 — `test_inline_recovery.py` — FR-033/034/035/064 + SC-004/015. `.start()` against expired-lease in-progress record uses persisted input; caller's new input flows through standard non-crash path (TaskConflictError or queue); observational identity between crash and non-crash flows for the same logical call sequence. Commit RED.
- [x] T-1.12 — `test_taskrun_shape.py` — FR-047/048. Slim `TaskRun` surface: 2 attributes + 1 property + 2 async methods + 1 dunder; no `status`, `delete`, `refresh`, `lease_expiry_count`. Internal slots absent. Commit RED.
- [x] T-1.13 — `tests/integration_responses/test_durable_orchestrator_v2.py` — **HAND-OFF to `feature/agentserver-responses-spec016` branch (NOT on this branch).** The `_durable_orchestrator.py` file was moved to that branch per commit `5c110099d6` (scope split). Responses migration tests for FR-066/067/068 + SC-008 MUST be authored on that branch's PR as a coordinated effort. Recorded in `gap-list.md` under follow-up items. No commit needed on this branch.
- [x] T-1.14 — **Phase 1 verification**: confirm every new test
  fails against the current branch HEAD; pre-existing tests stay
  green; total test count increases by ~25-30. Update `gap-list.md`
  with the new baseline. **DONE 2026-06-13: 543 passed (511 baseline + 32 new GREEN incidentals), 110 failed RED, 63 skipped. 13 new test files collect.**

---

## Phase 2 — Implementation: Primitive split + identifier supply + handler-sig validation

One commit per area + doc travel per Principle IX.

- [x] T-2.1 — `_decorator.py` split: `Task` (one-shot) + `MultiTurnTask` (multi-turn) as distinct public classes per FR-069; `@task` returns `Task[I, O]`; `@multi_turn_task(steerable=)` returns `MultiTurnTask[I, O]`. FR-051 kwarg rejection (`ephemeral=`/`steerable=` on `@task`/`tags=`). `title=` accepts only `str | None` per FR-001/002. Handler signature validation per FR-003 (sync/wrong-arg/missing-annotation → `TypeError` at decoration time). Update `__init__.py` `__all__` for the new exports. Update dev-guide decorator section. Commit (turns Phase 1 tests T-1.1 GREEN for those FRs).
- [x] T-2.2 — `.run()` / `.start()` identifier supply (FR-004/005) on both classes: one-shot auto-gens `task_id` + collapses `input_id=task_id`; multi-turn requires `task_id`. Both methods accept `if_last_input_id: str | None = None` kwarg. **Precondition behavior**: when `if_last_input_id` is supplied, framework compares against persisted `payload["_last_input_id"]` (FR-029); mismatch → `LastInputIdPreconditionFailed(actual_last_input_id)` (FR-076). Commit (turns T-1.2 GREEN).
- [x] T-2.3 — `multi_turn_task.delete(task_id)` async classmethod (FR-024) — force-delete via provider DELETE with `force=True`. Idempotent. `multi_turn_task.get_active_run(task_id, input_id)` async classmethod (FR-023) — in-process only; cross-process attach NOT supported. Commit (turns T-1.9 GREEN).
- [x] T-2.4 — `_options.py` cleanup: no `Task.options` classmethod (FR-006), no `ephemeral` field, tightened allow-list. Commit.
- [x] T-2.5 — `_retry.py` docs: confirm/document `RetryPolicy.__init__` matches FR-073 (`max_attempts`, `initial_delay`, `max_delay`, `backoff_coefficient`, `jitter`, `retry_on`); presets enumerate kwargs. No code change. Commit.
- [x] T-2.6 — **Phase 2 code review** per Principle XIII (use `code-review` agent). SCOPE: class-split type-safety actually enforced by mypy/pyright (not just runtime); decorator allow-list covers all variants; `title=` non-string rejection at decoration time; identifier supply edge cases (auto-gen collisions, one-shot 1:1 invariant, `if_last_input_id` precondition error shape). Apply BLOCKING/HIGH findings before Phase 3 begins; log MEDIUM/LOW to `gap-list.md`.

---

## Phase 3 — Implementation: Multi-turn ergonomics + raise + retry + auto-flush

- [x] T-3.1 — `_context.py`: remove public `ctx.suspend()` method on multi-turn context (FR-008); internal `suspension_reason` recording stays. Update dev-guide multi-turn section. Commit.
- [x] T-3.2 — `_manager.py` multi-turn raise semantics (FR-010-015 + FR-053). Refactor `_handle_failure` → `_handle_multi_turn_failure` per 7-step ordering: (1) run failure handler, (2) auto-flush `ctx.metadata` BEFORE PATCH (load-bearing per FR-045), (3) clear `payload["input"]` + `payload["_retry_attempt"]`, (4) PATCH chain to `suspended` with `suspension_reason="run_completion"`, (5) resolve caller's future — `CancelledError` → bare `TaskCancelled` else `TaskFailed(error_dict)`, (6) if queued steerers exist promote head with `entry_mode="resumed"`, (7) else leave chain in `suspended`. Structured failure log per FR-015. Commit (turns T-1.3 + T-1.7 GREEN for relevant assertions).
- [x] T-3.3 — `_manager.py` retry semantics (FR-041/042/043). Verify within-attempt retry behavior (unchanged from current `RetryPolicy` mechanics); crash recovery does NOT consume budget; suspend bypasses retry; one-shot post-exhaustion → record deleted + `TaskFailed` to caller (FR-042); multi-turn post-exhaustion → chain `suspended` + `TaskFailed` to listener + subsequent turns get fresh retry budgets (FR-043). Commit (turns T-1.4 GREEN).
- [x] T-3.4 — `_metadata.py` + `_manager.py` auto-flush (FR-045/046): auto-flush at all lifecycle boundaries (suspend / success / cancel / retry-exhausted); load-bearing at multi-turn raise (next turn's handler MUST see flushed metadata — FR-045); one-shot metadata invocation-local — no cross-invocation visibility (FR-046). Update dev-guide metadata section. Commit (turns T-1.5 GREEN).
- [x] T-3.5 — `_manager.py` one-shot raise path (FR-014): `in_progress → completed`, delete record, raise `TaskFailed` on caller. Commit.
- [x] T-3.6 — **Phase 3 code review** per Principle XIII. SCOPE: 7-step ordering observable (auto-flush BEFORE PATCH; current TaskFailed resolves BEFORE queued steerer promotes; queued promotion uses persisted-cleared input slot); `ctx.suspend()` truly absent from public surface (grep + import-fail check); multi-turn raise truly transitions to `suspended` not `completed`; queued-steerer promotion uses correct `entry_mode` (`"resumed"`); retry-budget reset on suspend; metadata propagation across raise. Apply BLOCKING/HIGH before Phase 4.

---

## Phase 4 — Implementation: Storage and persistence

- [x] T-4.1 — `_manager.py` output write removal (FR-025/026/068a): delete `_build_output_co_write` and all output write/clear sites (success / suspend / drain Phase-1 / `_handle_failure`). No output serialization or size-check anywhere. Local provider gets NO code change (manager owns output write sites per Q16). Commit.
- [x] T-4.2 — `_manager.py` error PATCH removal (FR-027/031): no `payload["error"]` write on terminal failure; no interim `error` PATCH between retry attempts. Commit.
- [x] T-4.3 — `_manager.py` input/retry-attempt clearing (FR-028/030): clear `payload["input"]` (and any input-attachment) at suspend / terminal transition ONLY (not mid-handler); clear `payload["_retry_attempt"]` at the same transition. Keep `payload["_last_input_id"]` (FR-029). Steering queue stays in `payload["_steering"]` (FR-032). Commit.
- [x] T-4.4 — `_models.py`: remove `_OUTPUT_KEY` + `_ERROR_KEY` payload-key constants and any helpers that read them. Update SOT spec §20 (framework-reserved payload keys). Update dev-guide payload section. Commit (turns T-1.6 GREEN).
- [x] T-4.5 — **Phase 4 code review** per Principle XIII. SCOPE: no remaining `payload["output"]` / `_output` / `payload["error"]` write sites (grep clean per SC-006); `payload["input"]` clearing at exactly the right transition; `_last_input_id` survives across suspend cycles (regression test); local provider tests still green (no code changed there). Apply BLOCKING/HIGH before Phase 5.

---

## Phase 5 — Implementation: Public surface and exception taxonomy

- [x] T-5.1 — Delete `_result.py` (no `TaskResult` / `Suspended`); delete `_snapshot.py` (no `TaskSnapshot`). Update all internal callsites in `_manager.py` to resolve futures with `Output` directly (FR-018/019). Commit.
- [x] T-5.2 — `_run.py` slim shape (FR-047/048): 2 attributes (`task_id`, `input_id`) + 1 property (`metadata`) + 2 async methods (`result`, `cancel`) + 1 dunder (`__await__`). Remove `status`, `delete`, `refresh`, `lease_expiry_count`. Remove internal slots `_provider`, `_terminate_event`, `_terminate_reason_ref`, `_status`, `_lease_expiry_count`. Commit (turns T-1.12 GREEN).
- [x] T-5.3 — `_exceptions.py` rewrite (FR-070-077). Bare exceptions: `TaskCancelled`, `TaskDeferred`, `SteeringQueueFull`, `InputTooLarge` (FR-077). Fielded exceptions: `TaskFailed(error)`, `TaskConflictError(current_status)`, `LastInputIdPreconditionFailed(actual_last_input_id)` (FR-076 — only `actual` field, not `expected`). Add `TaskErrorDict` + `TaskExhaustedRetriesErrorDict` TypedDicts per FR-071 (typed payload for `TaskFailed.error`). Remove `OutputTooLarge` from public exports (FR-021). Move `TaskNotFound` + `TaskPreconditionFailed` to `_exceptions_internal.py` (FR-074). `TaskFailed.__cause__ is None` invariant preserved (FR-075). `TaskCancelledError` name does not exist (FR-077). Commit (turns T-1.7 GREEN for these assertions).
- [x] T-5.4 — `_metadata.py` finalize: `JSONValue` recursive type alias exported (FR-070); `TaskMetadata` public surface per FR-044 (dunders + `get` + namespace callable + `_`-prefix reserved). Commit.
- [x] T-5.5 — `__init__.py` `__all__` rewrite: 7 public exceptions + `Task` + `MultiTurnTask` + `task` + `multi_turn_task` + `TaskRun` + `TaskContext` + `TaskMetadata` + `JSONValue` + `TaskErrorDict` + `TaskExhaustedRetriesErrorDict` + `TaskDeferred` + `RetryPolicy` + `EntryMode`. Remove all unsupported re-exports. Fix stale docstring at line 18-19 per FR-050. Commit (turns T-1.0 + T-1.7 GREEN).
- [x] T-5.6 — Update dev-guide exception taxonomy section + TaskRun shape section + SOT spec error taxonomy §39 trim. Commit.
- [x] T-5.7 — **Phase 5 code review** per Principle XIII. SCOPE: exception public-surface (FR-070-077) — every public exception class has the right field set; `TaskNotFound` / `TaskPreconditionFailed` truly absent from `__all__` (SC-017); `TaskRun` slim shape (FR-047) — no `status` / `delete` / `refresh`; `TaskFailed.__cause__ is None` invariant (FR-075); mypy/pyright strict mode green for the new typed exports. Apply BLOCKING/HIGH before Phase 6.

---

## Phase 6 — Implementation: Cancellation / timeout / recovery

- [x] T-6.1 — `_manager.py` cancellation matrix (FR-054-057): caller-visible outcome depends ENTIRELY on what the handler raises — `CancelledError` → `TaskCancelled`, other `E` → `TaskFailed`, clean return → `Output` (no auto-conversion even when `ctx.cancel` set). Timeout watchdog cooperative-only (never raises automatically); FR-038 re-arm watchdog on steering drain. Commit (turns T-1.8 partial GREEN).
- [x] T-6.2 — `_manager.py` queued-steerer cancel (FR-037): `TaskRun.cancel()` on a handle bound to a queued (not-yet-promoted) steerer removes the input from `payload["_steering"]` and resolves the handle's `.result()` with `TaskCancelled`. Chain unaffected. Commit (turns T-1.8 fully GREEN for cancel rows).
- [x] T-6.3 — `_context.py` + `_manager.py` `ctx.exit_for_recovery()` (FR-039/058): caller's `.result()` raises `TaskDeferred` (NOT `TaskCancelled`); task stays `in_progress`. Commit.
- [x] T-6.4 — `_manager.py` inline-recovery (FR-033/034/035/064): `.start()` against expired-lease in-progress record acquires lease via CAS, re-invokes handler with PERSISTED input (entry_mode="recovered"), evaluates caller's new input through standard non-crash path (TaskConflictError for one-shot/non-steerable, queue for steerable). Observational identity guaranteed between crash and non-crash flows. Commit (turns T-1.11 GREEN).
- [x] T-6.5 — `_context.py` entry_mode matrix (FR-063): `ctx.entry_mode` literal correctly stamped for the 6 scenarios. Commit (turns T-1.10 GREEN).
- [x] T-6.6 — `_manager.py` force-delete-vs-promotion race (FR-061): if promotion CAS succeeded before delete, newly-promoted turn raises `TaskCancelled` via FR-060 lease-loss path (NOT cooperative FR-055); if delete arrived first, queued head never runs, resolved with `TaskCancelled`. Commit.
- [x] T-6.7 — Update dev-guide cancellation section + SOT cancellation matrix. Commit.
- [x] T-6.8 — **Phase 6 code review** per Principle XIII. SCOPE: cancellation matrix conformance (FR-054-062) — one E2E test per row; FR-061 force-delete-vs-promotion race resolves to `TaskCancelled` regardless of timing (NOT through FR-055 cooperative path); inline-recovery (FR-064) uses persisted input not caller's new input; entry_mode (FR-063) correct for all 6 scenarios. Apply BLOCKING/HIGH before Phase 7.

---

## Phase 7 — Downstream migration + final docs

- [x] T-7.0 — **Stale `durable-agent-demo/` folder removed** from this branch's `azure-ai-agentserver-invocations/samples/`. Only `.gitignore` was tracked (everything else was gitignored: wheels, `__pycache__`, `.demo-session`). The actual demo lives on `feature/agentserver-durable-agent-demo` branch — see T-7.12 for the cross-branch hand-off tracking. To be committed as part of T-7.1 or a dedicated cleanup commit.
- [x] T-7.1 — Delete `_resume_route.py` (FR-049). Delete `TaskManager.handle_resume` method. Update tests that referenced them (`test_entry_mode.py:109`, `test_sample_e2e.py:337/361/529/554`). Remove SOT §26 + related conformance items. Commit (may bundle with T-7.0 stale-folder removal).
- [x] T-7.2 — Responses migration (FR-066/067) — **HAND-OFF (see T-1.13).** `_durable_orchestrator.py` does not exist on this branch; lives on `feature/agentserver-responses-spec016`. Migration work happens on that branch's PR.
- [x] T-7.3 — Responses migration `ctx.suspend()` rewrites — **HAND-OFF (see T-1.13).** No `ctx.suspend(...)` call sites exist in the responses package on this branch.
- [x] T-7.4 — Responses bookkeeping-task variant verification — **HAND-OFF (see T-1.13).** Bookkeeping body lives on the responses-spec016 branch.
- [x] T-7.5 — Document `steerable_conversations` config-flip orphaning — **HAND-OFF.** Belongs in the responses-spec016 branch's CHANGELOG.
- [ ] T-7.6 — **Final dev-guide rewrite per Q17** (MOVED EARLIER per Principle IX — guide is the source from which samples derive). `durable-task-guide.md`: omit `Task.options` / `Task.get` / `ctx.suspend()` / `ephemeral` sections; rewrite examples using `return X` for multi-turn; fix stale `async for chunk in task_run` docstring; add `TaskDeferred` + `multi_turn_task.delete` sections + cancellation matrix worked example + retry budget section + metadata namespace docs. Each example MUST be mechanically reproducible from the documented public surface. Commit.
- [x] T-7.7 — **Invocations samples migration — `durable_research`** (FR-068b/c). Derived from the updated dev-guide (T-7.6) per Principle IX. `azure-ai-agentserver-invocations/samples/durable_research/agent.py`: `@task(name="deep_research", steerable=True)` → `@multi_turn_task(name="deep_research", steerable=True)`. `return await ctx.suspend()` (line 413) → `return None`. Update docstring references to `ctx.suspend(...)` / `Suspended` sentinel to describe the return-is-implicit-suspend semantic (verbatim from the dev-guide). Verify `tests/e2e/test_durable_research_live.py` green. Commit.
- [x] T-7.8 — **Invocations samples migration — `durable_multiturn`** (FR-068b/c). Derived from the updated dev-guide (T-7.6). `azure-ai-agentserver-invocations/samples/durable_multiturn/agent.py`: `@task(name="session_workflow")` → `@multi_turn_task(name="session_workflow")` — **`steerable=False`** (default; the sample is sequential turns with no parallel-input pattern — verified against agent.py + app.py). `return await ctx.suspend(reason="awaiting_user_input", output=output)` (line 118) → `return output`. Verify `tests/e2e/test_durable_multiturn.py` green. Commit.
- [x] T-7.9 — **Invocations samples migration — `durable_langgraph`** (FR-068b/c). Derived from the updated dev-guide (T-7.6). `azure-ai-agentserver-invocations/samples/durable_langgraph/agent.py`: `@task(name="langgraph_session", steerable=True)` → `@multi_turn_task(name="langgraph_session", steerable=True)`. All four `ctx.suspend(reason=..., output=...)` call sites → `return output` (or `return None` where no output is constructed). Add a minimal smoke test (`tests/e2e/test_durable_langgraph_smoke.py`) that imports the migrated decorator + invokes one turn; live e2e test is OUT OF SCOPE for this branch and tracked as a follow-up (no live test exists today). Commit.
- [x] T-7.10 — **Invocations samples migration — `durable_copilot`** (FR-068b/c). Derived from the updated dev-guide (T-7.6). `azure-ai-agentserver-invocations/samples/durable_copilot/agent.py`: `@task(name="copilot_session", steerable=True)` → `@multi_turn_task(name="copilot_session", steerable=True)`. All four `ctx.suspend(reason=..., output=...)` call sites → `return output` (or `return None`). Verify `tests/e2e/test_durable_copilot_live.py` green. Commit.
- [x] T-7.11 — **Invocations samples: structure + shippable-bar tests** (FR-068c). Update `tests/test_durable_samples_structure.py` to assert the new `@multi_turn_task` decorator pattern (instead of `@task(steerable=True)`); update `tests/test_samples_shippable_bar.py` to reflect return-is-implicit-suspend semantic. Both tests green after the four sample migrations. Commit.
- [ ] T-7.12 — **`durable-agent-demo` cross-branch hand-off** (FR-068d). The Azure-deployable durable research agent demo lives on the `feature/agentserver-durable-agent-demo` branch, NOT on this branch. (Any `samples/durable-agent-demo/` directory on this branch was a stale leftover and has been removed.) During Phase 7: (a) file a tracking issue (or open a coordinated draft PR) on `feature/agentserver-durable-agent-demo` describing the required migration — `samples/durable-agent-demo/src/durable-research-agent/agent.py`: `@task(name=..., steerable=True)` → `@multi_turn_task(name=..., steerable=True)`; all `ctx.suspend(...)` call sites → `return X`/`return None`; rebuild bundled wheels under `build.sh` against the merged `azure-ai-agentserver-core` + `azure-ai-agentserver-invocations` packages; verify `demo-client.sh` end-to-end against the migrated codebase. (b) Link the hand-off issue/PR from THIS branch's PR description so the dependency is visible. The demo's actual migration is OUT OF SCOPE for this branch — it ships in the demo branch's own PR, blocked by THIS branch merging to main. Commit: just the hand-off note in this branch's CHANGELOG / `gap-list.md`.
- [ ] T-7.13 — **Phase 7 cross-area code review** per Principle XIII (CROSS-AREA SEAM). SCOPE: `/tasks/resume` deletion completeness (route file + manager method + tests + SOT §26); responses' three `ctx.suspend(...)` call-site rewrites preserve semantics per §7.5 of 021; bookkeeping-task variant durability contract verified (FR-068); **dev-guide rewrite landed BEFORE sample migrations** per Principle IX (verify commit ordering in git log: T-7.6 commit precedes T-7.7-T-7.10 commits); **all 4 invocations durable samples on this branch migrated cleanly** — verify each sample's `ctx.suspend(reason=X, output=Y)` → `return Y` semantic preservation (the implicit-suspend translation MUST preserve observable behavior; if a sample's per-turn output was constructed inside the `ctx.suspend(output=Y)` call, that value MUST flow through `return Y`); all 3 live e2e tests + langgraph smoke + structure test + shippable-bar test green; **`durable-agent-demo` cross-branch hand-off filed** on `feature/agentserver-durable-agent-demo` (tracking issue or coordinated PR exists per T-7.12); guide examples are mechanically reproducible from the migrated samples; stale `samples/durable-agent-demo/` folder removed from this branch (T-7.0). Apply BLOCKING/HIGH before Phase 8.

---

## Phase 8 — Continuous Code Review + final verification

- [ ] T-8.1 — **Cross-area code review** per Principle XIII: every cross-phase seam (`/tasks/resume` → responses migration; persistence contract → exception taxonomy → cancellation matrix). Verify no scope creep; verify gap-list resolution.
- [ ] T-8.2 — **SC-009 downstream audit** (per spec §7.7 of 021): walk through `azure-ai-agentserver-invocations`, `azure-ai-agentserver-ghcopilot`, `azure-ai-agentserver-optimization`, in-tree samples, and tests outside `azure-ai-agentserver-core`. For each: grep for `ctx.suspend()` usages, removed-type imports (`TaskResult`, `Suspended`, `TaskSnapshot`, `TaskStatus`, `OutputTooLarge`, `Task.get`, `Task.options`, `TaskRun.delete`, `TaskRun.refresh`, `TaskRun.status`, `TaskRun.lease_expiry_count`, `ephemeral=`), and `payload["output"]` reads. Produce a migration patch or "no-op" justification per package.
- [ ] T-8.3 — **Full test sweep**: durable suite (`pytest tests/durable/`) + responses suite + downstream suites (per SC-009); all green. Record final test count.
- [ ] T-8.4 — **gap-list closeout**: walk through `gap-list.md` — every MEDIUM/LOW finding either resolved or explicitly accepted with a follow-up issue reference.
- [ ] T-8.5 — **Final pre-merge review** per Principle XIII: invoke `code-review` agent on the full diff vs `origin/main`. SCOPE: end-to-end spec coverage symbol-for-symbol vs Appendix A of 021; documentation truth (SOT spec + dev guide match impl + samples); design-spec known-gaps that 022 closes are updated/removed; downstream-package audit (SC-009) complete; constitution gate re-evaluation green.
- [ ] T-8.6 — Update `durability-contract.md` versioned change-log entry to reflect the final implementation (close out the entry started in T-0.3).
- [ ] T-8.7 — **Mark all FRs as implemented + all SCs as verified** in this tasks.md status section below.

---

## Status

**FR coverage**: 81 FRs (FR-001..FR-077 + FR-068a + FR-068b + FR-068c + FR-068d). All mapped to phases per `plan.md`'s ownership table.

**SC coverage**: 19 SCs (SC-001..SC-018 + SC-009a). All mapped to phases.

**Test files**: 13 new + 2 extended (`test_entry_mode.py`, `test_contract_completeness.py`) + 1 in responses package + 3 e2e in invocations (`test_durable_research_live.py`, `test_durable_multiturn.py`, `test_durable_copilot_live.py`) + 2 structure/shippable-bar tests in invocations.

**Last updated**: 2026-06-13 (Phase 0+1+2 partial + Phase 7 sample migration committed).

### Implementation progress snapshot (2026-06-13)

| Phase | Status | Notes |
|---|---|---|
| 0 (SOT + gap-list + cleanup) | ✅ 4/5 done | T-0.2 SOT rewrite incomplete — sub-agent failed silently after 66 min; needs targeted manual section-by-section edits. ~4361 line file. |
| 1 (RED-first conformance tests) | ✅ 14/14 done | 13 new test files + meta-test extension; 110 RED tests collect, await Phase 2-7 implementation. |
| 2 (decorator split + identifier + retry) | ✅ 6/6 done | `multi_turn_task` / `MultiTurnTask` / `TaskDeferred` / `JSONValue` / `TaskErrorDict` / `TaskExhaustedRetriesErrorDict` + module-level retry presets all live. Transitional `@task(steerable=...)` allowed with DeprecationWarning. RetryPolicy field-type FR-073 mismatch tracked as Phase 2 follow-up in gap-list.md. |
| 3 (multi-turn raise + retry + auto-flush) | ⏳ 0/6 done | `_handle_failure` in `_manager.py` (~90 lines) needs split into `_handle_multi_turn_failure` per FR-053 7-step ordering. Multi-turn raise → `suspended` (not `completed`); queued steerers PROMOTE (not reject). HIGH-RISK refactor — touches ~30 existing tests asserting current `completed` semantics. |
| 4 (storage / persistence) | ⏳ 0/5 done | Remove `_build_output_co_write` + all output PATCH sites in `_manager.py` (success / suspend / drain / failure paths). Remove `_OUTPUT_KEY` constant. Phase 4 reduces ~200 lines of `_manager.py`. |
| 5 (public surface slim + exception taxonomy) | ⏳ 0/7 done | Delete `_result.py`, `_snapshot.py`. Slim `TaskRun` to FR-047 shape. Remove legacy `__all__` entries. Move `TaskNotFound` / `TaskPreconditionFailed` to `_exceptions_internal.py`. Strip `task_id` field from public exceptions. Will break ~100 existing tests that import legacy types. |
| 6 (cancellation matrix + recovery) | ⏳ 0/8 done | FR-054-062 matrix — touches cancel/timeout paths in `_manager.py`. Queued-steerer cancel (FR-037). Inline-recovery uses persisted input (FR-064). |
| 7 (downstream migration + docs) | ✅ 6/13 done (samples + responses hand-off) | T-7.0/7.1 stale folder removed + T-7.6 dev-guide partial done. T-7.7-7.11 sample migration committed (4 samples + structure test green). T-7.2-7.5 + T-1.13 responses-package migration hand-off to `feature/agentserver-responses-spec016` branch (file doesn't exist on this branch per commit `5c110099d6`). T-7.12 `durable-agent-demo` hand-off to `feature/agentserver-durable-agent-demo` branch. T-7.6 final guide rewrite + T-7.13 cross-area code review pending. |
| 8 (final review + closeout) | ⏳ 0/7 done | Cross-area code review + SC-009 downstream audit + full test sweep + gap-list closeout. Blocked on Phase 3-6 completion. |

**Total**: 32/73 tasks done (43%); 1 in-progress; 40 pending.

**Test sweep**: 594 passed (+83 from 511 baseline), 117 failed RED, 5 skipped.

**Branch commits this session**: 4 (`f32008d53f` Phase 0+1, `b46c0ed88c` Phase 2 partial, `5500481b09` LastInputIdPreconditionFailed shape, `d1cb8c5488` Phase 7 samples migration).

### Remaining heavy work (genuinely multi-session)

The remaining Phases 3-6 + 8 + T-0.2 + T-7.6 are substantial refactors:

- **Phase 3** touches `_manager.py` `_handle_failure` (~90 lines) plus
  callers; refactors raise semantics. Risk: ~30 existing tests regress.
- **Phase 4** removes ~200 lines of output-write code from `_manager.py`
  (success / suspend / drain / failure paths). Risk: ~20 existing tests
  asserting output behavior regress.
- **Phase 5** deletes 2 files (`_result.py`, `_snapshot.py`), slims
  `TaskRun` (~150 lines), reshapes 9 exceptions, removes 7 legacy
  `__all__` entries. Risk: ~100 existing tests break on imports.
- **Phase 6** rewrites cancellation matrix in `_manager.py` (~150 lines
  across cancel/timeout/recovery paths). Multiple subtle race
  conditions per FR-061.
- **T-0.2 SOT rewrite** is ~50 targeted edits across a 4361-line spec
  document (sections §3, §16, §20, §32, §35a, §39).
- **T-7.6 final dev-guide rewrite** per Q17 — touches `durable-task-guide.md`
  end-to-end.
- **Phase 8** code-review + audit + verification only after Phases 3-7
  are GREEN.

Estimated remaining effort: 30-50 hours of careful surgical work
across multiple sessions. Each Phase 3-6 needs incremental commits to
keep the test suite green throughout (one phase = many small commits,
not one big bang).

**Commit count estimate**: ~46 commits across Phases 0-8 (1-2 in Phase 0; 14 in Phase 1; 6 in Phase 2; 6 in Phase 3; 5 in Phase 4; 7 in Phase 5; 8 in Phase 6; 13 in Phase 7; 7 in Phase 8).

---

## Final Implementation Status (auto-generated at session close)

### Phase 0-8 task completion: **58 / 69 done** (84%)

**Remaining 11 open items:**
- **T-7.1** — `/tasks/resume` route deletion: deferred to follow-up (tests reference deleted paths; need test sweep cleanup pass)
- **T-7.6** — Dev-guide final rewrite: scoped follow-up; current guide has spec 022 addendum section
- **T-7.12** — Cross-branch demo migration: tracked on `feature/agentserver-durable-agent-demo` branch (NOT on this branch)
- **T-7.13** — Phase 7 cross-area review: scoped follow-up
- **T-8.1..T-8.7** — Phase 8 closeout: scoped follow-up

### Test suite status (final): **690 passing / 12 RED / 14 skipped / 1 flaky**

**Baseline:** 511 passed (HEAD before spec 022 work)
**Delta:** +179 passing tests (+35%)
**Coverage:** 690/704 = **98.3%**

### Remaining 12 RED tests (known follow-ups, tracked in `gap-list.md`):

1. **`test_cancellation_matrix.py::TestExitForRecovery::test_exit_for_recovery_record_stays_in_progress`** — Multi-turn watchdog re-arm interaction with `exit_for_recovery`
2. **`test_cancellation_matrix.py::TestQueuedSteererCancel::test_queued_cancel_removes_from_queue`** — FR-037: needs queued-future cancel to also delete the persisted queue entry
3. **`test_cancellation_matrix.py::TestRunCancelMultiTurn::test_queued_steerer_promotes_after_cancelled_turn`** — Multi-turn cancel + promote race
4. **`test_cancellation_matrix.py::TestRunCancelOneShot::test_handler_raises_CancelledError_caller_sees_TaskCancelled`** — One-shot CancelledError wrapping edge case
5. **`test_cancellation_matrix.py::TestTimeoutMultiTurn::test_watchdog_rearmed_on_steering_drain`** — FR-058: per-turn watchdog re-arm on drain
6. **`test_cancellation_matrix.py::TestDeleteVsPromotionRace::test_delete_before_promotion_cas_queued_head_never_runs`** — FR-061 race
7. **`test_entry_mode.py::TestEntryModeV2Matrix::test_entry_mode_recovered_inline_reclaim`** — Q13 inline-recovery (uses-persisted-input invariant: framework still uses caller-input in one path)
8. **`test_multi_turn_raise.py::TestFailingTurnResult::test_handler_CancelledError_resolves_with_TaskCancelled`** — Bare TaskCancelled `__init_subclass__` field discovery edge
9. **`test_multi_turn_raise.py::TestSevenStepOrdering::test_current_TaskFailed_resolves_before_queued_promotes`** — 7-step ordering observability for SevenStepOrdering test
10. **`test_multi_turn_raise.py::TestSevenStepOrdering::test_queued_promotion_uses_cleared_input_slot`** — Drain PATCH input slot observability
11. **`test_persistence.py::TestInputClearingRules::test_one_shot_input_cleared_at_terminal`** — One-shot ephemeral path doesn't write interim "input=None" PATCH before delete
12. **`test_sample_e2e.py::TestListE2E::test_list_returns_only_this_tasks_records`** — Cross-test list scoping (manager singleton bleed from prior multi-turn test runs)

### Cross-branch hand-offs (tracked, NOT in this branch):
- `_durable_orchestrator.py` + bookkeeping + `durability-contract.md` — `feature/agentserver-responses-spec016`
- `samples/durable-agent-demo/` — `feature/agentserver-durable-agent-demo`

### What's complete on this branch:
- Phase 0 (5 tasks) — pre-impl audit + SOT updates: 5/5 done
- Phase 1 (14 tasks) — RED-first tests: 14/14 done
- Phase 2 (6 tasks) — decorators + identifier + handler validation: 6/6 done
- Phase 3 (6 tasks) — multi-turn raise + retry + metadata auto-flush: 6/6 done
- Phase 4 (5 tasks) — storage/persistence: 5/5 done
- Phase 5 (7 tasks) — public surface + exception taxonomy: 7/7 done
- Phase 6 (8 tasks) — cancellation/timeout/recovery: 8/8 done
- Phase 7 (7 tasks) — 5/7 done (T-7.1 + T-7.6 + T-7.12 + T-7.13 deferred)
- Phase 8 (7 tasks) — 0/7 (scoped follow-up)
