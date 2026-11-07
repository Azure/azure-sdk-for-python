# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Explicit local-only test inventory; sources remain available for migration."""

from pathlib import Path


TESTS_ROOT = Path(__file__).resolve().parents[1]

# Do not replace this inventory with a root-level test_*.py wildcard: shared
# wrapper, packaging, paging, and Rust change-feed checks also live at the root.
LEGACY_MODULES = frozenset({
    "test_aad.py",
    "test_aad_async.py",
    "test_aad_inference_service_lazy_init.py",
    "test_aad_inference_service_lazy_init_async.py",
    "test_aggregate.py",
    "test_analytical_ttl.py",
    "test_analytical_ttl_async.py",
    "test_availability_strategy.py",
    "test_availability_strategy_async.py",
    "test_backwards_compatibility.py",
    "test_backwards_compatibility_async.py",
    "test_change_feed.py",
    "test_change_feed_all_versions.py",
    "test_change_feed_all_versions_async.py",
    "test_change_feed_async.py",
    "test_changefeed_partition_key_variation.py",
    "test_changefeed_partition_key_variation_async.py",
    "test_child_range_diagnostics_unit.py",
    "test_circuit_breaker_emulator.py",
    "test_circuit_breaker_emulator_async.py",
    "test_client_user_agent_async.py",
    "test_compact_utf8_resilience.py",
    "test_computed_properties.py",
    "test_computed_properties_async.py",
    "test_config.py",
    "test_container_properties_cache.py",
    "test_container_properties_cache_async.py",
    "test_container_rid_header_unit.py",
    "test_container_rid_header_unit_async.py",
    "test_content_length_encoding.py",
    "test_cosmos_http_logging_policy.py",
    "test_cosmos_http_logging_policy_async.py",
    "test_cosmos_responses.py",
    "test_cosmos_responses_async.py",
    "test_crud.py",
    "test_crud_async.py",
    "test_crud_container.py",
    "test_crud_container_async.py",
    "test_crud_database.py",
    "test_crud_database_async.py",
    "test_crud_response_payload_on_write_disabled.py",
    "test_crud_response_payload_on_write_disabled_async.py",
    "test_crud_subpartition.py",
    "test_crud_subpartition_async.py",
    "test_effective_preferred_locations.py",
    "test_effective_preferred_locations_async.py",
    "test_encoding.py",
    "test_encoding_async.py",
    "test_excluded_locations.py",
    "test_excluded_locations_async.py",
    "test_excluded_locations_emulator.py",
    "test_excluded_locations_emulator_async.py",
    "test_fault_injection_transport.py",
    "test_fault_injection_transport_async.py",
    "test_feed_range.py",
    "test_feed_range_async.py",
    "test_feed_range_continuation_token.py",
    "test_full_text_policy.py",
    "test_full_text_policy_async.py",
    "test_global_secondary_index_live.py",
    "test_globaldb.py",
    "test_globaldb_mock.py",
    "test_headers.py",
    "test_headers_async.py",
    "test_health_check.py",
    "test_health_check_async.py",
    "test_hybrid_search_aggregator.py",
    "test_integrated_cache.py",
    "test_item_body_serialization.py",
    "test_location_cache.py",
    "test_location_cache_async.py",
    "test_multi_execution_aggregator_unit.py",
    "test_multi_execution_aggregator_unit_async.py",
    "test_multi_orderby.py",
    "test_multimaster.py",
    "test_none_options.py",
    "test_none_options_async.py",
    "test_orderby.py",
    "test_partition_key.py",
    "test_partition_key_async.py",
    "test_partition_split_query.py",
    "test_partition_split_query_async.py",
    "test_partition_split_retry_unit.py",
    "test_partition_split_retry_unit_async.py",
    "test_partition_split_scenarios.py",
    "test_partition_split_scenarios_async.py",
    "test_per_partition_automatic_failover.py",
    "test_per_partition_automatic_failover_async.py",
    "test_per_partition_circuit_breaker_mm.py",
    "test_per_partition_circuit_breaker_mm_async.py",
    "test_per_partition_circuit_breaker_sm_mrr.py",
    "test_per_partition_circuit_breaker_sm_mrr_async.py",
    "test_pk_range_child_update_live_async.py",
    "test_pk_range_drain.py",
    "test_pk_range_drain_async.py",
    "test_query.py",
    "test_query_aggregate_utils_unit_async.py",
    "test_query_async.py",
    "test_query_cross_partition.py",
    "test_query_cross_partition_async.py",
    "test_query_execution_context.py",
    "test_query_feed_range.py",
    "test_query_feed_range_async.py",
    "test_query_feed_range_multipartition.py",
    "test_query_feed_range_multipartition_async.py",
    "test_query_hybrid_search.py",
    "test_query_hybrid_search_async.py",
    "test_query_response_headers.py",
    "test_query_response_headers_async.py",
    "test_query_vector_similarity.py",
    "test_query_vector_similarity_async.py",
    "test_read_items.py",
    "test_read_items_async.py",
    "test_regional_routing_context.py",
    "test_regional_routing_context_async.py",
    "test_request_response_decoding.py",
    "test_resource_id.py",
    "test_resource_id_async.py",
    "test_response_decoding.py",
    "test_response_decoding_paged.py",
    "test_retry_policy.py",
    "test_retry_policy_async.py",
    "test_retryable_writes.py",
    "test_retryable_writes_async.py",
    "test_routing_map.py",
    "test_routing_map_provider_unit.py",
    "test_routing_map_provider_unit_async.py",
    "test_semantic_reranker.py",
    "test_semantic_reranker_async.py",
    "test_semantic_reranker_unit.py",
    "test_service_request_retry_policy.py",
    "test_service_request_retry_policy_async.py",
    "test_service_retry_policies.py",
    "test_service_retry_policies_async.py",
    "test_session.py",
    "test_session_async.py",
    "test_session_token_unit.py",
    "test_shared_cache_fault_injection.py",
    "test_shared_cache_fault_injection_async.py",
    "test_shared_cache_integration.py",
    "test_shared_cache_integration_async.py",
    "test_split_test_utils.py",
    "test_streaming_failover.py",
    "test_timeout_and_failover_retry_policy.py",
    "test_timeout_and_failover_retry_policy_async.py",
    "test_transactional_batch.py",
    "test_transactional_batch_async.py",
    "test_transport_body_encoding.py",
    "test_ttl.py",
    "test_user_agent.py",
    "test_user_agent_async.py",
    "test_user_agent_overwrite_regression.py",
    "test_user_agent_overwrite_regression_async.py",
    "test_user_configs.py",
    "test_vector_policy.py",
    "test_vector_policy_async.py",
    "common/test_legacy_backend_unit.py",
    "patch_item/sync/core_python/test_headers.py",
    "patch_item/aio/core_python/test_headers.py",
})

LOCAL_COMPARISON_MODULES = frozenset({
    "binding/test_binding_contract_parity.py",
    "common/test_write_session_token_emulator.py",
})

# These existing files mix local comparisons with independently useful Rust
# checks. Keep the latter without moving or editing their assertion bodies.
RETAINED_COMPARISON_TESTS = {
    "binding/test_binding_contract_parity.py": frozenset({
        "test_binding_rejects_invalid_timeout_with_real_handle",
    }),
    "common/test_write_session_token_emulator.py": frozenset({
        "test_future_token_is_enforced_on_a_read_rust",
    }),
}

# Only these service tests parameterize real client selection. Unit tests using
# fake Adapters must not lose their compatibility-contract cases.
ADAPTER_PARAMETER_MODULES = frozenset({
    "common/test_write_session_token_emulator.py",
    "create_item/aio/test_legacy_contracts.py",
    "create_item/aio/test_legacy_variants.py",
    "create_item/sync/test_legacy_contracts.py",
    "create_item/sync/test_legacy_variants.py",
})


def relative_test_path(path, tests_root=None):
    try:
        return Path(path).resolve().relative_to(Path(tests_root or TESTS_ROOT).resolve()).as_posix()
    except ValueError:
        return None


def exclude_module(path, *, tests_root=None):
    relative = relative_test_path(path, tests_root)
    return relative in LEGACY_MODULES or (
        relative in LOCAL_COMPARISON_MODULES and relative not in RETAINED_COMPARISON_TESTS
    )


def exclude_test(path, name):
    relative = relative_test_path(path)
    return relative in LEGACY_MODULES or (
        relative in LOCAL_COMPARISON_MODULES
        and name not in RETAINED_COMPARISON_TESTS.get(relative, ())
    )


def exclude_parameters(path, parameters):
    if relative_test_path(path) not in ADAPTER_PARAMETER_MODULES:
        return False
    return any(parameters.get(name) in ("core-python", "core_python") for name in ("backend", "backend_name"))
