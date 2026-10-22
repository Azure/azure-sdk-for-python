// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Let the Rust driver obtain tokens from a Python credential.
//!
//! An order read reaches the binding from the Python wrapper. If authentication
//! needs a token, the call goes in the other direction:
//! `Rust driver -> PyTokenCredential in the binding -> Python credential`.
//! PyTokenCredential implements the azure_core TokenCredential interface; the
//! separately owned Rust driver does not need to know about Python objects.
//!
//! A synchronous credential's get_token call runs on Tokio's blocking worker
//! pool. Stopping the Rust wait cannot forcibly stop that Python call. The worker
//! retains the refresh lock until the call finishes, preventing another refresh
//! from starting while the first is still running.
//!
//! For an async credential, the Python wrapper supplies AsyncTokenCredentialBridge.
//! The binding uses its _start_token_request method and awaits the resulting
//! Python future through a completion callback, without blocking a Tokio worker.
//! Dropping that Rust wait requests cancellation of the Python future.
//!
//! Both paths parse the returned token and expiry, then retain one cached token
//! with the scope actually requested from Python. Account credentials use the
//! saved override or endpoint-derived scope, with the legacy policy's restricted
//! fallback to the global scope. This adapter does not run the Python event loop, close the
//! customer app's credential, or establish that it supports arbitrary thread use.

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_core::credentials::{AccessToken, TokenCredential, TokenRequestOptions};
use azure_core::error::{Error as AzureError, ErrorKind as AzureErrorKind};
use azure_core::time::{Duration, OffsetDateTime};
use parking_lot::{Mutex, RwLock};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tokio::sync::oneshot;

const COSMOS_DEFAULT_SCOPE: &str = "https://cosmos.azure.com/.default";

struct TokenScopePolicy {
    initial_scope: String,
    allow_fallback: bool,
    fallback: AtomicBool,
}

impl TokenScopePolicy {
    fn current_scope(&self) -> &str {
        if self.fallback.load(Ordering::Acquire) {
            COSMOS_DEFAULT_SCOPE
        } else {
            &self.initial_scope
        }
    }

    fn try_fallback(&self, py: Python<'_>, error: &PyErr) -> PyResult<bool> {
        if !self.allow_fallback || self.current_scope() == COSMOS_DEFAULT_SCOPE {
            return Ok(false);
        }
        let http_error = py
            .import_bound("azure.core.exceptions")?
            .getattr("HttpResponseError")?;
        let value = error.value_bound(py);
        if !value.is_instance(&http_error)? || !value.str()?.to_str()?.contains("AADSTS500011") {
            return Ok(false);
        }
        // Match the Python policy: the scope remains switched even if fallback fails.
        self.fallback.store(true, Ordering::Release);
        Ok(true)
    }
}

struct CachedToken {
    scopes: Vec<String>,
    token: AccessToken,
}

#[pyclass]
struct TokenResultSender {
    sender: Mutex<Option<oneshot::Sender<PyResult<Py<PyAny>>>>>,
}

#[pymethods]
impl TokenResultSender {
    fn __call__(&self, future: &Bound<'_, PyAny>) {
        let result = future.call_method0("result").map(Bound::unbind);
        if let Some(sender) = self.sender.lock().take() {
            // The Rust wait may have been cancelled before this callback finishes.
            let _ = sender.send(result);
        }
    }
}

struct CancelTokenRequest(Py<PyAny>);

impl Drop for CancelTokenRequest {
    fn drop(&mut self) {
        Python::with_gil(|py| {
            if let Err(error) = self.0.bind(py).call_method0("cancel") {
                error.print(py);
            }
        });
    }
}

/// Connect the Rust driver's token request to the supplied Python credential.
/// The Python object can be a synchronous credential or AsyncTokenCredentialBridge.
pub(crate) struct PyTokenCredential {
    // Retain the supplied Python object while this adapter exists. This does
    // not grant ownership of closing the customer app's credential.
    credential: Py<PyAny>,
    // Keep one scope-qualified entry rather than an unbounded scope cache.
    cached_token: Arc<RwLock<Option<CachedToken>>>,
    refresh: Arc<tokio::sync::Mutex<()>>,
    scope_policy: Option<Arc<TokenScopePolicy>>,
}

impl PyTokenCredential {
    /// Retain the Python credential object supplied during driver acquisition.
    /// Clients reusing a cached CosmosDriver also reuse this adapter and its cache.
    fn new(credential: Py<PyAny>) -> Self {
        Self {
            credential,
            cached_token: Arc::new(RwLock::new(None)),
            refresh: Arc::new(tokio::sync::Mutex::new(())),
            scope_policy: None,
        }
    }

    pub(crate) fn for_account(
        credential: Py<PyAny>,
        account_scope: String,
        override_scope: Option<String>,
    ) -> Self {
        let mut result = Self::new(credential);
        result.scope_policy = Some(Arc::new(TokenScopePolicy {
            allow_fallback: override_scope.is_none(),
            initial_scope: override_scope.unwrap_or(account_scope),
            fallback: AtomicBool::new(false),
        }));
        result
    }

    fn effective_scopes(&self, requested: &[&str]) -> Vec<String> {
        match &self.scope_policy {
            Some(policy) => vec![policy.current_scope().to_owned()],
            None => requested.iter().map(|scope| (*scope).to_owned()).collect(),
        }
    }

    /// With Python's global interpreter lock (GIL) held, call `get_token(*scopes)`.
    /// Convert its `.token` and `.expires_on` fields into an `AccessToken`.
    /// Reject empty tokens and unrepresentable expiry timestamps, mapping these
    /// and Python extraction/call errors to credential errors. A newly fetched
    /// token is not checked for expiry against the current time here.
    fn fetch_token(
        credential: &Bound<'_, PyAny>,
        scopes: &mut Vec<String>,
        policy: Option<&TokenScopePolicy>,
    ) -> azure_core::Result<AccessToken> {
        let py = credential.py();
        let token_obj = loop {
            match credential.call_method1("get_token", PyTuple::new_bound(py, &*scopes)) {
                Ok(token) => break token,
                Err(error) => {
                    let fallback = match policy {
                        Some(policy) => policy.try_fallback(py, &error),
                        None => Ok(false),
                    }
                    .map_err(|e| {
                        credential_error(format!("token scope fallback check failed: {e}"))
                    })?;
                    if !fallback {
                        return Err(credential_error(format!(
                            "token credential get_token() failed: {error}"
                        )));
                    }
                    *scopes = vec![COSMOS_DEFAULT_SCOPE.to_owned()];
                }
            }
        };
        Self::parse_token(&token_obj)
    }

    fn parse_token(token_obj: &Bound<'_, PyAny>) -> azure_core::Result<AccessToken> {
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

    /// Reuse the cached token only for identical scopes in the same order and
    /// more than five minutes before expiry. This does not guarantee that a token
    /// remains valid for the duration of a request.
    fn cached_fresh_token(&self, scopes: &[&str]) -> Option<AccessToken> {
        let cached = self.cached_token.read();
        cached
            .as_ref()
            .filter(|entry| {
                entry
                    .scopes
                    .iter()
                    .map(String::as_str)
                    .eq(scopes.iter().copied())
                    && entry.token.expires_on > OffsetDateTime::now_utc() + Duration::minutes(5)
            })
            .map(|entry| entry.token.clone())
    }

    /// Test-only synchronous path for token validation and cache behavior.
    #[cfg(test)]
    fn get_token_sync(&self, scopes: &[&str]) -> azure_core::Result<AccessToken> {
        let mut scopes = self.effective_scopes(scopes);
        let scope_refs: Vec<&str> = scopes.iter().map(String::as_str).collect();
        if let Some(token) = self.cached_fresh_token(&scope_refs) {
            return Ok(token);
        }

        let fresh = Python::with_gil(|py| {
            Self::fetch_token(
                self.credential.bind(py),
                &mut scopes,
                self.scope_policy.as_deref(),
            )
        })?;
        *self.cached_token.write() = Some(CachedToken {
            scopes,
            token: fresh.clone(),
        });
        Ok(fresh)
    }

    async fn get_token_async(&self, scopes: &[&str]) -> azure_core::Result<AccessToken> {
        let requested = scopes;
        let scopes = self.effective_scopes(requested);
        let scope_refs: Vec<&str> = scopes.iter().map(String::as_str).collect();
        if let Some(token) = self.cached_fresh_token(&scope_refs) {
            return Ok(token);
        }
        let refresh = self.refresh.clone().lock_owned().await;
        let mut scopes = self.effective_scopes(requested);
        let scope_refs: Vec<&str> = scopes.iter().map(String::as_str).collect();
        if let Some(token) = self.cached_fresh_token(&scope_refs) {
            return Ok(token);
        }
        let fresh = loop {
            let pending = Python::with_gil(|py| -> PyResult<_> {
                let credential = self.credential.bind(py);
                if !credential.hasattr("_start_token_request")? {
                    return Ok(None);
                }
                let future = credential
                    .call_method1("_start_token_request", PyTuple::new_bound(py, &scopes))?;
                let guard = CancelTokenRequest(future.unbind());
                let (sender, receiver) = oneshot::channel();
                let callback = Py::new(
                    py,
                    TokenResultSender {
                        sender: Mutex::new(Some(sender)),
                    },
                )?;
                guard
                    .0
                    .bind(py)
                    .call_method1("add_done_callback", (callback,))?;
                Ok(Some((guard, receiver)))
            })
            .map_err(|error| {
                credential_error(format!("token credential scheduling failed: {error}"))
            })?;

            match pending {
                Some((_guard, receiver)) => {
                    let result = receiver.await.map_err(|_| {
                        credential_error("token result sender was dropped".to_string())
                    })?;
                    match result {
                        Ok(token) => {
                            break Python::with_gil(|py| Self::parse_token(token.bind(py)))?
                        }
                        Err(error) => {
                            let fallback = Python::with_gil(|py| match &self.scope_policy {
                                Some(policy) => policy.try_fallback(py, &error),
                                None => Ok(false),
                            })
                            .map_err(|e| {
                                credential_error(format!("token scope fallback check failed: {e}"))
                            })?;
                            if !fallback {
                                return Err(credential_error(format!(
                                    "token credential get_token() failed: {error}"
                                )));
                            }
                            scopes = vec![COSMOS_DEFAULT_SCOPE.to_owned()];
                        }
                    }
                }
                None => {
                    let credential = Python::with_gil(|py| self.credential.clone_ref(py));
                    let cache = self.cached_token.clone();
                    let policy = self.scope_policy.clone();
                    return tokio::task::spawn_blocking(move || {
                        // Cancellation stops waiting, not synchronous Python code. Keep
                        // the refresh lock until that code finishes and publishes its token.
                        let _refresh = refresh;
                        let fresh = Python::with_gil(|py| {
                            Self::fetch_token(credential.bind(py), &mut scopes, policy.as_deref())
                        })?;
                        *cache.write() = Some(CachedToken {
                            scopes,
                            token: fresh.clone(),
                        });
                        Ok(fresh)
                    })
                    .await
                    .map_err(|error| credential_error(format!("token worker failed: {error}")))?;
                }
            }
        };
        *self.cached_token.write() = Some(CachedToken {
            scopes,
            token: fresh.clone(),
        });
        Ok(fresh)
    }
}

impl std::fmt::Debug for PyTokenCredential {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        // Never render the wrapped Python credential -- it may hold secrets, and
        // this type ends up in the Rust driver's debug output.
        f.write_str("PyTokenCredential")
    }
}

/// Implement the token-request interface used by the Rust driver.
/// get_token_async chooses the synchronous-credential or async-credential-bridge path.
#[async_trait::async_trait]
impl TokenCredential for PyTokenCredential {
    async fn get_token(
        &self,
        scopes: &[&str],
        options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        // Match every TokenRequestOptions field so an added field requires review.
        let TokenRequestOptions { method_options: _ } = options.unwrap_or_default();
        self.get_token_async(scopes).await
    }
}

/// Build a Credential-kind azure_core::Error for the Rust driver's token request.
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

    #[tokio::test]
    async fn account_scope_policy_matches_legacy_for_sync_and_async_credentials() {
        use azure_core::credentials::TokenCredential;
        pyo3::prepare_freethreaded_python();
        for async_bridge in [false, true] {
            for scenario in [
                "success",
                "fallback",
                "other_error",
                "wrong_type",
                "fallback_fails",
            ] {
                for override_scope in [
                    None,
                    Some("https://override.example/.default"),
                    Some("https://alpha-bank-account.documents.azure.com/.default"),
                    Some(super::COSMOS_DEFAULT_SCOPE),
                ] {
                    let (object, expected_scopes, expected_outcomes) = Python::with_gil(|py| {
                        let module = PyModule::from_code_bound(
                            py,
                            r#"
import asyncio
from concurrent.futures import Future
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.rest import HttpRequest
from azure.cosmos._auth_policy import CosmosBearerTokenCredentialPolicy
from azure.cosmos.aio._auth_policy_async import AsyncCosmosBearerTokenCredentialPolicy

ACCOUNT = "https://alpha-bank-account.documents.azure.com/.default"
GLOBAL = "https://cosmos.azure.com/.default"

class Credential:
    def __init__(self, scenario):
        self.scenario = scenario
        self.scopes = []
    def get_token(self, *scopes, **kwargs):
        assert len(scopes) == 1
        scope = scopes[0]
        self.scopes.append(scope)
        if self.scenario == "fallback_fails":
            raise HttpResponseError(message="AADSTS500011: test resource unavailable")
        if self.scenario == "fallback" and scope != GLOBAL:
            raise HttpResponseError(message="AADSTS500011: test resource unavailable")
        if self.scenario == "other_error":
            raise HttpResponseError(message="AADSTS700016: unrelated failure")
        if self.scenario == "wrong_type":
            raise ValueError("AADSTS500011: not an HTTP authentication error")
        return AccessToken("example-token-not-for-use", 4102444800)
    def _start_token_request(self, *scopes):
        result = Future()
        try:
            result.set_result(self.get_token(*scopes))
        except Exception as error:
            result.set_exception(error)
        return result

class AsyncCredential(Credential):
    async def get_token(self, *scopes, **kwargs):
        return super().get_token(*scopes, **kwargs)

def legacy(async_mode, scenario, override):
    credential = (AsyncCredential if async_mode else Credential)(scenario)
    policy = (AsyncCosmosBearerTokenCredentialPolicy if async_mode
              else CosmosBearerTokenCredentialPolicy)(credential, ACCOUNT, override)
    outcomes = []
    async def invoke_async(request):
        await policy.on_request(request)
    for _ in range(2):
        request = PipelineRequest(HttpRequest("GET", "https://example.test"),
                                  PipelineContext(None))
        try:
            if async_mode:
                asyncio.run(invoke_async(request))
            else:
                policy.on_request(request)
            outcomes.append(True)
        except (HttpResponseError, ValueError):
            outcomes.append(False)
    return credential.scopes, outcomes
"#,
                            "scope_parity.py",
                            "scope_parity",
                        )
                        .unwrap();
                        let expected: (Vec<String>, Vec<bool>) = module
                            .getattr("legacy")
                            .unwrap()
                            .call1((async_bridge, scenario, override_scope))
                            .unwrap()
                            .extract()
                            .unwrap();
                        let object = module
                            .getattr("Credential")
                            .unwrap()
                            .call1((scenario,))
                            .unwrap();
                        if !async_bridge {
                            object.get_type().delattr("_start_token_request").unwrap();
                        }
                        (object.unbind(), expected.0, expected.1)
                    });
                    let credential = Python::with_gil(|py| {
                        PyTokenCredential::for_account(
                            object.clone_ref(py),
                            "https://alpha-bank-account.documents.azure.com/.default".to_owned(),
                            override_scope.map(str::to_owned),
                        )
                    });
                    let mut outcomes = Vec::new();
                    for _ in 0..2 {
                        outcomes.push(
                            credential
                                .get_token(&[super::COSMOS_DEFAULT_SCOPE], None)
                                .await
                                .is_ok(),
                        );
                    }
                    assert_eq!(
                        outcomes, expected_outcomes,
                        "{async_bridge} {scenario} {override_scope:?}"
                    );
                    Python::with_gil(|py| {
                        let actual: Vec<String> = object
                            .bind(py)
                            .getattr("scopes")
                            .unwrap()
                            .extract()
                            .unwrap();
                        assert_eq!(
                            actual, expected_scopes,
                            "{async_bridge} {scenario} {override_scope:?}"
                        );
                    });
                }
            }
        }
    }

    #[tokio::test]
    async fn concurrent_account_refresh_shares_fallback_and_effective_scope_cache() {
        use std::sync::Arc;
        pyo3::prepare_freethreaded_python();
        for async_bridge in [false, true] {
            let object = Python::with_gil(|py| {
                let object = make_python_credential(
                    py,
                    r#"
import threading
import time
from concurrent.futures import Future
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
class Credential:
    def __init__(self):
        self.scopes = []
    def get_token(self, *scopes):
        self.scopes.append(scopes[0])
        time.sleep(0.01)
        if scopes[0] != "https://cosmos.azure.com/.default":
            raise HttpResponseError(message="AADSTS500011: test resource unavailable")
        return AccessToken("example-token-not-for-use", 4102444800)
    def _start_token_request(self, *scopes):
        result = Future()
        def complete():
            try:
                result.set_result(self.get_token(*scopes))
            except Exception as error:
                result.set_exception(error)
        threading.Timer(0.01, complete).start()
        return result
"#,
                )
                .unwrap();
                if !async_bridge {
                    object
                        .bind(py)
                        .get_type()
                        .delattr("_start_token_request")
                        .unwrap();
                }
                object
            });
            let credential = Arc::new(Python::with_gil(|py| {
                PyTokenCredential::for_account(
                    object.clone_ref(py),
                    "https://alpha-bank-account.documents.azure.com/.default".to_owned(),
                    None,
                )
            }));
            let mut tasks = tokio::task::JoinSet::new();
            for _ in 0..12 {
                let credential = credential.clone();
                tasks.spawn(async move {
                    credential
                        .get_token_async(&[super::COSMOS_DEFAULT_SCOPE])
                        .await
                });
            }
            while let Some(result) = tasks.join_next().await {
                assert_eq!(
                    result.unwrap().unwrap().token.secret(),
                    "example-token-not-for-use"
                );
            }
            Python::with_gil(|py| {
                let scopes: Vec<String> = object
                    .bind(py)
                    .getattr("scopes")
                    .unwrap()
                    .extract()
                    .unwrap();
                assert_eq!(
                    scopes,
                    vec![
                        "https://alpha-bank-account.documents.azure.com/.default",
                        super::COSMOS_DEFAULT_SCOPE,
                    ]
                );
            });
        }
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

    #[tokio::test]
    async fn concurrent_refresh_is_single_flight_and_cache_is_scope_qualified() {
        use azure_core::credentials::TokenCredential;
        use std::sync::Arc;
        pyo3::prepare_freethreaded_python();
        for async_bridge in [false, true] {
            let object = Python::with_gil(|py| {
                let object = make_python_credential(
                    py,
                    r#"
import time
import threading
from concurrent.futures import Future
from types import SimpleNamespace
class Credential:
    def __init__(self):
        self.calls = 0
    def get_token(self, *scopes):
        self.calls += 1
        time.sleep(0.03)
        return SimpleNamespace(token=",".join(scopes), expires_on=4102444800)
    def _start_token_request(self, *scopes):
        self.calls += 1
        future = Future()
        token = SimpleNamespace(token=",".join(scopes), expires_on=4102444800)
        threading.Timer(0.03, lambda: future.set_result(token)).start()
        return future
"#,
                )
                .unwrap();
                if !async_bridge {
                    object
                        .bind(py)
                        .get_type()
                        .delattr("_start_token_request")
                        .unwrap();
                }
                object
            });
            let credential = Arc::new(Python::with_gil(|py| {
                PyTokenCredential::new(object.clone_ref(py))
            }));
            let mut tasks = tokio::task::JoinSet::new();
            for _ in 0..12 {
                let credential = credential.clone();
                tasks.spawn(async move { credential.get_token_async(&["scope-a"]).await });
            }
            while let Some(result) = tasks.join_next().await {
                assert_eq!(result.unwrap().unwrap().token.secret(), "scope-a");
            }
            Python::with_gil(|py| {
                assert_eq!(
                    object
                        .bind(py)
                        .getattr("calls")
                        .unwrap()
                        .extract::<usize>()
                        .unwrap(),
                    1
                );
            });
            let token = credential
                .get_token(&["scope-b"], Some(Default::default()))
                .await
                .unwrap();
            assert_eq!(token.token.secret(), "scope-b");
            assert!(credential.cached_fresh_token(&["scope-a"]).is_none());
            assert!(credential.cached_fresh_token(&["scope-b"]).is_some());
            Python::with_gil(|py| {
                assert_eq!(
                    object
                        .bind(py)
                        .getattr("calls")
                        .unwrap()
                        .extract::<usize>()
                        .unwrap(),
                    2
                );
            });
        }
    }

    #[tokio::test]
    async fn cancelled_blocking_refresh_keeps_ownership_until_python_finishes() {
        use std::sync::Arc;
        pyo3::prepare_freethreaded_python();
        let object = Python::with_gil(|py| {
            make_python_credential(
                py,
                r#"
import threading
from types import SimpleNamespace
class Credential:
    def __init__(self):
        self.calls = 0
        self.started = threading.Event()
        self.release = threading.Event()
    def get_token(self, *scopes):
        self.calls += 1
        self.started.set()
        if not self.release.wait(2):
            raise RuntimeError("test did not release credential")
        return SimpleNamespace(token="one-refresh", expires_on=4102444800)
"#,
            )
            .unwrap()
        });
        let credential = Arc::new(Python::with_gil(|py| {
            PyTokenCredential::new(object.clone_ref(py))
        }));
        let first = {
            let credential = credential.clone();
            tokio::spawn(async move { credential.get_token_async(&["scope"]).await })
        };
        let started = Python::with_gil(|py| object.bind(py).getattr("started").unwrap().unbind());
        assert!(tokio::task::spawn_blocking(move || Python::with_gil(|py| {
            started
                .bind(py)
                .call_method1("wait", (2.0,))
                .unwrap()
                .extract::<bool>()
                .unwrap()
        }))
        .await
        .unwrap());
        first.abort();
        assert!(first.await.unwrap_err().is_cancelled());
        let mut second = {
            let credential = credential.clone();
            tokio::spawn(async move { credential.get_token_async(&["scope"]).await })
        };
        assert!(
            tokio::time::timeout(std::time::Duration::from_millis(30), &mut second)
                .await
                .is_err()
        );
        Python::with_gil(|py| {
            assert_eq!(
                object
                    .bind(py)
                    .getattr("calls")
                    .unwrap()
                    .extract::<usize>()
                    .unwrap(),
                1
            );
            object
                .bind(py)
                .getattr("release")
                .unwrap()
                .call_method0("set")
                .unwrap();
        });
        assert_eq!(second.await.unwrap().unwrap().token.secret(), "one-refresh");
        Python::with_gil(|py| {
            assert_eq!(
                object
                    .bind(py)
                    .getattr("calls")
                    .unwrap()
                    .extract::<usize>()
                    .unwrap(),
                1
            );
        });
    }

    #[tokio::test]
    async fn operation_deadline_cancels_async_token_future() {
        pyo3::prepare_freethreaded_python();
        let object = Python::with_gil(|py| {
            make_python_credential(
                py,
                r#"
from concurrent.futures import Future
class Credential:
    def __init__(self):
        self.future = Future()
    def _start_token_request(self, *scopes):
        return self.future
"#,
            )
            .unwrap()
        });
        let credential = Python::with_gil(|py| PyTokenCredential::new(object.clone_ref(py)));
        assert!(tokio::time::timeout(
            std::time::Duration::from_millis(20),
            credential.get_token_async(&["scope"]),
        )
        .await
        .is_err());
        Python::with_gil(|py| {
            assert!(object
                .bind(py)
                .getattr("future")
                .unwrap()
                .call_method0("cancelled")
                .unwrap()
                .extract::<bool>()
                .unwrap());
        });
        assert!(credential.cached_fresh_token(&["scope"]).is_none());
    }

    #[tokio::test]
    async fn async_token_completion_converts_and_caches_result() {
        pyo3::prepare_freethreaded_python();
        let object = Python::with_gil(|py| {
            make_python_credential(
                py,
                r#"
from concurrent.futures import Future
from types import SimpleNamespace
class Credential:
    def __init__(self):
        self.calls = 0
    def _start_token_request(self, *scopes):
        self.calls += 1
        future = Future()
        future.set_result(SimpleNamespace(token="async-token", expires_on=4102444800))
        return future
"#,
            )
            .unwrap()
        });
        let credential = Python::with_gil(|py| PyTokenCredential::new(object.clone_ref(py)));
        assert_eq!(
            credential
                .get_token_async(&["scope"])
                .await
                .unwrap()
                .token
                .secret(),
            "async-token"
        );
        assert_eq!(
            credential
                .get_token_async(&["scope"])
                .await
                .unwrap()
                .token
                .secret(),
            "async-token"
        );
        Python::with_gil(|py| {
            assert_eq!(
                object
                    .bind(py)
                    .getattr("calls")
                    .unwrap()
                    .extract::<u32>()
                    .unwrap(),
                1
            );
        });
    }

    #[tokio::test]
    async fn native_cancellation_reaches_real_async_credential_bridge() {
        pyo3::prepare_freethreaded_python();
        let (bridge, customer) = Python::with_gil(|py| {
            let customer = make_python_credential(
                py,
                r#"
import asyncio
import threading
class Credential:
    def __init__(self):
        self.started = threading.Event()
        self.cancelled = threading.Event()
        self.loop = asyncio.new_event_loop()
        ready = threading.Event()
        self.loop.call_soon(ready.set)
        self.owner = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.owner.start()
        assert ready.wait(2)
    def close_owner_loop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.owner.join(2)
        assert not self.owner.is_alive()
        self.loop.close()
    async def get_token(self, *scopes):
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled.set()
"#,
            )
            .unwrap();
            let module = PyModule::from_code_bound(
                py,
                include_str!("../../azure/cosmos/_backend/_async_credential_bridge.py"),
                "credential_bridge_test.py",
                "credential_bridge_test",
            )
            .unwrap();
            let kwargs = pyo3::types::PyDict::new_bound(py);
            kwargs
                .set_item("loop", customer.bind(py).getattr("loop").unwrap())
                .unwrap();
            let bridge = module
                .getattr("AsyncTokenCredentialBridge")
                .unwrap()
                .call((customer.bind(py),), Some(&kwargs))
                .unwrap()
                .unbind();
            (bridge, customer)
        });
        let credential = Python::with_gil(|py| PyTokenCredential::new(bridge.clone_ref(py)));
        let task = tokio::spawn(async move { credential.get_token_async(&["scope"]).await });
        let started = Python::with_gil(|py| customer.bind(py).getattr("started").unwrap().unbind());
        assert!(tokio::task::spawn_blocking(move || Python::with_gil(|py| {
            started
                .bind(py)
                .call_method1("wait", (2.0,))
                .unwrap()
                .extract::<bool>()
                .unwrap()
        }))
        .await
        .unwrap());
        task.abort();
        assert!(task.await.unwrap_err().is_cancelled());
        Python::with_gil(|py| {
            assert!(customer
                .bind(py)
                .getattr("cancelled")
                .unwrap()
                .call_method1("wait", (2.0,))
                .unwrap()
                .extract::<bool>()
                .unwrap());
            bridge
                .bind(py)
                .call_method0("_close_cosmos_async_bridge")
                .unwrap();
            assert!(bridge
                .bind(py)
                .getattr("_loop")
                .unwrap()
                .call_method0("is_running")
                .unwrap()
                .extract::<bool>()
                .unwrap());
            customer
                .bind(py)
                .call_method0("close_owner_loop")
                .unwrap();
        });
    }
}
