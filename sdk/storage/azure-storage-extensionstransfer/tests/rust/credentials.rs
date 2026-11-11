// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;
use std::ffi::CString;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Barrier;

use azure_core::time::OffsetDateTime;
use pyo3::ffi::c_str;

fn provider(py: Python<'_>) -> Bound<'_, PyModule> {
    static NEXT_MODULE: AtomicUsize = AtomicUsize::new(0);
    let name = CString::new(format!(
        "credential_fixture_{}",
        NEXT_MODULE.fetch_add(1, Ordering::Relaxed)
    ))
    .unwrap();
    let module = PyModule::from_code(
        py,
        c_str!(
            r#"calls = []
fail = False
invalid = False
def provider(scopes):
    calls.append(scopes)
    if fail:
        raise RuntimeError('callback failed')
    if invalid:
        return ('token',)
    return ('fresh-token', expiry)
"#
        ),
        c_str!("credential_fixture.py"),
        &name,
    )
    .unwrap();
    module
        .setattr("expiry", OffsetDateTime::now_utc().unix_timestamp() + 3600)
        .unwrap();
    module
}

fn token(credential: &PyCallbackCredential) -> azure_core::Result<AccessToken> {
    crate::get_runtime()
        .unwrap()
        .block_on(credential.get_token(&["scope-a", "scope-b"], None))
}

#[test]
fn callback_receives_scopes_and_valid_token_is_reused() {
    Python::initialize();
    Python::attach(|py| {
        let module = provider(py);
        let credential = PyCallbackCredential::new(module.getattr("provider").unwrap().unbind());
        let first = token(&credential).unwrap();
        let second = token(&credential).unwrap();
        assert_eq!(first.token.secret(), "fresh-token");
        assert_eq!(second.token.secret(), "fresh-token");
        assert_eq!(
            first.expires_on,
            module
                .getattr("expiry")
                .unwrap()
                .extract::<i64>()
                .map(|timestamp| OffsetDateTime::from_unix_timestamp(timestamp).unwrap())
                .unwrap()
        );
        assert_eq!(
            module
                .getattr("calls")
                .unwrap()
                .extract::<Vec<Vec<String>>>()
                .unwrap(),
            vec![vec!["scope-a".to_string(), "scope-b".to_string()]],
        );
    });
}

#[test]
fn expired_and_near_expiry_tokens_refresh_once() {
    Python::initialize();
    Python::attach(|py| {
        for remaining in [-60, 120] {
            let module = provider(py);
            let credential =
                PyCallbackCredential::new(module.getattr("provider").unwrap().unbind());
            *credential.cache.write().unwrap() = Some((
                "old-token".to_string(),
                OffsetDateTime::now_utc() + azure_core::time::Duration::seconds(remaining),
            ));
            assert_eq!(token(&credential).unwrap().token.secret(), "fresh-token");
            assert_eq!(token(&credential).unwrap().token.secret(), "fresh-token");
            assert_eq!(module.getattr("calls").unwrap().len().unwrap(), 1);
        }
    });
}

#[test]
fn concurrent_callers_share_one_refresh() {
    Python::initialize();
    Python::attach(|py| {
        let module = provider(py);
        let credential = Arc::new(PyCallbackCredential::new(
            module.getattr("provider").unwrap().unbind(),
        ));
        *credential.cache.write().unwrap() = Some((
            "expired-token".to_string(),
            OffsetDateTime::now_utc() - azure_core::time::Duration::hours(1),
        ));
        let barrier = Arc::new(Barrier::new(8));
        let handles: Vec<_> = (0..8)
            .map(|_| {
                let credential = credential.clone();
                let barrier = barrier.clone();
                std::thread::spawn(move || {
                    barrier.wait();
                    token(&credential).unwrap().token.secret().to_string()
                })
            })
            .collect();
        py.detach(move || {
            for handle in handles {
                assert_eq!(handle.join().unwrap(), "fresh-token");
            }
        });
        assert_eq!(module.getattr("calls").unwrap().len().unwrap(), 1);
    });
}

#[test]
fn callback_failure_does_not_cache_and_can_recover() {
    Python::initialize();
    Python::attach(|py| {
        let module = provider(py);
        module.setattr("fail", true).unwrap();
        let credential = PyCallbackCredential::new(module.getattr("provider").unwrap().unbind());
        assert!(token(&credential).is_err());
        assert!(credential.cache.read().unwrap().is_none());
        module.setattr("fail", false).unwrap();
        assert_eq!(token(&credential).unwrap().token.secret(), "fresh-token");
        assert_eq!(module.getattr("calls").unwrap().len().unwrap(), 2);
    });
}

#[test]
fn invalid_callback_result_and_expiry_do_not_cache() {
    Python::initialize();
    Python::attach(|py| {
        for invalid_shape in [true, false] {
            let module = provider(py);
            module.setattr("invalid", invalid_shape).unwrap();
            module.setattr("expiry", i64::MAX).unwrap();
            let credential =
                PyCallbackCredential::new(module.getattr("provider").unwrap().unbind());
            assert!(token(&credential).is_err());
            assert!(credential.cache.read().unwrap().is_none());
            assert_eq!(module.getattr("calls").unwrap().len().unwrap(), 1);
        }
    });
}
