# `azure_cosmos_rust` — the Rust crate behind `azure.cosmos._rust`

You're in a Rust crate. The Python SDK that lives one directory up has a
tiny chunk of code that isn't Python — it's Rust, and it lives here.
This README is for someone about to edit it.

If instead you want to install/build/test the Python SDK as a whole, the
README at `../README.md` is the one you want.

## What this crate is for

The Python SDK needs to call into a Rust HTTP driver for some operations
(today: `create_item`). Python can't call Rust functions directly — the
two languages don't share a calling convention. So we have a small
"glue" crate, this one, that does the translation. When it's compiled,
you get one file: `_rust.pyd` on Windows, `_rust.so` on Linux/macOS.
That file gets dropped into `azure/cosmos/`, and the Python code
imports it as `azure.cosmos._rust`.

The whole crate is one source file: `src/lib.rs`, ~320 lines. Reading it
top-to-bottom is the fastest way to understand what's here. This README
is the map.

## What Python actually sees

After a successful build, this is what Python can do:

```python
from azure.cosmos import _rust

handle = _rust.init_client("https://localhost:8081", "<master key>")
status, sub_status, headers, body = _rust.create_item(handle, prepared)
```

Two functions, one module attribute. They get there because `src/lib.rs`
declares them with `#[pyfunction]` and then a small init function lists
them by name (look for `#[pymodule] fn _rust(...)` near the top of
`lib.rs` — that's the only place a function becomes visible to Python).

What each one does:

- **`init_client(endpoint, master_key) -> handle`** — first call per
  process spins up a Tokio runtime and a `CosmosDriverRuntime`, builds
  the `CosmosDriver` for that endpoint, and caches it. Returns the
  endpoint string back to Python as an opaque "handle." Subsequent calls
  with the same endpoint reuse the cached driver.
- **`create_item(handle, prepared) -> (status, sub_status, headers, body)`**
  — `prepared` is a Python `PreparedRequest` dataclass the SDK builds
  before calling in. The function pulls its fields out one at a time
  (`getattr` + `extract`), constructs a typed driver operation, runs it
  on the cached Tokio runtime with the GIL released, and returns the
  driver's response as a 4-tuple the Python parser unpacks.
- **`__version__`** — string, set from the crate's Cargo version at
  compile time. Useful for "which build of the binding am I running?"

## Where the Rust driver actually lives

Look at the bottom of `Cargo.toml`. You'll see:

```toml
azure_data_cosmos_driver = { path = "../../../../../azure-sdk-for-rust/sdk/cosmos/azure_data_cosmos_driver" }
```

The driver isn't in this repo. We point at a sibling clone of the
`azure-sdk-for-rust` repository. So the on-disk layout we expect is:

```
<your repos folder>/
├── azure-sdk-for-python/sdk/cosmos/azure-cosmos/   ← this crate
└── azure-sdk-for-rust/sdk/cosmos/azure_data_cosmos_driver/   ← the driver
                       /sdk/core/azure_core/                  ← + two more
                       /sdk/identity/azure_identity/             from the same clone
```

Two more `path =` deps live in the workspace `Cargo.toml` one directory
up, pointing at `azure_core` and `azure_identity` from the same clone.

**Don't change one without the others, and don't mix `path` with `git`.**
If the binding's `azure_core` resolves to a different copy than the
driver's `azure_core`, Cargo treats them as two different crates and
the build fails with this exact error:

```
error[E0308]: mismatched types
   = note: expected struct `azure_core::Error`
              found struct `azure_core::Error`
```

Same name, two copies, no automatic conversion. The fix is always the
same: make all three deps (`azure_data_cosmos_driver`, `azure_core`,
`azure_identity`) `path = ...` entries pointing into the same external
clone.

If your clones live somewhere other than side-by-side, edit those three
lines. Nothing else in the build assumes that layout.

## Building from in here (without going through maturin)

For day-to-day Python work, build via `maturin develop` from the outer
directory — see `../README.md`. But while you're hacking on Rust, the
two fastest feedback loops bypass maturin entirely:

```powershell
# From the workspace root one level up — NOT from inside this directory:
cd ..

cargo check -p azure_cosmos_rust          # fastest: compiles, doesn't link
cargo build -p azure_cosmos_rust --release   # also produces the .dll, but doesn't install it
```

Why from the workspace root? Because that's where `Cargo.toml` defines
which `azure_core` and `azure_identity` versions get used. Run from
inside this directory and Cargo will refuse — it can't find the
workspace.

Once `cargo check` is green, `maturin develop` (back at the outer
directory) is what actually produces a fresh `_rust.pyd` and copies it
into `azure/cosmos/` so Python can import it.

## What this binding currently forwards on the wire

The Python helper layer hands us a `headers` dict full of Cosmos request
headers. The driver's typed `CosmosRequestHeaders` only accepts two of
them today, so those are the only two we forward:

- `x-ms-activity-id` (we parse it as a UUID before attaching)
- `x-ms-session-token`

Every other header in the dict — `x-ms-cosmos-intended-collection-rid`,
trigger headers, indexing directive, priority, and so on — is **silently
dropped** before the wire. That's not a bug in the binding; it's a
driver gap. Closing each header is tracked individually in
`../docs/V5_PARITY_AUDIT.md` § B, with corresponding `xfail` markers in
the parity test suite that flip green automatically when the gap closes.

If you're investigating a parity-test failure that looks like "header
present on the Python path, missing on the Rust path" — that's why,
and it's expected until the driver lands the support.

## File layout (and what's actually in each part of `lib.rs`)

```
azure_cosmos_rust/
├── Cargo.toml          # cdylib output + pyo3 0.22 (extension-module, abi3-py39)
│                       # + the three external path deps
├── src/
│   └── lib.rs          # everything below
└── README.md           # this file
```

Reading `lib.rs` top-to-bottom you'll see, in this order:

1. `use` lines — three of them (`pyo3::prelude::*`, `pyo3::types::{...}`,
   `pyo3::exceptions::{...}`) plus driver imports.
2. Per-process singletons (`OnceLock`s) for the Tokio runtime, the
   driver runtime, and a per-endpoint cache of drivers.
3. `#[pymodule] fn _rust(...)` — the init function CPython calls once at
   import time. Two `m.add_function(...)` calls plus one `m.add(...)`
   are what makes the three names listed above visible to Python.
4. `#[pyfunction] fn init_client(...)` — see "What Python actually sees."
5. `#[pyfunction] fn create_item(...)` — same.
6. Three small private helpers at the bottom: `parse_container_link`,
   `parse_partition_key_header`, `extract_item_id`.

## Where to look when you're stuck

- **PyO3 syntax confusion** (what `Bound<'py, T>` means, why some
  signatures have `'py` and others don't, what `into_any().unbind()`
  does, why `PyDict::new` got renamed to `PyDict::new_bound`, what
  `py.allow_threads` actually releases): `../docs/PY03-BASICS.md`. Read
  this before changing any function signature or any line that
  constructs a Python object from Rust.
- **Build/packaging questions** (why the cdylib gets renamed, what
  `extension-module` and `abi3-py39` actually do, why a `.dll` ends up
  named `.pyd`): `../docs/PYTHON_RUST_PACKAGING.md`.
- **Who calls this crate from the Python side**: `../azure/cosmos/_backend/rust.py`
  builds the `PreparedRequest` and parses the 4-tuple. Reading it
  alongside `lib.rs` shows exactly what every parameter and every return
  value carries.
- **Why a parity test is failing on the Rust path**: `../docs/V5_PARITY_AUDIT.md`
  enumerates every known driver-side gap with its tracking ID.

