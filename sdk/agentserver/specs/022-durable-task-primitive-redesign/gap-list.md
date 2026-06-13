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

(populated as implementation progresses)

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
