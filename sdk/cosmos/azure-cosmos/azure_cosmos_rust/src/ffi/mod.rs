// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Binding functions called by the synchronous and asynchronous Python backends.
//!
//! For an order read, the Python wrapper passes a driver handle and
//! `PreparedRequest` to `read_item`. This module checks the operation name and
//! extracts the inputs. Helpers in `wire/` obtain the retained `CosmosDriver`
//! object, run the operation, and convert its result to a binding response tuple.
//! The Python wrapper then constructs `BackendResponse`; the tuple is not that
//! Python record yet.
//!
//! Most operations use prepared requests. Container metadata instead takes
//! explicit arguments, and feed-range subset comparison is local. Request
//! signing, service routing, and retries remain the Rust driver's responsibility.
//!
//! Async binding functions can check and extract inputs on the calling thread
//! before returning an awaitable. Rust operation work runs with the Tokio
//! runtime, not one Python worker thread per service request. See the shared
//! execution helpers for cancellation and credential-callback limits.
//!
//! Reuse docs/V5/VOCABULARY.md for terminology. `runtime.rs` explains which
//! CosmosDriverRuntime resources and CosmosDriver objects can be shared;
//! request inputs remain specific to each binding call.

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

/// Extract read/delete inputs: container link, typed partition key, settings,
/// and the required item id. For example, "order-42" comes from `item_id`,
/// not a body. The caller supplies errors that name its operation.
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

/// Extract create/upsert inputs, preferring `PreparedRequest.item_id`.
/// If that field is None or empty, read the id from body bytes. A missing
/// attribute or wrong type raises; it does not silently select the body.
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

/// Extract replace/patch inputs without deriving the target from the body.
/// `item_id` is required here; replace may subsequently use `item_self_link`.
/// A different id inside the body must not redirect the operation.
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

/// Extract settings, the offer resource id from `item_id`, and replacement body bytes.
/// The common extractor still reads the container link and typed partition key,
/// but offer execution does not use them to select a container or partition.
fn extract_replace_offer_inputs(prepared: &Bound<'_, PyAny>) -> PyResult<OfferReplaceInputs> {
    let (_container_link, _partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    let offer_id = extract_required_item_id(prepared, REPLACE_OFFER_ID_REQUIRED)?;
    Ok((modifiers, offer_id, body_bytes))
}

/// Extract the container link, typed partition key, and settings for read-all.
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

/// Extract the container link and typed partition key for feed-range calculation.
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
// Shared waiting and cancellation rules are in wire/driver_runner.rs.
// Credential callbacks use the separate path in credential.rs; returning an
// operation awaitable is not the job of AsyncTokenCredentialBridge.

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
