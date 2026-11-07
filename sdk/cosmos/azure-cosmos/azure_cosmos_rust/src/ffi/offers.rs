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
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn get_throughput<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "get_throughput")?;
    let (_container_link, _partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    run_get_throughput_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        body_bytes,
        "get_throughput",
        timeout_seconds,
        include_attempts,
    )
}

/// Replace the offer named by the resource id in PreparedRequest.item_id.
/// The Python wrapper has already updated the offer body. Return the updated
/// record as body bytes in a binding response tuple, not an Offers list.
/// The execution helper requests response content for the throughput result.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn replace_throughput<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "replace_throughput")?;
    let (modifiers, offer_id, body_bytes) = extract_replace_throughput_inputs(prepared)?;
    run_replace_throughput_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        offer_id,
        body_bytes,
        "replace_throughput",
        timeout_seconds,
        include_attempts,
    )
}
/// Async twin of `get_throughput`.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn get_throughput_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "get_throughput")?;
    let (_container_link, _partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    run_get_throughput_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        body_bytes,
        "get_throughput",
        timeout_seconds,
        include_attempts,
    )
}

/// Async twin of `replace_throughput`.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn replace_throughput_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "replace_throughput")?;
    let (modifiers, offer_id, body_bytes) = extract_replace_throughput_inputs(prepared)?;
    run_replace_throughput_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        offer_id,
        body_bytes,
        "replace_throughput",
        timeout_seconds,
        include_attempts,
    )
}
