# Design: resilient tasks with memory snapshots

**Status:** draft implementation and design review.

This design builds on the snapshot lifecycle hooks in
[Python SDK PR #49217](https://github.com/Azure/azure-sdk-for-python/pull/49217).
It separates process-side task definitions from session-bound TaskManager
construction and startup. Applications submit startup work from the existing
`after_restore_handler`: the requested manager is prepared before the handler,
and automatic recovery starts after the handler finishes rebuilding dependencies.
No new public callback or capture-time launch registry is required.

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
- Calling decorated task methods from the existing application restore handler.
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
| Absent | Same as `false`: activate during ordinary cold/local initialization |
| `true` | Defer construction/startup; activate through after-restore |
| `false` | Activate during ordinary cold/local session initialization |

Application resilience enablement is still required through
`set_resilient_tasks_enabled(True)` or Responses resilience options. A
declaration alone does not enable the subsystem.

| Resilient tasks enabled | Environment value | Ordinary startup | After-restore |
|---|---|---|---|
| No | absent, `false`, or `true` | No task subsystem | No task subsystem |
| Yes | absent or `false` | Activate immediately | Activate/retain the same session runtime |
| Yes | `true` | Defer activation | Prepare before the application callback; recover after it |

Present values must be case-insensitive `true` or `false`; surrounding
whitespace is accepted. Empty/malformed values fail explicitly. Missing is
treated as false. The flag chooses an initialization trigger, not permission
to execute or renew leases after activation.

After-restore is itself the explicit activation signal. Activation does not
require a new flag override or changing the flag to false.

### Compatibility and rollout requirement

Non-snapshot/local launchers need no new environment variable: absent preserves
ordinary startup. Every temporary capture producer must supply `true`, including
direct capture and queued version/Managed Harness package warm templates.
The captured value survives restoration; no restore override is required, and
the hook explicitly activates tasks while the value remains `true`.

An unmarked capture would start enabled tasks immediately and could capture
session-bound runtime state. The before-snapshot callback is not a substitute
for correct startup signaling. Coordinate service and SDK rollout: the earlier
prototype treated absence as deferred, so removing its cold-boot `false` wiring
requires this SDK update too. Prior registry-prototype hosted results below do
not qualify the revised signal contract.

## Lifecycle

### Process preparation and capture

```text
imports and session-independent warmup
  -> construct protocol routes/orchestrators
  -> register task definitions and options
  -> preserve resilience intent
  -> capture environment explicitly sets the snapshot variable to true
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
absent or false + application resilience opt-in
  -> construct manager with current session configuration
  -> install registered callbacks
  -> existing initial recovery
  -> one periodic recovery scanner
  -> admit normal requests
```

Local development uses this path without platform snapshots.
Sequential cold-start lifespans on the same host reset the task shutdown gate
and create a fresh enabled runtime. Snapshot-mode startup still waits for
session activation; disabled tasks remain disabled.

### Snapshot materialization

```text
apply real-session environment/configuration
  -> protected SDK restore extension
  -> construct/bind requested TaskManager
  -> load existing registered definitions
  -> optional application after_restore_handler:
       rebuild application dependencies
       submit decorated startup tasks using normal .start()/.run() APIs
  -> initial recovery: detect, reclaim, dispatch immediately
  -> ensure one periodic scanner
  -> commit successful restore
  -> platform admits new requests
```

Submitted and recovered tasks may execute and renew leases while after-restore is still
running. There is no barrier waiting for the hook response or platform
acknowledgment, and the hook does not wait for LRA completion.

The manager has a provider, real session/worker identity and registered task
definitions when the application handler runs. It has not yet started its
automatic recovery scan or periodic scanner. Applications rebuild dependencies
before submitting their own tasks. Recovery waits until the handler returns,
so previously persisted work cannot race ahead of that preparation.

This ordering applies to a newly prepared runtime. An already-active cold or
retained runtime/scanner is not paused by this change; live idle-snapshot
quiescence is a separate lifecycle requirement.

## Initialization phases and retry

TaskManager retains private phase state:

| Phase | Completion means |
|---|---|
| Construct/bind | A manager exists for the bound session, before the app handler |
| Register | Captured definitions/options are installed; task submission is available |
| Recovery | The application handler returned; best-effort initial scan completed |
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
- A completed restore ID does not replay the application handler. If host
  shutdown disposed the runtime, the same payload re-establishes it before
  acknowledging success; delayed older IDs use the latest committed binding.
- Recovery is reconsidered for a different restore ID without creating an
  additional valid manager/scanner for the same binding.
- A stopped scanner is not silently counted as readiness. A scanner exception
  is surfaced; invalid periodic/readiness markers are cleared.
- Shutdown invalidates phase state. A stopped manager cannot restart.
- A host refuses a manager owned by another host or a conflicting session
  binding rather than replacing it silently.
- An inactive manager whose construction-time provider configuration no longer
  matches hydrated settings is disposed and rebuilt. Provider changes while
  workers are live fail explicitly instead of sending work to a stale endpoint.

This is not a general retained-memory reconciliation framework. Changes to
session-incarnation binding require explicit lifecycle treatment rather than
blind reuse or duplicate initialization.

## Failure, cancellation, and runtime ownership

The host owns the current manager, not a lifespan-local variable captured before
restore. A manager created after lifespan entry must still be stopped when that
host exits.

Protocol shutdown signals handlers before manager draining. Manager cleanup
cancels owned execution, renewal, and watchdog tasks, invalidates
initialization state, and clears only its own singleton. Before the host rolls
back session configuration, it asks cleanup to also wait for those tasks to
finish, so cancelled handlers complete under the binding they started with.
This rollback-only cleanup preserves unfinished task records and saved inputs.
It stops workers before expiring their leases, allowing a restore retry to
recover the original task rather than treating interruption as user cancellation.
Ordinary shutdown and explicit task cancellation keep their existing behavior.
The manager owns execution, renewal, scanner and watchdog workers until they
finish, independently of active task records. Rollback joins those workers,
including renewals whose handlers completed before cleanup began.
No new steering turn executes during cleanup. If the current turn finishes
normally, the next queued input is durably staged as `in_progress` for recovery,
without invoking its handler; the next activation resumes that input.
After workers stop, rollback reconciles any suspended steering chain whose
next-input transition was interrupted. Reconciliation uses the same fenced
drain path with an explicit lease claim before that lease is expired for retry.
If reconciliation fails, cleanup propagates the error rather than rolling
configuration back while queued work is stranded.
The stopped manager retains its reconciliation handles until cleanup succeeds.
A later hook first retries that cleanup under the original session binding,
before rehydrating configuration or invoking restore callbacks. Only then is
the stopped manager disposed and a replacement activated. Repeated cleanup
failures remain failures; an already committed input promotion is not repeated.
The host also retains the original environment/configuration rollback snapshots
until cleanup and rollback finish. It restores those values before computing a
retry's environment baseline, so omitted overrides cannot retain a failed value
and repeated overrides cannot replace the captured baseline with that value.
Ordinary host shutdown also finishes any pending rollback preservation rather
than discarding its queued work.
A newly restored manager records
its restore ID before recovery so a same-ID retry cannot rotate lease identity
under retained live workers.

Completed inactive phase resources can survive a failed restore attempt and
be reused after the same session is rebound. However, rollback cannot revert
shared configuration while recovered workers continue using an incompatible
binding. In that case the host first stops the owned runtime, waits for cleanup,
and invalidates its state before rolling back environment/configuration.

Cleanup is shielded against cancellation of the hook caller. A cleanup failure
is reported as the sanitized `after_restore_failed` JSON error rather than
claiming rollback safely completed. Pending cleanup and rollback state remain
owned for a later retry.

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
When resilience is enabled and startup is deferred (the variable is
`true`), Responses propagates that initialization error through existing error
handling instead of silently running non-durably. When resilience is
intentionally disabled, or startup is not deferred (absent/`false`, including in-process
clients whose lifespan never ran), the existing in-process fallback remains.

Deferred-start failures remove the exact caller-scoped execution record before
propagating the error, so an execution that never started is not retained.

No new HTTP 503 contract is introduced. Normal platform request admission
occurs after successful restore.

## Customer startup tasks: selected existing-handler design

Declare `@task` or `@multi_turn_task` methods normally, then submit them from
`@app.after_restore_handler` after rebuilding the dependencies they use:

```python
@app.after_restore_handler
async def initialize_session(context):
    await rebuild_dependencies()
    await startup_work.start(input={"session_id": context.session_id})
```

The callback remains an ordinary async function receiving `AgentSessionContext`;
the submitted decorated method receives its normal `TaskContext`. Task methods
defined inside the handler also register with the prepared live manager.
Neither task declaration nor handler registration submits work during capture.
Calls in capture-time `__main__` are not automatically queued or replayed.

Await `.start()` only for acceptance/its handle. `.run()` also works for bounded
work, but awaiting a long-running result delays the hook response and can exceed
the platform timeout. Put long result-dependent sequences in a launched durable
orchestration instead.

The existing restore lock/completed-ID guard deduplicates concurrent and repeated
successful hooks. On failure, normal ownership/rollback rules preserve unfinished
records and inputs; a retry may execute the callback again. Use task IDs and
`get_active_run()` to reconcile unfinished submissions. A completed one-shot
record may be deleted, so once-per-logical-session behavior also needs an
application-owned durable completion marker. No generic exactly-once guarantee,
automatic task replay, or new receipt type is added.

Opt-out remains authoritative: when resilience is disabled the callback still
runs, but durable task submission retains `TaskManagerNotInitialized`.
Ordinary cold startup remains unchanged and does not manufacture a restore event
or invoke this callback.

## Historical startup alternatives (not selected)

Registering decorated definitions is supported. Explicitly calling `.start()`
or `.run()` before the deferred manager exists is not automatically queued,
and restore does not rerun already completed `__main__`/lifespan statements.

The following earlier alternatives are retained as design history, not the
current implementation. The selected approach above reuses the existing handler
by splitting preparation from recovery. Separate registry-prototype evidence
does not qualify the selected handler implementation.

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

#### Execution order and customer migration

```text
Capture:
  declare decorated functions
  register session-start callback
  warm process without invoking the callback
  capture both function references

Cold startup / restore:
  bind real session and prepare dependencies
  initialize TaskManager and perform existing recovery
  invoke session-start callback
  finish initialization without waiting for LRA completion
```

The task definition stays in imports or main construction. The actual
`.start()` statements move into the callback. An unchanged capture-time
submission still fails; the callback does not intercept it, rerun `__main__`,
or serialize its arguments.

The callback context needs the current session and, for restore, the
materialization ID. Cold initialization has no platform restore ID. Inputs
can therefore be computed from current session identity rather than retaining
capture-time placeholder values.

This historical proposal assumed manager preparation and recovery were
inseparable. The selected existing-handler design instead prepares the manager
before the handler and delays recovery until afterward, removing the need for
that separate callback.

#### Results, failure, and repetition

Await `.start()` only until submission is accepted. A result-dependent
sequence should execute in a launched durable orchestration rather than block
the restore hook on long-running completion.

Successful same-materialization callbacks can be deduplicated by restore ID;
an in-flight retry waits for the lifecycle lock. Failure before completion
permits another callback attempt. External effects of a partially executed
callback are not transactional.

A fresh golden clone invokes the callback again. Its author must reconcile
already-recovered jobs and any durable completion marker before creating
another copy. The callback alone is not a once-per-logical-session job system.
Resilience enablement remains independent; registration must not silently
turn on a disabled task subsystem.

#### Benefits and costs

The contract is explicit, uses normal task handles after initialization, and
computes session-correct inputs. The cost is author migration and a new API.
It does not preserve arbitrary existing startup launch statements unchanged.
The callback alternative remains unselected and is not included in the
registry prototype.

### Option B: startup launch-intent registry

Keep existing launch-only code:

```python
run = await startup_work.start(input={"index": "catalog"})
# Do not await run.result() to complete capture-time startup.
```

Intercept the call before TaskManager lookup or task-store access. Recording
the intention requires no session, task record, lease, result future, or
execution worker. The caller receives an explicitly deferred receipt and
startup can continue.

#### Collection boundary

The prototype installs an owned registry at host construction. Under this
revised contract, collection must be allowed only while `true` intentionally
defers the runtime, resilience
is enabled, no manager is installed, and capture startup enrollment remains
open. Before-snapshot freezes enrollment. After-restore also freezes it before
dependency preparation.

The earlier registry prototype also collected in absent mode; it must be aligned
and validated again before adoption. This PR does not implement that registry.

HTTP/WebSocket request execution is excluded through an ASGI request boundary.
Missing-manager requests must not become queued startup work. Resilience
opt-out, invalid inputs, cold-mode calls before manager initialization, and
calls made before there is an owning host retain explicit failure behavior.
Once the manager exists, `.start()` takes the ordinary path.

A composed lifespan that submits work after entering the original SDK
lifespan is a supported test placement: cold mode has a real manager, whereas
capture mode enrolls the same statement without executing its body.

#### Recorded data

Record each call separately, not just each method:

| Field | Purpose |
|---|---|
| Intention ID | Stable identity for this captured launch |
| Function reference and declared options | Preserve the actual handler and per-call task options |
| Frozen input and input type | Preserve submitted values and reconstruct supported typed input |
| Explicit task ID or automatic-ID policy | Keep caller identity or bind it after session assignment |
| Input ID and input precondition | Preserve chain semantics |
| Submission order | Retain launch order, not completion order |

Freeze JSON-compatible inputs at enrollment, including model serialization.
Reject nonportable live objects/nonfinite values rather than retaining mutable
references or silently changing them. Keep session-dependent behavior inside
the task body or explicitly redesign its input; freezing an absent session ID
does not make it correct after restoration.

Captured functions/options remain process references. This is not a second
storage backend or a serialization of arbitrary Python resources.

#### Deferred receipt

The prototype uses a distinct `DeferredTaskRun`, rather than pretending an
already running `TaskRun` exists:

| Operation | Before activation | After binding |
|---|---|---|
| `is_deferred` | True | False |
| `intent_id` | Available, immutable | Same intention identity |
| `task_id` | Explicit requested ID, or None for automatic ID | Actual submitted task ID |
| `input_id` | Requested value or None | Accepted run's input ID |
| `result()` / awaiting receipt | Explicit initialization error; never wait for capture to finish | Delegate to actual run |
| `cancel()` | Cancel enrollment without task-store access | Delegate to actual run |

Normal `TaskRun` keeps its existing shape and execution semantics, with an
`is_deferred=False` observation. The prototype widens `.start()`'s annotated
return to include the deferred receipt only for the newly supported case.
That API/type shape needs review; it is not a claim of release compatibility.

#### Activation and recovery

```text
Real-session binding and dependency preparation
  -> provide captured startup definitions/options to the manager
  -> initialize manager; immediately recover eligible persisted tasks
  -> reconcile each recorded intention
  -> bind receipt to recovered run or submit through ordinary .start()
  -> finish restore without waiting for task completion
```

Automatic IDs for **new submissions** include the captured intention, actual
agent/session, and platform `restore_id` when available:

```text
snapshot: SHA256(agent_name : session_id : intent_id : restore_id)
no restore ID: SHA256(agent_name : session_id : intent_id)
```

The second form is unchanged for registry activation without a restore ID.
Ordinary non-snapshot startup still uses its existing task submission path and
ID generation; it does not manufacture a platform restore ID.

FHA generates a new restore ID for a new golden materialization, crash
replacement, idle restoration, and qualifying in-place memory resume. Retries
and concurrent hook calls for the same restoration reuse that ID. Normal
requests and lease renewal do not change it.

**Recover first, allocate second.** Match a captured intention to unfinished
startup work by its stable intention marker and actual session before deriving
a new launch ID. A recovered run retains its persisted task ID even though a
fresh submission in the new restoration would have a different ID. Retain the
recovered handle if a short job completes before the registry drain.

When no unfinished match exists, create new work. A completed/deleted one-shot
job is not recreated with its old ID: the new materialization gets a new
restore-scoped ID. This addresses the hosted create409 that previously failed
idle after-restore.

The existing best-effort manager scan remains unchanged. Query failure or an
unreclaimed in-progress startup record is not proof of absence; registry drain
surfaces the uncertainty/conflict rather than launching another copy.
Same-restoration retry IDs are deterministic, and valid accepted launches are
not repeated.

Explicit user task IDs remain unchanged. Unrelated marker/source conflicts
fail, rather than silently attaching or rewriting the caller's identity.

The prototype persists an internal intention marker with normal task creation.
Initial/inline recovery uses that marker to recover the captured handler,
input type, and options. Recovered run handles are retained through startup
reconciliation even if a short one-shot task finishes and deletes its record
before the registry is drained. Otherwise recovery followed by replay could
start it twice in the same materialization.

Accepted intentions are checkpointed by runtime/materialization. Same-ID
retries do not resubmit valid accepted work; an unfinished drain retries
remaining work. Runtime disposal invalidates unfinished acceptance, not a
successful result that the receipt already holds. If a later intention fails
and the manager is rebuilt for the same restore ID, previously successful
completed intentions remain deduplicated. A different restore ID can create
fresh startup work when no unfinished job exists. Partial submission failure
follows the existing worker cleanup/configuration rollback path.

No change to worker timing, task storage backend, lease fencing, or immediate
best-effort discovery policy is required.

#### Limits and rollout

It cannot transparently complete startup that requires:

```python
value = await prepare.run(input=...)
await bootstrap.start(input=value)
```

The result does not exist during capture. Waiting for it can prevent readiness
and capture. The same issue applies to `.start()` followed by `.result()`.
Inputs tied to session identity/live resources need restore-time rebinding.
An unawaited coroutine has not submitted anything to record.

The registry only preserves launch intentions that actually execute the
supported submission path before enrollment freezes. It does not replay all
startup Python statements, supply capture-time task results, or repair missing
dependencies of an immediately recovered task.

Cancellation before capture can remain part of the template. Cancellation or
completion that happens later in a session is not written back into the golden
registry. Applications needing permanent logical-session cancellation or
once-only effects must persist and reconcile that state externally.

The advantage is preserving existing non-blocking startup launches without a
new callback. Costs include the deferred receipt contract, collection boundary,
input/identity policy, and explicit replay reconciliation. Testing must cover
actual startup calls, not merely decorator registration.

### Shared duplicate-launch concern

Both options must specify per-materialization versus once-per-logical-session
behavior. Every golden clone begins with the original callback/intent state.
In-memory restore checkpoints do not establish cross-clone once-only effects.
Stable task IDs help, but one-shot records are deleted at terminal exit.
Once-per-session guarantees need durable reconciliation or application
idempotency; neither option provides generic exactly-once execution.

Neither historical option is selected. Option B's separate restore-scoped
prototype has its own local and hosted evidence below, but is not included in
this implementation or proposed as a released API.

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
| True deferral; absent/false cold startup; opt-out; malformed input | Targeted startup tests |
| Definitions before activation; restored binding | Core/Responses activation tests |
| Same-ID concurrent/duplicate hooks | Real ASGI tests; one runtime/scanner |
| Partial initialization/scanner failure | Completed-phase reuse tests |
| Actual cancellation and environment rollback | Worker quiescence and retry tests |
| Client timeout/retry | Loopback HTTP test |
| Recovery LIST failure | Best-effort completion and periodic retry test |
| Recovery/lease filtering/fencing | Existing targeted task suites |
| Execution/renewal during hook | Real recovered task/heartbeat integration test |
| Application handler task submission | Decorated `.start()`/bounded `.run()`, nested definitions, no automatic recovery before dependencies, failed/cancelled-hook retries |
| Inactive provider configuration changes | Cancelled initial scan followed by omitted endpoint override rebuilds the provider |
| Cold and initial golden LRA activation | Controlled hosted sample, actual external lease renewal |
| Hard crash after checkpoints 1 and 2 | Controlled hosted recovery; no new invocation during orphan interval |
| Independent sessions/concurrent tasks | Controlled hosted owner/worker/lease observations |
| Cancellation | Controlled hosted terminal cancellation, no task resurrection during observation |
| Natural idle/resume | Controlled hosted test: 120-second policy; after six quiet minutes, same session/capture with a new restore ID and worker, followed by renewed leases and completion |
| Historical Option B startup submissions | Separate unselected prototype; not qualification of the existing-handler implementation |

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

### Historical, unselected Option B prototype qualification

The fixed registry prototype passed 220 selected local/package tests and nine
controlled hosted cases. The hosted sample executes a real decorated startup
task through a composed ordinary lifespan, not a session-start callback:

| Case | Observation |
|---|---|
| Cold startup | Original non-snapshot task creation and lease behavior |
| Absent-flag capture/restoration (previous prototype contract) | Deferred intention/no runtime at capture; real leased launch after SDK activation |
| Completed startup followed by natural idle | New restore ID and fresh startup task ID, without the prior create409/hook500 |
| Crash while startup is unfinished | Original task ID retained, fencing generation increments, saved progress resumes |
| Crash after startup completes | New materialization creates fresh startup work with a new automatic ID |
| Checkpoint2 crash after startup completes | Original response resumes at phase3; fresh startup work completes |
| Independent sessions and concurrent responses | Session-scoped identities, one manager/startup job and independent leases |
| Response cancellation | Target response stays cancelled without resurrecting or cancelling the independent startup job |
| Literal true SDK flag | Set in a separate controlled image; capture defers and restored work leases normally |

Task-store observations establish actual lease acquisition/renewal, worker
identity and fencing. Capture/restore logs establish materialization ordering.
Crash runs prohibit request-driven recovery before independent task-store
reclaim evidence. The idle run closes logs, waits six quiet minutes after all
initial work completes, then invokes the same session once; exact suspension
time is not inferred.

The previous registry version failed after completed task deletion because it
reused the same automatic ID. Including an available restore ID for **fresh**
work resolved that hosted conflict while preserving unfinished-task recovery.
Application completion state is not a generic exactly-once guarantee.

Explicit caller IDs, same-restore failure/retry, and fault-injected discovery
failure are covered by the local suite, not separate hosted fault runs.
Setting true in the image does not prove automatic platform flag injection or
support for a reserved agent-definition environment override.
