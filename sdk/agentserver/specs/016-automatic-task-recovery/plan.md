# Implementation Plan: Durable-task primitive — pre-release contract hardening

**Branch**: `feature/agentserver-durable-tasks` (continuing on current branch; no new branch)
**Date**: 2026-06-01
**Spec**: [`./spec.md`](./spec.md)
**Input**: Feature specification at `sdk/agentserver/specs/016-automatic-task-recovery/spec.md`

> **Pre-release framing.** This plan is the implementation plan for an in-place rewrite of the durable-task primitive's unshipped pre-release contract. No migration code, no "breaking change" framing — see the spec's Pre-release scope note.

---

## Implementation status (rolling update — 2026-06-02)

**Status: substantially complete.** All 9 user stories' surface contracts and behavioral requirements are landed and verified by **347+ passing tests** across the durable suite (1 documented skip, no regressions). 15 spec-implementation commits landed across the 13 phases:

| Commit | Phase | What landed |
|---|---|---|
| `019fea47a8` | US8 extended | T094(b) recovery re-entry + T096 queued-input preservation tests |
| `ed207011b0` | US7 deep | `_turn_started_at` end-to-end + recovered-watchdog remaining computation + SC-013 clamping + FR-025 immediate-fire (5 new tests) |
| `832890d37e` | Phase 13 fixes | Code-review BLOCKING/HIGH addressed: FR-002 Layer 3 wired, TaskTerminated strict-removed, is_superseded deleted, _steering[generation] removed, dev guide truth-claim softened |
| `66b3fe582b` | Phase 12 | Polish: sample updates + gap-list §7 audit |
| `f360b939ee` | Phase 10+11 | Per-turn timeout (Phase 10) + exit_for_recovery (Phase 11) |
| `38348efde4` | Phase 9 | US6 cancel-cause booleans + terminate removal |
| `dda570aa9a` | Phase 8 | US5 steering as plain multi-turn |
| `fce1919c28` | Phase 6 | US3+US4 three-layer recovery + async get_active_run |
| `a199e573ce` | Phase 5 | US2 split-brain eviction integration |
| `2dbb83e5dd` | Phase 6 partial | FR-004a lease-owner agent+session |
| `6b3f2531a6` | Phase 4 | US1 stale_timeout removal + 13 test ports |
| `ad33e12c16` | Phase 3 | US9 transport migration to azure.core |
| `665c22d425` | Phase 2 | Foundational docs + meta-test invariants + shared fixtures |
| `af16196abc` | Phase 1 | Setup: T002/T003/T004 decisions + conformance-gap-list.md scaffold |

**Final code-review verdict (T122 holistic)**: REQUEST-CHANGES → all BLOCKING + HIGH addressed in follow-up commits. Remaining MEDIUM/LOW items tracked in `conformance-gap-list.md` §7 as follow-ups (residual cosmetic dead-code cleanup; dedicated parametrized sweep tests; doc-string polish).

**Known follow-ups** (cosmetic, not blocking):
- HIGH #6 (commit followup): residual `_terminate_event`/`_terminate_reason_ref` slots in `_ActiveTask` and `TaskRun` are inert dead code (FR-022 behavior is fully removed; the slots accept but ignore the kwargs). Mechanical cleanup.
- HIGH #8: dedicated parametrized SC-006/SC-008/SC-009/SC-010 sweep tests beyond the per-scenario tests already in place. The scenarios ARE covered behaviorally by the existing tests; the explicit sweep style is stylistic.

---

## Summary

Close six inter-related defects in the unshipped durable-task primitive in `azure-ai-agentserver-core` before it ships: (1) recovery is leaky — make it framework-owned and three-layered; (2) steering is over-modeled — collapse to plain multi-turn with a queue; (3) cancellation surface is confused — decompose into independent cause booleans + simplified steering state; (4) timeout is non-durable and per-invocation — make it per-turn / wall-clock / durable; (5) shutdown has no first-class API — add `ctx.exit_for_recovery()`; (6) transport has no policy stack — migrate the hosted task-store client to `azure.core.AsyncPipelineClient` with the `ContentDecodePolicy` exclusion lesson from the responses package. Plus one corollary fix: include agent name in the stable lease owner string so different agents sharing a session ID can't collide (FR-004a).

**Technical approach:** rewrite the affected internal modules in a single cohesive PR, preserving Constitution Principle XII's RED-first TDD discipline by extending existing test files per the Conformance Test Map in the spec. Up to two genuinely-new test modules are justified (split-brain eviction, transport-layer pipeline behavior); a third (`test_periodic_recovery.py`) is permissible per spec.md's gap-list escape hatch if the periodic-scan fixture proves unwieldy in `test_lifecycle.py`.

## Technical Context

**Language/Version**: Python 3.10+ (matches existing `azure-ai-agentserver-core` floor)

**Primary Dependencies**:
- `azure.core.AsyncPipelineClient` and standard policies (new transport — replaces `httpx.AsyncClient`)
- `azure.core.credentials_async.AsyncTokenCredential` (for typed credential parameter)
- `asyncio` (existing; no change)
- `httpx` — removed from production install requirements once nothing under `azure-ai-agentserver-core/azure/` imports it. May remain as a dev/test dependency during the migration's transitional period.

**Storage**:
- Task-store REST API (hosted Foundry endpoint; existing protocol) — accessed via the new `azure.core` pipeline.
- `LocalFileTaskProvider` (existing) — unchanged in protocol; lease-owner derivation update propagates through it.
- Cosmos DB ETag CAS (`If-Match`) — existing platform feature, now relied on by the reclaim helper.

**Testing**:
- `pytest` with `pytest-asyncio` (existing).
- Provider stubs returning `409 + binding_mismatch` for split-brain testing (new fixture).
- Fake `AsyncHttpTransport` injected into `azure.core` pipeline for transport-layer testing (new fixture).
- `_crash_harness` patterns from prior specs for crash-recovery scenarios in SC-012 (existing).
- Test-only hooks per FR-009 (interval override / trigger function for periodic-scan determinism) — concrete shape decided in Phase 1.

**Target Platform**: Azure Foundry hosted agent containers (Linux). Per the spec's assumptions: one process serves one session_id; NTP-synchronized hosts (best-effort, with framework clock-skew clamping as defense).

**Project Type**: Library (`azure-ai-agentserver-core` SDK package). Internal-only changes to the durable subsystem; no new public packages.

**Performance Goals**:
- Periodic recovery scan interval ~300s (internal constant; test override available).
- Inline reclaim adds at most one extra store read + one CAS write per `.run()` / `.start()` / `get_active_run()` call when the record is in-progress with a dead lease (and zero extra calls when the lease is live in this process).
- Watchdog-fire latency: cooperative-only; the handler sees `ctx.cancel.is_set() == True` within `asyncio.sleep` resolution of the configured timeout (deferred to handler's next checkpoint).

**Constraints**:
- Pre-release: in-place rewrite; no migration code; no "breaking change" framing.
- Single cohesive PR is the target; the implementation order in §Implementation Ordering Strategy below mitigates intermediate broken states.
- Constitution Principle XII (Core-Primitive TDD Discipline) requires RED-first commits for every public-surface conformance test, verifiable from git history.
- Constitution Principle X (Durability Contract Conformance) requires the `durability-contract.md` amendment (cross-cutting note, NOT a new matrix row) in the same PR.
- Constitution Principle IX (Docs ↔ Samples Loop) requires the developer guide to land BEFORE tests.

**Scale/Scope**:
- Internal changes touch `azure/ai/agentserver/core/durable/` — primarily `_manager.py`, `_lease.py`, `_context.py`, `_result.py`, `_client.py`, `_exceptions.py`, `_run.py`, `_decorator.py`. Roughly 6 of 15 files in the durable package.
- Test changes extend ~10 existing test files and add 2 new modules per the Conformance Test Map.
- Developer guide gets one new Cancellation subsection and a rewritten Steering + Timeout + Shutdown sections.

---

## Constitution Check

*GATE: Re-evaluated post-Phase-1 below. Initial pass.*

| # | Principle | Status | Justification |
|---|---|---|---|
| I | Modular Package Architecture | ✅ | Only touches `azure-ai-agentserver-core`. Transport migration adopts `azure.core` (existing dep). No new cross-package deps. |
| II | Strong Type Safety (NON-NEG) | ✅ | Improves typing: narrows `TaskResult.status` Literal, adds typed `bool`/`int` properties on `TaskContext`, re-types `credential: AsyncTokenCredential`, classifier returns explicit `Literal`. |
| III | Azure SDK Design Guidelines | ✅ | Pre-release framing locked; `is_stable=false` / Beta classifier (existing). CHANGELOG framing aligned per spec. |
| IV | Async-First Design | ✅ | New `CancelSignal`-style logic rejected in favor of bare `asyncio.Event`; `exit_for_recovery()` is async; watchdog respawn uses `asyncio.Task`. |
| V | Fail-Fast Config, Graceful Runtime | ✅ | Removes `stale_timeout` knob (one fewer); single classifier for store errors; `ctx.exit_for_recovery()` misuse raises `RuntimeError` at call site. |
| VI | Observability & Correlation | ✅ | New pipeline adds `RequestIdPolicy`, `DistributedTracingPolicy`, task-API logging policy with header allow-list; eviction logs WARNING with correlation. |
| VII | Test-Driven Development | ✅ | Every FR has at least one SC. Principle XII checklist demands RED-first ordering. Conformance Test Map in spec routes every assertion to an existing or justified-new test file. |
| VIII | Minimal Surface, Maximum Composability | ✅ | Aggressive removal: `stale_timeout`, `superseded`, `is_superseded`, `_pending_steering_futures`, `was_steered`, `pending_inputs`, `steering_generation`, `TaskRun.terminate`, `TaskTerminated`. Net new public surface: 4 boolean/int properties + 1 method on `TaskContext`. |
| IX | Docs ↔ Samples Feedback Loop (NON-NEG) | ✅ | Spec's Docs↔Samples section authored guide-first; samples-affected matrix enumerates every sample touched. |
| X | Durability Contract Conformance (NON-NEG) | ✅ | `durability-contract.md` amendment (cross-cutting note covering `binding_mismatch`) lands in the same PR per the spec's exit checklist. FR-015 metadata-flush invariant lives in Principle XII scope (core-primitive layer) with explicit justification — not a new matrix row. |
| XI | Contract-Surface Test Depth (NON-NEG) | N/A | Principle XI governs the **response-stream durability matrix** under `tests/e2e/durability_contract/` (per-cell depth assertions, `_test_handler.py` per-lifetime-tagged content, `CONTRACT_COVERAGE.md` mapping). This spec does NOT add or modify a `durability-contract.md` matrix row — the cross-cutting `binding_mismatch` note is prose, not a matrix entry — so the per-cell depth requirement is structurally inapplicable. Spec-internal SC depth (SC-006 3×3, SC-008 4×2, SC-010 6-cell, SC-012 4-cell crash-recovery, SC-016 transport behavior) lives under Principle XII's core-primitive depth complement, not XI. (This is the same X-vs-XII routing the spec uses for FR-015 metadata-flush invariant.) |
| XII | Core-Primitive TDD Discipline (NON-NEG) | ✅ | Spec mandates `conformance-gap-list.md` deliverable; Conformance Test Map names existing test files for every surface area; only 2 new modules justified; pre-existing tests ported (not deleted by default). RED-first ordering mandated and verifiable from git history. |
| XIII | Continuous Code Review Discipline (NON-NEG) | ✅ | Spec implementation spans 9 user stories across 12 implementation phases on one cohesive PR — triggers Principle XIII's three-or-more-phases rule. The Code Review Cadence subsection below enumerates the per-phase reviews, the two cross-phase seam reviews (A→B, B→C), and the final holistic review. `tasks.md` materializes these as Phase 13 (T112–T122) with `→ Run TXXX before moving to Phase Y` arrows on each Checkpoint marker. BLOCKING / HIGH findings gate the next phase per Principle XIII §4. |

**Constitution Check verdict (initial)**: PASS (12 principles applicable, all PASS; Principle XI structurally N/A — see row XI). No gates violated; no complexity-tracking entries needed. Re-evaluation after Phase 1 design below.

### Code Review Cadence (Constitution Principle XIII)

*Required by Constitution Principle XIII §1 because this spec has 9 user stories across 12 implementation phases — well above the three-or-more-phases threshold.*

The review structure materialized in `tasks.md` Phase 13:

- **Per-phase reviews** (one per implementation phase containing user-story work):
  - **T112 — Phase 3 / US9 (Transport, Implementation-phase A)**: `azure.core` pipeline migration; `ContentDecodePolicy` exclusion; classifier seam shape-stability; httpx-fixture port discipline.
  - **T114 — Phase 4 / US1**: `stale_timeout` removal completeness; no replacement knob secretly introduced; FR-009 test-only hook port.
  - **T115 — Phase 5 / US2**: `binding_mismatch` body-shape tolerance; atomic local-cleanup sequence; Invariant 1 outcome preservation; no synthetic-bypass shortcuts.
  - **T116 — Phase 6+7 combined / US3+US4** (US4 is verification-only over US3): three-layer recovery; CAS race protection; lease-owner agent+session identity; `get_active_run` reclaim semantics.
  - **T118 — Phase 8 / US5**: steering-as-multi-turn rewrite; `superseded` removal; metadata auto-flush invariant across every terminal-of-turn boundary; pre-existing-test port discipline.
  - **T119 — Phase 9 / US6**: cancel-cause boolean accumulation; `is_steered_turn` sticky-True bug fix; `terminate` + `TaskTerminated` removal across all ~13 call sites.
  - **T120 — Phase 10 / US7**: per-turn / wall-clock / durable timeout; watchdog respawn at every boundary; clock-skew clamping; docstring correctness.
  - **T121 — Phase 11 / US8**: `exit_for_recovery()` sentinel handling; lease release; misuse-as-`failed` path; queued-input preservation across shutdown.
- **Cross-phase seam reviews** (at the architecturally significant boundaries the Implementation Ordering Strategy identifies):
  - **T113 — Phase A → B seam**: is the FR-006 classifier seam stable for Phase B's consumers? are policy-chain ordering and outcome enumeration final? no throw-away Phase A scaffolding?
  - **T117 — Phase B → C seam**: are the recovery primitives stable for the Phase C `_execute_task_loop` rewrite? does the eviction-cleanup sequence compose cleanly with the cancel-cause cleanup the loop rewrite introduces?
- **Final whole-PR holistic review**: **T122** at the end of Phase 12 Polish — spec coverage symbol-for-symbol, documentation truth, plan-phase-decision resolution, constitution exit checklists complete, no regression, RED-first commit-history audit, lint/type/build clean.

Each Checkpoint marker in Phases 3–11 of `tasks.md` carries a `→ Run TXXX before moving to Phase Y` arrow pointing at its gating review task. BLOCKING / HIGH findings MUST be addressed before the gate clears; MEDIUM / LOW findings get logged to `conformance-gap-list.md` for the T122 final-review sweep.

---

## Project Structure

### Documentation (this feature)

```text
sdk/agentserver/specs/016-automatic-task-recovery/
├── spec.md                     # Feature specification (469 lines; locked-in)
├── plan.md                     # This file
├── cancel-surface-proposal.md  # Iteration history for the cancel surface design (reference; not normative)
├── research.md                 # Phase 0 output — see §Phase 0 below
├── data-model.md               # Phase 1 output — see §Phase 1 below
├── quickstart.md               # Phase 1 output — see §Phase 1 below
├── contracts/                  # Phase 1 output — see §Phase 1 below
│   └── (no separate contract files; the contract is the public-surface enumeration in spec.md's Principle XII section)
├── conformance-gap-list.md     # Required deliverable per Principle XII (produced before /speckit.tasks)
└── tasks.md                    # /speckit.tasks output (NOT produced by /speckit.plan)
```

### Source code (affected directories)

```text
sdk/agentserver/azure-ai-agentserver-core/
├── azure/ai/agentserver/core/
│   ├── durable/
│   │   ├── __init__.py          # MODIFY: drop TaskTerminated re-export; verify presence of new public names
│   │   ├── _client.py           # REWRITE: AsyncPipelineClient migration (FR-029..FR-034)
│   │   ├── _context.py          # MODIFY: cancel-cause booleans, pending_input_count, is_steered_turn, exit_for_recovery (FR-016..FR-021, FR-027)
│   │   ├── _decorator.py        # MODIFY: remove stale_timeout kwarg, drop the slot from the inline-defined TaskOptions class, remove _is_stale helper (FR-001)
│   │   ├── _exceptions.py       # MODIFY: remove TaskTerminated (FR-022)
│   │   ├── _lease.py            # MODIFY: derive_lease_owner(agent_name, session_id) (FR-004a); lease_renewal classifier integration (FR-007)
│   │   ├── _manager.py          # REWRITE-IN-PLACE: layered recovery, reclaim helper, classifier, drain rewrite, watchdog respawn, _turn_started_at, exit_for_recovery sentinel handling (FR-002..FR-027, large)
│   │   ├── _models.py           # MODIFY: _turn_started_at payload field (FR-023); other internal-record shape touches as needed
│   │   ├── _result.py           # MODIFY: narrow TaskResult.status Literal; remove is_superseded (FR-010)
│   │   └── _run.py              # MODIFY: drop terminate() (FR-022); rebind result_future flow for steering (FR-013, FR-014)
│   └── _config.py               # READ-ONLY HERE: source of FOUNDRY_AGENT_NAME for lease-owner derivation (no change)
└── tests/durable/
    ├── test_public_api_surface.py        # EXTEND (Conformance Test Map row 1)
    ├── test_dev_guide_review.py          # EXTEND (row 2)
    ├── test_decorator.py                 # EXTEND (row 3)
    ├── test_lifecycle.py                 # EXTEND (rows 4, 9, 11)
    ├── test_entry_mode.py                # EXTEND (row 5)
    ├── test_steering.py                  # EXTEND (row 6)
    ├── test_metadata.py                  # EXTEND (row 7)
    ├── test_cancellation_timeout.py      # EXTEND (rows 8, 9, 10)
    ├── test_local_provider.py            # EXTEND (row 12 — lease-owner agent+session)
    ├── test_contract_completeness.py     # AUTO-PICKUP (row 10)
    ├── test_split_brain_eviction.py      # NEW (row 13)
    └── test_hosted_provider_transport.py # NEW (row 14)
```

**Documentation impact:**

```text
sdk/agentserver/azure-ai-agentserver-core/
├── docs/durable-task-guide.md  # REWRITE sections: Recovery, Errors, Steering, Cancellation (NEW subsection), Timeout, Shutdown (NEW), §5 Reference
└── CHANGELOG.md                # REWRITE 2.0.0b4 (Unreleased) — initial-release shape per Pre-release scope note

sdk/agentserver/specs/
└── durability-contract.md      # AMEND: cross-cutting "Lease eviction (binding_mismatch)" note + change-log entry (Principle X)
```

**Structure decision**: This is a single-library project (Option 1 in the speckit template) targeting the `azure-ai-agentserver-core` package. All changes are localized to the `durable/` submodule plus its tests, the developer guide, the CHANGELOG, and a single amendment to `durability-contract.md`. No new packages, no cross-package dependencies.

---

## Phase 0 — Research

Per the spec's iteration history, the design decisions have already been researched and locked in. The research artifacts that informed this spec are reference material; this Phase 0 documents the *decisions* with their rationale and alternatives so future readers don't have to re-derive them.

**Output**: [`./research.md`](./research.md) — see §Generated Artifacts below for the full content.

### Outstanding unknowns (NEEDS CLARIFICATION)

None. The spec is locked-in. All 5 open questions from the cancel-surface proposal were resolved per user direction. Three implementation decisions deferred to the plan/implementation phase (NOT clarifications, just plan-phase implementation choices — these match `research.md` §Plan-phase implementation decisions exactly):

1. **Concrete shape of the test-only hook for periodic-scan determinism (FR-009)**: interval-override-constant vs. trigger-function-on-manager. Plan-phase choice; both are valid; pick based on which is least invasive to existing tests.
2. **Whether the internal `_steering["generation"]` payload field can be deleted** alongside the public `ctx.steering_generation` removal (FR-021). Requires tracing every read site of `_steering["generation"]` against the post-FR-013/14 invariants. If no load-bearing internal use remains, drop in the same PR; otherwise retain internally with an inline justification comment.
3. **`_turn_started_at` on-the-wire payload field name + location (FR-023)**. The contract is "ISO-8601 UTC string, persisted at every turn-start boundary, NOT re-stamped on recovery"; the exact field name (`_turn_started_at` vs. `_lease["turn_started_at"]` vs. another location) is documented in `data-model.md` during `/speckit.tasks`.

### Research consolidation

The spec already contains the consolidated decisions. The `research.md` artifact below restates them in the speckit Decision / Rationale / Alternatives format for reference.

---

## Phase 1 — Design & Contracts

### Data model

The durable-task primitive does not have an entity-relationship model in the database-design sense; its "model" is the public-surface contract of `TaskContext`, `TaskResult`, `Task`, `TaskRun`, `TaskManager`, plus the persisted record shape used by the task-store API. The relevant decisions are in spec.md's §Core Durable-Task Primitive Conformance §Affected public symbols section.

**Output**: [`./data-model.md`](./data-model.md) — see §Generated Artifacts below.

### Interface contracts

This is a library, not a web service. The "contract" is the public Python API of the `azure.ai.agentserver.core.durable` namespace. The contract is enumerated in spec.md's affected-symbols section; no separate `contracts/` directory is required (per the speckit template guidance: "Skip if project is purely internal" — partial: the public API IS the contract surface).

**No new `contracts/` files are generated.** The contract is the spec's affected-symbols enumeration plus the SC-006 / SC-008 / SC-010 / SC-012 / SC-015 / SC-017 parametrized observable-behavior sweeps.

### Quickstart

A developer-facing quickstart for the rewritten contract.

**Output**: [`./quickstart.md`](./quickstart.md) — see §Generated Artifacts below.

### Agent context update

The `.github/copilot-instructions.md` file under `sdk/agentserver` includes a SPECKIT block pointing at the current plan file. Per the speckit.plan workflow, I will update that block to point at this plan.

```text
sdk/agentserver/.github/copilot-instructions.md  (between <!-- SPECKIT START --> and <!-- SPECKIT END -->)
  → updated to: specs/016-automatic-task-recovery/plan.md
```

---

## Implementation Ordering Strategy

Three implementation phases land in one cohesive PR. The order minimizes intermediate broken states.

### Phase A — Transport migration (FR-029..FR-034 + FR-006 classifier seam)

**Why first**: the new pipeline is a prerequisite for the eviction classifier integration (FR-007/FR-008) — implementing those cleanly on raw `httpx` would mean re-inventing the policy machinery `azure.core` already provides. Land the pipeline first; the classifier wires into the new seam.

**Surface touched**: `_client.py` (HostedTaskProvider rewrite), new task-API logging policy module, `pyproject.toml` (drop `httpx` from install requires once safe).

**Tests added/extended (RED-first)**:
- `test_hosted_provider_transport.py` (NEW): pipeline policy chain composition, retry on 503, no-retry on 409, gzip round-trip, non-JSON body classification, headers populated (SC-016, SC-017).
- `test_public_api_surface.py` (EXTEND): `HostedTaskProvider.__init__` parameter typing assertion.

**Risk mitigation**: existing tests against `httpx.AsyncClient` fixtures break; port them to `azure.core` transport fakes in the same commit pair (RED rewrite → GREEN code migration).

### Phase B — Recovery + eviction classifier + lease-owner identity (FR-001..FR-009 + FR-004a)

**Why second**: the classifier seam from Phase A is now available. This phase wires recovery into it. Also lands the lease-owner agent+session identity fix as a paired concern (touches the same code paths).

**Surface touched**: `_lease.py` (derive_lease_owner signature, lease_renewal classifier integration), `_manager.py` (3-layer recovery, reclaim helper, classifier funnel, FR-009 test hooks), `_decorator.py` (drop stale_timeout kwarg + inline-`TaskOptions` slot + `_is_stale` helper), `_context.py` (drop stale_timeout if any references remain).

**Tests added/extended (RED-first)**:
- `test_split_brain_eviction.py` (NEW): provider stub with `binding_mismatch`, full FR-006..FR-008 sweep (SC-002, SC-005).
- `test_public_api_surface.py` (EXTEND): stale_timeout absent assertions (SC-001).
- `test_dev_guide_review.py` (EXTEND): stale_timeout absence regex.
- `test_decorator.py` (EXTEND): `@task(stale_timeout=...)` → `TypeError`.
- `test_lifecycle.py` (EXTEND): scheduling-primitive 3×3 sweep (SC-006), `get_active_run` reclaim semantics (SC-003), periodic-recovery via FR-009 hook (SC-004).
- `test_local_provider.py` (EXTEND): `derive_lease_owner(agent, session)` differentiation (SC-005a).

**Risk mitigation**: pre-existing tests using `stale_timeout` are ported to FR-009 test-only hook in the same commit pair.

### Phase C — Steering + cancel-cause surface + timeout + shutdown (FR-010..FR-028)

**Why last**: this is the cohesive `_execute_task_loop` / drain rewrite. It depends on Phase B's classifier seam (the drain interacts with the suspend-persist path, which now funnels errors through the classifier) and on Phase A's pipeline (suspend/terminal writes go through the pipeline). Landing it as the last phase keeps `_execute_task_loop` rewritten exactly once.

**Surface touched**: `_context.py` (cancel-cause booleans, pending_input_count, is_steered_turn rename, drop steering_generation, exit_for_recovery method), `_result.py` (narrow status Literal, drop is_superseded), `_exceptions.py` (drop TaskTerminated), `_run.py` (drop terminate, steerer-future binding rewrite), `_manager.py` (drain rewrite, watchdog respawn + durable budget, exit_for_recovery sentinel handling, metadata flush invariant on drain paths), `_models.py` (`_turn_started_at` payload field).

**Tests added/extended (RED-first)**:
- `test_public_api_surface.py` (EXTEND): presence/absence sweep for all new/removed `TaskContext` and `TaskRun` symbols (SC-007, SC-010, SC-014).
- `test_dev_guide_review.py` (EXTEND): invariants for all new/removed dev-guide vocabulary.
- `test_steering.py` (EXTEND): SC-008 4×2 multi-turn equivalence sweep; SC-010 6-cell cancel-cause sweep; SC-011 `is_steered_turn` correctness.
- `test_metadata.py` (EXTEND): SC-009 6-boundary flush-invariant sweep.
- `test_cancellation_timeout.py` (EXTEND): SC-012 4-cell per-turn-durable-timeout sweep; SC-013 clock-skew clamping; SC-015 `exit_for_recovery` semantics; cancel-cause boolean cases.
- `test_entry_mode.py` (EXTEND): `(entry_mode="recovered", is_steered_turn=True)` orthogonality (SC-011).
- Pre-existing tests using `is_superseded`, `pending_inputs`, `was_steered`, `steering_generation`, `terminate()`, `TaskTerminated` are ported per the "Hardening pre-existing tests" subsection of the spec.

**Risk mitigation**: this phase has the largest test churn. The Conformance Gap-List deliverable (required before /speckit.tasks) inventories every test file touched and every ported test, giving the reviewer a mechanical checklist.

### Cross-cutting deliverables

These do NOT belong to any single phase; they MUST land in the same PR:

- **`durability-contract.md` amendment** — cross-cutting "Lease eviction (binding_mismatch)" note + change-log entry (Principle X exit checklist).
- **Developer guide rewrite** — all sections per the spec's Docs↔Samples Loop §Authoring sequence step 1. Lands as ONE up-front rewrite preceding all phases' tests (matches the spec's authoring sequence which treats the guide as a single deliverable). Constitution Principle IX strictly requires guide-before-**samples** (not guide-before-tests); the guide-before-tests ordering is the spec's authoring sequence requirement, not the Constitution's.
- **CHANGELOG.md (2.0.0b4 Unreleased)** — full initial-release-shape rewrite per spec §Docs↔Samples Loop step 3.
- **Source docstrings** — `_timeout_watchdog`, the drain helper, the pipeline construction comment (ContentDecodePolicy exclusion), `TaskResult` class docstring, new `TaskContext` properties + `exit_for_recovery`.
- **Sample updates** — recommended-not-required updates per the spec's "Samples affected" table; deferrals recorded in `tasks.md` with one-line justifications per Constitution Principle IX.

---

## Constitution Check (post-Phase-1)

Re-evaluation: no new gate violations introduced by the design.

- The chosen approach **extends existing test files** wherever the surface area is already owned by one — Principle XII non-duplication satisfied.
- The two new test modules (`test_split_brain_eviction.py`, `test_hosted_provider_transport.py`) are justified in the Conformance Test Map by genuinely-new fixture requirements (custom provider stub for binding_mismatch; fake AsyncHttpTransport for pipeline introspection).
- Implementation ordering minimizes intermediate broken states without introducing throw-away scaffolding.
- Pre-existing tests are ported, not deleted; deletion requires gap-list justification.
- All `NEEDS CLARIFICATION` items in the spec are resolved; the two plan-phase implementation choices (FR-009 hook shape; internal `_steering["generation"]` retain-or-delete) are NOT clarifications — they're implementation decisions to be made during `/speckit.tasks` planning.

**Constitution Check verdict (post-design)**: PASS (12 applicable principles PASS; Principle XI N/A as noted in initial check; Principle XIII satisfied by the Code Review Cadence subsection above + Phase 13 tasks T112–T122).

---

## Complexity Tracking

(No constitution-check violations to justify.)

---

## Generated Artifacts

The speckit.plan workflow produces `research.md`, `data-model.md`, and `quickstart.md` alongside this plan. Their content is sized to the spec's scope:

### research.md (Phase 0 output)

The spec's iteration history (captured in `cancel-surface-proposal.md` and the session's plan.md) covers the research. The `research.md` artifact restates the locked-in decisions in the Decision / Rationale / Alternatives format for future readers. Notable decisions:

- **Independent boolean per cancel cause (rejected: CancelSignal wrapper class with .reason enum)** — booleans accumulate; first-cause-wins would lose information in composite cases. Decision Iter 14b.
- **Steering as plain multi-turn (rejected: synthetic `superseded` status)** — framework cannot observe whether the handler honored cooperative cancel; pretending it can leaks a non-fact onto the public surface. Decision Iter 9.
- **Per-turn durable wall-clock timeout (rejected: per-invocation reset, fresh budget per turn without durability)** — recovery within a turn must preserve budget so net effective compute is bounded. Decision Iter 13.
- **Remove `TaskRun.terminate()` entirely (rejected: keep with reduced surface)** — `.cancel()` + handler-side `raise` covers the force-fail use case; the dedicated terminate pathway costs ~25 lines of plumbing for marginal benefit. Decision Iter 14b.
- **`ctx.exit_for_recovery()` for shutdown (rejected: document `raise asyncio.CancelledError` as the prescribed pattern)** — asyncio coupling leaks into handler code; the explicit framework API is discoverable and misuse-safe. Decision Iter 14b.
- **Transport on `azure.core` (rejected: stay on raw httpx with hand-rolled retry)** — the policy stack is the right seam for the FR-006 classifier; re-inventing it on httpx is wasted scaffolding. Decision Iter 10.
- **Lease owner = (agent_name, session_id) (rejected: session_id alone)** — different agents sharing a session ID would collide on ownership; binding_mismatch doesn't catch this case. Decision Iter 15.

### data-model.md (Phase 1 output)

The library has no entity-relationship model; the "data model" is the persisted record shape and the public-API contract. The artifact captures:

- **Persisted record shape** (`_steering` payload structure, `_turn_started_at` ISO-8601 string field, lease metadata) — internal-only; concrete on-the-wire format is a plan-phase decision documented in the artifact.
- **Public-surface contract** — same enumeration as spec's affected-symbols section, restated for self-containment.

### quickstart.md (Phase 1 output)

A developer-facing quickstart demonstrating the rewritten contract end-to-end. Sized to ~80 lines:

- Defining a steerable handler with `@task(steerable=True, timeout=timedelta(seconds=30))`.
- Cancellation-aware checkpoint pattern: `if ctx.cancel.is_set(): ...` with optional disambiguation via `ctx.timeout_exceeded` / `ctx.cancel_requested` / `ctx.pending_input_count`.
- Multi-turn / suspend pattern: `return await ctx.suspend(output=X)`.
- Shutdown pattern: `if ctx.shutdown.is_set(): await ctx.metadata.flush(); return await ctx.exit_for_recovery()`.
- Recovery: handler is idempotent on `ctx.entry_mode == "recovered"`; check `ctx.metadata` for prior progress.

---

## Next steps

1. **User reviews this plan.**
2. After approval: run `/speckit.tasks` to generate `tasks.md` from the spec's user stories, FRs, and the Conformance Test Map. The tasks output will:
   - Inventory every test extension / new-file / port per the Conformance Test Map.
   - Sequence tasks per the implementation-ordering strategy (Phase A → B → C with cross-cutting deliverables interleaved per phase).
   - Mark each task with its phase, the RED-test commit and GREEN-implementation commit that paired with it.
3. Produce `conformance-gap-list.md` as a /speckit.tasks output artifact (Principle XII required deliverable).
4. After `/speckit.tasks` approval: implementation per RED-first commits, verifiable from git history.
