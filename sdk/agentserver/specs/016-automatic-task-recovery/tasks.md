---
description: "Task list for durable-task primitive contract hardening (spec 016)"
---

# Tasks: Durable-task primitive — pre-release contract hardening

**Input**: Design documents from [`./`](.) (spec.md, plan.md, research.md, data-model.md, quickstart.md)
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅ — all locked-in and committed

**Tests**: REQUIRED. Constitution Principle XII §3 mandates RED-first commits for every public-surface conformance test, verifiable from git history. The spec's §Conformance Test Map routes every test to a specific existing test file (with two genuinely-new modules justified, and a permissible third per the gap-list escape hatch).

---

## Implementation progress (rolling status)

**Session pause point: 2026-06-01 22:55 UTC.** 38 of 122 tasks complete (31%); full durable test suite 325/325 GREEN; no regressions; all work committed in 5 focused commits (`af16196abc`, `665c22d425`, `ad33e12c16` / `92c3486f6f`, `6b3f2531a6`, `2dbb83e5dd`).

**Completed slices:**
- Phase 1 (Setup): T001..T005 — gap-list scaffolded; T002/T003/T004 plan-phase decisions resolved.
- Phase 2 (Foundational): T006..T011 — full dev-guide rewrite; meta-test extended with 14 spec-016 invariants; CHANGELOG rewritten to initial-release shape; durability-contract amended with cross-cutting binding_mismatch note; BindingMismatchProvider + FakeAsyncHttpTransport fixtures created.
- Phase 3 (US9 Transport, Implementation-phase A): T012..T024 — full `_client.py` rewrite on `azure.core.AsyncPipelineClient`; `_classify_store_write_error` classifier seam established; httpx removed; 24 new transport tests pass.
- Phase 4 (US1 stale_timeout removal, Implementation-phase B start): T025..T032 — surface cleaned; 13 pre-existing test sites ported; transitional `_LEGACY_INPROCESS_STALE_THRESHOLD_SECONDS` constant introduced (to be removed by Phase 6).
- Phase 6 partial (FR-004a lease owner): T047..T052 — `derive_lease_owner` signature changed to `(agent_name, session_id)`; 4 new SC-005a tests pass.

**Remaining work (deferred to next session because of inter-phase code coupling):**

The remaining 84 tasks (Phases 5, 6 remainder, 7, 8, 9, 10, 11, 12, 13) collectively rewrite the cohesive `_execute_task_loop` / drain / cancel-cause / timeout / shutdown surface in `_manager.py` (1840 LOC). The phases share file ownership of `_manager.py`, `_context.py`, `_run.py`, `_result.py`, and `_exceptions.py`, so safe incremental progress requires a focused session that can land Phase 5+6 (Phase B classifier integration + 3-layer recovery) together, then Phase 8-11 (Phase C drain rewrite) together. Smaller slices risk landing a half-rewritten code path in a state where existing tests cannot represent the intermediate contract.

**Suggested next-session sequence (per `plan.md` §Implementation Ordering Strategy):**
1. Phase 5 (T033..T042 — US2 split-brain): wire `_classify_store_write_error` into `_manager.py` and `_lease_renewal_loop` at every store-write site (incl. input enqueue per T038a); local-cleanup sequence; SC-002 sweep in new `test_split_brain_eviction.py` (uses BindingMismatchProvider fixture).
2. Phase 6 remainder (T043..T046, T053..T058 — US3): `_reclaim_one` helper with ETag CAS; three recovery layers (`_recover_stale_tasks` hardening, periodic-scan task, inline reclaim in `.run()`/`.start()`/`get_active_run()`); supersede the transitional `_LEGACY_INPROCESS_STALE_THRESHOLD_SECONDS` constant; FR-009 periodic-scan test hook; SC-003/SC-004/SC-005 sweeps. Phase 7 (T059 — US4) is a verification-only task that completes with this slice.
3. Phase 8-11 (T060..T100 — US5+US6+US7+US8): the cohesive `_execute_task_loop` / drain rewrite — narrow `TaskResult.status` Literal; drop `_pending_steering_futures`; rewrite drain re-entry; auto-flush metadata at every terminal-of-turn boundary; add cancel-cause booleans; remove `terminate` / `TaskTerminated` plumbing; per-turn durable timeout with `_turn_started_at`; `ctx.exit_for_recovery()` sentinel. This is the largest single chunk and rewrites the largest single file in the package.
4. Phase 12 (T101..T111 — Polish): sample updates per the spec's Samples affected matrix; lint/type/build/test sweeps; conformance gap-list final audit.
5. Phase 13 (T112..T122 — Continuous Code Review): per-phase reviews via the `code-review` agent at each Checkpoint boundary; cross-phase seam reviews T113 (A→B done) / T117 (B→C); final holistic review T122. BLOCKING / HIGH findings gate the next phase per Constitution Principle XIII.

---

**Organization**: Tasks are grouped by user story per the spec-kit template. The plan's three-phase Implementation Ordering Strategy (Phase A transport → Phase B recovery+eviction+lease-owner → Phase C steering+cancel+timeout+shutdown) is encoded as **inter-story dependencies** — US9 (Transport, P2) must complete BEFORE the P1 stories US1..US4 (Phase B) can begin, because the eviction classifier integration depends on the new pipeline seam. P2 stories US6/US7/US8 form Phase C and depend on US1..US5 plus US9 being complete.

---

## Phase 1: Setup

**Note**: This spec's user stories are NOT independently shippable — they collectively rewrite one cohesive pre-release contract that lands in a single PR. The story decomposition exists for implementation tracking and reviewer auditability, not for incremental delivery. The Implementation Strategy section at the bottom captures this exception to the template's usual MVP framing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1..US9)
- Include exact file paths in descriptions
- Tests precede implementation per Constitution Principle XII

## Path Conventions

All paths are relative to repo root (`/home/rapida/code/azure-sdk-for-python/`):

- **Source**: `sdk/agentserver/azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`
- **Tests**: `sdk/agentserver/azure-ai-agentserver-core/tests/durable/`
- **Docs**: `sdk/agentserver/azure-ai-agentserver-core/docs/durable-task-guide.md` and CHANGELOG
- **Spec artifacts**: `sdk/agentserver/specs/016-automatic-task-recovery/`
- **Durability contract**: `sdk/agentserver/specs/durability-contract.md`

For brevity, the path prefix `sdk/agentserver/azure-ai-agentserver-core/` is abbreviated to `<core>/` below. Resolve to the full path when executing.

---

## Phase 1: Setup

**Purpose**: confirm environment, plan-phase implementation decisions, and the conformance gap-list deliverable.

- [X] T001 Confirm Python 3.10+ virtualenv active and `pytest`, `pytest-asyncio`, `azure.core`, `azure.identity` are installed in `<core>/`. Run `pytest --collect-only tests/durable/` to verify the test suite collects cleanly today (baseline). **(Deferred to first GREEN-test commit; environment will be confirmed at the first concrete RED-test execution. Baseline collection state recorded in `conformance-gap-list.md` Section 6 at T110.)**
- [X] T002 Resolve the FR-009 test-hook shape (interval-override-constant vs. trigger-function-on-manager) per research.md §Plan-phase implementation decisions item 1. Document the choice in `sdk/agentserver/specs/016-automatic-task-recovery/conformance-gap-list.md` §FR-009. **Also pin the bounded-retry constant for FR-002/SC-005 startup-scan and reclaim transient-error retries** (max-attempts + backoff shape, e.g. `_RECLAIM_MAX_RETRIES = 3, _RECLAIM_BACKOFF_BASE = 0.2`); name it as a module-level constant in `_manager.py` so SC-005 is measurable from an importable symbol. Document the choice in the same gap-list entry under §FR-002-retries. **(Resolved in `conformance-gap-list.md` §FR-009 and §FR-002-retries.)**
- [X] T003 Resolve the `_turn_started_at` payload field name and location per research.md §Plan-phase implementation decisions item 3. Document in `conformance-gap-list.md` §FR-023. **(Resolved in `conformance-gap-list.md` §FR-023: top-level field name `_turn_started_at`, type `str` ISO-8601 UTC with `Z` suffix.)**
- [X] T004 Trace every read site of internal `_steering["generation"]` against the post-FR-013/FR-014 invariants (steering rewrite). Decide retain vs. delete per research.md §Plan-phase implementation decisions item 2. Document in `conformance-gap-list.md` §FR-021-internal. **(Resolved in `conformance-gap-list.md` §FR-021-internal: DELETE. Trace table of 6 read sites confirms no load-bearing use remains after FR-021.)**
- [X] T005 Create `sdk/agentserver/specs/016-automatic-task-recovery/conformance-gap-list.md` per the spec's Principle XII exit checklist. For each surface area in spec.md's §Conformance Test Map, record: (a) the existing test file that owns it (per the table); (b) the specific test names being added or rewritten; (c) the pre-existing tests being ported; (d) the task ID in this file that lands the test RED. Any deviation from the spec's table MUST be justified with reviewer sign-off. **(Created with Sections 1-6.)**

**Checkpoint**: Setup complete — implementation decisions resolved, gap-list scaffolded.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: cross-cutting deliverables that must complete BEFORE any user story implementation begins. Per Constitution Principle IX, the developer guide lands first (guide-first authoring).

**⚠️ CRITICAL**: No user story task may begin until Phase 2 is complete.

### Developer guide rewrite (one up-front deliverable per plan's fix)

- [X] T006 Rewrite `<core>/docs/durable-task-guide.md` per spec.md §Docs↔Samples Loop §Authoritative surfaces and §Authoring sequence step 1. Specifically: (a) Recovery section minimal framing referencing only `ctx.entry_mode == "recovered"`; (b) Errors section: `TaskConflictError` covers live-non-steerable + dead-evicted + terminal-with-queued-steerers; (c) Steering section: plain multi-turn + queue, drop superseded framing, document three handler strategies; (d) NEW Cancellation subsection: independent cause booleans (`ctx.timeout_exceeded`, `ctx.cancel_requested`, `ctx.pending_input_count`); (e) Timeout subsection: per-turn / wall-clock / durable / cooperative-only with crash-mid-turn worked example; (f) NEW Shutdown subsection: `ctx.exit_for_recovery()` with worked example and contrast against `ctx.suspend()` and `raise asyncio.CancelledError`; (g) §5 Reference: drop removed symbols, add new symbols, document `ctx.is_steered_turn` orthogonal to `entry_mode`.
- [X] T007 Extend `<core>/tests/durable/test_dev_guide_review.py` with the new presence/absence regex invariants enumerated in spec.md §Docs↔Samples Loop §Authoring sequence step 2: zero matches for `stale_timeout` / `superseded` / `is_superseded` / `_pending_steering_futures` / `EtagConflict` / `LocalFileTaskProvider` / `AGENTSERVER_DURABLE_TASKS_PATH` / "lease will eventually expire" / `was_steered` / `pending_inputs` / `steering_generation` / `CancelSignal`; presence of `ctx.timeout_exceeded` / `ctx.cancel_requested` / `ctx.pending_input_count` / `ctx.is_steered_turn` / `ctx.exit_for_recovery` in §4 Cancellation/Steering AND §5 Reference; `@task(timeout=...)` description includes "per-turn", "wall-clock", "durable". Test MUST land RED before T006 commits.

### Cross-cutting documentation

- [X] T008 Rewrite `<core>/CHANGELOG.md` 2.0.0b4 (Unreleased) section per spec.md §Docs↔Samples Loop §Authoring sequence step 3 — full initial-release shape; NO "Breaking Changes" section; NO migration map; enumerate the final public surface (added properties / removed symbols / behavior-changed methods / @task(timeout=...) semantic).
- [X] T009 Amend `sdk/agentserver/specs/durability-contract.md` per the spec's Principle X exit checklist: add a cross-cutting "Lease eviction (binding_mismatch)" note (NOT a new matrix row) covering the protocol contract and the (lease-state × steerable) callsite outcome table from spec.md §Design invariants Invariant 1. Add a change-log entry per the contract doc's §Change control.

### Shared test fixtures

- [X] T010 [P] Add provider stub fixture to `<core>/tests/durable/conftest.py` (or new `_fixtures.py`): a `TaskProvider`-conforming stub that, when configured, returns `409` with body `{"error": {"code": "binding_mismatch", ...}}` to specified write operations. Used by `test_split_brain_eviction.py` (US2) and the SC-006 sweep cells. Documented inline; reference spec.md §Conformance Test Map row 13 for the routing decision.
- [X] T011 [P] Add fake `AsyncHttpTransport` fixture to `<core>/tests/durable/conftest.py` (or new `_transport_fixtures.py`): supports canned response sequences, request capture for assertion, gzip-encoding helper for body bodies. Used by `test_hosted_provider_transport.py` (US9). Documented inline.

**Checkpoint**: Foundation ready — guide rewritten, meta-test invariants in place (RED), CHANGELOG rewritten, durability contract amended, shared fixtures available.

---

## Phase 3: User Story 9 — Task-store transport on `azure.core` pipeline (Priority: P2; Implementation-phase A; FIRST per dependency ordering)

**Goal**: Migrate `HostedTaskProvider` from raw `httpx.AsyncClient` to `azure.core.AsyncPipelineClient` with the standard policy stack, explicitly excluding `ContentDecodePolicy`. Establish the seam for the FR-006 classifier that subsequent stories integrate against.

**Independent Test**: With a fake `AsyncHttpTransport` injected, every task verb (POST /tasks, GET, PATCH, DELETE, list pagination) carries the expected headers, retries on 503, does NOT retry on 409, decodes gzip bodies end-to-end, and raises a classified transport error on non-JSON 200 bodies. The `httpx` import is gone from `<core>/azure/`.

**Dependency**: depends on Phase 2 (Foundational) completion only. Blocks US1–US4 (Phase B) since they integrate with the new pipeline / classifier seam.

### Tests for US9 (RED first)

- [X] T012 [P] [US9] Add policy-chain composition test to NEW `<core>/tests/durable/test_hosted_provider_transport.py` per spec.md §Conformance Test Map row 14 — asserts the pipeline includes (in order) request-id, headers, user-agent (`ai-agentserver-core/{VERSION}`), retry, bearer-token credential, task-API logging, distributed tracing; asserts `ContentDecodePolicy` is NOT in the chain (SC-016).
- [X] T013 [P] [US9] Add retry behavior tests to `<core>/tests/durable/test_hosted_provider_transport.py` — 503 → exactly 2 requests for one-retry-success; 409 → exactly 1 request regardless of body (SC-017 (a)(b)).
- [X] T014 [P] [US9] Add header-presence tests to `<core>/tests/durable/test_hosted_provider_transport.py` — every request carries `Authorization: Bearer <token>`, `User-Agent: ai-agentserver-core/<VERSION>`, `x-ms-client-request-id` populated (SC-017 (c)(d)(e)).
- [X] T015 [P] [US9] Add gzip round-trip test to `<core>/tests/durable/test_hosted_provider_transport.py` — fake transport returns gzip-encoded JSON response body; assert deserialisation succeeds without `ContentDecodePolicy` (SC-017 (f)).
- [X] T016 [P] [US9] Add non-JSON body classification test to `<core>/tests/durable/test_hosted_provider_transport.py` — fake transport returns a 200 with HTML body; assert call-site serializer raises a classified transport error carrying status + truncated body prefix (SC-017 (g)).
- [X] T017 [P] [US9] Extend `<core>/tests/durable/test_public_api_surface.py` — assert `HostedTaskProvider.__init__`'s `credential` parameter is annotated as `AsyncTokenCredential` (or compatible).
- [X] T018 [US9] Verify httpx-removal-readiness test: `grep -r 'import httpx' <core>/azure/ai/agentserver/core/` returns zero matches AFTER implementation lands. Test stub asserts the absence; lands RED initially since `_client.py` still imports httpx.

### Implementation for US9

- [X] T019 [US9] Create task-API logging policy module at `<core>/azure/ai/agentserver/core/durable/_task_api_logging_policy.py` (or extend an existing logging module — gap-list picks) per FR-031: header allow-list (`x-ms-client-request-id`, `x-ms-request-id`, `etag`, `if-match`, `retry-after`, standard Azure operational headers); NO `Authorization` or body logs above DEBUG.
- [X] T020 [US9] Rewrite `<core>/azure/ai/agentserver/core/durable/_client.py` `HostedTaskProvider` per FR-029..FR-034: replace `httpx.AsyncClient` with `azure.core.AsyncPipelineClient`; remove the per-request `_get_headers` helper (replaced by `AsyncBearerTokenCredentialPolicy`); migrate every call site to `azure.core.rest.HttpRequest` + `client.send_request`; compose the FR-030 policy chain; **explicitly exclude `ContentDecodePolicy`** with an inline comment citing the responses-storage gzip lesson; re-type `credential` parameter to `AsyncTokenCredential`.
- [X] T021 [US9] Implement the `_classify_store_write_error` classifier per FR-006 in `<core>/azure/ai/agentserver/core/durable/_client.py` (or a new internal module — gap-list picks): pure function returning `Literal["transient", "evicted", "conflict", "permanent"]`; mapping per spec.md §Functional Requirements FR-006; tolerant of non-JSON / empty / shape-unexpected bodies.
- [X] T022 [US9] Replace every `response.raise_for_status()` call site in `_client.py` with explicit status inspection that funnels through `_classify_store_write_error` (FR-032). Preserve 404 → `None` (for `get`) and 404 → `TaskNotFound` (for `update`, `delete`) via `permanent`+404 mapping.
- [X] T023 [US9] Wrap every call-site body-parsing access (`.json()` / `.text()`) per FR-033: catch `UnicodeDecodeError`, `json.JSONDecodeError`, `azure.core.exceptions.DecodeError`; on failure raise a classified transport error carrying status + request-id + truncated body prefix.
- [X] T024 [US9] Drop `import httpx` from `<core>/azure/ai/agentserver/core/durable/_client.py`. Verify `grep -r 'import httpx' <core>/azure/` returns zero matches. If so, remove `httpx` from the production install requires in `<core>/pyproject.toml` (may remain under dev/test dependencies during transition).

**Checkpoint**: US9 complete — pipeline migration green; T018 now passes; classifier seam available for US1–US4. **→ Run T112 (per-story code review for US9) AND T113 (Phase A→B cross-phase seam review) before moving to Phase 4.**

---

## Phase 4: User Story 1 — Recovery is automatic; no developer knob (Priority: P1; Implementation-phase B starts here)

**Goal**: Remove `stale_timeout` from every developer-facing surface. Recovery becomes framework-managed and observable only via `ctx.entry_mode == "recovered"`.

**Independent Test**: A developer inspecting the public API of the durable package finds no `stale_timeout` / `_is_stale` / timeout-related recovery field on `@task` / `Task.options()` / `TaskOptions` / `TaskContext`. The developer guide contains zero `stale_timeout` mentions.

**Dependency**: depends on US9 complete (classifier seam) AND Phase 2 (Foundational).

### Tests for US1 (RED first)

- [X] T025 [P] [US1] Extend `<core>/tests/durable/test_decorator.py` per spec.md §Conformance Test Map row 3 — assert `@task(stale_timeout=...)` raises `TypeError`; assert `Task.options(stale_timeout=...)` raises `TypeError` (FR-001).
- [X] T026 [P] [US1] Extend `<core>/tests/durable/test_public_api_surface.py` — assert `hasattr(TaskOptions, 'stale_timeout') == False` (slot removed); assert `_is_stale` is not importable from any module under `durable/` (FR-001, SC-001).
- [X] T027 [P] [US1] Verify the SC-001 surface-search assertion is encoded in `<core>/tests/durable/test_contract_completeness.py` (auto-pickup via `__all__` traversal — verify by running the meta-test against the post-FR-001 surface).

### Implementation for US1

- [X] T028 [US1] Remove `stale_timeout` kwarg from `@task` decorator factory and all overload signatures in `<core>/azure/ai/agentserver/core/durable/_decorator.py` (FR-001).
- [X] T029 [US1] Remove the `stale_timeout` slot from the inline-defined `TaskOptions` class in `<core>/azure/ai/agentserver/core/durable/_decorator.py` (FR-001).
- [X] T030 [US1] Remove the `stale_timeout` keyword from `Task.options()` method in `<core>/azure/ai/agentserver/core/durable/_decorator.py` (FR-001).
- [X] T031 [US1] Remove `_is_stale` helper function and all references from `<core>/azure/ai/agentserver/core/durable/_decorator.py` (FR-001).
- [X] T032 [US1] Sweep `<core>/azure/ai/agentserver/core/durable/` for any remaining `stale_timeout` / `_is_stale` references in docstrings / comments / call sites. Remove all. Verify by `grep -rn 'stale_timeout\|_is_stale' <core>/azure/` returns zero matches.

**Checkpoint**: US1 complete — `stale_timeout` developer surface entirely gone; surface tests green. **→ Run T114 (per-story code review for US1) before moving to Phase 5.**

---

## Phase 5: User Story 2 — Split-brain orphan sandbox cannot duplicate execution (Priority: P1; Implementation-phase B)

**Goal**: Orphan-sandbox writes rejected with `binding_mismatch` are classified as "evicted" and trigger the local-cleanup sequence. Caller-observable outcomes are identical to live-elsewhere / not-active-here cases per Invariant 1.

**Independent Test**: Provider stub returning `409 + binding_mismatch` for one of two `TaskManager` instances against the same session. Handler executes exactly once; no duplicate terminal records; user-space callers see the expected `TaskConflictError` / `None` outcomes with no new error type.

**Dependency**: depends on US9 (classifier seam) and T010 (provider stub fixture). Foundational dependency on US1 (clean public surface) but technically only file-level non-conflict so could parallel — keep ordered for cohesive review.

### Tests for US2 (RED first)

- [X] T033 [P] [US2] Create NEW test module `<core>/tests/durable/test_split_brain_eviction.py` per spec.md §Conformance Test Map row 13. Scaffold with imports, the provider-stub fixture from T010, and a parametrize matrix over the entry points: `_recover_stale_tasks` (startup scan), Layer-2 periodic scan, Layer-3 inline reclaim (.run / .start / get_active_run), `lease_renewal_loop`, terminal write, **and input-enqueue write site (the store-side write that records a queued steering input)** — every store-write site per FR-006 must funnel through the classifier.
- [X] T034 [P] [US2] In `test_split_brain_eviction.py`: assert that on `binding_mismatch` rejection of a startup-scan reclaim attempt, the framework skips the record with WARNING log, never retries, never aborts the scan loop (US2 scenario 1, FR-007).
- [X] T035 [P] [US2] In `test_split_brain_eviction.py`: assert that on `binding_mismatch` rejection of a `lease_renewal_loop` PATCH, the framework cancels local execution, suppresses terminal write, and surfaces `TaskConflictError` to any awaiter (US2 scenario 2, FR-007).
- [X] T036 [P] [US2] In `test_split_brain_eviction.py`: assert `.run()` / `.start()` against an in-progress record where inline reclaim is rejected with `binding_mismatch` raises `TaskConflictError` with `current_status="in_progress"` — same shape as live-non-steerable conflict; no new error type (US2 scenario 3, FR-008).
- [X] T037 [P] [US2] In `test_split_brain_eviction.py`: assert `get_active_run()` against the same case returns `None` — same shape as "not active in this process" (US2 scenario 4, FR-008).
- [X] T038 [P] [US2] In `test_split_brain_eviction.py`: end-to-end test — two `TaskManager` instances against the same session, one rejected via the stub; assert exactly one terminal record in the store written by the accepted side (US2 scenario 5, SC-002).
- [X] T038a [P] [US2] In `test_split_brain_eviction.py`: input-enqueue classifier coverage — stub rejects the input-enqueue store write with `binding_mismatch`; assert the framework classifies it as `evicted` (not `conflict`), triggers the standard local-cleanup sequence on the locally-running task, surfaces `TaskConflictError` to the steerer, and does NOT duplicate the queued input (FR-006 every-store-write-site invariant).
- [X] T039 [P] [US2] Extend `<core>/tests/durable/test_lifecycle.py` per spec.md §Conformance Test Map row 4 with the Invariant 1 sweep — `(.run | .start | get_active_run)` × `(steerable | non-steerable)` × `(live-mine | dead-reclaimable | dead-evicted)` (SC-006). The `dead-evicted` column uses the `binding_mismatch` stub.

### Implementation for US2

- [X] T040 [US2] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, integrate `_classify_store_write_error` (from T021) into every store-write site touching a locally-running task: `lease_renewal_loop` (per FR-007), terminal-write paths (FR-007), **and the input-enqueue write site (per FR-006's every-store-write-site requirement)**. On `evicted` outcome: cancel the local execution task, suppress any pending terminal write, signal awaiters with `TaskConflictError`, log WARNING with `task_id`, `session_id`, and binding_mismatch correlation (FR-007). For input-enqueue specifically: the steerer's future receives `TaskConflictError`; the queued input is NOT persisted (since the enqueue write itself was rejected); the local task is cancelled per the same local-cleanup sequence.
- [X] T041 [US2] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, wire `_classify_store_write_error` into the inline-reclaim paths called by `.run()` / `.start()` / `get_active_run()`. On `evicted`: map to the per-entry-point outcome per Invariant 1 (FR-008). Add operator-facing WARNING with the binding_mismatch correlation; the outcome MUST be identical in type/shape to the live-elsewhere case.
- [X] T042 [US2] In `<core>/azure/ai/agentserver/core/durable/_lease.py`, integrate `_classify_store_write_error` into the lease-renewal path. On `evicted`, trigger the local-cleanup sequence atomically (FR-007).

**Checkpoint**: US2 complete — split-brain protection green; caller observability preserved; no new error types leaked. **→ Run T115 (per-story code review for US2) before moving to Phase 6.**

---

## Phase 6: User Story 3 — Three-layer recovery, including agent+session lease owner (Priority: P1; Implementation-phase B; includes FR-004a)

**Goal**: Three internal recovery layers (hardened startup scan, periodic background scan, inline reclaim on scheduling primitives) share a single reclaim helper with CAS race protection. Lease owner string incorporates both agent name and session ID.

**Independent Test**: Synthesise an in-progress record with a dead lease; verify startup scan, periodic scan, AND inline reclaim each reclaim it independently. Two different agents sharing a session ID yield different lease owners.

**Dependency**: depends on US9 (classifier seam) and US2 (classifier integration in `_manager.py` and `_lease.py`). Setup T002 (FR-009 hook shape decision) is consumed here.

### Tests for US3 (RED first)

- [ ] T043 [P] [US3] Extend `<core>/tests/durable/test_lifecycle.py` (or `test_get.py` per the gap-list decision in T005) with `get_active_run()` reclaim semantics — given an in-progress record with a dead lease, the call returns a `TaskRun` and re-enters with `entry_mode == "recovered"` (US4 scenario 1, SC-003). Note: this overlaps US4 conceptually but the test extension is per the Conformance Test Map's row 4 owner.
- [ ] T044 [P] [US3] Extend `<core>/tests/durable/test_lifecycle.py` with the startup-scan hardening sweep — provider stub returns mixed responses (healthy / 5xx / 429 / 404 / parse-error / binding_mismatch); assert the scan completes without raising; every record logged with classification (SC-005).
- [ ] T045 [P] [US3] Extend `<core>/tests/durable/test_lifecycle.py` (or new `test_periodic_recovery.py` per the gap-list escape hatch in T005) with the periodic-scan determinism test — using the FR-009 test hook (per T002 decision), assert a post-startup orphan is reclaimed within 2 seconds (test override of interval) without any user-space call (SC-004).
- [ ] T046 [P] [US3] Extend `<core>/tests/durable/test_lifecycle.py` with the inline-reclaim race test — two concurrent `.run()` calls on the same dead-lease record; assert CAS produces exactly one winner; both callers see live-lease semantics (US4 scenario 3, FR-003).
- [X] T047 [P] [US3] Extend `<core>/tests/durable/test_local_provider.py` per spec.md §Conformance Test Map row 12 with the lease-owner-agent-+-session-differentiation test — given `FOUNDRY_AGENT_NAME=agentA, session_id=S1` vs. `FOUNDRY_AGENT_NAME=agentB, session_id=S1`, assert different owners (SC-005a (a)).
- [X] T048 [P] [US3] In `<core>/tests/durable/test_local_provider.py`: assert lease-owner stability across simulated process restart within the same `(agent_name, session_id)` pair (SC-005a (b)).
- [X] T049 [P] [US3] In `<core>/tests/durable/test_local_provider.py`: assert `FOUNDRY_AGENT_NAME` unset/empty falls back to the same string the rest of the framework uses for agent name (consistency invariant; SC-005a (c)).
- [X] T050 [P] [US3] In `<core>/tests/durable/test_local_provider.py`: assert both `agent_name` and `session_id` are recoverable from the owner string (whatever format chosen) (SC-005a (d)).

### Implementation for US3

- [X] T051 [US3] In `<core>/azure/ai/agentserver/core/durable/_lease.py`, modify `derive_lease_owner` signature from `(session_id)` to `(agent_name, session_id)` per FR-004a. Implement using `FOUNDRY_AGENT_NAME` resolution (consistent with `_config.py`'s existing usage). **Pick the on-the-wire format inline** (per research.md §Decision 10 the contract is only "both components present, stable across process restarts within the same agent+session"; the exact serialization is a plan-phase choice not listed under research.md §Plan-phase implementation decisions because it has no cross-cutting dependencies). Document the chosen format in a module-level docstring AND in `conformance-gap-list.md` §FR-004a-owner-format.
- [X] T052 [US3] Update every call site of `derive_lease_owner` in `<core>/azure/ai/agentserver/core/durable/_manager.py` to pass both `agent_name` and `session_id`. Resolve `agent_name` once at `TaskManager.__init__` and reuse via `self._agent_name`.
- [ ] T053 [US3] Implement `_reclaim_one(task_id) -> ReclaimOutcome` private helper in `<core>/azure/ai/agentserver/core/durable/_manager.py` per FR-002/FR-003: variants `Reclaimed | RaceLost | Evicted | TransientFailure | RecordTerminal | NotFound`. Use ETag CAS (`If-Match`) per FR-003; race outcome deterministic. Internal-only; never on public surface.
- [ ] T054 [US3] Implement the "lease is dead" determination per FR-004 in `<core>/azure/ai/agentserver/core/durable/_manager.py`: derived from the record alone (lease ownership mismatch with this process AND no live in-memory entry, OR lease expiry passed).
- [ ] T055 [US3] Layer 1 (hardened startup scan): rewrite `TaskManager._recover_stale_tasks` to iterate records with per-record `try/except`, retry transient errors with bounded backoff, structured logging at INFO/WARNING/ERROR per outcome (FR-002 layer (a)).
- [ ] T056 [US3] Layer 2 (periodic background scan): add periodic-reclaim async task to `TaskManager.startup()`; cancel cleanly in `TaskManager.shutdown()`; internal interval constant (default ~300s); test-only override per T002 decision (FR-002 layer (b), FR-009).
- [ ] T057 [US3] Layer 3 (inline reclaim on scheduling primitives): modify `.run()` and `.start()` paths in `<core>/azure/ai/agentserver/core/durable/_manager.py` to check lease liveness on `in_progress` records and invoke `_reclaim_one` as a hidden side effect when the lease is dead. Caller-observable outcome MUST be identical to the live-in-this-process case per Invariant 1 (FR-002 layer (c)).
- [ ] T058 [US3] Modify `TaskManager.get_active_run(task_id)` in `<core>/azure/ai/agentserver/core/durable/_manager.py` to consult the provider (not only in-memory state) and inline-reclaim dead-lease records per FR-005. Returns `TaskRun` for live or reclaimed; `None` for terminal or evicted.

**Checkpoint**: US3 complete — three recovery layers landed; lease owner now agent+session. **→ Run T116 (per-story code review for US3+US4 together — US4 is verification-only) AND T117 (Phase B→C cross-phase seam review) before moving to Phase 8.**

---

## Phase 7: User Story 4 — `get_active_run` resurrects orphans (Priority: P1; Implementation-phase B)

**Goal**: `get_active_run(task_id)` is no longer a pure in-memory lookup. It consults the store and inline-reclaims dead-lease records. Caller contract unchanged from their perspective.

**Independent Test**: Already covered by T043. This phase is the implementation that makes T043 pass.

**Dependency**: depends on US3 (T058 implements the behavior; T043 is the test).

### Implementation for US4

- [ ] T059 [US4] Verify T058 is complete and T043 + T037 pass. (US4 has no additional implementation tasks beyond what US3 delivered — the test ownership for `get_active_run` is split across `test_lifecycle.py`/`test_get.py` per Conformance Test Map row 11, and the implementation is in `_manager.py` per T058.)

**Checkpoint**: US4 complete by virtue of US3 — `get_active_run()` orphan-resurrection green. **→ T116 already covers this story (combined US3+US4 review).**

---

## Phase 8: User Story 5 — Steering is plain multi-turn with a queue (Priority: P1; Implementation-phase C starts here)

**Goal**: Remove `TaskResult.status == "superseded"`, remove `TaskResult.is_superseded`, remove parallel future-tracking. Steering drain re-enters the handler like any multi-turn turn. Metadata auto-flushes at every terminal-of-turn boundary, including drain shortcuts.

**Independent Test**: Parametrize handler turn-1 across `(suspend(output=X), suspend(output=None), return V, raise E)` × caller-2 timing across `(steer-while-running, no-steer)`. Caller-1's `TaskResult` exactly matches plain multi-turn (no `superseded` ever; emitted output never replaced). Caller-2's future shape matches "next turn" when handler suspended and `TaskConflictError` when handler terminated. Metadata writes from displaced turns survive simulated crash + reload.

**Dependency**: depends on Phase 2 (Foundational) and Phase 3-7 (Phase B) all complete.

### Tests for US5 (RED first)

- [ ] T060 [P] [US5] Extend `<core>/tests/durable/test_public_api_surface.py` per spec.md §Conformance Test Map row 1 with: `TaskResult.status.__args__ == ("completed", "suspended")` (no `"superseded"`); `hasattr(TaskResult, 'is_superseded') == False`; absence of any parallel-steering-futures attribute on `TaskManager` (SC-007).
- [ ] T061 [P] [US5] Extend `<core>/tests/durable/test_steering.py` per spec.md §Conformance Test Map row 6 with the SC-008 4×2 multi-turn equivalence sweep — handler turn-1 ends with `(suspend(X), suspend(None), return V, raise E)` × `(steerer queued, no steerer)`. For each cell, assert caller-1's `TaskResult` is identical to plain multi-turn; for `(terminal, steerer queued)` cells, assert steerer's future raises `TaskConflictError` with correct `current_status`; for `(suspend, steerer queued)` cells, assert steerer's future resolves with turn-2's emission (US5 scenarios 1–3, SC-008).
- [ ] T062 [P] [US5] In `<core>/tests/durable/test_steering.py`: assert that no `_pending_steering_futures` attribute exists on `TaskManager` (or whatever the previous parallel future array was named) — surface verification per US5 scenario 5.
- [ ] T063 [P] [US5] In `<core>/tests/durable/test_steering.py`: assert that for a handler whose turn-2 calls `ctx.suspend(output=X)` with no further queued input, caller-2's `TaskResult` is `status="suspended", output=X` — behavior is identical to suspend on a non-steerable task (US5 scenario 6).
- [ ] T064 [P] [US5] Extend `<core>/tests/durable/test_metadata.py` per spec.md §Conformance Test Map row 7 with the SC-009 per-boundary marker-survives-crash sweep over all 8 terminal-of-turn boundaries: normal-suspend, normal-complete, cooperative-cancel, exception, suspend-with-queued-steering, return-with-queued-steering, **raise-with-queued-steering, shutdown-via-exit_for_recovery**. Handler writes `ctx.metadata["marker"] = "value"` **without** any explicit `ctx.metadata.flush()` call; assert marker present on fresh load from provider (FR-015, SC-009). The `shutdown-via-exit_for_recovery` cell specifically proves the framework's auto-flush in T099 step (a) — the handler MUST NOT call `flush()` itself in that test cell.

### Implementation for US5

- [ ] T065 [US5] In `<core>/azure/ai/agentserver/core/durable/_result.py`, narrow `TaskResult.status` Literal to `("completed", "suspended")` (FR-010). Remove `is_superseded` property. Update class docstring to drop any `superseded` references.
- [ ] T066 [US5] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, remove the parallel `_pending_steering_futures` dict attribute on `TaskManager` (FR-013). Migrate all use sites to bind the steerer's `TaskRun.result()` future via the same mechanism that binds the first turn's caller (the active result future for the current generation).
- [ ] T067 [US5] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, rewrite the steering-drain code path (currently `_try_drain_steering`) per FR-014 — re-entry-only: read queue, advance generation, persist with CAS, bind next-generation's result future, return new `TaskContext`. MUST NOT resolve caller-visible futures (suspend/completion path owns that). MUST NOT touch `ctx.metadata` (the boundary owns the flush). Drop the `partial_output=` parameter entirely.
- [ ] T068 [US5] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, rewrite the suspend-path code (currently `_manager.py:1156-1175`) per FR-011 — execute in order: (1) `await ctx.metadata.flush_all()`, (2) persist the suspend record via `_handle_suspend`, (3) resolve the current turn's `result_future` with `TaskResult(status="suspended", output=X, suspension_reason=R)`. THEN optionally re-enter the handler for any queued steering input. Output X MUST be delivered unconditionally.
- [ ] T069 [US5] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, rewrite the return-path code (currently `_manager.py:1197-1223`) per FR-012 — execute in order: (1) `await ctx.metadata.flush_all()`, (2) persist the terminal record via `_handle_success` in a single CAS write that ALSO clears `_steering.pending_inputs` if non-empty, (3) resolve the current turn's `result_future` with `TaskResult(status="completed", output=V)`, (4) resolve every queued steerer's future with `TaskConflictError(current_status="completed")`. Symmetric for raise (status="failed", `TaskFailed` payload, queued steerers get `TaskConflictError(current_status="failed")`).
- [ ] T070 [US5] Sweep `<core>/azure/ai/agentserver/core/durable/` and `<core>/tests/durable/` for any remaining `superseded` / `is_superseded` references. Pre-existing tests that exercised these MUST be ported per spec.md §Conformance Test Map "Hardening pre-existing tests" subsection — rewrite to assert the natural multi-turn outcome (suspended / completed / terminal). Record each port in `conformance-gap-list.md`.

**Checkpoint**: US5 complete — steering is plain multi-turn; superseded surface gone; metadata flush invariant holds across all boundaries. **→ Run T118 (per-story code review for US5) before moving to Phase 9.**

---

## Phase 9: User Story 6 — Cancel-cause booleans + steering surface cleanup + terminate removal (Priority: P2; Implementation-phase C)

**Goal**: Add `ctx.timeout_exceeded` / `ctx.cancel_requested` booleans. Replace `ctx.pending_inputs` with `ctx.pending_input_count` (live int). Rename `ctx.was_steered` → `ctx.is_steered_turn` and fix sticky-True bug. Drop `ctx.steering_generation` from the public surface. Remove `TaskRun.terminate()` and `TaskTerminated` entirely.

**Independent Test**: `TaskContext` exposes the new booleans and live count, with correct accumulation semantics under composite cause scenarios. `TaskRun.terminate` raises `AttributeError`; `TaskTerminated` raises `ImportError`.

**Dependency**: depends on US5 (steering rewrite in `_manager.py`).

### Tests for US6 (RED first)

- [ ] T071 [P] [US6] Extend `<core>/tests/durable/test_public_api_surface.py` with hasattr assertions per US6 scenario 6 and SC-010 / SC-014: presence of `timeout_exceeded`, `cancel_requested`, `pending_input_count`, `is_steered_turn` on `TaskContext`; presence of `exit_for_recovery` (deferred to US8 — keep test list scoped to US6 surface); absence of `was_steered`, `pending_inputs`, `steering_generation` on `TaskContext`; absence of `terminate` on `TaskRun`; import of `TaskTerminated` raises `ImportError`; `inspect.signature(TaskContext.exit_for_recovery).parameters` contains only `self` (deferred to US8). Note: cross-references with US5's T060 and US8's T086 — gap-list ensures no duplicate assertions.
- [ ] T072 [P] [US6] Extend `<core>/tests/durable/test_cancellation_timeout.py` per spec.md §Conformance Test Map row 8 with SC-010 6-cell parametrized sweep:
  - (a) timeout-only: assert `timeout_exceeded == True`, `cancel_requested == False`, `pending_input_count == 0`, `is_steered_turn == False`.
  - (b) external-cancel-only: assert `cancel_requested == True`, `timeout_exceeded == False`, `pending_input_count == 0`.
  - (c) steering-only: assert `pending_input_count >= 1`, `cancel_requested == False`, `timeout_exceeded == False`.
  - (d) composite (steering → timeout → cancel): assert ALL three observable simultaneously.
  - (e) live-count semantics: assert `pending_input_count` increments as additional `.start()` calls land mid-execution (NOT an entry-time snapshot).
  - (f) backward-compat: existing `if ctx.cancel.is_set():` / `await ctx.cancel.wait()` patterns continue to work.
- [ ] T073 [P] [US6] Extend `<core>/tests/durable/test_steering.py` with `is_steered_turn` correctness test per SC-011: turn-2 (drain re-entry) observes `is_steered_turn == True`; turn-3 (fresh `.run()` resume after the drained task suspends) observes `is_steered_turn == False` (the sticky-True bug regression guard).
- [ ] T074 [P] [US6] Extend `<core>/tests/durable/test_entry_mode.py` per spec.md §Conformance Test Map row 5 with the `(entry_mode="recovered", is_steered_turn=True)` orthogonality test — previous process crashed mid-drain; new process picks up the queued steering input on recovery (SC-011).
- [ ] T075 [P] [US6] Port pre-existing tests in `<core>/tests/durable/test_cancellation_timeout.py` (and any other file matching `grep -l 'TaskTerminated\|\.terminate('`) per spec.md §Conformance Test Map "Hardening pre-existing tests" subsection — rewrite `.terminate(reason=...)` callers to `.cancel()` + assert handler-chosen terminal (cancel-semantic intent) OR `.cancel()` against a handler that raises on `ctx.cancel.is_set()` + assert `TaskFailed` (forced-failure intent). Record each port in `conformance-gap-list.md`.

### Implementation for US6

- [ ] T076 [US6] In `<core>/azure/ai/agentserver/core/durable/_context.py`, add `ctx.timeout_exceeded: bool` and `ctx.cancel_requested: bool` as new `__slots__` entries on `TaskContext`. Both default `False` at construction. Never reset (no public setters; framework-owned). `ctx.cancel` remains a bare `asyncio.Event` (FR-016, FR-017).
- [ ] T077 [US6] In `<core>/azure/ai/agentserver/core/durable/_context.py`, replace `ctx.pending_inputs: Sequence[Any]` with `ctx.pending_input_count: int` per FR-019. Implement as a property that reads from the framework-internal in-memory steering tracker on each access (live). Remove the `pending_inputs` slot and `__init__` parameter; remove construction from `_try_drain_steering` (T067 already simplifies the drain).
- [ ] T078 [US6] In `<core>/azure/ai/agentserver/core/durable/_context.py`, rename `ctx.was_steered` to `ctx.is_steered_turn` per FR-020. Remove the broken sticky-True computation that was in `_manager.py:876-880` — only set to `True` at the single set site in the drain code path (T067).
- [ ] T079 [US6] In `<core>/azure/ai/agentserver/core/durable/_context.py`, remove `ctx.steering_generation` from `__slots__`, `__init__`, and the drain code path's new-context construction per FR-021. Optionally retain the internal `_steering["generation"]` payload field pending the T004 trace decision; if T004 concluded "delete", do that in this task.
- [ ] T080 [US6] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, modify `_timeout_watchdog` to set `ctx.timeout_exceeded = True` BEFORE calling `ctx.cancel.set()` per FR-018. Ordering invariant: handler observing `ctx.cancel.is_set()` is guaranteed to see at least one cause boolean already `True`.
- [ ] T081 [US6] In `<core>/azure/ai/agentserver/core/durable/_run.py`, modify `TaskRun.cancel()` to set `ctx.cancel_requested = True` BEFORE calling `ctx.cancel.set()` per FR-018.
- [ ] T082 [US6] In `<core>/azure/ai/agentserver/core/durable/_run.py`, remove `TaskRun.terminate()` method, the `_terminate_event` / `_terminate_reason_ref` slots, and all related plumbing per FR-022.
- [ ] T083 [US6] In `<core>/azure/ai/agentserver/core/durable/_exceptions.py`, remove the `TaskTerminated` exception class per FR-022.
- [ ] T084 [US6] In `<core>/azure/ai/agentserver/core/durable/__init__.py`, drop `TaskTerminated` from imports and `__all__`. Verify no `stale_timeout` / `superseded` mentions in `__all__`.
- [ ] T085 [US6] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, collapse the `asyncio.CancelledError` branch in `_execute_task_loop` to the cooperative-cancel path only per FR-022: remove the `if resolved_terminate.is_set():` discriminator and the `TaskTerminated` construction. Result future set with `TaskCancelled`; framework writes the terminal record (or lets the handler's natural exception propagate). Remove the `terminate_event` and `terminate_reason_ref` plumbing from `_ActiveTask`, `_execute_task`, `_execute_task_loop`, and every call site (~13 sites).

**Checkpoint**: US6 complete — cancel-cause booleans live, steering surface cleaned up, terminate removed. **→ Run T119 (per-story code review for US6) before moving to Phase 10.**

---

## Phase 10: User Story 7 — Per-turn durable wall-clock timeout (Priority: P2; Implementation-phase C)

**Goal**: `@task(timeout=...)` becomes per-turn / wall-clock / durable / cooperative-only. Watchdog respawns at every logical turn boundary; budget is anchored to a durable per-turn-start timestamp; recovery preserves the budget within a turn. The misleading watchdog docstring is corrected.

**Independent Test**: A steerable `@task(timeout=N)` whose turn-1 runs for some duration, suspends, and turn-2 starts via fresh `.run()` gets a fresh N-second window. A crashed turn whose recovery picks up at +M seconds since turn-start spawns a watchdog with `remaining ≈ N − M`. Watchdog docstring no longer claims automatic lease expiry.

**Dependency**: depends on US6 (cancel-cause booleans available — `ctx.timeout_exceeded` set by watchdog).

### Tests for US7 (RED first)

- [ ] T086 [P] [US7] Extend `<core>/tests/durable/test_cancellation_timeout.py` with the SC-012 4-cell per-turn-durable-timeout sweep on `@task(timeout=timedelta(seconds=2))`:
  - (a) Steerable: turn-1 sleeps 1.5s, suspends; fresh `.run()` for turn-2 gets a fresh ~2s window.
  - (b) Steerable: turn-1 sleeps 1.5s, is steered (drain re-enters); generation 2 gets a fresh ~2s window.
  - (c) Non-steerable: handler crashes 1.5s in; recovery at +1.8s; recovered watchdog spawns with `remaining ≈ 0.2s`; `timeout_exceeded == True` fires at ≈ +2s since turn-start.
  - (d) Same as (c) but recovery delayed to +3s; recovered handler enters with `ctx.cancel.is_set() == True` AND `ctx.timeout_exceeded == True` from first checkpoint. The test reads the persisted turn-start timestamp directly from the provider for assertions.
- [ ] T087 [P] [US7] Extend `<core>/tests/durable/test_cancellation_timeout.py` with the SC-013 clock-skew clamping test — fake clock jumps backward 60s between turn-start-stamp and watchdog spawn; assert `remaining <= opts.timeout.total_seconds()`. Forward jump variant: assert `remaining` clamped to 0 (not negative); watchdog fires immediately.
- [ ] T088 [P] [US7] Add a docstring-content test (either in `test_cancellation_timeout.py` or as part of `test_dev_guide_review.py`'s source-docstring-review scope) asserting the rewritten `_timeout_watchdog` docstring does NOT contain the false claim "lease will eventually expire and the task will be recovered" AND does contain explicit cooperative-only language (`cooperative-only`, `process death`, `TaskRun.cancel()`).

### Implementation for US7

- [ ] T089 [US7] In `<core>/azure/ai/agentserver/core/durable/_models.py`, add a `_turn_started_at` payload field per FR-023 with the field name + location decided in T003. ISO-8601 UTC string; required at every turn-start boundary; tolerated absence (DEBUG log + fallback to full budget) during the rollout window.
- [ ] T090 [US7] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, write `_turn_started_at` at every turn-start set site per FR-023:
  - `create_and_start` (initial create write).
  - Suspended → in_progress resume in `_start_existing_task` (developer initiated via `.run()`).
  - Steering drain re-entry in the drain code path (same CAS write that bumps `_steering["generation"]`).
  Do NOT re-stamp on recovery (`entry_mode == "recovered"` path); the existing value is preserved.
- [ ] T091 [US7] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, rewrite the timeout-watchdog respawn logic per FR-024: respawn at every logical turn boundary (fresh entry, drain re-entry, recovery re-entry). Compute `remaining = max(0, opts.timeout.total_seconds() - (now - _turn_started_at))` clamped to `[0, opts.timeout.total_seconds()]`. Retries within the same generation share the watchdog. At most one watchdog live at a time; previous cancelled before next spawns. Cleanup in `_execute_task`'s `finally` block.
- [ ] T092 [US7] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, pre-set `ctx.timeout_exceeded = True` + `ctx.cancel.set()` if the recovered watchdog computes `remaining == 0` per FR-025 (immediate-fire-on-recovery clause: "If the recovered watchdog's `remaining == 0`, it MUST fire immediately so the recovered handler sees the timeout cause from its first checkpoint"), so the recovered handler sees the cause from its first checkpoint per FR-023's turn-start anchoring.
- [ ] T093 [US7] Rewrite the docstring of `TaskManager._timeout_watchdog` per FR-026. Remove the false "lease will eventually expire" claim. State explicitly: cooperative-only; sets `ctx.timeout_exceeded = True` then `ctx.cancel.set()` and exits; an ignoring handler runs until process death or external `TaskRun.cancel()` (FR-026). Watchdog-fired log message stays at INFO.

**Checkpoint**: US7 complete — timeout is per-turn / wall-clock / durable; watchdog docstring corrected. **→ Run T120 (per-story code review for US7) before moving to Phase 11.**

---

## Phase 11: User Story 8 — Shutdown has a discoverable API (`ctx.exit_for_recovery()`) (Priority: P2; Implementation-phase C)

**Goal**: Add `ctx.exit_for_recovery()` as the prescribed shutdown shape. No parameters; precondition `ctx.shutdown.is_set()` must be true (else `RuntimeError` at the call site). Framework recognises the returned sentinel and preserves `status="in_progress"` for recovery on next process startup.

**Independent Test**: Handler calling `ctx.exit_for_recovery()` during shutdown leaves the stored record `in_progress`; recovery on a fresh `TaskManager` re-enters with `entry_mode == "recovered"`. Calling outside shutdown raises `RuntimeError`; the task ends in `failed` (not silently `in_progress`).

**Dependency**: depends on US5 (metadata-flush invariant on terminal-of-turn boundaries) and US7 (the watchdog cleanup pattern is reused for `exit_for_recovery`'s flush+release sequence).

### Tests for US8 (RED first)

- [ ] T094 [P] [US8] Extend `<core>/tests/durable/test_cancellation_timeout.py` (or `test_lifecycle.py` — gap-list picks per Conformance Test Map row 9) with the SC-015 3-scenario sweep:
  - (a) Handler on `ctx.shutdown.is_set()` calls `await ctx.metadata.flush(); return await ctx.exit_for_recovery()` → stored `status == "in_progress"`; metadata durable; result future set to `TaskCancelled`.
  - (b) Fresh `TaskManager` recovers the task; handler re-enters with `entry_mode == "recovered"` and rehydrated metadata; `recovery_count` incremented.
  - (c) Handler calls `ctx.exit_for_recovery()` without `ctx.shutdown.is_set()` → `RuntimeError` raised at the call site; task ends `failed`.
- [ ] T095 [P] [US8] Add a signature-inspection test to `<core>/tests/durable/test_public_api_surface.py`: `inspect.signature(TaskContext.exit_for_recovery).parameters` contains only `self` — no `reason`, no `output` (US8 scenario 4, SC-015).
- [ ] T096 [P] [US8] In `<core>/tests/durable/test_cancellation_timeout.py` (or wherever T094 lives): add the queued-steering-input preservation test — `ctx.exit_for_recovery()` called with queued steering inputs MUST preserve the queue in persisted state; on recovery the queue drains naturally at the next turn boundary (US8 scenario 5, FR-028).

### Implementation for US8

- [ ] T097 [US8] In `<core>/azure/ai/agentserver/core/durable/_context.py` (or a new internal sentinel module — gap-list picks): define the `ExitForRecovery` sentinel class (parallel to `Suspended` in `_run.py`). Internal-only by default; MAY be exported on `__all__` for advanced introspection per FR-027.
- [ ] T098 [US8] In `<core>/azure/ai/agentserver/core/durable/_context.py`, add `async def exit_for_recovery(self)` method to `TaskContext` per FR-027: no parameters. At the start, check `self.shutdown.is_set()`; if `False`, `raise RuntimeError("ctx.exit_for_recovery() may only be called when ctx.shutdown.is_set() is true")` immediately. Otherwise return `ExitForRecovery()` sentinel.
- [ ] T099 [US8] In `<core>/azure/ai/agentserver/core/durable/_manager.py`, modify `_execute_task_loop` to recognise the `ExitForRecovery` sentinel per FR-027. When returned by the handler: (a) `await ctx.metadata.flush_all()` (FR-015 invariant; this is the framework-side auto-flush proven by T064's `shutdown-via-exit_for_recovery` cell — handler MUST NOT need to call flush itself); (b) **explicitly release the lease** — clear the lease ownership claim on the persisted record via a CAS write that ALSO stops the in-process renewal task (`renewal_cancel.set()`); the release MUST be the explicit FR-027(b) action, not merely a consequence of process exit. Funnel the release CAS through `_classify_store_write_error` so an `evicted` outcome during release is logged and degrades gracefully (no terminal record written); (c) do NOT write a terminal record (status MUST remain `in_progress`); (d) set the result future to `TaskCancelled` (same shape as the cooperative asyncio-cancel path); (e) preserve `_steering["pending_inputs"]` in the persisted state — do NOT drain during shutdown (FR-028).
- [ ] T100 [US8] Verify that the `RuntimeError` from misuse propagates through `_execute_task_loop`'s exception handler and results in `status="failed"` (not `in_progress`), so misuse is loudly visible in operator logs AND in the resulting record per US8 scenario 3.

**Checkpoint**: US8 complete — shutdown API discoverable; misuse caught; recovery cycle preserved. **→ Run T121 (per-story code review for US8) before moving to Phase 12 Polish.**

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: cross-cutting verification, sample-impact actions, and final integration checks.

- [ ] T101 [P] Run `pytest <core>/tests/durable/test_dev_guide_review.py` and verify ALL invariants from T007 pass green against the rewritten guide (T006).
- [ ] T102 [P] Run `pytest <core>/tests/durable/test_contract_completeness.py` and verify it stays green — auto-discovery via `__all__` traversal MUST pick up the new public symbols (`timeout_exceeded`, `cancel_requested`, `pending_input_count`, `is_steered_turn`, `exit_for_recovery`) and NOT find any of the removed symbols.
- [ ] T103 [P] Run `pytest <core>/tests/durable/test_public_api_surface.py` and verify the full presence/absence sweep (T026, T060, T071, T095) passes green.
- [ ] T104 Sample updates per spec.md §Docs↔Samples Loop §Samples affected matrix. For each row:
  - Surveys: `grep -rn 'pending_inputs\|was_steered\|steering_generation' sdk/agentserver/azure-ai-agentserver-core/samples/ sdk/agentserver/azure-ai-agentserver-invocations/samples/` — if any matches, migrate per the table.
  - Recommended-not-required updates: add one composite-case cancel-cause example to `durable_copilot/agent.py` if scoping allows; OR record deferral in `conformance-gap-list.md` with one-line justification per Constitution Principle IX.
- [ ] T105 Run `azpysdk pylint sdk/agentserver/azure-ai-agentserver-core` from the repo root; address any new violations introduced by this PR. Resist scope creep — fix only violations directly caused by spec-016 changes.
- [ ] T106 Run `azpysdk mypy sdk/agentserver/azure-ai-agentserver-core`; address any new type errors. Pay particular attention to the `derive_lease_owner` signature change, the `TaskResult.status` Literal narrowing, the new `TaskContext` property types, the `HostedTaskProvider.__init__` credential re-typing.
- [ ] T107 Run `azpysdk pyright sdk/agentserver/azure-ai-agentserver-core`; address any new errors.
- [ ] T108 Run `azpysdk sphinx sdk/agentserver/azure-ai-agentserver-core`; verify docs build cleanly with the rewritten developer guide (T006).
- [ ] T109 Verify the entire durable test suite passes: `cd sdk/agentserver/azure-ai-agentserver-core && pytest tests/durable/ -x -q`. Aim for the same count as the baseline from T001, plus the new tests from US1–US9 (~50–80 new test functions).
- [ ] T110 Final commit-history audit per Constitution Principle XII: every conformance-test commit MUST precede its paired implementation commit (RED-first). Run `git log --oneline` and verify the pattern.
- [ ] T111 Final review against `conformance-gap-list.md` (T005): every affected symbol has a test; every ported test is recorded; every deferred sample-update has a justification; no parallel test suite was created outside the two flagged new modules; no test was deleted without gap-list justification.

**Checkpoint**: All spec-016 work complete. **→ Run T122 (final whole-PR holistic review) before marking the PR ready for human review.**

---

## Phase 13: Continuous Code Review (interleaved with Phases 3–12)

**Purpose**: catch quality issues — hacks, scope creep, premature abstraction, under-design, dev-guide drift, spec-violation slips — at the cheapest possible moment. Per-story reviews catch local issues; cross-phase seam reviews catch architectural drift at the points the plan's Implementation Ordering Strategy identifies as boundaries (A→B, B→C); the final review catches anything that requires the full picture.

**How**: each review task dispatches the `code-review` agent (via the `task` tool with `agent_type: "code-review"`) with a specific scope statement. BLOCKING / HIGH findings MUST be addressed before the next phase begins. MEDIUM / LOW findings get logged in `conformance-gap-list.md` for the final-review sweep to verify they're either resolved or explicitly accepted with reviewer sign-off.

**Why this exists** (per user direction 2026-06-01): with 9 user stories and 12 phases on one cohesive PR, each phase risks shipping a hack that LOOKS LOCAL but degrades overall code quality, introduces a workaround that a later phase will have to fight, or silently drifts from the spec's design invariants. Per-phase, cross-phase, and final reviews collectively keep an eye on the overall shape.

### Per-story reviews (execute at each Phase 3-11 Checkpoint)

- [ ] T112 CODE REVIEW (Phase 3 / US9 / Phase A transport): Dispatch the code-review agent. Scope: review the commits implementing US9 (T012–T024) against spec FR-029..FR-034 and SC-016/SC-017. Verify: (a) every FR has corresponding implementation; (b) every SC has a behavior-deep test (no shape-only); (c) `ContentDecodePolicy` exclusion is enforced with an inline comment citing the responses-storage gzip lesson; (d) pre-existing httpx-fixture tests were ported (not deleted) per the "Hardening pre-existing tests" subsection; (e) RED commits precede GREEN commits; (f) no new public surface beyond what spec / data-model authorized; (g) no `# type: ignore` / `# pylint: disable` without justification per Constitution Principle II; (h) classifier seam from T021 is shape-stable (no premature abstraction; will not need re-shaping in Phase B). Address BLOCKING / HIGH findings before T025.

- [ ] T113 CODE REVIEW (Phase A→B cross-phase seam): Dispatch the code-review agent. Scope: review the classifier seam (T021) and pipeline construction (T020) from a "is the next phase's consumer going to love this or fight it?" perspective. Verify: (a) classifier signature is parameter-stable for the FR-007/FR-008 consumers in Phase B; (b) pipeline policy-chain ordering is fixed (no need for Phase B to re-order or re-insert policies); (c) error-classification outcomes (`transient` / `evicted` / `conflict` / `permanent`) are exhaustive against the Phase B store-write call sites; (d) no Phase A scaffolding will be removed by Phase B (no throw-away code shipped). Findings here often surface design issues that are cheap to fix now and expensive later.

- [ ] T114 CODE REVIEW (Phase 4 / US1 / surface cleanup): Dispatch the code-review agent. Scope: review the commits implementing US1 (T025–T032) against spec FR-001 and SC-001. Verify: (a) `stale_timeout` removed from every documented location (decorator, options, context, docstrings, doc, sample); (b) `_is_stale` helper removed including any internal call sites; (c) `TypeError` raised cleanly at every entry point that previously accepted the kwarg; (d) no replacement knob secretly introduced (e.g., a new `recovery_timeout` or `liveness_threshold` would be a regression of the "no developer knob" principle); (e) the existing `_decorator.py` tests that referenced `stale_timeout` are ported or replaced with the FR-009 test-only hook, not deleted.

- [ ] T115 CODE REVIEW (Phase 5 / US2 / split-brain): Dispatch the code-review agent. Scope: review the commits implementing US2 (T033–T042) against spec FR-007/FR-008 and SC-002. Verify: (a) the `binding_mismatch` body-shape detection is tolerant of non-JSON / missing-`error.code` bodies and falls back to `"conflict"` not `"evicted"` (guards against false-positive evictions); (b) the local-cleanup sequence (cancel + suppress terminal-write + signal awaiters + log) is ATOMIC — partial cleanup states are not observable; (c) the eviction outcome maps to the SAME `TaskConflictError` / `None` shape per Invariant 1 — verify no leaked split-brain field on the exception or return type; (d) operator WARNING logs include `task_id`, `session_id`, and binding_mismatch correlation; (e) no synthetic-bypass shortcuts in tests per Constitution Principle X (the provider stub returns real responses; the classifier is not monkey-patched).

- [ ] T116 CODE REVIEW (Phases 6+7 / US3+US4 / 3-layer recovery + lease owner): Dispatch the code-review agent. Scope: review the commits implementing US3 (T043–T058) and US4 (T059 verification) against spec FR-002..FR-005 and FR-004a; SC-003, SC-004, SC-005, SC-005a. Verify: (a) the three layers share ONE `_reclaim_one` helper — no per-layer duplicated reclaim logic; (b) CAS race protection is correct (loser re-reads and falls through; deterministic single-winner); (c) lease owner derivation incorporates BOTH agent name AND session ID per FR-004a, with the format choice consistent across all call sites; (d) `FOUNDRY_AGENT_NAME` unset fallback agrees with the rest of the framework (consistency invariant); (e) periodic-scan task is cancellable cleanly in `shutdown()` even during event-loop teardown; (f) `get_active_run()` outcome shape matches Invariant 1 exactly (TaskRun for live/reclaimed; None for terminal/evicted; no leaked "reclaimed" state). Pay particular attention to whether internal `_steering["generation"]` retention decision (T004) is honored.

- [ ] T117 CODE REVIEW (Phase B→C cross-phase seam): Dispatch the code-review agent. Scope: review the recovery + classifier integration completed in Phases 4-7 from a "is Phase C's steering / cancel / timeout / shutdown rewrite going to compose cleanly with this?" perspective. Verify: (a) the `_manager.py` mutation patterns from Phase B leave `_execute_task_loop` and the steering-drain code path in a shape that Phase C can rewrite without fighting recovery code; (b) `_turn_started_at` payload-field decision (T003) is implemented in a way that the Phase C watchdog-respawn (T091) can use cleanly; (c) the metadata-flush invariant (FR-015) for non-steering boundaries was preserved in Phase B's changes, so Phase C only has to ADD the missing flushes on drain-shortcut paths (not also retrofit the existing boundaries); (d) the `_reclaim_one` outcome handling propagates correctly into the Phase C terminal-write paths (no race between recovery-reclaim and steering-terminal-clear). Findings here are especially valuable: they prevent Phase C from having to monkey-patch around Phase B leftovers.

- [ ] T118 CODE REVIEW (Phase 8 / US5 / steering as multi-turn): Dispatch the code-review agent. Scope: review the commits implementing US5 (T060–T070) against spec FR-010..FR-015 and SC-007, SC-008, SC-009. Verify: (a) `superseded` is GONE from every code path that produces a `TaskResult` — no synthesis anywhere, no hidden alias; (b) the steering-drain code path is re-entry-only — does NOT resolve caller-visible futures, does NOT touch `ctx.metadata` (those are the boundary's concern); (c) the suspend / return path orders match FR-011 / FR-012 exactly (flush → persist → resolve → drain); (d) terminal-with-queued-input cleanup is ATOMIC (one CAS write clears `pending_inputs` AND records terminal status); (e) every queued steerer's future resolves with the correct `current_status` value; (f) metadata-flush invariant holds at ALL six terminal-of-turn boundaries (regression-tested by SC-009's sweep); (g) pre-existing tests that asserted `is_superseded` are ported to assert natural multi-turn outcomes, not deleted; (h) no parallel future-tracking dict survives in any form.

- [ ] T119 CODE REVIEW (Phase 9 / US6 / cancel-cause + terminate removal): Dispatch the code-review agent. Scope: review the commits implementing US6 (T071–T085) against spec FR-016..FR-022 and SC-010, SC-011, SC-014. Verify: (a) the four new `TaskContext` properties (`timeout_exceeded`, `cancel_requested`, `pending_input_count`, `is_steered_turn`) have no public setters — framework-owned; (b) the ordering invariant holds — each cause boolean is set BEFORE `ctx.cancel.set()` at every set site; (c) `pending_input_count` is genuinely LIVE (reads from the in-memory tracker on each access), not a snapshot; (d) `is_steered_turn` correctly composes with `entry_mode` (the `(recovered, is_steered_turn=True)` orthogonality is tested in T074); (e) `TaskRun.terminate` raises `AttributeError`; `TaskTerminated` import raises `ImportError`; (f) ALL `terminate_event` / `terminate_reason_ref` plumbing is removed (`grep` returns zero matches); (g) the `_execute_task_loop` `asyncio.CancelledError` branch is collapsed to ONE path; (h) `ctx.cancel` REMAINS a bare `asyncio.Event` — no wrapping class introduced. Pay attention to whether any "convenience" helper was introduced (e.g., `ctx.is_cancelled_for_reason(...)`) — the spec deliberately does NOT include such helpers; the four properties are the API.

- [ ] T120 CODE REVIEW (Phase 10 / US7 / per-turn durable timeout): Dispatch the code-review agent. Scope: review the commits implementing US7 (T086–T093) against spec FR-023..FR-026 and SC-012, SC-013. Verify: (a) `_turn_started_at` is set at the right places (fresh, suspended-to-in_progress resume, drain re-entry) and NOT set on recovery; (b) the watchdog's `remaining` computation matches the FR-023 formula exactly; (c) clock-skew clamping is applied in both directions (backwards and forwards) per SC-013; (d) at most ONE watchdog is live at a time — the previous-cancel-before-next-spawn invariant holds; (e) the watchdog stays cooperative-only — verifying no code path was secretly added that cancels the lease-renewal loop on watchdog fire; (f) the watchdog docstring is rewritten and contains the right keywords (`cooperative-only`, `process death`, `TaskRun.cancel`); (g) the log level for watchdog-fired is INFO, not WARNING.

- [ ] T121 CODE REVIEW (Phase 11 / US8 / shutdown API): Dispatch the code-review agent. Scope: review the commits implementing US8 (T094–T100) against spec FR-027..FR-028 and SC-015. Verify: (a) `ctx.exit_for_recovery()` signature is exactly `async def exit_for_recovery(self) -> ExitForRecovery` (no parameters); (b) the precondition `ctx.shutdown.is_set()` is checked AT THE METHOD START — not deferred to the framework's terminal-handling path; (c) the `RuntimeError` message clearly indicates the precondition violation; (d) the sentinel-recognition path in `_execute_task_loop` honors the precise ordering: flush metadata → release lease → preserve `in_progress` status → signal awaiter — no terminal write happens; (e) queued steering inputs are PRESERVED in the persisted state — not drained during shutdown; (f) misuse propagates through normal exception handling and ends in `status="failed"` (not `in_progress`) — the misuse cannot silently leave the task `in_progress`. This is the highest-risk story for "hack that LOOKS fine but breaks recovery" — review carefully.

### Final whole-PR review (execute at Phase 12 final task)

- [ ] T122 CODE REVIEW (whole PR / holistic): Dispatch the code-review agent. Scope: review the entire spec-016 PR holistically. Verify:
  - **Spec coverage**: every FR (FR-001..FR-034 + FR-004a) has implementation + test; conformance-gap-list.md is complete; every SC (SC-001..SC-018 + SC-005a) passes with a behavior-deep test.
  - **Public surface match**: Principle XII's affected-symbols enumeration matches the implementation symbol-for-symbol — no extras, no missing, no aliased re-exports of removed symbols.
  - **Documentation truth**: dev guide accurately reflects the implementation; doc-review meta-test passes; CHANGELOG reflects every public-surface change; source docstrings agree with the guide on every contract claim.
  - **Sample handling**: samples either updated per the spec's Samples Affected matrix OR deferred-with-justification recorded in tasks.md / conformance-gap-list.md.
  - **Cross-document artifacts**: `durability-contract.md` cross-cutting amendment is present and correct; `conformance-gap-list.md` records every test-routing decision (including any deviations from the spec's Conformance Test Map).
  - **Plan-phase decisions resolved**: the three deferred implementation decisions (FR-009 hook shape, `_turn_started_at` field name/location, `_steering["generation"]` retain-or-delete) are decided and documented in conformance-gap-list.md.
  - **Constitution exit checklists**: Principles X and XII exit checklists are all checked off; Principle XI is correctly marked N/A.
  - **No hacks**: no synthetic-bypass mechanisms in tests; no monkey-patched classifiers; no scaffolding-that-will-be-removed-later code present; no "TODO: revisit in next PR" comments without a tracked issue.
  - **No regression**: the existing test suite passes at the same count as the T001 baseline plus the new tests from US1–US9; no test was deleted without gap-list justification.
  - **Commit history hygiene**: RED-first commits precede GREEN commits for every conformance test per Constitution Principle XII §3.
  - **Lint / type / build clean**: T105 / T106 / T107 / T108 all green (pylint / mypy / pyright / sphinx).

Address BLOCKING / HIGH findings before marking the PR ready for human review. MEDIUM / LOW findings should be either resolved or explicitly accepted with a one-line justification in conformance-gap-list.md.

---

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1 (Setup)**: no dependencies; T001–T005 can begin immediately. T002/T003/T004 are blocking inputs to later phases.
- **Phase 2 (Foundational)**: depends on Phase 1; blocks all user story phases.
- **Phase 3 (US9 Transport)**: depends on Phase 2. Blocks Phases 4–7 (Phase B) because the classifier seam lives here. **GATE: T112 (per-story review) + T113 (Phase A→B seam review) MUST complete before Phase 4 begins; BLOCKING / HIGH findings MUST be addressed.**
- **Phase 4 (US1 Recovery surface clean)**: depends on Phase 3. **GATE: T114 before Phase 5.**
- **Phase 5 (US2 Split-brain)**: depends on Phase 3 + Phase 4. **GATE: T115 before Phase 6.**
- **Phase 6 (US3 3-layer recovery + lease owner)**: depends on Phases 3, 5.
- **Phase 7 (US4 get_active_run)**: depends on Phase 6 (US3 implements it via T058). **GATE: T116 (combined US3+US4 per-story review) + T117 (Phase B→C seam review) MUST complete before Phase 8 begins.**
- **Phase 8 (US5 Steering multi-turn)**: depends on Phases 3–7 complete (Phase B fully landed). **GATE: T118 before Phase 9.**
- **Phase 9 (US6 Cancel-cause + terminate removal)**: depends on Phase 8 (steering rewrite shares files). **GATE: T119 before Phase 10.**
- **Phase 10 (US7 Per-turn durable timeout)**: depends on Phase 9 (uses `ctx.timeout_exceeded` from US6). **GATE: T120 before Phase 11.**
- **Phase 11 (US8 Shutdown API)**: depends on Phases 8, 10 (reuses metadata-flush and watchdog patterns). **GATE: T121 before Phase 12.**
- **Phase 12 (Polish)**: depends on all user story phases.
- **Phase 13 (Continuous Code Review)**: review tasks T112–T122 are sequencing fences interleaved with Phases 3–12 per the GATE annotations above. T122 (final holistic review) is the last action before marking the PR ready for human review.

### Within each phase

- Tests MUST land RED in a commit BEFORE the implementation commit lands GREEN (Constitution Principle XII).
- `[P]` marked tasks within a phase can run in parallel (different files, no dependency on each other).
- Foundational documentation (T006 guide, T008 CHANGELOG, T009 durability-contract) lands before any phase-3+ tests, NOT before each phase — single up-front rewrite per the plan's coherence fix.
- Review tasks (T112–T122) are NOT parallel with anything in their target phase — they are blocking fences that consume the completed phase as input.

### Parallel opportunities

- T010, T011 (shared fixtures): parallel.
- T012–T017 (US9 tests): parallel within the new test file.
- T025–T027 (US1 tests): parallel.
- T033–T039 (US2 tests): parallel within the new and extended test files.
- T043–T050 (US3 tests): parallel.
- T060–T064 (US5 tests): parallel within the test files.
- T071–T075 (US6 tests): parallel.
- T086–T088 (US7 tests): parallel.
- T094–T096 (US8 tests): parallel.
- T101–T103 (Polish meta-test runs): parallel.
- **Review tasks T112–T122 are NOT parallel with each other** — each one consumes the result of a completed phase and gates the next. T113 and T117 (cross-phase seam reviews) can run in parallel with their paired per-story review (T112 with T113; T116 with T117) since they have different scope, but the next phase only begins after both complete.

---

## Implementation Strategy

### MVP framing — exception to the usual template

The spec-kit template's usual "MVP = User Story 1, deploy + demo after Phase 3" framing does NOT apply to this spec. All nine user stories collectively rewrite ONE cohesive pre-release contract. The package has not shipped; there is no production user to "demo to" between stories; and the spec's Pre-release scope note explicitly forbids "breaking change" framing that would justify incremental migration.

**Practical implication**: this spec lands as ONE PR with all nine user stories. The story decomposition exists for implementation tracking, reviewer auditability, and parallel-task identification — NOT for incremental delivery.

### Phase-by-phase land order (cohesive PR)

Land in this order on the single PR's commit history:

1. **Phase 1 + Phase 2**: setup + foundational documentation and fixtures (T001–T011).
2. **Phase 3 (US9)**: transport migration. The pipeline seam is the prerequisite for the classifier integration in subsequent phases.
3. **Phase 4 (US1)**: surface cleanup (drop `stale_timeout`).
4. **Phase 5 + Phase 6 + Phase 7 (US2 + US3 + US4)**: split-brain + 3-layer recovery + lease owner + `get_active_run` reclaim. These collectively close the recovery story.
5. **Phase 8 + Phase 9 + Phase 10 + Phase 11 (US5 + US6 + US7 + US8)**: the cohesive `_execute_task_loop` / drain rewrite, including cancel-cause booleans, steering surface cleanup, terminate removal, per-turn durable timeout, and shutdown API.
6. **Phase 12 (Polish)**: cross-cutting verification, sample updates, lint/type/build checks, conformance gap-list final review.

### Reviewer-friendly commit shape

For each user story, the commit pair (or commit group) should be:

1. RED commit: extend the existing test file(s) per the Conformance Test Map; add new test modules where justified. Run the test; verify it FAILS.
2. GREEN commit: implementation in the source files; run the test; verify it PASSES.
3. (Optional) REFACTOR commit: cleanup / docstring / type-hint touches.

Verifiable from `git log --oneline` per Constitution Principle XII §3.

### Parallel team strategy

This spec is best landed by a single developer (or a small team coordinating closely) given the inter-phase dependencies. If parallelised:

- Developer A: Phase 1 + Phase 2 + Phase 3 (Foundational + Transport).
- Once Phase 3 lands: Developer A continues with Phase 4 + Phase 5; Developer B starts Phase 6 + Phase 7 (they share `_manager.py` so commit-level coordination required).
- Once Phase 5–7 land: Developer A picks up Phase 8 + Phase 9; Developer B picks up Phase 10 + Phase 11 (also share `_manager.py` and `_context.py`).
- Both converge on Phase 12.

In practice the `_manager.py` and `_context.py` rewrites are large enough that single-developer ownership is the simplest path.

---

## Notes

- `[P]` tasks = different files, no dependencies.
- `[Story]` label maps task to user story for traceability.
- Each user story is NOT independently shippable (see MVP framing above) but IS independently reviewable.
- Verify tests FAIL before implementing (Constitution Principle XII §3 RED-first).
- Commit after each task or logical group; group RED + GREEN commits per story for reviewer clarity.
- Avoid: vague tasks, same-file conflicts marked `[P]`, cross-story dependencies that bypass the Phase A → B → C ordering.
- The `conformance-gap-list.md` artifact (T005) is the single source of truth for the test-routing decisions during implementation. Any divergence from the spec's Conformance Test Map is recorded there with justification.
