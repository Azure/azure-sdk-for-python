# Durability Contract — Conformance Specification

**Status**: Authoritative conformance contract for the durability behaviour of
`azure-ai-agentserver-responses`. This document defines the per-row × per-path
guarantees that the durability-contract conformance suite
(`tests/e2e/durability_contract/`) enforces. It is the test-facing companion
to the design source-of-truth `docs/responses-durability-spec.md`: where that
document explains *why* and *how* durability works, this one states the
precise, testable promises and binds each to its conformance test.

**Audience**: Framework maintainers, handler authors, SDK reviewers, and the
conformance meta-test.

This document defines:

- The **flags and server option** that select a durability behaviour.
- The **termination lifecycle** — the three paths a server lifetime can take
  when a request is in flight.
- The **matrix** — for each flag combination, what the framework promises on
  each termination path.
- The **developer checkpoint-write contract** (Row 11) — the
  `yield stream.checkpoint()` write point and its recovery semantics.
- The **streaming sub-contract** layered on top when `stream=true`.
- The **composition rules** (which flag combinations require which providers).
- The **test discipline** the conformance suite follows.

---

## How to read this document

1. Handler authors asking "what happens if the server dies?" read **The
   matrix**, then their row's **Per-row contract**, then **Handler obligations**.
2. Maintainers changing anything near durability read the whole document and
   keep every row × applicable-path behaviour intact (see **Test discipline**).

The terms `MUST`, `MUST NOT`, `SHOULD`, `MAY` follow RFC 2119.

---

## Concepts

### Request flags

Three boolean flags on the request select the durability shape:

- **`store`** *(request body, default `true`)* — whether the response and its
  events are persisted to the configured `ResponseStore`.
- **`background`** *(request body, default `false`)* — whether the request
  returns immediately with an `in_progress` response that clients poll or
  stream-reconnect to observe.
- **`stream`** *(request body, default `false`)* — whether the response is
  delivered as SSE events on the original connection. Independent of the
  durability shape; see the **Streaming sub-contract**.

### Server option

- **`durable_background`** *(server option, default `False`)* — whether the
  framework engages full crash-recovery for `background=true, store=true`
  requests. When `True`, the supporting providers MUST be present (see
  **Composition rules**); the server fails loud at startup otherwise.

### Termination paths

Every in-flight request faces one of three paths from the moment the process
receives a termination signal (or crashes). The matrix specifies a contract
per path.

- **Path A — graceful shutdown, handler reaches terminal within grace.** New
  requests are refused; in-flight handlers continue; the handler reaches a
  terminal state before grace expires. The happy path; identical across rows.
- **Path B — graceful shutdown, grace exhausted with handler still running.**
  The framework MUST act in-process before the runtime exits, per the row's
  contract, and respond to waiting clients in this lifetime.
- **Path C — crash, or a graceful shutdown whose Path-B action did not run**
  (SIGKILL, OOM, power loss, a hang during the shutdown loop). On the next
  process lifetime the framework scans persisted state and applies the row's
  restart contract. Path C is the complete fallback for Path B.

A single termination event is handled by exactly one path.

### Durable record

Every accepted `store=true` request is registered with the underlying
durable-task primitive at acceptance time. The registration carries the
response id, the row's Path-C disposition (`re-invoke` for Row 1,
`mark-failed` for Rows 2 and 3), and (for re-invocation rows) the handler
reference. `store=false` requests have no durable record; Path C does not
apply.

### Recovered entry

On a recovered re-invocation (Row 1 Path B post-restart, or Path C) the
handler observes `context.is_recovery == True`. Its cross-turn checkpoint
store is `context.conversation_chain_metadata`; its single-turn,
per-response watermark surface is the `internal_metadata` map. The handler
seeds its resumption from `context.persisted_response` (the last durably
persisted snapshot — see Row 11).

---

## The matrix

The matrix is the per-row × per-path contract. Rows 1–4 are keyed on the three
flags (`store`, `background`, `durable_background`); `stream` is intentionally
NOT a row key (the contract is mode-flag agnostic with respect to `stream`,
and the streaming sub-contract specifies how it is delivered). Row 11 is a
**checkpoint-write extension of Row 1** — it has Row 1's flags and adds the
developer `stream.checkpoint()` write point; its cutpoints are detailed in its
per-row contract.

| Row | `store` | `background` | `durable_background` | Path A (within-grace) | Path B (grace exhausted) | Path C (crash / Path-B failure) |
|----:|---------|--------------|----------------------|-----------------------|--------------------------|---------------------------------|
|  1  | `true`  | `true`       | `True`               | natural terminal      | hand the in-flight handler to the durable-task primitive's recovery; runtime exits; next lifetime re-invokes the handler with `is_recovery=True` | next lifetime re-invokes the handler with `is_recovery=True` |
|  2  | `true`  | `true`       | `False`              | natural terminal      | mark response `failed` (`code=server_error`) in-process before exit; respond to waiting clients | next lifetime marks response `failed` (`code=server_error`) |
|  3  | `true`  | `false`      | any                  | natural terminal      | mark response `failed` (`code=server_error`) in-process before exit; respond to waiting clients | next lifetime marks response `failed` (`code=server_error`) |
|  4  | `false` | any          | any                  | natural terminal      | best-effort `failed` marker in-process; original HTTP connection may already be closing | no recovery applies (no persisted state) |
| 11  | `true`  | `true`       | `True`               | all phases checkpoint + complete; final `response.output` reflects every phase | handler at a checkpoint boundary calls `await context.exit_for_recovery()`; recovery resumes from the last checkpointed snapshot | SIGKILL at a checkpoint boundary; recovery resumes from the last checkpointed snapshot |

Read every cell as a MUST for the framework. Path A is identical across Rows
1–4 because no framework intervention is needed.

---

## Per-row contracts

### Row 1 — Full recovery (`store=true, background=true, durable_background=True`)

**Path A.** Handler completes within grace. Standard happy path.

**Path B.** Grace expires with the handler still running. The framework MUST
hand the in-flight handler to the durable-task primitive's recovery (NOT mark
it `failed`) and exit; the next lifetime re-invokes the handler with
`context.is_recovery == True`.

**Path C.** SIGKILL or a Path-B action that did not complete. On the next
lifetime the framework finds the durable record and re-invokes the handler
with `context.is_recovery == True`.

**Recovered handler entry contract** (Path B post-restart and Path C):

- `context.is_recovery == True`.
- `context.conversation_chain_metadata` carries any cross-turn checkpoint
  state the handler flushed in a prior lifetime.
- The framework does not impose a watermark schema. The handler chooses what
  it stores and how it resumes.
- For streaming, the recovered handler emits a `response.in_progress` reset
  event as its first event (see **Streaming sub-contract**).
- Graceful-shutdown recovery is requested with the single uniform primitive
  `await context.exit_for_recovery()`, which works in every handler shape
  (coroutine, async generator, sync).

### Row 2 — Marked failed (`store=true, background=true, durable_background=False`)

A stored, observable response without crash recovery.

**Path A.** Handler completes within grace. Standard.

**Path B.** The in-process shutdown loop MUST mark the response `failed`
(`code=server_error`, path cause in `message`), persist any final events, and
respond to waiting clients in this lifetime.

**Path C.** On the next lifetime the framework finds the durable record
(disposition `mark-failed`) and marks the response `failed`
(`code=server_error`) with a synthetic terminal event so subsequent polling
and stream-reconnect see terminal.

### Row 3 — Marked failed, foreground (`store=true, background=false`, any `durable_background`)

A stored response observable over the original (foreground) HTTP connection.
`durable_background` is a free axis — foreground responses do not benefit from
durable handler recovery because the client connection is gone. Path A/B/C
have the same shape as Row 2; all failure markers use `code=server_error` with
the path-specific cause in `message`.

### Row 4 — Best-effort (`store=false`, any `background`, any `durable_background`)

In-memory-only, no persistence, no recovery.

**Path A.** Handler completes within grace. Standard.

**Path B.** The shutdown loop MAY write a best-effort `failed` event to the
open connection. No persistence is required (there is nowhere to persist).

**Path C.** No persisted state, so no next-lifetime action applies.

### Row 11 — Developer checkpoint write (extension of Row 1)

Row 11 covers the `yield stream.checkpoint()` write point used by the
**one-OutputItem-per-phase** durable pattern. A handler emits one output item
per logical phase and checkpoints at each phase boundary; the checkpoint
persists a snapshot whose `output` holds exactly the phases completed so far.
On recovery the handler **seeds the stream** from `context.persisted_response`
(so the already-checkpointed phases' items are present in
`stream.response.output`, keeping their original lifetime marker) and resumes
at `len(stream.response.output)`, running only the remaining phases. This makes
the recovery resume-point directly observable in the recovered
`response.output`.

`checkpoint()` is gated to durable background responses
(`durable_background=True` + `store=true` + `background=true`) and is a no-op
otherwise.

**Cutpoints** (the failure boundaries the contract guarantees, expressed in
the one-item-per-phase model):

- **C1 — crash after a successful checkpoint.** Phase N's item is emitted and
  its `checkpoint()` succeeds, then the process is lost before phase N+1's item
  is emitted. Recovery's `persisted_response.output` holds N+1 items; the
  handler resumes at phase N+1. Phase N survives with its original lifetime
  marker; only later phases re-run. No data loss, no duplication.
- **C3 — crash before a checkpoint.** Phase N's item is emitted but the handler
  is lost *before* calling `checkpoint()`. The snapshot still holds N items
  (the un-checkpointed item N never persisted); recovery re-runs phase N.
  **This is the central guarantee of the one-item-per-phase pattern.**
- **C2 — crash mid-checkpoint-write (provider-atomicity limitation).** The
  `FileResponseStore` provider commits the response envelope via an atomic
  `os.replace`, so a crash during `update_response` exposes either the prior
  committed snapshot or the newly committed one — **never a torn snapshot**.
  Whether recovery sees N or N+1 items therefore depends on the provider's
  commit point, not on a torn write. The contract guarantees *no corruption*;
  it does NOT promise "prior snapshot only" for a mid-write crash with this
  provider. No torn-write recovery is asserted.
- **C4 — checkpoint after terminal.** A checkpoint event yielded after the
  terminal event is dropped (the terminal write is authoritative); no
  overwrite, no exception.
- **C5 — provider failure swallowed.** A transient `update_response` failure
  during `checkpoint()` is swallowed; the handler does not observe it and
  recovery sees the prior snapshot.

**Path A.** All phases checkpoint and the handler reaches a natural terminal;
the final `response.output` reflects every phase produced by the fresh entry.

**Path B.** The handler is parked at a checkpoint cutpoint when grace is
exhausted; it observes `context.shutdown`, calls
`await context.exit_for_recovery()`, and the framework leaves the response
`in_progress`. On restart the handler resumes from the checkpointed snapshot.
The deferral MUST NOT overwrite the last checkpoint snapshot with a
pre-terminal record.

**Path C.** SIGKILL at a checkpoint cutpoint; on restart recovery resumes from
the last checkpointed snapshot.

**Contract-surface depth (Principle XI).** Row 11 conformance tests assert the
recovered `response.output` *content* using per-lifetime-identifiable markers
(`L{lifetime}_phase{n}`) so the resume-point — and the absence of loss or
duplication — is directly visible (e.g. C1 →
`[L0_phase0, L0_phase1, L1_phase2]` vs C3 →
`[L0_phase0, L1_phase1, L1_phase2]`), not just terminal `status`.

---

## Streaming sub-contract

When `stream=true`, the row's contract applies as written, PLUS:

1. **Event persistence (Rows 1, 11).** Every emitted SSE event MUST be appended
   to the durable stream provider in order BEFORE being flushed to the
   original connection, so a reconnecting client is served the same prefix.
2. **Resumable reconnect endpoint.** `GET /responses/{id}?stream=true&starting_after=<event_id>`
   MUST return durable events strictly after `<event_id>` and then live-tail
   (or return the terminal event if the response is complete).
3. **`response.in_progress` reset event.** On re-invocation the recovered
   handler MUST emit a `response.in_progress` event as its first event,
   carrying the corrected output items.
4. **Stable event ids across recovery.** Pre-crash events retain their ids;
   recovered events get fresh monotonic ids after the last pre-crash id.

**Client-side rule.** A streaming client MUST reset its accumulator on every
`response.in_progress` event after the first.

---

## Composition rules

The framework MUST validate at startup and fail loud if a required provider is
absent; it MUST NOT silently downgrade to a weaker row.

| Server config | Required providers | If missing |
|---|---|---|
| `durable_background=True` | `ResponseStore` supporting durable task records; a durable stream provider for streamed durable responses | Startup error naming the missing provider |
| `store=true` requests accepted (any row) | `ResponseStore` | Startup error |
| `stream=true` requests accepted (any row) | A streaming-capable transport configuration | Startup error |

---

## Handler obligations

- Emit output via builder events (`add_output_item_*` → `emit_*`); do NOT
  pre-populate `response.created` with output items on a **fresh** entry. (On a
  **recovered** entry, seeding the stream from `context.persisted_response` —
  which carries the already-persisted items on `response.created` — is the
  intended recovery pattern and is accepted by the framework.)
- For durable graceful shutdown, call `await context.exit_for_recovery()` to
  leave the response `in_progress` for next-lifetime recovery.
- For the checkpoint pattern (Row 11), checkpoint at safe phase boundaries and,
  on recovery, resume from `context.persisted_response`.
- For at-most-once side effects across recovery, write a dedup marker to
  `context.conversation_chain_metadata` and `await ...flush()` before the
  side effect.

---

## Framework obligations

- Deliver every row × applicable-path cell above as a MUST.
- Persist the checkpoint snapshot durably on success; on a swallowed provider
  failure, preserve the prior snapshot (C5).
- On recovery deferral (`exit_for_recovery`), preserve the last checkpoint
  snapshot — do NOT overwrite it with a pre-terminal record (Row 11 Path B).
- Strip `internal_metadata` (item-level and the response-level reserved key)
  from every client egress; never persist client-injected internal metadata.

---

## Test discipline

The matrix is the contract, enforced by the behavioural suite at
`tests/e2e/durability_contract/` and codified by Constitution Principle X.

1. **One test module per (row × path)** — `test_row_<N>_path_{a,b,c}.py`. Each
   module drives the contract end-to-end through a real HTTP client.
2. **Real signals only.** Path A uses SIGTERM with a long grace; Path B uses
   SIGTERM with a deliberately short grace; Path C uses SIGKILL via
   `_crash_harness` then restart. No mocking, no synthetic-crash shortcuts, no
   fabricated recovery state.
3. **`stream` is parametrized** — every module runs both `stream=False` and
   `stream=True`.
4. **Completeness meta-test.** `test_contract_completeness.py` parses **The
   matrix** here and fails if any (row × applicable path) lacks a test module,
   and requires `CONTRACT_COVERAGE.md` to map every conformance test.
5. **Contract-surface depth (Principle XI).** Per-cell tests assert on event
   content / `response.output` / sequence numbers as applicable, not just
   terminal status. Row 11 uses per-lifetime markers (above).

For Row 11, the real-crash cutpoints **C1** and **C3** are exercised e2e under
Path B (graceful `exit_for_recovery`) and Path C (SIGKILL); **C2** is the
documented provider-atomicity limitation above (no torn-write assertion);
**C4** and **C5** are unit-tested in `tests/unit/test_checkpoint.py`.
