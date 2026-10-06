// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

use std::collections::HashMap;
use std::sync::{Arc, Mutex, RwLock};

use azure_core::credentials::{AccessToken, Secret, TokenCredential, TokenRequestOptions};
use once_cell::sync::Lazy;
use pyo3::prelude::*;

/// Process-wide token credentials keyed by the identity of their Python credential.
static CACHED_CREDENTIALS: Lazy<Mutex<HashMap<usize, Arc<PyCallbackCredential>>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

pub(crate) fn get_cached_credential(
    provider: Py<PyAny>,
    credential_id: usize,
) -> Arc<dyn TokenCredential> {
    let mut cached = CACHED_CREDENTIALS
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    cached
        .entry(credential_id)
        .or_insert_with(|| Arc::new(PyCallbackCredential::new(provider)))
        .clone()
}

/// A `TokenCredential` that delegates to a Python callable on every request.
///
/// We hold a Python "token provider" (`Py<PyAny>`) and additionally cache the last token it
/// returned. The cache lets the credential serve tokens without re-entering Python on every
/// request; when the cached token nears expiry the provider is invoked again, so refresh
/// still flows back to the real Python credential (e.g. `DefaultAzureCredential`).
///
/// The provider has the signature `provider(scopes: list[str]) -> (token: str, expires_on: int)`
/// where `expires_on` is a Unix timestamp in seconds.
///
/// Thread-safety: the provider is an immutable `Py<PyAny>` (`Send + Sync`); the token cache is
/// guarded by an `RwLock`. Concurrent callers take the read path and return the cached token;
/// a refresh takes the write lock so callers coalesce onto a single Python invocation.
#[derive(Debug)]
struct PyCallbackCredential {
    provider: Py<PyAny>,
    /// Cached token as `(token, expiry)`. Stored as components rather than an `AccessToken`
    /// so we don't rely on `Secret` being cloneable.
    cache: RwLock<Option<(String, azure_core::time::OffsetDateTime)>>,
}

impl PyCallbackCredential {
    fn new(provider: Py<PyAny>) -> Self {
        Self {
            provider,
            cache: RwLock::new(None),
        }
    }
}

#[async_trait::async_trait]
impl TokenCredential for PyCallbackCredential {
    async fn get_token(
        &self,
        scopes: &[&str],
        _options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        // Refresh a little ahead of expiry, mirroring the bearer-token policy's own window, so
        // callers always receive a token with comfortable remaining lifetime.
        const REFRESH_WINDOW_SECS: i64 = 300;
        let now = azure_core::time::OffsetDateTime::now_utc().unix_timestamp();

        // Fast path: return the cached token if it is still comfortably valid. This is what
        // avoids re-invoking the Python credential on every transfer, since each new
        // `BlobClient` starts with a cold per-pipeline token cache.
        {
            let cache = self
                .cache
                .read()
                .unwrap_or_else(|poisoned| poisoned.into_inner());
            if let Some((token, expires)) = cache.as_ref() {
                if expires.unix_timestamp() - now > REFRESH_WINDOW_SECS {
                    return Ok(AccessToken::new(Secret::new(token.clone()), *expires));
                }
            }
        }

        // Slow path: fetch a fresh token. Hold the write lock across the fetch so concurrent
        // callers coalesce onto a single refresh rather than each calling into Python.
        let mut cache = self
            .cache
            .write()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        if let Some((token, expires)) = cache.as_ref() {
            if expires.unix_timestamp() - now > REFRESH_WINDOW_SECS {
                return Ok(AccessToken::new(Secret::new(token.clone()), *expires));
            }
        }

        // Re-attach the current thread to the interpreter (valid to do inside the outer
        // `detach`) and call the Python token provider to obtain a fresh token and its
        // real expiry.
        let (token, expires) = Python::attach(|py| {
            let scope_list: Vec<String> = scopes.iter().map(|s| s.to_string()).collect();
            let result = self.provider.bind(py).call1((scope_list,)).map_err(|e| {
                azure_core::Error::with_message(
                    azure_core::error::ErrorKind::Credential,
                    format!("Python token provider call failed: {}", e),
                )
            })?;
            let (token, expires_on): (String, i64) = result.extract().map_err(|e| {
                azure_core::Error::with_message(
                    azure_core::error::ErrorKind::Credential,
                    format!(
                        "Python token provider returned an unexpected value (expected (str, int)): {}",
                        e
                    ),
                )
            })?;
            let expires = azure_core::time::OffsetDateTime::from_unix_timestamp(expires_on)
                .map_err(|e| {
                    azure_core::Error::with_message(
                        azure_core::error::ErrorKind::Credential,
                        format!("Python token provider returned an invalid expiry: {}", e),
                    )
                })?;
            Ok::<(String, azure_core::time::OffsetDateTime), azure_core::Error>((token, expires))
        })?;

        *cache = Some((token.clone(), expires));
        Ok(AccessToken::new(Secret::new(token), expires))
    }
}
