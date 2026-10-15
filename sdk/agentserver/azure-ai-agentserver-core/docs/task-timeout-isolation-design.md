# Task timeout hard-cap via process isolation — unified design (spawn + fork)

**Status:** spawn + per-chain reuse **implemented & tested** (unit + live westus2); fork backend
**implemented & tested** (unit on Linux/WSL + live westus2). Both are **opt-in, default off**.
This doc is the single source of truth: the **general design is common to both backends**;
the two options differ **only in the worker-internals** (§7). It supersedes/combines
`task-timeout-hardcap-design.md` and `fork-worker-design.md`.

---

## 1. Problem & requirements
A durable/resilient task's per-turn `timeout` was historically **cooperative-only** — a handler
that ignored `ctx.cancel` could run forever (conformance C-TMO-6: "MUST NOT force-stop"). We
need a **hard execution cap**: when the timeout elapses and the handler ignores the cooperative
cancel, force-stop it after a bounded grace, **without**:

- **R1 — Force-stop at will:** the SDK must be able to stop a runaway handler regardless of what
  it's doing (CPU-bound loop, blocking syscall, C-extension call, or code that swallows
  cancellation).
- **R2 — Don't disrupt the parent:** killing the handler must not affect the main container or
  co-located tasks.
- **R3 — Durability preserved:** the task store, lease, recovery/nanny, streaming, and steering
  must stay correct; a force-stopped turn must **not** be silently resurrected.

**Non-goal:** capping concurrency. We do **not** introduce a policy concurrency cap (see §9).

---

## 2. The only authoritative mechanism: a separate OS process you can kill
For **arbitrary native Python**, the *only* way to satisfy R1+R2 is to run the handler in a
**separate OS process and `kill()` it**. Everything else fails one requirement:

| Option | Force-stop? | Parent-safe? | Verdict |
|---|---|---|---|
| `task.cancel()` / `asyncio.timeout()` / `wait_for()` | ❌ cooperative | ✅ | old behavior; stubborn handler ignores it |
| `PyThreadState_SetAsyncExc` / `sys.settrace` / `SIGALRM` | ⚠️ can't interrupt C/blocking; catchable | ❌ corrupts shared state | rejected (non-authoritative + unsafe) |
| Thread + kill | ⚠️ no clean thread-kill in CPython | ❌ shares GIL/memory | rejected |
| Subinterpreters (PEP 734) | ❌ can't force-stop busy interp | ❌ shares process | immature; doesn't solve killability |
| **Subprocess + SIGKILL (chosen)** | ✅ | ✅ | the mechanism |
| Instrumented runtime (WASM epoch/fuel) | ✅ | ✅ | N/A — not native Python |

**`spawn` and `fork` are two ways to create that killable process** — same kill mechanism,
different creation internals. That difference is the entire subject of §7; everything else in
this doc is common.

---

## 3. Architecture — parent owns authority, child is pure compute
**Parent (main process):** owns everything with side effects/authority — the **task store &
lease**, **timeout watchdog**, **recovery/nanny**, **streams registry**, **steering queue**,
the `_ActiveTask` registry and (reuse) the worker registry. It runs the retry loop, drain,
suspend/complete/delete transitions, and marker/recovery logic.

**Child (worker process):** a pure compute unit that runs **only `fn(ctx)`**. It may compute
anything but may **not** own or directly touch any durable/shared resource. Every side effect
the handler triggers is **proxied to the parent** over IPC. The child has **no** direct
store/lease access (enforced — see §8).

The developer contract is **`@task` / `@multi_turn_task` on `async def fn(ctx)` and nothing
else** — isolation/spawn/fork/reuse are invisible, toggled by platform env vars.

---

## 4. IPC — the common wire protocol & contracts
The protocol is **identical for both backends** (only the transport bytes differ — §7). It is
**length-prefixed (4-byte big-endian) UTF-8 JSON**, with an id-correlated request/response
sub-protocol.

### 4.1 Message families
**Parent → child (control):**
- `MSG_RUN {snapshot, reuse?}` — start a turn (the snapshot = ctx fields + handler module/name).
- `MSG_CANCEL {timeout_exceeded, cancel_requested, pending?}` — cooperative cancel.
- `MSG_SHUTDOWN` — process-scoped shutdown.
- `MSG_RESP {id, value}` — response to a child round-trip.

**Child → parent:**
- `MSG_EMIT {stream_id, payload, close}` / `MSG_STREAM_CLOSE {stream_id}` — streaming.
- `MSG_REQ {id, kind, ...}` — round-trip: `flush` / `last_cursor` / `pending_count`.
- **Terminal (exactly one per turn):** `MSG_RESULT {value, metadata}` |
  `MSG_SUSPEND {reason, output, metadata}` | `MSG_EXIT_FOR_RECOVERY {metadata}` |
  `MSG_ERROR {exc_type, exc_msg, traceback, metadata}`.

### 4.2 The `ctx` proxy (what the handler touches)
The child's `ctx` looks identical to in-process, but its IO-bound handles are proxies:
- `ctx.metadata` → `_ProxyMetadata` → `REQ_FLUSH` → parent persists; full snapshot also rides
  the terminal message so un-flushed mutations aren't lost.
- streams / `ctx.emit` → `_ProxyStream` (via `streams._factory`) → `MSG_EMIT` → parent's real
  streams.
- `ctx.cancel` / `ctx.shutdown` → `_HybridCancel` (a thread-settable bool + `asyncio.Event`, so
  it works even for a CPU-bound handler that polls without awaiting).
- `ctx.pending_input_count` → provider backed by `proto.pending`.
- Pure-data fields (`task_id`, `input`, `entry_mode`, `retry_attempt`, `recovery_count`, …) are
  plain values carried in the snapshot.

### 4.3 Bidirectional `ctx` bridge (watchdog ↔ handler)
In-process, `ctx` is shared mutable state between the watchdog (writes `timeout_exceeded`,
`cancel`) and the handler (reads them). Across processes there is no shared memory, so the
"sharing" is **emulated by message passing**, in both directions, preserving the ordering
invariant:

- **Parent → child:** `_bridge_cancel_to_worker` watches the parent `ctx.cancel`/`ctx.shutdown`;
  on fire it sends `MSG_CANCEL`/`MSG_SHUTDOWN`. The child reader sets the **cause booleans
  first**, then trips the cancel event (cause-before-cancel invariant, same as in-process).
- **Child → parent:** metadata flush (`REQ_FLUSH`), pending count (`REQ_PENDING_COUNT`), streams
  (`MSG_EMIT`), and the terminal metadata snapshot.

**Design rule:** any *new* field shared between the handler and the watchdog/framework must get
an explicit bridge message — it will not "just work" across the boundary.

### 4.4 Terminal-outcome contract (how the parent learns the result)
The parent never infers the outcome from an exit code. The child sends a **structured terminal
message** (§4.1); the parent's `outcome()`/`run_turn` applies the final metadata snapshot then
`_reconstruct_outcome`:
`MSG_RESULT`→value, `MSG_SUSPEND`→`_Suspended`, `MSG_EXIT_FOR_RECOVERY`→`_ExitForRecovery`,
`MSG_ERROR`→re-raised reconstructed exception (type+message+traceback; `CancelledError` mapped).
The exit code / EOF is used **only** as a crash fallback (§6).

---

## 5. Lifecycle — tiered timeout enforcement (common)
Per turn, the parent arms a **tiered watchdog** (a task independent of the handler):

1. **Stage 1 — cooperative.** At the per-turn budget: set `ctx.timeout_exceeded = True` **then**
   `ctx.cancel` (bridged to the child); persist a durable `timeout_cancelled_at` marker.
2. **Stage 2 — grace.** Wait `AGENTSERVER_TASK_TIMEOUT_HARDCAP_GRACE_SECONDS` (default 1 hr). If
   the handler winds down, the turn ends normally and no kill happens.
3. **Stage 3 — hard cap.** Still running → `run.kill()` (SIGKILL the child). The kill surfaces
   (via socket EOF, no terminal message) as `_WorkerKilled` → `_run_handler` raises
   `asyncio.CancelledError()` → the **existing** end-of-turn finalization runs:
   - one-shot → **delete** (ephemeral);
   - multi-turn → `_try_drain_steering`: if input is queued, **drain to the next turn**; else
     **suspend** the chain.

The **manager awaits the handler** in `_execute_task_loop` (`await self._run_handler(...)`).
Because the watchdog is a *separate* task and the kill closes the child → EOF, the await is
**guaranteed to unblock** (unlike in-process, where a runaway `await fn(ctx)` can hang forever).

---

## 6. Outcome, crash, lease, recovery (common)
- **Normal terminal:** parent reconstructs the outcome (§4.4), persists status
  (completed/suspended/failed), and **releases the lease**. The child never touches the
  lease/store.
- **Intentional kill (hard cap):** no terminal + we killed it → `_WorkerKilled` → CancelledError
  → finalization as in §5.
- **Unexpected death (OOM/segfault):** no terminal + we did *not* kill it → **`WorkerCrash`** →
  bounded local re-invoke (`max_worker_attempts = 2`, re-entered as a recovered turn), then fail
  the turn.
- **Recovery / nanny non-resurrection:** a force-stopped turn is detected via the persisted
  `timeout_cancelled_at` marker (correlated to `turn_started_at`) **or** the derived backstop
  `now ≥ turn_started_at + timeout`; recovery **finalizes** it instead of re-running, and moving
  the record out of `in_progress` stops the external `StaleTaskRecoveryService` from reviving it.
- **Parent crash (orphan child):** durability is handled by the *normal* crash-recovery path —
  lease renewal stops → lease expires → nanny reclaims the `in_progress` task → re-runs from the
  last checkpoint in a fresh container/parent/child. The orphaned child **cannot corrupt the
  store** (no direct access; its IPC writes hit a dead pipe and silently no-op) and receives a
  **cooperative shutdown** via EOF on its control channel. See §10 for the orphan-cleanup gap.

---

## 7. **Backend internals — the ONLY place spawn and fork diverge**
Everything in §1–§6 and §8–§12 is backend-agnostic. The two backends differ purely in **how the
worker process is created, how bytes are transported, and how the handler/ctx are obtained** —
then both plug into the **same** `IsolatedRun` (one-shot) / `PersistentWorker` (reuse) and the
same protocol. Selected once per turn by `_make_spawner()` / the fork flag.

### 7.0 Shared worker classes (both backends run these)
- `_ChildProtocol` — child-side protocol endpoint (control-reader thread + writer).
- `IsolatedRun` — parent-side one-shot runner (`outcome()`, `kill()`, read-loop, dispatch).
- `PersistentWorker` — parent-side reusable runner (`run_turn()`, turn-loop, `kill()`).
- `IsolationBridge` — parent callbacks (flush/emit/last_cursor/pending/apply_final_metadata).
- `_build_child_context` / `_resolve_handler` / `_classify_terminal` / `_reconstruct_outcome`.

### 7.1 SPAWN internals (`create_subprocess_exec`) — the shipped default
- **Create:** `asyncio.create_subprocess_exec(python, "-m", "...tasks._isolation")` → a **blank
  interpreter**.
- **Get the app:** the child **re-imports** the handler's module (~1–2 s) via `_resolve_handler`
  (`importlib.import_module`), then **resolves the handler by name** from
  `_REGISTERED_DESCRIPTORS`.
- **Get ctx:** rebuilt from the JSON **snapshot** (nothing crosses a process boundary without
  serialization).
- **Transport:** three std streams — `stdin` (control), `stdout` (protocol), `stderr` (user
  logs, forwarded to the parent logger). The child dups fd1→fd2 first so user `print()` can't
  corrupt the protocol; the true fd1 is a private protocol fd.
- **Process handle:** `asyncio.subprocess.Process` → `.pid`, `.kill()` (SIGKILL), `.wait()`.
- **Memory:** full private copy per worker (**~100–300 MB**, no COW).
- **OS:** portable — Linux, macOS, Windows.
- **Manager in child:** never set (`_manager is None`) → Tasks API unavailable "for free" (§8).

### 7.2 FORK internals (`multiprocessing.get_context("fork")`) — Unix-only, opt-in
- **Create:** `mp.get_context("fork").Process(target=_fork_child_entry, args=(child_sock,
  parent_fd, reuse))`; `proc.start()` calls `os.fork()`. The child **inherits the parent's whole
  imported app** (COW).
- **Get the app:** **no re-import** — `_resolve_handler`'s `import_module` is a **free no-op hit
  on the inherited `sys.modules`**; the handler object is already resident. Start cost **~1–5
  ms**.
- **Get ctx:** rebuilt from the snapshot via the **same** `_build_child_context` — chosen over
  literally inheriting the live `ctx` because (a) multi-turn reuse can't inherit a fresh ctx per
  turn, (b) lowest risk, (c) the perf/memory wins come from inheriting the *interpreter*, not the
  ctx object. (Developer DX is identical either way.)
- **Sanitization — `_after_fork_child` (fork-only, mandatory):** the child inherited a live
  async+threaded parent, so **first thing**: `set_task_manager(None)` (neutralize the inherited
  manager → no split-brain, §8), **close the inherited peer-socket fd** (and other dead fds), and
  let `asyncio.run()` create a **fresh event loop** (the inherited loop is never used). CPython's
  `os.register_at_fork` resets GIL/import/logging locks.
- **Transport:** one `socket.socketpair()` — a single bidirectional channel carrying the **same**
  length-prefixed-JSON protocol (`_ChildProtocol(in_fd == out_fd == socketfd)`). User logs go to
  the inherited `stderr` directly.
- **Process handle:** a thin **`_ForkProcAdapter`** presents the `multiprocessing.Process` + the
  asyncio-wrapped socket with the **exact surface** `IsolatedRun`/`PersistentWorker` consume
  (`stdin` writer, `stdout` reader, `stderr=None`, `pid`, `kill()`, `wait()`, `returncode`) — so
  those classes run over fork **unchanged**. `start_forked` / `start_forked_worker` are the fork
  analogues of `start_isolated` / `start_persistent_worker`.
- **Memory:** COW — each worker is a small incremental cost, not a full copy.
- **OS:** **Linux only** (`_worker_fork_enabled()` returns False elsewhere → spawn). macOS fork +
  native libs is unsafe; Windows has no fork.
- **Safe alternative (`forkserver`):** fork children from a dedicated single-threaded preloaded
  server (no held locks, no live loop) — safest, but must snapshot+resolve (no live ctx). Kept as
  a documented sub-mode; not the default. Neither fork nor forkserver adds a concurrency cap
  (they're factories, not pools).

### 7.3 Side-by-side
| Property | Spawn | Fork |
|---|---|---|
| Create | `create_subprocess_exec` (blank interp) | `mp fork` (inherit app, COW) |
| Re-import app | **yes (~1–2 s/turn)** | **no** (inherited) |
| Resolve handler | by name (after re-import) | by name = free (already imported) |
| Build ctx | from snapshot | from snapshot |
| Transport | 3 std pipes (stdin/stdout/stderr) | 1 `socketpair` |
| Process handle | `asyncio.subprocess.Process` | `mp.Process` via `_ForkProcAdapter` |
| Start latency | ~1–2 s | **~1–5 ms** |
| Memory/worker | full copy ~100–300 MB | **COW** (small increment) |
| OS | Linux/macOS/Windows | **Linux only** |
| Manager in child | `None` (never set) | **`None` (actively nulled)** |
| Extra safety step | none | `_after_fork_child` sanitization |
| Kill primitive | `proc.kill()` | `proc.kill()` (mp) via adapter |

---

## 8. Enforcement boundary — no Tasks API inside a handler (common)
A handler's complete interface is `ctx` (metadata, streams, cancel/shutdown/timeout, `return`
to suspend, pending count). The **Task manager is framework infrastructure**; a handler calling
`get_task_manager()` / `other_task.start()` / `manager.provider.get()` is reaching below its
layer. This is:
- **Unnecessary** — everything a handler needs is in `ctx`; orchestration belongs in the
  request/app layer (main process), where the manager is always present.
- **Recovery-unsafe** — such calls aren't checkpointed, so a crash+recovery **re-fires** them
  (e.g. duplicate `start`). In-handler orchestration silently violates durability.

Isolation **enforces** this boundary by construction: the child has no manager (spawn: never
set; fork: actively nulled in `_after_fork_child`) → in-handler Tasks-API calls raise
`TaskManagerNotInitialized`. For fork this also prevents **split-brain** (using the inherited
manager copy would make two processes write the same lease/record).

**Only the narrow `ctx` surface is bridged** (metadata/streams/cancel/pending). We deliberately
do **not** bridge the general Tasks API — see §11 (optional/deferred, with the recovery-safety
caveat).

---

## 9. Concurrency, performance, memory (common framing, per-backend numbers)
- **No policy cap.** Neither backend imposes a concurrency ceiling; the only limit is physical
  memory / OS fd+PID ulimits. We explicitly reject a bounded shared pool (it would cap
  concurrency, which is a non-goal).
- **Isolation is a parallelism win:** handlers run in separate processes → no shared-GIL
  starvation from a CPU-bound handler.
- **Spawn cost:** ~1–2 s re-import + ~100–300 MB per concurrent turn ⇒ effective ceiling ~**8–10
  on a 2 Gi** container (memory-bound; overload risks OOM). Per-chain reuse (below) amortizes the
  re-import to once/chain.
- **Fork cost:** ~ms start + COW memory ⇒ ceiling rises **back toward in-process density**.
- **Per-chain reuse + idle-TTL** (multi-turn only): a warm worker per `task_id`, reused across
  turns, evicted after `AGENTSERVER_TASK_WORKER_IDLE_TTL_SECONDS` idle. **This is a *spawn*
  optimization** (import once/chain instead of once/turn); **fork barely needs it** (per-turn
  fork is already ~ms + COW), so the recommended fork mode is per-turn fork with reuse off. Reuse
  composes with fork if cross-turn warm RAM is explicitly wanted.

---

## 10. Open items / known gaps (same for both backends)
1. **Orphan-child hard guarantee (unimplemented).** On parent crash the child gets a cooperative
   shutdown (EOF → `ctx.shutdown`) and can't corrupt the store, but a runaway child isn't
   *guaranteed* to die (no `PR_SET_PDEATHSIG`). In the hosted container model, parent crash =
   container/PID-namespace teardown → children die anyway; the gap bites only if the parent dies
   but the namespace survives. **Hardening:** set `prctl(PR_SET_PDEATHSIG, SIGKILL)` on Linux
   (fork: in `_after_fork_child`; spawn: in the child at startup) so the kernel kills the child
   on parent death.
2. **Tasks-API bridge (spec only; optional/deferred).** In-handler Tasks-API calls raise today
   (by design, §8). If genuine in-handler orchestration is ever needed it requires a *replay-safe
   orchestrator* feature, not just an RPC bridge (the bridge would make the call *work* but not
   *recovery-safe*). See §11.
3. **Clearer error message.** Replace `TaskManagerNotInitialized` (when hit from inside a
   handler) with a purpose-built "the Tasks API can't be called from a handler; use `ctx` /
   orchestrate from the app layer" error. Cheap, worth doing.
4. **At-least-once external side effects.** Inherent to crash-recovery (not isolation-specific):
   a recovered turn re-runs from checkpoint; handler idempotency for external effects is the
   author's responsibility. The store is always safe.

---

## 11. Tasks-API bridge — optional/deferred (summary)
*Backend-agnostic.* If we ever support in-handler orchestration safely, route the Tasks-API
surface (`start`/`get`/`list`/`cancel`; then `run`/`result`/streaming) to the parent's **real**
manager over a new `MSG_TASKAPI_REQ/RESP` family, via a child-side `_ProxyTaskManager` (returned
by `get_task_manager()`) + `_ProxyTaskRun`, with all execution (and thus all store/lease writes)
in the parent (split-brain-free). Requires refactoring the decorator's `start`/`run` to delegate
to a manager entry point the proxy can intercept, plus error-type reconstruction across the
boundary. **Caveat:** the bridge is transport only — it does not make in-handler orchestration
recovery-safe; that needs a purpose-built deterministic/replay-safe orchestrator. Ship only if a
real need arises.

---

## 12. Selection, flags, backward-compat, testing
### 12.1 Flags (all opt-in; default off ⇒ exact legacy in-process behavior)
- `AGENTSERVER_TASK_ISOLATION` — turn isolation on.
- `AGENTSERVER_TASK_WORKER_FORK` — use fork backend (Linux only; else spawn).
- `AGENTSERVER_TASK_WORKER_REUSE` — per-chain reuse (multi-turn only).
- `AGENTSERVER_TASK_TIMEOUT_HARDCAP_GRACE_SECONDS` (default 1 hr).
- `AGENTSERVER_TASK_WORKER_IDLE_TTL_SECONDS` (default 300).

Selection is a **single OS-branch** at worker creation (`_run_handler` / `_get_or_start_worker`
pick `start_forked*` vs `start_isolated`/`start_persistent_worker`). Off ⇒ `_run_handler`
short-circuits to `await fn(ctx)` (zero overhead). Runtime **fallback to spawn** if a fork
hand-off fails — never fail a turn over the optimization.

### 12.2 Backward-compat
- **Default off = no change**; the legacy cooperative-only, in-process path is untouched.
- **Persisted state is two-way compatible:** the only new field (`timeout_cancelled_at`) is
  additive/optional (recovery tolerates its absence; old readers ignore it). The **execution
  backend is never persisted** → a task can be checkpointed in-process and recovered under
  spawn/fork (or vice versa) freely.
- **Crash-restart is the safest upgrade point:** a crash already wiped RAM, so switching backends
  there loses nothing that wasn't already gone.
- **Behavior changes are gated behind the flags:** hard-cap enforcement (was cooperative-only)
  and per-turn RAM reset (spawn/fork) / cross-turn RAM persistence (reuse) — transparent to
  handlers that keep durable state in `ctx.metadata`.

### 12.3 Validation status
- **Unit:** full tasks suite green with isolation off (654 passed); isolation suite (spawn
  one-shot/multi-turn/reuse) green; **fork** suite (one-shot + multi-turn drain/suspend + reuse
  same-pid / hard-kill respawn / idle-TTL) green on Linux/WSL. Windows: fork tests skip
  (Linux-gated), spawn tests pass — no regression.
- **Live westus2 (hosted Foundry agent):** spawn validated earlier (one-shot hard-kill+delete,
  not recovered; multi-turn drain). Fork validated this session — image built (with an
  `httpx`-in-requirements fix for image dependency drift), agent version deployed with
  `AGENTSERVER_TASK_WORKER_FORK=1`, one-shot + multi-turn runaway dispatched, and the parent
  container **survived the fork-child hard-kills and kept serving** (the core R2 signal).

---

## 13. Alternatives considered & rejected
This consolidates every significant option evaluated across the design, grouped by decision.

### 13.1 How to force-stop a runaway handler (the core mechanism)
| Alternative | Why rejected |
|---|---|
| **Cooperative only** — `task.cancel()`, `asyncio.timeout()`, `wait_for()`, `CancellationToken`-style flag | Not authoritative — a handler that never awaits or swallows `CancelledError` ignores it. This *was* the old behavior and is exactly what we're fixing. |
| **In-process exception injection** — `PyThreadState_SetAsyncExc`, `sys.settrace` deadline hook, `signal.SIGALRM` | Non-authoritative **and** unsafe: cannot interrupt a C-extension call or blocking syscall, is catchable, and injecting at an arbitrary point corrupts shared in-process state (same reason .NET removed `Thread.Abort`, Java deprecated `Thread.stop`). |
| **Thread + kill** | CPython has no clean thread termination; a killed thread shares the GIL/heap so it can't be isolated or safely stopped. |
| **Subinterpreters** (PEP 734) | Can't force-stop a busy interpreter, and it still shares the process → violates "don't disrupt the parent." Immature. |
| **cgroups / one container per task** | Works, but it's the same "kill a separate process" principle at a much heavier orchestration layer — more infra, slower, out of the SDK's control. |
| **Instrumented runtime** (WASM epoch/fuel, e.g. Wasmtime) | Genuinely preempts guest code without killing the host, but requires running handlers as **WASM, not native Python** — inapplicable. |
| **✅ Subprocess + SIGKILL (chosen)** | The only mechanism that is both authoritative (kills regardless of what the handler is doing) and parent-safe, for arbitrary native Python. |

### 13.2 Enforcing the timeout — why not `asyncio.timeout` / `wait_for`
Rejected as the *enforcement* primitive because they are (a) equally cooperative (defeated by the same handlers), (b) `wait_for` **awaits the task's actual completion after firing**, so an uncooperative task makes it hang — it can't even hand control back to escalate, and (c) an `asyncio.timeout` context manager would cancel *our own* watchdog coroutine, which must survive to run the grace→SIGKILL. Chosen instead: `Event` + cause-bool for Stage 1, and a plain `asyncio.sleep(grace)` → out-of-process SIGKILL for Stage 3.

### 13.3 Worker process creation
| Alternative | Decision |
|---|---|
| **Spawn** (`create_subprocess_exec`) | **Chosen default** — portable (Linux/macOS/Windows), single code path, zero overhead when off. Cost: per-turn re-import + full-copy memory. |
| **Fork** (`multiprocessing fork`) | **Chosen, Linux-only, opt-in** — inherits the imported app (COW, ~ms start, no re-import). Rejected as *default* because it's Unix-only and forking a live async+threaded parent needs sanitization. |
| **forkserver** | **Documented sub-mode, not default** — safest fork variant (forks from a clean preloaded server, no held locks), but it pickles args and lacks the live `ctx`, so it reverts to snapshot+resolve. Kept as the fallback if a native lib proves fork-hostile. |
| **Direct fork inheriting the live `ctx` object** | **Rejected in favor of snapshot-built `ctx`** — multi-turn reuse can't inherit a fresh ctx per turn anyway; inheriting a live object graph adds shared-fd/mutation risk; the perf/memory wins come from inheriting the *interpreter*, not the ctx object; developer DX is identical. |

### 13.4 Worker lifecycle / concurrency
| Alternative | Decision |
|---|---|
| **Per-turn spawn/fork** | **Chosen default.** Spawn amortized via optional reuse; fork is already ~ms so per-turn is optimal. |
| **Per-chain reuse + idle-TTL** | **Optional, multi-turn only.** A spawn optimization (import once/chain); fork barely needs it. Retained for spawn latency and (optionally) cross-turn warm RAM. |
| **Bounded shared worker pool (size P)** | **Rejected** — it imposes a concurrency **cap** of P, and capping concurrency is an explicit non-goal. |
| **Unbounded warm pool** | **Rejected** — self-defeating: keeps the import saving but re-introduces the exact memory/OOM ceiling the pool was meant to remove (and grows idle memory without eviction). If a fixed P is undesirable, use a memory-derived cap + idle-TTL, never a hard pool. |

### 13.5 Handler ↔ Task manager
| Alternative | Decision |
|---|---|
| **Let the (fork) child use the inherited manager** | **Rejected** — the inherited manager is a frozen COW copy holding the parent's store/lease fds → **split-brain** (two processes writing the same record). The child's manager is actively nulled. |
| **Bridge the Tasks API to the parent over RPC** | **Deferred / not built** — in-handler Tasks-API use is unnecessary (everything is in `ctx`; orchestration belongs in the app layer) **and recovery-unsafe** (uncheckpointed calls double-fire on recovery). We **enforce** the boundary (child has no manager) rather than bridge it. If real in-handler orchestration is ever needed it requires a replay-safe orchestrator feature, not just this bridge. |

### 13.6 Recovery detection of a force-stopped turn
| Alternative | Decision |
|---|---|
| **Persisted "timed-out" terminal state** | Not used — avoids a bespoke terminal state and extra transitions. |
| **✅ Durable `timeout_cancelled_at` marker + derived backstop** (`now ≥ turn_started_at + timeout`) | **Chosen** — recovery finalizes the turn instead of re-running; moving the record out of `in_progress` stops the external nanny from resurrecting it. |

### 13.7 Orphan child on parent crash
| Alternative | Decision |
|---|---|
| **Cooperative shutdown via control-channel EOF (current)** | Implemented, but not a hard guarantee — a runaway orphan can linger unless the container/namespace is torn down. |
| **`PR_SET_PDEATHSIG` → SIGKILL (recommended, not yet implemented)** | The robust fix — the kernel kills the child the instant the parent dies. Flagged as the hardening item (§10). |

---

## Appendix — decision records
- **Only authoritative stop = separate killable process** (§2); in-process injectors are
  non-authoritative + unsafe; instrumented runtimes (WASM) are inapplicable to native Python.
- **Concurrency capping is not a goal** (§9); no bounded pool; unbounded per-turn/reuse; the only
  limit is physical memory.
- **Spawn is the portable default; fork is a Linux-only perf/memory optimization** behind a flag,
  reusing all shared worker code via `_ForkProcAdapter`.
- **Handler must not call the Tasks API** (§8) — unnecessary + recovery-unsafe; enforced by
  construction, not bridged (bridge is optional/deferred, §11).
- **`ctx` is shared state bridged by message-passing** (§4.3); new shared fields need explicit
  bridging.
