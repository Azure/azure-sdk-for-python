// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

/// read_offer: read a container's provisioned throughput by querying the account's
/// `/offers` feed. Offers are an account-level, non-partitioned resource, so the
/// container link and partition-key header on the PreparedRequest are unused here;
/// the offer query JSON (the same filter the legacy path sends) rides in the body
/// and the matching offer records come back in the `{"Offers":[...]}` envelope.
/// Without it, get_throughput could not run on the rust driver and would stay on
/// the core-python path.
/// Async twin of `read_offer`.
#[pyfunction]
pub(crate) fn read_offer<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (_container_link, _partition_key_header, modifiers, body_bytes) =
        extract_query_inputs(prepared)?;
    run_read_offer_operation(py, handle, modifiers, body_bytes, "read_offer")
}

/// replace_offer: replace a container's provisioned throughput by PUTting the
/// already-mutated offer document to `/offers/{rid}`. Offers are an account-level,
/// non-partitioned resource, so -- like `read_offer` -- the container link and
/// partition-key header on the PreparedRequest are unused; the offer RID (which
/// offer to overwrite) rides in `PreparedRequest.item_id` and the mutated offer
/// document rides in the body. Returns the single updated offer document (the
/// single-document tuple shape), so `get_throughput`'s caller can read back the
/// applied RU/s. Without it, `replace_throughput` could not run on the rust driver
/// and would stay on the core-python path.
#[pyfunction]
pub(crate) fn replace_offer<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (modifiers, offer_id, body_bytes) = extract_replace_offer_inputs(prepared)?;
    run_replace_offer_operation(py, handle, modifiers, offer_id, body_bytes, "replace_offer")
}
#[pyfunction]
pub(crate) fn read_offer_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (_container_link, _partition_key_header, modifiers, body_bytes) =
        extract_query_inputs(prepared)?;
    run_read_offer_operation_async(py, handle, modifiers, body_bytes, "read_offer")
}

/// Async twin of `replace_offer`.
#[pyfunction]
pub(crate) fn replace_offer_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (modifiers, offer_id, body_bytes) = extract_replace_offer_inputs(prepared)?;
    run_replace_offer_operation_async(py, handle, modifiers, offer_id, body_bytes, "replace_offer")
}
