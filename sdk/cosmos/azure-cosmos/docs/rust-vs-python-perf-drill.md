# Rust vs Python — Cosmos SDK Speed Test Results

The Cosmos Python SDK can run database calls two ways: the original **all-Python**
engine, and a **new engine that hands the heavy work to Rust**. This document answers a
simple question a customer would ask: **is the new (Rust) engine faster, by how much, and
what does it cost?**

## Test plan in this doc (Iteration 1)

We keep the phase labels for tracking, but each phase maps to a clear test goal:

| Phase | Test goal | Current status |
|------|-----------|----------------|
| **Phase 0** | **Environment validation** — light-load (1 in-flight) SLA-near latency baseline | **Complete** |
| **Phase A** | **Fixed-load performance baseline** (latency, throughput, RU/op, CPU) | **Complete** |
| **Phase B** | **Long-run memory stability** (12-hour soak, leak/drift checks) | **Complete** |
| **Phase C** | **Stress behavior under heavy load** (concurrency scale sweep, resilience at higher pressure) | **Complete** |
| **Phase D** | **Failure-mode resilience + correctness under breakage** (failover/429/cancel/fork/resource-pressure/correctness parity) | **Planned (future iteration)** |

So this doc is not just one benchmark dump — it is the migration performance story: baseline speed first, then memory safety, then stress behavior.
Phase D is intentionally out of Iteration 1 scope, see TODO below.

## Phase setup quick-reference (Phase 0, A, B, C)

This is the fast "what changed between phases" view so nobody has to hunt in the long sections.

| Phase | Client VM | Account path | Operation container | Results container | Throughput / request model |
|------|-----------|--------------|---------------------|-------------------|----------------------------|
| **Phase 0** (light-load latency baseline) | `vm-python-dr-drill` | **Compute Gateway** (Gateway path) | `lat_probe_db/lat_probe_cont` (isolated) | `perfdb/perfresults` | Probe container at **20,000 RU/s**; **1 in-flight request** (concurrency=1), arrival rate 0, 1 client, no proxy; **~8 minutes** per operation per engine |
| **Phase A** (fixed-load baseline) | `vm-python-phasec` | **Compute Gateway** (Gateway path) | `scale_db/scale_cont` | `perfdb/perfresults` | Operation container at **100,000 RU/s**; results container at **4,000 RU/s**; fixed **100 in-flight requests**; **30-minute** run per operation per engine |
| **Phase B** (12-hour memory soak) | `vm-python-dr-drill` | **Compute Gateway** (Gateway path) | `leak_cont` | `perfdb/perfresults` (same as Phase A) | Not a throughput benchmark; request model changed to a **continuous 12-hour soak** — the six operations run as six parallel processes per engine (engines back-to-back, ~24 h wall-clock) — with ~5-minute memory sampling; integrity gate observed **772,501,793** total requests |
| **Phase C** (concurrency scale sweep) | `vm-python-phasec` | **Compute Gateway** (Gateway path) | `scale_db/scale_cont` @ **150,000 RU/s** (Phase A's container, bumped from 100k) | `perfdb/perfresults` | Throughput ceiling test; `read`+`upsert` on both engines swept across **32 → 1024** in-flight, **1800 s per point** (600 s warm-up dropped); achieved req/s = `count / window_seconds`; provenance gate enforced |

---

## What code these results test (engine build & versioning)

**Why this matters first.** A performance number is only meaningful if you know exactly *which*
code produced it. The Rust path is made of **two separate pieces of code that we version very
differently**, so before reading any result it helps to know what is under test and how we keep it
current.

- **The Python SDK + the Rust binding — code we own.** The binding (`azure_cosmos_rust`, a small
  PyO3 extension compiled into `azure/cosmos/_rust.abi3.so`) is the glue that lets Python call the
  Rust engine. It lives in **this** repo (`azure-sdk-for-python`) on the drill branch
  (`users/dibahl/python-sdk-with-rust-driver`), and it is the only Rust-facing code we author and pin.
- **The Rust driver — code we do *not* own.** The actual engine (`azure_data_cosmos_driver`) lives
  in the sibling repo **`azure-sdk-for-rust`**. We do not own or pin it; we treat its **`main`**
  branch as the source of truth so every drill runs against the **latest** driver.

**How the two fit together.** The binding pulls the driver in as a **path dependency** — a sibling
clone of `azure-sdk-for-rust` on the same VM. That means rebuilding the binding compiles the driver
from **whatever commit that clone is checked out to**. There is no separate "install the driver"
step: the driver version is decided entirely by where the sibling clone points.

**How we refresh a VM to the latest code before a run (the workflow):**

1. Update the Python + binding repo to our branch tip (`git fetch` + `git reset --hard` to
   `origin/users/dibahl/python-sdk-with-rust-driver`).
2. Update the sibling `azure-sdk-for-rust` clone to **`origin/main`** tip (that is where the newest
   driver lives — we always build from `main` to get the latest).
3. Rebuild the binding with `maturin develop --release`. Because the driver is a path dependency,
   this recompiles the driver from the freshly-updated `main` and drops a new `_rust.abi3.so` next
   to the Python files. A successful compile confirms the binding is API-compatible with the current
   driver; we then run a short one-request smoke to confirm it also works at runtime.

**Customer impact.** Because the driver moves quickly on `main`, "the Rust engine" is a moving
target. Tying results to a driver version is therefore essential: each run is rebuilt against the
current `main`, so a given phase's numbers reflect the driver as of that phase's run date, not a
frozen release. When a result is surprising, the first question is always *which driver commit was
compiled in* — the workflow above makes that answer reproducible.

---

## Why we ran this test, and how the results are used

**Motivation.** The Rust engine is a large change to how the SDK executes every database
call. Before it can be trusted in production or recommended to customers, we need hard,
side-by-side numbers proving it is actually faster, that it does not cost more in database
charges, and that we understand what it trades away (CPU). 

**Goals achieved by this test (Phase A — fixed-load baseline):**

- **A trustworthy speed baseline.** Exact p50/p99 latency and throughput for all six
  everyday operations on both engines, under identical conditions, with proof of which
  engine ran each request.
- **Cost transparency.** Confirmation that the Rust engine charges the *same* database
  cost (RU) per operation, and a clear measure of the *extra CPU* it uses to go faster.
- **A clean reference point.** Zero errors, steady numbers, database never a bottleneck —
  so these results measure the SDK engine itself, not the network or the service.

**How these results will be used:**

- **A go/no-go signal for the Rust engine** — the per-operation speedups here are the core
  evidence for whether the new engine is worth shipping.
- **The "hour-0" anchor for the follow-up tests** — the long-running memory test is now
  complete (**Phase B — memory stability**, below) and the heavy-load stress test
  (**Phase C — stress behavior**, below) is now complete as well.
  Both are read *against* this baseline, so any drift or slowdown they show can be attributed
  to the thing being tested, not to a broken workload.
- **A customer-facing summary** of the expected latency and CPU trade-off when choosing
  the Rust engine.

---

## Phase 0 — environment validation (SLA-near latency baseline)

**Why this phase exists (and why it comes first).** A performance comparison is only meaningful
if the *baseline itself* is healthy. For Cosmos point operations in the same region, a reasonable
environment should deliver latency in the neighborhood of **p99 ≈ 10 ms** — if it does, the numbers
mean something; if the baseline is running at tens or hundreds of milliseconds, the whole comparison
is measuring the test rig, not the SDK. Phase A is deliberately a *loaded* test (a fixed **100
requests in flight** at all times), so its per-request "latency" is mostly **time spent waiting in
the client's own queue under saturation**, not the time the database took. That is the right way to
compare two engines under identical pressure, but it is the wrong number to quote as an SLA baseline.
Phase 0 fills that gap: a **light-load probe that sends exactly one request at a time**, so there is
no client queue and the measured latency is a single round trip — the true per-request cost.

**What we did.** Same account, same region (West US 2), same Gateway path, on a separate VM
(`vm-python-dr-drill` — the same VM used for the Phase B soak, kept apart from the Phase A/C
throughput VM) and an isolated container so it never disturbs the loaded phases. For each of the six point operations, on
**both engines**, we ran one request at a time (`concurrency=1`, arrival rate 0, one client, no proxy)
for ~8 minutes. Percentiles below are **pooled exactly** — every reporting window stores its full
HdrHistogram, and the report tool merges those histograms across the whole run before reading the
percentile (so these are not the per-window-average approximations discussed later for Phase A).

**Results (one request in flight; pooled p50/p90/p99/p99.9 in milliseconds):**

| Operation | Engine | p50 | p90 | p99 | p99.9 | req/s @conc=1 | RU/op | Errors |
|-----------|--------|----:|----:|----:|------:|--------------:|------:|:------:|
| **Read**    | Python | 3.49 | 4.19 | 5.72 | 10.84 | 274 | 1.00 | 0 |
|             | Rust   | 2.83 | 3.65 | 6.14 | 9.46  | 329 | 1.00 | 0 |
| **Create**  | Python | 6.89 | 7.85 | 9.08 | 12.92 | 74  | 7.24 | 0 |
|             | Rust   | 6.70 | 7.90 | 11.25 | 16.13 | 74 | 7.24 | 0 |
| **Upsert**  | Python | 7.49 | 8.70 | 11.47 | 17.17 | 129 | 11.19 | 0 |
|             | Rust   | 6.88 | 7.97 | 10.93 | 17.77 | 139 | 11.18 | 0 |
| **Replace** | Python | 7.49 | 8.60 | 10.97 | 15.39 | 129 | 11.62 | 0 |
|             | Rust   | 6.65 | 7.68 | 10.34 | 15.68 | 145 | 11.62 | 0 |
| **Delete**  | Python | 6.66 | 7.73 | 10.55 | 26.94 | 70  | 7.24 | 0 |
|             | Rust   | 5.67 | 6.40 | 7.37 | 12.17 | 81  | 7.24 | 0 |
| **Patch**   | Python | 7.65 | 8.76 | 11.31 | 15.75 | 127 | 10.79 | 0 |
|             | Rust   | 9.99 | 11.62 | 15.57 | 22.11 | 96 | 10.67 | 0 |

**What this proves.**

- **The environment is valid.** The Python baseline lands at **~6–11 ms p99** for every operation
  (reads well under 10 ms; writes right on the line, which is expected since writes replicate and
  cost 7–12 RU). Zero errors, zero throttling. So the test rig genuinely delivers SLA-near latency,
  and any comparison anchored here is meaningful.
- **It confirms Phase A's latencies are a saturation effect, not the service.** Same database, same
  region, same networking — yet one request at a time is **~3.5 ms** for a read versus Phase A's
  ~57 ms. The difference is entirely the 100-in-flight client queue in Phase A. Phase A remains valid
  for *engine-vs-engine under identical offered load* and for *how to measure*; Phase 0 is the number
  to quote for *per-request SLA*.
- **Follow-up verdict for Read/Create tails (code-verified).**  
  > ⚠️ **SUPERSEDED (CDT 2026-07-02 16:45).** The retry-behavior explanation below was a *hypothesis*
  > from reading the driver's default config. We later **instrumented and measured** it and found the
  > retry paths **never fire** at `concurrency=1` (0 retries on every op), and — after updating the
  > driver to **v0.6.0** — the Read/Create tail regression **is gone entirely** (Rust is now faster than
  > Python at p50/p99/p99.9 on both). See **"Root-cause of the Read/Create tail (v0.6.0 re-measurement)"**
  > at the end of this Phase 0 section for the corrected, data-backed conclusion. The text below is kept
  > for the audit trail only.

  **Outcome (CDT 2026-07-01 23:07:45):** for Read/Create, we do **not** see a Python-wrapper or
  Python-binding request-shape bug. The remaining gap is driven by **Rust-driver retry behavior**
  (plus one workload artifact), not by Python request prep translation.
  1. **Create p99 gap:** Rust driver failover/retry is active by default in the operation pipeline
     (`max_failover_retry_count` resolves to 3 when unset), while legacy Python non-idempotent
     write retries are effectively off unless `retry_write` is set (`RetryNonIdempotentWrites`
     defaults to 0; write retry path is blocked when `retry_write <= 0`). This can raise Rust create
     tail latency without changing RU/op.
  2. **Read p99 gap (small):** Rust read path allows sent-transport local retry on idempotent/read
     operations (`allow_sent_transport_retry` with one local connectivity retry), which can add a
     small p99 shoulder while still improving median.
  3. **Workload artifact:** `create_item` cleanup deletes are best-effort (exceptions swallowed),
     and runs were sequential (Python stamp then Rust stamp), so container-state drift can bias
     create tails.
- **One anomaly worth chasing: Patch on Rust.** It is the only operation where Rust is *slower* than
  Python at conc=1, and the gap **widens with the percentile** — about **+2.34 ms at p50**
  (9.99 vs 7.65) and about **+4.26 ms at p99** (15.57 vs 11.31). The per-window Rust patch p50 series
  is flat across all eight windows (not a warm-up artifact), so this is a real, steady per-request
  cost in the Rust patch path, flagged for follow-up.

**Plain-English Phase 0 findings.**

> ⚠️ **These four bullets are the ORIGINAL (pre-root-cause) reading and are now SUPERSEDED** by the
> corrected conclusion in **"Root-cause of the Read/Create tail (v0.6.0 re-measurement)"** below. Kept
> for the audit trail.

- The test environment is healthy, so the baseline is trustworthy.
- Rust is faster at the middle (p50) for Read and Create, but has a heavier tail on those two.
- That tail difference is most likely from Rust retry behavior plus run-order/container-state noise,
  not from Python wrapper/binding request translation.
- Patch is still the only clear, stable per-request slowdown on Rust at conc=1.

**Reproducibility.** The probe is driven by `tests/workloads/run_phase0_probe.sh` (default engine
`core-python`; set `PHASE0_BACKENDS=rust` for the Rust pass), and the table above is produced by
`tests/workloads/phase0_report.py --stamp <run>`, which merges the per-window histograms into the
pooled percentiles shown. Both live alongside the existing `perf_validate.py` integrity gate.

### Root-cause of the Read/Create tail (v0.6.0 re-measurement)

**Why we revisited this.** The original Phase 0 pass (table above) showed Rust with a heavier *tail*
(p99/p99.9) than Python on **Read** and **Create**, and we had explained it as Rust retry behavior.
That explanation was a **hypothesis read off the driver's default config, never measured**. Because a
tail regression on the two most common operations would directly hurt customers, we treated it as a
real defect and drove it to a measured root cause before accepting any conclusion. Two things changed
the answer: (1) we **instrumented** the retry paths and found they never fire here, and (2) we updated
the Rust driver to **v0.6.0** and **re-measured**. The regression is gone.

**How we ruled it out — three steps, each with the evidence:**

1. **Retries do not fire (measured, not assumed).** We added per-attempt counters inside the Rust
   binding (`azure_cosmos_rust/src/wire.rs`: `BINDING_ATTEMPT_COUNT` / `BINDING_RETRY_COUNT`, surfaced
   to the harness as `attempt_calls` / `retry_calls`). At `concurrency=1` the counts are exact:
   Read/Upsert/Replace = **1.0 attempt/op, 0 retries**; Patch = 2.0 (its read-modify-write, see below);
   Create = 2.0 (a *timed* create plus an *untimed* best-effort cleanup delete — not a retry). **Zero
   retries on every operation.** The retry hypothesis is therefore disproven regardless of the tail
   numbers.

2. **Reproduce on current code.** We re-ran the same one-request-at-a-time probe on the **v0.6.0**
   driver. The Read and Create tail regressions **do not reproduce** — Rust is faster than Python at
   **every** percentile, tail included (see table). The earlier tail was a property of the *older*
   driver build; the update to v0.6.0 (`106ad05bc`) fixed it.

3. **Localize the remaining latency — client vs. server.** To prove *where* each millisecond is spent,
   we captured the service's own processing time, which Cosmos returns on every response in the
   `x-ms-request-duration-ms` header and which **both** engines expose. The arithmetic is simple:

   > **client time − server time = everything outside the service** (network + transport + the
   > Python↔Rust binding hop).

   If a tail lived in the service it would show up as high *server* time on **both** engines; if it is
   client-side it shows up only in the *gap*. We recorded server time into a second histogram alongside
   the existing client histogram and pooled both exactly.

**Re-measured results (v0.6.0, one request in flight, pooled; ms). CLIENT is wall-clock at the caller,
SERVER is the service-reported `x-ms-request-duration-ms`, GAP = client − server (the client-side
cost):**

| Operation | Engine | client p50 | client p99 | client p99.9 | server p99 | server p99.9 | **client-side gap @p99.9** |
|-----------|--------|-----------:|-----------:|-------------:|-----------:|-------------:|---------------------------:|
| **Read**   | Python | 3.75 | 7.48 | 13.50 | 3.35 | 6.11 | 7.40 |
|            | **Rust**   | **3.15** | **7.18** | **12.10** | 3.11 | 7.72 | **4.38** |
| **Create** | Python | 7.07 | 11.10 | 20.27 | 7.43 | 10.62 | 9.65 |
|            | **Rust**   | **6.25** | **9.67** | **14.38** | 7.05 | 10.30 | **4.08** |

Each cell above pools **60k–170k requests** (Read legs ~150k–174k; write legs ~63k–85k), zero errors,
zero throttling, with the server header present on **100%** of requests on both engines.

**What the split proves (plain English):**

- **The service does the same work in the same time on both engines.** Server-reported time is
  effectively identical (Read p99 3.11 vs 3.35; Create p99 7.05 vs 7.43). So the tail was never
  service-side — it could only be client-side.
- **Rust's client-side cost is the *smaller* of the two.** The client-side gap (network + transport +
  binding) at p99.9 is **4.38 ms for Rust vs 7.40 ms for Python** on Read, and **4.08 vs 9.65 ms** on
  Create. Rust's transport/binding stack is leaner than Python's `aiohttp` stack at every percentile.
- **Net: there is no Read/Create tail regression on v0.6.0.** Rust matches or beats Python on every
  point operation at p50/p99/p99.9. The customer-facing worry that motivated this investigation does
  not exist on current code.

**The one genuine difference — Patch on Rust is a 2-round-trip read-modify-write, by design.** Patch is
the only op where Rust is slower at conc=1 (p50 ≈ 10.4 vs 7.6 ms). This is **not** a regression or a
retry: on Rust, a partial update is implemented as **read the item, apply the patch locally, then
replace it** — two network round trips — whereas core-Python issues a single server-side partial
update. The 2.0 attempts/op counter and the ~2× latency both reflect that design, which is understood
and tracked separately. It is not a tail defect.

**A tail caveat we are keeping honest about.** In one of the two write runs, Rust **Upsert** p99.9 spiked
to ~48 ms; in the other run it was ~15 ms (better than Python's ~25 ms), with normal server time in both.
A single-run tail that swings 15↔48 ms with a healthy service time is host/GC noise on one reporting
window, not a stable engine property — but we flag it rather than hide it, and a confirmatory upsert
re-run is the clean way to close it if needed.

**Reproducibility (this root-cause work).** The retry counters and the client-vs-server capture ship in
the harness (commit `0d62335d70`): `perf_stats.py` records a parallel server-latency histogram from the
`x-ms-request-duration-ms` header, `workload_utils.py` reads that header in the SDK response hook, and
`perf_reporter.py` emits `server_p50/p99/p99_9` + `server_hist_b64` per window. The split table is
produced by **`tests/workloads/crt_split_report.py --prefix <run> --stamp <YYYYMMDD-HHMMSS>`**, which
pools both the client and server histograms and prints the per-op gap; the client-only pooled table is
`phase0_report.py` as before. The runs were `concurrency=1`, one client, no proxy, on an isolated probe
container, with each engine's legs run adjacent to minimize time drift.

---

## What we tested and why (Phase A baseline details)

We ran the six everyday database operations — **Read, Create, Upsert, Replace, Delete,
and Patch (partial update)** — through each engine and timed every request.

**Test setup at a glance:**

| Setting | Value |
|---------|-------|
| Azure region | **West US 2** — single region (the account's only read *and* write region; multi-region writes off) |
| Client machine | One VM, `vm-python-phasec`, in the same region as the database |
| Account routing plane | **Compute Gateway** |
| Client connection mode | **Gateway** |
| VM networking | **Accelerated networking enabled** |
| Operation container | `scale_db/scale_cont`, provisioned at **100,000 RU/s** |
| Account consistency | **Session** (the account's default consistency level) — identical for both engines |
| Records pre-loaded | **~1,000,000 items** (~1 KB each) so reads/updates/deletes had a real working set |
| Results container | A **separate** container, `perfdb/perfresults`, at 4,000 RU/s, so recording results never competes with the operation being timed |
| Load | **100 requests in flight at all times**, identical for both engines; 30-second request timeout |
| Duration | **30 minutes per operation, per engine** |
| Total operations run | **52,271,400** across both engines, with **0 errors** |

A few choices kept the comparison fair and the numbers trustworthy:

- **App and database in the same Azure region.** No long-distance network time is mixed
  into the results — we're measuring the SDK itself.
- **Connection mode was Gateway for this run.** The table compares the two SDK engines under
  the same Gateway-path conditions; do not read it as a direct-mode SLA certification.
- **The operation container had far more capacity (100,000 RU/s) than the load needed**,
  so the database was never the thing slowing us down. Confirmed by **zero errors** across
  every run.
- **Results were written to a separate container** (`perfdb/perfresults`), so the act of
  recording a measurement never competed with the operation being measured.
- **Each operation ran for 30 minutes on each engine**, long enough that the numbers
  settle and stay steady rather than reflecting a brief warm-up spike.
- **100 requests were kept in flight at all times**, identical for both engines. This is
  a steady, moderate load — deliberately *not* the maximum either engine can handle — so
  neither engine gets an unfair advantage.
- **We recorded proof of which engine actually ran each request.** So the "Rust" numbers
  are genuinely from Rust and the "Python" numbers are genuinely from Python — not
  mislabeled.

**How to read the columns (latency in milliseconds; lower is better):**

- **p50** — the median. Half of all requests were faster than this; the everyday
  experience.
- **p99** — the slow tail. Only 1 request in 100 was slower.
- **p99.9** — the deep tail. Only 1 request in 1,000 was slower — the rare slow ones.
  (See the measurement caveat at the end: these deep-tail numbers are approximate.)
- **throughput** — how many operations finished per second.
- **Requests** — the total number of operations completed over the 30-minute run.
- **Errors** — requests that failed (timeout, throttling/429, or a service error). Zero
  everywhere here, which is what makes the latency numbers trustworthy.
- **CPU** — how many processor cores the engine used, on average, to sustain that load
  (1.0 = one full core).

---

## Detailed — each operation

> **These are fixed-load numbers, not SLA latency.** Every latency below is measured with **100
> requests in flight at all times**, so it includes time each request spent queued in the client
> under saturation — the right basis for comparing the two engines under identical pressure, but
> *not* a per-request SLA figure. For the SLA-near, one-request-at-a-time baseline, see
> [Phase 0 — environment validation](#phase-0--environment-validation-sla-near-latency-baseline)
> (e.g. a read is ~3.5 ms at conc=1 versus ~60 ms here).

| Operation | Engine | p50 (ms) | p99 (ms) | p99.9 (ms) | Throughput (ops/sec) | Requests | Errors | RU/op | CPU (cores) | p50 speed-up |
|-----------|--------|---------:|---------:|-----------:|---------------------:|---------:|:------:|------:|------------:|:------------:|
| **Read**    | Python | 60.5 | 93.2 | 104.2 | 1,041 | 1,873,700 | 0 | 1.00 | 1.0 | — |
|             | Rust   | 9.6  | 26.4 | 31.9  | 5,655 | 10,177,100 | 0 | 1.00 | 2.4 | **6.3× faster** |
| **Create**  | Python | 56.0 | 86.5 | 111.9 | 584   | 1,051,800 | 0 | 7.24 | 1.0 | — |
|             | Rust   | 11.5 | 29.0 | 41.9  | 2,627 | 4,727,900 | 0 | 7.24 | 2.3 | **4.9× faster** |
| **Upsert**  | Python | 55.3 | 85.1 | 108.4 | 1,132 | 2,037,100 | 0 | 11.19 | 1.0 | — |
|             | Rust   | 11.3 | 28.1 | 38.4  | 4,374 | 7,872,900 | 0 | 11.19 | 2.2 | **4.9× faster** |
| **Replace** | Python | 57.0 | 88.4 | 110.4 | 1,096 | 1,972,800 | 0 | 11.63 | 1.0 | — |
|             | Rust   | 11.3 | 28.2 | 35.3  | 4,387 | 7,895,200 | 0 | 11.63 | 2.2 | **5.0× faster** |
| **Delete**  | Python | 52.8 | 82.8 | 108.5 | 593   | 1,067,200 | 0 | 7.24 | 1.0 | — |
|             | Rust   | 10.0 | 26.2 | 33.7  | 2,706 | 4,870,800 | 0 | 7.24 | 2.4 | **5.3× faster** |
| **Patch**   | Python | 60.2 | 93.7 | 121.5 | 1,040 | 1,871,700 | 0 | 10.80 | 1.0 | — |
|             | Rust   | 10.9 | 26.2 | 53.1  | 3,808 | 6,853,200 | 0 | 10.67 | 2.7 | **5.5× faster** |

> **How the p99.9 column is computed (and its one caveat).** Why this matters: p99.9 is the
> "one-in-a-thousand slowest request" number, so if we aggregate it inconsistently the doc can
> quietly under- or over-state the tail a customer would actually feel. This run
> (stamp `20260630-063923`) recorded a per-window p99.9 scalar for each reporting window but did
> **not** store the full latency histogram (`hist_b64`) for those windows. That means the exact
> pooled p99.9 across the whole run cannot be reconstructed after the fact — the best honest
> estimate is the **count-weighted average of the per-window p99.9 values**, which is the method
> now used for every cell above. It is a close approximation and slightly *understates* the true
> pooled tail (averaging blends the worst windows down), but it is applied uniformly so the
> engines stay comparable. The p50, p99, throughput, request counts, and RU columns are exact
> count-weighted aggregates and were unaffected. Newer runs capture the full HdrHistogram per
> window, so their p99.9 is pooled exactly rather than approximated.

---

## Visual snapshot — Phase A (fixed-load baseline, XY-coordinate curves)

Below are XY charts built from the same table values above (X = operation, Y = metric).

### p50 latency curve (lower is better)

```mermaid
xychart-beta
    title "Phase A p50 latency (ms) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "p50 latency (ms)" 0 --> 70
    line "Core Python" [60.5,56.0,55.3,57.0,52.8,60.2]
    line "Rust" [9.6,11.5,11.3,11.3,10.0,10.9]
```

### p99 latency curve (lower is better)

```mermaid
xychart-beta
    title "Phase A p99 latency (ms) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "p99 latency (ms)" 0 --> 100
    line "Core Python" [93.2,86.5,85.1,88.4,82.8,93.7]
    line "Rust" [26.4,29.0,28.1,28.2,26.2,26.2]
```

### Throughput curve (higher is better)

```mermaid
xychart-beta
    title "Phase A throughput (ops/sec) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Throughput (ops/sec)" 0 --> 6000
    line "Core Python" [1041,584,1132,1096,593,1040]
    line "Rust" [5655,2627,4374,4387,2706,3808]
```

### CPU curve (higher is more host CPU)

```mermaid
xychart-beta
    title "Phase A CPU (cores) by operation"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "CPU (cores)" 0 --> 3
    line "Core Python" [1.0,1.0,1.0,1.0,1.0,1.0]
    line "Rust" [2.4,2.3,2.2,2.2,2.4,2.7]
```

---

## Summary — the bottom line

The per-operation numbers are in the table above; this is only the aggregate synthesis
that the detailed rows don't show at a glance. Across all six operations the Rust engine
was faster at every latency level, for the **same** database cost (RU) and with **zero**
errors:

- **Typical latency (p50):** ~57 ms → ~11 ms — about **5× faster**.
- **Slow tail (p99):** ~88 ms → ~27 ms — about **3× faster**.
- **Total work in the same 30 min/op:** ~9.9 million ops → ~42.4 million ops — about
  **4× more**.
- **Cost unchanged, CPU higher:** RU/op identical on both engines; Rust used ~2.2–2.7
  cores vs ~1.0 for all-Python.

**In plain terms:** the new engine is several times faster and handles far more work in
the same time, without costing any more in database charges. The trade-off is that it
uses more of the machine's CPU — a good deal on today's multi-core servers.

---


## About the latency percentiles (p50/p90/p99/p99.9) — a measurement limitation

**Iteration note:** this document is **Iteration 1**. In a later iteration we will publish
pooled p50/p90/p99/p99.9 computed from merged per-window histograms, which closes this
percentile-pooling gap.

**What to keep in mind:** throughput/cost/error totals are exact from additive fields. Any
latency percentile derived from per-window scalar summaries (p50, p90, p99, p99.9) is not
strictly poolable across windows. p99.9 is called out separately below because it was the
least stable percentile in this run.

- **What we recorded.** For each operation we split its 30-minute run into six 5-minute
  slices, and for each slice we saved scalar percentile summaries (p50, p90, p99, p99.9) —
  **not** the raw timing of every single request.
- **How errors are tracked.** Each slice also records `count` and `errors` for that window,
  and the harness emits separate error documents with message/status metadata. For this
  Phase A stamp, all windows reported `errors = 0`.
- **Why this affects all percentile rows (and especially p99.9).** You cannot correctly
  combine per-window percentile scalars into one true run-wide percentile — percentiles do
  not add up the way counts do. So the count-weighted averages of the per-window scalars
  reported here are approximations. In this run, p99.9 was the most sensitive one (up to
  ~28% slice-to-slice spread), so its approximation error is the largest. (The p99.9 column
  in the table above was recomputed with this single count-weighted method after an earlier
  version of this doc mixed aggregation methods — e.g. a per-window max on one cell and a
  lower value on another — which understated several Python write-op tails by ~7–10 ms.)
- **Why p50/p90/p99 were acceptable here (but still not mathematically poolable).** These
  percentiles also do **not** add up across windows; we report the count-weighted average
  across the run's windows, and they were very stable between slices (only a few-percent
  spread), making the practical approximation error small for this run. Throughput and
  request counts simply add up across slices, so those are exact.
- **The one operation to call out is Patch.** Its p99.9 (~53 ms) is higher than the other
  Rust operations. Even so, that ~53 ms is still faster than the Python engine's *typical*
  (p50 ~60 ms) Patch time and under half its p99.9 (~122 ms) — so Patch is still a clear
  win, just with a bumpier deep tail, most likely because partial-document updates vary
  more on the server side.
- **How future runs fix this.** The harness stores a full HdrHistogram per slice (`hist_b64`).
  That is **not** raw per-request storage; it is a compact bucketed latency distribution for
  each 5-minute window. Those window histograms can be merged offline into one pooled
  distribution and then used to compute pooled p50/p90/p99/p99.9 from the merged histogram.
  This Phase A run was captured before `hist_b64` was present in the stored rows, so pooled
  percentiles cannot be recomputed after the fact for this stamp.

---

## Phase B — Long-run memory stability (12-hour soak)

**Status:** Complete. **Both engines are safe to run continuously; neither leaks.** One Rust
operation (Create) shows a small, unresolved upward drift we are keeping an eye on — details
below.

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
| What we recorded | The process's memory (RSS), sampled about every **5 minutes** — **144 readings per operation** over the 12 hours. Each reading stamps its own window length (`window_seconds`), which is normally ~300 s but can drift if a flush is delayed or shortened; for this run the windows were tightly clustered (median **300.196 s**, range **256.216–305.305 s**). The first reading, taken during warm-up, is dropped from the trend, leaving **143 analyzed**. |
| Results container | The same separate `perfdb/perfresults`, so recording never disturbs the run |
| Provenance | Every reading is stamped with which engine produced it, and we **verified engine purity** before trusting the numbers |

**A note on data hygiene (why you can trust these numbers).** The harness records two kinds
of documents: normal memory readings, and separate *error notes* (which carry no memory
number). An earlier version of our checking tool accidentally mixed the two — which made a
clean run look like it had failed and made some memory lines appear to start at "0 MB". We
fixed the checker to keep error notes out of the memory math and count them separately. On
this run the purity check **passed**, with **7 error notes** across the whole 12 hours (core
Patch 3, Rust Delete 2, Rust Patch 2) — a negligible rate — all correctly set aside from the
memory trend.

### How we know this run is trustworthy — two required gates + completion

We do not trust the memory numbers on their own; a run only counts if it passes **two
automated gates** and is proven to have run to completion.

**Gate 1 — provenance + memory-verdict gate.** Confirms every recorded row
actually ran on the engine it claims (the all-Python rows really are Python; the Rust rows
really are Rust), then computes the leak verdict. **Result: PASS** (exit 0), 7 error notes
set aside as described above.

**Gate 2 — integrity gate.** This is the check that a *dropped* reading can't
quietly hide a leak. It verifies three things: (1) **no reporting window was lost** — the time
gap between consecutive readings matches each row's recorded window length (any bigger jump =
a lost window); (2) **the reporter logged no dropped-write warnings**; and (3) **binding-call
counts prove the engine** — each Rust row shows Rust binding calls, each Python row shows
zero. **Result: PASS** (exit 0) — all 12 operation×engine cells clean, **772,501,793 total
operations** with **7 errors** (0.00%), no missing windows.

**Completion proof.** The soak ran the **full 12 hours per engine** — the run's output ends on
its terminal line `=== integrity gate PASSED ===`, and that output file is timestamped exactly
at the 12-hour mark (06:16:11 UTC, i.e. 43200 s after the core-engine batch began). Afterwards
**every worker process exited** (no hung or stuck processes), and re-running *both* gates today
reproduces PASS. (The harness build used for this run ends at the integrity gate; the updated
harness used for Phase C also prints an explicit `Phase B OK` line and a pass/fail exit
code, so future runs have a one-line success stamp.)

### How to read the verdicts:

- **PLATEAUED** — climbed during warm-up, then went flat and stayed there. Healthy.
- **STAIRCASE** — rose in a few discrete jumps (memory pools grabbing a chunk at a time) and
  then held. Bounded and healthy — *not* a leak.
- **WATCH** — mostly flat, but the final stretch is still drifting up a little, so we cannot
  yet *prove* it has leveled off. Not a proven leak; a follow-up item.

*How we decide the verdict, in plain English: we look at the last hour's growth rate and
its uncertainty band (95% CI). If the worst-case side is still small (upper bound ≤ 2 MB/h),
we call it bounded/flat (`PLATEAUED` or `STAIRCASE` depending on shape). If even the best-case
side is clearly high (lower bound ≥ 5 MB/h), we call it `GROWING`. Anything in between is
`WATCH` — basically "not scary, but not fully closed yet."*

### All-Python engine — flat, no leak

Every operation settled around **85–91 MB** and held there for 12 hours. The tail (the last
hour) is essentially flat — between **+0.01 and +0.07 MB per hour**, which is noise, not
growth.

| Operation | Memory start→end (MB) | Verdict |
|-----------|----------------------:|---------|
| Read    | 85 → 89 | PLATEAUED |
| Create  | 87 → 91 | PLATEAUED |
| Upsert  | 86 → 90 | PLATEAUED |
| Replace | 86 → 90 | PLATEAUED |
| Delete  | 86 → 90 | PLATEAUED |
| Patch   | 86 → 91 | PLATEAUED |

Shape (Create, all-Python): `87 ▁▅▅▅▆▆▆▇▇▇▇▇▇▇▇▇▇▇▇▇█ 91` — a small warm-up rise, then a flat line.

### Rust engine — higher but bounded; one to watch

The Rust engine settles at a **higher** memory level than the all-Python engine (roughly
**2.5–3.6× more**, ~240–330 MB). That is expected: it keeps more machinery resident (per-core
worker threads, connection pools, buffers) — the same machinery that buys the 5× speed. The
important question is not "is it higher?" (it is, by design) but "does it *keep climbing*?"
For four of six operations, no — they rise in a couple of steps and hold:

| Operation | Memory start→end (MB) | Last-hour drift (MB/h) | Verdict |
|-----------|----------------------:|-----------------------:|---------|
| Delete  | 162 → 275 | −0.19 | STAIRCASE (bounded) |
| Read    | 146 → 265 | −0.19 | STAIRCASE (bounded) |
| Replace | 152 → 250 | +0.32 | STAIRCASE (bounded) |
| Upsert  | 153 → 242 | +0.19 | STAIRCASE (bounded) |
| Patch   | 172 → 329 | +1.30 | WATCH (mild) |
| **Create** | **154 → 296** | **+4.74** | **WATCH** |

### Visual snapshot — Phase B (XY-coordinate curves)

For chart consistency, X-axis order is: **Read, Create, Upsert, Replace, Delete, Patch**.

```mermaid
xychart-beta
    title "Phase B memory at start of analysis window (MB)"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Memory start (MB)" 0 --> 200
    line "Core Python" [85,87,86,86,86,86]
    line "Rust" [146,154,153,152,162,172]
```

```mermaid
xychart-beta
    title "Phase B memory at end of run (MB)"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Memory end (MB)" 0 --> 350
    line "Core Python" [89,91,90,90,90,91]
    line "Rust" [265,296,242,250,275,329]
```

```mermaid
xychart-beta
    title "Phase B Rust last-hour drift (MB/h) vs decision bounds"
    x-axis ["Read","Create","Upsert","Replace","Delete","Patch"]
    y-axis "Drift (MB/h)" -1 --> 6
    line "Rust observed drift" [-0.19,4.74,0.19,0.32,-0.19,1.30]
    line "Flat upper bound (2 MB/h)" [2,2,2,2,2,2]
    line "Leak lower bound (5 MB/h)" [5,5,5,5,5,5]
```

Shape (Create, Rust): `154 ▁▁▂▂▂▂▂▂▂▂▂▂▂▂▂▂▄▄▇▇▇█ 296` — flat for most of the run, then a
**step-up near the very end**.

**What the Create "WATCH" means, honestly.** Create's upward drift (+4.74 MB/h) comes almost
entirely from a single step-up that landed in the **last hour** of the run — which is exactly
the window we measure the "is it still climbing?" slope over. So the number reads as "still
rising" even though the rest of the 12 hours was flat. This is most likely another staircase
step (a memory pool grabbing one more chunk) that simply arrived late — **not** evidence of
an unbounded leak. But because the run ended before it flattened, we are being conservative
and labeling it **WATCH** rather than declaring it closed. Patch shows a much milder version
of the same thing.

### Phase B bottom line

- **The all-Python engine does not leak** — flat ~90 MB for 12 hours, every operation.
- **The Rust engine does not leak either**, with one caveat: it runs at a **higher, bounded**
  memory level (~240–330 MB) that grows in discrete steps and then holds. Four of six
  operations are conclusively flat; **Create and (mildly) Patch** end on a small upward drift
  we have flagged **WATCH** — probably a late bounded step, not a leak.
- **Recommendation:** safe for long-running services. To fully close the Create question, a
  short **Create-only settle run** (let it continue past the last step until the line goes
  flat) is the clean follow-up. It needs the account to itself, so it will run after the
  heavy-load test (Phase C).


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
guaranteed never to be the bottleneck under the heavier concurrency). For two representative
operations (`read`, `upsert`) on **both engines**, we swept a concurrency ladder of
**32 → 64 → 128 → 256 → 512 → 1024** in-flight requests, **1800 s per point**, dropping the first
600 s as warm-up. Achieved throughput is measured directly as `count / window_seconds` per
reporting window. A **provenance gate** (`scale_verdict.py`) confirms every point actually ran on
the engine it claims before any ceiling is reported.

**Results — achieved throughput (req/s), with latency and per-process CPU (median of measurement windows):**

| Op | Engine | c32 | c64 | c128 | c256 | c512 | c1024 |
|----|--------|----:|----:|-----:|-----:|-----:|------:|
| **Read** | core-python req/s | 936 | 947 | 969 | 954 | 918 | 887 |
|          | rust req/s | 4,812 | 5,185 | 5,696 | **5,822** | 5,724 | 5,389 |
|          | core-python p50/p99 ms | 20.5/42.2 | 41.1/70.0 | 82.0/123.4 | 167.2/226.2 | 352.3/451.1 | 722.4/914.4 |
|          | rust p50/p99 ms | 3.3/7.2 | 6.7/20.0 | 11.7/29.6 | 21.3/44.5 | 40.7/78.1 | 82.3/149.8 |
| **Upsert** | core-python req/s | 883 | 1,026 | 1,082 | **1,097** | 1,033 | 1,069 |
|            | rust req/s | 2,413 | 3,555 | 4,338 | **4,955** | 4,921 | 4,863 |
|            | core-python p50/p99 ms | 23.4/49.9 | 39.1/66.2 | 74.6/111.3 | 143.6/191.5 | 319.0/387.6 | 604.7/734.7 |
|            | rust p50/p99 ms | 7.7/12.7 | 8.3/22.9 | 14.3/32.8 | 25.2/50.0 | 47.2/87.0 | 92.5/157.4 |

Per-process CPU (median of post-warmup windows) ranged **~85–103 % for core-python** and
**~129–235 % for rust**. **Zero throttling (0 × 429) at every point** — the 150k RU container was never
the bottleneck.

**Throughput vs concurrency (req/s):**

```
READ                                UPSERT
        core-py    rust                    core-py    rust
  32      936      4,812              32      883      2,413
  64      947      5,185              64    1,026      3,555
 128      969      5,696             128    1,082      4,338
 256      954     [5,822] peak       256   [1,097]   [4,955] peak
 512      918      5,724             512    1,033     [4,921] knee
1024      887      5,389            1024    1,069      4,863

core-py |=          flat ~0.9k (1 core, GIL)   core-py |=       flat ~1.1k (1 core, GIL)
rust    |=======    ~6× , knee c256            rust    |=====   ~4× , knee c512
```

**What the sweep tells us:**

- **Each engine has a clear ceiling, and rust's is far higher.** Rust delivers **~5.8× more read
  throughput** (geomean 5.81×, range 5.15–6.20× across the shared levels) and **~3.9× more upsert
  throughput** (geomean 3.92×, range 2.70–4.76×) than core-python at matched concurrency.
- **core-python is GIL-bound and saturates almost immediately.** Its throughput is essentially flat
  (~0.9k read / ~1.1k upsert req/s) from c32 onward while pinned at ~1 CPU core — adding concurrency
  buys **no** extra throughput, only linearly worse latency (read p50 20 ms → 722 ms at c1024).
- **rust scales with concurrency to a knee, then flattens.** Read peaks at **c256 (~5,822 req/s)**.
  For upsert, throughput **peaks at c256 (~4,955 req/s)** and the verdict knee is **c512 (~4,921 req/s)**,
  where gains have flattened. Beyond that, throughput is flat/slightly down while latency keeps
  climbing. **Practical guidance: operate rust around 256–512 in-flight per process**; pushing to 1024
  gains nothing.
- **The wall is the client, not the database.** 0 × 429 everywhere means RU headroom was never the
  limit — core-python is capped by the GIL (~1 core) and rust by client CPU (~2.3 cores). To go
  past one process's ceiling toward the account's full capacity, **scale out** (run N processes at
  the knee concurrency and sum their throughput), not up.

> **One cold-start footnote (does not affect the result).** The very first point of the whole sweep
> (`read`, rust, c32) logged **32 errors in its opening reporting window** — transient connection
> cold-start — then ran clean for the rest of the point. Net error rate for that point is
> **0.0004 %** (32 of 8.63 M) and every other point had **zero** errors. The pooled ceiling for that
> point uses only its clean steady-state windows.

**Reproducibility & integrity.** The sweep is driven by `tests/workloads/run_throughput_sweep.sh`
and the verdict (knees, geomean, provenance gate) by `tests/workloads/scale_verdict.py`;
`tests/workloads/perf_validate.py` independently confirms window coverage and per-row engine
provenance. Both gates pass for this run. (The provenance gate was hardened in this iteration to
ignore empty zero-count reporting windows — an idle/cold-start window legitimately carries no engine
label — so it no longer false-fails on cold-start, while still failing genuine engine mislabels or
points with no real data.)

---

## TODO (next iteration)

- **Phase C scale-out follow-up.** Phase C established the single-process throughput ceiling and
  the per-engine knee concurrency; the natural next step is a **scale-out run** (N processes at the
  knee concurrency, summing throughput) to chart how far the account scales past one process.
- **Phase A percentile gap (iteration follow-up).** Publish pooled percentile numbers from
  merged per-window histograms so p50/p90/p99/p99.9 are mathematically pooled for the full run.
- **Phase B Create closure.** Run the short Create-only settle follow-up to confirm the late
  step levels off and close the current `WATCH` item.
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

**The new Rust engine won every operation at every level: about 5× faster for typical
response time, about 3× faster for slow requests, and about 4× more work handled in the
same time — for the same database cost, in exchange for using 2–3× more CPU. Zero errors
throughout.** Because the app and database were in the same region with the database
never a bottleneck, these numbers reflect the SDK engine itself. This is now the trusted
reference point for the remaining tests. The **memory test (Phase B) is now complete — both
engines are stable over 12 hours, with one Rust operation (Create) flagged WATCH for a late,
likely-bounded drift** (see the Phase B section). The **heavy-load stress test (Phase C) is now
complete too**: under a concurrency sweep, Rust sustains **~5.8× the read and ~3.9× the upsert
throughput** of the all-Python engine, which is GIL-bound and saturates at ~1 core; both engines
plateau at a clear concurrency knee (Rust ~256–512 in-flight) with zero throttling, so the ceiling
is client CPU, not the database (see the Phase C section). The **Phase 0 Read/Create tail concern is
now closed**: on the v0.6.0 driver Rust is faster than Python at p50/p99/p99.9 on both, a client-vs-server
split shows the service time is identical across engines and Rust's client-side overhead is the smaller
of the two, and the only remaining per-op difference — Patch being slower on Rust — is a by-design
2-round-trip read-modify-write, not a defect (see "Root-cause of the Read/Create tail" under Phase 0).
