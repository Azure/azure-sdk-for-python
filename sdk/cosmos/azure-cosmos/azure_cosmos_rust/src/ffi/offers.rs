// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Binding calls that read or replace throughput offer records.
//!
//! Offers belong to the account, not an item partition. The Python wrapper
//! prepares the query or replacement body before calling these functions.

use super::*;

/// Query the account's offers using PreparedRequest.body_bytes.
/// Read account-scoped settings without container or partition-key inputs.
/// Return a binding response tuple with an `{"Offers":[...]}` body.
/// The execution helper supplies query headers when absent.
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
    let (modifiers, body_bytes) = extract_offer_body_inputs(prepared)?;
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
    let (modifiers, body_bytes) = extract_offer_body_inputs(prepared)?;
    run_get_throughput_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        body_bytes,
        "get_throughput_async",
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
        "replace_throughput_async",
        timeout_seconds,
        include_attempts,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::headers::HeaderName;
    use pyo3::exceptions::PyTypeError;

    fn prepared_offer(py: Python<'_>) -> Bound<'_, PyAny> {
        let helper = PyModule::from_code_bound(
            py,
            r#"
class OfferRequest:
    protocol_version = 3
    op = "get_throughput"
    headers = {"x-app": "retained"}
    body_bytes = b'{"query":"SELECT * FROM c"}'
    item_id = "offer-rid"

    @property
    def container_link(self):
        raise AssertionError("offer extraction must not read container_link")

    @property
    def partition_key(self):
        raise AssertionError("offer extraction must not read partition_key")
"#,
            "offer_input_test.py",
            "offer_input_test",
        )
        .unwrap();
        let prepared = helper.getattr("OfferRequest").unwrap().call0().unwrap();
        prepared
            .setattr("settings", crate::wire::settings::test_settings(py))
            .unwrap();
        prepared
    }

    #[test]
    fn account_scoped_offer_inputs_preserve_settings_body_and_replacement_id() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let prepared = prepared_offer(py);
            let (modifiers, body) = extract_offer_body_inputs(&prepared).unwrap();
            assert_eq!(body, br#"{"query":"SELECT * FROM c"}"#);
            assert_eq!(
                modifiers.custom_headers[&HeaderName::from_static("x-app")].as_str(),
                "retained",
            );
            let (_, id, replacement) = extract_replace_throughput_inputs(&prepared).unwrap();
            assert_eq!(id, "offer-rid");
            assert_eq!(replacement, body);
        });
    }

    #[test]
    fn offer_exports_ignore_item_routing_before_validating_the_driver_handle() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let exports = PyModule::new_bound(py, "offer_input_exports").unwrap();
            crate::_rust(py, &exports).unwrap();
            for operation in ["get_throughput", "replace_throughput"] {
                for suffix in ["", "_async"] {
                    let prepared = prepared_offer(py);
                    prepared.setattr("op", operation).unwrap();
                    let name = format!("{operation}{suffix}");
                    let error = exports
                        .getattr(name.as_str())
                        .unwrap()
                        .call1((py.None(), prepared))
                        .unwrap_err();
                    assert!(error.is_instance_of::<PyTypeError>(py), "{name}: {error}");
                    assert!(
                        error.to_string().contains("_DriverHandle"),
                        "{name}: {error}"
                    );
                }
            }
        });
    }

    #[test]
    fn offer_extraction_still_rejects_invalid_required_inputs() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let prepared = prepared_offer(py);
            prepared.setattr("protocol_version", 0).unwrap();
            assert!(extract_offer_body_inputs(&prepared)
                .err()
                .unwrap()
                .is_instance_of::<PyValueError>(py));

            let prepared = prepared_offer(py);
            prepared
                .getattr("settings")
                .unwrap()
                .setattr("protocol_version", 0)
                .unwrap();
            assert!(extract_offer_body_inputs(&prepared)
                .err()
                .unwrap()
                .is_instance_of::<PyValueError>(py));

            let prepared = prepared_offer(py);
            prepared.setattr("body_bytes", "not bytes").unwrap();
            assert!(extract_offer_body_inputs(&prepared)
                .err()
                .unwrap()
                .is_instance_of::<PyTypeError>(py));

            let prepared = prepared_offer(py);
            prepared.setattr("item_id", py.None()).unwrap();
            assert!(extract_replace_throughput_inputs(&prepared)
                .err()
                .unwrap()
                .is_instance_of::<PyValueError>(py));
        });
    }
}
