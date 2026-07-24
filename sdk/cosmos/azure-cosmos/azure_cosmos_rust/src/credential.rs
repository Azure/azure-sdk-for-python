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
//! The rust driver invokes `get_token` from its async pipeline, which the binding
//! always drives under `py.allow_threads(|| rt.block_on(..))` -- so the GIL is
//! released there and this impl can re-acquire it with `Python::with_gil` without
//! deadlocking. The call is synchronous (no `.await`), so the future async_trait
//! builds holds nothing across an await point and is trivially `Send`, satisfying
//! the trait's `Send + Sync` bound.
//!
//! Only *synchronous* Python credentials are supported: an async credential's
//! `get_token` returns a coroutine, and there is no event loop to drive it on the
//! rust driver's worker thread. The Python factory (`_resolve_credential`) rejects
//! async credentials up front (wrapping them in the bridge first), so this impl
//! only ever sees a synchronous one.

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
    // Small in-process cache to avoid repeatedly crossing into Python for every
    // authorization call when the token is still fresh.
    cached_token: RwLock<Option<AccessToken>>,
}

impl PyTokenCredential {
    /// Take ownership of a strong reference to the customer's Python credential.
    /// The binding calls this once, at client construction, and hands the result
    /// to the rust driver as its `TokenCredential`. Holding the reference here is
    /// what keeps the Python object alive for the whole life of the driver.
    pub(crate) fn new(credential: Py<PyAny>) -> Self {
        Self {
            credential,
            cached_token: RwLock::new(None),
        }
    }

    /// The actual callback into Python. Takes the GIL, calls the Python
    /// credential's `get_token(*scopes)`, and maps the returned object (an
    /// AccessToken with `.token` / `.expires_on`) into the rust driver's typed
    /// `AccessToken`. This is the one place the binding crosses from Rust back
    /// into Python for auth; every failure becomes a `Credential`-kind error so
    /// the rust driver reports a clean authentication failure instead of an
    /// opaque one. Without it the driver would receive no token and could not
    /// sign the request.
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
    /// left. The 5-minute margin refreshes early so a request is never signed
    /// with a token that expires mid-flight. Without this check every request
    /// would cross back into Python for a fresh token, adding a GIL round-trip
    /// to the hot path for no benefit while the current token is still good.
    fn cached_fresh_token(&self) -> Option<AccessToken> {
        let cached = self.cached_token.read();
        cached
            .as_ref()
            .filter(|token| token.expires_on > OffsetDateTime::now_utc() + Duration::minutes(5))
            .cloned()
    }

    /// The synchronous entry the rust driver's `get_token` calls into: serve the
    /// cached token if it is still fresh, otherwise fetch a new one from Python
    /// and cache it. Kept synchronous on purpose -- the driver already released
    /// the GIL before calling, so this re-takes it with `Python::with_gil` and
    /// runs the Python `get_token` without an event loop and without deadlocking.
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
    // KNOWN LIMITATION -- CAE / claims challenges are not propagated (by design,
    // upstream-bounded). `_options` carries the driver's `TokenRequestOptions`,
    // but two facts make forwarding it a no-op today:
    //   1. The rust driver never sends any: `authorization_policy.rs` calls
    //      `credential.get_token(&[COSMOS_AAD_SCOPE], None)` -- always `None`,
    //      with no 401-challenge / Continuous-Access-Evaluation handling.
    //   2. azure_core's `TokenRequestOptions` models no claims/tenant_id field
    //      (only a `ClientMethodOptions` Context), so there is nothing to lift
    //      into Python's `get_token(claims=..., tenant_id=...)` even if we tried.
    // Net: on a CAE/conditional-access 401, the rust driver re-fetches the same
    // token without claims and the challenge cannot be satisfied. This is a real
    // gap for AAD tenants that enforce CAE, but it lives in the rust driver +
    // azure_core, not in this binding -- forwarding `_options` here changes nothing.
    // Revisit once the rust driver plumbs challenge claims through `get_token`.
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
