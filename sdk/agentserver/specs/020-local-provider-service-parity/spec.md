# Spec 020 — Local-provider ↔ service parity, and the developer-surface fallout

**Date:** 2026-06-11
**Status:** Draft
**Branch:** `feature/agentserver-durable-tasks` (local commits only)
**Scope:** `azure-ai-agentserver-core`'s durable-task primitive — the local file-backed task provider, the hosted HTTP task provider's response/error mapping, and the developer-facing public surface that sits on top of both.
**Authoritative service source:** `~/code/vienna/src/azureml-api/src/AgentExtensions/Services/Tasks/WorkspaceTaskService.cs` and `Contracts/Models/` at master HEAD (post PR 2127599 attachments, 2135250 distinct conflict codes, 2139242 PATCH latency fix, 2122040 opaque pagination, 2142642 omit-attachment-values).

---

## 1. Why

Today the framework runs against two task-storage backings:

- **Hosted** (`HostedTaskProvider`) — thin HTTP client that talks to the Vienna-side `WorkspaceTaskService`. The behavior the developer observes is defined by the service.
- **Local** (`LocalFileTaskProvider`) — file-backed, used in dev / local-mode / tests when there's no hosted endpoint. The behavior should be **observationally indistinguishable** from hosted so a workflow that succeeds locally does not silently fail (or, worse, succeed differently) when deployed.

A diff against the post-pull service surface shows ~40 places where local quietly accepts requests the service would reject, omits a field the service emits, or branches differently from the service's state machine. Most of them are validation gaps (no payload-size cap, no tag-key regex, etc.) that don't matter until you hit them in prod. A few are real semantic drifts (delete-without-force returns 400 not 409; conflict codes are now distinct strings; pagination uses opaque cursors not task ids).

At the same time, the service's API surface has *moved* — distinct error codes, opaque continuation tokens, a `lease_ownership_changed` race resolution — and **none of those API details should leak into the developer's surface**. The developer calls `task.run()` / `task.start()` / `ctx.suspend()`; they do not know `task_immutable` is the HTTP code on the wire, nor should they have to. The exception they catch should be a stable Python type whose name reflects intent, not the service code string.

This spec covers the three pieces of work that fall out of that:

1. **Parity** — bring local up to the service's validation, state machine, lease semantics, attachments behavior, and list-filter surface.
2. **Hosted-side adaptation** — translate the service's newly-distinct error codes and opaque cursors into the framework's stable Python exception types and pagination idiom. Nothing the developer catches changes.
3. **Developer-surface review** — sweep what we currently expose to confirm none of the API-level vocabulary (HTTP codes, etag strings, cursor format, "if-match", "lease_owner") has leaked above the provider boundary.

---

## 2. Goals

- **G1.** A developer running their `@task` handler under `LocalFileTaskProvider` observes the same exceptions, the same accept/reject decisions, the same field shapes, and the same state transitions as they would running against the hosted service. "Works locally, fails in service" stops happening for any of the surface this spec touches.
- **G2.** The framework keeps its existing developer-visible Python exception hierarchy unchanged (`TaskConflictError`, `TaskFailed`, `TaskCancelled`, `TaskNotFound`, `TaskPreconditionFailed`, `SteeringQueueFull`, `LastInputIdPreconditionFailed`). The service's distinct HTTP codes (`task_immutable`, `lease_held_by_another`, …) are absorbed by the framework's internal classifier and translated to the existing public types (or trigger transparent retry). **No new public exception exports.**
- **G3.** The developer-facing public API surface (`@task`, `Task.run`, `Task.start`, `Task.get`, `TaskContext`, `TaskResult`, `TaskRun`, `TaskSnapshot`, the documented exceptions) carries **no service-API leakage** — no HTTP status codes, no etag strings, no "lease_owner" terminology in error messages, no continuation-token shape exposed for pagination.
- **G4.** The hosted provider's response mapping and the local provider's raise sites use the **same** internal validation/exception module so they cannot drift again.

## 3. Non-goals

- Adding new service features. We don't ship new hosted surface from this spec; we only adapt to what the service already exposes.
- Workspace partitioning, Cosmos etag format, Cosmos race detection, search-index updates, lease keep-alive notifier, S2S session binding, stale-task scanner, sandbox keep-alive — all hosted-only infra that has no local counterpart and isn't observable through `@task`.
- Changing `payload`'s 1 MB inline cap or `attachments`' 2 MB-per-entry × 20-entry cap. Those already match the service.
- Reworking the streaming primitive (`streams` registry) — out of scope; spec 019 owns that.
- Adding a new public surface for end-developers around tasks. The spec deliberately leaves the developer-facing API where it is.

---

## 4. Three workstreams

The work splits cleanly into three workstreams. Each is independently shippable; together they close the parity loop.

### Workstream A — Local-provider parity (the bulk of the work)

Bring `LocalFileTaskProvider` up to the service's validation + state machine + lease semantics. The developer running locally sees the same accept/reject behavior as if they were running against the hosted service.

Concrete changes (numbered for tracking; each MUST land with a paired test that fails first):

**A. Validation** (mirror service-side input checks)
- A1. Task id must match `^[a-zA-Z0-9_-]{1,128}$`.
- A2. `agent_name`, `session_id`, `title` are required on create.
- A3. Tag keys must match `^[a-zA-Z0-9_.\-]{1,64}$`.
- A4. Tag values ≤ 256 chars.
- A5. At most 16 tag entries.
- A6. Payload JSON ≤ 1 MB.
- A7. Error JSON ≤ 64 KB.
- A8. Source JSON ≤ 4 KB.
- A9. Suspension reason ≤ 256 chars.
- A10. When `source` is provided, `source.type` is required.
- A11. Status `"failed"` is rejected (failures are represented as `completed` + non-null `error`).
- A12. Status `"done"` normalizes to `"completed"` on read and in list filters (legacy alias).

**B. State machine**
- B1. Status transitions follow the service matrix:
  - `pending` → `in_progress`, `completed`
  - `in_progress` → `pending`, `suspended`, `completed`, `in_progress` (lease renewal)
  - `suspended` → `pending`, `in_progress`, `completed`, `suspended`
  - `completed` → terminal, no outgoing transitions
- B2. Terminal-status tasks are immutable — PATCH is rejected (except the no-op `completed → completed` with no other fields changed).
- B3. The immutable fields `title`, `description`, `id`, `agent_name`, `session_id`, `source` are rejected on PATCH.
- B4. `suspension_reason` is only allowed when the target status is `suspended`.
- B5. DELETE on a non-terminal task without `force=true` is rejected with a `400 InvalidRequest` (note: this changed from 409 in service PR 2135250).
- B6. DELETE honors `If-Match` when supplied.
- B7. Error PATCH requires `message` and `type` as non-empty strings.
- B8. Error PATCH defaults `code` to `"error"` when missing.

**C. Lease semantics**
- C1. `lease_duration_seconds` must be `0` (force-expire) or `10..3600`.
- C2. `lease_owner`, `lease_instance_id`, `lease_duration_seconds` are all-or-nothing — supplying any without all three is rejected.
- C3. Different-owner takeover when the existing lease is not yet expired is rejected (`lease_held_by_another`).
- C4. `in_progress → pending` requires the lease params and the existing lease's `owner` + `instance_id` to match (`EnsureLeaseMatches`).
- C5. Lease renewal (no status change) is only allowed when the current status is `in_progress`.
- C6. Force-expire (`lease_duration_seconds=0`) cannot be combined with a status transition.
- C7. Force-expire requires the caller's lease params to match the current lease's owner+instance UNLESS the lease is already expired.
- C8. On different-owner takeover when the prior lease was expired, `expiry_count` increments.
- C9. `started_at` is **immutable** after the first `in_progress` transition. Lease re-acquisition (different-owner takeover OR same-owner restart after expiry), recovery scanner takeover, and suspend/resume cycles MUST all preserve the original `started_at` value.
- C10. Lease has `heartbeat_at` field, set on every lease write (today our `LeaseInfo` is missing it).

**D. Attachments**
- D1. Attachment keys must match `^[a-zA-Z0-9_.\-]{1,64}$`; empty/whitespace keys rejected. (Per-key value 2 MB and total count 20 are already enforced.)
- D2. Per-key `null` in `TaskPatchRequest.attachments` deletes that key — already supported ✅.
- D3. **Clear-all gesture.** Service supports top-level `attachments: null` → wipe all attachments. Local provider must support the same semantic so a future framework caller (or direct typed-API user) can use it. Add a `clear_attachments: bool = False` flag on `TaskPatchRequest`: when true, hosted provider serializes `attachments: null` on the wire; local provider clears the file's attachments dict. When false and `attachments=None` → no change (current semantic). When false and `attachments={...}` → per-key patch (current semantic).
- D4. `list()` gains an `omit_attachment_values` option — when true, returned tasks carry attachment keys with `None` values (perf optimization for paging through many tasks without paying for full value reads).
- D5. DELETE on a task removes all attachments along with the task. Local already does this trivially (the attachments dict lives in the same JSON file as the task record, so unlinking the file removes both). Add a regression test for clarity.

**E. Status-transition side-effects**
- E1. `→ pending` clears the lease AND clears `suspension_reason`.
- E2. `→ in_progress` sets `started_at` if null AND clears `suspension_reason` AND clears `completed_at`.
- E3. `→ completed` clears the lease AND clears `suspension_reason` AND sets `completed_at` if null.
- E4. `→ suspended` clears the lease AND sets `suspension_reason` AND clears `completed_at`.

**F. PATCH semantics**
- F1. Payload PATCH: if the patch value is a JSON object, shallow-merge into the current payload; if it's any other JSON type (array, string, number, null-treated-as-no-op), full-replace. (Today we always assume dict and would `TypeError` on non-object.)

**G. List-filter parity** (the `list()` operation is internal-only per Spec 015 Phase 3 — `Task._list` is underscore-prefixed and not in `__init__.py` exports; consumers go through `manager.list_tasks(fn_name=...)`. Per goal G3 (no service vocabulary leaking to developers), filter parity here is purely for the framework's internal callers and for hosted/local consistency, not for public API additions.)
- G1. New filter: `has_error`.
- G2. New filter: `lease_expired`.
- G3. Pagination: `after` (cursor — plain `task_id` for local provider, since local has no Cosmos continuation-token concept), `limit` (default 20, max 100). Hosted provider round-trips the service's opaque token (up to 4096 chars) transparently. Internal callers treat the cursor as opaque regardless of provider.
- G4. `order` accepts `"asc"` or `"desc"`, by `created_at`.
- G5. `before` is rejected with a 400-equivalent (cursor pagination forward-only, matching service).
- G6. The status filter normalizes `"done"` → `"completed"` (matches A12).
- G7. `agent_name` and `session_id` are optional (today both are required on local; service makes them optional).

### Workstream B — Hosted-side adaptation (translating new service responses)

The service has moved underneath us. Two changes the hosted provider must absorb without leaking them to the developer:

- **B-Hosted-1. Distinct conflict codes — internal-only discriminator.** The service used to return generic `conflict` for any 409. It now returns distinct codes per cause:
  - `task_immutable` (409) — PATCH on terminal task
  - `invalid_state_transition` (409) — bad state transition
  - `lease_held_by_another` (409) — different owner holds active lease
  - `task_already_exists` (409) — duplicate id on create
  - `lease_ownership_changed` (409) — Cosmos write race, lease was stolen
  - `etag_mismatch` (412) — If-Match precondition failure (renamed from `precondition_failed`)

  **The framework needs to discriminate** because each code maps to a different recovery action (e.g. `etag_mismatch` → retry with re-read; `task_immutable` → propagate to caller as `TaskConflictError(current_status="completed")`; `lease_held_by_another` → propagate as `TaskConflictError(current_status="in_progress")`; `invalid_state_transition` → framework bug, log and raise). **None of these become developer-visible types.** The framework absorbs them internally and produces the existing public `TaskConflictError(current_status=...)` shape (or, for `etag_mismatch`, transparently retries — the developer never sees it).

  Concretely:
  - Add a private internal exception with a `code` field (or a small set of private subclasses inside `_exceptions_internal.py`) that the response-classifier raises.
  - The framework's lifecycle / retry code catches the internal type, branches on `code`, and either retries (etag/race), translates to the existing public `TaskConflictError(current_status=...)`, or — for `invalid_state_transition` — logs a framework-bug warning and raises a generic `RuntimeError` (because the developer doesn't pick transitions, the framework does).
  - **Zero new exports from `azure.ai.agentserver.core.durable`.** Existing `except TaskConflictError:` callers keep working unchanged.

- **B-Hosted-2. Opaque continuation tokens.** The service's list response now returns an opaque cursor (`LastId = continuation token`, up to 4096 chars), not the previous "last task id" string. The hosted provider must round-trip it transparently — pass `after=<cursor>` on the next page request without parsing it. Local mints its own opaque cursor for symmetry. If `Task.list()` is publicly exposed, the developer sees a `next_page_token` (opaque string) that they pass back on the next call. No new exception types involved.

Neither change should produce a single line of developer-visible API change. The framework's public types stay where they are.

### Workstream C — Developer-surface review

A focused sweep of the public surface to confirm no service-API vocabulary leaks above the provider boundary. The developer does not know the task-API exists; their mental model is `@task` decorator + `TaskContext` + `Task.run/start/get` + a small set of named exceptions.

The review looks at five places:

- **C1. Exception names.** The new service codes (`task_immutable`, `lease_held_by_another`, etc.) do NOT become developer-visible Python types. They are internal discriminators only (see Workstream B-Hosted-1). The developer keeps catching the exact same types they catch today: `TaskConflictError` (with `.current_status`), `TaskFailed`, `TaskCancelled`, `TaskNotFound`, `TaskPreconditionFailed`, `SteeringQueueFull`, `LastInputIdPreconditionFailed`. **Zero new public exports.** The audit confirms no service-code string appears in `azure/ai/agentserver/core/durable/__init__.py`, `_exceptions.py`, or any docstring.
- **C2. Exception messages.** Today some raise sites embed service-shaped phrases like "etag mismatch" or "lease_owner mismatch". Rewrite in framework vocabulary ("the task has been modified by another writer; retry"; "this task is being processed by another worker"). Lease-owner identity is an implementation detail of how the framework coordinates work — the developer doesn't manage leases.
- **C3. Pagination shape.** `Task._list()` is **internal-only** per Spec 015 Phase 3 (underscore-prefixed; not in `__init__.py` exports). No developer-visible pagination surface to design. The framework's internal callers see the cursor string and treat it as opaque. Hosted provider round-trips the service's opaque continuation token; local provider uses plain `task_id`. Confirmed: no public-surface change needed.
- **C4. `TaskSnapshot` fields.** Today `TaskSnapshot` (spec 019 work) deliberately excludes framework-internal storage details (lease, etag, raw payload, raw attachments, source, tags). Confirm post-spec-020 that none of the new fields we added on the service side (e.g. `heartbeat_at` on lease) leak into the snapshot. They shouldn't — `lease` is already excluded — but worth a one-line audit per added field.
- **C5. The developer guide and CHANGELOG.** No changes in `durable-task-guide.md` should reference "task API", "WorkspaceTaskService", HTTP codes, etag strings, or any other service vocabulary. The CHANGELOG entry for this spec describes what changed in developer terms (e.g. "stricter validation in local mode to match production behavior"; "distinct conflict types via subclasses of TaskConflictError") and does NOT enumerate service codes.

---

## 5. Decisions (all signed off)

All design decisions are now resolved:

- **Internal discriminator design** (Workstream B-Hosted-1) → **Option A**: a single private internal exception (e.g. `_HostedConflict(_code: str, status_code: int)`) raised by the response-classifier. The framework's lifecycle code catches it, matches on `_code`, then translates into the right *public* exception (`TaskConflictError(current_status=...)`, `TaskPreconditionFailed`, etc.) or retries silently. **Zero new public exports.**
- **Pagination cursor format** → **plain `task_id`** for the local file provider. Hosted provider transparently round-trips whatever opaque token the service returns. Consumers see `next_page_token` (or similar) and treat it as opaque regardless of which provider is underneath.
- **"Clear all attachments" gesture** → **support it** for parity with service. Add `clear_attachments: bool = False` flag on `TaskPatchRequest` (D3 in Workstream A above). Hosted provider serializes it as `attachments: null` on the wire; local provider clears the file's attachments dict.

---

## 6. Test plan (per Principle VII / XII §4)

- **Local-provider tests** (Workstream A): each numbered item (A1–A12, B1–B8, C1–C10, D1–D3, E1–E4, F1, G1–G7) gets a paired test in the existing test files (`test_local_provider.py`, `test_lifecycle.py`, `test_etag_cas.py`, `test_attachments_*.py`, `test_errors_public_surface.py`). New tests land RED first. Per non-duplication, extend existing files rather than create parallel.
- **Hosted-provider tests** (Workstream B): extend `test_hosted_provider_transport.py` with mocked HTTP responses carrying each of the 6 service codes; assert the framework **internally** dispatches correctly — i.e. retryable codes (`etag_mismatch`, `lease_ownership_changed`) trigger retry, conflict codes (`task_immutable`, `lease_held_by_another`, `task_already_exists`) surface as `TaskConflictError(current_status=...)` with the right status, and `invalid_state_transition` produces a framework-bug error. Extend pagination tests to cover opaque cursor round-trip.
- **Public-surface tests** (Workstream C): extend `test_public_api_surface.py` / `test_errors_public_surface.py` to assert that **no new exception names are exported** from `azure.ai.agentserver.core.durable` as a result of this spec (negative assertion). The existing public exception set is the same before and after. Snapshot-field audit lives in `test_task_get_api.py`.

## 7. Sequence

1. Get sign-off on the three §5 decisions.
2. Land Workstream A first (largest scope, no external dependency).
3. Land Workstream B (hosted-side mapping uses the same internal exception module Workstream A produces).
4. Land Workstream C as a final review pass + small docstring/message rewrites + CHANGELOG.
5. Final `code-review` sub-agent pass scoped to "is the developer surface free of service-API vocabulary?".

Estimated effort: ~8–10 hours for A + ~2 hours for B + ~1 hour for C ≈ ~11–13 hours total.

## 8. Out-of-scope items recorded for traceability

| # | Item | Why out |
|---|---|---|
| O1 | Workspace partitioning | Hosted-infra concern; not observable through `@task`. |
| O2 | Cosmos etag format | Etag is opaque to consumers; equality is what matters. |
| O3 | Search index updates | Hosted-internal observability. |
| O4 | Service's `UpsertInternalAsync` / `UpdateStatusInternalAsync` | Hosted-internal callers (routine dispatch). |
| O5 | Lease keep-alive notifier (`ITaskLeaseKeepAliveNotifier`) | Hosted-only sandbox concern. |
| O6 | Attachment hash/size metadata in stored document | Hosted-storage concern for blob-backed offload; local stores values inline. |
| O7 | `ITaskAttachmentStore` (blob store) | Hosted uses external store; local uses inline storage. Functionally equivalent for the developer. |
| O8 | `IAgentSessionBindingValidationClient` + lease-refresh fence | Hosted-only S2S validation. |
| O9 | `IStaleTaskScanner` + `StaleTaskRecoveryService` (Cosmos nanny) | Hosted-only orphan detection. |
| O10 | `IHostedAgentSandboxKeepAliveController` | Hosted-only sandbox lifecycle. |
| O11 | `IHostedAgentSessionRecoveryController` | Hosted-only session recovery. |
| O12 | `lease_ownership_changed` race detection | Cosmos concurrency race; single-process local has no concurrent writers. |
| O13 | Workstream B's response-mapping for `lease_ownership_changed` | If/when hosted observes this code, the framework maps it to `LeaseHeldByAnother` (same parent, same observable behavior — the lease is held by someone else). |

## 9. Open questions

*(none — all decisions resolved during spec review)*
