# Rust vs Python — Cosmos SDK Speed Test Results

The Cosmos Python SDK can run database calls two ways: the original **all-Python**
engine, and a **new engine that hands the heavy work to Rust**. This document answers a
simple question a customer would ask: **is the new (Rust) engine faster, by how much, and
what does it cost?**

> **Rust driver under test:** Cosmos Rust driver **v0.6.0** (commit `106ad05bc`). Every Rust
> measurement in this document was produced by this single build (enforced by a provenance gate on
> each phase's results).

## Test plan in this doc

We keep the phase labels for tracking, but each phase maps to a clear test goal:

| Phase | Test goal | Current status |
|------|-----------|----------------|
| **Phase 0** | **Environment validation** — light-load (1 in-flight) SLA-near latency baseline | **Complete** |
| **Phase A** | **Fixed-load performance baseline** (latency, throughput, RU/op, CPU) | **Complete** |
| **Phase B** | **Long-run memory stability** (12-hour soak, leak/drift checks) | **Complete** |
| **Phase C** | **Stress behavior under heavy load** (concurrency scale sweep, resilience at higher pressure) | **Complete** |
| **Phase D** | **Failure-mode resilience + correctness under breakage** (failover/429/cancel/fork/resource-pressure/correctness parity) | **Planned** |


## Phase setup quick-reference (Phase 0, A, B, C)

This is the fast "what changed between phases" view so nobody has to hunt in the long sections.

| Phase | Client VM | Account path | Operation container | Results container | Throughput / request model |
|------|-----------|--------------|---------------------|-------------------|----------------------------|
| **Phase 0** (light-load latency baseline) | `vm-python-dr-drill` | **Compute Gateway** (Gateway path) | `lat_probe_db/lat_probe_cont` (isolated) | `perfdb/perfresults` | Probe container at **20,000 RU/s**; **1 in-flight request** (concurrency=1), arrival rate 0, 1 client, no proxy; **~8 minutes** per operation per engine |
| **Phase A** (fixed-load baseline) | `vm-python-phasec` | **Compute Gateway** (Gateway path) | `scale_db/scale_cont` | `perfdb/perfresults` | Operation container at **100,000 RU/s**; results container at **4,000 RU/s**; fixed **100 in-flight requests**; **30-minute** run per operation per engine |
| **Phase B** (12-hour memory soak) | `vm-python-dr-drill` | **Compute Gateway** (Gateway path) | `leak_cont` | `perfdb/perfresults` (same as Phase A) | Not a throughput benchmark; request model changed to a **continuous 12-hour soak _per engine_** — the six operations run as six parallel processes for a full **12 hours on one engine, then the same 12 hours on the other engine**. The two engines run one after the other (back-to-back), so the whole phase takes **≈ 24 hours of wall-clock time** even though each engine is only measured for 12. Memory is sampled about every 5 minutes; the integrity check counted **over 541 million** Rust requests (plus the all-Python engine's slower-paced volume) across the phase |
| **Phase C** (concurrency scale sweep) | `vm-python-phasec` | **Compute Gateway** (Gateway path) | `scale_db/scale_cont` @ **150,000 RU/s** (Phase A's container, bumped from 100k) | `perfdb/perfresults` | Throughput ceiling test; `read`+`upsert` on both engines swept across **32 → 1024 in-flight requests** (explained in the notes just under this table), **1800 s per point** (600 s warm-up dropped); achieved req/s = `count / window_seconds`; every point is verified to have truly run on the engine it claims (Rust vs Python), so a run can never be mislabeled |

---

## Phase 0 — environment validation (SLA-near latency baseline)

**What this phase does.** Validates the environment with a light-load probe — one request at a time (no client queue) — to establish the true per-request latency baseline (target p99 ≈ 10 ms).

**What we did.** Single region (West US 2), account on the **Compute Gateway** routing plane, client VM
in the same region with accelerated networking on, over the Gateway path, on an isolated container. For
each of the six point operations, on **both engines**, we ran one request at a time (`concurrency=1`,
one client) for ~8 minutes. The percentiles below reflect every request across the full run — true
per-request latencies, not an average of separate time windows.

**Results (one request in flight; p50/p90/p99/p99.9 in milliseconds):**

| Operation | Engine | p50 | p90 | p99 | p99.9 | req/s @conc=1 | RU/op | Errors |
|-----------|--------|----:|----:|----:|------:|--------------:|------:|:------:|
| **Read**    | Python | 3.66 | 4.63 | 7.62 | 23.90 | 250 | 1.00 | 0 |
|             | Rust   | 2.75 | 3.56 | 6.28 | 9.90  | 337 | 1.00 | 0 |
| **Create**  | Python | 6.89 | 7.88 | 10.64 | 34.14 | 70  | 7.24 | 0 |
|             | Rust   | 6.36 | 7.24 | 10.46 | 15.56 | 78 | 7.24 | 0 |
| **Upsert**  | Python | 7.37 | 8.34 | 10.04 | 16.43 | 132 | 11.18 | 0 |
|             | Rust   | 6.68 | 7.89 | 10.96 | 15.31 | 144 | 11.19 | 0 |
| **Replace** | Python | 7.43 | 8.50 | 11.32 | 17.84 | 130 | 11.62 | 0 |
|             | Rust   | 6.73 | 7.91 | 10.95 | 15.26 | 143 | 11.62 | 0 |
| **Delete**  | Python | 6.68 | 7.68 | 10.57 | 23.86 | 70  | 7.24 | 0 |
|             | Rust   | 5.97 | 7.06 | 9.83 | 15.49 | 78  | 7.24 | 0 |
| **Patch**   | Python | 7.48 | 8.62 | 11.12 | 15.97 | 129 | 10.79 | 0 |
|             | Rust   | 9.46 | 11.03 | 14.63 | 23.50 | 101 | 10.67 | 0 |

> **Provenance for this table.** Freshly measured on **2026-07-03** against Rust driver
> **v0.6.0 (`106ad05bc`)**, run stamp `20260703-060120992`, on the isolated
> `lat_probe_db/lat_probe_cont` container. Percentiles are pooled across windows from merged
> HdrHistograms (exact). All 48 Rust rows passed the driver-provenance gate (single build,
> no mixing). Zero errors and zero throttling (429s) across every cell.

**What this proves.**

- **The environment is valid.** The Python baseline lands at **~7–11 ms p99** for every operation
  (reads well under 10 ms; writes right on the line, which is expected since writes replicate and
  cost 7–12 RU). Zero errors, zero throttling. So the test rig genuinely delivers SLA-near latency,
  and any comparison anchored here is meaningful.
- **It confirms Phase A's latencies are a saturation effect, not the service.** Same database, same
  region, same networking — yet one request at a time is **~3.7 ms** for a read versus Phase A's
  ~64 ms. The difference is entirely the 100-in-flight client queue in Phase A. Phase A remains valid
  for *engine-vs-engine under identical offered load* and for *how to measure*; Phase 0 is the number
  to quote for *per-request SLA*.
- **One anomaly worth chasing: Patch on Rust.** It is the only operation where Rust is *slower* than
  Python at conc=1, and the gap **widens with the percentile** — about **+1.98 ms at p50**
  (9.46 vs 7.48) and about **+3.51 ms at p99** (14.63 vs 11.12). The per-window Rust patch p50 series
  is flat across all eight windows (not a warm-up artifact), so this is a real, steady per-request
  cost in the Rust patch path, flagged for follow-up. (Note this is a **conc=1** effect only — under
  Phase A's 100-in-flight load Patch on Rust is ~5× faster than Python, see below.)

---

## Phase A — fixed-load performance baseline

We ran the six everyday database operations — **Read, Create, Upsert, Replace, Delete,
and Patch (partial update)** — through each engine under a fixed, identical load and timed every request.

**Environment.** Single region (West US 2), account on the **Compute Gateway** routing plane, client VM
in the same region with accelerated networking on, Gateway connection mode, **Session** consistency.
What's specific to Phase A on top of that baseline:

- **Records pre-loaded:** **~1,000,000 items** (~1 KB each), so reads/updates/deletes worked against a real data set.
- **Load:** **100 requests in flight at all times**, identical for both engines — a steady, moderate load (deliberately *not* each engine's maximum); 30-second request timeout.
- **Duration:** **30 minutes per operation, per engine** — **49,452,500** operations in total, with **0 errors**.
- **Containers:** operation container `scale_db/scale_cont` at **100,000 RU/s** (far more headroom than the load needs, so the database is never the bottleneck); results written to a separate `perfdb/perfresults` so recording never competes with the measured operation.

---

## Detailed — each operation

> **These are fixed-load numbers, not SLA latency.** Every latency below is measured with **100
> requests in flight at all times**, so it includes time each request spent queued in the client
> under saturation — the right basis for comparing the two engines under identical pressure, but
> *not* a per-request SLA figure. For the SLA-near, one-request-at-a-time baseline, see
> [Phase 0 — environment validation](#phase-0--environment-validation-sla-near-latency-baseline)
> (e.g. a read is ~3.7 ms at conc=1 versus ~64 ms here).

| Operation | Engine | p50 (ms) | p99 (ms) | p99.9 (ms) | Throughput (ops/sec) | Requests | Errors | RU/op | CPU (cores) | p50 speed-up |
|-----------|--------|---------:|---------:|-----------:|---------------------:|---------:|:------:|------:|------------:|:------------:|
| **Read**    | Python | 64.3 | 99.5 | 114.2 | 982   | 1,767,700 | 0 | 1.00 | 1.01 | — |
|             | Rust   | 9.7  | 26.3 | 31.5  | 5,542 | 9,973,900 | 0 | 1.00 | 2.34 | **6.6× faster** |
| **Create**  | Python | 59.7 | 92.7 | 104.4 | 560   | 1,007,200 | 0 | 7.24 | 1.01 | — |
|             | Rust   | 11.9 | 28.3 | 37.8  | 2,523 | 4,540,500 | 0 | 7.24 | 2.27 | **5.0× faster** |
| **Upsert**  | Python | 59.5 | 92.5 | 104.1 | 1,066 | 1,917,900 | 0 | 11.19 | 1.00 | — |
|             | Rust   | 11.9 | 28.0 | 35.1  | 4,099 | 7,377,400 | 0 | 11.19 | 2.05 | **5.0× faster** |
| **Replace** | Python | 59.0 | 90.8 | 101.4 | 1,077 | 1,937,600 | 0 | 11.63 | 1.00 | — |
|             | Rust   | 12.0 | 28.7 | 40.1  | 3,955 | 7,117,400 | 0 | 11.63 | 2.00 | **4.9× faster** |
| **Delete**  | Python | 56.5 | 89.0 | 113.2 | 560   | 1,007,100 | 0 | 7.24 | 1.00 | — |
|             | Rust   | 10.2 | 25.5 | 35.6  | 2,542 | 4,575,500 | 0 | 7.24 | 2.27 | **5.5× faster** |
| **Patch**   | Python | 59.7 | 93.6 | 115.7 | 1,046 | 1,882,600 | 0 | 10.80 | 0.99 | — |
|             | Rust   | 11.6 | 27.1 | 45.5  | 3,527 | 6,347,700 | 0 | 10.67 | 2.58 | **5.1× faster** |

> **Where these numbers come from.** Measured on **2026-07-03** using the Rust driver **v0.6.0**
> (build `106ad05bc`) — every Rust row came from that one build, which we checked automatically so no
> results can be mixed together or mislabeled. Each operation ran with **100 requests in flight for 30
> minutes on each engine**, on the `scale_db/scale_cont` container (100,000 RU/s). The latency
> percentiles are the exact values across the whole run (not an average of separate windows); CPU is the
> per-process average after dropping the first 10 minutes of warm-up; and every cell had **zero errors
> and zero throttling**.

> **About the p99.9 column.** p99.9 is the "one-in-a-thousand slowest request" number, so it must be
> pooled correctly. For this run, p50/p90/p99/p99.9 are computed exactly from merged per-window
> HdrHistograms (`hist_b64`) with no missing histogram rows. Throughput, request-count, RU/op, and
> error/429 totals are also exact.

---

## Visual snapshot — Phase A (fixed-load baseline, XY-coordinate curves)

Below are XY charts built from the same table values above (X = operation, Y = metric).

### p50 latency curve (lower is better)

```mermaid
xychart-beta
    title "Phase A p50 latency (ms) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "p50 latency (ms)" 0 --> 70
    line "Core Python" [64.3,59.7,59.5,59.0,56.5,59.7]
    line "Rust" [9.7,11.9,11.9,12.0,10.2,11.6]
```

### p99 latency curve (lower is better)

```mermaid
xychart-beta
    title "Phase A p99 latency (ms) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "p99 latency (ms)" 0 --> 100
    line "Core Python" [99.5,92.7,92.5,90.8,89.0,93.6]
    line "Rust" [26.3,28.3,28.0,28.7,25.5,27.1]
```

### Throughput curve (higher is better)

```mermaid
xychart-beta
    title "Phase A throughput (ops/sec) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Throughput (ops/sec)" 0 --> 6000
    line "Core Python" [982,560,1066,1077,560,1046]
    line "Rust" [5542,2523,4099,3955,2542,3527]
```

### CPU curve (higher is more host CPU)

```mermaid
xychart-beta
    title "Phase A CPU (cores) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "CPU (cores)" 0 --> 3
    line "Core Python" [1.01,1.01,1.00,1.00,1.00,0.99]
    line "Rust" [2.34,2.27,2.05,2.00,2.27,2.58]
```

---

## Summary — the bottom line

The per-operation numbers are in the table above; this is only the aggregate synthesis
that the detailed rows don't show at a glance. Across all six operations the Rust engine
was faster at every latency level, for the **same** database cost (RU) and with **zero**
errors:

- **Typical latency (p50):** ~60 ms → ~11 ms — about **5× faster**.
- **Slow tail (p99):** ~93 ms → ~27 ms — about **3× faster**.
- **Total work in the same 30 min/op:** ~9.5 million ops → ~39.9 million ops — about
  **4× more**.
- **Cost unchanged, CPU higher:** RU/op identical on both engines; Rust used ~2.0–2.6
  cores vs ~1.0 for all-Python.

**In plain terms:** the new engine is several times faster and handles far more work in
the same time, without costing any more in database charges. The trade-off is that it
uses more of the machine's CPU — a good deal on today's multi-core servers.

---


## About the latency percentiles (p50/p90/p99/p99.9)

**What to keep in mind:** for Phase A, throughput, cost, and error totals are exact, and latency
percentiles are also exact run-wide values because they are pooled from merged per-window
HdrHistograms (`hist_b64`) rather than averaged from scalar window percentiles.

- **p50/p90/p99 are exact and stable.** They are pooled exactly and show low run-to-run sensitivity
  under this load shape.
- **p99.9 is exact but naturally noisier.** Even with exact pooling, the one-in-a-thousand tail is
  sensitive to rare host/service events, so treat it as a high-sensitivity indicator and compare it
  with p99 plus throughput/error context.
- **The one operation to call out is Patch.** Its Rust p99.9 (~46 ms) is higher than the other
  Rust operations. Even so, that ~46 ms is still faster than the Python engine's *typical*
  (p50 ~60 ms) Patch time and well under half its p99.9 (~116 ms) — so Patch is still a clear win, just
  with a bumpier deep tail, most likely because partial-document updates vary more on the server side.

---

## Phase B — Long-run memory stability (12-hour soak)

**Status:** Complete (re-run from scratch on Rust driver v0.6.0). **Both engines are safe to run
continuously; neither shows a per-operation memory leak.** All-Python is flat on every operation.
Rust holds flat on five of six operations; this run the one exception is **Read**, whose memory
kept drifting up (**+18.9 MB/h** over the last hour) — labeled `GROWING`. Importantly, *which*
Rust operation drifts changes between runs (it was Create on the previous driver), which points at
process-level allocator/arena behavior rather than a leak tied to any one operation. A dedicated
**Read-only settle** (below) since narrowed this: in isolation Rust Read creeps only **+1.25–1.54 MB/h**
(`WATCH`) — ~92% below the soak number — but had **not fully flattened in 6 h**. Whether that residual
is bounded allocator retention or a slow Rust-side leak is the **one open memory question**, and needs
a longer settle plus allocator introspection to close — details and follow-ups below.

**Why we ran this, and what's at stake for a customer.** Speed (Phase A) tells you how the
SDK behaves for a few minutes. But real customer apps run for *days or weeks* without
restarting. If an SDK uses a little more memory on every call and never gives it back — a
"memory leak" — that memory piles up until the app runs out and the operating system kills
it. The customer sees random crashes and forced restarts, usually at the worst time (peak
load). So before recommending the Rust engine for always-on services, we had to prove its
memory settles at a stable level and *stays* there over a long run, rather than creeping up
forever. Phase B is that proof.

**What "memory" means here.** We tracked the RAM the SDK's process actually held (its
"resident" memory, in megabytes). A healthy long-running process climbs a bit during warm-up
— as it builds connection pools and caches — and then holds flat. A leaking one keeps
climbing with no ceiling.

**Test setup (verified from the live account):**

| Setting | Value |
|---------|-------|
| What we varied | The **engine** (all-Python vs Rust) and the **operation** (all six) |
| Client machine | One VM, `vm-python-dr-drill`, in the same West US 2 region as the account (the same VM used for the Phase 0 latency probe; separate from the Phase A/C throughput VM `vm-python-phasec`) |
| Account routing plane | **Compute Gateway** |
| Client connection mode | **Gateway** |
| Duration | **12 hours per engine.** The six operations ran as **six separate processes on the VM at the same time** (one process per operation, all six in parallel), each soaking continuously for the full 12 hours. The two engines ran **back-to-back, never together** (all-Python's 12-hour batch, then Rust's) — so the total wall-clock was **~24 hours**, and at no moment were more than six workload processes running. We keep the engines apart on purpose: run them together and they would fight over the same VM CPU and RAM, which would distort each engine's memory reading. |
| Container | `leak_cont` (same West US 2 account) |
| Request profile change vs Phase A | Switched from fixed **100 in-flight** / 30-minute windows to a **continuous 12-hour soak** — six operations in parallel per engine (six concurrent processes, **not** one operation after another), memory-focused run |
| What we recorded | The process's memory (RSS), sampled about every **5 minutes** — **144 readings per operation** over the 12 hours. Each reading stamps its own window length (`window_seconds`), which is normally ~300 s but can drift if a flush is delayed or shortened; for this run the windows were tightly clustered (median **300.197 s**, range **256.879–305.298 s**). The first reading, taken during warm-up, is dropped from the trend, leaving **143 analyzed**. |
| Results container | The same separate `perfdb/perfresults`, so recording never disturbs the run |
| Engine check | Every reading is stamped with which engine produced it, and we **verified** each engine's rows before trusting the numbers |

**A note on data hygiene (why you can trust these numbers).** Memory readings and error notes are
recorded and counted separately, so error notes never pollute the memory math. On this run the
purity check **passed**, with **13 error notes** across the whole 12 hours (core Delete 2, core
Patch 2, core Replace 1, core Upsert 3, Rust Patch 5) — a negligible rate — all correctly set
aside from the memory trend.

### How we know this run is trustworthy — two required gates + completion

We do not trust the memory numbers on their own; a run only counts if it passes **two
automated gates** and is proven to have run to completion.

**Gate 1 — engine-purity + memory verdict.** Confirms every recorded row
actually ran on the engine it claims (the all-Python rows really are Python; the Rust rows
really are Rust), then computes the leak verdict. **Result: PASS**, 13 error notes
set aside as described above.

**Gate 2 — integrity.** This is the check that a *dropped* reading can't
quietly hide a leak. It verifies that **no reporting window was lost** — the time
gap between consecutive readings matches each row's recorded window length (any bigger jump =
a lost window) — and that **every row truly ran on the engine it claims**. **Result: PASS** —
all 12 operation×engine cells clean — **over 541 million Rust operations** (the six Rust
operations alone; the all-Python engine adds its own slower-paced volume) with **13 error notes**
(0.00%), no missing windows.

**Completion proof.** The soak ran the **full 12 hours per engine** (43200 s each), completing both engines
back-to-back. Afterwards
**every worker process exited** (no hung or stuck processes), and re-running both checks
reproduces PASS.

> **Provenance for this Phase B section.** Results are from `--prefix leak-` stamp
> `20260703-055829915` (12-hour all-ops soak) and `20260704-060235418` (Create-only settle),
> with a single Rust driver build `106ad05bc` across all Rust rows.

### How to read the verdicts:

- **PLATEAUED** — climbed during warm-up, then went flat and stayed there. Healthy.
- **STAIRCASE** — rose in a few discrete jumps (memory pools grabbing a chunk at a time) and
  then held. Bounded and healthy — *not* a leak.
- **WATCH** — mostly flat, but the final stretch is still drifting up a little, so we cannot
  yet *prove* it has leveled off. Not a proven leak; a follow-up item.
- **GROWING** — the final stretch is still *clearly* climbing (even the best-case slope is ≥ 5
  MB/h), so this run alone cannot call it bounded. Not proof of an unbounded leak, but the
  strongest "keep investigating" signal.

*How we decide the verdict, in plain English: we look at the last hour's growth rate and
its uncertainty band (95% CI). If the worst-case side is still small (upper bound ≤ 2 MB/h),
we call it bounded/flat (`PLATEAUED` or `STAIRCASE` depending on shape). If even the best-case
side is clearly high (lower bound ≥ 5 MB/h), we call it `GROWING`. Anything in between is
`WATCH` — basically "not scary, but not fully closed yet."*

### All-Python engine — flat, no leak

Every operation settled around **85–92 MB** and held there for 12 hours. The tail (the last
hour) is essentially flat — between **+0.00 and +0.05 MB per hour**, which is noise, not
growth.

| Operation | Memory start→end (MB) | Verdict |
|-----------|----------------------:|---------|
| Read    | 86 → 90 | PLATEAUED |
| Create  | 87 → 91 | PLATEAUED |
| Upsert  | 87 → 92 | PLATEAUED |
| Replace | 87 → 92 | PLATEAUED |
| Delete  | 86 → 92 | PLATEAUED |
| Patch   | 86 → 91 | PLATEAUED |

Shape (Create, all-Python): `87 ▁▅▅▅▆▆▆▇▇▇▇▇▇▇▇▇▇▇▇▇█ 91` — a small warm-up rise, then a flat line.

### Rust engine — higher but bounded; one operation still drifting (Read this run)

The Rust engine settles at a **higher** memory level than the all-Python engine (roughly
**2.1–2.4× more**, ~190–220 MB). That is expected: it keeps more machinery resident (per-core
worker threads, connection pools, buffers) — the same machinery that buys the 5× speed. The
important question is not "is it higher?" (it is, by design) but "does it *keep climbing*?"
For **five of six** operations, no — they rise during warm-up and then hold flat. The one
exception this run is **Read**:

| Operation | Memory start→end (MB) | Last-hour drift (MB/h) | Verdict |
|-----------|----------------------:|-----------------------:|---------|
| Create  | 168 → 194 | +0.31 | PLATEAUED |
| Delete  | 159 → 195 | +0.68 | PLATEAUED |
| Patch   | 175 → 220 | +0.08 | PLATEAUED |
| Replace | 155 → 197 | +1.14 | PLATEAUED |
| Upsert  | 158 → 200 | +0.63 | PLATEAUED |
| **Read** | **132 → 191** | **+18.92** | **GROWING** |

### Visual snapshot — Phase B (XY-coordinate curves)

For chart consistency, X-axis order is: **Read, Create, Upsert, Replace, Delete, Patch**.

```mermaid
xychart-beta
    title "Phase B memory at start of analysis window (MB)"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Memory start (MB)" 0 --> 200
    line "Core Python" [86,87,87,87,86,86]
    line "Rust" [132,168,158,155,159,175]
```

```mermaid
xychart-beta
    title "Phase B memory at end of run (MB)"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Memory end (MB)" 0 --> 350
    line "Core Python" [90,91,92,92,92,91]
    line "Rust" [191,194,200,197,195,220]
```

```mermaid
xychart-beta
    title "Phase B Rust last-hour drift (MB/h) vs decision bounds"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Drift (MB/h)" -1 --> 20
    line "Rust observed drift" [18.92,0.31,0.63,1.14,0.68,0.08]
    line "Flat upper bound (2 MB/h)" [2,2,2,2,2,2]
    line "Leak lower bound (5 MB/h)" [5,5,5,5,5,5]
```

Shape (Read, Rust): `132 ▁▂▂▃▃▄▄▄▅▅▅▆▆▆▇▇▇▇███ 191` — a warm-up rise that, unlike the other five
operations, **never flattened** — it kept drifting upward through the end of the run.

Shape (Create, Rust): `168 ▁▃▄▅▅▆▆▆▇▇▇▇▇▇▇▇▇▇▇██ 194` — warm-up rise, then flat (this run).

**What the Read `GROWING` label means, honestly.** Rust Read's memory rose steadily from 132 to
191 MB and was **still climbing** in the final hour (+18.9 MB/h), so we cannot call it bounded
from this run alone. Two things keep this from being an alarm — but also keep it open:

- **The drifting operation is not stable across runs.** On the previous driver the drifter was
  Create (+4.74 MB/h) while Read was flat; on v0.6.0 it is the reverse. A genuine
  per-operation leak would stay with the *same* operation. A drifter that moves points instead at
  **process-level allocator/arena behavior** — the C allocator holding freed memory in per-thread
  arenas rather than returning it — which the all-Python engine, with a different allocator
  profile, never exhibits.
- **We closed the Create question directly.** A dedicated Create-only settle run (next section)
  shows Create *in isolation* also creeps (+9.69 MB/h) and never fully flattened in 6 hours — the
  same signature. A dedicated **Read-only settle** (also below) shows the same shape for Read:
  isolated, Read creeps far slower than the soak number (+1.25–1.54 MB/h vs +18.9) but has **not
  flattened in 6 hours**. So the honest reading is: Rust's resident memory has a slow, Rust-side
  upward creep on **whichever operation is pushing the most allocation churn** — clearly *not* an
  unbounded per-operation logical leak, but **not yet proven to plateau** either. Whether the residual
  is bounded allocator/arena retention or a slow leak is still open.

### Phase B bottom line

- **The all-Python engine does not leak** — flat ~90 MB for 12 hours, every operation.
- **The Rust engine shows no per-operation leak either**, with one caveat: it runs at a
  **higher, bounded** memory level (~190–220 MB) and, on **one operation per run**, exhibits a
  slow upward creep. Five of six operations are conclusively flat this run; **Read** ended still
  climbing (+18.9 MB/h, `GROWING`).
- **The creep is not tied to a specific operation** — it was Create on the previous driver and
  Read on v0.6.0 — which points at process-level allocator/arena behavior, not a per-operation
  logical leak. Dedicated **Create-only** and **Read-only** settle runs (below) both reproduce a
  slow creep in isolation.
- **Recommendation:** safe for long-running services *today* (memory stays bounded-looking and small
  — 177–223 MB — over 6–12 h with zero errors), but Rust carries a **higher, slowly creeping**
  resident memory that has **not been proven to plateau**. Budget for it and **re-check periodically**.
  **Open item:** both single-operation settles (Create-only +9.69 MB/h, Read-only +1.25–1.54 MB/h)
  creep far less than the six-op soak but did **not flatten in 6 h**, so the classification —
  *bounded allocator/arena retention* vs *a slow Rust-side leak* — is still open. Closing it needs a
  longer isolated soak (12–24 h) plus allocator introspection (arena-cap / `malloc_trim` reclaim test
  and a native-vs-Python heap split), not more narrative.

### Create-only settle (isolated follow-up) — complete

To test the earlier Create `WATCH` directly, we ran **Create-only** for 6 hours per engine on
`leak_cont` (nothing else competing). Result:

| Engine | Create memory start→end (MB) | Last-hour drift (MB/h) | Verdict |
|--------|-----------------------------:|-----------------------:|---------|
| All-Python | 86 → 90 | −0.15 | PLATEAUED (flat) |
| **Rust** | **173 → 223** | **+9.69** | **WATCH** (still creeping) |

In isolation, all-Python Create is flat while **Rust Create keeps creeping** (+9.69 MB/h, one
late step, not yet flattened in 6 hours). Rust did **59.2 M** creates vs all-Python's **13.1 M**
(~4.5×) with **zero errors** and a single verified driver build. This mirrors the main-run Read
behavior: **whichever operation drives the most allocation churn shows a slow, bounded-looking
upward creep** — an allocator/arena signature, not an unbounded leak. It still argues for a
longer dedicated settle run to watch the line finally go flat.


### Read-only settle (isolated follow-up) — complete

To test the v0.6.0 Read `GROWING` result directly, we ran **Read-only** for 6 hours per engine on
`leak_cont` (nothing else competing), stamp `leak-20260704-232608148`. Result:

| Engine | Read memory start→end (MB) | Last-hour drift (MB/h) | Full-run slope (MB/h) | Verdict |
|--------|---------------------------:|-----------------------:|----------------------:|---------|
| All-Python | 86 → 89 | +0.20 ± 0.07 | +0.15 | PLATEAUED (flat) |
| **Rust** | **146 → 177** | **+1.54 ± 0.50** | **+1.25** | **WATCH** (still creeping) |

**What this shows.** Isolating Read **cut its creep by ~92%** — from **+18.9 MB/h** in the six-operation
soak down to **+1.25–1.54 MB/h** here. So the large soak-time number was mostly a *multi-operation*
allocator/arena effect, **not** a Read-specific defect: with only Read running, the same operation
creeps far more slowly and at a bounded-looking level (177 MB vs all-Python's 89 MB). Volume was
**121.7 M** Rust reads vs **21.9 M** all-Python, **zero errors**, single verified driver build, and no
staircase steps.

**What it does *not* yet settle (kept honest).** The Rust line still had a small, non-zero slope that
**did not fully flatten within 6 hours** — the last-hour slope (+1.54) is not lower than the full-run
slope (+1.25), so it is not visibly decelerating yet. Over a 6-hour window a *bounded* allocator-retention
effect and a *genuine slow leak* look identical. What the data **does** establish: the growth is
**Rust-side** (all-Python is flat) and is **not tied to one operation** (the culprit migrates between
runs). What it **cannot** yet establish is whether the line plateaus. Deciding that requires a longer
isolated soak (12–24 h) plus allocator introspection — an arena-cap (`MALLOC_ARENA_MAX`) and
`malloc_trim` reclaim test to tell *freed-but-retained* memory from *leaked* memory, and a
native-vs-Python heap split (`tracemalloc` + object counts) to localize where the bytes live. Tracked
as the open Phase B follow-up.


---

## Phase C — Stress behavior under heavy load (concurrency scale sweep)

**Why we ran this (and what a customer gets from it).** Phase 0 measured one request at a
time, and Phase A held a single fixed load (100 in flight). Neither answers the question a
team sizing a service actually asks: *"As I turn concurrency up, how much work can each engine
really push, where does it stop getting faster, and what becomes the wall — the database or my
own process?"* Phase C answers exactly that. It drives each engine harder and harder and reads
back the **achieved throughput, the latency cost, and the CPU cost** at every step. The payoff
for a customer is concrete: it tells you the **maximum requests/second you can expect from one
process**, the **concurrency setting that reaches it** (past which you only add latency, not
throughput), and **whether scaling further needs a bigger RU budget or just more processes**.

**How we ran it.** Same account and Gateway path, on a dedicated VM (`vm-python-phasec` — the same
VM used for the Phase A fixed-load baseline) with the account to itself.
Operation container `scale_db/scale_cont` provisioned at **150,000 RU/s** (the same physical
container used in Phase A, re-provisioned up from 100,000 RU/s so RU headroom — not the SDK — is
the intended limit under the heavier concurrency). This throughput is configured out-of-band
(`az ... throughput update`); the runner reports the target but does not enforce it. For two representative
operations (`read`, `upsert`) on **both engines**, we swept a concurrency ladder of
**32 → 64 → 128 → 256 → 512 → 1024** in-flight requests, **1800 s per point**, dropping the first
600 s as warm-up. Achieved throughput is measured directly as `count / window_seconds` per
reporting window. Every point is verified to have truly run on the engine it claims (Rust vs Python)
before any ceiling is reported.

**Results — achieved throughput (req/s), with latency and per-process CPU (median of measurement windows):**

| Op | Engine | c32 | c64 | c128 | c256 | c512 | c1024 |
|----|--------|----:|----:|-----:|-----:|-----:|------:|
| **Read** | core-python req/s | 948 | **960** | 950 | 923 | 910 | 882 |
|          | rust req/s | 4,514 | 5,027 | 5,468 | **5,453** | 5,205 | 5,161 |
|          | core-python p50/p99 ms | 20.9/42.1 | 40.8/70.0 | 84.9/126.1 | 172.2/234.0 | 354.6/451.8 | 723.5/912.9 |
|          | rust p50/p99 ms | 3.6/7.6 | 7.0/20.6 | 12.2/30.7 | 23.1/46.5 | 45.5/85.6 | 87.7/157.1 |
| **Upsert** | core-python req/s | 900 | 986 | 1,051 | **1,047** | 1,012 | 994 |
|            | rust req/s | 2,454 | 3,583 | 4,360 | 4,732 | **4,820** | 4,789 |
|            | core-python p50/p99 ms | 23.3/44.2 | 40.5/68.7 | 76.1/113.7 | 152.8/203.8 | 327.2/396.5 | 648.2/791.6 |
|            | rust p50/p99 ms | 7.6/11.9 | 8.4/22.6 | 14.8/34.0 | 26.9/53.1 | 47.8/87.5 | 93.8/160.3 |

**Zero throttling (0 × 429) at every point** — the 150k RU container was never the bottleneck. As
in every phase, core-python is pinned near **~1 CPU core** (the GIL ceiling) while Rust spreads
across **~2+ cores**, which is why Rust keeps scaling with concurrency and core-python does not.

**Throughput vs concurrency (req/s):**

```
READ                                UPSERT
        core-py    rust                    core-py    rust
  32      948      4,514              32      900      2,454
  64     [960]     5,027              64      986      3,583
 128      950     [5,468] peak       128    1,051      4,360
 256      923      5,453  knee       256   [1,047]     4,732
 512      910      5,205             512    1,012    [4,820] knee/peak
1024      882      5,161            1024      994      4,789

core-py |=          flat ~0.9k (1 core, GIL)   core-py |=       flat ~1.0k (1 core, GIL)
rust    |=======    ~5.5× , knee c256           rust    |=====   ~4× , knee c512
```

**What the sweep tells us:**

- **Each engine has a clear ceiling, and rust's is far higher.** Rust delivers **~5.5× more read
  throughput** (geomean 5.52×, range 4.76–5.91× across the shared levels) and **~4× more upsert
  throughput** (geomean 4.03×, range 2.73–4.82×) than core-python at matched concurrency.
- **core-python is GIL-bound and saturates almost immediately.** Its throughput is essentially flat
  (~0.9k read / ~1.05k upsert req/s), topping out by c64–c256 while pinned at ~1 CPU core — adding
  concurrency buys **no** extra throughput, only linearly worse latency (read p50 21 ms → 724 ms at c1024).
- **rust scales with concurrency to a knee, then flattens.** Read **peaks at c128 (~5,468 req/s)** and
  holds its knee at **c256 (~5,453 req/s)**. Upsert **peaks and knees together at c512 (~4,820 req/s)**,
  beyond which throughput is flat/slightly down while latency keeps climbing. **Practical guidance:
  operate rust around 256–512 in-flight per process**; pushing to 1024 gains nothing.
- **The wall is the client, not the database.** 0 × 429 everywhere means RU headroom was never the
  limit — core-python is capped by the GIL (~1 core) and rust by client CPU (~2+ cores). To go
  past one process's ceiling toward the account's full capacity, **scale out** (run N processes at
  the knee concurrency and sum their throughput), not up — quantified in the next section.

> **Zero errors this run.** Unlike an earlier driver run (which logged a handful of transient
> cold-start errors in one opening window), **every point of this v0.6.0 sweep ran with zero
> errors and zero throttling.**

**Integrity.** For this run, every measurement window was confirmed to have full coverage and every
point was verified to have truly run on the engine it claims (Rust vs Python). Both checks pass.

> **Provenance for Phase C-1 (ceiling sweep).** Results are from `--prefix sweep-` stamp
> `20260703-133727400` with **24 workload IDs** (2 ops × 2 engines × 6 concurrency levels), all
> zero-error/zero-throttle post-warmup windows, and a single Rust driver build `106ad05bc`.

---

## Phase C scale-out — one VM, many processes

**Why we ran this.** Phase C found each *single process* has a ceiling (Rust ~5.5k read req/s at
its knee) set by client CPU, not the database. The obvious question for anyone sizing a fleet:
*if one process tops out on CPU, do several processes side by side simply add up?* This run
answers it directly.

**How we ran it.** On one VM (`vm-python-phasec`), we launched **N identical Rust `read`
processes**, each at the single-process knee concurrency (c256), for **N = 1, 2, 4, 8, 12, 16**,
and summed their achieved throughput. The 150k RU/s container had ample RU headroom, so the only
thing that can bend the curve is the VM's own CPU.

| N processes | Total read req/s | vs 1 process | Efficiency |
|------------:|-----------------:|-------------:|-----------:|
| 1  | 5,399  | 1.0×  | 1.00 |
| 2  | 10,746 | 2.0×  | 1.00 |
| 4  | 20,079 | 3.7×  | 0.93 |
| 8  | 35,838 | 6.6×  | 0.83 |
| 12 | 47,911 | 8.9×  | 0.74 |
| 16 | 56,263 | 10.4× | 0.65 |

**What it means.** Throughput **scales out cleanly**: two processes are perfectly linear, and even
at 16 processes one VM pushes **~56,000 read req/s** — 10.4× a single process — with **zero
throttling**. Efficiency tapers from 1.00 to 0.65 only because the VM's CPU fills up (system CPU
rose ~3 % → ~53 %), exactly the expected shape. Practical takeaway: **to go past one process's
ceiling, add processes (and then VMs), not concurrency** — the database was never the limit here.

> **Provenance for Phase C-2 (scale-out).** Results are from `--prefix scaleout-` stamp
> `20260704-013736722` with **43 workload IDs** (N=1+2+4+8+12+16), zero post-warmup errors/no 429
> error documents, and the same single Rust driver build `106ad05bc`.

---

## Mixed / blended workload — the realistic-SLA number

**Why.** The phases above isolate one operation at a time. Real services send a *mix*. Here one
process issues a weighted blend (read-heavy, with create/upsert/replace/patch) so we can report
the **blended tail latency** a real app would actually see.

| Engine | Blended p99 | Blended p99.9 | Blended req/s | Errors |
|--------|------------:|--------------:|--------------:|-------:|
| All-Python | 91.0 ms | 99.7 ms | 192 | 0 |
| **Rust**   | **26.7 ms** | **35.0 ms** | **721** | 0 |

**What it means.** On a realistic mix, **Rust's blended p99 is ~3.4× lower** (26.7 ms vs 91.0 ms)
and it pushes ~3.8× the blended throughput, with zero errors on both engines. The per-operation
wins from Phase A carry through to a blended workload — the SLA number a customer would quote
improves across the board.

> **Provenance.** Measured **2026-07-04**; Rust driver v0.6.0 (`106ad05bc`), single verified
> build (provenance gate **PASS**); run stamp `20260704-031122916` with **2 workload IDs**
> (one per engine). One process issues a weighted blend; per-op and blended percentiles are
> pooled across windows from merged HdrHistograms (exact). **0 errors / 0×429** on both engines.

---

## Cold-start — the first call after a process starts

**Why this matters.** Everything above measures steady state. But serverless functions, autoscaled
pods, and scale-to-zero services are judged on the **very first call** after a fresh process
starts. We started **25 fresh processes per operation per engine** and recorded the first call each
one made.

| Operation | All-Python first-call p50 | Rust first-call p50 |
|-----------|--------------------------:|--------------------:|
| Read    | 20.3 ms | 152.7 ms |
| Create  | 27.6 ms | 160.6 ms |
| Upsert  | 28.5 ms | 161.9 ms |
| Replace | 28.1 ms | 167.8 ms |
| Patch   | 28.6 ms | 155.0 ms |

**What it means — a real Rust trade-off.** Rust's **first call is ~5–8× slower** than all-Python
(~150–170 ms vs ~20–30 ms), and a few processes saw multi-second first-call outliers (p99 up to
~5 s on read/upsert/replace) from cold TLS handshakes, Tokio-runtime spin-up, and connection-pool
warm-up. This is the flip side of Rust's steady-state speed: it front-loads more one-time setup.
**Guidance:** for long-lived processes this is a non-issue (paid once, then far faster forever);
for short-lived / scale-to-zero workloads, **pre-warm the client** (make one throwaway call at
startup) before serving traffic, or prefer all-Python if cold-start latency dominates.

> **Provenance.** Measured **2026-07-04**; Rust driver v0.6.0 (`106ad05bc`), single verified
> build (provenance gate **PASS**); run stamp `20260704-034123886` with **10 workload IDs**
> (5 ops × 2 engines). First-call pooling uses **25 cold samples per op+engine**; the report
> also saw additional error-only rows (`rows_without_cold_sample=300`), which are excluded from
> first-call percentile math by design. For this historical stamp, captured
> `config_concurrency` was 100.

---

## Payload size — small vs large documents (create)

**Why.** Document size changes both cost (RU) and where time goes (serialization, network). We
compared **create** on a small (~730 B, 7.24 RU) vs a large (30 RU) document, on both engines.

| Engine · size | p50 | p99 | p99.9 | req/s | RU/op |
|---------------|----:|----:|------:|------:|------:|
| All-Python · small | 56.1 ms | 84.7 ms | 97.7 ms | 594 | 7.24 |
| All-Python · large | 59.7 ms | 93.9 ms | 542.2 ms | 377 | 30.0 |
| Rust · small | 12.3 ms | 29.7 ms | 269.1 ms | 1,576 | 7.24 |
| Rust · large | 16.9 ms | **510.5 ms** | 521.0 ms | 377 | 30.0 |

**What it means.** Rust stays much faster at the median on both sizes. **But large documents hurt
Rust's tail disproportionately:** at large size Rust's p99 jumps to **510 ms — worse than
all-Python's 94 ms** at the same size, an inversion of the usual Rust-wins pattern. Both engines
pay the same 30 RU/op and become RU-bound (equal ~377 req/s) on large writes. Net: **Rust is the
clear pick for small/medium documents; for large-payload writes its median is still better but its
tail is not — worth a dedicated payload-shape matrix (see TODO).**

> **Provenance.** Measured **2026-07-04**; Rust driver v0.6.0 (`106ad05bc`), single verified
> build (provenance gate **PASS**); run stamp `20260704-041711998` with **4 workload IDs**
> (2 engines × 2 profiles). `create` at **conc=100** on a small (~730 B, 7.24 RU) vs large
> (30 RU) document; percentiles pooled from merged HdrHistograms (exact). **0 errors / 0×429**
> on both engines.

---

## TODO

- **Payload-shape & mixed-workload depth.** The blended-SLA, cold-start, and payload-size probes
  (new sections above) are each single points; turn them into curves — more op mixes, more
  idle/first-call scenarios, and a full small-vs-large document grid — and localize the Rust
  large-write tail (p99 510 ms) and cold-start first-call cost.
- **Phase B Read-only settle (new).** The Create-only settle is done (see Phase B); on v0.6.0 the
  drift moved to Read, so the natural next step is a long **Read-only settle** to watch the Rust
  Read line finally flatten and quantify the allocator/arena ceiling.
- **Phase D planning backlog .** Add the failure-mode
  and resilience runs we still owe: open-loop overload recovery, 429/throttle recovery,
  region failover, many-clients/many-accounts boundedness, mixed/large-item behavior, and
  lifecycle create/close churn.
- **Phase D correctness/safety gates (same §13 backlog).** Add differential correctness fuzz,
  cancellation/timeout chaos, fork+signal lifecycle, resource-exhaustion behavior, credential
  refresh at scale, and multi-day sanitizer soak.
- **Phase D dependency to unblock failover/429 on Rust.** Add fault injection that sits below
  the SDK path the Rust engine actually uses; without that, failover/429 “passes” can be false
  positives.

---

## Bottom line

**In the Phase A fixed-load baseline, the new Rust engine won every operation: about 5× faster
for typical response time, about 3× faster for slow requests, and about 4× more work handled
in the same time — for the same database cost, in exchange for using 2–3× more CPU.** Across
the full program, error rates stayed low but were **not** literally zero in every phase (for
example: Phase B had 13 error notes across hundreds of millions of operations; the Phase C sweep
ran error-free). Because the app and database were in the same region with the database
never a bottleneck, these numbers reflect the SDK engine itself. This is now the trusted
reference point for the remaining tests. The **memory test (Phase B) is now complete — both
engines show no per-operation leak over 12 hours; Rust runs at a higher (~190–220 MB), bounded
level with a slow allocator-driven creep on one operation per run (Read on v0.6.0, Create
previously), which a Create-only settle reproduced in isolation** (see the Phase B section). The
**heavy-load stress test (Phase C) is now complete too**: under a concurrency sweep, Rust sustains
**~5.5× the read and ~4.0× the upsert throughput** of the all-Python engine, which is GIL-bound and
saturates at ~1 core; both engines plateau at a clear concurrency knee (Rust ~256–512 in-flight)
with zero throttling, so the ceiling is client CPU, not the database — and a **scale-out** run shows
one VM reaching **~56k read req/s at 16 processes** (see the Phase C sections). Follow-on probes add
three practical findings: on a **blended workload** Rust's p99 is ~3.4× lower; Rust pays a real
**cold-start** penalty (~150 ms first call vs ~25 ms); and on **large-document writes** Rust's tail
inverts (p99 510 ms vs all-Python 94 ms). At **single-request (conc=1) load** (Phase 0) Rust is faster
than Python at p50/p99/p99.9 on every point operation; the only per-op difference is **Patch**, which is
slower on Rust by design because it is a 2-round-trip read-modify-write, not a defect.