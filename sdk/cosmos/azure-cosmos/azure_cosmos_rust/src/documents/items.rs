// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

/// Insert a new item, rejecting an existing item with the same id and partition key.
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
