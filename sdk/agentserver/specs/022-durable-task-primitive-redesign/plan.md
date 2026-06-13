# Spec 022 — Implementation plan

## Summary

This plan covers the durable-task primitive in
`azure-ai-agentserver-core`. Spec is `spec.md` in this directory
(81 FRs, 19 SCs); design rationale and Q1-Q17 decisions are in
`/home/rapida/code/azure-sdk-for-python/sdk/agentserver/specs/021-narrow-redesign.md`
(living draft; **authoritative source for all "why"**).

**Branching**: continue on the existing `feature/agentserver-durable-tasks`
branch — NOT a new branch (per user direction).

**Strategy**: Eight-phase, spec-driven TDD per Constitution Principle VII
(TDD) + Principle XII (Core-Primitive TDD Discipline, NON-NEGOTIABLE) +
Principle XIII (Continuous Code Review Discipline, NON-NEGOTIABLE).

| Phase | Output |
|---|---|
| 0. Pre-impl audit + SOT update | `task-and-streaming-spec.md` (SOT) rewritten to describe the design as implemented (Q17 cleanup list applied); `durable-task-guide.md` flagged for Phase 7 rewrite; baseline test sweep snapshot. |
| 1. RED-first conformance tests | All FR / SC tests written and FAILING per Principle XII §3. Completeness meta-test extended to assert `__all__` shape + unsupported-surface absence. |
| 2. Primitive split + identifier supply + handler-sig validation | Decorators (`@task`, `@multi_turn_task`); separate `Task` / `MultiTurnTask` public classes; handler-signature validation; identifier supply rules; `if_last_input_id` precondition behavior; title static-string-only; no `Task.options` public method. |
| 3. Multi-turn ergonomics + raise + retry + metadata auto-flush | Return-is-implicit-suspend; multi-turn handlers use `return X` only; multi-turn raise → `suspended` (chain alive); queued steerers PROMOTE on raise; 7-step ordering per FR-053; retry semantics per FR-041-043; metadata auto-flush load-bearing per FR-045. |
| 4. Storage and persistence | Record writes exclude `payload["output"]`, `_output` attachments, and `payload["error"]`; suspend / terminal transitions clear `payload["input"]` + `payload["_retry_attempt"]` and keep `_last_input_id`. |
| 5. Public surface and exception taxonomy | Public exports match the specified surface: no `TaskResult`, `Suspended`, `TaskSnapshot`, `TaskStatus`, `OutputTooLarge`, or `Task.get`; `TaskRun` slim (FR-047/048); **7 public exceptions** carry only new-info fields per FR-077; `TaskDeferred`, `JSONValue`, `TaskErrorDict`, and `TaskExhaustedRetriesErrorDict` are exported; `TaskNotFound` / `TaskPreconditionFailed` live in `_exceptions_internal.py` (FR-074); local provider unchanged (FR-068a). |
| 6. Cancellation / timeout / recovery | Cooperative-only signaling (FR-054-057); queued-steerer cancel (FR-037); `TaskDeferred` from `exit_for_recovery` (FR-058); inline-recovery uses persisted input (FR-064); cancel/delete/shutdown matrix per FR-053-062; entry_mode matrix per FR-063. |
| 7. Downstream migration + final docs | Responses package migrated per §7 of 021: two registrations + dispatch + three `ctx.suspend(...)` → `return None` rewrites + `steerable_conversations` guard removal + `derive_task_id` preservation + bookkeeping-task verification (FR-066-068). **Invocations-package durable samples migration** (FR-068b/c): 4 samples on this branch rewritten (`durable_research`, `durable_multiturn`, `durable_langgraph`, `durable_copilot`) — `@task(steerable=True)` → `@multi_turn_task(...)`; `ctx.suspend(reason=..., output=output)` → `return output`; e2e tests green. **`durable-agent-demo` cross-branch hand-off** (FR-068d): file an issue / track follow-up PR on `feature/agentserver-durable-agent-demo` branch for the same migration applied to the demo's `src/durable-research-agent/agent.py` + rebuilt wheels + `demo-client.sh` green. Final docs sweep (`durable-task-guide.md`). |
| 8. Continuous Code Review + final verification | Per-phase + cross-area + final reviews per Principle XIII. Full test sweep; downstream (`invocations` / `ghcopilot` / `optimization` / in-tree samples) audit per SC-009; gap-list closeout. |

## Code Review Cadence (per Constitution Principle XIII)

This spec has 7 implementation areas (Phases 2-8), so the Continuous
Code Review Discipline applies (NON-NEGOTIABLE). Each phase ends with
a `code-review` agent invocation BEFORE the phase is considered done;
BLOCKING / HIGH findings clear before the next phase or area begins;
MEDIUM / LOW findings logged to `gap-list.md` for final sweep.

### Common SCOPE dimensions (apply to every per-phase review)

Per Principle XIII §3 + §314-322, every per-phase review's SCOPE
explicitly verifies (in addition to phase-specific risks):

1. **FR completeness** — every in-scope FR is FULLY implemented; each
   FR maps to specific code locations and paired tests.
2. **SC behavior assertions** — paired SCs assert *behavior*, not
   *shape*. Tests that only confirm a symbol exists are spec drift.
3. **Design-spec conformance** — implementation matches
   `docs/task-and-streaming-spec.md` symbol-for-symbol. Public
   symbols must be authorized by `spec.md` / Appendix A of 021.
   Conformance items updated in the same impl commit, not deferred.
4. **No scope creep** — no internal symbol introduced beyond what
   spec / data-model authorized.
5. **No phase-local hacks** — no TODO shortcuts, no unjustified
   `# type: ignore` / `# pylint: disable`, no monkey-patches.
6. **RED-first commit ordering** — test commit precedes impl commit
   (Principle XII §3).
7. **Doc travel** — dev-guide / skill-doc / CHANGELOG updates live
   in the SAME commit as the developer-visible change (Principle IX).
8. **Gap-list discipline** — MEDIUM/LOW findings logged;
   BLOCKING/HIGH clear before the next phase begins.

### Per-phase risk focus

| Review | Phase-specific risks |
|---|---|
| Phase 2 review | Class-split type-safety (FR-069) actually enforced by mypy/pyright (not just runtime); decorator allow-list (FR-051) covers all variants; `title=` non-string rejection at decoration time (FR-001/002); identifier supply edge cases (auto-gen collisions, one-shot 1:1 invariant, `if_last_input_id` precondition error shape). |
| Phase 3 review | 7-step ordering per FR-053 (auto-flush BEFORE PATCH; current TaskFailed resolves BEFORE queued steerer promotes; queued promotion uses persisted-cleared input slot); `ctx.suspend()` absent from public surface (grep + import-fail check); multi-turn raise truly transitions to `suspended` not `completed`; queued-steerer promotion uses correct entry_mode (`"resumed"`). |
| Phase 4 review | No remaining `payload["output"]` / `_output` / `payload["error"]` write sites (grep clean); `payload["input"]` clearing happens at exactly the right transition (suspend for multi-turn, terminal for one-shot — NOT mid-handler); `_last_input_id` survives across suspend cycles (regression test); local provider parity holds (Q16). |
| Phase 5 review | Exception public-surface (FR-070-077) — every public exception class has the right field set; `TaskNotFound` / `TaskPreconditionFailed` truly absent from `__all__` (SC-017); `TaskRun` slim shape (FR-047) — no `status` / `delete` / `refresh`; `TaskFailed.__cause__ is None` invariant (FR-075). |
| Phase 6 review | Cancellation matrix conformance (FR-054-062) — one E2E test per row; FR-061 force-delete-vs-promotion race resolves to `TaskCancelled` regardless of timing (NOT through FR-055 cooperative path); inline-recovery (FR-064) uses persisted input not caller's new input; entry_mode (FR-063) correct for all 6 scenarios. |
| Phase 7 review **CROSS-AREA SEAM** | `/tasks/resume` absence completeness (no route file, no manager method, tests + SOT §26 updated); responses' three `ctx.suspend(...)` call-site rewrites preserve semantics per §7.5 of 021 (return None deliberately chosen — NOT because equivalent to raise); bookkeeping-task variant durability contract verified (FR-068); **all 4 invocations durable samples on this branch migrated cleanly with green e2e tests** (FR-068b/c) — verify each sample's `ctx.suspend(reason=X, output=Y)` → `return Y` semantic preservation (the implicit-suspend translation MUST preserve observable behavior); **`durable-agent-demo` cross-branch hand-off filed** (FR-068d) — tracking issue / coordinated PR exists on `feature/agentserver-durable-agent-demo` branch with the same translation rules + wheels rebuild + `demo-client.sh` verification; guide rewrite has no broken cross-references. |
| Final review (Phase 8) | End-to-end spec coverage symbol-for-symbol vs Appendix A of 021; documentation truth (SOT spec + dev guide match impl + samples); design-spec known-gaps that 022 closes are updated; downstream-package audit (SC-009) complete; gap-list resolved or explicitly accepted. |

## Technical Context

**Language/Version**: Python 3.10+ (`azure-ai-agentserver-core`,
`azure-ai-agentserver-responses`, plus downstream readers in
`invocations` / `ghcopilot` / `optimization`).

**Primary Dependencies**:
- `azure-ai-agentserver-core` — the entire `core.durable/` subpackage
  is touched. Decorators, manager, run handle, context, exceptions,
  models, options, retry, metadata facade, payload-key constants,
  resume route absence, local provider (no code change per Q16).
- `azure-ai-agentserver-responses` — `_durable_orchestrator.py`
  (decorator switch + three `ctx.suspend(...)` → `return None`
  rewrites + bookkeeping-task verification); `start_durable` dispatch
  per the 6-row matrix in §7.1 of 021.
- `azure-ai-agentserver-invocations` / `azure-ai-agentserver-ghcopilot` /
  `azure-ai-agentserver-optimization` / in-tree samples — audit only
  for `ctx.suspend()` usage and unsupported-type imports per SC-009.
- Existing test infrastructure: `pytest` + `pytest-asyncio` +
  `azpysdk` runner; no new test frameworks.

**Storage**: Hosted provider (HTTP) + local file-backed provider
(`LocalFileTaskProvider`). The design narrows what the framework writes (no
`payload["output"]` / `_output` attachment / `payload["error"]`) but
adds no new fields. **Local provider requires NO code change** per
Q16 — it's a generic PATCH/DELETE engine; output write sites live in
the manager. The recently-fixed `started_at` immutability bug
(commit `843a21df02`) is independent of this work.

**Testing**: pytest. Conformance suite at
`azure-ai-agentserver-core/tests/durable/`. Existing crash-recovery
harness (`_crash_harness`) reused for FR-033/059/064 verification
(no synthetic-crash shortcuts per Principle X). Existing durability
contract suite (`tests/e2e/durability_contract/`) MUST stay green.

**Target Platform**: Linux (CI) + macOS (dev). Crash scenarios are
POSIX-only via `_crash_harness`.

**Performance Goals**: Not a release gate. Per-process single-session
concurrency model (per memory: hosted agentserver = one session per
process; occasional steering messages). No high-concurrency baseline.

**Constraints**:
- `feature/agentserver-durable-tasks` is the implementation branch
  (existing). No separate branch.
- The implementation exposes a single specified public surface (SC-007).
- Local provider gets NO code change (Q16); only the manager stops
  emitting output PATCHes.
- Hosted provider unchanged at the wire — no schema additions.
- The full durability-contract suite + existing core durable test
  suite stays green throughout (Phase 1 RED-first additions are
  expected to fail; everything pre-existing stays green).
- Responses test suite (unit + integration + interop + live) MUST
  stay green by end of Phase 7.

**Scale/Scope**: ~12 source files modified in `core/durable/`
(decorator, manager, run, context, exceptions, metadata, options,
models, retry, payload_keys, resume_route-deleted, __init__),
~3 files absent in final tree (`_resume_route.py`, `_result.py`, optionally
`_snapshot.py`). 1 source file modified in `responses/` orchestrator.
~25-30 new test cases across decorator / multi-turn / raise /
cancellation / exception / type-system layers. 4 docs touched
(`task-and-streaming-spec.md` SOT, `durable-task-guide.md`,
`CHANGELOG.md` per-package, `__init__.py` docstrings).

## Constitution Check

*GATE: must pass before Phase 2 implementation and again after
Phase 8 final verification.*

| Principle | Gate | Status |
|---|---|---|
| I. Modular Package Architecture | Changes stay in `core/durable/` + `responses/hosting/_durable_orchestrator.py`. No new top-level packages. No cross-package leaks (responses consumes only the public decorator + classmethod surface). | ✅ Plan stays within. |
| II. Strong Type Safety (NON-NEGOTIABLE) | Class split (FR-069) enforces "no `.delete()` on one-shot" + "multi-turn `get_active_run` needs `input_id`" STATICALLY (mypy/pyright), not at runtime. Public TypedDicts (`TaskErrorDict`, `TaskExhaustedRetriesErrorDict`) replace untyped `dict`. `JSONValue` replaces `Any` in metadata. No additional `Any` introduced. | ⏳ Verify Phase 5. |
| III. Azure SDK Design Guidelines | Decorator + classmethod surface follows Python SDK Design Guidelines conventions; exception names follow Pythonic suffix rules (`TaskFailed` / `TaskCancelled` / `TaskDeferred` — no `Error` suffix on these per repo precedent). | ✅ Honored. |
| IV. Async-First Design | All public methods on `Task` / `MultiTurnTask` / `TaskRun` / `TaskContext` that touch I/O are `async def`. `multi_turn_task.delete(task_id)` is `async`. Future-resolution is via `asyncio.Future`. No sync wrappers added. | ✅ Built in. |
| V. Fail-Fast Configuration | Decorator argument validation (FR-051) raises `TypeError` at decoration time (module import); rejected kwargs fail at startup, not at call time. `title=` non-string also fails at decoration time. | ✅ Enforced by FR-001/002/051 + SC-018. |
| VI. Observability & Correlation | Structured failure log/telemetry event for every handler failure (FR-015) regardless of listener presence; cancellation cause detail flows to logs (FR-054/056) not to exception fields. Recovery scanner / inline-recovery transitions emit `entry_mode` log fields per FR-063. | ⏳ Verify Phase 1 + Phase 6. |
| VII. Test-Driven Development | Every code-changing FR has a paired RED-first test task (Phase 1). Conformance gap-list (Phase 0) records the extend-X-vs-new-Y decision for every affected symbol. | ✅ Enforced via Phase 1 + gap-list. |
| VIII. Minimal Surface, Maximum Composability | Public exports drop from ~25 to ~17 symbols overall (net −8); 7 exceptions (down from 9); No public exports for `TaskResult`, `Suspended`, `TaskSnapshot`, `TaskStatus`, `OutputTooLarge`, `TaskNotFound`, or `TaskPreconditionFailed`; `.run()` returns `Output` directly. `Task` and `MultiTurnTask` split for type-safe composition. | ✅ Surface is intentionally smaller. SC-006 + SC-016 + SC-017 gate this. |
| IX. Docs ↔ Samples Loop (NON-NEGOTIABLE) | SOT (`task-and-streaming-spec.md`) updated in Phase 0 to describe the design as implemented (Q17 cleanup); dev guide (`durable-task-guide.md`) rewritten in Phase 7 alongside responses migration; per-package CHANGELOGs travel WITH each impl commit (not deferred). Loop completion criterion documented in spec §Docs↔Samples Loop. | ⏳ Verify per phase + final docs sweep in Phase 7. |
| X. Durability Contract Conformance (NON-NEGOTIABLE) | Contract changes (Q6 handler-failure semantic; Q13 recovery input-source; FR-025-027 no output/error persistence; FR-016-021 API surface) require `durability-contract.md` versioned change-log entry in same PR. Crash-recovery tests use real SIGTERM/SIGKILL via `_crash_harness`; no synthetic-crash shortcuts. | ⏳ Verify Phase 1 + Phase 6. |
| XI. Contract-Surface Test Depth (NON-NEGOTIABLE) | Conformance tests assert *behavior*, not just symbol existence. Class-split test (SC-016) uses mypy/pyright to validate type-safety enforcement, not just imports. Cancellation matrix tests (SC-014) verify caller-visible outcome + queued-steerer outcome + record state after — not just the exception type. | ⏳ Verify Phase 1 RED tests. |
| XII. Core-Primitive TDD Discipline (NON-NEGOTIABLE) | Applies to `core/durable/`. Every public symbol in the specified `__all__` has a paired conformance test landed RED before implementation (Phase 1). Completeness meta-test asserts `__all__` shape, unsupported-surface absence, decorator-allow-list, and exception-public-surface invariants. | ⏳ Verify Phase 1. |
| XIII. Continuous Code Review Discipline (NON-NEGOTIABLE) | 7 implementation phases (Phase 2-8). Per-phase + cross-area (Phase 7) + final (Phase 8) reviews per "Code Review Cadence" section above. BLOCKING/HIGH findings clear before next phase begins. | ⏳ Verify per phase. |

No gate failures pre-flight. All 13 principles honored; class split
(Principle II) + minimal-surface enforcement (Principle VIII) are
the load-bearing wins of this design.

## Project Structure

```
sdk/agentserver/
├── azure-ai-agentserver-core/
│   ├── azure/ai/agentserver/core/
│   │   └── durable/
│   │       ├── __init__.py                # `__all__` rewritten (Phase 5)
│   │       ├── _decorator.py              # @task one-shot; @multi_turn_task; class split; handler-sig validation (Phase 2)
│   │       ├── _options.py                # no Task.options/ephemeral; tags rejected (Phase 2)
│   │       ├── _context.py                # multi-turn uses return-only exit (Phase 3)
│   │       ├── _manager.py                # MAJOR — output/error write policy, raise semantics, 7-step ordering, retry, recovery
│   │       ├── _run.py                    # TaskRun slim shape (Phase 5); input_id attribute
│   │       ├── _result.py                 # absent in final tree (no TaskResult / Suspended)
│   │       ├── _snapshot.py               # absent in final tree (no TaskSnapshot)
│   │       ├── _exceptions.py             # 7 public exceptions + TaskErrorDict + TaskExhaustedRetriesErrorDict (Phase 5)
│   │       ├── _exceptions_internal.py    # TaskNotFound + TaskPreconditionFailed (internal-only; per FR-074)
│   │       ├── _metadata.py               # JSONValue alias + TaskMetadata facade (Phase 3 + Phase 5)
│   │       ├── _retry.py                  # RetryPolicy public-attr documentation only (Phase 2)
│   │       ├── _models.py                 # no `_OUTPUT_KEY` / `_ERROR_KEY` payload-key constants (Phase 4)
│   │       ├── _resume_route.py           # absent in final tree
│   │       └── _local_provider.py         # NO CHANGE (Q16 / FR-068a) — already correct
│   ├── docs/
│   │   ├── task-and-streaming-spec.md     # Phase 0 (SOT update per Q17 cleanup)
│   │   ├── durable-task-guide.md          # Phase 7 (rewrite for this design)
│   │   └── durability-contract.md         # Phase 0 + per-phase amendments (Principle X)
│   ├── tests/durable/
│   │   ├── test_decorator_surface.py      # Phase 1, RED — FR-001/002/003/004/005/051/069 + SC-016/018
│   │   ├── test_input_precondition.py     # Phase 1, RED — FR-029/076 + SC-005
│   │   ├── test_multi_turn_raise.py       # Phase 1, RED — FR-010-015/053 + SC-003/010
│   │   ├── test_retry.py                  # Phase 1, RED — FR-041/042/043 + SC-012
│   │   ├── test_metadata_flush.py         # Phase 1, RED — FR-044/045/046 + SC-011
│   │   ├── test_persistence.py            # Phase 1, RED — FR-025-032 + SC-001
│   │   ├── test_exception_taxonomy.py     # Phase 1, RED — FR-070-077 + SC-017
│   │   ├── test_cancellation_matrix.py    # Phase 1, RED — FR-037/054-062 + SC-014
│   │   ├── test_active_run.py             # Phase 1, RED — FR-022/023 + SC-002/005
│   │   ├── test_entry_mode.py             # extends existing — FR-063 + SC-013
│   │   ├── test_inline_recovery.py        # Phase 1, RED — FR-033/034/035/064 + SC-004/015
│   │   ├── test_taskrun_shape.py          # Phase 1, RED — FR-047/048
│   │   └── test_contract_completeness.py  # EXTEND meta-test — `__all__` shape + SC-006/007
│   └── CHANGELOG.md                       # entries land per-commit; final consolidation Phase 8
├── azure-ai-agentserver-responses/
│   ├── azure/ai/agentserver/responses/hosting/
│   │   └── _durable_orchestrator.py       # Phase 7 — two decorators + dispatch + three ctx.suspend → return None
│   ├── tests/integration/
│   │   └── test_durable_orchestrator_v2.py # Phase 7 — responses E2E for FR-066-068 + SC-008
│   ├── docs/                              # responses-specific guide updates (Phase 7)
│   └── CHANGELOG.md                       # Phase 7 (incl. `steerable_conversations` config-flip note)
├── azure-ai-agentserver-invocations/
│   ├── samples/
│   │   ├── durable_research/agent.py      # Phase 7 — @task(steerable=True) → @multi_turn_task; ctx.suspend → return
│   │   ├── durable_multiturn/agent.py     # Phase 7 — @task → @multi_turn_task; ctx.suspend(reason=...) → return output
│   │   ├── durable_langgraph/agent.py     # Phase 7 — same migration shape, 4 call sites
│   │   └── durable_copilot/agent.py       # Phase 7 — same migration shape, 4 call sites
│   ├── tests/e2e/
│   │   ├── test_durable_research_live.py  # Phase 7 — verify green post-migration
│   │   ├── test_durable_multiturn.py      # Phase 7 — verify green post-migration
│   │   └── test_durable_copilot_live.py   # Phase 7 — verify green post-migration
│   ├── tests/
│   │   ├── test_durable_samples_structure.py # Phase 7 — update if shape assertions need it
│   │   └── test_samples_shippable_bar.py  # Phase 7 — update for new decorator + return-is-implicit-suspend
│   └── CHANGELOG.md                       # Phase 7
└── specs/022-durable-task-primitive-redesign/
    ├── spec.md                            # this directory
    ├── plan.md                            # this directory
    ├── tasks.md                           # this directory
    ├── conformance-gap-list.md            # Phase 0 deliverable (per Principle XII §2)
    └── gap-list.md                        # Phase 8 deliverable (MEDIUM/LOW findings sweep)
```

**Cross-branch tracking — NOT in this branch's tree:**

```
[branch: feature/agentserver-durable-agent-demo]
sdk/agentserver/azure-ai-agentserver-invocations/samples/durable-agent-demo/
├── README.md
├── azure.yaml
├── build.sh
├── demo-client.sh
├── infra/                                 # Bicep templates for the Azure-deployable demo
└── src/durable-research-agent/
    ├── agent.py                            # MUST be migrated per FR-068d (same translation rules as FR-068b)
    ├── app.py
    └── store.py
```

The `durable-agent-demo` migration is tracked under FR-068d as a separate
workstream on `feature/agentserver-durable-agent-demo` — see Phase 7 task
T-7.12 for the hand-off note. Any `durable-agent-demo/` directory on
THIS branch was a stale leftover (only the `.gitignore` was tracked) and
has been removed.

## Implementation Phases

### Phase 0 — Pre-impl audit + SOT update

**Output**: `task-and-streaming-spec.md` rewritten end-to-end to
describe the design as implemented. Apply Q17 cleanup list from 021 §3
(drop §26 `/tasks/resume`, §35a `TaskSnapshot`, `TaskResult` /
`Suspended` envelope definitions, `ephemeral` parameter, all
`Task.get` / `Task.options` mentions, `payload["output"]` /
`payload["error"]` storage rules, public `TaskStatus` literal,
`OutputTooLarge` / `TaskNotFound` / `TaskPreconditionFailed`
from error taxonomy §39). Add new sections for `@multi_turn_task`
(decorator + classmethod), `TaskDeferred`, `if_last_input_id` on
both primitives, class split type-safety contract.

Also: produce `conformance-gap-list.md` recording the extend-existing-vs-add-test decision for every affected symbol (per Principle XII §2).

Pre-impl test baseline snapshot: full durable test suite green
(511 tests per the recent run); record this as the floor that
Phase 1 RED additions add to.

### Phase 1 — RED-first conformance tests

**Prerequisites**: Phase 0 complete (SOT + gap-list).

For each FR / SC in `spec.md`, write a paired test (extend an
existing file OR add a new one per the gap-list) that is **failing
as expected** against the current branch baseline. Tests land in
this exact set (one commit per file):

- `test_decorator_surface.py` — FR-001/002/003/004/005/051/069 + SC-016 + SC-018 (handler-signature validation per FR-003 lands here)
- `test_input_precondition.py` — FR-029 (last_input_id retention) + FR-076 (LastInputIdPreconditionFailed shape) + FR-004/005 (precondition arg on `.run()`/`.start()`) + SC-005
- `test_multi_turn_raise.py` — FR-010-015/053 + SC-003/010
- `test_retry.py` — FR-041/042/043 + SC-012
- `test_metadata_flush.py` — FR-044/045/046 + SC-011 (auto-flush load-bearing for cross-turn metadata propagation)
- `test_persistence.py` — FR-025-032 + SC-001
- `test_exception_taxonomy.py` — FR-070-077 + SC-017
- `test_cancellation_matrix.py` — FR-037/054-062 + SC-014 (queued-steerer cancel per FR-037 belongs here, not in TaskRun-shape tests)
- `test_active_run.py` — FR-022/023 + SC-005 (multi-turn input_id matching) + SC-002 (sequential chain metadata accumulation)
- `test_entry_mode.py` (extend existing) — FR-063 + SC-013
- `test_inline_recovery.py` — FR-033/034/035/064 + SC-004/015
- `test_taskrun_shape.py` — FR-047/048 (slim TaskRun surface)
- `test_contract_completeness.py` (extend) — `__all__` shape +
  unsupported-surface grep assertions + SC-006 + SC-007 (no
  backward-compat shims) verified by code review
- `tests/integration_responses/test_durable_orchestrator_v2.py` (in
  the responses package) — FR-066/067/068 + SC-008

**Exit**: every new test FAILS; pre-existing tests stay green.

### Phase 2 — Primitive split + identifier supply

**Owns**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-051, FR-069,
FR-073, FR-076 (signature + precondition behavior).

- `_decorator.py`: split `Task` into `Task` (one-shot) +
  `MultiTurnTask` (multi-turn). `@task` returns `Task[I, O]`;
  `@multi_turn_task(steerable=)` returns `MultiTurnTask[I, O]`.
  Reject `ephemeral=` / `steerable=` / `tags=` per FR-051.
  `title=` accepts only `str | None`; non-string raises `TypeError`.
- Handler signature validation per FR-003: at decoration time,
  inspect the handler's signature and assert it matches
  `async def fn(ctx: TaskContext[Input]) -> Output`. Reject sync
  handlers; reject non-`ctx` first-arg names; reject extra positional
  args. Type-check that `ctx` is annotated `TaskContext[...]` (or
  raise an actionable `TypeError` at decoration time).
- `_options.py`: expose no `Task.options` classmethod or `ephemeral`
  field; tighten the allow-list.
- `.run()` / `.start()` on both classes: accept optional
  `if_last_input_id: str | None = None`; one-shot auto-gens task_id
  + collapses input_id to task_id; multi-turn requires task_id.
  **Precondition behavior**: when `if_last_input_id` is supplied,
  the framework MUST compare against `payload["_last_input_id"]` on
  the persisted record (per FR-029); on mismatch, raise
  `LastInputIdPreconditionFailed(actual_last_input_id)` (per FR-076).
  No precondition check when omitted.
- `multi_turn_task.delete(task_id)` async classmethod (force-delete path).
- `multi_turn_task.get_active_run(task_id, input_id)` async classmethod
  (in-process only — see FR-022/023).
- `_retry.py`: docstring / public-attr documentation; no code change
  (already regular class with `__slots__` per repo convention).
  Verify `RetryPolicy.__init__` signature matches FR-073 exactly
  (field names: `max_attempts`, `initial_delay`, `max_delay`,
  `backoff_coefficient`, `jitter`, `retry_on`).

**Doc travel**: `__init__.py` exports + dev-guide decorator section
+ CHANGELOG entry for the decorator split. Per Principle IX, the
dev-guide section MUST land in the same commit as the decorator code.

**Exit**: Phase 1 tests for Phase 2 FRs pass; class-split mypy/pyright
strict mode passes; per-phase code review clean.

### Phase 3 — Multi-turn ergonomics + raise semantics + retry + auto-flush

**Owns**: FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013,
FR-014, FR-015, FR-041, FR-042, FR-043, FR-045, FR-046, FR-053.

- `_context.py`: expose no multi-turn `ctx.suspend()` method;
  internal `suspension_reason` recording stays.
- `_manager.py`: refactor `_handle_failure` → `_handle_multi_turn_failure`
  per 7-step ordering in FR-053 (auto-flush BEFORE PATCH; current
  TaskFailed resolves BEFORE queued steerer promotes; if handler
  raised `asyncio.CancelledError` resolve with bare `TaskCancelled`
  per the final-review Finding-3 fix). Multi-turn raise → `suspended`
  (NOT `completed`); chain stays alive; no `payload.error` written;
  `payload._last_input_id` unchanged.
- Queued-steerer promotion on raise (FR-013): queue head PROMOTES; promoted turn
  dispatches with `ctx.entry_mode == "resumed"`.
- One-shot raise (FR-014): `in_progress → completed`,
  delete record, raise `TaskFailed` on caller.
- Structured failure log/telemetry per FR-015.
- **Retry semantics (FR-041-043)**: per-handler-invocation retry budget
  unchanged from today's `RetryPolicy` mechanics. Verify within-attempt
  retry behavior, crash recovery NOT consuming budget, suspend
  bypassing retry. Post-exhaustion: one-shot → record deleted +
  `TaskFailed` to caller (FR-042); multi-turn → chain `in_progress →
  suspended` per FR-010/FR-011 + `TaskFailed` to listener + subsequent
  turns get fresh retry budgets (FR-043).
- **Auto-flush (FR-045)**: `ctx.metadata` auto-flush MUST run at all
  lifecycle boundaries (suspend / success / cancel / retry-exhausted).
  For multi-turn, auto-flush at handler-raise is LOAD-BEARING — the
  next turn's handler MUST see the flushed metadata (per Q6
  chain-stays-alive semantic). Verify the 7-step ordering puts
  auto-flush BEFORE record PATCH.
- **One-shot metadata locality (FR-046)**: confirm that one-shot
  metadata is invocation-local (no cross-invocation visibility) since
  the record is deleted on terminal exit.

**Doc travel**: dev-guide multi-turn section rewrite + retry section
+ metadata facade section + CHANGELOG. All in same commits per
Principle IX.

**Exit**: Phase 1 tests for Phase 3 FRs pass; SC-010 + SC-011 + SC-012
pass; per-phase code review verifies 7-step ordering observability
and metadata propagation across raise.

### Phase 4 — Storage and persistence

**Owns**: FR-025, FR-026, FR-027, FR-028, FR-029, FR-030, FR-031,
FR-032.

- `_manager.py`: omit `_build_output_co_write` and all output
  write/clear sites (success / suspend / drain Phase-1 /
  `_handle_failure`). Omit interim `error` PATCH between retry
  attempts.
- `payload["input"]` clearing at the suspend / terminal transition
  ONLY (NOT mid-handler); `payload["_retry_attempt"]` cleared at
  the same transition; `payload["_last_input_id"]` KEPT.
- `_models.py`: omit `_OUTPUT_KEY` + `_ERROR_KEY` constants and any
  helpers that read them.
- Local provider parity (Q16) — manager owns output write
  sites, not provider.

**Doc travel**: SOT spec §20 (framework-reserved payload keys) update
to reflect supported keys; dev-guide payload section.

**Exit**: Phase 1 tests for Phase 4 FRs pass; grep clean for
`payload\["output"\]`, `payload\["error"\]`, `_output`-attachment
write sites (per SC-006); local provider tests still green
(no code changed there).

### Phase 5 — Public surface and exception taxonomy

**Owns**: FR-016, FR-017, FR-018, FR-019, FR-020, FR-021, FR-022,
FR-023, FR-024, FR-047, FR-048, FR-065, FR-068a, FR-070, FR-071,
FR-072, FR-074, FR-075, FR-077.

- `_result.py` does not exist in the final tree (no TaskResult / Suspended); `_snapshot.py` does not exist in the final tree (no TaskSnapshot).
- `_run.py`: slim `TaskRun` to 2 attributes (`task_id`, `input_id`) +
  1 property (`metadata`) + 2 methods (`result`, `cancel`) + 1
  dunder (`__await__`). Do not expose `status`, `lease_expiry_count`,
  `delete`, or `refresh`. Internal slots absent: `_provider`,
  `_terminate_event`, `_terminate_reason_ref`, `_status`,
  `_lease_expiry_count`.
- `_exceptions.py`: bare `TaskCancelled` / `TaskDeferred` /
  `SteeringQueueFull` / `InputTooLarge`; `TaskFailed(error)` /
  `TaskConflictError(current_status)` /
  `LastInputIdPreconditionFailed(actual_last_input_id)`. Do not export
  `OutputTooLarge`. Export `TaskDeferred`, `TaskErrorDict`,
  `TaskExhaustedRetriesErrorDict`. Keep `TaskNotFound` +
  `TaskPreconditionFailed` in an internal-only module
  (`_exceptions_internal.py` if not already).
- `_metadata.py`: add `JSONValue` recursive type alias and export.
  `TaskMetadata` exposes the dunders + `get` + `_`-namespace-reserved
  per FR-044 (`TaskMetadata` itself was already authored in Phase 3
  for the auto-flush work; this phase just confirms the public
  surface is documented and tested).
- **Local provider (FR-068a)**: NO code change to
  `_local_provider.py` — output write sites live in the manager
  per Q16. Tests asserting `_output` attachment behavior (C-OUT in
  SOT, plus related C-ATT-3/4/5 entries) MUST be removed or rewritten
  because no code generates the writes they assert on.
- `__init__.py`: rewrite `__all__` to the 7-exception public-surface;
  exclude unsupported re-exports; add `MultiTurnTask`, `multi_turn_task`,
  `JSONValue`, `TaskErrorDict`, `TaskExhaustedRetriesErrorDict`,
  `TaskDeferred`.

**Doc travel**: dev-guide exception taxonomy section rewrite + SOT
spec error taxonomy §39 trim + CHANGELOG.

**Exit**: SC-016 + SC-017 pass; grep clean for unsupported symbols
(SC-006); mypy/pyright strict mode green.

### Phase 6 — Cancellation / timeout / recovery

**Owns**: FR-033, FR-034, FR-035, FR-036, FR-037, FR-038, FR-039,
FR-040, FR-054, FR-055, FR-056, FR-057, FR-058, FR-059, FR-060,
FR-061, FR-062, FR-063, FR-064.

- `_manager.py`: cancellation matrix — caller-visible outcome
  depends ENTIRELY on what the handler raises (per FRs 054-057 /
  final-review Finding-4 fix). Timeout = cooperative-only
  signaling; framework never raises automatically.
- **`TaskRun.cancel()` semantics (FR-037)**: cooperative cancel via
  `ctx.cancel.set()` for active runs; for handles bound to queued
  (not-yet-promoted) steerers, `cancel()` MUST remove the input
  from the steering queue and resolve the handle's `.result()` with
  `TaskCancelled` (the chain itself is unaffected; other queued
  steerers proceed normally).
- `ctx.exit_for_recovery()` → caller sees `TaskDeferred` (NOT
  `TaskCancelled`). Task stays `in_progress`.
- Inline-recovery (FR-064): `.start()` against expired-lease
  in-progress record uses PERSISTED input for the recovered
  handler; caller's new input flows through the standard non-crash
  path (TaskConflictError for one-shot/non-steerable; queue for
  steerable).
- `_context.py`: `ctx.entry_mode` literal correctly stamped for the
  6 scenarios in FR-063 (fresh / resumed / recovered / steering
  promotion).
- `multi_turn_task.delete(task_id)` mid-promotion race (FR-061):
  promoted turn cancels via force-delete lease-loss path (NOT
  cooperative FR-055 — per final-review Finding-5 fix).

**Doc travel**: dev-guide cancellation section + SOT cancellation
matrix + CHANGELOG. All in same commits per Principle IX.

**Exit**: SC-013 + SC-014 + SC-015 + SC-004 pass; per-phase code
review verifies cancellation matrix conformance.

### Phase 7 — Downstream migration + final docs

**Owns**: FR-049, FR-050, FR-052, FR-066, FR-067, FR-068, FR-068b,
FR-068c; SC-008, SC-009a. **Hands off FR-068d** to a follow-up
workstream on `feature/agentserver-durable-agent-demo` branch
(not in this branch's PR).

**Ordering note (Principle IX — Docs ↔ Samples Loop):** the dev-guide
rewrite (T-7.6 in tasks.md) MUST land BEFORE the sample migrations
(T-7.7 through T-7.10). Samples derive from the guide, not the other
way around. The guide consolidates the design that's already
authoritatively captured in spec 022 + Appendix A of 021 — the
guide rewrite is mechanical translation; samples then derive their
new shape verbatim from the guide examples. Verify the commit
ordering at code review (T-7.13).

- `_resume_route.py` and `TaskManager.handle_resume` do not exist in the final tree. Update
  any tests that referenced them (`test_entry_mode.py:109`,
  `test_sample_e2e.py:337/361/529/554`). Rewrite SOT §26 + related
  conformance items.
- **Responses-package migration** (FR-066/067/068):
  `_durable_orchestrator.py` — two decorator registrations
  (`@task` + `@multi_turn_task(steerable=opt_in)`); `start_durable`
  dispatch per 6-row matrix; three `ctx.suspend(reason=...)` call
  sites rewritten to `return None` (two recovery branches + one
  normal turn-return per FR-067); remove the
  `if self._options.steerable_conversations:` guards that today
  wrap those call sites; preserve the `derive_task_id` partition
  logic unchanged; bookkeeping-task variant durability-contract
  verification per FR-068; document the `steerable_conversations`
  config-flip orphaning behavior in the responses-package CHANGELOG.
- **Dev-guide rewrite (FIRST among the sample-related work)**:
  `durable-task-guide.md` per Q17. Omit `Task.options` / `Task.get`
  / `ctx.suspend()` / `ephemeral` sections; rewrite examples using
  `return X` for multi-turn; fix the stale `async for chunk in
  task_run` docstring; add `TaskDeferred` +
  `multi_turn_task.delete` sections; document the
  `steerable=False` default and when to opt in. Each example MUST
  be mechanically reproducible from the documented public surface.
- **Invocations-package samples migration** (FR-068b/c):
  Migrate all 4 durable samples in `azure-ai-agentserver-invocations/samples/`,
  deriving each from the updated dev-guide:
  - `durable_research/agent.py` — `@task(steerable=True)` →
    `@multi_turn_task(steerable=True)`; `return await ctx.suspend()`
    → `return None` (or `return <terminal>`); update docstring.
  - `durable_multiturn/agent.py` — `@task` → `@multi_turn_task`
    (steerable=False default — sample is sequential turns only,
    verified against agent.py + app.py);
    `return await ctx.suspend(reason=..., output=output)` → `return output`.
  - `durable_langgraph/agent.py` — `@task(steerable=True)` →
    `@multi_turn_task(steerable=True)`; 4× `ctx.suspend(...)` →
    `return output`/`return None`.
  - `durable_copilot/agent.py` — `@task(steerable=True)` →
    `@multi_turn_task(steerable=True)`; 4× `ctx.suspend(...)` →
    `return output`/`return None`.
  Update / re-run the live e2e tests
  (`tests/e2e/test_durable_research_live.py`,
  `tests/e2e/test_durable_multiturn.py`,
  `tests/e2e/test_durable_copilot_live.py`); add a smoke test for
  langgraph (`tests/e2e/test_durable_langgraph_smoke.py` — full
  live e2e is out of scope for this branch since no live test
  exists today); update the structure test
  (`tests/test_durable_samples_structure.py`) +
  the shippable-bar test (`tests/test_samples_shippable_bar.py`).
- **`durable-agent-demo` cross-branch hand-off** (FR-068d):
  the deployable demo lives on `feature/agentserver-durable-agent-demo`
  branch (NOT in this branch). File a follow-up issue (or directly
  open a coordinated PR on that branch) tracking the same migration
  applied to the demo's `src/durable-research-agent/agent.py` —
  `@task(steerable=True)` → `@multi_turn_task(steerable=True)`;
  `ctx.suspend(...)` → `return X`. Rebuild the bundled wheels under
  `build.sh` against the merged `azure-ai-agentserver-core` +
  `azure-ai-agentserver-invocations` packages and verify
  `demo-client.sh` end-to-end. The hand-off itself happens during
  Phase 7 (file the issue / coordinate with the demo owner); the
  demo's actual migration is owned by the demo branch's PR and
  blocked by THIS branch merging to main.

**Doc travel**: this IS the docs consolidation phase — every change
above carries its own doc / CHANGELOG entry, in addition to the
per-phase doc travel already happening since Phase 2 (per Principle
IX). Phase 7 is NOT the only doc-update phase; it's the place where
the cross-cutting story comes together, AND it's where the
guide-before-samples ordering (Principle IX) is most visible.

**Exit**: SC-008 + SC-009a pass; SC-009 audit completion is
the responsibility of Phase 8.

### Phase 8 — Continuous Code Review + final verification

**Owns**: SC-009 (downstream audit completion). All other SCs and
FRs are owned by earlier phases; Phase 8 verifies the full picture.

- Cross-area code review: every cross-phase seam (`/tasks/resume`
  → responses migration; persistence contract → exception taxonomy
  → cancellation matrix). Verify no scope creep.
- SC-009 audit: walk through `invocations` / `ghcopilot` /
  `optimization` / in-tree samples / tests outside core; produce
  migration patches or "no-op" justifications per package.
- Full test sweep: durable suite + responses suite + downstream
  suites; all green.
- Final pre-merge review per Principle XIII.

**Exit**: All FRs implemented; all SCs verified; gap-list resolved
or explicitly accepted; ready for merge.

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Class split breaks downstream packages that pattern-match on `Task` | HIGH | SC-009 downstream audit kicks off in Phase 7; pre-impl grep across all packages for `Task[I, O]` / `isinstance(_, Task)` patterns; Phase 2 review verifies. |
| 7-step ordering on multi-turn raise gets observably wrong (auto-flush AFTER PATCH = lost metadata) | HIGH | SC-010 explicitly tests this ordering in a single E2E. Phase 3 review verifies. |
| Recovery scanner uses caller's new input instead of persisted (Q13 regression) | HIGH | SC-015 verifies for steerable + non-steerable; SC-004 across all 4 crash scenarios. Phase 6 review verifies. |
| Cancellation/timeout watchdog gets bug where ANY handler return → `TaskCancelled` regardless of what was raised (final-review Finding 4 regression) | HIGH | FR-054-057 explicitly require clean return → `Output` even when `ctx.cancel` was set; SC-014 has one row per matrix cell. Phase 6 review verifies. |
| Force-delete race resolves to cooperative cancel instead of forced (final-review Finding 5 regression) | MEDIUM | FR-061 explicitly cites FR-060 not FR-055; SC-014 covers the race. Phase 6 review verifies. |
| Internal `TaskNotFound` reuse pattern accidentally exports it (final-review Finding 7 regression) | MEDIUM | SC-017 verifies `from azure.ai.agentserver.core.durable import TaskNotFound` raises `ImportError`. Phase 5 review verifies. |
| Responses-package three-site rewrite picks up only 2 sites (final-review Finding 10 regression) | MEDIUM | FR-067 enumerates all three; SC-008 verifies in responses' E2E. Phase 7 review verifies. |
| Stale `payload["output"]` reads in downstream packages | MEDIUM | SC-009 audit explicitly greps. Pre-impl audit + Phase 7 review verify. |
| Dev-guide samples drift from impl during multi-phase work | MEDIUM | Principle IX — every developer-visible change ships with its CHANGELOG and dev-guide update in the same commit; Phase 7 is the consolidation pass. |
| Multi-turn `get_active_run(task_id, input_id)` accidentally returns cross-process handles (final-review Finding 6 regression) | LOW | FR-023 scopes to "in this process or reclaimable inline"; no interprocess channel. Phase 5 review verifies. |
| `started_at` immutability regression resurfaces | LOW | Already fixed + 5 regression tests added in commit `843a21df02`. No further mitigation needed. |
| Queued-steerer `TaskRun.cancel()` hangs the chain or fails to clean the queue (FR-037) | HIGH | `test_cancellation_matrix.py` covers the queued-vs-active branch explicitly; Phase 6 review verifies queue compaction on queued cancel. |
| Retry-budget drift across crash recovery (FR-041-043) — recovered handler consumes budget twice or fresh turn starts mid-budget | HIGH | `test_retry.py` covers crash-recovery-doesn't-consume-budget + per-turn fresh budget assertions; Phase 3 review verifies. |
| `if_last_input_id` precondition check races with concurrent steerers (FR-029/076) — read-modify-write hazard at the manager level | MEDIUM | Precondition compare happens under the per-task write queue serialization (same path as today's etag CAS); `test_input_precondition.py` covers concurrent-input + stale-precondition scenarios. Phase 2 review verifies. |
| Responses bookkeeping-task variant loses crash recovery during decorator switch (FR-068) | HIGH | Pre-migration: write down the current durability contract (signal persistence, recovery semantics) BEFORE switching decorators. `tests/integration/test_durable_orchestrator_v2.py` extends with a bookkeeping-recovery scenario. Phase 7 review verifies. |
| `TaskMetadata` JSON-serialization breaks legitimate developer values (datetime, bytes, custom classes) — FR-070 `JSONValue` constraint is stricter than today | MEDIUM | FR-070 says SHOULD raise `TypeError` at write time. Document supported types explicitly in the dev-guide; provide migration hint for common cases (datetime → ISO string; bytes → base64). Phase 5 review verifies. |
| Invocations durable-samples migration produces silently-incorrect samples (e.g., `ctx.suspend(reason="X", output=Y)` becomes `return Y` but the dev forgets the `output=` value, losing observable per-turn outputs) | HIGH | FR-068b enumerates each call site verbatim; e2e tests (`test_durable_research_live.py` etc.) exercise the actual per-turn output values. Phase 7 cross-area review verifies the semantic-preservation translation per sample. |
| `samples/durable-agent-demo` cross-branch hand-off forgotten — design merges but the deployable demo on `feature/agentserver-durable-agent-demo` branch keeps using removed API and `demo-client.sh` breaks | MEDIUM | FR-068d requires filing a tracking issue / coordinating PR on the demo branch during Phase 7 (task T-7.12 — see tasks.md). Demo branch owner is responsible for the actual code change; THIS branch's PR cannot land without the hand-off note. |

## Locked design decisions

All locked decisions are in `021-narrow-redesign.md` §3 (Q1-Q17,
all resolved) + Appendix A (full public surface enumeration).
Highlights:

- Q1: multi-turn handlers use return-only exit (internal
  `suspension_reason="run_completion"`)
- Q5: `@task` + `@multi_turn_task` decorator names (NOT
  `@one_shot_task`; NOT a single decorator with mode flag)
- Q6: Multi-turn raise → `suspended` (chain stays alive)
- Q9: `TaskResult[O]` / `Suspended[O]` are not part of the public surface; `.run()` returns
  `Output` directly
- Q10: `Task.options` is not part of the public surface (multiple decorators with distinct
  `name=` for variants)
- Q11: `ctx.exit_for_recovery()` exists; raises `TaskDeferred`
  (NOT `TaskCancelled`) per refinement
- Q12: `/tasks/resume` route is not part of the public surface
- Q13: Inline-recovery uses persisted input
- Q14: 7-step ordering + cancellation/deletion/shutdown matrix
- Q17: Consolidated dead-code cleanup list

## Open questions deferred to follow-up specs

None. Q1-Q17 in 021 are all resolved as of the latest iteration
log entry (2026-06-13 "do all these need dedicated exceptions"
+ subsequent gap-audit findings + final-review BLOCKING fixes).

## Cross-references

- **Spec**: `./spec.md` (81 FRs, 19 SCs)
- **Living draft**: `../021-narrow-redesign.md` (design rationale,
  Q1-Q17, Appendix A public-surface enumeration)
- **Constitution**: `../../.specify/memory/constitution.md`
- **SOT**:
  `../../azure-ai-agentserver-core/docs/task-and-streaming-spec.md`
- **Dev guide**:
  `../../azure-ai-agentserver-core/docs/durable-task-guide.md`
- **Recent independent fix**: commit `843a21df02` —
  `started_at` immutability bug in local provider (independent of
  this spec; resolved 2026-06-13)
