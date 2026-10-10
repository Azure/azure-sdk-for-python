// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Execute account-level throughput offer operations using the Rust driver.
//!
//! Reading throughput queries offers and returns an Offers list in body bytes.
//! Replacing throughput targets an offer resource id and returns one offer
//! record. Neither helper resolves an item container or partition key.

use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, SessionToken},
    options::{ContentResponseOnWrite, PlanOptions},
};

use super::diagnostics::BINDING_OP_COUNT;
use super::request::{build_operation_options, RequestHeadersAndOptions};
use super::response::{tuple_from_offer_feed_result, tuple_from_result};
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

/// Complete the offer query and return its binding response tuple.
/// Wait on the calling thread with Python's global interpreter lock (GIL) released.
pub(crate) fn run_read_offer_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result = py.allow_threads(|| {
        runtime_ctx
            .tokio_rt
            .block_on(run_read_offer_future(driver, modifiers, body_bytes))
    });

    tuple_from_offer_feed_result(py, response_result)
}

/// Async sibling of `run_read_offer_operation`.
pub(crate) fn run_read_offer_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx
        .tokio_rt
        .spawn(run_read_offer_future(driver, modifiers, body_bytes));
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_offer_feed_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

/// Replace the named offer and return its binding response tuple.
/// Wait on the calling thread with the GIL released; the body contains one record.
pub(crate) fn run_replace_offer_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(run_replace_offer_future(
            driver, modifiers, offer_id, body_bytes,
        ))
    });

    tuple_from_result(py, response_result)
}

/// Async sibling of `run_replace_offer_operation`.
pub(crate) fn run_replace_offer_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx.tokio_rt.spawn(run_replace_offer_future(
        driver, modifiers, offer_id, body_bytes,
    ));
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}
/// Build query_offers against the account using the prepared query body.
/// Add default query `Content-Type` and `x-ms-documentdb-isquery` markers only if
/// absent from custom headers. The prepared container-recreate guard header is
/// also supplied through those custom headers; this helper does not enforce it.
async fn run_read_offer_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
) -> Result<Vec<CosmosResponse>, CosmosError> {
    let account = driver.account().clone();
    let mut op = CosmosOperation::query_offers(account).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    let mut custom_headers = modifiers.custom_headers;
    custom_headers
        .entry(HeaderName::from_static("content-type"))
        .or_insert_with(|| HeaderValue::from("application/query+json".to_string()));
    custom_headers
        .entry(HeaderName::from_static("x-ms-documentdb-isquery"))
        .or_insert_with(|| HeaderValue::from("true".to_string()));

    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        custom_headers,
    );
    let mut plan = driver
        .plan_operation(op, &options, None, &PlanOptions::default())
        .await?;
    let mut responses = Vec::new();
    while let Some(response) = driver
        .execute_plan(&mut plan, None, options.clone())
        .await?
    {
        responses.push(response);
    }
    Ok(responses)
}

/// Build replace_offer using the offer resource id and prepared replacement body.
/// Pass through custom headers, including any container-recreate guard. The
/// Rust driver handles signing and execution; this helper does not enforce the guard.
async fn run_replace_offer_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let account = driver.account().clone();
    let mut op = CosmosOperation::replace_offer(account, offer_id).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    // Request response content because replace_throughput reads the returned
    // offer. Override the extracted no-response setting here; this option alone
    // does not guarantee that a service response contains a body.
    let content_response = Some(ContentResponseOnWrite::Enabled);
    let options = build_operation_options(
        content_response,
        modifiers.excluded_regions_value,
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_singleton_operation(op, options).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    use azure_core::http::{StatusCode, Url};
    use azure_data_cosmos_driver::{
        fault_injection::{
            CustomResponse, CustomResponseBuilder, FaultInjectionResultBuilder, FaultInjectionRule,
            FaultInjectionRuleBuilder,
        },
        in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
        models::AccountReference,
        options::DriverOptions,
    };
    use pyo3::types::PyBytes;

    fn page(
        status: StatusCode,
        body: &str,
        continuation: Option<&str>,
        charge: &str,
    ) -> CustomResponse {
        let mut response = CustomResponseBuilder::new(status)
            .with_header("x-ms-request-charge", charge.to_owned())
            .with_header("etag", format!("page-{charge}"))
            .with_body(body.as_bytes().to_vec());
        if let Some(token) = continuation {
            response = response.with_header("x-ms-continuation", token.to_owned());
        }
        response.build()
    }

    async fn setup(
        pages: Vec<CustomResponse>,
    ) -> (Arc<CosmosDriver>, Vec<Arc<FaultInjectionRule>>) {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://offers.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        let rules: Vec<_> = pages
            .into_iter()
            .enumerate()
            .map(|(index, response)| {
                let rule = Arc::new(
                    FaultInjectionRuleBuilder::new(
                        format!("offer-page-{index}"),
                        FaultInjectionResultBuilder::new()
                            .with_custom_response(response)
                            .build(),
                    )
                    .with_hit_limit(1)
                    .build(),
                );
                rule.disable();
                rule
            })
            .collect();
        let runtime = emulator
            .runtime_builder_with_fault_rules(rules.clone())
            .build()
            .await
            .unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .build(),
            )
            .await
            .unwrap();
        for rule in &rules {
            rule.enable();
        }
        (driver, rules)
    }

    fn modifiers() -> RequestHeadersAndOptions {
        RequestHeadersAndOptions {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            driver_timeout_policy: None,
            operation_timeout: None,
            availability_strategy: None,
            read_consistency_strategy: None,
            patch_strategy: None,
            custom_headers: HashMap::new(),
        }
    }

    #[tokio::test]
    async fn drains_empty_and_nonempty_offer_pages_and_keeps_final_headers() {
        let (driver, rules) = setup(vec![
            page(StatusCode::Ok, r#"{"Offers":[]}"#, Some("second"), "1"),
            page(StatusCode::Ok, r#"{"Offers":[{"id":"a","content":{"offerThroughput":4000}}]}"#, Some("third"), "2"),
            page(StatusCode::Ok, r#"{"Offers":[{"id":"b","content":{"offerAutopilotSettings":{"maxThroughput":10000}}}]}"#, None, "3"),
        ]).await;
        let result = run_read_offer_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        assert!(rules.iter().all(|rule| rule.hit_count() == 1));
        Python::with_gil(|py| {
            let response = tuple_from_offer_feed_result(py, result).unwrap();
            let bytes = response.get_item(3).unwrap();
            let body: serde_json::Value =
                serde_json::from_slice(bytes.downcast::<PyBytes>().unwrap().as_bytes()).unwrap();
            assert_eq!(body["Offers"].as_array().unwrap().len(), 2);
            assert_eq!(body["Offers"][0]["content"]["offerThroughput"], 4000);
            assert_eq!(
                body["Offers"][1]["content"]["offerAutopilotSettings"]["maxThroughput"],
                10000
            );
            let headers = response.get_item(2).unwrap();
            assert_eq!(
                headers
                    .get_item("etag")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "page-3"
            );
            assert_eq!(
                headers
                    .get_item("x-ms-request-charge")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "3"
            );
        });
    }

    #[tokio::test]
    async fn later_offer_failure_does_not_return_partial_success() {
        let (driver, rules) = setup(vec![
            page(
                StatusCode::Ok,
                r#"{"Offers":[{"id":"a"}]}"#,
                Some("second"),
                "1",
            ),
            page(
                StatusCode::Forbidden,
                r#"{"code":"Forbidden","message":"second page denied"}"#,
                None,
                "2",
            ),
        ])
        .await;
        let result = run_read_offer_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        assert!(result.is_err());
        assert!(rules.iter().all(|rule| rule.hit_count() == 1));
        Python::with_gil(|py| {
            let response = tuple_from_offer_feed_result(py, result).unwrap();
            assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), 403);
            assert_eq!(
                response
                    .get_item(2)
                    .unwrap()
                    .get_item("etag")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "page-2"
            );
        });
    }

    #[tokio::test]
    async fn empty_final_offer_page_is_a_complete_empty_result() {
        let (driver, rules) =
            setup(vec![page(StatusCode::Ok, r#"{"Offers":[]}"#, None, "1")]).await;
        let result = run_read_offer_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        assert_eq!(rules[0].hit_count(), 1);
        Python::with_gil(|py| {
            let response = tuple_from_offer_feed_result(py, result).unwrap();
            let bytes = response.get_item(3).unwrap();
            let body: serde_json::Value =
                serde_json::from_slice(bytes.downcast::<PyBytes>().unwrap().as_bytes()).unwrap();
            assert_eq!(body, serde_json::json!({"Offers":[]}));
        });
    }

    #[tokio::test]
    async fn malformed_later_offer_page_cannot_be_partial_success() {
        let (driver, _) = setup(vec![
            page(
                StatusCode::Ok,
                r#"{"Offers":[{"id":"a"}]}"#,
                Some("second"),
                "1",
            ),
            page(StatusCode::Ok, r#"{"Offers":"invalid"}"#, None, "2"),
        ])
        .await;
        let result = run_read_offer_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        Python::with_gil(|py| match result {
            Err(_) => {}
            Ok(responses) => assert!(tuple_from_offer_feed_result(py, Ok(responses)).is_err()),
        });
    }
}
