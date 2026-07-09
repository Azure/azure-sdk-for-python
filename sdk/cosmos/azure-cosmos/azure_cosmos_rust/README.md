# `azure_cosmos_rust` — the Rust crate behind `azure.cosmos._rust`

You're in a Rust crate. The Python SDK that lives one directory up has a
tiny chunk of code that isn't Python — it's Rust, and it lives here.
This README is for someone about to edit it.

If instead you want to install/build/test the Python SDK as a whole, the
README at `../README.md` is the one you want.

## What this crate is for

The Python SDK needs to call into a Rust HTTP driver for point operations
and client lifecycle. Python can't call Rust functions directly — the two
languages don't share a calling convention. So we have a small
"glue" crate, this one, that does the translation. When it's compiled,
you get one file: `_rust.pyd` on Windows, `_rust.so` on Linux/macOS.
That file gets dropped into `azure/cosmos/`, and the Python code
imports it as `azure.cosmos._rust`.

The binding is split across modules:

- `src/lib.rs` — module registration (`#[pymodule]` export list)
- `src/runtime.rs` — process runtime + driver cache + `init_client`/`close_client`
- `src/documents.rs` — point-op entry points (sync + async)
- `src/wire.rs` — request/response translation, header mapping, tuple shaping
- `src/credential.rs` — Python token-credential adapter for driver auth

## What Python actually sees

After a successful build, this is what Python can do:

```python
from azure.cosmos import _rust

handle = _rust.init_client("https://localhost:8081", master_key="<master key>")
status, sub_status, headers, body, diagnostics = _rust.create_item(handle, prepared)
```

Exports are registered in `src/lib.rs` (`#[pymodule] fn _rust(...)`).
Current surface:

- lifecycle: `init_client`, `close_client`
- point ops (sync): `create_item`, `upsert_item`, `replace_item`, `delete_item`, `read_item`, `patch_item`
- point ops (async): `*_item_async` for the same six operations
- diagnostics/provenance: `operation_count`, `DriverTransportError`, `__version__`

`init_client` requires **exactly one** auth input: either `master_key` or
`credential` (token credential), never both.

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
```

Workspace note: `azure_core` is pinned in the workspace Cargo file to the
same published version the driver uses, so the binding and driver share one
`azure_core` crate instance. If they diverge, Cargo type identity breaks
across the boundary and you get this class of error:

```
error[E0308]: mismatched types
   = note: expected struct `azure_core::Error`
              found struct `azure_core::Error`
```

Same name, two copies, no automatic conversion. Keep the driver dependency
and workspace `azure_core` pin aligned.

If your clones live somewhere other than side-by-side, edit the driver
`path = ...` line. Nothing else in this crate assumes that layout.

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

The Python helper layer hands us a `headers` dict plus prepared fields. The
binding translates those into:

- typed operation fields (`activity-id`, `session-token`)
- typed options (`responsePayloadOnWriteDisabled`, `excludedLocations`,
  `__overall_timeout_seconds`)
- custom-header passthrough for known wire keys and mapped option keys
  (for example triggers, indexing directive, priority, throughput bucket,
  intended collection rid, `if-match`, `if-none-match`, and already wire-named
  `x-ms-*` headers)

Unknown option keys remain lenient by default (legacy-compatible drop). For
drift detection in tests/CI, set `COSMOS_WIRE_STRICT=1` to fail fast on
untranslated non-allowlisted option keys.

## File layout

```
azure_cosmos_rust/
├── Cargo.toml          # cdylib output + pyo3 0.22 (extension-module, abi3-py39)
│                       # + external driver path dependency
├── src/
│   ├── lib.rs          # module export registration
│   ├── runtime.rs      # runtime/cache/client lifecycle
│   ├── documents.rs    # six point ops, sync + async
│   ├── wire.rs         # prepared request parsing + response tuple shaping
│   └── credential.rs   # Python token credential adapter
└── README.md           # this file
```

Start at `lib.rs` to see the exported surface, then read in this order:
`runtime.rs` -> `documents.rs` -> `wire.rs` -> `credential.rs`.

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
  builds the `PreparedRequest` and parses the backend tuple. Reading it
  alongside `lib.rs` shows exactly what every parameter and every return
  value carries.
- **Why a parity test is failing on the Rust path**: `../docs/V5_PARITY_AUDIT.md`
  enumerates every known driver-side gap with its tracking ID.
