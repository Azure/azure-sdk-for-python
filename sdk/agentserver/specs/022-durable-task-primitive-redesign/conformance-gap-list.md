# Spec 022 — Conformance gap-list

Per Constitution Principle XII §2. For every FR / SC in `spec.md`,
this document records the extend-X-vs-new-Y test-file decision —
which existing test file gets extended OR which new test file gets
created to cover the FR/SC, with justification.

## Baseline (recorded 2026-06-13)

Pre-implementation full durable test suite: **511 passed, 5 skipped, 0 failed**.

Phase 1 RED additions are expected to land on top of this baseline
(net +25-30 new test cases initially failing; turn GREEN as Phase 2-7
implementation lands).

## FR / SC → test file mapping

| Item | Test file | Extend / New | Justification |
|---|---|---|---|
| FR-001 | tests/durable/test_decorator_surface.py | NEW | The decorator-allow-list contract is new; existing `test_decorator.py` (if any) covers older semantics. |
| FR-002 | tests/durable/test_decorator_surface.py | NEW | Same — `@multi_turn_task` is a new decorator with its own kwarg matrix. |
| FR-003 | tests/durable/test_decorator_surface.py | NEW | Handler-signature validation is a new contract enforced at decoration time. |
| FR-004 / FR-005 | tests/durable/test_decorator_surface.py + tests/durable/test_input_precondition.py | NEW | Identifier supply is in test_decorator_surface; `if_last_input_id` precondition belongs in dedicated test_input_precondition. |
| FR-006 | tests/durable/test_contract_completeness.py | EXTEND | `Task.options` non-existence is a meta-test grep assertion. |
| FR-007 | tests/durable/test_multi_turn_raise.py | NEW | Return-is-implicit-suspend is the new multi-turn return semantic. |
| FR-008 / FR-009 | tests/durable/test_contract_completeness.py | EXTEND | Negative-presence assertions (no `ctx.suspend`, no `ctx.end_chain`). |
| FR-010 / FR-011 / FR-012 / FR-013 | tests/durable/test_multi_turn_raise.py | NEW | New raise semantics (chain stays alive; queued steerers promote). |
| FR-014 | tests/durable/test_multi_turn_raise.py | NEW | One-shot failure shape. |
| FR-015 | tests/durable/test_multi_turn_raise.py | NEW | Structured failure log assertion. |
| FR-016-021 | tests/durable/test_contract_completeness.py | EXTEND | Negative-presence (no Task.get / TaskSnapshot / TaskResult / Suspended / TaskStatus / OutputTooLarge in `__all__`). |
| FR-022 / FR-023 / FR-024 | tests/durable/test_active_run.py | NEW | get_active_run + delete classmethod semantics are new. |
| FR-025-032 | tests/durable/test_persistence.py | NEW | New payload-key write rules (no output/error persistence; clear input on suspend). |
| FR-033-036 | tests/durable/test_inline_recovery.py | NEW | Recovery semantics with persisted input. |
| FR-037 | tests/durable/test_cancellation_matrix.py | NEW | Queued-steerer cancel is a new branch. |
| FR-038 | tests/durable/test_cancellation_matrix.py | NEW | Cooperative-only timeout signaling. |
| FR-039 / FR-058 | tests/durable/test_cancellation_matrix.py | NEW | `TaskDeferred` is a new exception. |
| FR-040 | tests/durable/test_contract_completeness.py | EXTEND | `ctx.shutdown` presence assertion. |
| FR-041-043 | tests/durable/test_retry.py | NEW | Retry semantics differ post-exhaustion per primitive. |
| FR-044 / FR-045 / FR-046 | tests/durable/test_metadata_flush.py | NEW | TaskMetadata facade + auto-flush + one-shot locality. |
| FR-047 / FR-048 | tests/durable/test_taskrun_shape.py | NEW | Slim TaskRun shape. |
| FR-049 / FR-050 | tests/durable/test_contract_completeness.py | EXTEND | `/tasks/resume` absence + docstring fix. |
| FR-051 | tests/durable/test_decorator_surface.py | NEW | Decorator allow-list. |
| FR-052 | tests/durable/test_contract_completeness.py | EXTEND | `.run()` return-type assertion. |
| FR-053 | tests/durable/test_multi_turn_raise.py | NEW | 7-step ordering. |
| FR-054-064 | tests/durable/test_cancellation_matrix.py + tests/durable/test_inline_recovery.py | NEW | Cancellation matrix + inline-recovery. |
| FR-065 | tests/durable/test_contract_completeness.py | EXTEND | Internal-only cleanup grep assertion. |
| FR-066-068 | tests/integration_responses/test_durable_orchestrator_v2.py | NEW (in responses package) | Responses-package migration verification. |
| FR-068a | NO TEST (Q16) | n/a | Local provider requires no code change; covered by existing test_local_provider.py staying green. |
| FR-068b / FR-068c | tests/e2e/test_durable_*_live.py + tests/e2e/test_durable_langgraph_smoke.py + tests/test_durable_samples_structure.py + tests/test_samples_shippable_bar.py (all in invocations package) | EXTEND existing + NEW langgraph smoke | Invocations samples migration verification. |
| FR-068d | Hand-off issue / cross-branch PR | n/a (cross-branch tracking only) | Demo lives on `feature/agentserver-durable-agent-demo`. |
| FR-069 | tests/durable/test_decorator_surface.py + mypy/pyright type-check test | NEW | Class split static-type-safety assertion. |
| FR-070 | tests/durable/test_metadata_flush.py + tests/durable/test_contract_completeness.py | NEW + EXTEND | JSONValue export + TaskMetadata value-type constraint. |
| FR-071 | tests/durable/test_exception_taxonomy.py | NEW | TypedDict exports + TaskFailed.error typing. |
| FR-072 | tests/durable/test_contract_completeness.py | EXTEND | TaskContext preserved-members enumeration. |
| FR-073 | tests/durable/test_decorator_surface.py | NEW | RetryPolicy shape (regular class, no @dataclass). |
| FR-074 | tests/durable/test_exception_taxonomy.py | NEW | TaskNotFound/TaskPreconditionFailed not in __all__. |
| FR-075 | tests/durable/test_exception_taxonomy.py | NEW | TaskFailed.__cause__ is None. |
| FR-076 | tests/durable/test_input_precondition.py | NEW | LastInputIdPreconditionFailed shape. |
| FR-077 | tests/durable/test_exception_taxonomy.py | NEW | Bare-vs-fielded exception rule. |
| SC-001 | tests/durable/test_persistence.py | NEW | Zero-persistence assertion. |
| SC-002 | tests/durable/test_active_run.py | NEW | Sequential multi-turn metadata accumulation. |
| SC-003 | tests/durable/test_multi_turn_raise.py | NEW | Chain stays alive across raises. |
| SC-004 | tests/durable/test_inline_recovery.py | NEW | Crash recovery reproduces handler-input pair. |
| SC-005 | tests/durable/test_active_run.py | NEW | get_active_run exact match. |
| SC-006 / SC-007 | tests/durable/test_contract_completeness.py | EXTEND | Grep-clean invariants. |
| SC-008 | tests/integration_responses/test_durable_orchestrator_v2.py | NEW | 6-row matrix coverage. |
| SC-009 / SC-009a | gap-list.md tracking (audit-only) + invocations sample tests | EXTEND | Audit completion + sample verification. |
| SC-010 | tests/durable/test_multi_turn_raise.py | NEW | 7-step ordering E2E. |
| SC-011 | tests/durable/test_metadata_flush.py | NEW | Cross-turn metadata propagation. |
| SC-012 | tests/durable/test_retry.py | NEW | Retry conformance. |
| SC-013 | tests/durable/test_entry_mode.py | EXTEND | Entry-mode matrix. |
| SC-014 | tests/durable/test_cancellation_matrix.py | NEW | Cancellation matrix. |
| SC-015 | tests/durable/test_inline_recovery.py | NEW | Inline-recovery algorithm. |
| SC-016 | tests/durable/test_decorator_surface.py + mypy/pyright test | NEW | Public-surface type system. |
| SC-017 | tests/durable/test_exception_taxonomy.py | NEW | Exception public-surface. |
| SC-018 | tests/durable/test_decorator_surface.py | NEW | Decorator argument validation. |

## Test files created (this design)

13 NEW test files in `azure-ai-agentserver-core/tests/durable/`:
- test_decorator_surface.py
- test_input_precondition.py
- test_multi_turn_raise.py
- test_retry.py
- test_metadata_flush.py
- test_persistence.py
- test_exception_taxonomy.py
- test_cancellation_matrix.py
- test_active_run.py
- test_inline_recovery.py
- test_taskrun_shape.py

2 EXTENDED test files:
- test_contract_completeness.py (Principle XII §2 meta-test)
- test_entry_mode.py

1 NEW in responses package:
- tests/integration/test_durable_orchestrator_v2.py

5 EXTENDED in invocations package:
- tests/e2e/test_durable_research_live.py
- tests/e2e/test_durable_multiturn.py
- tests/e2e/test_durable_copilot_live.py
- tests/test_durable_samples_structure.py
- tests/test_samples_shippable_bar.py

1 NEW in invocations package:
- tests/e2e/test_durable_langgraph_smoke.py
