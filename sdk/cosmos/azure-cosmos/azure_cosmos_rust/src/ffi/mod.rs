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
//! Operation entry points extract fields from `PreparedRequest` and delegate to
//! runners under `wire/`; metadata helpers take explicit arguments instead.
//! Request signing, region routing, retries, and service execution remain in the
//! shared Rust driver. Local feed-range subset checks do not contact the service.
//!
//! Terminology used here (consistent with the rest of the backend):
//!   * binding      -- this compiled `_rust` extension Python calls into.
//!   * rust driver  -- the `CosmosDriver` driver that does the real Cosmos work.
//!   * driver handle -- the string naming which pooled rust driver a client uses.
//!   * shared Tokio runtime -- the binding-owned process-wide executor (in the
//!     binding) that runs the driver's async work; see `runtime.rs`. It is NOT
//!     the rust driver and NOT the driver runtime -- it is just the executor the
//!     driver's futures run on.
//!
//! What is shared, what is not, and why (all grounded in `runtime.rs`):
//!   * SHARED, per process: `RuntimeContext.tokio_rt` and `CosmosDriverRuntime`,
//!     initialized lazily by acquisition. The saved initialization result can
//!     also be an error. The Python awaitable bridge is a separate mechanism.
//!   * SHARED, per cache handle: a `CosmosDriver` and its routing state. The
//!     handle combines endpoint, credential fingerprint, and config fingerprint;
//!     see `runtime.rs` for hash and reference-counting limitations.
//!   * PER CALL: extracted body, item id, partition key, modifiers, and the
//!     constructed operation. These inputs are separate even when calls share
//!     a driver and its caches.

use crate::wire::partition_key_input::{extract_partition_key, BindingPartitionKey};
use pyo3::types::PyTuple;
use pyo3::{exceptions::PyValueError, prelude::*};

#[cfg(test)]
mod request_boundary_benchmark;

use azure_data_cosmos_driver::models::CosmosOperation;

use crate::wire::{
    execute_item_operation_async, execute_item_operation_sync, extract_account_prepared_modifiers,
    extract_body_bytes, extract_common_prepared_inputs, extract_create_item_id,
    extract_database_prepared_inputs, extract_read_feed_ranges_force_refresh,
    extract_required_item_id, run_create_database_operation, run_create_database_operation_async,
    run_delete_database_operation, run_delete_database_operation_async,
    run_feed_range_from_partition_key_operation, run_feed_range_from_partition_key_operation_async,
    run_is_feed_range_subset_operation, run_is_feed_range_subset_operation_async,
    run_list_databases_operation, run_list_databases_operation_async,
    run_query_databases_operation, run_query_databases_operation_async, run_query_operation,
    run_query_operation_async, run_read_all_items_operation, run_read_all_items_operation_async,
    run_read_database_operation, run_read_database_operation_async, run_read_feed_ranges_operation,
    run_read_feed_ranges_operation_async, run_read_offer_operation, run_read_offer_operation_async,
    run_replace_offer_operation, run_replace_offer_operation_async, RequestHeadersAndOptions,
};

const REPLACE_ITEM_ID_REQUIRED: &str = "replace_item: PreparedRequest.item_id is required (the id of the document to overwrite, resolved from the `item` argument)";
const REPLACE_OFFER_ID_REQUIRED: &str = "replace_offer: PreparedRequest.item_id is required (the offer RID to overwrite, resolved from the throughput offer's `_self`)";
const DELETE_ITEM_ID_REQUIRED: &str =
    "delete_item: PreparedRequest.item_id is required for delete operations";
const DELETE_DATABASE_ID_REQUIRED: &str =
    "delete_database: PreparedRequest.item_id is required (the id of the database to delete)";
const READ_ITEM_ID_REQUIRED: &str =
    "read_item: PreparedRequest.item_id is required for read operations";
const DELETE_ITEM_PARTITION_KEY_REQUIRED: &str = "delete_item requires an explicit partition key";
const READ_ITEM_PARTITION_KEY_REQUIRED: &str = "read_item requires an explicit partition key";
const PATCH_ITEM_ID_REQUIRED: &str = "patch_item: PreparedRequest.item_id is required (the id of the document to patch, resolved from the `item` argument)";

type CommonInputs = (String, BindingPartitionKey, RequestHeadersAndOptions);
type ItemInputs = (String, BindingPartitionKey, RequestHeadersAndOptions, String);
type ItemBodyInputs = (
    String,
    BindingPartitionKey,
    RequestHeadersAndOptions,
    String,
    Vec<u8>,
);
type BodyInputs = (String, BindingPartitionKey, RequestHeadersAndOptions, Vec<u8>);
type OfferReplaceInputs = (RequestHeadersAndOptions, String, Vec<u8>);
type ReadAllInputs = (String, BindingPartitionKey, RequestHeadersAndOptions);
type ReadFeedRangesInputs = (String, bool);
type FeedRangeFromPartitionKeyInputs = (String, BindingPartitionKey);

fn validate_prepared_operation(prepared: &Bound<'_, PyAny>, expected: &str) -> PyResult<()> {
    crate::wire::settings::validate_request_protocol(prepared)?;
    if prepared.getattr("op")?.extract::<String>()? != expected {
        return Err(PyValueError::new_err(format!(
            "PreparedRequest.op does not match binding operation {expected}"
        )));
    }
    Ok(())
}

/// Pull the common fields (container link, partition-key header, per-request
/// modifiers) plus a *required* item id off the PreparedRequest. Used by the
/// operations that send no body (delete, read), where the id comes from the request. Without a
/// single shared extractor each op would re-derive the same inputs and could
/// diverge on which fields it reads or which error it raises.
///
/// Both error messages are passed in by the caller so the failure names the
/// operation the customer actually called, rather than the shared extractor.
fn extract_item_inputs(
    prepared: &Bound<'_, PyAny>,
    item_id_error: &'static str,
    partition_key_error: &'static str,
) -> PyResult<ItemInputs> {
    let (container_link, partition_key, modifiers): CommonInputs =
        extract_common_prepared_inputs(prepared)?;
    if matches!(partition_key, BindingPartitionKey::Extract) {
        return Err(PyValueError::new_err(partition_key_error));
    }
    let item_id = extract_required_item_id(prepared, item_id_error)?;
    Ok((container_link, partition_key, modifiers, item_id))
}

/// Common fields plus the item body, then use the item id Python already
/// resolved on `PreparedRequest.item_id`. Callers that have not been updated may leave that field
/// unset, in which case `extract_create_item_id` reads the id from the body.
/// Without this shared extractor, create and upsert could disagree on that
/// preference and fallback behavior.
fn extract_create_body_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<ItemBodyInputs> {
    let (container_link, partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    let item_id = extract_create_item_id(prepared, &body_bytes)?;
    Ok((
        container_link,
        partition_key,
        modifiers,
        item_id,
        body_bytes,
    ))
}

/// Common fields plus the body plus a *required* item id taken from the request
/// (not the body). Used by replace and patch. Taking the id from the request is
/// the safety point: deriving it from the body could target the wrong item
/// if the body's id disagreed with the `item` argument the customer passed.
fn extract_item_body_inputs(
    prepared: &Bound<'_, PyAny>,
    error_message: &'static str,
) -> PyResult<ItemBodyInputs> {
    let (container_link, partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    let item_id = extract_required_item_id(prepared, error_message)?;
    Ok((
        container_link,
        partition_key,
        modifiers,
        item_id,
        body_bytes,
    ))
}

/// Common fields and body, shared by item writes, queries and offer reads.
fn extract_body_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<BodyInputs> {
    let (container_link, partition_key, modifiers): CommonInputs =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    Ok((container_link, partition_key, modifiers, body_bytes))
}

/// Inputs for `replace_offer`: per-request modifiers, the offer RID (required, from
/// `PreparedRequest.item_id`), and the mutated offer document body. Offers are an
/// account-level, non-partitioned resource, so the container link and partition-key
/// header on the PreparedRequest are unused here (matches `read_offer`).
fn extract_replace_offer_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<OfferReplaceInputs> {
    let (_container_link, _partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
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
    crate::wire::settings::validate_request_protocol(prepared)?;
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let force_refresh = extract_read_feed_ranges_force_refresh(prepared)?;
    Ok((container_link, force_refresh))
}

/// Fields for `feed_range_from_partition_key` (container link + partition-key header).
fn extract_feed_range_from_partition_key_inputs(
    prepared: &Bound<'_, PyAny>,
) -> PyResult<FeedRangeFromPartitionKeyInputs> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let partition_key = extract_partition_key(prepared)?;
    Ok((container_link, partition_key))
}

// ---------------------------------------------------------------------------
// Async entry points
// ---------------------------------------------------------------------------
//
// Async item entry points share input extraction and operation construction
// with their synchronous counterparts, but return awaitables rather than tuples.
//
// What "async" means here, precisely (grounded in `wire/`):
//   * Driver work is spawned on the binding's Tokio runtime. No Python worker
//     thread is reserved for the full operation, but argument extraction, result
//     conversion, and credential callbacks still acquire the GIL. Synchronous
//     credential acquisition is offloaded to a blocking worker; an async
//     credential is awaited through its Python bridge.
//   * The spawned Rust task is turned into a Python awaitable by
//     `pyo3_async_runtimes::tokio::future_into_py`. That is a library that maps
//     a Rust future onto an object the customer's asyncio event loop can
//     `await`; when the task finishes it resolves with the BackendResponse
//     tuple. This is NOT the credential bridge (`AsyncTokenCredentialBridge`) --
//     that one wraps an async *credential* into a sync `get_token` and is
//     unrelated to dispatching operations.
//   * Dropping the Rust bridge future drops its abort guard and requests task
//     cancellation. This does not guarantee immediate cleanup or undo service
//     work already submitted.
//
// The Python async backend (`aio/_backend/rust_backend.py`) dispatches to these.
//
// Layering (async path) -- same downward direction as the sync path, the tail
// end just returns to asyncio instead of blocking:
//
//     async Python client -> AsyncRustBackend (Python) -> a *_item_async here
//         -> look up the rust driver by handle (GIL held)
//         -> spawn the driver's work on the shared Tokio runtime
//         -> hand asyncio a Python awaitable (via pyo3-async-runtimes)
//         -> [driver future runs; credential callbacks can re-enter Python]
//         -> await resolves with the BackendResponse tuple

mod containers;
mod databases;
mod feed_range;
mod items;
mod offers;
mod query;

pub(crate) use containers::{
    create_container, create_container_async, delete_container, delete_container_async,
    get_container_metadata, get_container_metadata_async, list_containers, list_containers_async,
    query_containers, query_containers_async, read_container, read_container_async,
    replace_container, replace_container_async,
};
pub(crate) use databases::{
    create_database, create_database_async, delete_database, delete_database_async, list_databases,
    list_databases_async, query_databases, query_databases_async, read_database,
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
