# Azure Cosmos DB SQL API client library for Python

This package contains a Python SDK for the Azure Cosmos DB SQL API, with a
Rust-backed extension module (`azure.cosmos._rust`) compiled from the crates
in this repo.

This README is intentionally minimal and only covers **building the package
and running tests locally against the Cosmos DB Emulator**. For deeper
context (architecture, packaging internals, FFI, wheels, etc.) see the
build documents elsewhere in the repo.

---

## Prerequisites

- Python 3.9+
- Rust toolchain (stable, 1.75+) — install via [rustup](https://rustup.rs/)
- Local **Cosmos DB Emulator** running on `https://localhost:8081`
  ([download](https://learn.microsoft.com/azure/cosmos-db/local-emulator)),
  OR a real Cosmos DB account.

---

## One-time setup (per machine)

From `sdk/cosmos/azure-cosmos/`:

```powershell
# Create and activate a virtualenv (maturin requires one)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Build tooling + test dependencies
pip install -U pip maturin pytest pytest-asyncio
pip install -r dev_requirements.txt
```

---

## Build the Rust extension

**Always clean stale `_rust*` artifacts before rebuilding** — a leftover
`.pyd` from a previous binding shape will load and silently shadow the
new build. Symptoms: `AttributeError: module 'azure.cosmos._rust' has
no attribute 'init_client'` (or similar) at runtime.

```powershell
# 1. Wipe stale artefacts (safe to run any time)
Get-ChildItem azure\cosmos -Filter "_rust*" -Recurse -ErrorAction SilentlyContinue |
    Remove-Item -Force

# 2a. Inside a venv: build + install in editable mode
maturin develop

# 2b. Outside a venv (e.g. system Python): build a wheel, then copy the
#     .pyd straight into azure/cosmos/ since `maturin develop` requires
#     a venv. This skips pip entirely and gets the binding into the
#     editable source tree.
maturin build --release
Copy-Item target\release\azure_cosmos_rust.dll azure\cosmos\_rust.pyd -Force
```

First build downloads and compiles every Rust dependency (~5–10 min).
Subsequent builds are seconds because Cargo caches everything in `target/`.

Verify:

```powershell
python -c "from azure.cosmos import _rust; print(sorted([a for a in dir(_rust) if not a.startswith('_')]))"
# Expected: ['create_item', 'init_client']

dir azure\cosmos\_rust.pyd
```

If you see *different* attributes than the binding source declares, you have
a stale `.pyd` — re-run the cleanup step above.

---

## Smoke-test the binding (one round-trip to Cosmos)

The smoke test bypasses the Python helper layer and goes straight from
`RustBackend` → PyO3 → driver → Cosmos. Useful as a "does the binding
work at all?" check before running the full parity suite.

```powershell
# Defaults to the emulator's well-known endpoint+key
python smoke_test_rust_create_item.py
```

You need a database `pyo3test` and container `items` (partitioned on `/pk`)
in the target account. Create them once via the emulator's Data Explorer.

Override target via env vars if you want to hit a real account:

```powershell
$env:COSMOS_ENDPOINT = "<your-cosmos-account-uri>"
$env:COSMOS_KEY      = "<your-cosmos-account-key>"
python smoke_test_rust_create_item.py
```

---

## Run the create_item parity suite

Side-by-side comparison of every supported `create_item` input shape
against the core-python and rust backends. Skips cleanly if either the
emulator/account or the binding is missing.

```powershell
$env:ACCOUNT_URI = "https://localhost:8081"
$env:ACCOUNT_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

# Add -s to see the side-by-side report for every test:
pytest tests/test_create_item_parity.py -v -s
```

Without env vars: every parity test skips. With env vars but no binding:
skipped with a clear "run maturin develop" message.

---

## Run the full unit-test suite (no emulator needed)

```powershell
pytest tests/ -q
```

Or the rust-integration subset only:

```powershell
pytest tests/test_backend_wiring_unit.py `
       tests/test_item_helper_unit.py `
       tests/test_request_prep_unit.py `
       tests/test_response_parse_unit.py `
       tests/test_pk_wire_unit.py `
       tests/test_body_wire_unit.py `
       tests/test_auto_id_unit.py `
       tests/test_options_unit.py `
       tests/test_container_rid_helper_unit.py `
       tests/test_create_item_parity.py -q
```

---

## When a build misbehaves

```powershell
# 1. Wipe stale .pyd
Get-ChildItem azure\cosmos -Filter "_rust*" -Recurse | Remove-Item -Force

# 2. Did the Rust code even compile? (fastest signal, no link)
cargo check

# 3. Nuke all cached Cargo artefacts and start over
cargo clean

# 4. Rebuild + reinstall
maturin develop
```

After editing **Rust code**, rerun `maturin develop` before `pytest`.
Editing **Python code** needs no rebuild — editable install picks it up
directly.

