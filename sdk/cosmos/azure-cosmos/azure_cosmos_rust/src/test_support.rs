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
                    // Load this checkout's Python package, not an older azure-cosmos
                    // that happens to be installed in the Python environment.
                    let package_dir = concat!(env!("CARGO_MANIFEST_DIR"), "/..");
                    let sys = py.import_bound("sys").expect("import sys");
                    sys.getattr("path")
                        .and_then(|path| path.call_method1("insert", (0, package_dir)))
                        .expect("put the checkout's Python package first on sys.path");
                    // Register this test program's binding as azure.cosmos._rust.
                    // Otherwise the import below also loads the checkout's prebuilt
                    // _rust file, which may be older than the code under test.
                    let binding = pyo3::wrap_pymodule!(crate::_rust)(py);
                    sys.getattr("modules")
                        .and_then(|modules| modules.set_item("azure.cosmos._rust", binding))
                        .expect("register the binding under test as azure.cosmos._rust");
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
fn python_code_uses_the_binding_under_test() {
    prepare_python();
    Python::with_gil(|py| {
        let adapter = py
            .import_bound("azure.cosmos._backend.binding_adapter")
            .unwrap();
        let handle_type = adapter
            .getattr("_rust_module")
            .unwrap()
            .getattr("_DriverHandle")
            .unwrap();
        // A second, prebuilt copy of the binding would define its own type object.
        assert!(handle_type.is(&py.get_type_bound::<crate::runtime::DriverHandle>()));
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
