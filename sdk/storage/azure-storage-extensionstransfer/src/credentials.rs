// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

use std::collections::HashMap;
use std::sync::{Arc, Mutex, RwLock};

use azure_core::credentials::{AccessToken, Secret, TokenCredential, TokenRequestOptions};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Token credentials owned by one process, keyed by their Python credential's identity.
#[derive(Default)]
pub(crate) struct CredentialCache(Mutex<HashMap<usize, Arc<PyCallbackCredential>>>);

impl CredentialCache {
    pub(crate) fn get(
        &self,
        provider: Py<PyAny>,
        credential_id: usize,
    ) -> Arc<dyn TokenCredential> {
        let mut cached = self
            .0
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        cached
            .entry(credential_id)
            .or_insert_with(|| Arc::new(PyCallbackCredential::new(provider)))
            .clone()
    }
}

pub(crate) fn get_cached_credential(
    provider: Py<PyAny>,
    credential_id: usize,
) -> Arc<dyn TokenCredential> {
    crate::get_process_state()
        .credentials
        .get(provider, credential_id)
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
                azure_core::Error::with_error(
                    azure_core::error::ErrorKind::Credential,
                    e,
                    "Python token provider call failed",
                )
            })?;
            let (token, expires_on): (String, i64) = result.extract().map_err(|e| {
                azure_core::Error::with_error(
                    azure_core::error::ErrorKind::Credential,
                    e,
                    "Python token provider returned an unexpected value (expected (str, int))",
                )
            })?;
            let expires = azure_core::time::OffsetDateTime::from_unix_timestamp(expires_on)
                .map_err(|e| {
                    azure_core::Error::with_error(
                        azure_core::error::ErrorKind::Credential,
                        PyValueError::new_err(format!(
                            "Python token provider returned an invalid expiry: {e}"
                        )),
                        "Python token provider returned an invalid expiry",
                    )
                })?;
            Ok::<(String, azure_core::time::OffsetDateTime), azure_core::Error>((token, expires))
        })?;

        *cache = Some((token.clone(), expires));
        Ok(AccessToken::new(Secret::new(token), expires))
    }
}

#[cfg(test)]
#[path = "../tests/rust/credentials.rs"]
mod callback_tests;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn credential_cache_reuses_only_matching_ids() {
        Python::initialize();
        Python::attach(|py| {
            let cache = CredentialCache::default();
            let first_provider = pyo3::types::PyDict::new(py).into_any().unbind();
            let second_provider = pyo3::types::PyDict::new(py).into_any().unbind();
            let first_id = first_provider.as_ptr() as usize;
            let second_id = second_provider.as_ptr() as usize;
            let first = cache.get(first_provider.clone_ref(py), first_id);
            let same = cache.get(second_provider.clone_ref(py), first_id);
            let other = cache.get(second_provider, second_id);
            assert!(Arc::ptr_eq(&first, &same));
            assert!(!Arc::ptr_eq(&first, &other));
        });
    }

    #[test]
    fn new_callback_credential_has_no_token() {
        Python::initialize();
        Python::attach(|py| {
            let credential = PyCallbackCredential::new(py.None());
            assert!(credential.cache.read().unwrap().is_none());
        });
    }

    #[test]
    fn new_process_state_does_not_lock_inherited_credentials() {
        let slot = crate::ProcessStateSlot::new();
        let parent = slot.get(1);
        let _locked = parent.credentials.0.lock().unwrap();
        let child = slot.get(2);
        assert!(child.credentials.0.try_lock().unwrap().is_empty());
    }
}
