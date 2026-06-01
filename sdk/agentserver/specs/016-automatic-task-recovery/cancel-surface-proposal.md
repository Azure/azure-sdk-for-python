# Proposal — Task-primitive cancellation surface

**Status:** Draft (iterate before incorporating into spec 016 / superseding FR-031 / FR-033 / SC-016).

**Why this exists:** FR-031 in spec 016 proposes adding `CancelSignal` (a wrapper around `asyncio.Event` with a `.reason` Literal) to disambiguate why `ctx.cancel` was set. On reflection (2026-05-30, mid-iter-14), `TaskContext` *already* carries enough state to disambiguate every cause without inventing a fourth surface. Before locking this into spec 016, audit the existing surface end-to-end against the responses-package's hard-won guidance, enumerate every scenario a handler can face, and decide whether a new public type is justified.

This document is the proposal — once we reach a decision, the chosen option will be folded into spec 016 (updating or deleting FR-031 / FR-033 / SC-016 accordingly) and this file can be archived or deleted.

---

## 1. What `TaskContext` already exposes (audit)

From `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_context.py`:

| Surface | Type | Default | What it represents |
|---|---|---|---|
| `task_id` | `str` | — | Identity. |
| `input` | `Input` | — | The current turn's input (typed). |
| `metadata` | `TaskMetadata` | — | Persistent state surface (namespace-aware). |
| `retry_attempt` | `int` | `0` | Durable failure-retry counter. Survives crashes; bumped only on failure-retries. |
| `recovery_count` | `int` | `0` | Number of times the framework re-entered this task after a lease loss / stale detection. |
| **`cancel`** | `asyncio.Event` | empty | Request-level cancellation. **Today overloaded: set by timeout watchdog AND by steering drain `cancel_requested` flag.** |
| **`shutdown`** | `asyncio.Event` | empty | Container-level shutdown event. **Distinct from `cancel`**; set on SIGTERM/SIGINT. |
| `entry_mode` | `Literal["fresh","resumed","recovered"]` | `"fresh"` | Why the framework entered the handler. |
| **`was_steered`** | `bool` | `False` | True when this invocation is the result of a steering-drain re-entry. Describes the entry — not "is steering pressure pending right now". |
| **`pending_inputs`** | `Sequence[Any]` | `()` | The queue of steering inputs not yet processed. **Length > 0 ⇒ steering pressure is queued for the current generation.** |
| `steering_generation` | `int` | `0` | Monotonically increasing per-drain. |

Plus methods: `suspend(reason, output)`, `stream(item)`.

**Constructor signal axes the handler can read while running:**

| Question | How to ask today |
|---|---|
| "Should I stop?" | `ctx.cancel.is_set()` |
| "Is the container going down?" | `ctx.shutdown.is_set()` |
| "Is there steering input queued for me right now?" | `len(ctx.pending_inputs) > 0` |
| "Am I a fresh entry vs a resume vs a crash-recovery vs a steering-drain re-entry?" | `ctx.entry_mode` + `ctx.was_steered` |
| "How many crash recoveries has this task seen?" | `ctx.recovery_count` |
| "Why was `ctx.cancel` set (timeout vs steering)?" | **Not directly answerable** — would need to infer. |

---

## 2. Every scenario the handler can face

For each scenario, the columns are: who set what; what the handler should observe; what the prescribed action is. This is the inventory we'll measure proposals against.

### S1 — Steady-state mid-handler (no signals set)
- **Trigger:** Nothing. Handler is doing work.
- **`cancel`:** unset. **`shutdown`:** unset. **`pending_inputs`:** empty.
- **Prescribed action:** keep going.

### S2 — Steering pressure arrives mid-handler (steerable=True only)
- **Trigger:** Caller invokes `.start(task_id, input=I2)` while turn-1 handler is running. Drain logic in `_try_drain_steering` enqueues `I2` into `_steering.pending_inputs` and sets `ctx.cancel` with `cancel_requested = True` so the active handler notices.
- **`cancel`:** set. **`shutdown`:** unset. **`pending_inputs`:** non-empty (contains I2).
- **Prescribed action (per the FR-020..FR-024a "three strategies" framing — **all three end with `return await ctx.suspend(...)`** because to enable multi-turn the function MUST suspend; returning a raw value terminates the task and burns the queued steering input as `TaskConflictError` per FR-022):**
  - Strategy A: yield immediately → `return await ctx.suspend(...)`.
  - Strategy B: wind down to a safe checkpoint → `await ctx.metadata.flush()` → `return await ctx.suspend(...)`.
  - Strategy C: ignore the cancel hint, finish current input naturally, THEN `return await ctx.suspend(...)` so the queued I2 can drain into a fresh re-entry of the handler. The terminal-via-`return-value` path is only correct when the developer genuinely wants the task to end (no more turns, no draining I2 — caller-2 will see `TaskConflictError`); for any handler that wanted to be steerable in the first place, the suspend ending is the right shape.

### S3 — Per-turn timeout fires
- **Trigger:** `@task(timeout=...)` watchdog. Reaches the durable wall-clock deadline (FR-032..FR-035). Watchdog calls `ctx.cancel.set()` (with `reason="timeout"` under FR-031, or bare `.set()` if we drop FR-031).
- **`cancel`:** set. **`shutdown`:** unset. **`pending_inputs`:** typically empty (steering didn't trigger this).
- **Prescribed action:** suspend with partial progress (`return await ctx.suspend(output=partial)`) or fail (`raise TimeoutError(...)`) — handler's choice. Multi-turn-friendly path is suspend; terminal-fail path is raise. Returning normally is also legal — it's a completed run, just one that overran the developer's deadline.

### S4 — Container shutdown (SIGTERM/SIGINT)
- **Trigger:** Process is going down. `_shutdown_event` is set; propagated to `ctx.shutdown`. Hard cutoff after `shutdown_grace_period_seconds`.
- **`cancel`:** unset (today). **`shutdown`:** set. **`pending_inputs`:** unrelated.
- **Prescribed action:** checkpoint progress to `ctx.metadata`, then suspend cleanly (`return await ctx.suspend(...)`) so the next process re-enters with `entry_mode="recovered"`. Do NOT raise — raising marks the task failed (terminal).
- **Note:** the responses guide treats shutdown as a flavor of cancel (SHUTTING_DOWN). The task primitive today keeps them separate (`ctx.cancel` vs `ctx.shutdown`).

### S5 — Explicit `TaskRun.cancel()` call from external code
- **Trigger:** Operator or test code wants to stop a specific task. `TaskRun.cancel()` sets `ctx.cancel`. The handler is responsible for the terminal shape (suspend / complete / raise) based on its reaction. **Note (spec 016 FR-036):** `TaskRun.terminate()` and the `TaskTerminated` exception are being REMOVED entirely; `.cancel()` is the only "stop the task" API. The handler chooses whether to suspend / complete / raise; the framework does not force a terminal failure.
- **`cancel`:** set. **`shutdown`:** unset. **`pending_inputs`:** unrelated.
- **Prescribed action:** handler decides. To honor cancellation cleanly: `if ctx.cancel.is_set(): return await ctx.suspend(reason="cancelled", output=partial)`. To force a failure (caller wanted terminal-failed semantics): `if ctx.cancel.is_set(): raise RuntimeError("cancelled by operator")`. To finish current input and then suspend: just let the handler run to its natural suspend boundary; `ctx.cancel` being set has no in-framework force-stop effect.

### S6 — Crash recovery mid-turn
- **Trigger:** Process died; new process restarts; recovery picks up an in-progress task. Handler re-enters.
- **`entry_mode`:** `"recovered"`. **`cancel`:** typically unset (fresh) — UNLESS the durable budget (FR-035) is already past deadline, in which case FR-033 says `ctx.cancel.set(reason="timeout")` is pre-set so the handler observes it from the first checkpoint.
- **Prescribed action:** handler should be idempotent (check `ctx.metadata` for prior progress) and resume from the last persisted checkpoint. If `ctx.cancel.is_set()` at entry → past deadline, suspend or raise.

### S7 — Multi-turn resume (normal, not steering)
- **Trigger:** Handler previously suspended; caller invokes `.run(task_id, input=I2)`. Handler re-enters with the new input.
- **`entry_mode`:** `"resumed"`. **`was_steered`:** `False`. **`cancel`:** unset. **`pending_inputs`:** empty.
- **Prescribed action:** treat as a normal new turn. `ctx.input` is the new input; `ctx.metadata` carries prior state.

### S8 — Steering-drain re-entry (the OTHER kind of "resumed")
- **Trigger:** Handler previously suspended (or returned and was drained-through), framework re-entered the loop with the next queued steering input.
- **`entry_mode`:** `"resumed"`. **`was_steered`:** `True`. **`cancel`:** may be pre-set if another steering input was already queued behind I2 at drain time (per existing `_try_drain_steering` logic at `_manager.py:1485-1486`). **`pending_inputs`:** may be non-empty (additional steering inputs already queued behind the one driving this re-entry).
- **Prescribed action:** treat as a normal new turn. The "was steered" flag exists for telemetry / branching, but the input itself is the source of truth.

### S9 — Multiple steering inputs queued simultaneously
- **Trigger:** Caller-2 AND caller-3 both `.start()` while turn-1 is running. Queue is `[I2, I3]`.
- **`cancel`:** set on turn-1 ctx. **`pending_inputs`:** `[I2, I3]`. On turn-2's re-entry: `cancel` set, `pending_inputs == [I3]`. On turn-3's re-entry: `cancel` unset, `pending_inputs == []`.
- **Prescribed action:** same as S2 — suspend or finish; framework drains FIFO.

### S10 — Hybrid: steering pressure + timeout firing within milliseconds of each other
- **Trigger:** Edge case. `ctx.cancel` is set; could be from either source; could be both.
- **`cancel`:** set. **`shutdown`:** unset. **`pending_inputs`:** non-empty (steering happened) — but could also be empty (timeout fired first).
- **Prescribed action:** handler doesn't actually need to know which fired first; the right reaction in both cases is the same — wind down, suspend with partial work, let the next turn run.

### S11 — Hybrid: shutdown + steering pressure
- **Trigger:** Rare. Shutdown firing while a steering input was queued.
- **`shutdown`:** set. **`cancel`:** may or may not be set. **`pending_inputs`:** non-empty.
- **Prescribed action:** shutdown wins — checkpoint and suspend. The queued steering input remains in the store; the recovered task will drain it on the next process's first scheduling.

### S12 — Hybrid: shutdown + timeout
- **Trigger:** Rare. Watchdog fires near shutdown.
- **`shutdown`:** set. **`cancel`:** set. **`pending_inputs`:** empty.
- **Prescribed action:** shutdown wins. Same as S11.

---

## 3. The disambiguation question, restated

A handler at a checkpoint that observes `ctx.cancel.is_set() == True` wants to decide: **what should I do next?** From the scenarios above, the decision tree is:

```
if ctx.shutdown.is_set():
    # S4, S11, S12 — shutdown wins.
    # Checkpoint to ctx.metadata, suspend (NOT raise).
    return await ctx.suspend(reason="shutting_down", output=partial)

if len(ctx.pending_inputs) > 0:
    # S2, S9, S10 — steering pressure. (S10 hybrid: timeout coexists but reaction is the same.)
    # Strategy A: yield now.  Strategy B: wind down + flush + suspend.
    # Strategy C: let current input finish, then suspend so I2 can drain.
    return await ctx.suspend(reason="steered", output=checkpoint)

# Else: timeout (S3). No steering, no shutdown — only timeout could have set ctx.cancel.
return await ctx.suspend(reason="deadline_exceeded", output=partial)
```

Two implementation truths fall out:

1. **The existing surface (`ctx.shutdown.is_set()`, `len(ctx.pending_inputs) > 0`, fall-through "must be timeout") gives complete disambiguation today** — no `CancelSignal.reason` needed for the *information*.
2. **All three strategies in S2 converge on `return await ctx.suspend(...)`** (the user's clarification, 2026-06-01: to enable multi-turn the function MUST suspend; returning a raw value terminates and burns the queued steering input). Similarly, for S3 (timeout), the multi-turn-friendly action is also `return await ctx.suspend(...)`. So the "any cancel → suspend uniformly" handler shape is a **valid uniform default** that needs no disambiguation at all.

So when does disambiguation *actually matter for handler behavior*? Three narrower cases:

- **Strategy choice within the cancel branch.** For STEERING, Strategy C (let current input finish, then suspend) is often appropriate — the queued input runs on the next turn; finishing the in-flight work is courteous. For TIMEOUT, Strategy A (yield ASAP) is more naturally appropriate — the deadline was missed, additional work is generally undesirable unless atomic. A handler that wants to pick Strategy C for steering but Strategy A for timeout needs to disambiguate.
- **Suspend vs raise on timeout.** For STEERING, suspending is always correct (raise terminates the conversation). For TIMEOUT, a handler may legitimately prefer to raise (`raise TimeoutError(...)`) instead of suspending, depending on the workflow's semantics — "I missed my deadline; give up" vs "let me be resumed later". The handler can only express this preference if it knows the cause was timeout.
- **Observability / log message.** Logging "I yielded because user steered" vs "I yielded because I missed the deadline" is a real-but-modest value-add. A handler can always log unconditionally as "I yielded because `ctx.cancel` was set" and it's not wrong.

The first two are the load-bearing reasons to add reason-disambiguation. The third is a nice-to-have.

**Important corollary of #2 above:** if a handler is willing to adopt the uniform "any `cancel` → suspend" default, NO disambiguation is needed and the existing surface is sufficient. Disambiguation is only required for handlers that want to vary strategy (Strategy A vs C) or terminal action (suspend vs raise) based on cause. That's a smaller set of handlers than I initially framed, which weakens the case for a new public surface and strengthens the case for Proposal A.

---

## 4. The responses-package precedent

The responses package solved an isomorphic problem and shipped this surface:

```python
# azure.ai.agentserver.responses.models.runtime
class CancellationReason(str, Enum):
    STEERED = "steered"
    CLIENT_CANCELLED = "cancelled"
    SHUTTING_DOWN = "shutting_down"

# On ResponseContext
context.cancellation_reason: CancellationReason | None  # set by the framework before/during the cancel
```

Note three differences from the task primitive:

1. **`CancellationReason` is a SINGLE enum covering all causes** — including `SHUTTING_DOWN`. The responses package does NOT split shutdown out into a separate event the way the task primitive's `ctx.shutdown` does.
2. **There's a separate `CLIENT_CANCELLED`** — for foreground HTTP disconnects and explicit `POST /cancel`. The task primitive has `TaskRun.cancel()` which sets `ctx.cancel` cooperatively. **Per spec 016 FR-036 the previously-existing `TaskRun.terminate()` / `TaskTerminated` force-fail pathway is being removed**, so there's no force-stop primitive to compare against responses' `CLIENT_CANCELLED` — they both end at "cooperative cancel; handler chooses terminal shape", just with different surface naming.
3. **No "TIMEOUT" reason.** Responses doesn't have a per-turn timeout knob (that's a task-primitive concept).

The responses guide's prescribed pattern (handler-implementation-guide.md §Cancellation):

```python
# Default pattern: handle all three cases uniformly with the same break+complete.
if cancellation_signal.is_set():
    break

# Advanced pattern: pre-entry check; reason determines whether to emit completed or just return.
if cancellation_signal.is_set():
    if context.cancellation_reason == CancellationReason.STEERED:
        yield stream.emit_completed()
    return  # for SHUTTING_DOWN / CLIENT_CANCELLED, just return
```

**Lessons we should carry into the task primitive:**

- **A single signal + a reason enum is more ergonomic than three separate events.** The responses guide can write "check `cancellation_signal.is_set()`" once; the task primitive forces "check `cancel` OR `shutdown`" which is two checks the developer has to remember to do.
- **The reason is read-after-the-fact, not waited-on.** Developers don't `await reason`; they observe it when they observe the signal. So the natural shape is "the signal is the event; the reason is an attribute that becomes meaningful once `is_set()` is true".
- **The framework sets reason at the source.** No race: the orchestrator sets `cancellation_reason` in the same code path that sets the event, so by the time the handler reads the event, the reason is already there.

**Lessons that DON'T transfer:**

- Responses has no per-turn timeout, so the task primitive's `TIMEOUT` reason is genuinely new.
- Responses has `CLIENT_CANCELLED` because foreground HTTP disconnects are a thing. The task primitive's `TaskRun.cancel()` is the equivalent — both sets `ctx.cancel` (or its responses analogue) and let the handler choose terminal shape. Per spec 016 FR-036, the previously-existing `TaskRun.terminate()` force-fail pathway is being removed, so there's no third "force-stop" semantic to align.

---

## 5. Proposals

Four shapes ranging from "no new surface" to "full alignment with responses".

### Proposal A — Zero new public surface (status quo + recipe)

Drop FR-031 entirely. Keep `ctx.cancel` as a bare `asyncio.Event`. Keep `ctx.shutdown` as a separate bare `asyncio.Event`. Keep `ctx.pending_inputs` as it is. Educate developers via the dev guide:

```python
# Disambiguating ctx.cancel (when needed):
if ctx.cancel.is_set():
    if ctx.shutdown.is_set():
        # Shutdown wins; suspend.
        return await ctx.suspend(reason="shutting_down", output=partial)
    elif ctx.pending_inputs:
        # Steering pressure. Strategy A/B/C — your choice.
        ...
    else:
        # Timeout fired (only remaining cause if no shutdown, no pending input).
        return await ctx.suspend(reason="deadline_exceeded", output=partial)
```

**Pros:**
- No new public class.
- Uses already-modeled state.
- Symmetric with the existing `ctx.shutdown` separation — we don't have to undo that decision.

**Cons:**
- Three-way `if` is less ergonomic than `cancel.reason == X`.
- The "fall-through means timeout" inference is fragile: if a future scope adds a fourth cause (e.g., lease eviction surfacing through `ctx.cancel`), the inference silently miscategorizes it.
- Inconsistent with `ResponseContext.cancellation_reason` — developers using both surfaces have to learn two patterns.

### Proposal B — Single-enum reason, drop the separate `ctx.shutdown`, mirror responses

Add `CancelReason` enum + replace `ctx.cancel` with a `CancelSignal` wrapper. Fold `ctx.shutdown` INTO `ctx.cancel.reason` so there's only one signal.

```python
class CancelReason(str, Enum):
    STEERED = "steered"          # steering pressure (pending_inputs > 0)
    DEADLINE_EXCEEDED = "deadline_exceeded"  # @task(timeout=...) fired
    SHUTTING_DOWN = "shutting_down"          # container SIGTERM
    # Note: TERMINATED reason previously considered for manager.terminate(),
    # but that API is being removed per spec 016 FR-036. TaskRun.cancel() —
    # which would yield this reason if we kept it — is itself the explicit
    # API, so a dedicated reason value would just say "the developer called
    # the cancel API I just called" which is tautological. Omit.

class CancelSignal:
    def is_set(self) -> bool: ...
    async def wait(self) -> None: ...
    @property
    def reason(self) -> CancelReason | None: ...

# ctx.cancel becomes CancelSignal (wraps an asyncio.Event)
# ctx.shutdown is REMOVED (was an asyncio.Event; now folded into CancelSignal)
```

**Pros:**
- One signal to check (`if ctx.cancel.is_set():`).
- Reason mirrors `CancellationReason` in responses — cross-package learning.
- First-reason-wins semantics make the priority clear.

**Cons:**
- Breaking change to `ctx.shutdown` (which today is its own event some handlers may already check). Pre-release, but still — every code path that used `ctx.shutdown.is_set()` has to migrate to `ctx.cancel.reason == SHUTTING_DOWN`.
- `TERMINATED` reason was considered but dropped — `TaskRun.terminate()` is being removed per spec 016 FR-036, and `TaskRun.cancel()` (which would yield this reason) is itself the API the developer is calling. Reason redundant.
- A wrapping class adds a tiny indirection on a hot path (`ctx.cancel.is_set()`).

### Proposal C — Add reason to `ctx.cancel`, KEEP `ctx.shutdown` separate

Add `CancelReason` (no `SHUTTING_DOWN` value; only `STEERED` and `DEADLINE_EXCEEDED`). Replace bare `ctx.cancel` with a `CancelSignal`. Keep `ctx.shutdown` as today.

```python
class CancelReason(str, Enum):
    STEERED = "steered"
    DEADLINE_EXCEEDED = "deadline_exceeded"

class CancelSignal:
    def is_set(self) -> bool: ...
    async def wait(self) -> None: ...
    @property
    def reason(self) -> CancelReason | None: ...

# ctx.cancel  : CancelSignal  (was asyncio.Event)
# ctx.shutdown: asyncio.Event (unchanged)
```

Developer pattern:

```python
if ctx.shutdown.is_set():
    return await ctx.suspend(reason="shutting_down", output=partial)
if ctx.cancel.is_set():
    if ctx.cancel.reason == CancelReason.STEERED:
        # Strategy A/B/C
        ...
    else:  # DEADLINE_EXCEEDED
        return await ctx.suspend(reason="deadline_exceeded", output=partial)
```

**Pros:**
- Adds reason for the case it's actually needed (steering vs timeout).
- Keeps `ctx.shutdown` separate — preserves the existing model.
- The enum is small (2 values), reflecting reality (the two things that set `ctx.cancel`).

**Cons:**
- Still adds a public class (`CancelSignal`) and an enum.
- Asymmetric with responses — responses bundles shutdown into the enum; task primitive doesn't. Cross-package developers might find this confusing.

### Proposal D — No CancelSignal, just `ctx.cancel_reason` directly on TaskContext

Add a single property `ctx.cancel_reason: Literal[...] | None` directly on `TaskContext`. Keep `ctx.cancel` as a bare `asyncio.Event`. Keep `ctx.shutdown` as today.

```python
# ctx.cancel        : asyncio.Event             (unchanged)
# ctx.shutdown      : asyncio.Event             (unchanged)
# ctx.cancel_reason : Literal["steered", "deadline_exceeded"] | None  (NEW; None when cancel is unset)
```

Developer pattern: identical to Proposal C, except the reason lives on `ctx` directly:

```python
if ctx.shutdown.is_set():
    ...
if ctx.cancel.is_set():
    if ctx.cancel_reason == "steered":
        ...
    elif ctx.cancel_reason == "deadline_exceeded":
        ...
```

**Pros:**
- No new public CLASS (no `CancelSignal`); just one new property on existing `TaskContext`.
- Smallest diff to public surface.
- Backward-compatible with `ctx.cancel.is_set()` patterns (they still work — no wrapping).

**Cons:**
- The reason is logically tied to the event but lives on a separate attribute — slightly less discoverable than `ctx.cancel.reason`.
- A `Literal` is less self-documenting than an `Enum` (no class to import / introspect / pattern-match on). Could use a `str Enum` instead; same idea.
- Same shutdown-asymmetry as Proposal C.

### Proposal E — Independent boolean property per cause (preferred per user direction 2026-06-01)

Drop the "single reason value" framing entirely. Each independent cause that can set `ctx.cancel` gets its own boolean property on `TaskContext`, set when the cause fires, never unset. `ctx.cancel` remains the composite "stop" signal that fires when ANY cause fires. `ctx.shutdown` remains separate (per user direction: shutdown is a distinct concern that requires a different handler action — `ctx.exit_for_recovery()` per FR-037 — and is optional to implement).

```python
# ctx.cancel              : asyncio.Event   (composite; set by ANY of the causes below)
# ctx.shutdown            : asyncio.Event   (separate concern, unchanged)
# ctx.pending_inputs      : Sequence        (already exists; len > 0 ⇒ steering pressure)
#
# NEW boolean properties (read-only from handler perspective; framework-set):
# ctx.timeout_exceeded    : bool            True iff the timeout watchdog fired
# ctx.cancel_requested    : bool            True iff TaskRun.cancel() was called externally
```

Note: steering is NOT a new boolean — `len(ctx.pending_inputs) > 0` already encodes it precisely. Adding a `ctx.steered` boolean would duplicate state.

Developer pattern:

```python
# Composite "should I stop?" — the simplest path, covers the majority case.
if ctx.cancel.is_set():
    await ctx.metadata.flush()
    return await ctx.suspend(output=partial)

# Advanced: branch on independent causes, including the COMPOSITE case
# where multiple causes have fired in sequence:
if ctx.cancel_requested:
    # External cancel takes priority — operator explicitly asked us to stop.
    # Often the handler wants to commit current work and exit.
    ...
if ctx.timeout_exceeded:
    # Deadline blown — handler may want to mark output as partial / log differently.
    ...
if ctx.pending_inputs:
    # Steering input queued — handler may want to wind down quickly to yield turn.
    ...

# Shutdown is checked separately (per user direction: distinct concern, optional):
if ctx.shutdown.is_set():
    await ctx.metadata.flush()
    return await ctx.exit_for_recovery()
```

**Pros:**
- **Composite cases compose naturally** — a handler that experiences steering → then timeout → then explicit cancel sees ALL THREE booleans `True` at the final checkpoint. No information lost. The user's concern about stacking causes is solved by construction.
- **Independent**: each cause can be queried independently. No "first-reason-wins" race semantics to reason about.
- **No new wrapping class** — bare `asyncio.Event` for `ctx.cancel` (and `ctx.shutdown`) preserved; just two new `bool` properties on `TaskContext`.
- **Backward-compatible** — every existing `ctx.cancel.is_set()` / `ctx.cancel.wait()` pattern works unchanged.
- **No enum to maintain** — adding a new cause is a new boolean (one line in `__slots__` + one assignment site), not an enum value plus migration.
- **Mirrors the established convention** — `ctx.was_steered` is already a boolean on `TaskContext` (for "this entry was a drain re-entry"). The new booleans extend that pattern.

**Cons:**
- More public surface than Proposal D (two boolean properties vs one Literal). Marginal.
- Slightly more verbose for handlers that DO want to discriminate (`if ctx.timeout_exceeded:` vs `if ctx.cancel_reason == "timeout":`). Trade-off for composite-case clarity.
- Could grow if many future causes are added. Mitigated by the fact that the causes are bounded by physical reality — there are only so many things that legitimately stop a task.

---

## 6. Tradeoff matrix

| Concern | A (status quo) | B (single enum) | C (reason, keep shutdown) | D (cancel_reason on ctx) | **E (separate booleans)** |
|---|---|---|---|---|---|
| New public class | None | `CancelSignal` + `CancelReason` | `CancelSignal` + `CancelReason` | Just `Literal`/Enum (no class) | **None** |
| New public attributes | 0 | 1 (class replaces event) | 1 (class replaces event) | 1 (Literal) | **2 (`timeout_exceeded`, `cancel_requested`)** |
| Handler ergonomics for "why was I cancelled" | Three-way `if` | `cancel.reason ==` | `cancel.reason ==` + `shutdown.is_set()` | `cancel_reason ==` + `shutdown.is_set()` | **Independent `if` per cause; composite-friendly** |
| **Composite cases (steering → timeout → cancel all stacked)** | Inferable but fragile | First-reason-wins; info lost | First-reason-wins; info lost | First-reason-wins; info lost | **All booleans True; full fidelity** |
| Mirrors responses-package guidance | No | Yes (closest) | Partial | Partial | No (different shape) |
| Breaks existing `ctx.shutdown` consumers | No | YES (removes it) | No | No | **No** |
| Breaks `ctx.cancel.is_set()` / `.wait()` patterns | No | No (wrapper preserves) | No (wrapper preserves) | No | **No** |
| Future-proof if a 4th cancel source appears | Fragile (fall-through breaks) | Add enum value | Add enum value | Add enum value | **Add boolean** |
| Test/spec churn | Lowest | Highest | Medium | Lowest among "add reason" options | **Low (2 attrs + assignment sites)** |

---

## 7. Recommendation (locked in per user direction 2026-06-01)

**Proposal E — Independent boolean property per cause.** User direction (three decisions):

1. **`ctx.shutdown` stays separate** — different concern, requires different handler action (`ctx.exit_for_recovery()` per FR-037), optional to implement. Folding it into a cancel reason (Proposal B) would re-introduce the "two checks for one concept" confusion.
2. **Timeout and `TaskRun.cancel()` MUST be distinguishable by the handler.** This rules out Proposal A (relies on fall-through inference).
3. **Composite cases are real and information must not be lost.** Multiple causes can stack across the handler's execution (steering → timeout → explicit cancel). A handler may want to react ONCE at the final checkpoint but with full visibility into which causes fired. This rules out first-reason-wins (Proposals B/C/D) and points squarely at separate booleans.

### Open questions — resolved per user direction

1. **`TaskRun.cancel()` distinguishability:** YES — surfaces as `ctx.cancel_requested = True`. No enum value needed.
2. **`SHUTTING_DOWN` in the cancel-reason enum:** N/A — no cancel-reason enum exists in Proposal E. Shutdown is `ctx.shutdown`, distinct as decided.
3. **First-reason-wins:** N/A — booleans accumulate. Every cause that fires sets its own boolean True; nothing is overwritten.
4. **Readable before `ctx.cancel.is_set()` is true:** booleans default to `False` at handler entry. They flip to `True` at the moment the corresponding framework subsystem fires the cause (watchdog sets `timeout_exceeded`; cancel call sets `cancel_requested`). They never flip back.
5. **Naming:**
   - `ctx.timeout_exceeded: bool` — the deadline configured via `@task(timeout=...)` was reached.
   - `ctx.cancel_requested: bool` — an external caller invoked `TaskRun.cancel()`. Naming chosen for symmetry with the existing internal "cancel_requested" steering flag, but here it's the *external* one. If confusion is a risk, alternatives: `cancelled_by_caller`, `was_cancelled_externally`, `external_cancel`. Recommend `cancel_requested` for brevity unless reviewer feedback prefers an alternative.

---

## 8. What changes in spec 016 (Proposal E locked in)

The following spec edits will land in a single follow-up commit:

- **Rewrite FR-031**: title becomes "Independent boolean properties for cancel causes". Defines `ctx.timeout_exceeded: bool` and `ctx.cancel_requested: bool` on `TaskContext`. Both default `False` at handler entry; framework subsystems set them at the moment the cause fires; they never flip back. Drop all references to `CancelSignal` class and `CancelReason` enum — `ctx.cancel` stays a bare `asyncio.Event`.
- **Rewrite FR-033**: title becomes "Set independent booleans at the source". `_timeout_watchdog` sets `ctx.timeout_exceeded = True` then `ctx.cancel.set()`. `TaskRun.cancel()` sets `ctx.cancel_requested = True` then `ctx.cancel.set()`. `_try_drain_steering` does NOT set a new boolean (steering pressure is already encoded by `len(ctx.pending_inputs) > 0`); it just sets `ctx.cancel.set()` as today. Crash-recovery zero-budget case (FR-032's `remaining == 0` path) pre-sets `ctx.timeout_exceeded = True` and `ctx.cancel.set()` so the recovered handler sees both from the first checkpoint.
- **Rewrite SC-016**: title becomes "Independent cause booleans visible to handler". Parametrized sweep covers (a) timeout-only — `timeout_exceeded=True`, `cancel_requested=False`, `pending_inputs=()`; (b) external-cancel-only — `timeout_exceeded=False`, `cancel_requested=True`, `pending_inputs=()`; (c) steering-only — `timeout_exceeded=False`, `cancel_requested=False`, `pending_inputs` non-empty; (d) composite (all three fire in sequence) — all three booleans observable as True at the final checkpoint; (e) backward-compat — existing `ctx.cancel.is_set()` / `await ctx.cancel.wait()` patterns continue to work unchanged.
- **Update `TaskContext` Key Entity** (currently lists `CancelSignal`): remove `CancelSignal` entry, add `timeout_exceeded` and `cancel_requested` to the field table.
- **Update Principle XII checklist**: remove `CancelSignal` and `TaskContext.cancel type change` from affected-symbols list; add `TaskContext.timeout_exceeded` and `TaskContext.cancel_requested` as new additive properties. `ctx.cancel` remains bare `asyncio.Event` — NOT a public-surface change.
- **Update "What goes where" table**: rewrite the `ctx.cancel` row to describe independent booleans + composite-case handling; cross-reference FR-037's `ctx.exit_for_recovery()` for the shutdown branch.
- **Dev guide updates** (per FR-031's Docs↔Samples sequence): rewrite §4 Steering's cancel-disambiguation paragraph around independent booleans, with a composite-case worked example showing all three booleans True at a final checkpoint.

Either the spec edits land in one cohesive commit, or alongside the FR-031..FR-037 cohesive `_execute_task_loop`/drain rewrite implementation PR per the existing implementation-order proposal in plan.md.

The other FRs in the cancel-signal cluster (FR-032 per-turn watchdog respawn, FR-034 docstring correction, FR-035 durable `_turn_started_at`, FR-036 terminate removal, FR-037 `ctx.exit_for_recovery`) are unaffected — they don't depend on the reason-surface shape.
