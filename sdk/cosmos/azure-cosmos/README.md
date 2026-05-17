# Azure Cosmos DB SQL API client library for Python

This is the `azure-cosmos` Python package. It contains the usual Python
client (`CosmosClient`, `Container.create_item`, etc.) plus a Rust
backend that some operations can route through instead of the legacy
Python HTTP path.

This README only covers **building it locally and running the tests**.
For architecture and design, see the docs under `docs/`.

---

## Before you start

You need three things on your machine:

1. **Python 3.9 or newer.** Run `python --version` to check.
2. **A Rust toolchain**, because part of this package compiles from Rust.
   Install via [rustup](https://rustup.rs/); any stable version ≥ 1.75 works.
   Run `cargo --version` to check.
3. **Either the Cosmos DB Emulator running on `https://localhost:8081`,
   or a real Cosmos DB account.** The emulator is the simpler choice for
   local work — [download here](https://learn.microsoft.com/azure/cosmos-db/local-emulator).
   You only need this for the integration tests; pure unit tests run
   without it.

You also need a sibling clone of `azure-sdk-for-rust` next to this repo,
because the Rust driver lives there. Layout we expect:

```
<your repos folder>/
├── azure-sdk-for-python/   ← you are here
└── azure-sdk-for-rust/
```

If you don't have it, clone it now:

```powershell
cd ..\..\..\..\..        # back up to <your repos folder>
git clone https://github.com/Azure/azure-sdk-for-rust.git
cd azure-sdk-for-python\sdk\cosmos\azure-cosmos
```

The build will tell you immediately if it can't find that clone — see
"When the build complains" at the bottom.

---

## Set things up once

From this directory (`sdk/cosmos/azure-cosmos`):

```powershell
# A virtualenv. The build tool we use (maturin) refuses to install
# the compiled Rust extension into your system Python.
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# maturin = build tool that compiles Rust + drops the result into the
# Python package. The other three are test deps.
pip install -U pip maturin pytest pytest-asyncio
pip install -r dev_requirements.txt
```

You're now in a venv. Every command below assumes you stay in it.

---

## Build the Rust part

The Rust code compiles into a single file called `_rust.pyd` (Windows)
or `_rust.so` (Linux/macOS). It lands in `azure/cosmos/` next to the
`.py` files, and Python imports it as `azure.cosmos._rust`.

**One thing to know first:** if an old `_rust.pyd` is sitting in
`azure/cosmos/` from a previous build, Python will load *that* and
ignore your new code. Symptom is usually
`AttributeError: module 'azure.cosmos._rust' has no attribute 'init_client'`
at runtime, even though `init_client` is right there in the source.
So clean before you build:

```powershell
# 1. Wipe any old _rust.pyd.
Get-ChildItem azure\cosmos -Filter "_rust*" -Recurse -ErrorAction SilentlyContinue |
    Remove-Item -Force

# 2. Build + install in editable mode.
maturin develop
```

First build pulls and compiles a few hundred Rust crates; expect 5–10
minutes. Subsequent builds are seconds — Cargo caches everything in
`target/`.

Did it work? This one-liner imports the new module and prints what it
exposes:

```powershell
python -c "from azure.cosmos import _rust; print(sorted(a for a in dir(_rust) if not a.startswith('_')))"
# Expected: ['create_item', 'init_client']
```

If you see anything other than those two names, you have a stale `.pyd`
— re-run the cleanup step.

(If you can't use a venv for some reason, `maturin build --release`
followed by `Copy-Item target\release\azure_cosmos_rust.dll azure\cosmos\_rust.pyd -Force`
does the same thing by hand.)

---

## Smoke test: one round trip Python → Rust → Cosmos

Before running any test suite, run the smoke test. It uses **only** the
Rust path — no Python fallback — so if it succeeds you know the binding
is wired correctly all the way to your Cosmos endpoint.

```powershell
python smoke_test_rust_create_item.py
```

By default this points at the emulator and expects:

- a database named `pyo3test`
- inside it, a container named `items` partitioned on `/pk`

Create those once via the emulator's Data Explorer.

To point at a real account instead:

```powershell
$env:COSMOS_ENDPOINT = "<your-cosmos-account-uri>"
$env:COSMOS_KEY      = "<your-cosmos-account-key>"
python smoke_test_rust_create_item.py
```

A successful run ends with `OK — round trip Python → PyO3 → driver → Cosmos succeeded.`

---

## Run the parity suite (Rust path vs. Python path)

The parity suite calls `create_item` with the same input twice — once
through the legacy Python backend, once through the Rust backend — and
diffs the results. It's how we catch behaviour drift while the Rust
path is being built out.

```powershell
$env:ACCOUNT_URI = "https://localhost:8081"
$env:ACCOUNT_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

pytest tests/test_create_item_parity.py -v          # only failures show diffs
pytest tests/test_create_item_parity.py -v -s       # show diff for every call
```

If you don't set the env vars, the suite skips cleanly. If you set them
but never built the Rust extension, the suite skips with a "run maturin
develop" message.

Tests marked `@pytest.mark.skip(reason="C# pending")` cover known
driver- or binding-side gaps; they're skipped today and you remove the
marker by hand once the gap closes. `git grep "C5b pending"` finds
every test waiting on a specific item. See `docs/V5_PARITY_AUDIT.md`
for the full gap list.

---

## Run the unit tests (no emulator needed)

Everything under `tests/` that doesn't talk to Cosmos:

```powershell
pytest tests/ -q
```

Just the Rust-integration unit subset (the ones that exercise the
binding without making network calls):

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

## When the build complains

A few specific failure modes show up enough to be worth naming.

**`failed to read .../azure-sdk-for-rust/...Cargo.toml`** — your sibling
`azure-sdk-for-rust` clone is missing or in a different folder. Either
clone it next to `azure-sdk-for-python` (see the layout in "Before you
start"), or edit the three `path = ...` lines (one in
`azure_cosmos_rust/Cargo.toml`, two in `Cargo.toml`) to point at where
your clone actually lives.

**`expected struct azure_core::Error, found struct azure_core::Error`**
— same type name, two different copies. Means the binding crate and the
driver crate ended up pulling `azure_core` from two different sources.
Check `Cargo.toml` (the one in this directory): `azure_core` and
`azure_identity` must both be `path = ...` deps into the same external
`azure-sdk-for-rust` clone the driver is using. Don't mix `path` and
`git`.

**`AttributeError: module 'azure.cosmos._rust' has no attribute ...`** —
stale `_rust.pyd`. Clean and rebuild:

```powershell
Get-ChildItem azure\cosmos -Filter "_rust*" -Recurse | Remove-Item -Force
maturin develop
```

**Anything else, before reaching for `cargo clean`:**

```powershell
cargo check          # compiles without linking — fastest "did Rust break?" signal
```

If `cargo check` is green and you still can't run, the issue is in the
Python wiring or in maturin's install step, not in the Rust code.

`cargo clean` (nukes `target/`) is the last resort — it costs you the
5–10-minute first-build time again.

---

## What rebuilds when

- Edited Python? Nothing to rebuild. Editable install picks it up.
- Edited Rust (anything under `azure_cosmos_rust/` or in the external
  driver clone)? Run `maturin develop` again before `pytest`.
- Edited a `Cargo.toml`? `maturin develop` will pick it up; if you only
  changed deps, `cargo check` first is faster.

