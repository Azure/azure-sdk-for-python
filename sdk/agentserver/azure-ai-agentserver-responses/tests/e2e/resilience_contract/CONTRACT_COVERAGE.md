# Resilience Contract — Test Coverage Matrix

**Purpose**: Map every normative clause in `sdk/agentserver/specs/resilience-contract.md` to the conformance test that verifies it. Empty cells are explicit findings — they MUST be filled before the next contract change ships, or the test gate at `test_contract_completeness.py` will fail.

This document is the answer to "what assertion proves we honour clause X". Reviewers checking a contract change consult this matrix to find the test they need to keep green; new contract clauses MUST land with a corresponding test entry here.

The matrix was authored during the Spec 014 Phase 9 follow-up reflection (the streaming-recovery-continuity bug slipped past the conformance suite because shape-only assertions weren't sensitive to content drift). It is enforced by the **completeness meta-test** (`test_contract_completeness.py`) which parses both the contract doc and this matrix and asserts no clause appears in one but not the other.

---

## How to read

Each row is one normative claim from `resilience-contract.md`. Columns:

- **Clause** — the claim, paraphrased from the contract doc with a section anchor.
- **Test file(s) and function(s)** — the conformance test(s) that verify the claim.
- **Assertion dimension** — `event sequence` (streaming order), `event content` (delta text / item shape / etc.), `seq monotonicity` (cross-attempt), `response.output content` (assembled snapshot), `response.status` (terminal state), `response.error` (failure fields), `metadata` (resilience.metadata persistence), `chain id` (conversation_chain_id stability), `composition guard` (startup validation), `meta` (test discipline).

A clause may have MULTIPLE rows if it spans dimensions; a test may appear in MULTIPLE rows if it covers multiple claims.

---

## Per-row matrix contracts (§ The matrix)

| Clause | Test | Dimension |
|---|---|---|
| Row 1 Path A: handler completes within grace; natural terminal | `test_row_1_path_a.py::test_row_1_path_a` (stream=F/T) | response.status; event sequence (stream=T) |
| Row 1 Path B: hand handler to resilient-task primitive; next lifetime re-invokes with `entry_mode="recovered"` | `test_row_1_path_b.py::test_row_1_path_b` (stream=F/T) | response.status (post-restart `completed`) |
| Row 1 Path B (stream=T): pre-crash events survive in `GET ?stream=true&starting_after=0` | `test_streaming_recovery_continuity.py::test_pre_crash_deltas_survive_recovery` | event sequence; event content; seq monotonicity |
| Row 1 Path C: next lifetime re-invokes with `entry_mode="recovered"` | `test_row_1_path_c.py::test_row_1_path_c` (stream=F/T) | response.status |
| Row 1 Path C (stream=T): pre-crash events survive cross-attempt assembly | `test_streaming_recovery_continuity.py` | event content; seq monotonicity |
| Row 1 Path C with SSE keep-alive enabled: a resilient task MUST still be created and recovery MUST succeed regardless of `SSE_KEEPALIVE_INTERVAL` (the hosted condition); the recovered lifetime produces the terminal | `test_row_1_keep_alive.py::test_row_1_keep_alive_path_c` (stream=F/T) | response.status; response.output content (recovered `L1_done`) |
| Row 2 Path A: handler completes within grace | `test_row_2_path_a.py::test_row_2_path_a` (stream=F/T) | response.status |
| Row 2 Path B: in-process shutdown loop marks failed with `code=server_error`; respond to waiting clients | `test_row_2_path_b.py::test_row_2_path_b` (stream=F/T) | response.status; response.error.code |
| Row 2 Path C: next-lifetime mark-failed with `code=server_error` | `test_row_2_path_c.py::test_row_2_path_c` (stream=F/T) | response.status; response.error.code |
| Row 2: pre-crash stream events are within-process only (no resilient stream provider auto-composed when `resilient_background=False`); cross-lifetime stream-content survival is NOT a Row 2 promise. The Row 2 contract surface for Path C is the response-store `failed` snapshot covered by `test_row_2_path_c.py`. | n/a | n/a |
| Row 3 Path A: handler completes within grace | `test_row_3_path_a.py::test_row_3_path_a` (stream=F/T) | response.status |
| Row 3 Path B: foreground mark-failed; respond to original connection | `test_row_3_path_b.py::test_row_3_path_b` (stream=F/T) | response.status; response.error.code |
| Row 3 Path C: foreground mark-failed via Path-C fallback | `test_row_3_path_c.py::test_row_3_path_c` (stream=F/T) | response.status; response.error.code |
| Row 4 Path A: handler completes; ephemeral, GET returns 404 | `test_row_4_path_a.py::test_row_4_path_a` (stream=F/T) | response.status (returned inline); GET 404 |
| Row 4 Path B: best-effort failed marker on live wire (MAY) | `test_row_4_path_b.py::test_row_4_path_b` (stream=F/T) | response.status (best-effort) |
| Row 4 Path C: no persisted state, no next-lifetime action | `test_row_4_path_c.py::test_row_4_path_c` (stream=F/T) | meta (n/a verification) |

---

## Streaming sub-contract (§ Streaming sub-contract)

| Clause | Test | Dimension |
|---|---|---|
| Server rule 1: every emitted SSE event MUST be appended to resilient stream provider BEFORE wire flush | Implicit via Row 1 Path B/C stream=T (assembled stream replay assertions) | event sequence |
| Server rule 2: `GET /responses/{id}?stream=true&starting_after=<event_id>` returns events strictly after `<event_id>` then live-tails | `test_streaming_recovery_continuity.py` (uses starting_after=0) | event sequence |
| Server rule 2: GET-reconnect for Row 2 stream=T | n/a — Row 2 has no resilient stream provider (resilient_background=False short-circuits the FileStreamProvider auto-compose in `_routing.py`), so Row 2's stream events are within-process best-effort only. Cross-lifetime stream survival is NOT a Row 2 promise (the contract surface for Row 2 Path C is the response-store `failed` snapshot, not the persisted stream). | n/a |
| Server rule 3: recovered handler emits `response.in_progress` reset event as first event | `test_streaming_recovery_continuity.py::test_pre_crash_deltas_survive_recovery` (asserts post-recovery in_progress with seq > pre-crash max) | event sequence |
| Server rule 3: reset event carries corrected output_items reflecting post-recovery state | `test_reset_event_content.py::test_reset_event_carries_corrected_output_items` (Spec 032 B1 — real crash; asserts the post-recovery `response.in_progress` event's `response.output` carries the seeded/corrected items) | event content |
| Server rule 4: event ids stable across recovery; recovered events get fresh monotonic ids picking up after last pre-crash id | `test_streaming_recovery_continuity.py` (asserts strict monotonic seq across attempts) | seq monotonicity |
| Client-side rule: client MUST reset accumulator on every `response.in_progress` after the first | n/a (client library concern; not framework-side) | n/a |
| Reconnection semantics: client resumes from last-seen event id without missing/duplicating events | `test_streaming_recovery_continuity.py` (verified via GET starting_after=0 returning the full assembled stream with no duplicates) | event sequence; seq monotonicity |
| **NEW (T-173):** Output_item slot reuse on recovery — recovered handler's `output_item.added` at a previously-used `output_index` correctly triggers snapshot replacement semantics | `test_output_item_slot_reconciliation.py` | event content; response.output content |

---

## Recovery stream gating & drop precondition (Spec 026 — § Streaming sub-contract clause 5 + § Recovery precondition)

| Clause | Test | Dimension |
|---|---|---|
| **Single `response.created` per resilient stream** — `response.created` is appended to the resilient stream provider only when the stream is empty; a recovered handler that re-emits `response.created` has it suppressed at the provider write, so a replaying client observes `response.created` exactly once | `test_streaming_recovery_continuity.py::test_pre_crash_deltas_survive_recovery` (asserts the fully-assembled `starting_after=0` stream contains exactly one `response.created`) + `tests/unit/test_spec026_created_gate.py` (unit: `last_cursor() is None` gates the append — permits on empty, suppresses once non-empty) | event sequence; single-created |
| **Recovered handler emits `response.in_progress` reset as first recovered event** (NOT a second `response.created`) | `test_streaming_recovery_continuity.py::test_pre_crash_deltas_survive_recovery` (asserts post-recovery `response.in_progress` with seq > pre-crash max) | event sequence |
| **Recovery precondition (persisted response required)** — the framework re-invokes the handler only if the response was resiliently created; a definitively-absent response (typed not-found) is dropped (no re-invocation, no `response.*` events, no terminal); transient/ambiguous store errors are NOT dropped | `test_recovery_drop_when_unpersisted.py` (real SIGKILL in the pre-create window → restart → asserts handler NOT re-invoked + `GET` 404) | recovery drop |
| Drop **gate** runs before the stream-vs-non-stream dispatch (applies to both modes) | Code-position verified; conformance-tested via `stream=False` (the bg+streaming path persists the response early at `POST` for reconnect, so its never-persisted window is not deterministically reproducible) | recovery drop |

---



| Clause | Test | Dimension |
|---|---|---|
| Recovered handler sees `context.resilience.entry_mode == "recovered"` | Implicit via `test_row_1_path_b/c` (recovery happens → terminal `completed`); per-lifetime tag in `_test_handler.py` derives lifetime from `entry_mode` | meta |
| `context.resilience.is_recovery == True` on recovery | Same as above (convenience alias of entry_mode) | meta |
| `context.resilience.metadata` contents from prior invocations survive crash (when paired with flush) | `test_metadata_survives_recovery.py::test_metadata_visited_marker_survives_recovery` (real crash; visited=[0,1] round-trip) | metadata |
| `metadata[key] = value` plus `await metadata.flush()` makes the key visible to recovered invocation | `test_metadata_survives_recovery.py` (same test — visited list proves the flushed key is visible to the recovered lifetime) | metadata |
| Keys with `_framework.` prefix are not visible to handler code | `tests/unit/test_resilience_context.py::test_filtered_metadata_hides_framework_keys` (helper-internal unit) | meta |
| Framework does NOT impose a watermark schema | n/a (negative claim — no test required) | n/a |
| Recovered handler emits `response.in_progress` reset as first event | `test_streaming_recovery_continuity.py` | event sequence |
| At-most-once side effects via metadata + flush + dedup token check | `test_metadata_survives_recovery.py` (Spec 032 B5: the framework guarantee — a flushed metadata key survives crash and serves as a dedup fence — IS the visited=[0,1] proof; external side-effect at-most-once is a handler/guide concern, not a framework contract) | metadata |
| `run_attempt` is per-process retry counter; does NOT survive recovery (see backlog B10) | **DOC-ONLY** — no behavioural test (and current behaviour is acknowledged-broken pending B10) | meta |
| **NEW (T-173):** `context.conversation_chain_id` is stable across attempts | `test_conversation_chain_id_stability.py` | chain id |
| **NEW (Spec 025 §A.4):** `await context.exit_for_recovery()` (unified recovery primitive) leaves the response `in_progress` for next-lifetime recovery — works in any handler shape; the orchestrator translates `ResponseExitForRecovery` to the core sentinel | `test_explicit_exit_for_recovery.py::test_explicit_exit_for_recovery_recovers` (stream=F/T) | response.status (post-restart `completed`) |

---

## Composition rules (§ Composition rules)

| Clause | Test | Dimension |
|---|---|---|
| `resilient_background=True` + non-persistent `store` (explicit `InMemoryResponseProvider`) → startup error | `tests/unit/test_composition_guard.py::*` (5 tests) + `tests/integration/test_startup_composition_guard.py::*` (2 tests) | composition guard |
| `store=true` requests accepted without ResponseStore → startup error | n/a — UNREACHABLE by construction (Spec 032 B2): `store=None` always resolves to a persistent `FileResponseStore` (`_routing.py` `store=None` branch); there is no missing-`ResponseStore` state to guard. The only reachable missing-provider case (explicit non-resilient store + resilient_background) IS guarded + tested above. | composition guard |
| `stream=true` requests accepted without streaming-capable transport → startup error | n/a — UNREACHABLE by construction (Spec 032 B2): the streams registry is auto-configured at startup (`_configure_streams_registry`); there is no missing-transport state to guard. | composition guard |
| `resilient_background=True` without ResilientStreamProviderProtocol for streamed resilient responses → startup error | Implicit via the responses package's auto-compose in `_routing.py` (FileStreamProvider when needed). Negative test absent. | composition guard |

---

## Test discipline (§ Constitution + § Spec template)

| Clause | Test | Dimension |
|---|---|---|
| Every (row × applicable path) cell has a paired conformance test | `test_contract_completeness.py::test_every_row_path_combination_has_test` | meta |
| Conformance tests use real signals (no synthetic-crash shortcuts) | `test_contract_completeness.py` (filename + handler-import audit) | meta |
| **NEW (Spec 024 Phase 1 step 7):** No race window on fast-handler completion (Rows 2/3 unified resilient-task path) | `test_no_fast_handler_race.py::test_no_fast_handler_race_row_2`, `::test_no_fast_handler_race_row_3` | race-guard |
| **NEW (T-174):** Per-cell tests verify the row's full contract surface — events + content + response.output as applicable, not just terminal status | `test_contract_completeness.py::test_per_cell_tests_assert_more_than_just_status` (Spec 032 FR-001 — now a HARD gate, not a soft warning) | meta |
| **NEW (T-174):** Every contract clause in `resilience-contract.md` has an entry in CONTRACT_COVERAGE.md | `test_contract_completeness.py::test_contract_coverage_matrix_exists_and_is_non_trivial` | meta |

---

## Row 11 — Developer checkpoint write (§ Per-row contracts → Row 11)

Row 11 is the checkpoint-write extension of Row 1 (`store=true, background=true,
resilient_background=True`). It covers `yield stream.checkpoint()` in the
one-OutputItem-per-phase pattern. Cutpoints C1/C3 require real crashes and are
exercised e2e (Path B graceful `exit_for_recovery` + Path C SIGKILL); C2 is a
documented provider-atomicity limitation; C4/C5 are unit-tested.

| Clause | Test | Dimension |
|---|---|---|
| Row 11 Path A: all phases checkpoint + complete; final `response.output` = every fresh-entry phase | `test_row_11_path_a.py::test_row_11_path_a` (stream=F/T) | response.output content (per-lifetime markers) |
| Row 11 Path B (C1=`after_checkpoint`): graceful shutdown after a successful checkpoint → `exit_for_recovery` → recovery resumes at next phase | `test_row_11_path_b.py::test_row_11_path_b[C1=after_checkpoint]` (stream=F/T) | response.output content; per-lifetime markers |
| Row 11 Path B (C3=`before_checkpoint`): graceful shutdown before a checkpoint → un-checkpointed phase re-runs | `test_row_11_path_b.py::test_row_11_path_b[C3=before_checkpoint]` (stream=F/T) | response.output content; per-lifetime markers |
| Row 11 Path C (C1=`after_checkpoint`): SIGKILL after a successful checkpoint → recovery resumes at next phase (no loss/dup) | `test_row_11_path_c.py::test_row_11_path_c[C1=after_checkpoint]` (stream=F/T) | response.output content; per-lifetime markers |
| Row 11 Path C (C3=`before_checkpoint`): SIGKILL before a checkpoint → un-checkpointed phase re-runs (central guarantee) | `test_row_11_path_c.py::test_row_11_path_c[C3=before_checkpoint]` (stream=F/T) | response.output content; per-lifetime markers |
| C2: mid-checkpoint-write crash exposes prior-or-new committed snapshot, never a torn one (FileResponseStore atomic `os.replace`) | **LIMITATION** — documented in `docs/resilience-contract.md` § Row 11 → C2; no torn-write recovery asserted (provider commits atomically) | provider atomicity |
| C4: checkpoint event after terminal is dropped; terminal snapshot wins; no exception | `tests/unit/test_checkpoint.py` (post-terminal drop) | event ordering |
| C5: provider `update_response` failure during `checkpoint()` is swallowed; recovery sees the prior snapshot | `tests/unit/test_checkpoint.py` (swallow-on-failure) | provider failure |
| Recovery deferral (`exit_for_recovery`) MUST NOT overwrite the last checkpoint snapshot with a pre-terminal record | `test_row_11_path_b.py` (stream=F asserts the checkpointed phase survives as `L0` after deferral) | response.output content |
| `checkpoint()` gated to resilient background (`resilient_background` + `store` + `background`); no-op otherwise | `tests/unit/test_checkpoint.py` (gate) | gate |

---

## Response.output content correctness (§ For polled / non-streaming clients)

The contract doesn't enumerate response.output content as a separate clause — it's implied by "the handler's output reaches the client". For stream=false cells, this is what the client SEES. Tests for this dimension need explicit response.output assertions; pure `status` assertions don't catch wrong-content bugs.

| Cell | Test | Dimension |
|---|---|---|
| Row 1 stream=F Path A: response.output reflects fresh handler's intent | **GAP** | response.output content |
| Row 1 stream=F Path C: response.output reflects recovered handler's intent | **GAP** | response.output content |
| Row 2 stream=F Path A: response.output reflects fresh handler's intent | **GAP** | response.output content |
| Row 3 stream=F Path A: response.output reflects fresh handler's intent | **GAP** | response.output content |
| Covered en masse | `test_response_output_content_correctness.py` | response.output content |

---

## Gaps summary (drives T-173)

**Status (post Spec 032):** the T-173 cross-cutting tests below now EXIST, and the Spec 032 audit closed the remaining genuine recovery gaps (see the Spec 032 section). The historical T-173 plan is retained for provenance:

1. **`test_streaming_recovery_continuity.py`** (already exists — T-170 baseline). Generalize to Row 2 in T-172 if scope permits.
2. **`test_metadata_survives_recovery.py`** (NEW T-173) — covers the recovery-handler-entry metadata clauses + the at-most-once side-effect pattern.
3. **`test_output_item_slot_reconciliation.py`** (NEW T-173) — covers streaming sub-contract server rule 3 (reset event payload reflecting post-recovery state) and the slot reuse client-side rule.
4. **`test_conversation_chain_id_stability.py`** (NEW T-173) — covers chain id stability across attempts.
5. **`test_response_output_content_correctness.py`** (NEW T-173) — covers all stream=F cells' response.output assertions.

T-172 (extend existing per-cell tests) adds content/continuity assertions to the existing Row 1/2/3 Path B/C stream=T tests so they don't rely solely on `status`.

---

## Change control

When `resilience-contract.md` changes:

1. Update this matrix with the new clause and its test entry.
2. Add the test (RED-first per Constitution Principle X) and confirm it goes GREEN with the implementation.
3. Run `test_contract_completeness.py` — the meta-test fails if any contract clause appears in `resilience-contract.md` but not in this matrix.
4. Land the implementation, contract amendment, test, and matrix update as a single PR.

---

*Authored during Spec 014 Phase 9 follow-up (T-171). Reflection that motivated this matrix: `~/.copilot/session-state/.../files/conformance_gap_analysis.md`.*

---

## Spec 032 — Conformance audit additions (depth-gate + recovery gaps)

This section records the Spec 032 reconciliation: the Principle XI depth gate is
now a HARD gate (`test_per_cell_tests_assert_more_than_just_status`), the stale
`**GAP**`/`TO BE ADDED` markers above were corrected to the tests that already
closed them, and the remaining genuine recovery gaps were filled.

| Clause | Test | Dimension |
|---|---|---|
| Reset event carries corrected output items after recovery (streaming clause 3, payload) | `test_reset_event_content.py` (B1 — real crash) | event content |
| Recovery precondition: a TRANSIENT store error during the recovery pre-fetch MUST NOT drop (proceed with `persisted_response=None`) | `test_recovery_precondition_transient.py` (B7 — real crash + fault-injecting store) | recovery gate |
| Client cancel DURING a recovered invocation settles to `cancelled` (client_cancelled cause, real signal) | `test_client_cancel_during_recovery.py` (B3 — real crash + real cancel endpoint) | response.status; cause |
| Path B proves the GRACEFUL grace-exhaustion handoff distinct from a Path-C SIGKILL fallback | `test_row_1_path_b.py::test_row_1_path_b_graceful_exit_not_sigkill` (B6 — clean exit, not SIGKILL) | shutdown path |
| `context.persisted_response` is seeded on recovery | Proven-by-consequence (B4): `test_row_11_path_c.py` resume markers + `test_reset_event_content.py` both FAIL if seeding is broken | recovery seeding |
| `response.created` idempotency across real crash recovery (single created per resilient stream) | `test_streaming_recovery_continuity.py` (B8 — asserts exactly one `response.created` after recovery) + `tests/e2e/test_recovery_idempotent_create.py` (provider layer) | event sequence |
| Per-cell tests MUST verify the row's contract surface, not terminal status alone | `test_contract_completeness.py::test_per_cell_tests_assert_more_than_just_status` (Spec 032 FR-001 — HARD gate) | meta |

---

## Conformance gap closure — request-carried `agent_reference` (hosted-shaped input)

| Clause | Test | Dimension |
|---|---|---|
| Row 1 Path C with a request-carried `agent_reference` (the hosted gateway-injected `AgentReference` model): resilient start MUST still create a resilient task and recover after SIGKILL — i.e. the model-typed `agent_reference` must not break resilient-input serialization and silently degrade to a non-resilient `asyncio.create_task` | `test_recovery_with_agent_reference.py::test_row_1_path_c_recovers_with_agent_reference` (stream=F/T) | recovery; resilient-input serialization |

This closes the gap that let the hosted `TypeError: Object of type AgentReference
is not JSON serializable` resilient-start failure ship: every other resilience
test sends no `agent_reference` (`{}` sentinel) or a plain string, so none
exercised the model form through the (provider-agnostic) resilient-input
serialization. Unit-level guard: `tests/unit/test_resilient_orchestrator.py::TestSplitRuntimeRefsSerializable`.

---

## Conformance gap closure — recovered-input parity (Spec 033 FR-002b)

| Clause | Test | Dimension |
|---|---|---|
| A recovered handler observes the IDENTICAL request-scoped inputs as fresh entry: `context.request` (incl. request-only fields), `client_headers`, `query_parameters`, and `get_input_items()` (resolved + unresolved) — none dropped or altered on recovery | `test_recovered_input_parity.py::test_recovered_input_parity` (Spec 033 — real SIGKILL; records & diffs lifetime-0 vs lifetime-1 observed inputs) | recovery; request-scoped input content |

This closes the latent `client_headers` / `query_parameters` drop-to-`{}` bug on
recovery and pins the typed resilient-boundary's reconstruction fidelity
(`responses-resilience-spec.md` §5.3 / §8.2). Reconstruction-level unit guard:
`tests/e2e/test_recovery_reconstruction.py::test_reconstruct_preserves_client_headers_and_query`.

---

## Conformance gap closure — crash WHILE steering (steering-feature resilience)

| Clause | Test | Dimension |
|---|---|---|
| A crash (SIGKILL) that lands while a **steered turn is mid-flight** (core `drain_in_progress`) MUST recover the steered response to terminal — the steered response must not be orphaned in `in_progress`. Both the superseded prior turn and the steered turn reach `completed` after restart, and the recovered steered turn re-runs the steered input (recovered `L1` lifetime) | `test_crash_while_steering.py::test_crash_while_steering_recovers_steered_turn` (steerable conversation; real SIGKILL mid-drain via `CrashHarness`) | response.status (both turns `completed`); recovery lifetime; steered input fidelity |

This replaces the retired hosted battery `verify_crash_steer.py`, which used
steering only as a crash-*delivery* mechanism (obsolete: a bare `crash` pinned
via `agent_session_id` lands on the same sandbox). The prior "steered turn stuck
`in_progress`" observation (`finding-t5`) was an artifact of steering the literal
`crash` sentinel as the turn input (the recovered turn re-ran `crash`), not a
framework steered-turn-recovery bug — this deterministic test proves normal
steered-turn crash recovery holds.
