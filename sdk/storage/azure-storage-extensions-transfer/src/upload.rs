// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

use std::collections::HashMap;
use std::str::FromStr;

use azure_core::http::{NoFormat, RequestContent};
use azure_core::Bytes;
use azure_storage_blob::models::{
    AccessTier, BlockBlobClientUploadOptions, EncryptionAlgorithmType, ImmutabilityPolicyMode,
};
use pyo3::buffer::PyBuffer;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

use crate::{build_blob_client, transfer_sizes, AzureError, RUNTIME};

/// An immutable Python buffer retained as the owner of a zero-copy [`Bytes`] value.
///
/// `PyBuffer` keeps the exporter and its allocation alive until it is dropped. Uploads only
/// construct this owner from Python `bytes`, whose contents cannot be mutated while Rust reads
/// them without the GIL.
struct PythonBytesOwner {
    buffer: PyBuffer<u8>,
}

impl AsRef<[u8]> for PythonBytesOwner {
    fn as_ref(&self) -> &[u8] {
        // SAFETY: construction requires a C-contiguous Python `bytes` object. Its allocation is
        // immutable and remains exported (and therefore alive) through `self.buffer`.
        unsafe {
            std::slice::from_raw_parts(self.buffer.buf_ptr().cast::<u8>(), self.buffer.len_bytes())
        }
    }
}

/// Upload a block blob using the Rust SDK.
///
/// This function releases the GIL during the entire Rust I/O operation,
/// allowing other Python threads to run concurrently.
#[pyfunction]
#[pyo3(signature = (
    url,
    data,
    *,
    token_provider = None,
    credential_id = None,
    overwrite = false,
    content_type = None,
    content_encoding = None,
    content_language = None,
    content_disposition = None,
    cache_control = None,
    content_md5 = None,
    metadata = None,
    tags = None,
    lease_id = None,
    encryption_key = None,
    encryption_key_sha256 = None,
    encryption_algorithm = None,
    encryption_scope = None,
    if_match = None,
    if_none_match = None,
    if_modified_since = None,
    if_unmodified_since = None,
    if_tags = None,
    immutability_policy_expiry = None,
    immutability_policy_mode = None,
    legal_hold = None,
    tier = None,
    timeout = None,
    max_concurrency = None,
    max_block_size = None,
))]
pub(crate) fn upload_blob<'py>(
    py: Python<'py>,
    url: &str,
    data: &Bound<'py, PyAny>,
    token_provider: Option<Py<PyAny>>,
    credential_id: Option<usize>,
    overwrite: bool,
    content_type: Option<&str>,
    content_encoding: Option<&str>,
    content_language: Option<&str>,
    content_disposition: Option<&str>,
    cache_control: Option<&str>,
    content_md5: Option<Vec<u8>>,
    metadata: Option<HashMap<String, String>>,
    tags: Option<HashMap<String, String>>,
    lease_id: Option<&str>,
    encryption_key: Option<&str>,
    encryption_key_sha256: Option<&str>,
    encryption_algorithm: Option<&str>,
    encryption_scope: Option<&str>,
    if_match: Option<&str>,
    if_none_match: Option<&str>,
    if_modified_since: Option<i64>,
    if_unmodified_since: Option<i64>,
    if_tags: Option<&str>,
    immutability_policy_expiry: Option<i64>,
    immutability_policy_mode: Option<&str>,
    legal_hold: Option<bool>,
    tier: Option<&str>,
    timeout: Option<i32>,
    max_concurrency: Option<usize>,
    max_block_size: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let blob_client = build_blob_client(url, token_provider, credential_id)?;

    // Export the Python allocation and make it the owner of `Bytes`. This passes its address
    // across the FFI boundary without copying; `Bytes` keeps the export alive while the Rust SDK
    // clones and slices the body across asynchronous upload tasks.
    if !data.is_instance_of::<PyBytes>() {
        return Err(PyValueError::new_err(
            "Native zero-copy upload requires an immutable bytes object.",
        ));
    }
    let buffer = PyBuffer::<u8>::get(data)?;
    if !buffer.is_c_contiguous() {
        return Err(PyValueError::new_err(
            "Native upload requires a C-contiguous buffer.",
        ));
    }
    let content: RequestContent<Bytes, NoFormat> =
        Bytes::from_owner(PythonBytesOwner { buffer }).into();

    let mut options = BlockBlobClientUploadOptions::default();

    let has_access_conditions = if_match.is_some()
        || if_none_match.is_some()
        || if_modified_since.is_some()
        || if_unmodified_since.is_some()
        || if_tags.is_some();
    if !overwrite && !has_access_conditions {
        options = options.if_not_exists();
    }

    if let Some(ct) = content_type {
        options.blob_content_type = Some(ct.to_string());
    }

    if let Some(encoding) = content_encoding {
        options.blob_content_encoding = Some(encoding.to_string());
    }

    if let Some(language) = content_language {
        options.blob_content_language = Some(language.to_string());
    }

    if let Some(disposition) = content_disposition {
        options.blob_content_disposition = Some(disposition.to_string());
    }

    if let Some(control) = cache_control {
        options.blob_cache_control = Some(control.to_string());
    }

    options.blob_content_md5 = content_md5;

    if let Some(meta) = metadata {
        options.metadata = Some(meta);
    }

    if let Some(tags) = tags {
        options = options.with_tags(tags);
    }

    options.lease_id = lease_id.map(str::to_string);
    options.encryption_key = encryption_key.map(str::to_string);
    options.encryption_key_sha256 = encryption_key_sha256.map(str::to_string);
    options.encryption_scope = encryption_scope.map(str::to_string);
    options.if_match = if_match.map(Into::into);
    options.if_none_match = if_none_match.map(Into::into);
    options.if_modified_since = if_modified_since
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| PyValueError::new_err(format!("Invalid if_modified_since value: {e}")))?;
    options.if_unmodified_since = if_unmodified_since
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| PyValueError::new_err(format!("Invalid if_unmodified_since value: {e}")))?;
    options.if_tags = if_tags.map(str::to_string);
    options.immutability_policy_expiry = immutability_policy_expiry
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| {
            PyValueError::new_err(format!("Invalid immutability policy expiry value: {e}"))
        })?;
    options.legal_hold = legal_hold;
    options.per_request_timeout = timeout;

    if let Some(algorithm) = encryption_algorithm {
        options.encryption_algorithm = Some(
            EncryptionAlgorithmType::from_str(algorithm)
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
        );
    }

    if let Some(mode) = immutability_policy_mode {
        options.immutability_policy_mode = Some(
            ImmutabilityPolicyMode::from_str(mode)
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
        );
    }

    if let Some(tier) = tier {
        options.tier =
            Some(AccessTier::from_str(tier).map_err(|e| PyValueError::new_err(e.to_string()))?);
    }

    let (concurrency, block_size) =
        transfer_sizes(max_concurrency, max_block_size).map_err(PyValueError::new_err)?;
    options.parallel = Some(concurrency);
    options.partition_size = Some(block_size);

    // Release the interpreter (detach this thread) and perform the upload on the shared tokio runtime
    let result = py
        .detach(|| RUNTIME.block_on(async { blob_client.upload(content, Some(options)).await }))
        .map_err(AzureError::from)?;

    // Build response dict from upload result fields
    let dict = PyDict::new(py);
    if let Some(etag) = result.etag {
        dict.set_item("etag", etag.to_string())?;
    }
    if let Some(last_modified) = result.last_modified {
        dict.set_item("last_modified", last_modified.to_string())?;
    }
    if let Some(content_md5) = result.content_md5 {
        dict.set_item("content_md5", PyBytes::new(py, &content_md5))?;
    }
    if let Some(content_crc64) = result.content_crc64 {
        dict.set_item("content_crc64", PyBytes::new(py, &content_crc64))?;
    }
    if let Some(encryption_key_sha256) = result.encryption_key_sha256 {
        dict.set_item("encryption_key_sha256", encryption_key_sha256)?;
    }
    if let Some(encryption_scope) = result.encryption_scope {
        dict.set_item("encryption_scope", encryption_scope)?;
    }
    if let Some(version_id) = result.version_id {
        dict.set_item("version_id", version_id)?;
    }

    Ok(dict)
}
