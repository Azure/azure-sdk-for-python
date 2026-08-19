# Resilience Contract — Conformance Specification

**Status**: Authoritative conformance contract for the resilience behaviour of
`azure-ai-agentserver-responses`. This document defines the per-row × per-path
guarantees that the resilience-contract conformance suite
(`tests/e2e/resilience_contract/`) enforces. It is the test-facing companion
to the design source-of-truth `docs/responses-resilience-spec.md`: where that
document explains *why* and *how* resilience works, this one states the
precise, testable promises and binds each to its conformance test.

**Normative ownership (single edit point).** This document is the **single
normative source** for the dispatch matrix and its per-cell dispositions, the
streaming sub-contract, the recovered-entry precondition, and the
handler/framework obligations — they are parsed by the conformance meta-tests
and pinned by the Constitution. `responses-resilience-spec.md` may summarize
these clauses for readability, but the normative edit for any of them is made
**here**; on conflict, this contract is authoritative. The design spec is
authoritative for everything this contract does not carry (terminology, chain
identity, the reserved metadata namespace, perpetual-task internals,
cancellation, steering, and the worked sequences).

**Audience**: Framework maintainers, handler authors, SDK reviewers, and the
conformance meta-test.

This document defines:

- The **flags and server option** that select a resilience behaviour.
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
2. Maintainers changing anything near resilience read the whole document and
   keep every row × applicable-path behaviour intact (see **Test discipline**).

The terms `MUST`, `MUST NOT`, `SHOULD`, `MAY` follow RFC 2119.

---

## Concepts

### Request flags

Three boolean flags on the request select the resilience shape:

- **`store`** *(request body, default `true`)* — whether the response and its
  events are persisted to the configured `ResponseStore`.
- **`background`** *(request body, default `false`)* — whether the request
  returns immediately with an `in_progress` response that clients poll or
  stream-reconnect to observe.
- **`stream`** *(request body, default `false`)* — whether the response is
  delivered as SSE events on the original connection. Independent of the
  resilience shape; see the **Streaming sub-contract**.

### Server option

- **`resilient_background`** *(server option, default `False`)* — whether the
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

### Resilient record

Every accepted `store=true` request is registered with the underlying
resilient-task primitive at acceptance time. The registration carries the
response id, the row's Path-C disposition (`re-invoke` for Row 1,
`mark-failed` for Rows 2 and 3), and (for re-invocation rows) the handler
reference. `store=false` requests have no resilient record; Path C does not
apply.

### Recovered entry

On a recovered re-invocation (Row 1 Path B post-restart, or Path C) the
handler observes `context.is_recovery == True`. Its cross-turn checkpoint
state comes from an application-owned `FoundryStateStore`; its single-turn,
per-response watermark surface is the `internal_metadata` map. The handler
seeds its resumption from `context.persisted_response` (the last resiliently
persisted snapshot — see Row 11).

**Recovery precondition (persisted response required).** The framework
re-invokes the handler only if the response was resiliently created in the
response store. If the response is **definitively absent** on recovery
(a typed not-found from the store), the original `POST /responses`
connection closed without ever returning a response id, so no client can
fetch it — the framework MUST drop the resilient execution (no
re-invocation, no `response.*` stream events, no terminal write) and settle
the task so the recovery scan does not re-select it. This applies to **both
`stream=false` and `stream=true`** resilient background recovery — the gate
runs before the stream-vs-non-stream dispatch. A transient/ambiguous store
error is NOT a definitive absence and MUST NOT trigger a drop.

**Recovered-input parity (recovery == fresh entry).** A recovered handler MUST
observe the **identical request-scoped inputs** it would on fresh entry:
`context.request` (every field, including request-only fields the stored response
does not carry), `context.client_headers`, `context.query_parameters`, and
`await context.get_input_items()` (resolved and unresolved) are equal to their
fresh-entry values. The only handler-visible difference on recovery is
`context.is_recovery == True` and the entry-only `context.persisted_response`
snapshot — never dropped or altered inputs/metadata. (Design: resilient-task input
boundary, `responses-resilience-spec.md` §5.3 / §8.2.)

---

## The matrix

The matrix is the per-row × per-path contract. Rows 1–4 are keyed on the three
flags (`store`, `background`, `resilient_background`); `stream` is intentionally
NOT a row key (the contract is mode-flag agnostic with respect to `stream`,
and the streaming sub-contract specifies how it is delivered). Row 11 is a
**checkpoint-write extension of Row 1** — it has Row 1's flags and adds the
developer `stream.checkpoint()` write point; its cutpoints are detailed in its
per-row contract.

| Row | `store` | `background` | `resilient_background` | Path A (within-grace) | Path B (grace exhausted) | Path C (crash / Path-B failure) |
|----:|---------|--------------|----------------------|-----------------------|--------------------------|---------------------------------|
|  1  | `true`  | `true`       | `True`               | natural terminal      | hand the in-flight handler to the resilient-task primitive's recovery; runtime exits; next lifetime re-invokes the handler with `is_recovery=True` | next lifetime re-invokes the handler with `is_recovery=True` |
|  2  | `true`  | `true`       | `False`              | natural terminal      | mark response `failed` (`code=server_error`) in-process before exit; respond to waiting clients | next lifetime marks response `failed` (`code=server_error`) |
|  3  | `true`  | `false`      | any                  | natural terminal      | mark response `failed` (`code=server_error`) in-process before exit; respond to waiting clients | next lifetime marks response `failed` (`code=server_error`) |
|  4  | `false` | any          | any                  | natural terminal      | best-effort `failed` marker in-process; original HTTP connection may already be closing | no recovery applies (no persisted state) |
| 11  | `true`  | `true`       | `True`               | all phases checkpoint + complete; final `response.output` reflects every phase | handler at a checkpoint boundary calls `await context.exit_for_recovery()`; recovery resumes from the last checkpointed snapshot | SIGKILL at a checkpoint boundary; recovery resumes from the last checkpointed snapshot |

Read every cell as a MUST for the framework. Path A is identical across Rows
1–4 because no framework intervention is needed.

---

## Per-row contracts

### Row 1 — Full recovery (`store=true, background=true, resilient_background=True`)

**Path A.** Handler completes within grace. Standard happy path.

**Path B.** Grace expires with the handler still running. The framework MUST
hand the in-flight handler to the resilient-task primitive's recovery (NOT mark
it `failed`) and exit; the next lifetime re-invokes the handler with
`context.is_recovery == True`.

**Path C.** SIGKILL or a Path-B action that did not complete. On the next
lifetime the framework finds the resilient record and re-invokes the handler
with `context.is_recovery == True`.

**Recovered handler entry contract** (Path B post-restart and Path C):

- `context.is_recovery == True`.
- The handler reloads cross-turn checkpoint state from its explicit
  `FoundryStateStore`.
- The framework does not impose a watermark schema. The handler chooses what
  it stores and how it resumes.
- For streaming, the recovered handler emits a `response.in_progress` reset
  event as its first event (see **Streaming sub-contract**).
- Graceful-shutdown recovery is requested with the single uniform primitive
  `await context.exit_for_recovery()`, which works in every handler shape
  (coroutine, async generator, sync).

### Row 2 — Marked failed (`store=true, background=true, resilient_background=False`)

A stored, observable response without crash recovery.

**Path A.** Handler completes within grace. Standard.

**Path B.** The in-process shutdown loop MUST mark the response `failed`
(`code=server_error`, path cause in `message`), persist any final events, and
respond to waiting clients in this lifetime.

**Path C.** On the next lifetime the framework finds the resilient record
(disposition `mark-failed`) and marks the response `failed`
(`code=server_error`) by overlaying the failed terminal onto the persisted
response snapshot — preserving `agent_reference`, `model`, and the progress
(output items) durably persisted before the crash — so subsequent polling
and stream-reconnect see terminal. When no snapshot was ever persisted, a
minimal `failed` object is synthesized carrying `agent_reference` + `model`
from the persisted task input.

### Row 3 — Marked failed, foreground (`store=true, background=false`, any `resilient_background`)

A stored response observable over the original (foreground) HTTP connection.
`resilient_background` is a free axis — foreground responses do not benefit from
resilient handler recovery because the client connection is gone. Path A/B/C
have the same shape as Row 2; all failure markers use `code=server_error` with
the path-specific cause in `message`.

### Row 4 — Best-effort (`store=false`, any `background`, any `resilient_background`)

In-memory-only, no persistence, no recovery.

**Path A.** Handler completes within grace. Standard.

**Path B.** The shutdown loop MAY write a best-effort `failed` event to the
open connection. No persistence is required (there is nowhere to persist).

**Path C.** No persisted state, so no next-lifetime action applies.

### Row 11 — Developer checkpoint write (extension of Row 1)

Row 11 covers the `yield stream.checkpoint()` write point used by the
**one-OutputItem-per-phase** resilient pattern. A handler emits one output item
per logical phase and checkpoints at each phase boundary; the checkpoint
persists a snapshot whose `output` holds exactly the phases completed so far.
On recovery the handler **seeds the stream** from `context.persisted_response`
(so the already-checkpointed phases' items are present in
`stream.response.output`, keeping their original lifetime marker) and resumes
at `len(stream.response.output)`, running only the remaining phases. This makes
the recovery resume-point directly observable in the recovered
`response.output`.

`checkpoint()` is gated to resilient background responses
(`resilient_background=True` + `store=true` + `background=true`) and is a no-op
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
  `os.replace`, and writes each output item to the shared `items/` store
  **before** the envelope (items-first). Items are immutable by id
  (re-stores are idempotent same-content), so a crash during
  `update_response` exposes either the prior committed snapshot or the newly
  committed one — **never a torn snapshot** (and never an envelope pointing
  at a missing item). Whether recovery sees N or N+1 items therefore depends
  on the provider's commit point, not on a torn write. The contract
  guarantees *no corruption*; it does NOT promise "prior snapshot only" for a
  mid-write crash with this provider. No torn-write recovery is asserted.
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
   to the resilient stream provider in order BEFORE being flushed to the
   original connection, so a reconnecting client is served the same prefix.
2. **Resumable reconnect endpoint.** `GET /responses/{id}?stream=true&starting_after=<event_id>`
   MUST return resilient events strictly after `<event_id>` and then live-tail
   (or return the terminal event if the response is complete).
3. **`response.in_progress` reset event.** On re-invocation the recovered
   handler MUST emit a `response.in_progress` event as its first **client-visible**
   event, carrying the corrected output items. The recovered handler may still
   emit `response.created` first (to seed its in-memory stream and satisfy the
   first-event validator), but the framework MUST NOT append a second
   `response.created` to the resilient stream — see clause 5.
4. **Stable event ids across recovery.** Pre-crash events retain their ids;
   recovered events get fresh monotonic ids after the last pre-crash id.
5. **Single `response.created` per resilient stream.** `response.created` is, by
   definition, the first event of a resilient stream. The framework appends it to
   the resilient stream provider **only when the stream is empty** (no events ever
   appended). On a recovered entry the stream already carries the pre-crash
   `response.created`, so the re-emitted one is suppressed at the provider
   write; a reconnecting/replaying client therefore observes `response.created`
   exactly once across the full (pre-crash + recovered) sequence. The
   persisted-but-stream-empty window (response created, crash before the first
   stream emit) correctly re-appends `response.created` because the stream is
   genuinely empty.

**Client-side rule.** A streaming client MUST reset its accumulator on every
`response.in_progress` event after the first.

---

## Composition rules

The framework MUST validate at startup and fail loud if a required provider is
absent; it MUST NOT silently downgrade to a weaker row.

| Server config | Required providers | If missing |
|---|---|---|
| `resilient_background=True` | `ResponseStore` supporting resilient task records; a resilient stream provider for streamed resilient responses | Startup error naming the missing provider |
| `store=true` requests accepted (any row) | `ResponseStore` | Startup error |
| `stream=true` requests accepted (any row) | A streaming-capable transport configuration | Startup error |

The same "fail loud, never silently downgrade" rule applies at **request
time**. When `resilient_background` is in effect and the resilient task cannot
be started, the framework MUST fail the request rather than silently running
the handler on a non-durable, connection-scoped task (which would lose crash
recovery while still returning a healthy-looking response):

- **Resilient start fails** (the task subsystem is present but starting the
  task fails — e.g. the task store rejects the write): fail immediately,
  surfaced as a **platform** error source. Non-streaming requests return
  `HTTP 500` with `x-platform-error-source: platform`; streaming requests (whose
  `200` headers are already sent) emit a standalone `error` event.
- **Task subsystem absent**: when hosted (`FOUNDRY_HOSTING_ENVIRONMENT` set),
  this is a platform-infrastructure failure and fails the request the same way.
  Only in non-hosted/local execution (e.g. an in-process test harness whose
  server lifespan never ran) does the framework run the handler in-process —
  there is nothing to recover, so this is the legitimate non-durable path, not a
  failure.

---

## Handler obligations

- Emit output via builder events (`add_output_item_*` → `emit_*`); do NOT
  pre-populate `response.created` with output items on a **fresh** entry. (On a
  **recovered** entry, seeding the stream from `context.persisted_response` —
  which carries the already-persisted items on `response.created` — is the
  intended recovery pattern and is accepted by the framework.)
- For resilient graceful shutdown, call `await context.exit_for_recovery()` to
  leave the response `in_progress` for next-lifetime recovery.
- For the checkpoint pattern (Row 11), checkpoint at safe phase boundaries and,
  on recovery, resume from `context.persisted_response`.
- For at-most-once side effects across recovery, write a dedup marker to
  `FoundryStateStore` before the side effect.

---

## Framework obligations

- Deliver every row × applicable-path cell above as a MUST.
- Persist the checkpoint snapshot resiliently on success; on a swallowed provider
  failure, preserve the prior snapshot (C5).
- On recovery deferral (`exit_for_recovery`), preserve the last checkpoint
  snapshot — do NOT overwrite it with a pre-terminal record (Row 11 Path B).
- **Append `response.created` to the resilient stream only when the stream is
  empty** — never re-append it on a recovered entry (Streaming sub-contract
  clause 5).
- **Drop recovery when the response was never resiliently created** — on a
  definitive store not-found, do not re-invoke the handler; settle the task
  (Recovered entry § Recovery precondition).
- Strip `internal_metadata` (item-level and the response-level reserved key)
  from every client egress; never persist client-injected internal metadata.

---

## Test discipline

The matrix is the contract, enforced by the behavioural suite at
`tests/e2e/resilience_contract/` and codified by Constitution Principle X.

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
