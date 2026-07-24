// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

//! PyO3 native module for accelerated Azure Blob Storage transfers.
//!
//! Provides `upload_blob` and `download_blob` functions that delegate to the
//! `azure_storage_blob` Rust crate for high-performance parallel transfers.

use std::collections::HashMap;
use std::num::NonZero;
use std::sync::Arc;

use azure_core::credentials::{AccessToken, Secret, TokenCredential, TokenRequestOptions};
use azure_core::http::{NoFormat, RequestContent, Url};
use azure_core::Bytes;
use azure_storage_blob::models::{
    BlobClientDownloadOptions, BlockBlobClientUploadOptions, HttpRange,
};
use azure_storage_blob::{BlobClient, BlobClientOptions};
use once_cell::sync::Lazy;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use tokio::runtime::Runtime;

/// Shared tokio runtime — created once, reused across all calls to avoid
/// per-call overhead of spawning a new runtime.
static RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    Runtime::new().expect("Failed to create tokio runtime")
});

/// Custom error wrapper for mapping `azure_core::Error` to Python exceptions.
struct AzureError(azure_core::Error);

impl From<AzureError> for PyErr {
    fn from(err: AzureError) -> PyErr {
        PyValueError::new_err(format!("Azure Storage error: {}", err.0))
    }
}

impl From<azure_core::Error> for AzureError {
    fn from(e: azure_core::Error) -> Self {
        Self(e)
    }
}

/// Build a `BlobClient` from the provided URL components and optional access token.
///
/// If `access_token` is provided, a simple bearer-token credential is used.
/// If the `account_url` contains a SAS token in the query string, pass `access_token=None`.
fn build_blob_client(
    account_url: &str,
    container: &str,
    blob: &str,
    access_token: Option<&str>,
) -> Result<BlobClient, AzureError> {
    let base = account_url.trim_end_matches('/');
    let blob_url_str = format!("{}/{}/{}", base, container, blob);
    let blob_url = Url::parse(&blob_url_str).map_err(|e| {
        azure_core::Error::with_message(
            azure_core::error::ErrorKind::Other,
            format!("Invalid URL: {}", e),
        )
    })?;

    let credential: Option<Arc<dyn TokenCredential>> = match access_token {
        Some(token) => Some(Arc::new(StaticTokenCredential::new(token.to_string()))),
        None => None,
    };

    let client =
        BlobClient::new(blob_url, credential, None::<BlobClientOptions>).map_err(AzureError::from)?;
    Ok(client)
}

/// A simple TokenCredential that returns a fixed access token.
/// The Python side extracts the token and passes just the string across FFI.
#[derive(Debug)]
struct StaticTokenCredential {
    token: String,
}

impl StaticTokenCredential {
    fn new(token: String) -> Self {
        Self { token }
    }
}

#[async_trait::async_trait]
impl TokenCredential for StaticTokenCredential {
    async fn get_token(
        &self,
        _scopes: &[&str],
        _options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        Ok(AccessToken::new(
            Secret::new(self.token.clone()),
            // Token expires far in the future — the Python SDK handles refresh
            azure_core::time::OffsetDateTime::now_utc() + azure_core::time::Duration::hours(1),
        ))
    }
}

/// Upload a block blob using the Rust SDK.
///
/// This function releases the GIL during the entire Rust I/O operation,
/// allowing other Python threads to run concurrently.
#[pyfunction]
#[pyo3(signature = (
    account_url,
    container,
    blob,
    data,
    *,
    access_token = None,
    overwrite = false,
    content_type = None,
    metadata = None,
    max_concurrency = None,
    _max_single_put_size = None,
    max_block_size = None,
))]
fn upload_blob<'py>(
    py: Python<'py>,
    account_url: &str,
    container: &str,
    blob: &str,
    data: &[u8],
    access_token: Option<&str>,
    overwrite: bool,
    content_type: Option<&str>,
    metadata: Option<HashMap<String, String>>,
    max_concurrency: Option<usize>,
    _max_single_put_size: Option<u64>,
    max_block_size: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let blob_client = build_blob_client(account_url, container, blob, access_token)?;

    let content: RequestContent<Bytes, NoFormat> = Bytes::copy_from_slice(data).into();

    let mut options = BlockBlobClientUploadOptions::default();

    if !overwrite {
        options = options.if_not_exists();
    }

    if let Some(ct) = content_type {
        options.blob_content_type = Some(ct.to_string());
    }

    if let Some(meta) = metadata {
        options.metadata = Some(meta);
    }

    if let Some(concurrency) = max_concurrency {
        options.parallel = NonZero::new(concurrency);
    }

    if let Some(block_size) = max_block_size {
        options.partition_size = NonZero::new(block_size);
    }

    // Release GIL and perform the upload on the shared tokio runtime
    let result = py
        .allow_threads(|| {
            RUNTIME.block_on(async { blob_client.upload(content, Some(options)).await })
        })
        .map_err(AzureError::from)?;

    // Build response dict from upload result fields
    let dict = PyDict::new(py);
    if let Some(etag) = result.etag {
        dict.set_item("etag", etag.to_string())?;
    }
    if let Some(last_modified) = result.last_modified {
        dict.set_item("last_modified", last_modified.to_string())?;
    }

    Ok(dict)
}

/// Download a block blob using the Rust SDK's `download_into` API.
///
/// Uses `download_into` which writes directly into a pre-allocated buffer,
/// avoiding intermediate allocations. The GIL is released during the entire
/// Rust I/O operation.
#[pyfunction]
#[pyo3(signature = (
    account_url,
    container,
    blob,
    *,
    access_token = None,
    offset = None,
    length = None,
    max_concurrency = None,
    expected_size = None,
))]
fn download_blob<'py>(
    py: Python<'py>,
    account_url: &str,
    container: &str,
    blob: &str,
    access_token: Option<&str>,
    offset: Option<u64>,
    length: Option<u64>,
    max_concurrency: Option<usize>,
    expected_size: Option<usize>,
) -> PyResult<Bound<'py, PyBytes>> {
    let blob_client = build_blob_client(account_url, container, blob, access_token)?;

    let mut options = BlobClientDownloadOptions::default();

    if let Some(off) = offset {
        options.range = Some(HttpRange::new(off, length.unwrap_or(u64::MAX - off)));
    }

    if let Some(concurrency) = max_concurrency {
        options.parallel = NonZero::new(concurrency);
    }

    // Determine buffer size: use expected_size if known, or length if specified,
    // otherwise fall back to a large default that download_into will fill.
    let buf_size = expected_size
        .or(length.map(|l| l as usize))
        .unwrap_or(256 * 1024 * 1024); // 256 MiB default max

    // Release GIL and perform the download on the shared tokio runtime
    let (data, len) = py
        .allow_threads(|| {
            RUNTIME.block_on(async {
                let mut buffer = vec![0u8; buf_size];
                let result = blob_client
                    .download_into(&mut buffer, Some(options))
                    .await
                    .map_err(AzureError::from)?;
                buffer.truncate(result.len);
                Ok::<(Vec<u8>, usize), PyErr>((buffer, result.len))
            })
        })?;

    Ok(PyBytes::new(py, &data[..len]))
}

/// Python module definition.
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(upload_blob, m)?)?;
    m.add_function(wrap_pyfunction!(download_blob, m)?)?;
    Ok(())
}
