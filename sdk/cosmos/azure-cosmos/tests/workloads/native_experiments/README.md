# Isolated native profiling experiments

These are **opt-in test tools**, not SDK optimizations. They investigate allocator
choice and Rust-to-Python completion handoff without changing the installed SDK,
normal Cargo features, or production allocator.

The runner copies the current native sources and compile-time fixtures into a
new output directory. It applies checked test seams there and builds standalone
Rust test executables. Python sources used by embedded tests remain in the
checkout and are fingerprinted before and after the experiment. Dirty source
changes are included; a Git commit alone is not treated as source identity.

## Prerequisites

- Linux or Windows, Python 3.10+ and the package's development dependencies.
- A working host Rust/C toolchain for the current binding and pinned driver.
- On Linux, shared `libpython` and its development files for the selected Python,
  plus readable `/proc/self/status` and `/proc/self/smaps_rollup`.
- Use the same Python environment that can run the package's native tests.

Run from the `sdk/cosmos/azure-cosmos` package directory. The script selects the
invoking Python executable for PyO3. It copies `rust-toolchain.toml` when present;
`--toolchain` is an explicit override, not an automatic fallback. For example,
the initial Windows experiments used installed Rust 1.95.0.

The runner passes that interpreter's package directories to embedded Python.
Both the runner and native samples verify the loaded `azure.cosmos` source path.
An editable SDK installation can shadow `PYTHONPATH`; if the source check fails,
use a separate virtual environment with the development dependencies, without
an editable Cosmos SDK installation pointing at a different checkout.

The fixtures do not use a Cosmos account or perform live Cosmos service calls.
Cargo can download build dependencies unless `--offline` is supplied.

## Start with smoke qualification

Linux:

```bash
python tests/workloads/profiling_native_experiments.py allocator \
  --output-dir /tmp/cosmos-allocator-smoke --smoke

python tests/workloads/profiling_native_experiments.py handoff \
  --output-dir /tmp/cosmos-handoff-smoke --smoke
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe tests\workloads\profiling_native_experiments.py allocator `
  --output-dir C:\temp\cosmos-allocator-smoke --smoke
```

Choose a **new output directory outside the package** for every invocation.
Existing output is never overwritten or deleted. Failed runs retain their logs.
`--smoke` uses 1,000 operations and one pair; it never qualifies performance.

By default, builds use the output directory's own Cargo target directory.
`--reuse-build-cache` reuses the package's `target` directory to reduce rebuild
time. It still does not install a wheel or replace `_rust.so` / `_rust.pyd`.

On Linux, only the copied manifest drops PyO3's `extension-module` feature:
these are executables embedding Python, so they must link to `libpython`.
The original SDK's extension build configuration is unchanged.

## Allocator comparison

```bash
python tests/workloads/profiling_native_experiments.py allocator \
  --output-dir /tmp/cosmos-allocator-01 --iterations 16384 --pairs 4
```

The default allocator and mimalloc run in separate fresh processes, with order
reversed in alternating pairs. Each process uses two Tokio workers, 512 warmup
operations, and one in-flight native read by default. `--concurrency 8` is also
supported for this experiment.

Both arms execute the same binding item future against the driver's in-memory
emulator, then perform the same Python response conversion. The experiment
records whole-phase elapsed time, process CPU, future type size, and memory
snapshots. It is **not** the public Python API or an asyncio handoff benchmark,
and includes emulator work. Future type size is not an allocation trace.

Only the copied crate gains the opt-in allocator feature. The experiment pins
`mimalloc 0.1.52` and `libmimalloc-sys 0.1.49`; all pre-existing dependency identities
and package records must remain unchanged. The system arm does not enable them.

Memory fields retain their platform meaning. Linux private clean/dirty resident
pages are not Windows private committed bytes. Peak RSS is process-lifetime,
not the peak of just the measured phase. Do not compare unlike memory fields.

## Completion handoff and allocation breakdown

```bash
python tests/workloads/profiling_native_experiments.py handoff \
  --output-dir /tmp/cosmos-handoff-01 --iterations 5000 --pairs 4
```

This uses a previously obtained native read response. The control calls the
current unmodified binding runner; an instrumented copy records boundaries from
native completion through GIL acquisition, response conversion, completion-hook
publication/execution, and application resumption. All markers use one Rust
`Instant` clock. There is no service work in the measured completion.

Controlled fixtures check result parity, error type/message, cancellation,
explicit hook context, and deliberate GIL/event-loop delays before measuring.
Handoff currently requires concurrency one.

Timing and allocation counting use **separate executables**. Allocation runs
compare full handoff with the same response conversion without the async bridge,
then run an idle control. Counts cover Rust's global allocator, including
reallocations and delayed cleanup; they exclude Python/C allocation and are not
retained memory or a leak verdict.

The timing gate requires median paired observer CPU overhead at most 10% and
control CPU spread at most 10%. A completed run can fail this gate. In that case,
phase distributions are descriptive only, not baseline latency or proof of a
bottleneck. Initial Windows timing failed qualification; that result is not
silently treated as a successful optimization.

Native-completion-to-join time can include initial PyO3 GIL work, not just Tokio
scheduling. Conversion-end-to-enqueue includes the later GIL acquisition and
publication work; those are not separately decomposed.

## Evidence and interpretation

`summary.json` records completion status, inputs, resolved key dependencies,
compiler/interpreter versions, source/asset/binary hashes, raw sample summaries,
and qualification results. Per-command output and handoff traces are retained.
A source mismatch, unexpected dependency change, missing marker, incorrect
result, compile error, timeout, or unsupported platform fails explicitly.

These are local screening tools. Neither experiment qualifies a production
allocator change, a Linux live-workload gain, query performance, or SDK p99.
Do not pool these results with the bounded service workload measurements.
No commit, push, deployment, account provisioning, or service seeding is performed.

Both experiments have passed native smoke qualification on Windows and Linux.
Linux qualification used a separate virtual environment and the embedded-Python
package paths and source-origin checks described above. These smoke runs qualify
execution and correctness, not a performance improvement.
