// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Python-backed token credential.
//!
//! Wraps a Python credential object (anything with a synchronous
//! `get_token(*scopes) -> AccessToken`, e.g. an azure-identity credential) as an
//! `azure_core::credentials::TokenCredential` the rust driver can call during
//! request signing (the gateway auth path's `Credential::TokenCredential` branch
//! calls `get_token(&[COSMOS_AAD_SCOPE], None)`).
//!
//! Direction / layering -- this is a *callback into Python*, the reverse of the
//! normal call flow. Normally a request travels down:
//!
//!     Python client  ->  binding (this compiled `_rust` extension)  ->  rust driver
//!
//! But to sign a request the rust driver needs an Entra/AAD token, so here the
//! call goes back *up*:
//!
//!     rust driver  ->  PyTokenCredential (this file, in the binding)  ->  Python credential.get_token()
//!
//! Why the binding is the layer in the middle both ways: it is the only layer
//! that can touch both worlds at once -- it holds Rust driver types *and*, via
//! PyO3, a live Python object (`Py<PyAny>`). The rust driver itself never touches
//! Python; it only knows the `TokenCredential` trait, and this file hands it a
//! `PyTokenCredential` that *implements* that trait. So the driver thinks it is
//! calling plain Rust and has no idea Python is on the other side. `credential.rs`
//! lives in the binding crate (`azure_cosmos_rust`); the rust driver is a separate
//! crate statically linked into the same compiled `_rust` file.
//!
//! Async credentials: if the customer passed an *async* credential, the Python
//! bridge (`AsyncTokenCredentialBridge`) has already wrapped it into a synchronous
//! `get_token` before it reaches here, so the full chain in that case is
//! `rust driver -> PyTokenCredential (binding) -> the bridge (Python) -> the
//! async credential's coroutine`.
//!
//! The driver's async token method calls a synchronous helper here. On a cache
//! miss, that helper acquires the Python global interpreter lock (GIL) and calls
//! `get_token` on the thread polling it. Sync operation runners release the GIL
//! while waiting; async runners spawn driver work and bridge its result to Python.
//! Neither path makes the credential callback itself asynchronous.
//!
//! This adapter expects a token object, not a coroutine, from `get_token`.
//! Python's credential preparation supplies the bridge for async credentials;
//! this adapter does not drive a Python event loop or ensure a credential is
//! safe to use across threads or loops.

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_core::credentials::{AccessToken, TokenCredential, TokenRequestOptions};
use azure_core::error::{Error as AzureError, ErrorKind as AzureErrorKind};
use azure_core::time::{Duration, OffsetDateTime};
use parking_lot::RwLock;

/// The binding-side adapter that lets the rust driver fetch an Entra/AAD token
/// from the customer's Python credential. It implements the rust driver's
/// `TokenCredential` trait (so the driver calls it as if it were plain Rust) and,
/// inside that call, reaches back up into Python via PyO3 to run the credential's
/// `get_token`. Without this type the rust driver would have no way to ask Python
/// for a token, so any client using an Entra/AAD (token) credential on the rust
/// backend could never authenticate a request.
pub(crate) struct PyTokenCredential {
    // A strong reference that keeps the Python credential alive for as long as
    // the rust driver (and thus this credential) lives. `Py<PyAny>` is Send + Sync.
    credential: Py<PyAny>,
    // One cached token per adapter, not keyed by scopes or request options.
    cached_token: RwLock<Option<AccessToken>>,
}

impl PyTokenCredential {
    /// Take ownership of a strong reference to the customer's Python credential.
    /// Driver acquisition creates this adapter when building a token-authenticated
    /// driver. Clients reusing a cached driver also reuse its adapter.
    pub(crate) fn new(credential: Py<PyAny>) -> Self {
        Self {
            credential,
            cached_token: RwLock::new(None),
        }
    }

    /// With the GIL already held, call Python's `get_token(*scopes)` and convert
    /// its `.token` and `.expires_on` fields into an `AccessToken`.
    /// Reject empty tokens and unrepresentable expiry timestamps, mapping these
    /// and Python extraction/call errors to credential errors. A newly fetched
    /// token is not checked for expiry against the current time here.
    fn fetch_token(&self, py: Python<'_>, scopes: &[&str]) -> azure_core::Result<AccessToken> {
        let credential = self.credential.bind(py);
        let scopes_arg = PyTuple::new_bound(py, scopes);
        let token_obj = credential
            .call_method1("get_token", scopes_arg)
            .map_err(|e| credential_error(format!("token credential get_token() failed: {e}")))?;
        let token: String = token_obj
            .getattr("token")
            .and_then(|value| value.extract())
            .map_err(|e| {
                credential_error(format!("token credential returned no string `token`: {e}"))
            })?;
        if token.trim().is_empty() {
            return Err(credential_error(
                "token credential returned empty `token`".to_string(),
            ));
        }
        let expires_on: i64 = token_obj
            .getattr("expires_on")
            .and_then(|value| value.extract())
            .map_err(|e| {
                credential_error(format!(
                    "token credential returned no int `expires_on`: {e}"
                ))
            })?;
        let expires = OffsetDateTime::from_unix_timestamp(expires_on).map_err(|e| {
            credential_error(format!("token credential `expires_on` out of range: {e}"))
        })?;
        Ok(AccessToken::new(token, expires))
    }

    /// Return the cached token only if it still has more than 5 minutes of life
    /// left. This margin limits cache reuse; it does not guarantee that a token
    /// remains valid for the duration of a request.
    fn cached_fresh_token(&self) -> Option<AccessToken> {
        let cached = self.cached_token.read();
        cached
            .as_ref()
            .filter(|token| token.expires_on > OffsetDateTime::now_utc() + Duration::minutes(5))
            .cloned()
    }

    /// The synchronous entry the rust driver's `get_token` calls into: serve the
    /// cached token if it is still fresh, otherwise fetch a new one from Python
    /// and cache it. The callback acquires the GIL and can block the calling
    /// thread. Fetching occurs outside the cache write lock, so concurrent misses
    /// can fetch more than once.
    fn get_token_sync(&self, scopes: &[&str]) -> azure_core::Result<AccessToken> {
        if let Some(token) = self.cached_fresh_token() {
            return Ok(token);
        }

        let fresh = Python::with_gil(|py| self.fetch_token(py, scopes))?;
        *self.cached_token.write() = Some(fresh.clone());
        Ok(fresh)
    }
}

impl std::fmt::Debug for PyTokenCredential {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        // Never render the wrapped Python credential -- it may hold secrets, and
        // this type ends up in the rust driver's debug output.
        f.write_str("PyTokenCredential")
    }
}

/// The rust driver's view of this type. The driver holds a `TokenCredential`
/// trait object and calls `get_token` on it during request signing, unaware that
/// the implementation crosses back into Python. This method is the top of the
/// callback: `rust driver -> get_token (here) -> get_token_sync -> fetch_token ->
/// Python credential`.
#[async_trait::async_trait]
impl TokenCredential for PyTokenCredential {
    // Only scopes are forwarded to Python. Request options are ignored; this
    // adapter has no claims-challenge handling or response-driven cache
    // invalidation. This method alone does not establish how a 401 is retried.
    async fn get_token(
        &self,
        scopes: &[&str],
        _options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        self.get_token_sync(scopes)
    }
}

/// Build a `Credential`-kind `azure_core::Error` from a message. The rust driver
/// wraps this as `AUTHENTICATION_TOKEN_ACQUISITION_FAILED` with it as the source.
fn credential_error(message: String) -> AzureError {
    AzureError::new(AzureErrorKind::Credential, message)
}

#[cfg(test)]
mod tests {
    use super::PyTokenCredential;
    use pyo3::prelude::*;
    use pyo3::types::PyModule;

    fn make_python_credential(py: Python<'_>, body: &str) -> PyResult<Py<PyAny>> {
        let module = PyModule::from_code_bound(py, body, "test_credential.py", "test_credential")?;
        module
            .getattr("Credential")?
            .call0()
            .map(|obj| obj.unbind())
    }

    #[test]
    fn get_token_caches_fresh_result() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let credential_obj = make_python_credential(
                py,
                r#"
class AccessToken:
    def __init__(self, token, expires_on):
        self.token = token
        self.expires_on = expires_on

class Credential:
    def __init__(self):
        self.calls = 0
    def get_token(self, *scopes):
        self.calls += 1
        return AccessToken("abc", 4102444800)
"#,
            )
            .expect("python credential should be created");

            let credential = PyTokenCredential::new(credential_obj.clone_ref(py));
            let first = credential
                .get_token_sync(&["https://cosmos.azure.com/.default"])
                .expect("first token fetch should succeed");
            let second = credential
                .get_token_sync(&["https://cosmos.azure.com/.default"])
                .expect("cached token fetch should succeed");

            assert_eq!(first.token.secret(), second.token.secret());
            let calls: usize = credential_obj
                .bind(py)
                .getattr("calls")
                .and_then(|v| v.extract())
                .expect("call counter should be readable");
            assert_eq!(1, calls);
        });
    }

    #[test]
    fn get_token_rejects_empty_token() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let credential_obj = make_python_credential(
                py,
                r#"
class AccessToken:
    def __init__(self, token, expires_on):
        self.token = token
        self.expires_on = expires_on

class Credential:
    def get_token(self, *scopes):
        return AccessToken("", 4102444800)
"#,
            )
            .expect("python credential should be created");

            let credential = PyTokenCredential::new(credential_obj);
            let err = credential
                .get_token_sync(&["https://cosmos.azure.com/.default"])
                .expect_err("empty token should fail");
            assert!(
                err.to_string().contains("empty `token`"),
                "unexpected error: {err}"
            );
        });
    }
}
