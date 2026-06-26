// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! The six point-operation entry points: create / upsert / replace / delete /
//! read / patch an item.
//!
//! Each one only does the op-specific work -- pull its inputs off the
//! PreparedRequest, resolve the item id, and hand a CosmosOperation builder to
//! the shared runner. The per-op wire semantics are documented on the crate
//! header at the top of `lib.rs`.

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::models::CosmosOperation;

use crate::wire::{
    extract_body_bytes, extract_common_prepared_inputs, extract_item_id, extract_required_item_id,
    run_item_operation, run_item_operation_async,
};

// create_item: write-with-body; the id is read from the body.
#[pyfunction]
pub(crate) fn create_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_item_id(&body_bytes)?;

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

// upsert_item: like create, but maps to upsert so an existing (partition_key,
// id) is replaced instead of rejected with 409.
#[pyfunction]
pub(crate) fn upsert_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_item_id(&body_bytes)?;

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

// replace_item: write-with-body, but the URL id comes from
// PreparedRequest.item_id (not the body). Maps to OperationType::Replace
// (overwrite-only PUT): a missing target is a 404, never an insert.
#[pyfunction]
pub(crate) fn replace_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    // The URL id (which document to overwrite) comes from item_id, not the
    // body -- deriving it from the body could overwrite the wrong document if
    // the body's id disagreed with `item`.
    let item_id = extract_required_item_id(
        prepared,
        "replace_item: PreparedRequest.item_id is required (the id of the document to overwrite, resolved from the `item` argument)",
    )?;

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

// delete_item: bodiless; id from PreparedRequest.item_id; no content-response
// toggle (nothing to suppress on a DELETE).
#[pyfunction]
pub(crate) fn delete_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let item_id = extract_required_item_id(
        prepared,
        "delete_item: PreparedRequest.item_id is required for delete operations",
    )?;

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

// read_item: bodiless; id from PreparedRequest.item_id; conditional reads
// surface as HTTP 304, which the Python parser treats as success.
#[pyfunction]
pub(crate) fn read_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let item_id = extract_required_item_id(
        prepared,
        "read_item: PreparedRequest.item_id is required for read operations",
    )?;

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

// patch_item: write-with-operations. The body is the `PatchInstructions`
// payload (`{"operations": [...]}`), not a document; the URL id comes from
// PreparedRequest.item_id (like delete / read / replace). Maps to
// OperationType::Patch: the driver reads the item, applies the ops, and
// writes it back with an If-Match-guarded Replace. honor_content_response
// is true, so `no_response` applies to that inner Replace.
//
// The Python helper only routes the supported subset here; a
// `filter_predicate` or a caller-set precondition takes the legacy path,
// so neither rides on this prepared request.
#[pyfunction]
pub(crate) fn patch_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_required_item_id(
        prepared,
        "patch_item: PreparedRequest.item_id is required (the id of the document to patch, resolved from the `item` argument)",
    )?;

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

// ---------------------------------------------------------------------------
// Async entry points
// ---------------------------------------------------------------------------
//
// One `*_item_async` per operation, mirroring the sync six above but returning a
// Python awaitable (the binding spawns the driver future on the shared runtime
// and bridges it to asyncio -- no per-call worker thread). Input extraction is
// identical; only the runner differs (`run_item_operation_async`). The Python
// async backend (`aio/_backend/rust.py`) dispatches to these.

#[pyfunction]
pub(crate) fn create_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_item_id(&body_bytes)?;

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

#[pyfunction]
pub(crate) fn upsert_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_item_id(&body_bytes)?;

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

#[pyfunction]
pub(crate) fn replace_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_required_item_id(
        prepared,
        "replace_item: PreparedRequest.item_id is required (the id of the document to overwrite, resolved from the `item` argument)",
    )?;

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

#[pyfunction]
pub(crate) fn delete_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let item_id = extract_required_item_id(
        prepared,
        "delete_item: PreparedRequest.item_id is required for delete operations",
    )?;

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

#[pyfunction]
pub(crate) fn read_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let item_id = extract_required_item_id(
        prepared,
        "read_item: PreparedRequest.item_id is required for read operations",
    )?;

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

#[pyfunction]
pub(crate) fn patch_item_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let item_id = extract_required_item_id(
        prepared,
        "patch_item: PreparedRequest.item_id is required (the id of the document to patch, resolved from the `item` argument)",
    )?;

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

