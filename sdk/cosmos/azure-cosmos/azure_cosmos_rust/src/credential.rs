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
//! Async bridges supply a cancellable Python future. Native work awaits its
//! completion without blocking a Tokio worker; dropping the native wait (including
//! an operation timeout) cancels that Python future. Ordinary synchronous
//! credentials run on Tokio's blocking pool; their Python code cannot be forcibly
//! interrupted when the enclosing operation stops waiting.
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
use parking_lot::{Mutex, RwLock};
use std::sync::Arc;
use tokio::sync::oneshot;

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
            // A dropped receiver means the native operation has already ended.
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
    // Keep one scope-qualified entry rather than an unbounded scope cache.
    cached_token: Arc<RwLock<Option<CachedToken>>>,
    refresh: Arc<tokio::sync::Mutex<()>>,
}

impl PyTokenCredential {
    /// Take ownership of a strong reference to the customer's Python credential.
    /// Driver acquisition creates this adapter when building a token-authenticated
    /// driver. Clients reusing a cached driver also reuse its adapter.
    pub(crate) fn new(credential: Py<PyAny>) -> Self {
        Self {
            credential,
            cached_token: Arc::new(RwLock::new(None)),
            refresh: Arc::new(tokio::sync::Mutex::new(())),
        }
    }

    /// With the GIL already held, call Python's `get_token(*scopes)` and convert
    /// its `.token` and `.expires_on` fields into an `AccessToken`.
    /// Reject empty tokens and unrepresentable expiry timestamps, mapping these
    /// and Python extraction/call errors to credential errors. A newly fetched
    /// token is not checked for expiry against the current time here.
    fn fetch_token(
        credential: &Bound<'_, PyAny>,
        scopes: &[&str],
    ) -> azure_core::Result<AccessToken> {
        let py = credential.py();
        let scopes_arg = PyTuple::new_bound(py, scopes);
        let token_obj = credential
            .call_method1("get_token", scopes_arg)
            .map_err(|e| credential_error(format!("token credential get_token() failed: {e}")))?;
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

    /// Return the cached token only if it still has more than 5 minutes of life
    /// left. This margin limits cache reuse; it does not guarantee that a token
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
        if let Some(token) = self.cached_fresh_token(scopes) {
            return Ok(token);
        }

        let fresh = Python::with_gil(|py| Self::fetch_token(self.credential.bind(py), scopes))?;
        *self.cached_token.write() = Some(CachedToken {
            scopes: scopes.iter().map(|scope| (*scope).to_owned()).collect(),
            token: fresh.clone(),
        });
        Ok(fresh)
    }

    async fn get_token_async(&self, scopes: &[&str]) -> azure_core::Result<AccessToken> {
        if let Some(token) = self.cached_fresh_token(scopes) {
            return Ok(token);
        }
        let refresh = self.refresh.clone().lock_owned().await;
        if let Some(token) = self.cached_fresh_token(scopes) {
            return Ok(token);
        }
        let pending = Python::with_gil(|py| -> PyResult<_> {
            let credential = self.credential.bind(py);
            if !credential.hasattr("_start_token_request")? {
                return Ok(None);
            }
            let future =
                credential.call_method1("_start_token_request", PyTuple::new_bound(py, scopes))?;
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

        let fresh = match pending {
            Some((_guard, receiver)) => {
                let result = receiver
                    .await
                    .map_err(|_| credential_error("token result sender was dropped".to_string()))?
                    .map_err(|error| {
                        credential_error(format!("token credential get_token() failed: {error}"))
                    })?;
                Python::with_gil(|py| Self::parse_token(result.bind(py)))?
            }
            None => {
                let credential = Python::with_gil(|py| self.credential.clone_ref(py));
                let scopes: Vec<String> = scopes.iter().map(|scope| (*scope).to_string()).collect();
                let cache = self.cached_token.clone();
                return tokio::task::spawn_blocking(move || {
                    // Cancellation stops waiting, not synchronous Python code. Keep
                    // the refresh lock until that code finishes and publishes its token.
                    let _refresh = refresh;
                    let scope_refs: Vec<&str> = scopes.iter().map(String::as_str).collect();
                    let fresh =
                        Python::with_gil(|py| Self::fetch_token(credential.bind(py), &scope_refs))?;
                    *cache.write() = Some(CachedToken {
                        scopes,
                        token: fresh.clone(),
                    });
                    Ok(fresh)
                })
                .await
                .map_err(|error| credential_error(format!("token worker failed: {error}")))?;
            }
        };
        *self.cached_token.write() = Some(CachedToken {
            scopes: scopes.iter().map(|scope| (*scope).to_owned()).collect(),
            token: fresh.clone(),
        });
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
/// callback: `rust driver -> get_token (here) -> Python credential`.
#[async_trait::async_trait]
impl TokenCredential for PyTokenCredential {
    async fn get_token(
        &self,
        scopes: &[&str],
        options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        // azure_core 1.1.0 exposes native method context only, not claims or CAE.
        // Exhaustive destructuring makes added authentication options a compile-time review.
        let TokenRequestOptions { method_options: _ } = options.unwrap_or_default();
        self.get_token_async(scopes).await
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
            let bridge = module
                .getattr("AsyncTokenCredentialBridge")
                .unwrap()
                .call1((customer.bind(py),))
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
            assert!(!bridge
                .bind(py)
                .getattr("_thread")
                .unwrap()
                .call_method0("is_alive")
                .unwrap()
                .extract::<bool>()
                .unwrap());
        });
    }
}
