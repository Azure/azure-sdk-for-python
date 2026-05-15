# `azure_cosmos_rust` — the PyO3 binding crate

This crate is the bridge between the Python SDK and the in-tree Rust
driver (`../azure_data_cosmos_driver/`). When compiled, it produces a
single `.pyd` / `.so` file that ships inside the Python wheel as
`azure/cosmos/_rust`. See
`../docs/PYTHON_RUST_BUILD_AND_PACKAGING.md` for the full build/packaging
story and `../docs/V5_CREATE_ITEM_IMPLEMENTATION.md` § "What still has
to land #0" for the design context.

## Status

End-to-end wired against the driver. The binding exposes two
Python-callable functions:

- `init_client(endpoint, master_key) -> handle`. Lazy-initialises the
  per-process Tokio runtime + `CosmosDriverRuntime`, builds the
  `CosmosDriver` for that endpoint, and returns a string handle the
  Python side stores.
- `create_item(handle, prepared) -> (status, sub_status, headers, body)`.
  Resolves the container, builds a typed `CosmosOperation::create_item`,
  block_on's `driver.execute_operation`, and converts the
  `CosmosResponse` into the 4-tuple the Python `BackendResponse` wraps.

Honored on the request path today (matches the driver's typed
`CosmosRequestHeaders` surface — see C1 in
`../docs/V5_CREATE_ITEM_IMPLEMENTATION.md`):

- `x-ms-activity-id` (parsed as UUID)
- `x-ms-session-token`

All other request headers in `PreparedRequest.headers`
(`x-ms-cosmos-intended-collection-rid`, trigger headers, indexing
directive, …) are dropped before the wire — the driver doesn't accept
them yet.

## Build and use locally

From the repo root (`sdk/cosmos/azure-cosmos`), in a Python venv:

```powershell
pip install maturin
maturin develop                        # compiles, drops _rust.pyd into azure/cosmos/
```

End-to-end smoke test (uses the local Cosmos DB Emulator by default;
override with `COSMOS_ENDPOINT` / `COSMOS_KEY` / `COSMOS_DB` /
`COSMOS_COLL` env vars):

```powershell
python smoke_test_rust_create_item.py
```

A successful run prints something like:

```
Endpoint : https://localhost:8081
Container: dbs/pyo3test/colls/items
Item id  : smoke-3f9c...
Calling RustBackend.create_item ...

status_code = 201
sub_status  = 0
body        = b'{"id":"smoke-3f9c...","pk":"smokeA","value":42,"_rid":"...",...}'

OK — round trip Python → PyO3 → driver → Cosmos succeeded.
```

Prerequisite: the database (`pyo3test`) and container (`items`,
partitioned on `/pk`) must already exist in the target account. The
binding does not create databases/containers.

## Known caveat — first build is slow and may need network

The driver pulls `azure_core` and `azure_identity` from the
[azure-sdk-for-rust](https://github.com/Azure/azure-sdk-for-rust)
repo via git deps declared in the workspace `Cargo.toml` at the repo
root. First `maturin develop` will download and compile a few hundred
crates and will take several minutes. Subsequent builds are cached.

If you have a local clone of `azure-sdk-for-rust`, replace the `git`
deps in `../Cargo.toml`'s `[workspace.dependencies]` with `path` deps
to skip the git fetch.

## File layout

```
azure_cosmos_rust/
├── Cargo.toml          # binding crate manifest; cdylib + pyo3 dep + driver dep
├── src/
│   └── lib.rs          # #[pymodule] fn _rust + create_item
└── README.md           # this file
```

## Next concrete piece of work

Replace the stub branch in `src/lib.rs::create_item` with the real
driver call. Sketch:

```rust
use azure_data_cosmos_driver::{
    driver::CosmosDriverRuntime,
    models::{AccountReference, CosmosOperation, ItemReference, PartitionKey},
    options::OperationOptions,
};

// Per-process singletons, lazy-initialised
static RUNTIME: OnceCell<CosmosDriverRuntime> = OnceCell::new();
// + Tokio runtime singleton

// Inside create_item, after extracting the PreparedRequest fields:
let driver = RUNTIME.get_or_init(...);
let container = driver.resolve_container(&db, &coll).await?;
let pk = parse_pk_header(&partition_key_header)?;   // string -> PartitionKey
let item_ref = ItemReference::from_name(&container, pk, "");
let op = CosmosOperation::create_item(item_ref).with_body(body_bytes);
let resp = py.allow_threads(|| { tokio_runtime.block_on(
    driver.execute_operation(op, OperationOptions::new())
)})?;
// then: convert resp.status / .headers / .body into the Python tuple
```

The two things this needs that the stub doesn't:
- A way to plumb account endpoint + auth across the binding (probably
  a new `init_client(endpoint, credential)` PyO3 function called from
  the Python client constructor).
- A real partition-key parser (string `"[\"customerA\"]"` → typed
  `PartitionKey`). C5a/C5b in the V5 doc's driver-team table track
  the cases this parser cannot represent yet.

