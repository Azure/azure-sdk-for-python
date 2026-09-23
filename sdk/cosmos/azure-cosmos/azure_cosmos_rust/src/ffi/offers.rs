// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Binding calls that read or replace throughput offer records.
//!
//! Offers belong to the account, not an item partition. The Python wrapper
//! prepares the query or replacement body before calling these functions.

use super::*;

/// Query the account's offers using PreparedRequest.body_bytes.
/// Common extraction reads the container link and typed partition key, but the
/// offer operation does not use them. Return a binding response tuple with an
/// `{"Offers":[...]}` body. The execution helper supplies query headers when absent.
#[pyfunction]
pub(crate) fn read_offer<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "read_offer")?;
    let (_container_link, _partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    run_read_offer_operation(py, driver_handle, modifiers, body_bytes, "read_offer")
}

/// Replace the offer named by the resource id in PreparedRequest.item_id.
/// The Python wrapper has already updated the offer body. Return the updated
/// record as body bytes in a binding response tuple, not an Offers list.
/// The execution helper requests response content for the throughput result.
#[pyfunction]
pub(crate) fn replace_offer<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "replace_offer")?;
    let (modifiers, offer_id, body_bytes) = extract_replace_offer_inputs(prepared)?;
    run_replace_offer_operation(
        py,
        driver_handle,
        modifiers,
        offer_id,
        body_bytes,
        "replace_offer",
    )
}
/// Async twin of `read_offer`.
#[pyfunction]
pub(crate) fn read_offer_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "read_offer")?;
    let (_container_link, _partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    run_read_offer_operation_async(py, driver_handle, modifiers, body_bytes, "read_offer")
}

/// Async twin of `replace_offer`.
#[pyfunction]
pub(crate) fn replace_offer_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "replace_offer")?;
    let (modifiers, offer_id, body_bytes) = extract_replace_offer_inputs(prepared)?;
    run_replace_offer_operation_async(
        py,
        driver_handle,
        modifiers,
        offer_id,
        body_bytes,
        "replace_offer",
    )
}
