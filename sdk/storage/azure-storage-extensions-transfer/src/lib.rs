// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

//! PyO3 native module for accelerated Azure Blob Storage transfers.
//!
//! Provides `upload_blob` and `download_blob` functions that delegate to the
//! `azure_storage_blob` Rust crate for high-performance parallel transfers.

mod credentials;
mod download;
mod upload;

#[cfg(test)]
#[path = "../tests/rust/support.rs"]
mod test_support;

use std::num::NonZero;
use std::sync::Arc;

use azure_core::credentials::TokenCredential;
use azure_core::http::{new_http_client, HttpClientOptions, Transport, Url};
use azure_storage_blob::{BlobClient, BlobClientOptions};
use once_cell::sync::{Lazy, OnceCell};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use tokio::runtime::Runtime;

use credentials::get_cached_credential;
use download::{download_blob, NativeDownloadStream};
use upload::upload_blob;

/// Shared tokio runtime — created once, reused across all calls to avoid
/// per-call overhead of spawning a new runtime.
static RUNTIME: OnceCell<Runtime> = OnceCell::new();

fn get_runtime() -> PyResult<&'static Runtime> {
    RUNTIME.get_or_try_init(|| {
        Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create tokio runtime: {e}")))
    })
}

/// Shared HTTP transport — a single connection pool reused by every `BlobClient` we build.
///
/// Each `BlobClient` otherwise constructs its own HTTP client (and therefore its own
/// connection pool), so building a fresh client per transfer would repeat TLS handshakes and
/// discard warm connections. Injecting one shared transport keeps the pool warm across calls.
///
/// Automatic decompression is disabled to guarantee the crate receives raw bytes for
/// partitioned/ranged downloads (matching the storage default for range requests).
static SHARED_TRANSPORT: Lazy<Transport> = Lazy::new(|| {
    Transport::new(new_http_client(Some(HttpClientOptions {
        automatic_decompression: false,
    })))
});

/// Custom error wrapper for mapping `azure_core::Error` to Python exceptions.
struct AzureError(azure_core::Error);

impl From<AzureError> for PyErr {
    fn from(err: AzureError) -> PyErr {
        let mut current: Option<&(dyn std::error::Error + 'static)> = Some(&err.0);
        while let Some(error) = current {
            if let Some(python_error) = error.downcast_ref::<PyErr>() {
                return Python::attach(|py| python_error.clone_ref(py));
            }
            current = error.source();
        }
        PyValueError::new_err(format!("Azure Storage error: {}", err.0))
    }
}

impl From<azure_core::Error> for AzureError {
    fn from(e: azure_core::Error) -> Self {
        Self(e)
    }
}

/// Build a `BlobClient` from a fully-qualified blob URL and optional token provider.
///
/// `blob_url` must be the complete, already percent-encoded blob URL
/// (e.g. `https://account.blob.core.windows.net/container/blob`), optionally including a
/// SAS token in the query string. It is parsed and used as-is — `BlobClient::new` expects
/// the caller to have encoded it correctly, and `Url::parse` preserves existing
/// percent-encoding, so no double-encoding occurs.
///
/// If `token_provider` is provided, `credential_id` is required and selects the cached
/// credential (fetching a token from Python once and reusing it). If the `blob_url` contains
/// a SAS token in the query string, pass `token_provider=None`.
///
/// Every client is built with the shared transport so connection pooling persists across
/// transfers regardless of authentication mode.
fn build_blob_client(
    blob_url: &str,
    token_provider: Option<Py<PyAny>>,
    credential_id: Option<usize>,
) -> PyResult<BlobClient> {
    let mut options = BlobClientOptions::default();
    options.client_options.transport = Some(SHARED_TRANSPORT.clone());
    build_blob_client_with_options(blob_url, token_provider, credential_id, options)
}

fn build_blob_client_with_options(
    blob_url: &str,
    token_provider: Option<Py<PyAny>>,
    credential_id: Option<usize>,
    options: BlobClientOptions,
) -> PyResult<BlobClient> {
    let blob_url =
        Url::parse(blob_url).map_err(|e| PyValueError::new_err(format!("Invalid URL: {e}")))?;

    let credential: Option<Arc<dyn TokenCredential>> = match token_provider {
        Some(provider) => {
            let credential_id = credential_id.ok_or_else(|| {
                PyValueError::new_err("credential_id is required when token_provider is provided")
            })?;
            Some(get_cached_credential(provider, credential_id))
        }
        None => None,
    };

    let client = BlobClient::new(blob_url, credential, Some(options)).map_err(AzureError::from)?;
    Ok(client)
}

const DEFAULT_PARTITION_SIZE: u64 = 4 * 1024 * 1024;

fn transfer_sizes(
    max_concurrency: Option<usize>,
    partition_size: Option<u64>,
) -> Result<(NonZero<usize>, NonZero<u64>), String> {
    let concurrency = max_concurrency.unwrap_or_else(|| {
        std::thread::available_parallelism()
            .map(NonZero::get)
            .unwrap_or(8)
    });
    let concurrency = NonZero::new(concurrency)
        .ok_or_else(|| "max_concurrency must be greater than zero.".to_string())?;
    let partition_size = NonZero::new(partition_size.unwrap_or(DEFAULT_PARTITION_SIZE))
        .ok_or_else(|| "Chunk/block size must be greater than zero.".to_string())?;
    Ok((concurrency, partition_size))
}

/// Python module definition.
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(upload_blob, m)?)?;
    m.add_function(wrap_pyfunction!(download_blob, m)?)?;
    m.add_class::<NativeDownloadStream>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_support::{response, MockHttpClient};
    use azure_core::error::ErrorKind;
    use azure_core::http::StatusCode;

    #[test]
    fn transfer_defaults_and_explicit_sizes() {
        let (parallel, partition) = transfer_sizes(None, None).unwrap();
        assert!(parallel.get() > 0);
        assert_eq!(partition.get(), 4 * 1024 * 1024);
        for (parallel, partition) in [(1, 1), (3, 17)] {
            let actual = transfer_sizes(Some(parallel), Some(partition)).unwrap();
            assert_eq!((actual.0.get(), actual.1.get()), (parallel, partition));
        }
    }

    #[test]
    fn zero_transfer_sizes_are_rejected() {
        for (parallel, partition) in [(Some(0), None), (None, Some(0))] {
            assert!(transfer_sizes(parallel, partition).is_err());
        }
    }

    #[test]
    fn runtime_is_shared_and_executes_tasks() {
        let first = get_runtime().unwrap();
        assert!(std::ptr::eq(first, get_runtime().unwrap()));
        assert_eq!(first.block_on(async { 42 }), 42);
    }

    #[test]
    fn client_validation_does_not_send_requests() {
        Python::initialize();
        Python::attach(|py| {
            let mock = MockHttpClient::new(|request| panic!("Unexpected request: {request:?}"));
            assert!(
                build_blob_client_with_options("not a URL", None, None, mock.options()).is_err()
            );
            let provider = py.None();
            assert!(build_blob_client_with_options(
                "https://account.blob.core.windows.net/container/blob",
                Some(provider),
                None,
                mock.options(),
            )
            .is_err());
            assert!(mock.requests().is_empty());
        });
    }

    #[test]
    fn client_preserves_encoded_url_and_sas() {
        let url =
            "https://account.blob.core.windows.net/container/a%20b%2Fc?sv=2026-02-06&sig=a%2Bb%3D";
        let mock = MockHttpClient::new(|request| {
            assert_eq!(request.method, "GET");
            assert_eq!(request.url.path(), "/container/a%20b%2Fc");
            assert_eq!(
                request
                    .url
                    .query_pairs()
                    .find(|(key, _)| key == "sig")
                    .unwrap()
                    .1,
                "a+b="
            );
            response(StatusCode::Ok, &[("content-length", "0")], Vec::new())
        });
        let client = build_blob_client_with_options(url, None, None, mock.options()).unwrap();
        get_runtime()
            .unwrap()
            .block_on(client.download(None))
            .unwrap();
        assert_eq!(mock.requests().len(), 1);
    }

    #[test]
    fn module_registers_transfer_bindings() {
        Python::initialize();
        Python::attach(|py| {
            let module = PyModule::new(py, "_native").unwrap();
            _native(&module).unwrap();
            assert!(module.getattr("upload_blob").unwrap().is_callable());
            assert!(module.getattr("download_blob").unwrap().is_callable());
            assert!(module
                .getattr("NativeDownloadStream")
                .unwrap()
                .is_instance_of::<pyo3::types::PyType>());
        });
    }

    #[test]
    fn python_error_is_preserved_through_nested_context() {
        Python::initialize();
        Python::attach(|py| {
            let original = PyValueError::new_err("original Python error");
            let error = azure_core::Error::with_error(
                ErrorKind::Credential,
                original.clone_ref(py),
                "Python token provider call failed",
            )
            .with_context("inner SDK context")
            .with_context("outer SDK context");

            let converted = PyErr::from(AzureError(error));
            assert!(converted.value(py).is(original.value(py)));
        });
    }

    #[test]
    fn sdk_error_mapping_is_unchanged() {
        Python::initialize();
        Python::attach(|py| {
            let error = azure_core::Error::with_message(ErrorKind::Other, "SDK failure");
            let converted = PyErr::from(AzureError(error));
            assert!(converted.is_instance_of::<PyValueError>(py));
            assert_eq!(
                converted.value(py).to_string(),
                "Azure Storage error: SDK failure"
            );
        });
    }
}
