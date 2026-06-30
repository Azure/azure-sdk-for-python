// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Python-backed token credential.
//!
//! Wraps a Python credential object (anything with a synchronous
//! `get_token(*scopes) -> AccessToken`, e.g. an azure-identity credential) as an
//! `azure_core::credentials::TokenCredential` the driver can call during request
//! signing (the gateway auth path's `Credential::TokenCredential` branch calls
//! `get_token(&[COSMOS_AAD_SCOPE], None)`).
//!
//! The driver invokes `get_token` from its async pipeline, which the binding
//! always drives under `py.allow_threads(|| rt.block_on(..))` -- so the GIL is
//! released there and this impl can re-acquire it with `Python::with_gil` without
//! deadlocking. The call is synchronous (no `.await`), so the future async_trait
//! builds holds nothing across an await point and is trivially `Send`, satisfying
//! the trait's `Send + Sync` bound.
//!
//! Only *synchronous* Python credentials are supported: an async credential's
//! `get_token` returns a coroutine, and there is no event loop to drive it on the
//! driver's worker thread. The Python factory (`_resolve_credential`) rejects
//! async credentials up front, so this impl only ever sees a synchronous one.

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_core::credentials::{AccessToken, TokenCredential, TokenRequestOptions};
use azure_core::error::{Error as AzureError, ErrorKind as AzureErrorKind};
use azure_core::time::OffsetDateTime;

pub(crate) struct PyTokenCredential {
    // A strong reference that keeps the Python credential alive for as long as
    // the driver (and thus this credential) lives. `Py<PyAny>` is Send + Sync.
    credential: Py<PyAny>,
}

impl PyTokenCredential {
    pub(crate) fn new(credential: Py<PyAny>) -> Self {
        Self { credential }
    }

    /// Call the Python credential's `get_token(*scopes)` under the GIL and map
    /// the returned object (an AccessToken with `.token` / `.expires_on`) into
    /// the driver's typed `AccessToken`. Every failure becomes a `Credential`-kind
    /// error so the driver surfaces a clean authentication failure.
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
}

impl std::fmt::Debug for PyTokenCredential {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        // Never render the wrapped credential -- it may hold secrets.
        f.write_str("PyTokenCredential")
    }
}

#[async_trait::async_trait]
impl TokenCredential for PyTokenCredential {
    // KNOWN LIMITATION -- CAE / claims challenges are not propagated (by design,
    // upstream-bounded). `_options` carries the driver's `TokenRequestOptions`,
    // but two facts make forwarding it a no-op today:
    //   1. The driver never sends any: `authorization_policy.rs` calls
    //      `credential.get_token(&[COSMOS_AAD_SCOPE], None)` -- always `None`,
    //      with no 401-challenge / Continuous-Access-Evaluation handling.
    //   2. azure_core's `TokenRequestOptions` models no claims/tenant_id field
    //      (only a `ClientMethodOptions` Context), so there is nothing to lift
    //      into Python's `get_token(claims=..., tenant_id=...)` even if we tried.
    // Net: on a CAE/conditional-access 401, the driver re-fetches the same token
    // without claims and the challenge cannot be satisfied. This is a real gap
    // for AAD tenants that enforce CAE, but it lives in the driver + azure_core,
    // not in this binding -- forwarding `_options` here would change nothing.
    // Revisit once the driver plumbs challenge claims through `get_token`.
    async fn get_token(
        &self,
        scopes: &[&str],
        _options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        Python::with_gil(|py| self.fetch_token(py, scopes))
    }
}

/// Build a `Credential`-kind `azure_core::Error` from a message. The driver
/// wraps this as `AUTHENTICATION_TOKEN_ACQUISITION_FAILED` with it as the source.
fn credential_error(message: String) -> AzureError {
    AzureError::new(AzureErrorKind::Credential, message)
}
