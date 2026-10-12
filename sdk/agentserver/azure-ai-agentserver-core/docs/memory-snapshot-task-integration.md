# Design: resilient tasks with memory snapshots

**Status:** draft implementation and design review.

This design builds on the snapshot lifecycle hooks in
[Python SDK PR #49217](https://github.com/Azure/azure-sdk-for-python/pull/49217).
It separates process-side task definitions from session-bound TaskManager
construction and startup. Application startup task submissions remain an open
design question; neither a new callback nor automatic replay is implemented.

## Problem

A golden memory snapshot is an initialized agent-version template. It is not
a checkpoint of the most recent session. Process memory and filesystem state
at capture are retained, but subsequent session mutations and external service
state are not incorporated into that template.

The current host constructs TaskManager during ASGI startup. That same startup
can run during golden capture before a real session has been assigned.
TaskManager selects a provider, derives lease-owner identity, creates worker
identity, and starts recovery. Capturing it at that point couples a reusable
process template to session execution.

Updating environment variables and shared configuration after restoration does
not, by itself, reconstruct all session-bound objects or safely reset workers.
Instead, this change retains task definitions during process preparation and
constructs the requested runtime during real-session activation.

## Scope

Included:

- Python Core task runtime activation through ordinary cold startup or the
  existing `after-restore` hook.
- Process-side task definitions and existing Responses task registration.
- Immediate recovery, initialization retry checkpoints, runtime ownership,
  and shutdown/rollback handling.
- A distinction between intentional resilience opt-out and an enabled runtime
  that has not yet initialized.

Not included:

- New application session-start callbacks or captured startup launch intentions.
- A general framework for rebuilding every protocol/client object.
- Changes to hosted task storage, stream replay storage, lease timing,
  task execution, or recovery filtering/fencing policy.
- A guarantee that arbitrary sockets, cached credentials, or application
  dependencies are snapshot-safe.
- Platform recovery implementation, .NET support, or public release rollout.

## Two independent controls

Platform memory-snapshot opt-in is a property of the hosted agent definition.
[REST-spec PR #46759](https://github.com/Azure/azure-rest-api-specs/pull/46759)
proposes:

```json
{
  "definition": {
    "kind": "hosted",
    "enable_memory_snapshot": true
  }
}
```

That field requests platform capture/materialization. It is independent of the
SDK startup variable below; setting the variable alone does not enable
platform snapshots. The REST proposal is subscription/region gated, defaults
to false, and introduces no extra feature header.

`FOUNDRY_MEMORY_SNAPSHOT_ENABLED` selects the SDK's ordinary startup trigger:

| Value | Enabled task subsystem at ordinary startup |
|---|---|
| Absent | Defer construction/startup; capture has no real-session runtime |
| `true` | Defer construction/startup; activate through after-restore |
| `false` | Activate during ordinary cold/local session initialization |

Application resilience enablement is still required through
`set_resilient_tasks_enabled(True)` or Responses resilience options. A
declaration alone does not enable the subsystem.

Present values must be case-insensitive `true` or `false`; surrounding
whitespace is accepted. Empty/malformed values fail explicitly. Missing is not
treated as false. The flag chooses an initialization trigger, not permission
to execute or renew leases after activation.

After-restore is itself the explicit activation signal. Activation does not
require a new flag override or changing the flag to false.

### Compatibility and rollout requirement

Non-snapshot/local launchers must explicitly supply false. An older launcher
with no value no longer automatically starts requested tasks. This is an
intentional draft contract, not a transparent backward-compatible default.
Launcher/platform provisioning and package rollout must be reviewed before
release. Do not silently fall back to eager startup to hide missing wiring.

## Lifecycle

### Process preparation and capture

```text
imports and session-independent warmup
  -> construct protocol routes/orchestrators
  -> register task definitions and options
  -> preserve resilience intent
  -> ordinary startup defers TaskManager
  -> before-snapshot
  -> capture warmed process
```

The existing `_REGISTERED_DESCRIPTORS` contains definitions, not submitted
task records or launch intentions. Manager construction is deferred, but
definition registration is not. Responses can register its one-shot and
multi-turn task functions before a manager exists.

Capture process readiness does not mean that session-bound tasks are active.
No application task should acquire a lease or execute in the capture sandbox.

### Ordinary cold startup

```text
explicit false + application resilience opt-in
  -> construct manager with current session configuration
  -> install registered callbacks
  -> existing initial recovery
  -> one periodic recovery scanner
  -> admit normal requests
```

Local development uses this path without platform snapshots.

### Snapshot materialization

```text
apply real-session environment/configuration
  -> protected SDK restore extension
  -> optional author dependency-rebinding callback
  -> construct/bind requested TaskManager
  -> load existing registered definitions
  -> initial recovery: detect, reclaim, dispatch immediately
  -> ensure one periodic scanner
  -> commit successful restore
  -> platform admits new requests
```

Recovered tasks may execute and renew leases while after-restore is still
running. There is no barrier waiting for the hook response or platform
acknowledgment, and the hook does not wait for LRA completion.

Dependencies needed by recovered callbacks must be prepared before manager
startup. This design keeps the existing author restore callback before task
activation; it is not a post-task-start callback.

## Initialization phases and retry

TaskManager retains private phase state:

| Phase | Completion means |
|---|---|
| Construct/bind | A manager exists for the bound session |
| Register | Captured task definitions/options are installed |
| Recovery | Existing best-effort initial scan attempt completed |
| Periodic | One scanner is present and running |
| Ready | Required initialization completed |

A completed phase stores the incoming `restore_id`, and is stamped only after
accepted completion. Cold startup uses private instance-once semantics without
inventing a platform restore event.

- The hook lifecycle lock and completed-restore guard serialize/deduplicate
  incoming hooks.
- TaskManager's startup lock independently prevents concurrent startup from
  duplicating workers.
- A same-ID retry reuses valid completed phases and retries unfinished steps.
- Recovery is reconsidered for a different restore ID without creating an
  additional valid manager/scanner for the same binding.
- A stopped scanner is not silently counted as readiness. A scanner exception
  is surfaced; invalid periodic/readiness markers are cleared.
- Shutdown invalidates phase state. A stopped manager cannot restart.
- A host refuses a manager owned by another host or a conflicting session
  binding rather than replacing it silently.

This is not a general retained-memory reconciliation framework. Changes to
session-incarnation binding require explicit lifecycle treatment rather than
blind reuse or duplicate initialization.

## Failure, cancellation, and runtime ownership

The host owns the current manager, not a lifespan-local variable captured before
restore. A manager created after lifespan entry must still be stopped when that
host exits.

Protocol shutdown signals handlers before manager draining. Manager cleanup
cancels and awaits owned execution, renewal, and watchdog tasks, invalidates
initialization state, and clears only its own singleton.

Completed inactive phase resources can survive a failed restore attempt and
be reused after the same session is rebound. However, rollback cannot revert
shared configuration while recovered workers continue using an incompatible
binding. In that case the host first stops the owned runtime, waits for cleanup,
and invalidates its state before rolling back environment/configuration.

Cleanup is shielded against cancellation of the hook caller. A cleanup failure
is reported rather than claiming rollback safely completed.

A client HTTP timeout/disconnect is not necessarily Python coroutine
cancellation. In the tested server configuration, work continues and a retry
waits behind the lifecycle lock. Explicit cancellation, shutdown, and process
loss remain distinct events.

## Recovery policy remains unchanged

Keep the existing recovery layers: initial scan, periodic scan, and inline
exact-task-ID reclaim through the task APIs.

Initial LIST failure is logged and initialization continues under current
best-effort semantics. Per-record failures do not fail the complete scan.
Periodic recovery can retry later. Essential construction/uncaught startup
failures still fail activation explicitly.

Do not change task scope/source filters, lease ownership, ETag fencing, or
normal heartbeat timing. The snapshot flag/lifecycle lock is not consulted by
running execution or renewal loops.

Recovery re-enters a handler using externally saved task input and application
checkpoints. It does not resume the later Python frames of the crashed session.
The definition registry does not replace input persistence.

## Responses integration

Keep eager registration of `responses_resilient_one_shot` and
`responses_resilient_multi_turn`. Definitions are available before recovery
without rebuilding the complete Responses protocol graph.

`TaskManagerNotInitialized` no longer necessarily means intentional opt-out.
When resilience is enabled, Responses propagates that initialization error
through existing error handling instead of silently running non-durably.
When resilience is intentionally disabled, the existing in-process fallback
remains.

No new HTTP 503 contract is introduced. Normal platform request admission
occurs after successful restore.

## Q3: customer task submissions during startup

Registering decorated definitions is supported. Explicitly calling `.start()`
or `.run()` before the deferred manager exists is not automatically queued,
and restore does not rerun already completed `__main__`/lifespan statements.

Two possible follow-ups remain unselected:

### Option A: explicit session-start callback

Add a narrow callback invoked after TaskManager initialization on cold start
and restoration, never during capture.

Illustrative API, **not implemented**:

```python
@app.on_session_started
async def launch_session_work(context):
    await bootstrap.start(input={"session_id": context.session_id})
```

The callback reference is registered during process preparation and preserved
in the snapshot. It computes inputs from the real session and uses normal
task submission semantics. Customers must move launch statements into it.
It must be distinct from the existing pre-activation dependency callback.

### Option B: startup launch-intent registry

During an explicitly identified capture-startup phase, record each supported
non-blocking submission with task identity/options, frozen input, call identity
policy, and ordering. Create no task record or lease during capture.

After task initialization/recovery, reconcile those intentions and submit
appropriate work through the normal task path. This needs an honest deferred
handle/receipt contract, not `None` or a falsely running task.

It cannot transparently complete startup that requires:

```python
value = await prepare.run(input=...)
await bootstrap.start(input=value)
```

The result does not exist during capture. Waiting for it can prevent readiness
and capture. The same issue applies to `.start()` followed by `.result()`.
Inputs tied to session identity/live resources need restore-time rebinding.
An unawaited coroutine has not submitted anything to record.

### Shared duplicate-launch concern

Both options must specify per-materialization versus once-per-logical-session
behavior. Every golden clone begins with the original callback/intent state.
In-memory restore checkpoints do not establish cross-clone once-only effects.
Stable task IDs help, but one-shot records are deleted at terminal exit.
Once-per-session guarantees need durable reconciliation or application
idempotency; neither option provides generic exactly-once execution.

Neither option is implemented/tested in this change.

## Persistence boundaries and limitations

Hosted task and response stores remain external. Application checkpoint
storage remains application-owned. Default local stream replay and arbitrary
post-capture local files are not guaranteed to survive golden replacement.

This task lifecycle change does not declare every captured provider/client
safe. Applications still need appropriate dependency rebinding. Existing
typed-input behavior is not broadened or redesigned.

## Validation and outstanding qualification

| Scenario | Evidence / status |
|---|---|
| Absent/true deferral; false cold startup; opt-out; malformed input | Targeted startup tests |
| Definitions before activation; restored binding | Core/Responses activation tests |
| Same-ID concurrent/duplicate hooks | Real ASGI tests; one runtime/scanner |
| Partial initialization/scanner failure | Completed-phase reuse tests |
| Actual cancellation and environment rollback | Worker quiescence and retry tests |
| Client timeout/retry | Loopback HTTP test |
| Recovery LIST failure | Best-effort completion and periodic retry test |
| Recovery/lease filtering/fencing | Existing targeted task suites |
| Execution/renewal during hook | Real recovered task/heartbeat integration test |
| Cold and initial golden LRA activation | Controlled hosted sample, actual external lease renewal |
| Hard crash after checkpoints 1 and 2 | Controlled hosted recovery; no new invocation during orphan interval |
| Independent sessions/concurrent tasks | Controlled hosted owner/worker/lease observations |
| Cancellation | Controlled hosted terminal cancellation, no task resurrection during observation |
| Natural idle/resume | Controlled hosted test: 120-second policy; after six quiet minutes, same session/capture with a new restore ID and worker, followed by renewed leases and completion |
| Customer startup submissions (Q3) | Deferred; options above only |

The controlled hosted test runs the existing resilient streaming sample.
A test-only wrapper exits the process with code 137 after a committed
checkpoint; it does not change SDK recovery or lease timing. An external
one-shot marker prevents repeated crash injection. A capture-only heap marker
is retained through restoration, together with a new restore ID/worker and
incremented fencing generation, to distinguish replacement from cold import.

For idle/resume, management continued reporting the logical session as active.
The test closed its log reader before the quiet interval and invoked the same
session only once afterwards. The new restore ID/worker, retained capture heap
marker, and subsequent lease-backed completion establish restoration; elapsed
quiet time or management status alone would not. This does not establish the
exact suspension timestamp or a guarantee of suspension at exactly 120 seconds.

These observations do not replace CI, public rollout qualification, or an
unobserved scenario.
