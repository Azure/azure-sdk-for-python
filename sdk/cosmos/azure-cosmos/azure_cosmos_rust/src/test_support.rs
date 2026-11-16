// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::prelude::*;
use std::sync::Once;

pub(crate) fn prepare_python() {
    static IMPORTS: Once = Once::new();

    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        // Imports release the GIL; another test must not hold it while waiting
        // for the initializer to finish importing the shared package graph.
        py.allow_threads(|| {
            IMPORTS.call_once(|| {
                Python::with_gil(|py| {
                    py.import_bound("azure.cosmos")
                        .expect("initialize the synchronous Python SDK for binding tests");
                    py.import_bound("azure.cosmos.aio")
                        .expect("initialize the asynchronous Python SDK for binding tests");
                });
            });
        });
    });
}

#[test]
fn parallel_initialization_with_and_without_gil_is_safe() {
    use std::{sync::Barrier, thread};

    pyo3::prepare_freethreaded_python();
    let ready = Barrier::new(8);
    let modules = [
        ("azure.core.credentials", "AccessToken"),
        ("azure.cosmos._base", "create_scope_from_url"),
        (
            "azure.cosmos._auth_policy",
            "CosmosBearerTokenCredentialPolicy",
        ),
        (
            "azure.cosmos.aio._auth_policy_async",
            "AsyncCosmosBearerTokenCredentialPolicy",
        ),
    ];
    thread::scope(|scope| {
        for index in 0..8 {
            let ready = &ready;
            let (module, attribute) = modules[index % modules.len()];
            scope.spawn(move || {
                ready.wait();
                if index % 2 == 0 {
                    Python::with_gil(|_| prepare_python());
                } else {
                    prepare_python();
                }
                Python::with_gil(|py| {
                    py.import_bound(module).unwrap().getattr(attribute).unwrap();
                });
            });
        }
    });
}
