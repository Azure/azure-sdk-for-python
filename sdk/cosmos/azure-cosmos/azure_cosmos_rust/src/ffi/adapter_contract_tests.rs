// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Call the real PyO3 exports against the driver's in-memory HTTP implementation.

use crate::driver_runtime::RuntimeHandle;
use crate::runtime::{acquire_driver_handle, runtime_context};
use azure_data_cosmos_driver::{
    in_memory_emulator::{
        ContainerConfig, InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
    },
    models::PartitionKeyDefinition,
};
use pyo3::{
    exceptions::{PyTimeoutError, PyTypeError},
    prelude::*,
    types::{PyDict, PyTuple},
};
use std::sync::Arc;
use url::Url;

const OPERATIONS: &[&str] = &[
    "read_item",
    "upsert_item",
    "delete_item",
    "delete_container",
    "read_feed_ranges",
    "feed_range_from_partition_key",
    "is_feed_range_subset",
];

fn exercise(
    operation: &str,
    asynchronous: bool,
    timeout: Option<f64>,
    attempts: bool,
    delayed: bool,
    fault_diagnostics: bool,
) {
    crate::test_support::prepare_python();
    let endpoint = Url::parse("https://adapter-contract.emulator.local").unwrap();
    let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
        VirtualAccountConfig::new(vec![VirtualRegion::new("East US", endpoint.clone())]).unwrap(),
    ));
    emulator.store().create_database("db");
    emulator.store().create_container_with_config(
        "db",
        "c",
        PartitionKeyDefinition::new(vec!["/pk".into()]),
        ContainerConfig::new()
            .with_partition_count(1)
            .build()
            .unwrap(),
    );
    let runtime = runtime_context()
        .tokio_rt
        .block_on(emulator.runtime_builder().build())
        .unwrap();
    Python::with_gil(|py| {
        let exports = PyModule::new_bound(py, "adapter_contract_exports").unwrap();
        crate::_rust(py, &exports).unwrap();
        let helper = PyModule::from_code_bound(py, r#"
import asyncio
from types import SimpleNamespace

def prepared(op, settings, partition_key):
    body = b'{"id":"item","pk":"A"}'
    if op == "read_feed_ranges":
        body = b'{"forceRefresh":true}'
    elif op == "is_feed_range_subset":
        body = b'{"parent":{"Range":{"min":"","max":"FF","isMinInclusive":true,"isMaxInclusive":false}},"child":{"Range":{"min":"","max":"FF","isMinInclusive":true,"isMaxInclusive":false}}}'
    return SimpleNamespace(
        protocol_version=3, op=op, container_link="dbs/db/colls/c",
        item_id="item", item_self_link=None, headers={}, body_bytes=body,
        partition_key=partition_key, settings=settings)

def config():
    return SimpleNamespace(fault_injection_rules=(SimpleNamespace(
        id="slow-metadata", operation_type="MetadataReadContainer",
        status_code=400, sub_status=0, container_id=None, region=None,
        delay_ms=400, probability=1.0, hit_limit=None, enabled=True),))

async def await_call(function, handle, request, kwargs):
    return await function(handle, request, **kwargs)

def invoke(function, handle, request, asynchronous, timeout, attempts, fault_diagnostics):
    kwargs = {"include_attempts": attempts}
    if fault_diagnostics:
        kwargs["include_fault_diagnostics"] = True
    if timeout is not None:
        kwargs["timeout_seconds"] = timeout
    if asynchronous:
        return asyncio.run(await_call(function, handle, request, kwargs))
    return function(handle, request, **kwargs)
"#, "adapter_contract_test.py", "adapter_contract_test").unwrap();
        let runtime = Py::new(py, RuntimeHandle::new(runtime)).unwrap();
        let config = delayed.then(|| helper.getattr("config").unwrap().call0().unwrap());
        let handle = Py::new(
            py,
            acquire_driver_handle(
                py,
                endpoint.as_str(),
                Some("ZW11bGF0b3Ita2V5"),
                config.as_ref(),
                None,
                Some(runtime.borrow(py)),
            )
            .unwrap(),
        )
        .unwrap();
        let request = helper
            .getattr("prepared")
            .unwrap()
            .call1((
                operation,
                crate::wire::settings::test_settings(py),
                crate::wire::partition_key_input::test_partition_key(py, Some("[\"A\"]")),
            ))
            .unwrap();
        if matches!(operation, "read_item" | "delete_item") && !delayed {
            request.setattr("op", "upsert_item").unwrap();
            exports
                .getattr("upsert_item")
                .unwrap()
                .call1((&handle, &request))
                .unwrap();
            request.setattr("op", operation).unwrap();
        }
        let name = format!("{operation}{}", if asynchronous { "_async" } else { "" });
        let result = helper.getattr("invoke").unwrap().call1((
            exports.getattr(name.as_str()).unwrap(),
            &handle,
            request,
            asynchronous,
            timeout,
            attempts,
            fault_diagnostics,
        ));
        if delayed {
            let error = result.unwrap_err();
            assert!(
                error.is_instance_of::<PyTimeoutError>(py),
                "{name}: {error}"
            );
            assert!(
                crate::runtime::_debug_fault_injection_rule_hit_count(
                    &handle.borrow(py),
                    "slow-metadata",
                )
                .unwrap()
                    > 0,
                "{name} must reach the delayed metadata request"
            );
        } else {
            let result = result.unwrap_or_else(|error| panic!("{name}: {error}"));
            let response = if attempts || fault_diagnostics {
                assert_eq!(result.downcast::<PyTuple>().unwrap().len(), 2);
                if fault_diagnostics {
                    let payload = result.get_item(1).unwrap();
                    assert!(payload.get_item("request_count").unwrap().extract::<u64>().unwrap() > 0);
                    assert!(payload.get_item("requests").unwrap().len().unwrap() > 0);
                    assert_eq!(
                        payload.get_item("result_status").unwrap().extract::<u16>().unwrap(),
                        result.get_item(0).unwrap().get_item(0).unwrap().extract::<u16>().unwrap(),
                    );
                }
                result.get_item(0).unwrap()
            } else {
                result
            };
            assert_eq!(response.downcast::<PyTuple>().unwrap().len(), 5);
            let status: u16 = response.get_item(0).unwrap().extract().unwrap();
            assert!((200..300).contains(&status), "{name}: status {status}");
            if operation == "is_feed_range_subset" {
                let body: Vec<u8> = response.get_item(3).unwrap().extract().unwrap();
                assert_eq!(
                    serde_json::from_slice::<serde_json::Value>(&body).unwrap()["IsSubset"],
                    true
                );
            }
        }
    });
}

#[test]
fn lifecycle_probe_exports_match_build_feature() {
    crate::test_support::prepare_python();
    Python::with_gil(|py| {
        let exports = PyModule::new_bound(py, "probe_contract_exports").unwrap();
        crate::_rust(py, &exports).unwrap();
        let enabled = cfg!(feature = "test-probes");
        assert_eq!(exports.hasattr("_AsyncOperationProbe").unwrap(), enabled);
        for name in [
            "_debug_operation_count",
            "_debug_attempt_count",
            "_debug_retry_count",
            "_debug_fault_injection_rule_hit_count",
            "_debug_set_fault_injection_rule_enabled",
            "_debug_cached_account_regions",
        ] {
            assert_eq!(exports.hasattr(name).unwrap(), enabled, "{name}");
        }
        let read = exports.getattr("read_item_async").unwrap();
        let signature: String = read
            .getattr("__text_signature__")
            .unwrap()
            .extract()
            .unwrap();
        assert_eq!(signature.contains("_debug_lifecycle"), enabled);
        for name in ["create_item", "create_item_async", "upsert_item", "upsert_item_async", "read_item", "read_item_async"] {
            let function = exports.getattr(name).unwrap();
            let signature: String = function.getattr("__text_signature__").unwrap().extract().unwrap();
            assert_eq!(signature.contains("include_fault_diagnostics"), enabled, "{name}");
            assert!(signature.contains("include_attempts"), "{name}");
            if !enabled {
                for value in [false, true] {
                    let kwargs = PyDict::new_bound(py);
                    kwargs.set_item("include_fault_diagnostics", value).unwrap();
                    let error = function.call((py.None(), py.None()), Some(&kwargs)).unwrap_err();
                    assert!(error.is_instance_of::<PyTypeError>(py));
                    assert!(error.to_string().contains("unexpected keyword argument 'include_fault_diagnostics'"));
                }
            }
        }
        if enabled {
            let probe = exports
                .getattr("_AsyncOperationProbe")
                .unwrap()
                .call0()
                .unwrap();
            assert_eq!(
                probe
                    .getattr("status")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "created"
            );
        } else {
            let kwargs = PyDict::new_bound(py);
            kwargs.set_item("_debug_lifecycle", py.None()).unwrap();
            let error = read
                .call((py.None(), py.None()), Some(&kwargs))
                .unwrap_err();
            assert!(error.is_instance_of::<PyTypeError>(py));
            assert!(error
                .to_string()
                .contains("unexpected keyword argument '_debug_lifecycle'"));
        }
    });
}

#[test]
fn mapped_exports_preserve_success_with_deadlines_and_attempt_envelopes() {
    for operation in OPERATIONS {
        for asynchronous in [false, true] {
            for attempts in [false, true] {
                for timeout in [None, Some(2.0)] {
                    exercise(operation, asynchronous, timeout, attempts, false, false);
                }
            }
        }
    }
}

#[test]
fn mapped_exports_enforce_subsecond_deadline_during_driver_metadata() {
    for operation in OPERATIONS
        .iter()
        .filter(|op| **op != "is_feed_range_subset")
    {
        for asynchronous in [false, true] {
            for attempts in [false, true] {
                exercise(operation, asynchronous, Some(0.125), attempts, true, false);
            }
        }
    }
}

#[cfg(feature = "test-probes")]
#[test]
fn item_exports_preserve_fault_diagnostics_in_probe_builds() {
    for operation in ["create_item", "upsert_item", "read_item"] {
        for asynchronous in [false, true] {
            exercise(operation, asynchronous, None, false, false, true);
        }
    }
}
