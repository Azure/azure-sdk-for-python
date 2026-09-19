// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

// Raised when this error path has no driver response to return. That does not
// prove no request was sent: a failure or timeout can follow service work.
// The Python backend translates this RuntimeError subclass to ServiceResponseError;
// that translation does not run legacy retry policies. Callers format the Rust
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
        DriverTransportError,
        pyo3::exceptions::PyRuntimeError,
        "A Cosmos driver operation failed without a wire response (transport failure, \
         client-side validation, or a pre-HTTP timeout)."
    );
}
/// Raised when a driver error is returned without an accompanying response.
pub use transport_error::DriverTransportError;

#[allow(unexpected_cfgs)]
mod response_error {
    pyo3::create_exception!(
        azure_cosmos_rust,
        DriverResponseError,
        pyo3::exceptions::PyRuntimeError,
        "A metadata operation failed; args[0] contains its error response tuple."
    );
}
pub use response_error::DriverResponseError;

#[allow(unexpected_cfgs)]
mod unsupported_query_error {
    pyo3::create_exception!(
        azure_cosmos_rust,
        UnsupportedQueryFeatureError,
        pyo3::exceptions::PyRuntimeError,
        "The Cosmos driver cannot execute this query plan."
    );
}
/// Raised when the driver cannot run a query plan.
pub use unsupported_query_error::UnsupportedQueryFeatureError;
