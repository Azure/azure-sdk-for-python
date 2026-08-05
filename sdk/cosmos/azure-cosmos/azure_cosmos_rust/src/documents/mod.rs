// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Python-callable entry points for migrated operations, with synchronous and
//! asynchronous variants grouped by operation family.
//!
//! Where this fits in the layering (same direction as a normal call):
//!
//!     Python client -> RustBackend (Python) -> a function here (binding)
//!         -> looks up the rust driver by handle
//!         -> runs the driver's work on the shared Tokio runtime
//!
//! Each entry point extracts fields from `PreparedRequest` and delegates to the
//! matching runner under `wire/`. Request signing, region routing, retries, and
//! service execution remain in the shared Rust driver.
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
    extract_account_prepared_modifiers, extract_body_bytes, extract_common_prepared_inputs,
    extract_create_item_id, extract_database_prepared_inputs,
    extract_read_feed_ranges_force_refresh, extract_required_item_id,
    run_create_database_operation, run_create_database_operation_async,
    run_feed_range_from_partition_key_operation, run_feed_range_from_partition_key_operation_async,
    run_is_feed_range_subset_operation, run_is_feed_range_subset_operation_async,
    run_item_operation, run_item_operation_async, run_list_databases_operation,
    run_list_databases_operation_async, run_query_operation, run_query_operation_async,
    run_read_all_items_operation, run_read_all_items_operation_async, run_read_database_operation,
    run_read_database_operation_async, run_read_feed_ranges_operation,
    run_read_feed_ranges_operation_async, run_read_offer_operation, run_read_offer_operation_async,
    run_replace_offer_operation, run_replace_offer_operation_async, OpModifiers,
};

const REPLACE_ITEM_ID_REQUIRED: &str = "replace_item: PreparedRequest.item_id is required (the id of the document to overwrite, resolved from the `item` argument)";
const REPLACE_OFFER_ID_REQUIRED: &str = "replace_offer: PreparedRequest.item_id is required (the offer RID to overwrite, resolved from the throughput offer's `_self`)";
const DELETE_ITEM_ID_REQUIRED: &str =
    "delete_item: PreparedRequest.item_id is required for delete operations";
const READ_ITEM_ID_REQUIRED: &str =
    "read_item: PreparedRequest.item_id is required for read operations";
const PATCH_ITEM_ID_REQUIRED: &str = "patch_item: PreparedRequest.item_id is required (the id of the document to patch, resolved from the `item` argument)";

type CommonInputs = (String, String, OpModifiers);
type ItemInputs = (String, String, OpModifiers, String);
type ItemBodyInputs = (String, String, OpModifiers, String, Vec<u8>);
type QueryInputs = (String, String, OpModifiers, Vec<u8>);
type OfferReplaceInputs = (OpModifiers, String, Vec<u8>);
type ReadAllInputs = (String, String, OpModifiers);
type ReadFeedRangesInputs = (String, bool);
type FeedRangeFromPartitionKeyInputs = (String, String);

/// Pull the common fields (container link, partition-key header, per-request
/// modifiers) plus a *required* item id off the PreparedRequest. Used by the
/// bodiless ops (delete, read), where the id comes from the request. Without a
/// single shared extractor each op would re-derive the same inputs and could
/// diverge on which fields it reads or which error it raises.
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

/// Inputs for `replace_offer`: per-request modifiers, the offer RID (required, from
/// `PreparedRequest.item_id`), and the mutated offer document body. Offers are an
/// account-level, non-partitioned resource, so the container link and partition-key
/// header on the PreparedRequest are unused here (matches `read_offer`).
fn extract_replace_offer_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<OfferReplaceInputs> {
    let (_container_link, _partition_key_header, modifiers): CommonInputs =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let offer_id = extract_required_item_id(prepared, REPLACE_OFFER_ID_REQUIRED)?;
    Ok((modifiers, offer_id, body_bytes))
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

// ---------------------------------------------------------------------------
// Async entry points
// ---------------------------------------------------------------------------
//
// One `*_item_async` per operation, matching the sync six above. Input
// extraction is byte-for-byte identical; the ONLY difference is the runner
// (`run_item_operation_async` instead of `run_item_operation`) and the return
// type: a Python awaitable instead of a ready tuple.
//
// What "async" means here, precisely (grounded in `wire/`):
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

mod containers;
mod databases;
mod feed_range;
mod items;
mod offers;
mod query;

pub(crate) use containers::{resolve_container_metadata, resolve_container_metadata_async};
pub(crate) use databases::{
    create_database, create_database_async, list_databases, list_databases_async, read_database,
    read_database_async,
};
pub(crate) use feed_range::{
    feed_range_from_partition_key, feed_range_from_partition_key_async, is_feed_range_subset,
    is_feed_range_subset_async, read_feed_ranges, read_feed_ranges_async,
};
pub(crate) use items::{
    create_item, create_item_async, delete_item, delete_item_async, patch_item, patch_item_async,
    read_item, read_item_async, replace_item, replace_item_async, upsert_item, upsert_item_async,
};
pub(crate) use offers::{read_offer, read_offer_async, replace_offer, replace_offer_async};
pub(crate) use query::{query_items, query_items_async, read_all_items, read_all_items_async};
