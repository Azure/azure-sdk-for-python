# Durability Contract — Authoritative Specification

**Status**: Authoritative. This document is the single source of truth for the durability contract of `azure-ai-agentserver-responses`.
**Audience**: Framework maintainers, handler authors, integration owners, SDK reviewers.
**Stability**: Contract changes here are breaking; they require a versioned amendment (see "Change control" at the end).

This document defines:
- The **flags and server options** that select a durability behavior.
- The **termination lifecycle** — the three paths a server lifetime can take when a request is in flight (graceful-within-grace, graceful-grace-exhausted, crash-or-grace-failure).
- The **matrix** — for each combination of flags, what the framework promises on each termination path.
- The **mechanisms** that deliver each promise.
- The **streaming sub-contract** that applies on top of the matrix when `stream=true`.
- The **composition rules** (what flag combinations require what server providers).
- The **obligations** placed on handler authors vs the framework.

Everything else — wire formats, OpenAI-compatibility, transport, sample app conventions — is OUT of scope here and belongs in service-API, transport, or sample specs.

This document supersedes the matrix snippets in `azure-ai-agentserver-responses/docs/durable-responses-developer-guide.md` and `handler-implementation-guide.md`; those docs SHOULD link here for the normative contract and keep developer-friendly summaries with a clear "see durability-contract.md for the normative version" pointer.

---

## How to read this document

1. If you're a handler author asking "what happens if the server dies?", read **The matrix** then your row's **Per-row contract** then **Handler obligations**.
2. If you're a framework maintainer making changes anywhere near durability, read the whole document. Every change MUST keep every row × applicable-path behavior intact (see **Test discipline**).
3. If you're a reviewer writing a new spec that touches durable behavior, the spec's exit checklist requires you to declare which rows your spec affects and confirm the contract-conformance tests stay green; see **Test discipline** and the spec-template gate.

The terms `MUST`, `MUST NOT`, `SHOULD`, `MAY` follow RFC 2119.

---

## Concepts

### Request flags

Three boolean flags on the request select the durability shape:

- **`store`** *(request body, default `true`)* — whether the response and its events are persisted to the configured `ResponseStore`. When `false`, the response lives only in the in-flight process; clients must keep the request connection open to observe it.
- **`background`** *(request body, default `false`)* — whether the request returns immediately with an `in_progress` response that clients poll/stream-reconnect to observe. When `false`, the request is foreground: the response is returned over the original HTTP connection only.
- **`stream`** *(request body, default `false`)* — whether the response is delivered as SSE events on the original connection. Independent of durability shape; see **The matrix** for how `stream` interacts.

### Server option

One server-side option gates the strongest guarantee:

- **`durable_background`** *(server option, default `False`)* — whether the framework engages full crash-recovery for background+store=true requests. When `False`, those requests fall to a weaker (mark-failed) guarantee. When `True`, the framework requires the supporting providers to be present (see **Composition rules**) and fails loud at startup if they are not.

### Termination paths

Every in-flight request faces one of three paths from the moment the process receives a termination signal (or experiences an abrupt crash). The matrix specifies a contract per path.

The responses package is a CONSUMER of an underlying **durable-task primitive** that provides automatic recovery of registered work on the next process lifetime. The contract below specifies what the responses package guarantees to the caller; the durable-task primitive's internal mechanics (how it persists registrations, how it detects expired work, etc.) are not part of this contract and are subject to change as long as the per-path guarantees here are preserved.

#### Path A — Graceful shutdown, handler reaches terminal within grace

The runtime receives a graceful-shutdown signal (typically SIGTERM on Unix, equivalent on other platforms). New requests are refused; in-flight handlers continue running. The handler reaches a terminal state (`completed` / `failed` from its own logic / `cancelled`) before the grace period expires. The response transitions naturally; no special framework involvement is required. This is the "happy path" and does not differ across matrix rows.

#### Path B — Graceful shutdown, grace exhausted with handler still running

Same signal as Path A, but the handler has not reached terminal when the grace period expires. The framework MUST act in-process BEFORE the runtime exits:

- It transitions the response per the row's contract (mark `failed` for rows 2/3/4; for row 1, hands the in-flight handler off to the durable-task primitive's recovery so the next process lifetime can re-invoke it).
- It responds to any waiting clients on the original HTTP connection so they observe terminal status in this process's lifetime.
- It then allows the runtime to exit.

Clients do NOT wait for restart on this path. The contract's terminal state is observable within the original shutdown window.

#### Path C — Crash, or graceful shutdown whose Path-B action did not run

The in-process actor is gone before it could run Path B. Examples: SIGKILL, OOM kill, segmentation fault, power loss, hung process during the shutdown loop, panic in Path-B code itself. On startup, the framework MUST scan persisted state and apply each row's restart contract:

- Row 1: re-invoke the handler with `entry_mode="recovered"`.
- Rows 2 and 3: mark the response `failed` with `code=server_error` (the generic server-failure code already used elsewhere in the codebase, e.g. `_endpoint_handler.py`, `_orchestrator.py`). The `message` field carries the path-specific detail ("server interrupted before completing this response" for Path C; "server stopped before this response completed" for Path B).
- Row 4: nothing to do (no persisted state to scan).

Path C is the FALLBACK for Path B. If Path B doesn't run for any reason, Path C catches the response. The implementation MUST ensure Path C is a complete fallback — a Path-B regression must not leave any row × path uncovered.

A single termination event is handled by exactly one path.

### Durable record

For Path C to work, the responses package needs the next process lifetime to know that a response was in-flight and what to do about it. To enable this, every accepted request with `store=true` is registered with the underlying durable-task primitive at acceptance time. The registration carries the response id, the row's path-C disposition (`re-invoke` for row 1; `mark-failed` for rows 2 and 3), and (for re-invocation rows) the handler reference. We call this registration the **durable record**.

On the next process lifetime, the durable-task primitive surfaces any registration that did not reach terminal in the prior lifetime. The framework reads the recorded disposition and applies it — re-invoking the handler for row 1, marking the response `failed` for rows 2 and 3.

How the durable-task primitive detects "did not reach terminal in the prior lifetime", where it persists registrations, and how it coordinates with running handlers are concerns of the primitive itself. The responses package treats the primitive as a black box that delivers the per-path guarantees in the matrix.

`store=false` requests have no durable record; Path C does not apply.

### In-process shutdown loop

The mechanism that makes Path B work is the **in-process shutdown loop**: a coroutine wired into the runtime's lifespan teardown that iterates in-flight responses, applies each row's Path-B action before the grace deadline, and responds to waiting clients. The precedent implementation lives at `azure-ai-agentserver-responses/azure/ai/agentserver/responses/hosting/_endpoint_handler.py` (search for the in-flight tracker walk and `mark_failed` call in the shutdown handler).

---

## The matrix

The matrix is the per-row × per-path contract. Rows are keyed on three flags (`store`, `background`, `durable_background`). `stream` is intentionally NOT a row key: the contract is mode-flag agnostic with respect to `stream`. Where `stream` affects HOW the contract is delivered (notably row 1 Paths B and C), the streaming sub-contract specifies the additional rules.

| Row | `store` | `background` | `durable_background` | Path A (within-grace) | Path B (grace exhausted) | Path C (crash / Path-B failure) |
|----:|---------|--------------|----------------------|-----------------------|--------------------------|---------------------------------|
|  1  | `true`  | `true`       | `True`               | natural terminal      | hand the in-flight handler to the durable-task primitive's recovery; runtime exits; next lifetime re-invokes handler with `entry_mode="recovered"` | next lifetime re-invokes handler with `entry_mode="recovered"` |
|  2  | `true`  | `true`       | `False`              | natural terminal      | mark response `failed` (`code=server_error`) in-process before exit; respond to waiting clients | next lifetime marks response `failed` (`code=server_error`) |
|  3  | `true`  | `false`      | any                  | natural terminal      | mark response `failed` (`code=server_error`) in-process before exit; respond to waiting clients | next lifetime marks response `failed` (`code=server_error`) |
|  4  | `false` | any          | any                  | natural terminal      | best-effort `failed` marker in-process; original HTTP connection may already be closing | no recovery applies (no persisted state) |

Read every cell as a MUST for the framework. Path A is the same across all rows because no framework intervention is needed. Path B and Path C differ row by row.

### "Marked failed on restart" precise reading

Some older documents shorthand rows 2 and 3 as "marked failed on restart." The precise statement is "marked failed in-process at end of grace (Path B) AND marked failed on restart as the Path-C fallback." Both deliveries MUST exist; clients receive Path-B terminal when Path B fires, restart-fallback terminal otherwise. The matrix above replaces the shorthand.

---

## Per-row contracts

### Row 1 — Full recovery contract (`store=true, background=true, durable_background=True`)

**What it gives the handler author**: a persistent per-response key-value metadata store and a fence (`flush`) you can use to record progress before side effects; if the server dies, your handler re-enters with `entry_mode="recovered"` and the metadata still there, and you decide from your own stored keys where to resume. Clients observe the response either via background polling or streaming reconnection; both work across crash recovery.

**Path A.** Handler completes within grace. Standard happy path. No framework involvement specific to durability beyond normal completion.

**Path B.** Grace expires with handler still running. The framework MUST:
1. Stop scheduling new handler work but allow the current step to complete to a safe boundary if it can do so within the remaining shutdown window.
2. Hand the in-flight handler off to the durable-task primitive's recovery so the next process lifetime can re-invoke it.
3. Do NOT mark the response `failed` — the contract is recovery, not failure.
4. Exit the process.
The next process lifetime re-invokes the handler with `entry_mode="recovered"`. The recovered handler resumes per the **Recovery handler entry contract** (below).

**Path C.** SIGKILL or Path B didn't complete. On the next process lifetime, the framework finds the response's durable record and re-invokes the handler with `entry_mode="recovered"`. Same delivery as Path B post-restart.

**Recovery handler entry contract** (Path B post-restart and Path C):
- The handler receives `context.durability.entry_mode == "recovered"` (the convenience `context.durability.is_recovery` is `True`).
- `context.durability.metadata` is the handler's persistent state surface. It is a **callable namespace facade**: `metadata["key"]` reads/writes the default namespace; `metadata("name")["key"]` reads/writes a sibling namespace; each namespace tracks dirty state independently and is snapshotted at lifecycle boundaries. The handler-facing wrapper **rejects** keys (and namespace names) starting with `_` with `ValueError` — those prefixes are reserved for framework-internal namespaces (e.g. `_responses` for the responses orchestrator). The framework guarantees values written via `metadata[key] = value` followed by `await metadata.flush()` (or `await metadata("name").flush()`) are visible to the recovered invocation.
- The framework does NOT impose a watermark schema or a checkpoint primitive. The handler chooses what keys it stores in `metadata` and what they mean. Common patterns (resume cursor, side-effect dedup token) are illustrated in `handler-implementation-guide.md`.
- The handler emits a `response.in_progress` reset event as its FIRST event of the recovered invocation. This signals reconnecting clients to reset their accumulator (see **Streaming sub-contract** for client side).
- To make a side effect at-most-once across re-invocations, the handler MUST write a dedup token to `metadata`, call `await metadata.flush()` BEFORE issuing the side effect, and on recovery skip the side effect if the dedup token is already present. This pattern is owned by handler code; the framework provides only the metadata store and `flush()`.
- ``context.durability.retry_attempt`` is the **cross-lifetime** failure-retry counter for this response. It persists across crash/recovery (re-hydrated from the underlying task's ``payload["_retry_attempt"]``), resets to 0 on successful invocation and on steering drain, and increments only when the handler raises a retryable failure. Use ``entry_mode`` / ``is_recovery`` to distinguish "this is the first lifetime that re-entered after a crash" from "the handler raised and we are about to retry inside the same lifetime".

This contract is established in `010-responses-durable-background/spec.md:37-89` and detailed in `012-durable-recovery-contract/spec.md`.

### Row 2 — Marked failed (`store=true, background=true, durable_background=False`)

**What it gives the handler author**: a stored, observable response that survives the original HTTP connection (so clients can poll or stream-reconnect), but without crash recovery. If the server dies mid-handler, your response goes to `failed`; there is no re-invocation.

**Path A.** Handler completes within grace. Standard.

**Path B.** Grace expires with handler still running. The in-process shutdown loop MUST:
1. Mark the response `failed` with `code=server_error`. The `message` field describes the Path-B cause ("server stopped before this response completed", or equivalent operator-friendly wording). The framework MAY include a separate diagnostic field (e.g. `error.additionalInfo.shutdown_reason="grace_exhausted"`) for operators, but the client-visible `code` stays generic.
2. Persist any final events already emitted.
3. Respond to any waiting clients (polling GET, streaming SSE) so they observe terminal in this lifetime.
4. Exit.

**Path C.** SIGKILL or Path B didn't run. On the next process lifetime, the framework finds the response's durable record (disposition `mark-failed`) and MUST:
1. Mark the response `failed` with `code=server_error`. The `message` field describes the Path-C cause ("server interrupted before completing this response", or equivalent). The framework MAY include `error.additionalInfo.shutdown_reason="crash_recovery"` for operator diagnostics; the client-visible `code` stays generic.
2. Persist any final events already emitted plus a synthetic terminal event so subsequent polling and stream-reconnect requests see terminal.

### Row 3 — Marked failed, foreground (`store=true, background=false`, any `durable_background`)

**What it gives the handler author**: a stored response observable over the original HTTP connection (foreground). If the connection is broken before the handler completes, the client cannot observe completion (no polling endpoint applies semantically). If the server dies, the response is marked `failed` so any retrieval via `GET /responses/{id}` returns terminal — for clients that hold the response id from an earlier interaction.

`durable_background` is intentionally a free axis for row 3 — foreground responses do not benefit from durable handler recovery because the client connection is gone; the row 3 contract is the same whether `durable_background=True` or `False`.

**Path A / B / C**: same shape as row 2. All failure markers use `code=server_error`; path-specific cause goes in `message` (and optionally in an `additionalInfo` diagnostic field) per the per-path rules in row 2 above.

### Row 4 — Best-effort (`store=false`, any `background`, any `durable_background`)

**What it gives the handler author**: in-memory-only response, no persistence, no recovery. Use when the response is ephemeral (e.g. dev iteration) or when storage backends are intentionally not configured.

**Path A.** Handler completes within grace. Standard.

**Path B.** The in-process shutdown loop MAY attempt to write a final `failed` event to the open HTTP connection on a best-effort basis. The contract does NOT require persistence (there's nowhere to persist to). Clients SHOULD be tolerant of an abruptly-closed connection.

**Path C.** No persisted state, so no next-lifetime action applies. Clients are responsible for treating an abandoned connection as failure on their side.

---

## Streaming sub-contract

When `stream=true`, the matrix row's contract applies as written, PLUS the following streaming-specific rules. The streaming sub-contract was originally specified in `010-responses-durable-background/spec.md:282-293`.

### Server-side rules

1. **Event persistence (row 1, row 2).** Every emitted SSE event MUST be appended to the durable stream provider in order, BEFORE being flushed to the original HTTP connection. This guarantees a reconnecting client can be served the same prefix of events that the original connection saw.

2. **Resumable reconnect endpoint.** A GET on `/responses/{id}?stream=true&starting_after=<event_id>` MUST return the durable events strictly after `<event_id>` and then switch to live tailing if the response is still in progress, or to the final terminal event otherwise. (Rows 1 and 2; row 4 is not applicable since there's no persistence.)

3. **`response.in_progress` reset event (row 1 Paths B post-restart, and C).** On handler re-invocation, the recovered handler MUST emit a `response.in_progress` event as the first event of the new invocation. This event MUST carry the corrected `output_items` (reflecting the post-recovery state if any output items were finalized pre-crash).

4. **At-most-once event ids.** Event ids are stable across recovery: an event that was persisted pre-crash retains its id; recovered events get fresh monotonic ids picking up after the last pre-crash id. The reconnecting client uses `starting_after=<last_seen_id>` to skip what it already has.

### Client-side rule

A streaming client MUST reset its in-memory accumulator (delta buffer, output-item map, etc.) on EVERY `response.in_progress` event AFTER the first one. The first `response.in_progress` is the normal start signal; any subsequent one means recovery has happened and the prior accumulation is stale. The post-reset events (which the handler emits as the first events of its recovered invocation) carry the corrected state.

This rule is published in the developer guide's "Stream Recovery" section; client libraries (Python, etc.) implement it inside their stream-iteration helpers so application code doesn't need to think about it.

### Reconnection semantics

A client that loses the original streaming connection MUST be able to reconnect via the GET endpoint above and resume from its last-seen event id without missing or duplicating events (modulo the `response.in_progress` reset, which is by design). Polling for row 1 is supported as a fallback: the client can GET `/responses/{id}` and see the terminal once recovery completes.

---

## Composition rules

Some flag/option combinations require specific server providers. The framework MUST validate at startup and fail loud if a required provider is absent (per RFC 2119 MUST). It MUST NOT silently downgrade to a weaker row.

| Server config | Required providers | If missing |
|---|---|---|
| `durable_background=True` | `ResponseStore` supporting durable task records; a `DurableStreamProviderProtocol` for streamed durable responses | Startup error naming the missing provider |
| `store=true` requests accepted (any row) | `ResponseStore` | Startup error |
| `stream=true` requests accepted (any row) | A streaming-capable transport configuration | Startup error |

The rationale: silent downgrade is the bug class this whole document exists to prevent. Operators who configured `durable_background=True` made a deliberate choice; the framework either honors it or refuses to start.

---

## Cross-cutting note — Lease eviction (`binding_mismatch`)

*Added by spec 016 (Durable-task primitive contract hardening). This note is NOT a matrix row — eviction is orthogonal to the (store × background × durable_background) axes that define rows 1-4 above. It applies uniformly to any durable record persisted via the task-store protocol.*

The task-store API rejects writes from an orphan sandbox (a sandbox whose host has been replaced; previous lifetime no longer authoritative) with `HTTP 409` and body `$.error.code == "binding_mismatch"`. The framework MUST classify this rejection as `evicted` (not `conflict`) and run a single local-cleanup sequence at every store-write site that may observe it: cancel the local execution task, suppress any pending terminal write, signal awaiters with `TaskConflictError`, log WARNING with `task_id`, `session_id`, and binding_mismatch correlation. The local cleanup MUST be atomic — partial cleanup states are not externally observable.

**Caller-observable outcomes (Invariant 1).** At scheduling primitives, the caller-observable outcome on `evicted` MUST be identical in type and shape to the corresponding live-elsewhere / not-active outcome. Operator WARNING logs are the only differentiator:

| Scheduling primitive | Lease state observed | Steerable? | Caller observes |
|---|---|---|---|
| `.run()` / `.start()` | live elsewhere (non-steerable) | no | `TaskConflictError(current_status="in_progress")` |
| `.run()` / `.start()` | dead lease, reclaimable | no | (inline reclaim succeeds; `entry_mode="recovered"`) |
| `.run()` / `.start()` | dead lease, **evicted** | no | `TaskConflictError(current_status="in_progress")` — **same shape as live-elsewhere** |
| `.run()` / `.start()` | live elsewhere | yes (steerable) | input queued; new `TaskRun` returned |
| `.run()` / `.start()` | dead lease, reclaimable | yes | (inline reclaim succeeds; `entry_mode="recovered"`) |
| `.run()` / `.start()` | dead lease, **evicted** | yes | `TaskConflictError(current_status="in_progress")` — **same shape as the non-steerable live-elsewhere case** |
| `get_active_run()` | any in-progress with live or dead-reclaimable lease | either | `TaskRun` |
| `get_active_run()` | dead lease, **evicted** | either | `None` — **same shape as "not active in this process"** |
| `get_active_run()` | terminal | either | `None` |

No new exception type is introduced for evictions. The orphan-sandbox case is silent to user code; only operator logs surface it.

**Authority.** This note is mirrored in the developer guide §4 Errors (the `TaskConflictError` table) and §7 Recovery. The implementation lives in `_classify_store_write_error` (see `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_client.py`) and is integrated at every store-write site in `_manager.py` and `_lease.py`.

**Test discipline.** The eviction sweep lives at `azure-ai-agentserver-core/tests/durable/test_split_brain_eviction.py` (new module per spec 016 Conformance Test Map row 13). The provider stub fixture in `tests/durable/conftest.py` returns the canonical `binding_mismatch` body shape on configured write operations.

---

## Handler obligations

The handler author's contract surface, for handlers that opt into any row that may re-enter (row 1):

1. **Tolerate re-invocation.** A row 1 handler MUST be safe to invoke more than once for the same response. Local Python state from the prior invocation is gone; persistent state lives only in `context.durability.metadata`.

2. **At-most-once side effects via metadata + flush.** Any work that produces external side effects (LLM calls, external API writes, etc.) that MUST run at most once across re-invocations MUST be guarded by handler code: write a dedup token to `context.durability.metadata` (e.g. `metadata["did_<step>"] = True` or store the upstream-generated request id), call `await context.durability.metadata.flush()`, then issue the side effect; on recovery, check the token and skip if already present. The framework provides the persistent metadata store and the `flush()` fence; the at-most-once pattern is the handler's responsibility.

3. **Resume position via metadata.** The framework does NOT impose a watermark schema. Handlers that need a resume position (e.g. "I have processed input items 0..N") MUST record it in `context.durability.metadata` under a key of their choosing, flushing as appropriate, and MUST read it on `entry_mode == "recovered"` to decide where to resume.

4. **Recovery entry signal.** When `context.durability.entry_mode == "recovered"` (equivalently, `context.durability.is_recovery` is `True`), the handler MUST emit a `response.in_progress` reset event as its first event of the recovered invocation (per **Streaming sub-contract**), then proceed from whatever resume position it stored in metadata.

Rows 2, 3, and 4 do not re-invoke the handler. Handlers running in those rows have no obligations beyond standard async correctness; if they crash, the framework marks the response failed.

---

## Framework obligations

The framework's contract surface, summarized:

1. **Routing.** Every entry path through `_endpoint_handler.handle_create` (foreground, background, streaming) MUST honor the matrix. No mode flag combination may bypass the durable-record creation or the Path-B/Path-C mechanisms.

2. **Durable-record creation.** Every accepted request with `store=true` MUST result in a durable record carrying the row's path-C disposition (re-invoke for row 1; mark-failed for rows 2 and 3).

3. **In-process shutdown loop.** The runtime's lifespan teardown MUST run the in-process shutdown loop for in-flight responses, applying each row's Path-B action before the grace deadline.

4. **Next-lifetime recovery.** On the next process lifetime, the framework MUST consult the durable-task primitive for any in-flight registrations and apply each row's Path-C disposition.

5. **Provider validation.** At startup, the framework MUST validate that all providers required by the configured option combination are present (per **Composition rules**).

6. **Streaming sub-contract delivery.** The streaming-specific rules above MUST be delivered automatically by the framework for any row that includes streaming; handler authors do not write streaming reconnection code.

---

## Test discipline

The matrix is the contract. The contract is enforced by a behavioral test suite at `tests/e2e/durability_contract/` in the responses package.

This section is normative and codified by **Constitution Principle X — Durability Contract Conformance** (`sdk/agentserver/.specify/memory/constitution.md`). The Constitution holds future specs to the same bar; this section publishes the rules.

### Suite requirements

1. **One test module per row** — `test_row_<N>_<short_description>.py`. Each module exercises its row's contract end-to-end through `_endpoint_handler.handle_create` from a real HTTP client.

2. **Every applicable path is exercised via the real signal mechanism.**
   - Path A: SIGTERM with grace period long enough for the handler to complete naturally.
   - Path B: SIGTERM with grace period deliberately short, forcing grace exhaustion while the handler is still running; assert the in-process action fires before subprocess exit and clients see terminal in this lifetime.
   - Path C: SIGKILL via `_crash_harness` mid-handler; restart the subprocess; assert the restart-side action fires.

3. **`stream` is parametrized** — every row module runs each path's assertions for both `stream=False` and `stream=True` (the matrix collapses `stream`, so the contract is the same; the test enforces "the same" empirically).

4. **No mocking, no synthetic shortcuts.** Tests MUST NOT mock `_crash_harness`, fabricate a `DurabilityContext`, call internal failure-marker functions directly, or otherwise short-circuit the real signal path. Path B's grace timing MUST be controlled by a real runtime configuration knob, not a test-only injection.

5. **Completeness meta-test.** `tests/e2e/durability_contract/test_contract_completeness.py` MUST parse this document, extract the matrix, and fail if any (row, applicable-path) is missing from the suite.

6. **Default CI gating.** The suite MUST run in the package's default `pytest` invocation. No opt-in marker.

### TDD discipline for changes affecting durable behavior

Any spec or pull request that affects code in the durability surface (orchestrator routing, shutdown loop, durable-task primitive integration, stream provider) MUST land its contract-conformance tests RED before the implementation change goes green. The pull-request reviewer verifies this from the commit history: the failing-test commit MUST precede the implementation commit for every changed (row, path) pair.

This rule is codified in the spec template's exit checklist and in the project Constitution.

---

## Glossary

- **`code=server_error`** — the generic failure code used whenever the framework marks a response `failed` for a server-side reason it could not avoid. Path-specific cause is conveyed in the `message` field (and optionally in `error.additionalInfo.shutdown_reason`). This code is already used elsewhere in the codebase (e.g. `_endpoint_handler.py`, `_orchestrator.py`) and matches OpenAI's generic-server-error convention; the durability surface deliberately reuses it rather than introducing path-specific codes that would leak framework internals to end users.
- **`entry_mode`** — durability-context field. Values: `"normal"` (first invocation) or `"recovered"` (re-invocation after Path B post-restart or Path C).
- **`retry_attempt`** — durability-context counter. **Cross-lifetime** failure-retry counter — persisted at `payload["_retry_attempt"]` and re-hydrated on every TaskContext construction. Increments only on handler-raised retryable failures (crash recovery does NOT consume the budget). Resets to 0 on successful invocation and on steering drain. Use `entry_mode` / `is_recovery` to distinguish first-time-after-crash from in-lifetime retry.
- **`recovery_count`** — primitive-level counter (renamed from `lease_generation`). Increments each time the task is re-acquired by a new lifetime after a lost lease.
- **`steering_generation`** — primitive-level counter (renamed from `generation`). Increments each time the task is drained for steerable input.
- **`RetryPolicy.max_attempts`** — total failure-retries across all lifetimes for the task. Crash recovery does NOT consume the budget; only handler-raised retryable failures do. When `retry_attempt >= max_attempts`, the framework marks the task `failed` without re-invoking the handler.
- **durable record** — see Concepts. The registration recorded with the underlying durable-task primitive at request acceptance time that lets the next process lifetime know what to do with each `store=true` response (re-invoke vs mark-failed).
- **in-process shutdown loop** — see Concepts. The runtime-lifespan coroutine that delivers Path B.
- **durable-task primitive** — the underlying primitive the responses package layers on top of for cross-lifetime registration and recovery. Treated as a black box by this contract; its internal mechanics are not part of what the responses package promises to callers.
- **`context.durability.metadata`** — callable namespace facade persisted with the response's durable record. `metadata[key]` reads/writes the default namespace; `metadata("name")[key]` reads/writes a sibling namespace. Each namespace tracks dirty state independently and is snapshotted at lifecycle boundaries. The handler-facing wrapper **rejects keys and namespace names starting with `_`** (raises `ValueError`) — those prefixes are reserved for framework-internal namespaces. The default namespace persists at `payload["metadata"]`; named namespaces at `payload["metadata:<name>"]`.
- **`_responses` namespace** — reserved namespace used by the responses framework for internal state (`response_id`, `last_sequence_number`, `background`, `disposition`). Handler code cannot read or write this namespace through the wrapped `DurabilityContext`; the orchestrator writes to it via the underlying `TaskContext` directly.
- **`await context.durability.metadata.flush()`** — force-persist any pending writes for the addressed namespace to the underlying durable-task primitive's store. Use `metadata.flush()` for the default namespace, `metadata("name").flush()` for a named namespace. The fence the handler uses to make at-most-once side-effect patterns work across recovery.

---

## Sources & related documents

This document consolidates and supersedes (for the contract surface) the following:

- `azure-ai-agentserver-responses/docs/durable-responses-developer-guide.md` — developer-friendly overview; should link here for the normative contract.
- `azure-ai-agentserver-responses/docs/handler-implementation-guide.md` — handler-author guide; should link here for the recovery-entry contract.
- `sdk/agentserver/specs/010-responses-durable-background/spec.md` — original durable-background feature spec. The matrix and the durable-record concept originated here.
- `sdk/agentserver/specs/012-durable-recovery-contract/spec.md` — the recovery-entry contract for row 1 handler re-invocation. The streaming sub-contract was refined here.
- `sdk/agentserver/specs/013-*` — cross-process reconstruction work that delivered row 1 Path C for the polled case.

This document does NOT cover:

- Wire format (SSE event shape, response object schema, HTTP status codes) — owned by service-API and transport specs.
- OpenAI-compatibility surface — owned by compat-layer specs.
- Foundry-hosted-agent runtime durability — owned by Foundry runtime spec; the matrix here applies to the self-hosted `azure-ai-agentserver-responses` runtime.
- `azure-ai-agentserver-invocations` durability — the invocations protocol may share concepts but has its own contract document (TBD).

---

## Change control

This document changes via amendment. Process:

1. Open a spec under `sdk/agentserver/specs/NNN-*/` proposing the amendment. The spec MUST cite the exact rows or sections of this document affected and MUST include rationale, backwards-compatibility analysis, and migration guidance (if any).
2. Update this document in the same pull request as the amendment spec is merged. Include a row at the top of the **Change log** below.
3. Update the durability-contract conformance suite at `tests/e2e/durability_contract/` in the same pull request, RED before the implementation moves it green, per **Test discipline**.
4. Update dev guide and handler guide summaries to reflect the amended contract.

Removing a row, narrowing a guarantee, or changing semantics on any cell is a BREAKING change. Adding a new optional axis (e.g. a new server option that selects a new row) is non-breaking as long as defaults preserve existing semantics.

### Change log

| Date | Spec | Summary |
|------|------|---------|
| 2026-05-28 | (initial) | First publication. Consolidates the contract from dev guide, handler guide, spec 010, spec 012. |
| 2026-06-01 | [016](016-automatic-task-recovery/spec.md) | Cross-cutting "Lease eviction (`binding_mismatch`)" note added. Eviction is orthogonal to the response-stream matrix (rows 1-4) and applies uniformly to every store-write site; caller-observable outcomes preserve Invariant 1 (identical shape to live-elsewhere / not-active). No matrix row added; no row semantics changed. |
