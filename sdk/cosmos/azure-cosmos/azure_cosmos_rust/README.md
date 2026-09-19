# `azure_cosmos_rust` — the Rust crate behind `azure.cosmos._rust`

You're in a Rust crate. The Python SDK that lives one directory up has a
tiny chunk of code that isn't Python — it's Rust, and it lives here.
This README is for someone about to edit it.

If instead you want to install/build/test the Python SDK as a whole, the
README at `../README.md` is the one you want.

## What this crate is for

The Python SDK needs to call into a Rust HTTP driver for item operations,
query/feed helpers, and client lifecycle. Python can't call Rust functions directly — the two
languages don't share a calling convention. So we have a small
"glue" crate, this one, that does the translation. When it's compiled,
you get one file: `_rust.pyd` on Windows, `_rust.so` on Linux/macOS.
That file gets dropped into `azure/cosmos/`, and the Python code
imports it as `azure.cosmos._rust`.

The binding is split across modules:

- `src/lib.rs` — module registration (`#[pymodule]` export list)
- `src/runtime.rs` — process runtime + driver cache + `acquire_driver_handle`/`release_driver_handle`
- `src/ffi/mod.rs` and its operation modules — entry points and shared input extraction
- `src/wire/mod.rs` and its operation modules — request/response translation
- `src/wire/driver_runner.rs` — shared lookup, execution, cancellation and tuple-conversion lifecycle
- `src/credential.rs` — Python token-credential adapter for driver auth

## What Python actually sees

This entire module is an SDK implementation detail, not a supported customer API.
Importability is not an access-control boundary within the Python process.
Customers use `CosmosClient`, not the entry points below. The wrapper translates
private native exceptions into the appropriate customer-facing exceptions.

After a successful build, this is how the wrapper calls the binding:

```python
from azure.cosmos import _rust

driver_handle = _rust.acquire_driver_handle("https://localhost:8081", master_key="<master key>")
status, sub_status, headers, body, diagnostics = _rust.create_item(driver_handle, prepared)
```

Exports are registered in `src/lib.rs` (`#[pymodule] fn _rust(...)`).
Current surface:

- lifecycle: `acquire_driver_handle`, `release_driver_handle`
- item ops (sync): `create_item`, `upsert_item`, `replace_item`, `delete_item`, `read_item`, `patch_item`
- item ops (async): `*_item_async` for the same six operations
- feed/query ops (sync): `query_items`, `read_feed_ranges`
- feed/query ops (async): `query_items_async`, `read_feed_ranges_async`
- retained feed paging: `fetch_page_with_cursor` and its `_async` counterpart,
  including the `query_items_change_feed` operation tag, with per-iterator
  `_ItemFeedCursor` storage.
  Public `query_items` also uses this retained cursor through `fetch_page_with_cursor`
  (not the older one-shot `query_items` binding helper). Python serializes the SQL
  body once per pager and the binding forwards those bytes without parsing and
  re-encoding them. Partition/feed-range scope and cross-partition permission
  travel separately as typed fields.
  The cursor reports `has_more` independently of `continuation_supported`, so a
  non-bookmarkable DISTINCT/non-streaming sort can still be fully enumerated.
  These properties read a snapshot of the last completed page and do not fail
  while a fetch holds the execution lock. Concurrent fetches still fail.
  Each Python pager creates its own cursor, including when two clients share a
  native driver. The driver's cache key is not the pager identity.
  Only the driver's two explicit unsupported-snapshot statuses suppress token minting;
  other snapshot failures remain errors. Python exposes query-bound `q1.` bookmarks
  for resumable queries and raises on bookmark access for non-resumable shapes.
  The wrapper checks the remaining budget after initialization; the native page
  deadline covers metadata, planning and execution. A
  cancelled or failed page invalidates its cursor. Public queries never replay on
  legacy Python after a Rust failure. Rebuild the extension after this cursor change.
  Change feed uses native change-feed operations, not a SQL query. The Python
  layer wraps its opaque driver token with backend/container/mode/scope metadata.
  The binding deliberately rejects multi-physical-partition change-feed scopes:
  it does not currently guarantee complete polling and checkpointing across
  those scopes. This is binding policy, not a rejection delegated to the driver.
- container deletion: `delete_container`, `delete_container_async`
- container replacement: `replace_container`, `replace_container_async`
- container reads: `read_container`, `read_container_async`
- process-wide measurement only: `_debug_operation_count`,
  `_debug_attempt_count`, `_debug_retry_count`. These cannot attribute work to a
  particular `CosmosClient`; concurrent callers contribute to the same totals.
- internal contract/runtime checks: `_request_settings_schema`,
  `_runtime_configuration`; neither is a client telemetry API.
- fault-test observation: `_debug_fault_injection_rule_hit_count`, scoped to the
  driver handle and rule rather than a particular Python client.
- private error translation: `_DriverTransportError`, `_DriverResponseError`,
  `_UnsupportedQueryFeatureError`.
- build provenance: `__version__` and the recorded source revisions.

Native operation entry points reject a mismatched `PreparedRequest.op` before
driver lookup. The request protocol remains structural and versioned; it is not
a sealed native request type. Deep immutability and a native/compact request
boundary are parked for a separate design and measurement pass.

Timeout names distinguish the customer's duration (`timeout`), the wrapper's
absolute monotonic deadline, and the remaining duration passed across the
boundary (`timeout_seconds`). `operation_timeout` bounds binding work including
metadata; `driver_timeout_policy` configures driver execution. The constructor's
`read_timeout` mapping still configures whole HTTP-attempt caps, not read
inactivity; renaming fields does not resolve that driver limitation.

Diagnostic formatting is also parked: `record_diagnostics` still updates
counters and eagerly formats the synthetic diagnostic response header.
Removing that work requires deciding when the header remains available.
Likewise, query/patch option snapshots still protect caller-owned mutable data.
The retained SQL-query path already reuses prepared body bytes rather than
parsing and reserializing the query in the binding. Synchronous driver
acquisition still blocks for initial native construction with the GIL released;
that is first-operation binding latency, not Python wrapper preparation time.

`acquire_driver_handle` requires **exactly one** auth input: either `master_key` or
`credential` (token credential), never both.

Offer and compatibility feed requests are now prepared directly by Python, without
legacy signing, generated dates/activity IDs, or a legacy session-cache lookup.
The existing native header/option contract is unchanged. Explicit activity/session
headers and service options still reach it; protocol defaults are generated by Rust.
`src/wire/offers.rs` supplies the offer-query content type and query marker.
Offer replacement receives the offer RID, not the owning database/container RID.
Existing offer timeouts remain driver-operation options, not a new absolute Python
deadline spanning the entire read-modify-write workflow.

Compatibility feed builders carry page size/continuation only in `PreparedQuery`.
Raw-header-only values are promoted; non-`None` typed options win conflicts.
The Python backend adapter materializes those headers once for the native entry.
The public retained item pagers and their bookmark contracts are unchanged.

Internal `get_container_metadata` and `get_container_metadata_async` return
`(rid, tuple(paths), kind, system_key)` rather than an HTTP response tuple.
The Python adapter constructs an immutable `ContainerMetadata` for explicit internal
lookups. Point operations no longer call these getters or stamp a Python-resolved RID.
The provider wrappers and their per-operation dictionaries have been removed.
Metadata success performs no JSON encode/decode and cannot update public response
headers. The driver remains the sole shared-cache owner.

Create/upsert/replace accept `PreparedRequest.partition_key=BindingPartitionKey("extract")` to extract
the key from `body_bytes` after native container resolution. An explicit key wins;
typed null and undefined remain distinct from extraction. Read/delete/patch require an
explicit key and never derive one from a patch payload. All six point operations
now enter the item binding once, without a separate metadata FFI call. This excludes
client/driver initialization and does not imply a single HTTP request.

`execute_item_on_driver` uses the same resolved definition for extraction and item
construction, with the existing timeout/cancellation scope and an expiry check after
extraction. Native metadata errors use the separate exception path below, so they
do not become item responses. The driver crate is unchanged; extraction ownership
is in the binding, and driver recreation recovery does not automatically re-extract
an omitted key against a changed definition.

`system_key=None` means unknown: the pinned driver does not retain `systemKey`.
Python preserves its existing fallback behavior; this refactor does not establish
legacy system-key parity. The partition-key kind is retained independently of
path count.

Metadata failures carrying a response raise `_DriverResponseError` with the error
tuple in `args[0]`. Python preserves its Cosmos exception contract and diagnostics,
without publishing metadata headers to client state. Response-less transport
errors retain `_DriverTransportError`; deadlines and cancellation keep their
existing behavior. Rebuild the extension for the renamed private entry points
and new exception export. There are no old-name compatibility aliases.

`runtime_configuration()` reports the initialized process runtime's proxy,
connection-timeout, and read-timeout settings, or `None` before initialization.
The Python wrapper uses this read-only snapshot to distinguish provisional client
reservations from settings already frozen by the native runtime. Failed startup
can release provisional reservations, but cannot reset an initialized runtime.
This also applies when runtime initialization succeeds and driver creation fails.
Rebuild the extension when updating this lifecycle integration.

Client hedging defaults to **disabled**, matching Python rather than the driver's
default-enabled behavior. `acquire_driver_handle` sets `AvailabilityStrategy::Disabled`
when `config` is absent or its `hedging_threshold_ms` is missing/`None`.
Python `availability_strategy=True` supplies 500 ms; a strategy dictionary
supplies its `threshold_ms`. A positive threshold enables hedging; an invalid
threshold is rejected. Supported per-request strategies still override the
client strategy, and the driver's `AZURE_COSMOS_HEDGING_ENABLED` and
`AZURE_COSMOS_HEDGING_ENABLED_OVERRIDE` environment overrides retain precedence.
Progressive `threshold_steps_ms` remains unsupported (migration pushback 25).

The returned `driver_handle` is a string registry key, not a `CosmosClient`
or the `CosmosDriver` itself. The private extension consistently names this
argument `driver_handle`, including keyword calls and `release_driver_handle`.
Internal callers using the old `handle` keyword must use `driver_handle`;
there is no compatibility alias. Positional calls are unchanged. Rebuild the
extension after this signature rename before validating native keyword calls.

Driver identity is binding-owned. It uses the parsed URL (normalizing host case,
default ports and the root slash without erasing meaningful paths or queries),
process-salted SHA-256 for master keys, token-credential object identity, and
typed configuration fields rather than Python `repr()`. The returned handle is
an opaque digest. `_driver_identity` and acquisition use the same computation;
identity lookup does not initialize a runtime or request a token.

Driver work and the Python async bridge share one Tokio executor. The binding
still owns one process-wide driver runtime: conflicting explicit proxy or
transport timeout settings raise rather than silently adopting another client's
values. The binding intentionally maps `read_timeout` to both complete-attempt
data-plane and metadata timeout caps; it is not a socket read-inactivity timer.

The token adapter qualifies its bounded cache by scopes and permits one active
refresh per adapter. A cancelled wait does not release a synchronous Python
refresh's ownership until that Python call finishes, preventing overlapping
refreshes and late overwrites. Async future cancellation remains cooperative.
The pinned `azure_core` 1.1.0 token options contain native method context, not
claims or a CAE flag; this binding does not claim to support those auth options.

The response body passed to Python is text JSON (or empty for operations such
as deletion). The shared operation-options builder explicitly disables binary
encoding: driver 0.8 defaults to binary responses, which Python's current JSON
parser cannot consume. Rebuilding against that driver must not silently change
the binding's response format.

Patch keeps the driver's `Auto` strategy. Both `patch_item` entry points accept
an optional keyword-only `timeout_seconds` containing the remaining Python
operation budget; this bounds native metadata resolution and execution together.
Caller If-Match headers become typed operation preconditions and are removed
from custom headers, keeping them separate from internal read/replace conditions.
The binding rejects patch If-None-Match and filtered patches rather than risk
dropping their conditions across the available execution strategies.
Python serializes canonical `incr` instructions before metadata access, copies
request options, and isolates success-hook body/header snapshots. Rebuild the
extension after updating this integration.

Filtered patch bodies and If-None-Match are rejected explicitly, with no legacy
replay. Forcing server-side PATCH alone does not establish predicate-aware retry
safety. Local point-operation validation/precondition failures with status 400/412
retain their status, substatus, message, and available diagnostics in the backend
tuple. Missing service headers are not fabricated. Other response-less failures
retain the existing `_DriverTransportError` mapping.

Container deletion takes database/container names from the prepared request.
The binding asks the Rust driver to resolve the container, then execute DELETE;
Python does not fetch metadata. Conditions and customer headers apply only to
DELETE, and an explicit timeout covers the lookup and deletion together.

Container replacement follows the same resolution pattern, using the shared
lookup-options and timeout helpers. Its conditions and customer headers apply
only to PUT, never the metadata GET. One timeout covers lookup plus replacement.
Both Python return shapes need the returned container ID, so the binding requests
a response body even when `return_properties` is false. No Rust-driver changes
are required for this integration; avoiding the cold-cache lookup remains a
driver optimization.

Container reads use `CosmosOperation::read_container_by_name` directly; unlike
delete/replace, they need no separate preliminary resolution step. The existing
request-header translations carry quota and partition-statistics flags, and the
returned body/headers retain the requested statistics and quota/usage values.
Python now allows these options through its Rust eligibility gate and rejects
unsupported settings instead of silently replaying the read through legacy
Python. Response-hook deep-copy isolation is also handled in Python. No new
driver API or binding rebuild is needed for that integration. This does not
resolve the broader original-HTTP-response-header gap.

## Where the Rust driver actually lives

This crate inherits the driver source from the outer workspace:

```toml
azure_data_cosmos_driver = { workspace = true, features = ["__internal_native_query_plan", "fault_injection"] }
```

The driver is not stored in this repository. The workspace pins a Git revision
of `azure-sdk-for-rust`, and Cargo downloads that exact source. A neighboring
Rust checkout is no longer required for the default build.

```toml
# ../Cargo.toml, under [workspace.dependencies]
azure_data_cosmos_driver = { git = "https://github.com/Azure/azure-sdk-for-rust", rev = "075917d6cb987055dfa93e31296b261574456b66" }
```

Normal builds and development dependencies share that source. The in-memory
emulator feature remains a development dependency, not a normal wheel feature.

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

To work on unpublished driver changes locally, use a deliberate local source
override and keep it out of the pipeline configuration. See
`../docs/build_and_release.md` for the prototype choices and remaining work.

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

The workspace root holds the shared dependencies and lock file. Cargo can also
find this workspace when run inside the binding directory.

The prototype's `../rust-toolchain.toml` selects `ms-prod-1.97`, which requires
Microsoft's `msrustup` toolchain manager. Public `rustup` cannot install that
channel. A deliberate public-toolchain override is only a local check, not
proof that the pipeline's selected toolchain works.

Once `cargo check` is green, `maturin develop` (back at the outer
directory) is what actually produces a fresh `_rust.pyd` and copies it
into `azure/cosmos/` so Python can import it.

## What this binding currently forwards on the wire

The Python helper layer supplies caller/default `headers` and validated frozen
`RequestSettings`. `wire/settings.rs` reads individual attributes, not an option
dictionary, and performs final service-header serialization or typed driver mapping.

- Common settings: priority, throughput bucket, activity/session identifiers,
  no-response, exclusions, hedging, consistency and request duration.
- Item settings: conditions, trigger tuples, indexing and cache staleness.
- Query settings: paging, query marker, metrics, scan and query-plan controls.
- Resource settings: explicit RID overrides, throughput, autoscale and resource controls.

Python retains compatibility option-name normalization and existing omission and
header-precedence rules. It no longer stringifies service settings only for Rust
to parse them again. Exclusions preserve inheritance versus explicit empty tuples;
hedging preserves inheritance, disabled and enabled-with-threshold states.
Absolute deadlines are keyword-only arguments of Python `execute` / `execute_pages`,
not fields on prepared records. They remain separate from `settings.timeout_seconds`;
the binding argument carries the remaining monotonic budget on supported execution
paths. Sync/async page adapters preserve settings and put page controls in
`settings.query`. This Python-only ownership change leaves native protocol 3 unchanged.

Unknown normalized Rust options always fail explicitly, independent of
`COSMOS_WIRE_STRICT`. The old dictionary reader and compact hedging parser are gone.
Private protocol version 3 requires a matching Python package and rebuilt extension.
`_request_settings_schema()` exports field inventories derived from native readers;
Python checks agreement before driver acquisition. Older private request shapes
are rejected before I/O, not supported through a compatibility shim. Legacy
backend use remains available when only the settings schema is incompatible.

The request envelope now carries `BindingPartitionKey(kind, values)` and its own
protocol version. `wire/partition_key_input.rs` extracts native scalars directly into
`PartitionKeyValue`: no JSON text is used to transport explicit keys through PyO3.
Extraction, cross-partition scope, empty sentinels and explicit empty sequences
have distinct kinds. Null and the private undefined component are distinct, too.
The schema inventory includes `BindingPartitionKey`, and sparse feed-range readers
also validate the envelope version.

Retained query/change-feed bodies no longer contain encoded partition-key strings.
Their persisted bookmark identities remain compatible. Customer-supplied HTTP
headers and persisted bookmarks still require JSON decoding at those external
boundaries; native request extraction does not. Legacy wire serializers live in
the legacy/parity helpers, with Rust JSON key parsers compiled only for tests.
The driver's actual HTTP-header serialization remains necessary.

Singleton document writes are serialized once in the Python wrapper as
`SerializedDocument(body_id, body_bytes)` before backend dispatch. Patch has its
own operations serializer; all four builders share bytes-only request construction.
Builders neither re-read caller payloads nor serialize fallbacks. Create uses a
shallow top-level copy, not a recursive clone. Replacement target IDs remain separate
from body IDs, and omitted keys are still extracted natively from the outgoing bytes.
The envelope remains protocol 3.

The retained wrapper codec preserves ASCII escaping, compact UTF-8, UTF-16 pair
normalization and escaping of unpaired surrogates. The latter is encoding parity
only: native automatic key extraction still rejects unpaired surrogates when it
parses a complete `serde_json::Value`, even in properties unrelated to the key.
No character replacement or silent extraction fallback is introduced.

This is Python/binding cleanup only: it neither extends driver capabilities nor
establishes a measured performance improvement.

## Naming and page dispatch

The Python backend is the dispatch object; the Rust driver is the native
`CosmosDriver`; the process-wide runtime has a separate lifetime and policy.
Python driver-client registration does not acquire a native handle.

The wrapper now passes synchronous `build_request` callbacks in both modes.
Native exports retain `_async` where sync and async functions share this module.
`_ItemFeedCursor` and `fetch_page_with_cursor` / `fetch_page_with_cursor_async`
serve retained item queries, read-all and change feeds. Stateless pages use their
own dispatch table; cursor dispatch depends on operation plus a non-`None`
`PreparedQuery.cursor`. The pager creates its concretely typed `_ItemFeedCursor`
lazily through the backend factory and owns its release; execution no longer
inserts it into a Python dictionary. Frozen `QueryScope` preserves the existing
wire payload and bookmark identity. The old read-all cursor names and native
change-feed aliases are removed. Public Python API names remain unchanged.
Install a matching rebuilt extension for the export renames; the request schema
remains protocol 3. Moving cursor ownership requires no additional native rebuild.

Temporary migration policy is centralized in Python `capabilities.py`, separate
from the binding dispatch tables. Only permitted pre-dispatch compatibility
decisions may use legacy; native execution/query-planning failures never replay.
The unused Python batch contracts and stubs are removed, not the public batch API.

## File layout

```
azure_cosmos_rust/
├── Cargo.toml          # cdylib output + pyo3 0.22 (extension-module, abi3-py310)
│                       # + workspace-pinned external driver
├── src/
│   ├── lib.rs          # module export registration
│   ├── runtime.rs      # runtime/cache/client lifecycle
│   ├── ffi/            # Python entry points, sync + async
│   ├── wire/           # prepared request parsing + response tuple shaping
│   │   └── item_feed.rs # shared retained item-feed cursor
│   └── credential.rs   # Python token credential adapter
└── README.md           # this file
```

Start at `lib.rs` to see the exported surface, then read in this order:
`runtime.rs` -> `ffi/mod.rs` -> `wire/mod.rs` -> `wire/item_feed.rs` -> `credential.rs`.

## Where to look when you're stuck

- **PyO3 syntax confusion** (what `Bound<'py, T>` means, why some
  signatures have `'py` and others don't, what `into_any().unbind()`
  does, why `PyDict::new` got renamed to `PyDict::new_bound`, what
  `py.allow_threads` actually releases): `../docs/PY03-BASICS.md`. Read
  this before changing any function signature or any line that
  constructs a Python object from Rust.
- **Build/packaging questions** (why the cdylib gets renamed, what
  `extension-module` and `abi3-py310` actually do, why a `.dll` ends up
  named `.pyd`): `../docs/PYTHON_RUST_PACKAGING.md`.
- **Who calls this crate from the Python side**: `../azure/cosmos/_backend/binding.py`
  builds the `PreparedRequest` and parses the backend tuple. Reading it
  alongside `lib.rs` shows exactly what every parameter and every return
  value carries.
- **Why a parity test is failing on the Rust path**: `../docs/V5_PARITY_AUDIT.md`
  enumerates every known driver-side gap with its tracking ID.
