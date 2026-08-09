// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

// A NEW exception type, defined here, for a driver operation that failed
// *without* a wire response (transport failure, client-side validation, a timeout
// before any HTTP round-trip). It keeps the existing exception contract intact in
// two ways: it subclasses `RuntimeError` (so any code that already catches
// `RuntimeError` keeps working), and the Python backend translates it into
// azure-core's `ServiceResponseError` so customer
// `except (ServiceRequestError, ServiceResponseError)` handlers and the SDK's
// transport-retry policies behave the same as on the legacy azure-core path,
// instead of seeing a bare `RuntimeError`. (This matches the
// `AsyncCredentialBridgeReentrantError(RuntimeError)` convention on the Python
// side.) One honest limitation: the driver's `CosmosError` carries no
// transport-vs-response classification, so the binding cannot faithfully split
// `ServiceRequestError` from `ServiceResponseError`; it maps to
// `ServiceResponseError`, preserves the typed Cosmos status (rendered by
// `CosmosError`'s Display) in the message, and chains the original error as the
// cause.
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
/// Raised when the driver fails before receiving a service response.
pub use transport_error::DriverTransportError;

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
