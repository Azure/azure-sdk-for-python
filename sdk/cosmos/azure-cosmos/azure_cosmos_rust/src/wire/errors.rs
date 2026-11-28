// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

// Raised when this error path has no driver response to return. That does not
// prove no request was sent: a failure or timeout can follow service work.
// The Python backend translates this RuntimeError subclass to ServiceResponseError;
// that translation does not run legacy retry policies. The point and item-feed
// converters use TimeoutError for the typed client-operation deadline (408/20008).
// Callers format the Rust
// error into a message, not a structured Python cause chain. Python can chain the
// binding exception, but it does not receive the original Rust error object.
// pyo3's `create_exception!` expansion references `cfg(feature = "gil-refs")`,
// a pyo3 feature this destination crate does not declare; the cfg is evaluated
// here (not in pyo3), producing a benign `unexpected_cfgs` warning from
// external-macro code. Scope the allow to just this generated item.
#[allow(unexpected_cfgs)]
mod transport_error {
    pyo3::create_exception!(
        azure_cosmos_rust,
        _DriverTransportError,
        pyo3::exceptions::PyRuntimeError,
        "A Cosmos driver operation failed without a response available to this error path. \
         This does not imply that no request was sent."
    );
}
/// Raised when a driver error is returned without an accompanying response.
pub use transport_error::_DriverTransportError;

#[allow(unexpected_cfgs)]
mod response_error {
    pyo3::create_exception!(
        azure_cosmos_rust,
        _DriverResponseError,
        pyo3::exceptions::PyRuntimeError,
        "A metadata operation failed; args[0] contains its error response tuple."
    );
}
pub use response_error::_DriverResponseError;

#[allow(unexpected_cfgs)]
mod unsupported_query_error {
    pyo3::create_exception!(
        azure_cosmos_rust,
        _UnsupportedQueryFeatureError,
        pyo3::exceptions::PyRuntimeError,
        "The Cosmos driver cannot execute this query plan."
    );
}
/// Raised when the driver cannot run a query plan.
pub use unsupported_query_error::_UnsupportedQueryFeatureError;

#[allow(unexpected_cfgs)]
mod authentication_error {
    pyo3::import_exception!(azure.core.exceptions, ClientAuthenticationError);
}
pub(super) use authentication_error::ClientAuthenticationError;

fn operation_panic(payload: Box<dyn std::any::Any + Send>) -> pyo3::PyErr {
    let message = payload
        .downcast_ref::<String>()
        .map(String::as_str)
        .or_else(|| payload.downcast_ref::<&str>().copied())
        .unwrap_or("non-string panic payload");
    pyo3::exceptions::PyRuntimeError::new_err(format!("Rust operation panicked: {message}"))
}

/// Discard the failed call on unwind; do not classify a panic as retryable transport failure.
pub(super) fn catch_operation_panic<T>(
    operation: impl FnOnce() -> pyo3::PyResult<T>,
) -> pyo3::PyResult<T> {
    std::panic::catch_unwind(std::panic::AssertUnwindSafe(operation))
        .unwrap_or_else(|payload| Err(operation_panic(payload)))
}

/// Normalize task panics without changing the caller's cancellation/error mapping.
pub(super) fn operation_join_error(
    error: tokio::task::JoinError,
    otherwise: impl FnOnce(tokio::task::JoinError) -> pyo3::PyErr,
) -> pyo3::PyErr {
    if error.is_panic() {
        operation_panic(error.into_panic())
    } else {
        otherwise(error)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::{
        exceptions::{PyKeyboardInterrupt, PyRuntimeError},
        prelude::*,
    };

    #[test]
    fn panic_payloads_normalize_but_python_base_exceptions_are_preserved() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            for (owned, expected) in [(true, "owned panic"), (false, "non-string panic payload")] {
                let error = catch_operation_panic::<()>(|| {
                    if owned {
                        std::panic::panic_any(String::from("owned panic"));
                    }
                    std::panic::panic_any(7_u32);
                })
                .unwrap_err();
                assert!(error.is_instance_of::<PyRuntimeError>(py));
                assert_eq!(
                    error.value_bound(py).str().unwrap().to_str().unwrap(),
                    format!("Rust operation panicked: {expected}"),
                );
            }
            let original = PyKeyboardInterrupt::new_err("stop");
            let expected = original.clone_ref(py);
            let error = catch_operation_panic::<()>(|| Err(original)).unwrap_err();
            assert!(error.value_bound(py).is(expected.value_bound(py)));
        });
    }

    #[tokio::test]
    async fn cancellation_is_not_reclassified_as_panic() {
        crate::test_support::prepare_python();
        let task = tokio::spawn(std::future::pending::<()>());
        task.abort();
        let error = task.await.unwrap_err();
        assert!(error.is_cancelled());
        Python::with_gil(|py| {
            let original = PyRuntimeError::new_err("existing cancellation message");
            let expected = original.clone_ref(py);
            let result = operation_join_error(error, |_| original);
            assert!(result.value_bound(py).is(expected.value_bound(py)));
        });
    }
}
