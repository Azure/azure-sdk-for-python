// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use azure_core::error::ErrorKind;
use azure_storage_blob::StorageError;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

pyo3::create_exception!(
    azure.storage.extensions.transfer._native,
    NativeTransferError,
    PyException,
    "A native transfer failure."
);

pub(crate) struct AzureError(pub azure_core::Error);

impl From<azure_core::Error> for AzureError {
    fn from(error: azure_core::Error) -> Self {
        Self(error)
    }
}

impl From<AzureError> for PyErr {
    fn from(error: AzureError) -> Self {
        Python::attach(|py| {
            let mut current: Option<&(dyn std::error::Error + 'static)> = Some(&error.0);
            let mut incomplete_read = false;
            while let Some(source) = current {
                if let Some(original) = source.downcast_ref::<PyErr>() {
                    return original.clone_ref(py);
                }
                if let Some(io_error) = source.downcast_ref::<std::io::Error>() {
                    incomplete_read |= io_error.kind() == std::io::ErrorKind::UnexpectedEof;
                }
                current = source.source();
            }
            match native_error(py, error.0, incomplete_read) {
                Ok(converted) => converted,
                Err(construction_error) => construction_error,
            }
        })
    }
}

fn native_error(
    py: Python<'_>,
    error: azure_core::Error,
    incomplete_read: bool,
) -> PyResult<PyErr> {
    let mut message = error.to_string();
    let headers = PyDict::new(py);
    let additional_info = PyDict::new(py);
    let mut request_id = None;
    let (kind, status_code, mut error_code, body) = match error.kind() {
        ErrorKind::HttpResponse {
            status,
            error_code,
            raw_response,
        } => {
            if let Some(response) = raw_response {
                for (name, value) in response.headers().iter() {
                    headers.set_item(name.as_str(), value.as_str())?;
                }
                request_id = response
                    .headers()
                    .get_optional_str(&"x-ms-request-id".into())
                    .map(str::to_owned);
            }
            (
                "http",
                Some(u16::from(*status)),
                error_code.clone(),
                raw_response
                    .as_ref()
                    .map(|response| PyBytes::new(py, response.body())),
            )
        }
        ErrorKind::Connection => ("connection", None, None, None),
        ErrorKind::Io if incomplete_read => ("incomplete_read", None, None, None),
        ErrorKind::Io => ("io", None, None, None),
        ErrorKind::DataConversion => ("data_conversion", None, None, None),
        ErrorKind::Credential => ("credential", None, None, None),
        ErrorKind::Other => ("other", None, None, None),
    };
    let mut normalization_error = None;
    if kind == "http" {
        // Capture the original response first: conversion consumes the error and may
        // return a parsing failure instead of the original HTTP error.
        match StorageError::try_from(error) {
            Ok(storage) => {
                message = storage.message.unwrap_or(message);
                error_code = storage
                    .error_code
                    .map(|code| code.to_string())
                    .or(error_code);
                request_id = storage.request_id.or(request_id);
                for (name, value) in storage.additional_error_info {
                    additional_info.set_item(name, value)?;
                }
                for (name, value) in [
                    ("reason", storage.reason),
                    (
                        "authentication_error_detail",
                        storage.authentication_error_detail,
                    ),
                    (
                        "copy_source_status_code",
                        storage
                            .copy_source_status_code
                            .map(|status| u16::from(status).to_string()),
                    ),
                    ("copy_source_error_code", storage.copy_source_error_code),
                    (
                        "copy_source_error_message",
                        storage.copy_source_error_message,
                    ),
                ] {
                    if let Some(value) = value {
                        additional_info.set_item(name, value)?;
                    }
                }
            }
            Err(error) => normalization_error = Some(error.to_string()),
        }
    }
    let converted = NativeTransferError::new_err(message.clone());
    let value = converted.value(py);
    value.setattr("message", message)?;
    value.setattr("kind", kind)?;
    value.setattr("status_code", status_code)?;
    value.setattr("error_code", error_code)?;
    value.setattr("headers", headers)?;
    value.setattr("body", body)?;
    value.setattr("request_id", request_id)?;
    value.setattr("additional_info", additional_info)?;
    value.setattr("normalization_error", normalization_error)?;
    Ok(converted)
}

#[cfg(test)]
#[path = "../tests/rust/errors.rs"]
mod tests;
