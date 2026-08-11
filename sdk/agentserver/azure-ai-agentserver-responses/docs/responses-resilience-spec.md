# Responses Resilience — Authoritative Specification

> **Status**: Living specification. Authoritative **design** reference for the
> responses resilience surface — the full mental model, internals, cancellation,
> steering, worked sequences, and the conformance-item index.
>
> **Normative ownership (single edit point).** The machine-verified
> **conformance contract** — the dispatch matrix and its per-cell dispositions,
> the streaming sub-contract, the recovered-entry precondition, and the
> handler/framework obligations — is owned by
> [`resilience-contract.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/resilience-contract.md). That doc is parsed by the
> conformance meta-tests and pinned by the Constitution. Where this spec restates
> any of those clauses it is a **non-normative summary for readability**; on any
> conflict, `resilience-contract.md` is authoritative, and the normative edit is
> made there. This spec is authoritative for everything the contract does NOT
> carry (terminology, chain identity, the reserved metadata namespace, the
> perpetual-task internals, cancellation §10, steering §11, the worked sequences
> §12–13, and the C-* conformance index §14).
>
> **Audience**: Library implementers porting this contract to another
> language; framework reviewers verifying behavior against the
> implementation; integrators building reference clients.
>
> **Scope**: The resilience, recovery, steering, conversation-locking,
> and stream-reconciliation contract that the agentserver responses
> layer adds on top of an underlying resilient-task primitive (see
> `azure-ai-agentserver-core/docs/task-and-streaming-spec.md`). The
> public OpenAI-compatible Responses HTTP/SSE surface is OUT OF SCOPE
> here except where this layer adds new headers, error codes, or
> event semantics on top of it.
>
> **Stability promise**: The contract terms (matrix rows, disposition
> values, reserved namespaces, reset semantics) are normative. The
> Python class names cited throughout are illustrative — port them as
> idiomatic in the target language.

This document is intentionally redundant in places (every section can
be read in isolation; cross-references are hints, not prerequisites)
to keep each contract surface independently understandable.

---

## §1 — Why this document exists

The responses resilience layer sits between (a) the OpenAI-compatible
Responses HTTP/SSE protocol that end-users call, and (b) the resilient
task primitive that gives the host process crash-recovery. The layer's
job is to translate the per-request HTTP shape — `(store, background,
stream, conversation_id, previous_response_id)` plus server options
`(resilient_background, steerable_conversations)` — into one of a small
set of resilience behaviors, and to give recovered handlers the
context they need to produce a coherent response after a process
restart.

The *behavior* of each request (when does the framework re-invoke the
handler? when does it mark `failed`? when does it return HTTP 409?) is
fully determined by the per-row dispatch matrix in §3 below. Once a
row is selected, the row's recovery, cancellation, and steering rules
fall out from the contracts in §§ 6–11. There is no other source of
behavioral variation a port should need to model.

Anything not explicitly stated here is unspecified and SHOULD NOT be
relied on; in particular, the layer makes no guarantees about
multi-replica concurrent recovery (single-node-restart only) or about
foundry-backed storage providers (the contract is validated against
the file-based provider and is the same contract the foundry provider
implements).

---

## §2 — Terminology

| Term | Meaning |
|---|---|
| **Response** | A single `POST /v1/responses` call's logical output, identified by a server-issued `response_id`. |
| **Conversation chain** | A sequence of responses sharing a stable chain identity (see §4) — either via `conversation_id` or via a sequence of `previous_response_id` links. |
| **Resilient task** | A record in the underlying task store representing the perpetual execution loop for a conversation chain. Identified by a deterministic `task_id` (§4). |
| **Handler** | The user-written response handler — an `async def` function (or async generator) that produces output for one turn of one conversation chain. |
| **Fresh entry** | A handler invocation that is not a recovery — either the chain's very first turn, or a subsequent turn delivered to a live task body. |
| **Recovered entry** | A handler invocation triggered by the resilient-task recovery scanner, after a previous lifetime's task body did not reach a terminal state. |
| **Steered turn** | A turn whose input arrived while a previous turn for the same chain was still in progress; the steered turn was queued and is now being delivered. |
| **Acceptance hook** | Optional developer-provided callback that produces the initial `status="queued"` response object the HTTP caller of a steered turn sees synchronously, before the handler runs. |
| **Disposition** | Per-task field on the durable task **input** telling the recovery scanner what to do on a recovered entry: `re-invoke` or `mark-failed`. |
| **Resumption response** | Handler-built `ResponseObject` reflecting the safe-to-resume-from state; carried as the `response` payload of the recovery `response.in_progress` event. |
| **Reset event** | The second-or-later `response.in_progress` event in a stream — clients MUST treat it as a snapshot reset of the local response view. |
| **Response store** | The persistent store of `ResponseObject` envelopes; written at `response.created` and at terminal events. |
| **Stream event store** | The persistent ordered log of SSE events emitted during a response's execution; used for `starting_after=` reconnection. |
| **Termination path A / B / C** | (A) handler completes within grace window; (B) grace exhausted, in-process marker fires; (C) crash or Path-B failure, next-lifetime recovery scanner fires. |
| **Row 1 / 2 / 3 / 4** | The four behaviour rows of the matrix (§3). |

---

## §3 — The dispatch matrix

Every `POST /v1/responses` falls in exactly one of four rows, keyed on
three flags:

- `store` — request-controlled, defaults to `true`.
- `background` — request-controlled, defaults to `false`.
- `resilient_background` — developer-controlled server option, defaults
  to `false`. Developers opt INTO crash-recovery re-invocation by
  setting it to `true`; the default lands the response in
  "crash-failed" mode (Row 2 disposition), where a crash mid-handler
  surfaces as a `failed` terminal in the next lifetime rather than
  re-invoking the handler.The end-user (HTTP caller) sets `store`, `background`, and `stream`.
The developer sets `resilient_background` and `steerable_conversations`
on `ResponsesServerOptions`. End-users CANNOT override developer
decisions; developers CANNOT override end-user request flags. This
separation is normative.

> **Normative source:** the four rows and their per-cell dispositions are the
> matrix in [`resilience-contract.md` § The matrix](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/resilience-contract.md). The
> table below is a readability summary; the contract is authoritative.

| # | `store` | `background` | `resilient_background` | Behaviour |
|---|---|---|---|---|
| 1 | true | true  | true  | **Full resilience.** Handler runs inside the resilient task body. Recovery re-invokes the handler. |
| 2 | true | true  | false | **Crash-failed resilience.** Handler runs inside the resilient task body; disposition is `mark-failed`. If the process dies before terminal, recovery marks the response `failed` (no re-invoke). |
| 3 | true | false | (any) | **Crash-failed resilience.** Same shape as Row 2: handler runs inside the resilient task body (HTTP request awaits via `TaskRun.result()`); recovery marks the response `failed` on crash. |
| 4 | false | (any) | (any) | **No resilience.** Best-effort failed marker during graceful shutdown. No persistence. No recovery. |

`stream` is orthogonal: it collapses out of the row keys. Each row × `stream`
combination is its own conformance cell.

`steerable_conversations` is orthogonal to the row but composes only with
`store=true` (Rows 1, 2, 3) — see §11.

`starting_after=` reconnection is supported only for `store=true` requests
(any row 1/2/3). For Row 4 there is no persisted event log; reconnection is
not meaningful.

### §3.1 — Termination paths

Each row × stream cell has three termination paths the framework MUST
deliver per the table below:

| Path | Trigger | Row 1 (`resilient_bg`) | Rows 2/3 (`store`, no `resilient_bg`) | Row 4 (no store) |
|---|---|---|---|---|
| **A** | Handler returns within grace | Persist terminal; task body returns | Persist terminal; task body returns | Persist terminal (best-effort) |
| **B** | Grace exhausted (graceful shutdown) | Task left `in_progress`; handler stops; **next lifetime re-invokes** | Task body persists `failed` (server_error, shutdown_reason=grace_exhausted) | Best-effort in-process `failed` marker |
| **C** | SIGKILL or Path-B failure | Next-lifetime recovery scanner re-fires task → handler re-invoked with `context.is_recovery=True` | Next-lifetime recovery scanner re-fires task → marks response `failed` (`server_error`) | No recovery applies (no persistence) |

The framework MUST implement Path B and Path C as independent fallbacks
for each other (Path C is a complete fallback for Path B). A Path-B
in-process marker that does not persist before the process
exits MUST be backed by a Path-C next-lifetime marker; the row 2/3
recovery scanner closes that window.

### §3.2 — `stream` × row interaction

`stream` does not alter row selection, but it MUST alter the
implementation path:

- **`stream=false`** — the handler is invoked, its terminal result is
  persisted to the response store, and the HTTP caller receives the
  full `ResponseObject` envelope (background: `200 OK` with the
  envelope reflecting the current state; foreground: `200 OK` with the
  terminal envelope).
- **`stream=true`** — the handler's emitted SSE events are persisted
  to the stream event store in order, and the HTTP caller receives a
  live SSE feed. Reconnection via `GET /responses/{id}?stream=true&starting_after=N`
  returns only events with `sequence_number > N`.

For Row 1 × `stream=true`, recovery MUST re-engage the resilient task
body so the recovered handler's events flow to both the live subject
and the persisted event log; recovered events appear in the same
stream after `starting_after=` reconnect.

For Rows 2/3 × `stream=true`, the handler runs inside the task body;
on crash, the task body's `mark-failed` recovery branch persists the
`failed` marker as the only post-crash artifact. Clients reading the
persisted stream see whatever events landed before the crash plus
no further events.

---

## §4 — Conversation chain identity

The framework computes a deterministic **chain id** for every request,
and uses it for two purposes:

1. **Partitioning the resilient task** — every turn in a chain shares a
   single `task_id`.
2. **Exposing identity to handlers** — handlers that wrap a stateful
   upstream SDK (e.g. an LLM agent SDK with its own session-resume
   facility) use the chain id as their upstream session identifier
   without having to allocate their own.

### §4.1 — Derivation

A conversation's stable identity is the **partition key embedded in its
response IDs**. IDs have the shape `{prefix}_{partitionKey}{entropy}`; when a
response ID is generated it inherits the partition key of its
`previous_response_id` / `conversation_id` hint, so every response in a chain
carries the *same* embedded partition key. Extracting it therefore yields a
value that is stable across every turn of the chain.

Since Spec 038 the chain id is a **native IdGenerator-convention id** — the
prefix acts as the discriminator, the embedded partition key co-locates the
chain with its responses, and a deterministic `(agent, session)` scope fills the
"entropy" slot. `task_id == conversation_chain_id` exactly (no wrapper prefix).
The three cases:

1. `conversation_id` present → `cchain_{partition(conversation_id)}{scope}`
   (partition extracted from the id, or derived deterministically when it is not
   in ID format).
2. Else if `steerable_conversations=true` →
   `rchain_{partition(previous_response_id or response_id)}{scope}`. Because
   chained response IDs share one partition key, every turn resolves to the same
   id.
3. Else (non-steerable, or no chain) → the **`response_id` verbatim** — already
   globally unique + native, so each request stands alone.

```
scope   = det_alnum32("{agent_name}\x1f{session_id}")   # 32 alnum, deterministic
case 1  = "cchain_" + partition_key(conversation_id)        + scope
case 2  = "rchain_" + partition_key(prev_resp or response)  + scope
case 3  = response_id
```

`scope` is a deterministic 32-char alnum digest; `agent_name` (DNS-style ≤63) and
`session_id` (any string ≤128) are hashed because they are too long/arbitrary to
embed. The constrained field is placed first (`agent_name` cannot contain the
`\x1f` separator), so `(agent, session)` encodes injectively even when
`session_id` contains arbitrary bytes. The prefix (`cchain_` vs `rchain_` vs the
response's own `caresp_`) namespaces the two chain kinds so they never collide.
This rule is normative; a port MUST exhibit the same priority order and the same
steerable / non-steerable disambiguation. The id stays within the Public Task
API charset/limit (`^[a-zA-Z0-9_-]{1,128}$`).

### §4.2 — The `task_id`

Since Spec 038 the chain id is itself a native, self-prefixed id, so the
resilient task is keyed directly on it:

```
task_id = chain_id      # e.g. "rchain_<partitionKey><scope>" (see §4.1)
```

The task that backs a conversation and the handler-facing chain id therefore
**are one and the same identity** and can never drift apart.

### §4.3 — Public surface

The chain id is exposed to handlers as `context.conversation_chain_id` (a
`str`, never `None`) — an opaque, agent/session-scoped hex hash. Handlers
wrapping a stateful upstream SDK SHOULD use this as their upstream session id
rather than allocating a fresh UUID. The value is stable across every turn of a
chain and across all attempts (fresh, recovered, multiply-recovered) of every
turn.

Known limitation: the identity is derived from framework-generated IDs. A
client that supplies its own `response_id` (via `x-agent-response-id` or an
explicit request field) carrying a mismatched embedded partition can shift the
chain identity for later turns.

---

## §5 — Recovery control state lives on the task **input**

> **Spec 039 (R1) update.** The responses layer previously mirrored three
> control values (`response_id`, `background`, `disposition`) into a reserved
> framework metadata namespace (`_responses`). That mirror has been **removed**.
> All three are sourced from the durable **task input** (§5.2) — the single
> source of truth, persisted at task `.start()` (strictly before the body's
> first entry) and read on every recovered entry. This matches the .NET port
> (`Azure.AI.AgentServer.Core`), which never wrote such a namespace, and removes
> the drift risk of parallel mode-flag metadata (cf. §5.3's re-derivation rule).

The framework no longer persists any control state in the handler's `metadata`
checkpoint store. The handler-facing `metadata` API still MUST raise
`ValueError` if a developer attempts to set, get, or open a namespace whose name
starts with `_` — this is a **defensive guard** so handlers cannot invent
framework-reserved namespaces, retained even though the framework itself no
longer creates one.

### §5.1 — Where the three control values come from

| Value | Source (from the task input) | Read by |
|---|---|---|
| `response_id` | `ResilientResponseInput.response_id` | Logs / operator triage |
| `background` | `bool(request.background)` — re-derived from the persisted `request` (§5.3) | Recovery dispatch (foreground → mark failed) |
| `disposition` | `ResilientResponseInput.disposition` (`"re-invoke"` Row 1 / `"mark-failed"` Rows 2, 3) | Recovery dispatch (§7) |

> **Note — no `last_sequence_number` key.** Earlier drafts reserved a
> `last_sequence_number` metadata watermark for streaming reconnection
> bookkeeping. The implementation does **not** maintain it: the highest
> persisted sequence number is derived directly from the resilient **stream
> event store's cursor** (`last_cursor()`), which is the single source of truth
> — a separate metadata watermark could diverge from the events actually
> persisted. See §9.1.

### §5.2 — Persistence ordering rule (satisfied by the input)

`disposition` MUST be durable before the task body performs any await that could
be interrupted by a crash — otherwise a recovered task with no disposition would
default to `re-invoke` and skip the `mark-failed` branch (losing recovery-marker
semantics for Rows 2/3). The **task input satisfies this by construction**: it is
persisted atomically at task `.start()`, i.e. *before the handler body runs at
all* — strictly earlier than any first-entry write could be. The same holds for
any future control value that affects recovery dispatch: carry it on the input.

### §5.3 — Resilient-task input boundary (the recovery payload)

The framework persists the **request-scoped state needed to rebuild the
handler's execution context on cross-process recovery** as the resilient task's
**input**. This is a single typed object — the only value that crosses the crash
boundary as task input, and (per R1) the source of truth for recovery routing:

| Field | Why it is persisted |
|---|---|
| `request` — the full create-response request | The recovered handler needs the whole request as `context.request`; it is un-derivable from the response store (the stored response is handler *output*, missing request-only fields). The request carries `.input`, so the conversation input is persisted **once**. |
| `client_headers`, `query_parameters` | Handler-facing request metadata; request-scoped and un-derivable. They MUST survive recovery so a recovered handler observes the identical metadata as fresh entry (§8). |
| `user_id_key`, `call_id` | Platform identity (protocol `2.0.0`, from `x-agent-user-id` / `x-agent-foundry-call-id`); the platform context is derived from these in exactly one place. `call_id` is captured on the create request and replayed on every outbound storage call for the response's whole lifetime (including cross-process recovery); `user_id_key` is the per-user partition and is never forwarded to storage. |
| `agent_reference`, `agent_session_id` | Gateway-injected / resolved values that are not functions of the request body. `agent_reference` is normalized to a plain serializable mapping. |
| `response_id` | The stable response id (identity). |
| `disposition` | The recovery-routing marker (`re-invoke` / `mark-failed`); read directly on every recovered entry (§7) — the single source of truth (R1). |

Everything else the recovered handler needs is **re-derived** from the
persisted `request` — these are pure functions of the request, identical to
fresh entry, so they are NOT stored as parallel fields (which could drift):
the mode flags (`store` / `stream` / `background`), `model`,
`previous_response_id`, the resolved `conversation_id`, and the resolved input
items. Conversation history is re-derived on demand via the store's
history-id lookup; it is a prefetch optimization, not recovery state.

The boundary is **fail-closed**: the object is JSON-serializable by
construction (no runtime object references — those live in a separate
process-local cache keyed by `response_id` and are never serialized), and a
malformed/incomplete persisted input fails the recovered task deterministically
rather than re-invoking the handler with partial state.

> **Port note.** Oversized input (e.g. a large input-item array) rides the core
> resilient-task primitive's attachment-spill — the responses layer does not shard
> or pointerize it.

---

## §6 — The perpetual conversation-scoped task

For every `store=true` request, the framework engages a resilient
task. The task is **perpetual**: it represents the conversation
chain's execution loop, not a single response.

**One architecture — unified handler-in-task-body.** The handler
ALWAYS runs inside the resilient task body, for every `store=true`
row. The"bookkeeping pattern" (where the handler ran
outside the body for Rows 2/3 and a separate task waited for a
completion signal) has been deleted. Recovery behaviour is selected
by the `disposition` carried on the durable task **input** (§5):
`re-invoke` means the recovery scanner re-fires the handler;
`mark-failed` means the recovery scanner persists `failed` and
returns without re-invoking.

Internally, the responses layer picks one of two underlying task
primitives per request based on the `(store, conversation_id,
previous_response_id, steerable_conversations)` tuple. Non-steerable
single requests use a one-shot primitive; chain requests — and every
turn (including the first) in a `steerable_conversations=true`
deployment — use a multi-turn chain primitive. The choice is invisible
to handlers (the flat recovery + steering surface — `is_recovery`,
`is_steered_turn`, `pending_input_count`
— looks the same regardless) and to clients (the HTTP/SSE contract is
identical). The full table is in §6.4.

### §6.1 — Lifecycle (Row 1 — `resilient_background=true`, bg+store)

For Row 1 with `steerable_conversations=true`:

1. **First turn** — `start(task_id, input=params, input_id=response_id_1)`
   creates the task. Task body runs the handler for turn 1.
2. **Handler returns** — the task body returns `None` (the framework's
   implicit-suspend signal for multi-turn primitives), keeping the
   task alive for the next turn.
3. **Subsequent turn** — `start(task_id, input=params, input_id=response_id_2,
   if_last_input_id=response_id_1)` resumes the task. The framework's
   input-precondition primitive enforces sequential chain extension
   (see §11.2). Task body runs the handler for turn 2.
4. **Crash mid-handler** — task stays `in_progress` until the
   recovery scanner re-fires it. The recovered entry runs the handler
   again with `context.is_recovery=true`. Disposition is `re-invoke`.

For Row 1 with `steerable_conversations=false`, each turn (whether
forked or sequential) maps to a distinct `task_id` (the `fork:` /
`resp:` partition disambiguates), so no suspend-and-resume loop is
needed; each task is one-shot.

### §6.2 — Lifecycle (Rows 2/3 — `resilient_background=false` and foreground+store)

Same shape as §6.1: the handler runs inside the resilient task body.
The only differences are:

1. **Disposition is `mark-failed`** — carried on the durable task
   **input** (persisted at `.start()`), so recovery does NOT re-invoke the handler.
2. **HTTP request coupling** — for Row 3 (foreground), the HTTP
   request awaits the task body's terminal via the framework's
   `TaskRun.result()` API. For Row 2 (background, non-resilient
   recovery), the HTTP request returns immediately after the
   `response.created` event is observed.
3. **Crash mid-handler** — task stays `in_progress`. The recovery
   scanner re-fires it; the recovered entry takes the `mark-failed`
   branch and persists `failed` (`server_error`) idempotently. (The idempotency
   check skips the overwrite if the response is already terminal —
   see §7.2.) The handler is NOT re-invoked.

### §6.3 — Lifecycle (Row 4 — `store=false`)

No resilient task. The handler runs inline (foreground) or via a
detached background task (background). The graceful-shutdown path
MAY make a best-effort attempt to persist a `failed` marker in
whatever transient response store is in use — but this is
best-effort only and not resilient. On SIGKILL there is no recovery.

### §6.4 — Primitive selection (per-request dispatch matrix)

The responses layer dispatches each `store=true` request to one of two
underlying resilient-task primitives, based on the request shape and the
deployment's `steerable_conversations` option. This is a refinement of
the top-level 4-row matrix in §3 — Rows 1, 2, and 3 (all `store=true`
rows) split into sub-rows here according to whether the request
identifies a multi-turn chain.

| `conversation_id` | `previous_response_id` | `steerable_conversations` | Primitive | Rationale |
|---|---|---|---|---|
| absent | absent | `false` | one-shot (`@task`) | Single request, no chain — the `task_id` is unique per request (the `resp:` partition uses the full response_id); auto-deleted on terminal exit. |
| absent | absent | `true` | multi-turn (`@multi_turn_task(steerable=true)`) | First turn of a steerable chain. The stable `conversation_chain_id` (§4.1) makes this turn's `task_id` (the `chain:` partition) SHARED with any later steered turn, so the task must be the suspendable chain host that drains queued steering inputs. A one-shot would auto-delete on terminal exit and orphan the queued steered turn. |
| absent | present | `false` | one-shot (`@task`) | Fork-style: each request gets its own task_id (the `fork:` partition), so no chain semantics needed. |
| absent | present | `true` | multi-turn (`@multi_turn_task(steerable=true)`) | Steerable chain extension: turns share a task_id (the `chain:` partition); the framework suspends between turns and queues mid-turn inputs. |
| present | (any) | `false` | multi-turn (`@multi_turn_task(steerable=false)`) | Conversation-scoped chain: turns share a task_id (the `conv:` partition); chain suspends between turns. Concurrent overlap returns 409 `conversation_locked` (no queueing). |
| present | (any) | `true` | multi-turn (`@multi_turn_task(steerable=true)`) | Same conversation-scoped chain, with mid-turn inputs queued instead of rejected. |

The primitive choice MUST be made at request-dispatch time (not at
deployment-config time) because the same deployment can serve both
one-shot requests and multi-turn requests. `steerable_conversations`
gates the primitive selection in two ways: it routes the first turn of
a chain (no `conversation_id`, no `previous_response_id`) to the
multi-turn primitive instead of one-shot, AND it controls the
multi-turn primitive's mid-turn-input behaviour (queue vs reject). When
`steerable_conversations=false`, only `conversation_id` requests use the
multi-turn primitive; bare and fork-style requests stay one-shot.

The choice is invisible to handlers — `recovery + steering context (flat fields on the response context)` looks
identical regardless of which primitive carries the body. The choice
is invisible to clients — the HTTP/SSE contract on `POST /v1/responses`
and `GET /responses/{id}` is independent of the underlying primitive.

The task_id derivation (§4.2) is also independent of the primitive
choice — the `conv:` / `chain:` / `fork:` / `resp:` partition prefix
in the hash input ensures requests routed to different primitives
also get distinct task_ids when they should.

---

## §7 — Recovery dispatch

> **Normative source:** the per-row recovery dispositions and the
> recovered-entry precondition (drop when the response was never resiliently
> created) are owned by [`resilience-contract.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/resilience-contract.md)
> (§ Recovered entry, Per-row contracts). This section is the design detail.

The recovered entry of any resilient task body inspects the
`disposition` carried on the durable task **input** (§5) and routes:

### §7.1 — `disposition == "re-invoke"` (Row 1)

The handler is invoked again with `context.is_recovery == True`. The
handler is responsible for building a resumption response and emitting
a reset `response.in_progress` event (§8). The framework does NOT
re-execute the handler from a checkpoint; it re-invokes the whole
handler body.

**Recovery precondition — the response must have been resiliently created.**
Before re-invoking, the framework reads the response from the response
store. If the response is **definitively absent** (a typed not-found:
`KeyError` from the in-memory / file providers, `FoundryResourceNotFoundError`
mapped from the hosted store's HTTP 404), the original `POST /responses`
disconnected before any `response.created` was persisted, so no client ever
received a response id to fetch or poll. The framework MUST **drop** the
recovery — do NOT re-invoke the handler, emit no `response.*` events, write
no terminal — and settle the task so the recovery scanner does not re-select
it. This gate applies to **both `stream=false` and `stream=true`** resilient
background recovery: it runs on the shared recovered-entry path *before* the
stream-vs-non-stream dispatch, so a non-streaming response with no persisted
snapshot is dropped identically to a streaming one. A transient/ambiguous
store error (`FoundryBadRequestError`, `FoundryApiError`,
`ServiceRequestError` / `ServiceResponseError` / `OSError`, or any other
class) is NOT a definitive absence and MUST NOT trigger a drop — recovery
proceeds with `persisted_response = None`.

The handler reloads application watermarks from an explicit
`FoundryStateStore`. Those writes are independent from task lifecycle
transitions and lease renewal.

### §7.2 — `disposition == "mark-failed"` (Rows 2, 3)

On recovery, the task body:

1. Looks up the response in the response store.
2. If the response is already terminal (`completed`, `failed`,
   `cancelled`, `incomplete`), returns without overwriting — the
   crash happened after terminal persistence and before the
   task body could complete.
3. Otherwise, marks the response `failed` by **overlaying a failed
   terminal onto the persisted response snapshot** — the developer's
   response object (its `agent_reference`, `model`, the `output`
   accumulated and durably persisted before the crash, `created_at`,
   `conversation_id`, and any other fields set at `response.created` or
   by a later checkpoint) is preserved. Only `status` is set to
   `failed` and an `error` is attached, with `error.code="server_error"`
   and a path-specific `error.message`. The internal recovery cause
   (crash vs graceful-shutdown) is **not** surfaced on the customer
   payload — it selects the `message` and is available in server logs.
   The
   progress the response made before the crash is **not** discarded —
   the persisted snapshot is the authoritative record of what was
   durably accomplished, and the failure is layered on top of it.

   When **no** response was ever persisted (the handler crashed before
   emitting `response.created`, so the store has no snapshot), the body
   synthesizes a minimal `failed` object instead, carrying the
   `agent_reference` and `model` from the persisted task input (§5) so
   the write still satisfies the store's agent-reference requirement.
4. Returns cleanly. Task → `completed`. The handler is NOT invoked.

For steerable chains (`steerable_conversations=true`), the body
returns `None` rather than raising an explicit suspend — the framework
records the implicit-suspend transition for multi-turn primitives
automatically. The response store's `failed` terminal that step 3
persisted is the authoritative failure record; the in-process result
of the body's `return None` is consistent with that. For non-steerable
chains, returning is correct.

### §7.3 — The `server_error` error object

Every framework-emitted recovery / shutdown marker attaches this
exact `error` object to the response's terminal:

```json
{
  "code": "server_error",
  "message": "<path-specific human-readable cause>"
}
```

- `code` is always `"server_error"` — the user-facing error class is
  generic. Per the SOT behaviour contract the response-object
  `ResponseError` carries only `code` and `message` (no `type` — that
  field belongs to the HTTP error envelope, not the response object —
  and no `additionalInfo`).
- `message` is human-readable and SHOULD encode the path-specific
  cause ("Server interrupted before completing this response" for path C
  / "Server stopped before this response completed" for path B). Ports
  MAY localise; the structure is what is normative.
- The internal recovery cause (path B `grace_exhausted` vs path C
  `crash_recovery`) is **not** surfaced on the customer payload — it
  only selects the `message` and is recorded in server logs. Exposing
  it would leak framework-internal lifecycle mechanics to customers.

**The error object is overlaid onto the response, not written as a
standalone object.** The enclosing response is the **preserved
persisted snapshot** (§7.2 step 3): `status` is set to `failed` and
the `error` above is attached, while `agent_reference`, `model`,
`output` (progress made before the crash), `created_at`, and other
developer-set fields are carried through unchanged. A representative
overlaid terminal — a two-phase response that crashed after its first
phase was durably persisted:

```json
{
  "id": "<response_id>",
  "object": "response",
  "status": "failed",
  "agent_reference": { "type": "agent_reference", "name": "<agent>", "version": "<n>" },
  "model": "<model>",
  "output": [ { "type": "message", "id": "msg_1", "...": "phase-1 output persisted before crash" } ],
  "error": {
    "code": "server_error",
    "message": "<path-specific human-readable cause>"
  }
}
```

**`agent_reference` (with both `name` and `version`) is mandatory on
every write to the response store** — the store validates it and
rejects the write when it is missing, which would leave the response
stuck `in_progress`. Preserving the persisted snapshot satisfies this
by construction (the snapshot already carries `agent_reference` from
`response.created`). When no snapshot exists, the synthesized minimal
`failed` object MUST still populate `agent_reference` and `model` from
the persisted task input, and its `output` is legitimately empty
(no progress was ever persisted).

---

## §8 — The recovery contract (handler-side)

The handler receives recovery + steering state via flat fields on
the response context:

| Property | Type | Meaning |
|---|---|---|
| `is_recovery` | `Bool` | True when this invocation is a re-entry after a crash; False on every other entry (including new turns in a multi-turn chain). |
| `is_steered_turn` | `Bool` | True only on the drain re-entry that follows steering pressure — set when the queued steering input is being executed as its own turn. NOT set on the cancelled current turn that produced the steering pressure. |
| `pending_input_count` | `Int` | Number of queued steering inputs visible to the handler (live count — decreases as the framework drains the queue). |
| `persisted_response` | `ResponseObject` \| `None` | Entry-only — the last resiliently-persisted snapshot (last `stream.checkpoint()`, or `response.created`), or `None` if nothing persisted before the crash. See §8.4. |

These fields are always present on the response context. For
`store=true` rows the framework populates them from the underlying
resilient task primitive; for `store=false` (Row 4) the fields
default to a fresh, non-recovered, non-steered shape.

### §8.1 — Application state semantics

Cross-turn application state MUST use `FoundryStateStore` or another
application-owned persistence layer keyed by `conversation_chain_id`.
State writes MUST NOT update the resilient task record, renew its lease,
or be implicitly flushed by lifecycle transitions.

### §8.2 — The recovery model

The recovery contract has three actors:

1. **Framework** — re-invokes the handler with
   `context.is_recovery == True`. Persists every SSE event
   in order (no dedup, except that a recovered handler's re-emitted
   `response.created` is not re-appended to a non-empty resilient stream —
   see §8.3). Persists the response **envelope** at the first attempt's
   `response.created`, at **each successful `stream.checkpoint()`**, and at
   the terminal event. The `response.created` and terminal writes are
   **deduplicated** across recovery attempts keyed on `response_id` (§9.4);
   the last persisted envelope is exposed on re-entry as
   `context.persisted_response` (§8.4).
2. **Handler** — computes a **resumption point** and resumes from it. Two
   shipping models (the handler picks based on where its resilient progress
   state lives, and they compose):
   - **Framework-checkpoint**: emit one `OutputItem` per phase +
     `stream.checkpoint()` at each boundary; on recovery seed
     `ResponseEventStream(response=context.persisted_response)` and resume
     from `len(stream.response.output)`. The persisted snapshot is the
     watermark — no separate metadata bookkeeping is required when it is the
     only resilient progress/side-effect boundary.
   - **Upstream-owned**: query an upstream framework/store + own metadata
     watermarks; build a resumption `ResponseObject` from that state;
     construct `ResponseEventStream(response=resumption_response)`.
   Either way the handler emits a `response.in_progress` event carrying the
   resumption response and continues from the resumption point. Metadata
   watermarks set BEFORE non-idempotent side-effecting calls protect against
   duplicate side effects across attempts (a composable overlay on either
   model).
3. **Client** — observes the reset-on-`in_progress` rule (§9.3);
   redraws its local response view from the reset event's payload.

**Request-scoped input parity (recovery == fresh entry).** On a recovered
re-invocation the handler observes the **identical** request-scoped state it
would on fresh entry: `context.request`, `context.client_headers`,
`context.query_parameters`, and `await context.get_input_items()` (resolved and
unresolved) are equal to their fresh-entry values. The recovered handler is
distinguished from a fresh one *only* by `context.is_recovery == True` and the
entry-only `context.persisted_response` snapshot — never by missing or altered
inputs/metadata. This parity is what the resilient-task input boundary (§5.3)
guarantees and is exercised end-to-end by the conformance suite.

### §8.3 — Naive fallback

A handler that does nothing recovery-specific MUST still produce a
correct response. The fallback shape is:

1. Handler runs from scratch on every recovery.
2. Emits `response.created`. On a recovered entry the framework does NOT
   re-append `response.created` to the resilient stream — it appends it only
   when the stream is empty, and a recovered stream already carries the
   pre-crash `response.created`. The re-emitted event still seeds the
   handler's in-memory stream and satisfies the first-event validator, but a
   reconnecting/replaying client observes `response.created` exactly once.
3. Emits `response.in_progress` with an empty `response.output` (this
   serves as the implicit snapshot reset for clients, and is the first
   stream-visible event of the recovered lifetime).
4. Re-streams the whole turn.
5. Emits its terminal event (the framework deduplicates against the
   first terminal that lands).

The final response is correct. The client UX is jarring (full re-stream
on every recovery) but consistent.

The naive opt-out is unsafe ONLY when the handler makes upstream
side-effecting calls without watermarks — duplicate side effects
(double-sending user input, double-debiting a credit balance, etc.)
are the handler's responsibility to prevent.

### §8.4 — Checkpoint-driven recovery (`stream.checkpoint()`, `persisted_response`, `internal_metadata`)

Between the naive full-re-stream fallback (§8.3) and hand-rolled
metadata watermarks, the framework offers a **developer checkpoint write
point** so a recovered handler can resume from resiliently-persisted output
rather than re-running the whole turn.

**`stream.checkpoint()`** — a yielded stream event:

```
yield stream.checkpoint()
```

Yielding it persists the current `stream.response` snapshot (every
output item finished so far) via `provider.update_response`. It is a third
write point alongside `response.created` and the terminal write (§9.1).
Properties:

- **Deterministic + developer-driven** — checkpoints happen only where the
  handler yields one. There are NO periodic, timer, or implicit checkpoints.
- **Backpressured** — because the handler is an async generator consumed
  lockstep, the provider write completes before control returns from the
  `yield`. "I checkpointed" means "it is resilient now".
- **Resilient-background-gated** — the write happens ONLY for a
  `resilient_background=True`, `background=true` (hence `store=true`) request —
  the only configuration with a crash-recovery re-invocation path. In every
  other case the event is dropped (no write), so a handler MAY yield it
  unconditionally.
- **Idempotent** — a snapshot byte-identical to the last persisted one is
  skipped.
- **Failures swallowed** — a provider error is logged and ignored; recovery
  falls back to the previously-persisted snapshot.
- **After terminal** — a checkpoint yielded after a terminal event is dropped
  (the terminal write is authoritative); no exception.
- **Deferral preserves the checkpoint** — when a handler defers via
  `await context.exit_for_recovery()`, the framework MUST NOT overwrite the
  last checkpoint snapshot with a pre-terminal record; the checkpoint remains
  authoritative for the next lifetime.

**`context.persisted_response`** — on a recovered entry, the last
resiliently-persisted `ResponseObject` snapshot (the last checkpoint, or the
`response.created` snapshot if none ran), or `None` if nothing persisted
before the crash. Entry-only: read it at the start of the recovered
invocation to decide the resume point; it is not refreshed mid-execution.

**The one-OutputItem-per-phase pattern.** Emit one output item per logical
phase and `yield stream.checkpoint()` at each boundary. On recovery, **seed
the stream** with `context.persisted_response` and resume from
`len(stream.response.output)`: a phase whose `output_item.done` + checkpoint
completed is already present in the seeded output (it survives); a phase
interrupted before its checkpoint is re-run — correct by construction. The
recovered handler `yield stream.emit_created()` exactly as on a fresh entry;
the framework recognises the recovered entry and accepts the seeded output
(deduping the response-store write). It then emits only the remaining phases
via builder events — the persisted response is the watermark, so there is no
replay or breadcrumb reconstruction. The per-row × per-path conformance for
this write point is **Row 11** in
[`resilience-contract.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/resilience-contract.md).

**`internal_metadata`** — a single-turn, platform-internal key/value bag on
each output item and on the response (via `stream.internal_metadata` /
`item.internal_metadata`, both live `MutableMapping[str, Any]` views). It is
persisted wherever the response is persisted (`response.created`, every
`stream.checkpoint()`, terminal) and is **always stripped before any
client-facing HTTP/SSE payload** — and symmetrically stripped on ingress, so
clients can neither read nor inject it. Use it for lightweight per-turn
watermarks, id mappings (upstream message id ↔ emitted item), or in-turn
stale-message detection; read it back on recovery via
`context.persisted_response`. It is distinct from the *public*
`ResponseObject.metadata` (the client's own metadata, never stripped) and
from `FoundryStateStore` (cross-turn application state — §8.1).
Rule of thumb: cross-turn state → `FoundryStateStore`; reconstruct
*this* response on crash →
`internal_metadata` + `stream.checkpoint()`.

---

## §9 — Stream contract

> **Normative source:** the streaming sub-contract — event-persistence
> ordering, `starting_after=` reconnect, the single-`response.created`
> per-stream rule, and the `response.in_progress` reset — is owned by
> [`resilience-contract.md` § Streaming sub-contract](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/resilience-contract.md).
> This section is the design detail; the contract is authoritative.

For every `stream=true` request with `store=true`:

### §9.1 — Persistence ordering

The framework MUST persist each SSE event to the stream event store
in the order the handler emits it, and MUST assign a strictly
monotonic `sequence_number` per event within a single
`response_id`'s log. The framework MUST NOT deduplicate events across
recovery attempts: if the handler emits `output_item.added(idx=0)`
twice (once in the pre-crash attempt, once in the recovered attempt),
both events are persisted, both have distinct sequence numbers, both
are delivered to reconnecting clients.

On a recovered entry the framework MUST seed the next sequence number
from the resilient stream event store's cursor — `next_seq = last_cursor() + 1`
(or `0` when the log is empty) — so the recovered attempt's events
carry sequence numbers strictly succeeding the pre-crash events. The
stream-store cursor is the single source of truth for "how far the
stream got"; the framework MUST NOT maintain a parallel
`last_sequence_number` watermark in task metadata (which could diverge
from the events actually persisted).

> **Implementation note — one authority per surface.** On the **streaming
> wire** (the only cursor-replayed, client-visible surface) the cursor-seeded
> `next_seq` is the **sole** `sequence_number` authority: the framework MUST
> stamp it onto every event as it is appended, **overwriting** any value the
> event builder produced. A builder's own per-stream counter therefore has no
> wire effect on the streaming path and MUST NOT be relied upon. The
> **non-stream background** path is not cursor-replayed — its snapshot is the
> source of truth and is built with `sequence_number` removed — so it does not
> carry a cursor and the builder's local counter is harmless there. A language
> SDK MAY keep a builder-local counter for standalone event construction, but
> it MUST NOT be a second authority on the streaming wire.

### §9.2 — Reconnection (`starting_after=`)

`GET /responses/{id}?stream=true&starting_after=N` returns only events
with `sequence_number > N`. The reconnection is transparent — clients
do not need an out-of-band signal that "this is a recovered stream";
the reset event in the stream is sufficient (§9.3).

### §9.3 — The reset-on-`in_progress` rule

Clients MUST treat the **second or later** `response.in_progress`
event in a stream as a snapshot reset:

> Replace the local `response.output` with the event's `response.output`.
> Discard any partial in-flight item content accumulated since the
> previous snapshot. Treat subsequent events as additive on top of the
> new snapshot.

This rule applies whether the client is reading the live SSE feed or
replaying via `starting_after=`.

The framework's persisted-response-state machine MUST observe the
same rule: a second-or-later `response.in_progress` REPLACES the
persisted response's `output` array; subsequent `output_item.added`
at indexes already present REPLACES the slot rather than appends.

### §9.4 — Idempotent `response.created` and terminal

The framework MUST tolerate a duplicate `response.created` event from
a recovery-aware handler that emits it idempotently; only the first
is authoritative for response-store persistence, subsequent ones are
no-ops at the persistence layer (but ARE persisted to the event
stream — see §9.1).

The framework MUST be idempotent against duplicate terminal events. A
second `response.completed` (or `response.failed`) after one has
already been persisted to the response store is a no-op at the
persistence layer.

The response store MUST raise `ResponseAlreadyExistsError` from
`create_response()` when called for a `response_id` that already has
a non-deleted entry. Callers MUST swallow this error on recovery
attempts (log at INFO, treat as already-persisted, proceed to the
terminal `update_response()` path).

### §9.5 — Output index re-use

After a snapshot reset, the handler MAY re-use `output_index` values
that appeared before the reset. The framework MUST allow this. Clients
MUST treat `output_index` as a slot identifier (not a monotonic
counter):

- `output_item.added` at an index already present in the snapshot →
  REPLACE the slot.
- `output_item.added` at a new index → APPEND a slot.
- Subsequent `output_item.delta` / `output_item.done` apply to the
  slot identified by `output_index`.

### §9.6 — `ResponseEventStream` seeding

`ResponseEventStream(response=resumption_response)` MUST seed the
stream's internal `_output_index` counter past the highest index
present in `resumption_response.output`, so the next
`add_output_item_*` allocates a non-colliding index by default. The
handler MAY still re-use prior indexes deliberately.

### §9.7 — Recovery `response.in_progress` is the reset point

In the recovery model, the handler's emitted `response.in_progress`
carrying the resumption response IS the client-visible reset point.
The framework MUST NOT synthesise a reset event of its own; the
client-side reset rule (§9.3) is the only mechanism. If a naive
handler emits `response.in_progress` with empty `output`, that empty
payload IS the reset to "nothing was persisted last time"; clients
process it identically.

---

## §10 — Cancellation

A handler running inside the resilient task body observes cancellation
via two **distinct** surfaces and a cause-flag boolean:

- **`cancellation_signal`** (3rd positional handler arg,
  `asyncio.Event`) — set when the request itself is being cancelled
  (`POST /v1/responses/{id}/cancel`, non-bg POST disconnect, or
  steering pressure). This is the wake-up signal handlers await /
  poll on inside their work loop.
- **`context.shutdown: Event`** — set when the server is shutting
  down (e.g. SIGTERM). This is a **separate** surface — shutdown
  does NOT fire the cancellation signal. Handler expectations differ:
  shutdown demands `await context.exit_for_recovery()` (resilient+bg)
  or a quick failed/incomplete terminal (others), while cancellation
  demands a graceful finish or status-aware terminal. Handlers that
  care about both surfaces MUST inspect each independently.
- **`context.client_cancelled: Bool`** — cause flag stamped at the
  HTTP boundary when the cancellation cause was explicit client
  cancellation (the `/cancel` endpoint OR a non-bg POST disconnect).
  When `cancellation_signal` fires but `client_cancelled` is False
  and `context.shutdown` is not set, the cause is steering pressure.

Cause matrix:

| Trigger | `cancellation_signal` (3rd positional handler arg) | `context.shutdown` | `context.client_cancelled` |
|---|---|---|---|
| Steering (new turn queued) | set | not set | False |
| Client `POST /responses/{id}/cancel` | set | not set | True |
| Non-bg POST disconnect | set | not set | True |
| Graceful shutdown (`SIGTERM`) | not set | set | False |
| Race: client cancel + concurrent shutdown | set | set | True |
| No cancellation has occurred | not set | not set | False |

**Recovery exit primitive.** Handlers request the graceful-shutdown
re-entry path explicitly with a single uniform call:

```
await context.exit_for_recovery()
```

It **raises** `ResponseExitForRecovery` internally (it never returns), so
the same line works in every handler shape — coroutine, async generator,
or sync. The framework catches the signal at the resilient task boundary and
leaves the response `in_progress` so the next-lifetime recovery scanner can
resume it. For `resilient_background=True` responses (Row 1) the handler is
re-invoked on the next process startup. For `store=false` / non-resilient
requests there is no task to defer, so the call raises `RuntimeError`
(surfacing as a `failed` response — the documented non-resilient shutdown
disposition). `ResponseExitForRecovery` subclasses `BaseException` (not
`Exception`), so a handler's broad `except Exception` cannot swallow the
recovery signal; `try/finally` cleanup still runs.

The cancellation contract for the handler:

- **Default pattern** (most handlers) — observe BOTH surfaces in the
  work loop. On `cancellation_signal.is_set()`, break and emit
  `response.completed` with the current partial output (the framework
  overrides this to `cancelled` when `context.client_cancelled` is
  True). On `context.shutdown.is_set()`, call
  `await context.exit_for_recovery()` (resilient+bg Row 1) or emit a quick
  terminal (others). For steering pressure (cancel set but no cause
  flag), the handler's `completed` terminal is correct — the
  steered-out turn really did complete with whatever output it
  managed to emit before the steer.
- **Hard rule** — every async-generator handler MUST emit
  `response.created` before any early return; framework forces
  `failed` if it does not. Every handler MUST emit a terminal event
  (`completed`, `incomplete`, `failed`) or the framework forces
  `failed`. To defer to recovery without a terminal, call
  `await context.exit_for_recovery()` — because it raises rather than
  returns a value, it works uniformly in async-generator and coroutine
  handlers alike (no `return <value>` generator-syntax constraint).
- **No `cancelled` from steering or shutdown** — the handler MUST
  NOT emit `response.cancelled` for steering pressure or shutdown;
  that terminal is reserved for `context.client_cancelled=True`.
- **Cooperation model** — steering pressure and client cancel wait
  indefinitely for the handler to honour the signal. Shutdown has a
  bounded grace window; if the handler does not return within the
  window, the framework moves to Path B / Path C handling.

### §10.1 — Cancellation × recovery composition

Recovery composes with cancellation as follows:

| Pre-crash trigger | Recovery behaviour |
|---|---|
| Steering pressure (during recovery) | Recovered entry sees `cancellation_signal.is_set()` with no cause flag. Handler honours the signal as in the fresh case. |
| Client cancel (during recovery) | Recovered entry sees `cancellation_signal.is_set()` and `context.client_cancelled=True`. Handler honours the signal; framework finalises with `cancelled` terminal. |
| Shutdown (during recovery) | If `context.shutdown.is_set()`, the handler calls `await context.exit_for_recovery()` (or returns without a terminal — the implicit fallback); the framework leaves the task `in_progress` for the next lifetime. |

The cancellation surface is unchanged across fresh and recovered
entries — handlers do not need a separate branch for "I'm in
recovery AND cancelled".

---

## §11 — Steering

`steerable_conversations=True` enables multi-turn steering on top of
Rows 1, 2, or 3 (i.e. any `store=true` row). With steering enabled:

- Every turn in a conversation chain shares the same resilient `task_id`
  (the chain partitioning rule in §4.2 collapses them).
- A new turn submitted while a prior turn's handler is still running
  is **queued** into the underlying task primitive's steering queue.
  The queued turn's HTTP caller synchronously receives a queued
  response (status `"queued"`) produced by the acceptance hook
  (§11.3).
- When the queued turn moves to the front of the queue, the
  framework signals the running handler via ``cancellation_signal` (3rd positional handler arg) Event`
  with `steering pressure (cancellation_signal set, no cause flag)`. Once the running handler
  reaches terminal, the framework drains the queue and the queued
  turn's handler is invoked with `is_steered_turn=True`.

### §11.1 — `steerable_conversations=False` semantics

For `store=true` Rows 1/2/3 with `steerable_conversations=False`:

- Each turn that uses `previous_response_id` (without
  `conversation_id`) maps to its own `task_id` (the `fork:` partition;
  §4.2). This makes parallel forks possible (sequential turns also
  work — each turn is just its own one-shot task).
- Each turn that uses `conversation_id` maps to a SHARED `task_id`
  (the `conv:` partition) regardless of `steerable_conversations`.
  The chain transitions to `suspended` between turns, so sequential
  turns successfully extend the chain. Only **concurrent overlap**
  (a new turn arriving while a prior turn's handler is still
  `in_progress`) raises `TaskConflictError`; the framework MUST
  translate this to HTTP 409:

  ```json
  {
    "error": {
      "message": "Conversation is locked — task is in_progress",
      "type": "conflict",
      "code": "conversation_locked",
      "param": null
    }
  }
  ```

  Clarifier: _in progress_ here means the underlying task is
  `status="in_progress"` (a handler is actively executing). A
  `suspended` chain between turns of a `conversation_id` +
  `steerable_conversations=False` deployment is NOT locked — sequential
  turns extend the chain. Only overlapping turns conflict.

  (Implementation note: `TaskConflictError` carries only
  `current_status` on this implementation's narrow surface — the
  human-readable status is included in the error body to give the
  client a clue about why the conflict fired.)

### §11.2 — Fork rejection (no branching of a steerable chain)

When `steerable_conversations=true`, each turn after the first MUST
reference the immediately-prior turn's `response_id` via
`previous_response_id`. The framework enforces this via the
underlying task primitive's **input-precondition primitive**:

- The responses layer passes `input_id=response_id` and
  `if_last_input_id=previous_response_id` to `start()`.
- The primitive stores `last_input_id` in a framework-reserved
  payload namespace (typically `_framework.last_input_id`) and
  rejects a `start()` whose `if_last_input_id` does not match the
  stored value.
- On rejection, the primitive raises `LastInputIdPreconditionFailed`
  (a typed subclass of `TaskPreconditionFailed`).

The framework MUST translate `LastInputIdPreconditionFailed` to HTTP
409 with body:

```json
{
  "error": {
    "message": "This agent does not support conversation forking. previous_response_id must reference the most recent response in the conversation.",
    "type": "conflict",
    "code": "conversation_fork_not_supported",
    "param": "previous_response_id"
  }
}
```

This covers both stale-predecessor cases ("you sent a `previous_response_id`
that refers to a turn other than the most recent one") and concurrent
races (two POSTs arrive together with the same `previous_response_id`
— exactly one wins by atomic precondition CAS; the other gets the
409). There is no soft path through.

### §11.3 — Acceptance hook

When a new turn arrives for an already-active steerable task, the
running handler cannot produce the response object for the queued
turn (it is busy with the prior turn). The acceptance hook fills
that gap: it runs synchronously during HTTP request handling and
produces the initial response object the HTTP caller sees.

| Property | Rule |
|---|---|
| **When invoked** | ONLY for steered turns (turn N where N ≥ 2 and the handler for turn N-1 is still running). NEVER for first-turn requests. |
| **Synchronous** | Runs in the request handler; MUST NOT make LLM calls or perform heavy I/O. |
| **Registration** | Via `@app.response_acceptor` decorator (or equivalent registration API). Optional. |
| **Default** | If unregistered or raises, framework returns a default queued response: `{ "id": <response_id>, "object": "response", "status": "queued", "model": <model>, "output": [] }`. |
| **Override status** | If the hook returns a dict without `status`, framework sets `status="queued"`. |
| **First turn** | The acceptance hook is NEVER invoked for the first turn of a chain (no prior handler is running). The first turn's `response.created` comes from the handler itself. |

### §11.4 — Steering queue semantics

The framework MUST guarantee:

- **Sequential delivery within a chain** — for `steerable_conversations=true`,
  queued turns drain in FIFO order; no two handlers for the same
  chain ever execute concurrently.
- **`is_steered_turn=True` for queued turns** — the second-and-later
  turns of a chain (any turn invoked by drain rather than by initial
  start) MUST observe `context.is_steered_turn == True`.
- **`pending_input_count` is post-this** — the count of inputs queued
  *after* the currently-being-invoked one. A handler observing
  `pending_input_count == 0` is the most recent queued turn.

### §11.5 — Steering × recovery

If the process crashes mid-steering-drain, the recovered entry is
given the mid-drain input as its `context.input` (or equivalent —
the primitive's race-recovery contract supplies the in-flight input).
Handler honours it as a normal turn invocation. The cancellation
signal is set with `steering pressure (cancellation_signal set, no cause flag)` if the prior turn's
handler was already cancelled at crash time.

---

## §12 — The acceptance flow (worked sequence)

The two-phase steerable-conversation accept flow:

```
       (turn 1, fresh)
HTTP   ──► POST /v1/responses { input: "...", store, background } ────────┐
                                                                          │
       framework: derive_task_id → "rchain_AB12..."                 │
       framework: task_fn.start(task_id, input=params,                    │
                                input_id=resp_1,                          │
                                if_last_input_id=None)                    │
       framework: task body schedules; handler invoked                    │
       handler:   emit response.created (response_id=resp_1)              │
       framework: persist response envelope → response store              │
                                                                          │
       HTTP    ◄── 200 { id: resp_1, status: in_progress, ... } ──────────┘
                                                                          
       (turn 2 arrives while turn 1's handler is still running)
HTTP   ──► POST /v1/responses { input: "...", previous_response_id: resp_1 } ──┐
                                                                                │
       framework: derive_task_id → SAME "rchain_AB12..." (chain)         │
       framework: task_fn.start(task_id, input=params2,                        │
                                input_id=resp_2,                               │
                                if_last_input_id=resp_1)                       │
       primitive: task already in_progress → queue input                       │
       primitive: precondition holds → advance last_input_id to resp_2         │
       primitive: signal turn-1 handler's ctx.cancel (steering)                │
       framework: acceptance_hook(parsed, context) → queued envelope           │
                                                                                │
       HTTP    ◄── 200 { id: resp_2, status: queued, ... } ────────────────────┘
                                                                          
       (turn 1's handler honours the steer, emits terminal, returns)
       framework: persist terminal for resp_1
       primitive: drain queue → invoke handler again for resp_2
                  with is_steered_turn=True
       handler:   emit response.created (response_id=resp_2)
       framework: persist response envelope → response store
       ...
```

If a third POST arrives with `previous_response_id=resp_1` (the now-stale
prior head), the precondition fails and the third caller receives 409
`conversation_fork_not_supported`.

If `steerable_conversations=False` instead, the second POST receives
409 `conversation_locked` (turn 1's task is in_progress; turn 2 cannot
extend a non-steerable chain).

---

## §13 — The recovery flow (worked sequence)

### §13.1 — Row 1 (`resilient_background=True`) × `stream=True`, crash before terminal

```
       (turn 1, fresh)
HTTP   ──► POST /v1/responses { stream: true, store, background } ────────┐
                                                                          │
       framework: task_fn.start(task_id, input=params)                    │
       framework: input.disposition="re-invoke" persisted at .start()     │
                  (durable before the body runs)                          │
       framework: schedule task body; handler invoked                     │
       handler:   emit response.created (seq=1)                           │
       framework: persist response envelope → response store              │
       handler:   emit response.in_progress (seq=2)                       │
       framework: ...stream events... emit output_item.added(idx=0) (seq=3)│
       framework: emit output_item.delta(idx=0, "Hel") (seq=4)            │
                                                                          │
       HTTP    ◄── live SSE events ────────────────────────────────────────┘
       
       ════════════ SIGKILL ════════════
       
       (next lifetime — recovery scanner re-fires task)
       primitive: task lease expired → re-fire task body
       framework: task body entered with context.is_recovery=True
       framework: read input.disposition → "re-invoke"
       framework: assign flat fields on response context (is_recovery=True, is_steered_turn=False, pending_input_count=0)
       framework: reconstruct ResponseExecution, ResponseContext from serialized params
       framework: re-invoke handler with flat-field assignment on context
       handler:   is_recovery == True
       handler:   query upstream framework for resumption state
       handler:   build resumption_response = ResponseObject(output=[...committed_items])
       handler:   construct ResponseEventStream(response=resumption_response)
       handler:   emit response.created  (seq=N, framework swallows duplicate persist)
       handler:   emit response.in_progress(response=resumption_response)
                  (seq=N+1, CLIENT-VISIBLE RESET POINT)
       handler:   resume from upstream-resumption-point; emit further deltas / items
       handler:   emit response.completed (seq=N+k)
       framework: persist terminal → response store
                                                                          
       (client reconnects after recovery)
HTTP   ──► GET /v1/responses/resp_1?stream=true&starting_after=4 ─────────┐
       framework: stream event store returns seq=5, 6, 7, ..., N, N+1, ...│
       HTTP    ◄── SSE events 5..N+k                                       │
       client:   observes second response.in_progress at seq=N+1           │
       client:   REPLACES local response.output with the event's payload   │
       client:   processes subsequent events on top of the new snapshot    │
                                                                          ─┘
```

### §13.2 — Row 2 (`resilient_background=False`, bg+store), crash before terminal

```
       (turn 1, fresh)
HTTP   ──► POST /v1/responses { stream: false, store, background } ───────┐
                                                                          │
       framework: start resilient task with disposition="mark-failed"        │
       framework: task body invokes handler (handler runs INSIDE the body) │
       handler:   emit response.created                                    │
       framework: persist response envelope                                │
                                                                          │
       HTTP    ◄── 200 { id: resp_1, status: in_progress, ... }            │
       
       ════════════ SIGKILL ════════════
       
       (next lifetime — recovery scanner re-fires the task)
       primitive: task lease expired → re-fire task body
       framework: task body entered with context.is_recovery=True
       framework: read input.disposition → "mark-failed"
       framework: lookup response in store: status="in_progress"
       framework: persist failed terminal:
                  { status: "failed",
                    error: { code: "server_error",
                             message: "Server interrupted before completing this response" }}
       framework: task body returns → task → completed
       
       (client polls)
HTTP   ──► GET /v1/responses/resp_1 ──────────────────────────────────────┐
       framework: return persisted failed envelope                        │
                                                                          ─┘
```

### §13.3 — Row 4 (no store), crash mid-handler

No recovery. The handler dies with the process. Any HTTP caller still
holding the connection sees a closed socket. No persisted envelope, no
recovery scanner action.

---

## §14 — Conformance items

Each conformance item is a normative behaviour that an implementation
MUST exhibit. The label is for cross-reference from tests and other
specs.

### C-MATRIX — Dispatch matrix

For every `POST /v1/responses`, the implementation MUST select exactly
one of the four rows in §3 based on `(store, background, resilient_background)`,
and MUST deliver each of Termination Paths A, B, C as documented in
§3.1.

### C-CHAIN — Chain identity

The chain id MUST be derived per §4.1. `task_id` MUST be derived per
§4.2 (deterministic; partition-key-prefixed; agent+session salted;
SHA-256 truncated). `context.conversation_chain_id` MUST expose the
chain id to handlers per §4.3.

### C-NS — Reserved namespace (defensive guard)

The handler-facing metadata API MUST reject keys and namespace names
starting with `_` per §5 — a defensive guard so handlers cannot invent
framework-reserved namespaces. The framework itself no longer creates a
`_responses` namespace (Spec 039 R1); `response_id` / `background` /
`disposition` are sourced from the durable task **input** (§5.1–§5.3),
which is persisted at `.start()` (before the body's first interruptible
await), satisfying the ordering rule by construction.

### C-PERPETUAL — Perpetual task

For Row 1 with `steerable_conversations=true`, the resilient task body
MUST signal implicit-suspend (in this implementation: `return None`
from a `@multi_turn_task`-decorated body) after the handler's terminal,
keeping the task alive for subsequent turns per §6.1. For Rows 2/3,
the task body invokes the handler directly; on graceful shutdown
without explicit `exit_for_recovery`, the body persists the
`shutdown_reason=grace_exhausted` failed terminal before returning.

### C-DISPOSITION — Recovery dispatch

On recovered entry, the task body MUST read `disposition` from the
durable task input (§5) and route per §7. For `re-invoke`, the handler
is re-invoked with `is_recovery=True`. For `mark-failed`, the handler is
NOT re-invoked; a `server_error` terminal is persisted unless the
response is already terminal (§7.2 idempotency check).

### C-SERVER-ERROR — `server_error` payload

Every framework-emitted shutdown/crash marker MUST conform to the
shape in §7.3 — `code="server_error"` + a path-specific `message` (no
`type` and no `additionalInfo` on the response-object `ResponseError`;
the internal recovery cause is not surfaced to customers). Output is
the preserved snapshot's output when a snapshot exists (§7.2 step 3),
and `[]` only when none was ever persisted.

### C-RESILIENCE-CTX — Flat recovery + steering surface on `context`

The handler MUST observe the flat recovery + steering fields on the
response context: `is_recovery: bool`, `is_steered_turn: bool`,
`pending_input_count: int` (see §8). Application state is explicitly
persisted through `FoundryStateStore` (§8.1).

### C-RECOVERY-MODEL — Three-actor recovery contract

The framework MUST re-invoke the handler with `is_recovery=True` per
§8.2 (no dedup of handler-emitted SSE events; persist the envelope
exactly-once at start and at terminal). The handler-side contract is
specified in §8.2 / §8.3 — a naive handler MUST still produce a
correct response (the framework MUST accept duplicate
`response.created` and duplicate terminals, treat second-or-later
`response.in_progress` as a reset, and tolerate output-index re-use).

### C-STREAM-ORDER — Stream persistence

The framework MUST persist every SSE event in emission order, MUST
assign strictly monotonic `sequence_number` per `response_id`, MUST
NOT deduplicate events across recovery attempts (§9.1).

### C-RECONNECT — `starting_after=`

`GET /responses/{id}?stream=true&starting_after=N` MUST return only
events with `sequence_number > N`. The reconnection MUST work
identically for fresh, recovered, and multiply-recovered streams
(§9.2).

### C-RESET — Reset on `response.in_progress`

Clients MUST treat any second-or-later `response.in_progress` as a
snapshot reset per §9.3. The framework's persisted-state machine MUST
observe the same rule when applying events to the persisted response.

### C-IDEMPOTENT — Idempotent `create` and terminal

`create_response()` MUST raise `ResponseAlreadyExistsError` for an
existing non-deleted entry per §9.4. The framework MUST swallow this
on recovery (log INFO; proceed to `update_response()`). Duplicate
terminal events MUST be idempotent at the persistence layer.

### C-INDEX-REUSE — `output_index` slot semantics

After a snapshot reset, the handler MAY re-use `output_index` values;
the framework MUST allow it and treat re-used indexes as slot
replacement per §9.5. `ResponseEventStream(response=...)` MUST seed
its internal counter past the highest pre-existing index per §9.6.

### C-CANCEL — Cancellation surface

`cancellation_signal` (3rd positional handler arg) and `context cancellation cause (composing — see §10)` MUST
be populated per §10. The cancellation policy (no `cancelled` from
steering or shutdown; framework forces `failed` for missing terminal;
cooperation model) MUST be enforced per §10.

### C-CANCEL-RECOVERY — Cancel × recovery composition

Pre-crash cancellation triggers MUST be re-surfaced on recovered
entry per §10.1. A recovered handler that returns without emitting
terminal under `SHUTTING_DOWN` MUST cause the framework to raise
`CancelledError` so the task stays `in_progress` for the next
lifetime.

### C-LOCK — Conversation lock

For `store=true` with `steerable_conversations=false`, a new turn
arriving while a prior turn for the same chain is in progress MUST
return HTTP 409 `conversation_locked` per §11.1.

### C-FORK-REJECT — No forking of steerable chains

For `steerable_conversations=true`, a turn whose
`previous_response_id` does not match the chain's `last_input_id`
MUST return HTTP 409 `conversation_fork_not_supported` per §11.2.
Concurrent same-`previous_response_id` POSTs MUST resolve so that
exactly one wins; the others get the 409.

### C-ACCEPT — Acceptance hook

The acceptance hook MUST run only for steered turns (not first
turns), synchronously during request handling, and MUST produce the
HTTP-visible queued response envelope per §11.3. If the hook is
unregistered or raises, the framework MUST emit the default queued
envelope.

### C-STEER-DELIVERY — Steering delivery order

For `steerable_conversations=true`, queued turns MUST drain in FIFO
order, with no concurrent handler executions for the same chain
(§11.4). Drained turns MUST observe `is_steered_turn=True`.
`pending_input_count` MUST count post-this queued turns.

### C-COMPOSE — Composition guards

`resilient_background=true` requires `store=true` to engage row 1; if
`store=false`, the request falls through to row 4 regardless of
`resilient_background`. `steerable_conversations=true` requires
`store=true` for the steering queue and acceptance hook to function;
implementations MUST reject the combination at startup or fall
through to non-store behaviour per their stability policy.

---

## §15 — Worked storage timeline (worked example)

A `(store=true, background=true, resilient_background=true, stream=true,
steerable_conversations=true)` chain with two turns and a crash
between them. Numbers are illustrative.

```
T=0   POST /v1/responses { input: "Hi", store: true, background: true }
      → derive_task_id  = "rchain_AB12..."
      → conversation_chain_id = "rchain_AB12..."  (== task_id; standalone first
                                              turn, derived from resp_1's
                                              embedded partition key)

T=1   primitive: task_store.create({
        id: "rchain_AB12...",
        status: "in_progress",
        payload: { input: <serialized ResilientResponseInput> },
        ...
      })

T=2   task body entered (fresh)
      primitive: _framework.last_input_id = resp_1 (precondition stamp)
      (disposition="re-invoke" / response_id=resp_1 / background=true are
       already on payload.input — persisted at T=1, no separate stamp)
      handler:   emit response.created
      framework: response_store.create({
                   id: resp_1, status: "in_progress", ...
                 })
      framework: stream_store.append(seq=1, event=response.created)

T=3   handler:   emit response.in_progress (seq=2)
      handler:   emit output_item.added(idx=0)
      framework: stream_store.append(seq=3, ...)
      handler:   emit output_item.delta(idx=0, "Hel")
      framework: stream_store.append(seq=4, ...)

T=4   ═══════ SIGKILL ═══════
      
T=5   process restarts; lease scanner sees "rchain_AB12..."
      with status="in_progress" and expired lease

T=6   primitive: re-fire task body with ctx.context.is_recovery=True
      framework: read input.disposition → "re-invoke"
      framework: assign flat fields on response context
                 (is_recovery=True,
                  is_steered_turn=False,
                  pending_input_count=0)
      framework: reconstruct (ResponseExecution, ResponseContext)
                 from serialized params
      framework: re-invoke handler

T=7   handler:   is_recovery == True
      handler:   query upstream framework for committed state
      handler:   build resumption_response (e.g., output=[] for naive
                 handler; or output=[committed_items] for recovery-aware)
      handler:   stream = ResponseEventStream(response=resumption_response)
      handler:   emit response.created
      framework: response_store.create({...}) → ResponseAlreadyExistsError
      framework: log INFO "_persist_create dedup'd on recovery"; continue
      framework: response.created GATED — the resilient stream is non-empty
                 (seq 1-4 survived the crash), so the provider append is
                 SUPPRESSED (spec 026 empty-stream gate). seq=5 is consumed
                 but never stream-visible; the recovered handler's
                 response.in_progress (next) is its first stream event.

T=8   handler:   emit response.in_progress (carries resumption_response)
      framework: stream_store.append(seq=6, event=response.in_progress)
                 NOTE: this is the second response.in_progress → reset event
      framework: persisted-response logic: REPLACE response.output with
                 resumption_response.output

T=9   handler:   emit output_item.added(idx=0, content=<new attempt>)
      framework: stream_store.append(seq=7, ...)
      framework: persisted: REPLACE output[0] (idx already present after reset)
      ...
      handler:   emit response.completed (seq=K)
      framework: response_store.update({id: resp_1, status: "completed", ...})
      framework: stream_store.append(seq=K, event=response.completed)

T=10  task body returns Suspended (steerable_conversations=true)
      primitive: task → status="suspended", awaiting next input

T=11  POST /v1/responses { input: "Now this", previous_response_id: resp_1,
                           store: true, background: true }
      → derive_task_id = SAME "rchain_AB12..." (chain inherits)
      framework: task_fn.start(task_id, input_id=resp_2,
                               if_last_input_id=resp_1)
      primitive: precondition holds (_framework.last_input_id == resp_1)
      primitive: advance _framework.last_input_id = resp_2
      primitive: task resumes (status: suspended → in_progress)
      ...turn 2 proceeds...
```

### §15.1 — Concurrent fork-attempt timeline

```
T=11a POST /v1/responses { previous_response_id: resp_1, ... }
T=11b POST /v1/responses { previous_response_id: resp_1, ... }   (concurrent)
      
      primitive: both call start(input_id=resp_2/resp_3, if_last_input_id=resp_1)
      primitive: atomic precondition CAS on _framework.last_input_id
      primitive: exactly one wins (say T=11a), advances last_input_id=resp_2
      primitive: T=11b sees stale last_input_id → LastInputIdPreconditionFailed
      framework: T=11a → 200 (queued or in_progress)
      framework: T=11b → 409 conversation_fork_not_supported
```

---

## §16 — Storage layout

The framework engages three logical stores:

### §16.1 — Resilient task store

Owned by the underlying task primitive. Holds:

- `task_id` (the §4.2 derivation)
- `status` (one of `queued`, `in_progress`, `suspended`, `completed`,
  `cancelled`, `failed`)
- `payload.input` (current turn's serialized input + recovery boundary —
  carries `disposition` / `response_id`; cleared at suspend per the core
  spec's data-retention rule)
- `payload.steering` (the primitive's steering-queue state — owned by
  the core spec)
- `payload._framework.last_input_id` (the input-precondition primitive's
  CAS slot from §11.2)
- `metadata` (developer's checkpoint store, in named namespaces)
- Lease state (owned by the primitive)

### §16.2 — Response store

Holds the `ResponseObject` envelope per `response_id`. Operations:

| Operation | Semantics |
|---|---|
| `create_response` | Idempotent at the conformance layer (§9.4). Raises `ResponseAlreadyExistsError` on conflict; callers swallow on recovery. |
| `update_response` | Updates the envelope in place. Raises `KeyError` if not present (caller falls back to `create_response` for race recovery). |
| `get_response` | Returns the envelope. |
| `delete_response` | Soft-delete. |

Local-dev implementations (`FileResponseStore`) MUST persist envelopes
to disk atomically (write to tempfile + `os.replace()`). Production
implementations (Foundry) MUST translate the HTTP 409 from
double-`POST` into `ResponseAlreadyExistsError`.

#### §16.2.1 — `FileResponseStore` on-disk layout (local dev, informative)

The response-store **contract** above (operations + atomic envelope
commit) is normative. The physical file layout below is specific to the
local-dev `FileResponseStore` and is **not** binding on other
implementations (Foundry uses its own storage); it is documented here
because the file provider is part of the responses resilience workstream.

Under the store root, each item is persisted **exactly once**; the
response envelope and conversations hold only pointers:

```
responses/
    {response_id}.json        # envelope. output[] entries are pointer
                              #   stubs {"$item_ref": <item_id>} for id'd
                              #   items; id-less items stay inline.
    {response_id}.indexes.json # ordered {input,output,history}_item_ids —
                              #   the single place history_item_ids is read.
    {response_id}.deleted     # soft-delete marker
items/
    {item_id}.json            # THE one copy of each item's content
conversations/
    {conversation_id}.json    # {response_ids: [...]}
```

- `get_items` / `get_input_items` / `get_history_item_ids` resolve content
  and id lists from `items/` + `indexes.json`; `get_response` rehydrates
  the envelope's pointer stubs from `items/`, returning a `ResponseObject`
  whose `output[]` is byte-equal (content and order) to the in-memory
  provider.
- **Crash ordering.** Writers store every referenced item under `items/`
  **before** the atomic envelope write. Items are immutable by id (re-stores
  are idempotent same-content), so a crash exposes either the prior or the
  new snapshot — **never** an envelope referencing a missing or
  mid-mutated item. An unresolvable pointer on read is treated as transient
  corruption (a non-`KeyError` storage error), **not** as the "definitively
  absent" not-found that triggers the §7 recovery drop.
- There is no per-response item directory and no separate `history.json`
  (both were redundant copies of data already in `items/` / `indexes.json`).

### §16.3 — Stream event store

Holds the ordered SSE event log per `response_id`. Operations:

| Operation | Semantics |
|---|---|
| `append(event)` | Append with strictly monotonic `sequence_number`. No dedup across recovery attempts. |
| `read(starting_after=N)` | Return events with `sequence_number > N`. |
| `read(starting_after=None)` | Return the full log. |

Local-dev implementations (`FileStreamProvider`) MUST persist events
to disk in the order they are appended. Production implementations
MUST give the same ordering guarantee. TTL-based replay cleanup
(framework-internal, defaults to at least 10 minutes per Rule B35)
is allowed.

A reset event (§9.3) is a `response.in_progress` event with
`sequence_number > N` where N is the previous `response.in_progress`
event's `sequence_number` for the same `response_id`.

---

## §17 — Composition constraints

### §17.1 — `resilient_background=true` requires `store=true`

If `store=false`, the request falls through to Row 4 regardless of
`resilient_background`. There is no persistent record to recover from;
the resilient orchestrator is bypassed. The implementation MUST NOT
silently fail; the row-4 best-effort marker fires per §6.3.

### §17.2 — `steerable_conversations=true` requires `store=true`

The steering queue, the conversation lock, and the acceptance hook
ALL depend on the resilient task primitive. With `store=false`, no
resilient task is created; there is no queue to enqueue into; the
acceptance hook is not invoked. Implementations MUST either reject the
combination at startup or document the no-op fall-through clearly.

### §17.3 — `steerable_conversations=true` × `resilient_background=false`

This combination is supported (composition guard relaxed in). The Row 2 task still provides the conversation lock and the
acceptance hook; the handler runs inside the task body just like
Row 1. The only difference from Row 1 is the recovery disposition —
`mark-failed` instead of `re-invoke`. The crash-recovery branch
persists `failed` per §7.2 instead of re-invoking the handler.

### §17.4 — `background=false` + steerable

This is Row 3. The handler runs inside the resilient task body; the
HTTP request awaits the task body's terminal via the framework's
`TaskRun.result()` API. A new turn arriving mid-handler still goes
through the queue / lock / acceptance hook per §11. (Note:
`background=false` + steering means the original HTTP caller's
connection is open while the handler runs to completion; a steered
turn arriving from a different client connection gets queued.)

---

## §18 — What this spec does NOT cover

- The underlying resilient-task primitive's own contract (lease,
  heartbeat, suspend/resume, steering queue, retry semantics,
  recovery scanner): see
  `azure-ai-agentserver-core/docs/task-and-streaming-spec.md`.
- Multi-replica / cross-region recovery. Single-node-restart only.
- Wire-format additions to the OpenAI Responses HTTP/SSE protocol.
  This spec adds new HTTP error codes (`conversation_locked`,
  `conversation_fork_not_supported`) and the recovery-time
  `response.in_progress` reset semantics; everything else uses
  existing OpenAI Responses event shapes.
- Schema migrations for `metadata` shapes across SDK upgrades.
- The OpenAI Responses input-conversion / output-rendering pipeline
  itself.

---

## §19 — Cross-references

| External | Topic |
|---|---|
| `azure-ai-agentserver-core/docs/task-and-streaming-spec.md` | Underlying resilient-task primitive (lease, suspend, recovery scanner, steering queue, input-precondition primitive, streaming reconciliation). |
| `azure-ai-agentserver-responses/docs/resilient-responses-developer-guide.md` | Developer-facing guide; configuration, public API surface, common patterns. |
| `azure-ai-agentserver-responses/docs/handler-implementation-guide.md` | Developer-facing guide; cancellation patterns, resumption response construction, framework-agnostic recovery walkthrough. |
| `azure-ai-agentserver-responses/docs/resilience-contract.md` | The per-row × per-path conformance contract matrix (rows 1–4 + Row 11 checkpoint-write); the test-facing companion to this design spec. |

A change to this spec implies coordinated changes to those documents.
A change to the resilient-task primitive's recovery / streaming /
steering surface implies a review of this spec.

---

## §20 — Change discipline

This spec is the source of truth for the responses resilience layer.
Implementation MUST NOT diverge silently. Every change here is
mirrored by:

1. The corresponding implementation change in the chosen host
   language (orchestrator + dispatch + endpoint layer).
2. The two developer guides above.
3. A conformance test under the resilience-contract suite that
   exercises the new or changed behaviour end-to-end through the
   create-response endpoint, on the real file-based providers, with
   a real crash harness for any recovery-relevant change.

If a future change has to alter this contract (rather than extend it),
this document MUST be updated first, the change MUST be reviewed as a
contract change, and the implementation MUST land in a single
coordinated commit alongside the contract update.
