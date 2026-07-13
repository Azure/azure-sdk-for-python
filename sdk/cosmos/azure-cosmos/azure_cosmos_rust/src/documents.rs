// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! The binding's front counter for the ten migrated operations:
//! create / upsert / replace / delete / read / patch / query_items /
//! read_all_items / read_feed_ranges / feed_range_from_partition_key -- each in a synchronous and an async version (20 functions
//! in all).
//!
//! Where this fits in the layering (same direction as a normal call):
//!
//!     Python client -> RustBackend (Python) -> a function here (binding)
//!         -> looks up the rust driver by handle
//!         -> runs the driver's work on the shared Tokio runtime
//!
//! Each function is deliberately tiny and identical in shape: (1) pull the
//! op-specific inputs off the PreparedRequest, (2) resolve the item id, (3) hand
//! a `CosmosOperation` builder to the shared runner (`run_item_operation` /
//! `run_item_operation_async` in `wire.rs`), which is what actually talks to the
//! rust driver. All the heavy lifting -- request signing, region routing,
//! retries -- lives in the rust driver; this file only adapts each op's inputs
//! into the one shape the runner expects. The per-op wire semantics are
//! documented on the crate header at the top of `lib.rs`.
//!
//! If this file did not exist, the rust backend would have no per-operation
//! doorways to call, and the subtle per-op differences that follow -- which are
//! exactly where data-loss bugs hide (see `replace_item`) -- would be scattered
//! across the Python backend or the driver instead of pinned down in one place.
//!
//! Terminology used here (consistent with the rest of the backend):
//!   * binding      -- this compiled `_rust` extension Python calls into.
//!   * rust driver  -- the `CosmosDriver` engine that does the real Cosmos work.
//!   * driver handle -- the string naming which pooled rust driver a client uses.
//!   * shared Tokio runtime -- the one process-wide Tokio thread pool (in the
//!     binding) that runs the driver's async work; see `runtime.rs`. It is NOT
//!     the rust driver and NOT the driver runtime -- it is just the executor the
//!     driver's futures run on.
//!
//! What is shared, what is not, and why (all grounded in `runtime.rs`):
//!   * SHARED, one per process: the Tokio runtime (`RuntimeContext.tokio_rt`)
//!     and the driver runtime (`CosmosDriverRuntime`, which owns the connection
//!     pool). Both are built once, lazily, on the first `init_client` and live
//!     until the process exits. One thread pool and one connection pool for the
//!     whole process means fewer threads and reused sockets, and -- on the async
//!     path -- no worker thread pinned per in-flight call.
//!   * SHARED, one per distinct `(endpoint, credential, config)`: the rust
//!     driver (`CosmosDriver`). Clients that match on all three get the *same*
//!     driver (the driver handle is that key); clients that differ get their
//!     own. So two `CosmosClient`s to the same account with the same credential
//!     and config share one driver and its routing state.
//!   * NOT shared -- per call: the inputs pulled off each PreparedRequest (body,
//!     item id, partition key, modifiers) and the `CosmosOperation` built from
//!     them. Each operation carries its own; nothing about one call leaks into
//!     another. The functions here hold no state -- they look the shared driver
//!     up by handle and run one operation on the shared runtime.

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::models::CosmosOperation;

use crate::wire::{
    extract_body_bytes, extract_common_prepared_inputs, extract_create_item_id,
    extract_read_feed_ranges_force_refresh, extract_required_item_id,
    run_feed_range_from_partition_key_operation, run_feed_range_from_partition_key_operation_async,
    run_item_operation, run_item_operation_async, run_query_operation, run_query_operation_async,
    run_read_all_items_operation, run_read_all_items_operation_async, run_read_feed_ranges_operation,
    run_read_feed_ranges_operation_async, OpModifiers,
};

const REPLACE_ITEM_ID_REQUIRED: &str = "replace_item: PreparedRequest.item_id is required (the id of the document to overwrite, resolved from the `item` argument)";
const DELETE_ITEM_ID_REQUIRED: &str =
    "delete_item: PreparedRequest.item_id is required for delete operations";
const READ_ITEM_ID_REQUIRED: &str =
    "read_item: PreparedRequest.item_id is required for read operations";
const PATCH_ITEM_ID_REQUIRED: &str = "patch_item: PreparedRequest.item_id is required (the id of the document to patch, resolved from the `item` argument)";

type CommonInputs = (String, String, OpModifiers);
type ItemInputs = (String, String, OpModifiers, String);
type ItemBodyInputs = (String, String, OpModifiers, String, Vec<u8>);
type QueryInputs = (String, String, OpModifiers, Vec<u8>);
type ReadAllInputs = (String, String, OpModifiers);
type ReadFeedRangesInputs = (String, bool);
type FeedRangeFromPartitionKeyInputs = (String, String);

/// Pull the common fields (container link, partition-key header, per-request
/// modifiers) plus a *required* item id off the PreparedRequest. Used by the
/// bodiless ops (delete, read), where the id comes from the request. Without a
/// single shared extractor each op would re-derive the same inputs and could
/// drift apart on which fields it reads or which error it raises.
fn extract_item_inputs(
    prepared: &Bound<'_, PyAny>,
    error_message: &'static str,
) -> PyResult<ItemInputs> {
    let (container_link, partition_key_header, modifiers): CommonInputs =
        extract_common_prepared_inputs(prepared)?;
    let item_id = extract_required_item_id(prepared, error_message)?;
    Ok((container_link, partition_key_header, modifiers, item_id))
}

/// Common fields plus the document body, then read the item id *out of the body*.
/// Used by create and upsert, where the customer's document carries its own id.
/// Without it, create/upsert would each have to dig the id out of raw JSON bytes
/// themselves and could disagree on how.
fn extract_create_body_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<ItemBodyInputs> {
    let (container_link, partition_key_header, modifiers): CommonInputs =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_create_item_id(prepared, &body_bytes)?;
    Ok((
        container_link,
        partition_key_header,
        modifiers,
        item_id,
        body_bytes,
    ))
}

/// Common fields plus the body plus a *required* item id taken from the request
/// (not the body). Used by replace and patch. Taking the id from the request is
/// the safety point: deriving it from the body could target the wrong document
/// if the body's id disagreed with the `item` argument the customer passed.
fn extract_item_body_inputs(
    prepared: &Bound<'_, PyAny>,
    error_message: &'static str,
) -> PyResult<ItemBodyInputs> {
    let (container_link, partition_key_header, modifiers): CommonInputs =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_required_item_id(prepared, error_message)?;
    Ok((
        container_link,
        partition_key_header,
        modifiers,
        item_id,
        body_bytes,
    ))
}

/// Common fields plus a required query body. Used by query_items (sync/async).
fn extract_query_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<QueryInputs> {
    let (container_link, partition_key_header, modifiers): CommonInputs =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    Ok((container_link, partition_key_header, modifiers, body_bytes))
}

/// Common fields for read-all feed operations (container link, partition-key
/// targeting header, and per-request modifiers).
fn extract_read_all_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<ReadAllInputs> {
    extract_common_prepared_inputs(prepared)
}

/// Fields for `read_feed_ranges` (container link + force-refresh flag).
fn extract_read_feed_ranges_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<ReadFeedRangesInputs> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let force_refresh = extract_read_feed_ranges_force_refresh(prepared)?;
    Ok((container_link, force_refresh))
}

/// Fields for `feed_range_from_partition_key` (container link + partition-key header).
fn extract_feed_range_from_partition_key_inputs(
    prepared: &Bound<'_, PyAny>,
) -> PyResult<FeedRangeFromPartitionKeyInputs> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let partition_key_header: String = prepared.getattr("partition_key_header")?.extract()?;
    Ok((container_link, partition_key_header))
}

/// create_item: write-with-body; the id is read from the body. Maps to
/// `CosmosOperation::create_item` (insert-only): an existing (partition key, id)
/// is rejected with 409, never overwritten. Without it there is no way to insert
/// a new document on the rust backend.
#[pyfunction]
pub(crate) fn create_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;

    run_item_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "create_item",
        true,
        move |item_ref| CosmosOperation::create_item(item_ref).with_body(body_bytes),
    )
}

/// upsert_item: like create, but maps to `upsert_item` so an existing
/// (partition key, id) is *replaced* instead of rejected with 409. Without it
/// customers could not do "insert-or-overwrite" in a single call on the rust
/// backend.
#[pyfunction]
pub(crate) fn upsert_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;

    run_item_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "upsert_item",
        true,
        move |item_ref| CosmosOperation::upsert_item(item_ref).with_body(body_bytes),
    )
}

/// replace_item: write-with-body, but the URL id (which document to overwrite)
/// comes from `PreparedRequest.item_id`, not the body. Maps to
/// `OperationType::Replace` (overwrite-only PUT): a missing target is a 404,
/// never a silent insert. Without it there is no safe overwrite -- and taking
/// the id from the body could overwrite the *wrong* document if the body's id
/// disagreed with the `item` argument.
#[pyfunction]
pub(crate) fn replace_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    // The URL id (which document to overwrite) comes from item_id, not the
    // body -- deriving it from the body could overwrite the wrong document if
    // the body's id disagreed with `item`.
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, REPLACE_ITEM_ID_REQUIRED)?;

    run_item_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "replace_item",
        true,
        move |item_ref| CosmosOperation::replace_item(item_ref).with_body(body_bytes),
    )
}

/// delete_item: bodiless; id from `PreparedRequest.item_id`; passes `false` for
/// the content-response toggle (a DELETE has nothing to return to suppress).
/// Without it there is no way to delete a single item on the rust backend.
#[pyfunction]
pub(crate) fn delete_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers, item_id) =
        extract_item_inputs(prepared, DELETE_ITEM_ID_REQUIRED)?;

    run_item_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "delete_item",
        false,
        CosmosOperation::delete_item,
    )
}

/// read_item: bodiless; id from `PreparedRequest.item_id`. A conditional read
/// surfaces as HTTP 304, which the Python parser treats as success. Without it
/// the single most common operation -- the point read -- would not work on the
/// rust backend.
#[pyfunction]
pub(crate) fn read_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers, item_id) =
        extract_item_inputs(prepared, READ_ITEM_ID_REQUIRED)?;

    run_item_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "read_item",
        false,
        CosmosOperation::read_item,
    )
}

/// patch_item: write-with-*operations*. The body is the `PatchInstructions`
/// payload (`{"operations": [...]}`), not a document; the URL id comes from
/// `PreparedRequest.item_id` (like delete / read / replace). Maps to
/// `OperationType::Patch`: the rust driver reads the item, applies the ops, and
/// writes it back with an If-Match-guarded Replace. `honor_content_response` is
/// true, so `no_response` applies to that inner Replace. Without it, partial
/// updates could not be pushed to the rust driver at all.
///
/// The Python helper only routes the supported subset here; a `filter_predicate`
/// or a caller-set precondition takes the legacy path, so neither rides on this
/// prepared request.
#[pyfunction]
pub(crate) fn patch_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, PATCH_ITEM_ID_REQUIRED)?;

    run_item_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "patch_item",
        true,
        move |item_ref| CosmosOperation::patch_item(item_ref).with_body(body_bytes),
    )
}

/// query_items: feed operation where `PreparedRequest.partition_key_header`
/// chooses the query scope. A non-empty header targets one logical partition;
/// `[]` targets the full container. The query JSON is read from
/// `PreparedRequest.body_bytes`. Without it, one page of query_items could not
/// run on the rust driver, and every query would stay on the core-python HTTP
/// path.
#[pyfunction]
pub(crate) fn query_items<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers, body_bytes) =
        extract_query_inputs(prepared)?;
    run_query_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        body_bytes,
        "query_items",
    )
}

/// read_all_items: feed operation that maps directly to the driver's read-feed
/// constructors (`read_all_items` for a specific partition key when provided,
/// `read_all_items_cross_partition` for full-container reads).
#[pyfunction]
pub(crate) fn read_all_items<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) = extract_read_all_inputs(prepared)?;
    run_read_all_items_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        "read_all_items",
    )
}

/// read_feed_ranges: enumerate the container's partition-key ranges (routing map)
/// and return them in the service-style `{"PartitionKeyRanges":[...]}` payload.
/// Without it, read_feed_ranges could not run on the rust driver and would stay
/// on the core-python path.
#[pyfunction]
pub(crate) fn read_feed_ranges<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, force_refresh) = extract_read_feed_ranges_inputs(prepared)?;
    run_read_feed_ranges_operation(
        py,
        handle,
        &container_link,
        force_refresh,
        "read_feed_ranges",
    )
}

/// feed_range_from_partition_key: compute the feed-range envelope for one partition key.
#[pyfunction]
pub(crate) fn feed_range_from_partition_key<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header) =
        extract_feed_range_from_partition_key_inputs(prepared)?;
    run_feed_range_from_partition_key_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        "feed_range_from_partition_key",
    )
}

// ---------------------------------------------------------------------------
// Async entry points
// ---------------------------------------------------------------------------
//
// One `*_item_async` per operation, mirroring the sync six above. Input
// extraction is byte-for-byte identical; the ONLY difference is the runner
// (`run_item_operation_async` instead of `run_item_operation`) and the return
// type: a Python awaitable instead of a ready tuple.
//
// What "async" means here, precisely (grounded in `wire.rs`):
//   * The driver work is `spawn`ed on the shared Tokio runtime -- the one
//     process-wide Tokio thread pool from `runtime.rs`, the same executor the
//     driver was built on (so its connection pool and timers stay put). Nothing
//     blocks a Python thread while the request is in flight.
//   * The spawned Rust task is turned into a Python awaitable by
//     `pyo3_async_runtimes::tokio::future_into_py`. That is a library that maps
//     a Rust future onto an object the customer's asyncio event loop can
//     `await`; when the task finishes it resolves with the BackendResponse
//     tuple. This is NOT the credential bridge (`AsyncTokenCredentialBridge`) --
//     that one wraps an async *credential* into a sync `get_token` and is
//     unrelated to dispatching operations.
//   * If the customer's `await` is cancelled (e.g. a client-side timeout), the
//     awaitable drops an abort guard that cancels the Tokio task, so the driver
//     operation actually stops (connection released, no more RU spent) instead
//     of running on with its result discarded.
//
// The Python async backend (`aio/_backend/rust.py`) dispatches to these.
//
// Layering (async path) -- same downward direction as the sync path, the tail
// end just returns to asyncio instead of blocking:
//
//     async Python client -> AsyncRustBackend (Python) -> a *_item_async here
//         -> look up the rust driver by handle (GIL held)
//         -> spawn the driver's work on the shared Tokio runtime
//         -> hand asyncio a Python awaitable (via pyo3-async-runtimes)
//         -> [request runs on the runtime; no Python thread held]
//         -> await resolves with the BackendResponse tuple

/// Async twin of `create_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn create_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;

    run_item_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "create_item",
        true,
        move |item_ref| CosmosOperation::create_item(item_ref).with_body(body_bytes),
    )
}

/// Async twin of `upsert_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn upsert_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;

    run_item_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "upsert_item",
        true,
        move |item_ref| CosmosOperation::upsert_item(item_ref).with_body(body_bytes),
    )
}

/// Async twin of `replace_item`: identical inputs and driver work (URL id from
/// the request, not the body), returns a Python awaitable instead of a tuple.
#[pyfunction]
pub(crate) fn replace_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, REPLACE_ITEM_ID_REQUIRED)?;

    run_item_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "replace_item",
        true,
        move |item_ref| CosmosOperation::replace_item(item_ref).with_body(body_bytes),
    )
}

/// Async twin of `delete_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn delete_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, item_id) =
        extract_item_inputs(prepared, DELETE_ITEM_ID_REQUIRED)?;

    run_item_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "delete_item",
        false,
        CosmosOperation::delete_item,
    )
}

/// Async twin of `read_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn read_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, item_id) =
        extract_item_inputs(prepared, READ_ITEM_ID_REQUIRED)?;

    run_item_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "read_item",
        false,
        CosmosOperation::read_item,
    )
}

/// Async twin of `patch_item`: identical inputs and driver work (body is the
/// PatchInstructions payload, URL id from the request), returns a Python
/// awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn patch_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, PATCH_ITEM_ID_REQUIRED)?;

    run_item_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        item_id,
        "patch_item",
        true,
        move |item_ref| CosmosOperation::patch_item(item_ref).with_body(body_bytes),
    )
}

/// Async twin of `query_items`: identical inputs/driver work; returns a Python
/// awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn query_items_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, body_bytes) =
        extract_query_inputs(prepared)?;
    run_query_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        body_bytes,
        "query_items",
    )
}

/// Async twin of `read_all_items`: identical inputs/driver work; returns a Python
/// awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn read_all_items_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) = extract_read_all_inputs(prepared)?;
    run_read_all_items_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        "read_all_items",
    )
}

/// Async twin of `read_feed_ranges`.
#[pyfunction]
pub(crate) fn read_feed_ranges_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, force_refresh) = extract_read_feed_ranges_inputs(prepared)?;
    run_read_feed_ranges_operation_async(
        py,
        handle,
        &container_link,
        force_refresh,
        "read_feed_ranges",
    )
}

/// Async twin of `feed_range_from_partition_key`.
#[pyfunction]
pub(crate) fn feed_range_from_partition_key_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header) =
        extract_feed_range_from_partition_key_inputs(prepared)?;
    run_feed_range_from_partition_key_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        "feed_range_from_partition_key",
    )
}
