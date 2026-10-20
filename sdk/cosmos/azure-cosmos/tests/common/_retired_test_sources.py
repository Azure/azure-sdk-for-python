# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Approved original-test retirements and their retained Rust regression cases.

Source comments remain historical provenance. Only these explicit retirements
may resolve to retained tests instead of a live original.
"""

RETIRED_THROUGHPUT_SOURCES = {
    "tests/test_auto_scale.py::TestAutoScale.test_autoscale_create_container": (
        "tests/get_container_throughput/sync/legacy/test_auto_scale.py"
        "::TestAutoScale.test_autoscale_create_container_rust"
    ),
    "tests/test_auto_scale.py::TestAutoScale.test_autoscale_create_database": (
        "tests/get_database_throughput/sync/legacy/test_auto_scale.py"
        "::TestAutoScale.test_autoscale_create_database_rust"
    ),
    "tests/test_auto_scale.py::TestAutoScale.test_autoscale_replace_throughput": (
        "tests/replace_database_throughput/sync/legacy/test_auto_scale.py"
        "::TestAutoScale.test_autoscale_replace_throughput_rust"
    ),
    "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_container_async": (
        "tests/get_container_throughput/aio/legacy/test_auto_scale_async.py"
        "::TestAutoScaleAsync.test_autoscale_create_container_async_rust"
    ),
    "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_database_async": (
        "tests/get_database_throughput/aio/legacy/test_auto_scale.py"
        "::TestAutoScaleAsync.test_autoscale_create_database_async_rust"
    ),
    "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_replace_throughput_async": (
        "tests/replace_database_throughput/aio/legacy/test_auto_scale.py"
        "::TestAutoScaleAsync.test_replace_throughput_async_rust"
    ),
    "tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_offer_methods": (
        "tests/get_container_throughput/sync/legacy/test_backwards_compatibility.py"
        "::TestBackwardsCompatibility.test_offer_methods_rust"
    ),
    (
        "tests/test_container_properties_cache.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate"
    ): (
        "tests/get_container_throughput/sync/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCache.test_offer_throughput_container_recreate_rust"
    ),
    (
        "tests/test_container_properties_cache.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate_sub_partition"
    ): (
        "tests/get_container_throughput/sync/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCache.test_offer_throughput_container_recreate_sub_partition_rust"
    ),
    (
        "tests/test_container_properties_cache_async.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCacheAsync.test_offer_throughput_container_recreate_async_rust"
    ),
    (
        "tests/test_container_properties_cache_async.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate_sub_partition_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCacheAsync.test_offer_throughput_container_recreate_sub_partition_async_rust"
    ),
    "tests/test_cosmos_responses.py::TestCosmosResponses.test_container_replace_throughput": (
        "tests/get_database_throughput/sync/legacy/test_cosmos_responses.py"
        "::TestCosmosResponses.test_container_replace_throughput_rust"
    ),
    "tests/test_cosmos_responses.py::TestCosmosResponses.test_database_replace_throughput": (
        "tests/get_database_throughput/sync/legacy/test_cosmos_responses.py"
        "::TestCosmosResponses.test_database_replace_throughput_rust"
    ),
    "tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_container_replace_throughput_async": (
        "tests/get_database_throughput/aio/legacy/test_cosmos_responses.py"
        "::TestCosmosResponsesAsync.test_container_replace_throughput_async_rust"
    ),
    "tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_database_replace_throughput_async": (
        "tests/get_database_throughput/aio/legacy/test_cosmos_responses.py"
        "::TestCosmosResponsesAsync.test_database_replace_throughput_async_rust"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_offer_read_and_query": (
        "tests/get_container_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_offer_read_and_query_rust"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_offer_replace": (
        "tests/get_container_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_offer_replace_rust"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_replace_throughput_offer_with_int": (
        "tests/replace_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_replace_throughput_offer_with_int_rust"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_replace_throughput_offer_with_object": (
        "tests/replace_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_replace_throughput_offer_with_object_rust"
    ),
    (
        "tests/test_crud_container.py::TestCRUDContainerOperations"
        ".test_negative_replace_throughput_with_all_configs_set"
    ): (
        "tests/replace_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_negative_replace_throughput_with_all_configs_set_rust"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_offer_read_and_query_async": (
        "tests/get_container_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_offer_read_and_query_async_rust"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_offer_replace_async": (
        "tests/get_container_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_offer_replace_async_rust"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_int": (
        "tests/replace_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_int_rust"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_object": (
        "tests/replace_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_object_rust"
    ),
    (
        "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync"
        ".test_negative_replace_throughput_with_all_configs_set"
    ): (
        "tests/replace_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_negative_replace_throughput_with_all_configs_set_rust"
    ),
    "tests/test_crud_database.py::TestCRUDDatabaseOperations.test_database_level_offer_throughput": (
        "tests/get_database_throughput/sync/legacy/test_crud_database.py"
        "::TestCRUDDatabaseOperations.test_database_level_offer_throughput_rust"
    ),
    "tests/test_crud_database_async.py::TestCRUDDatabaseOperationsAsync.test_database_level_offer_throughput_async": (
        "tests/get_database_throughput/aio/legacy/test_crud_database.py"
        "::TestCRUDDatabaseOperationsAsync.test_database_level_offer_throughput_async_rust"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled"
        ".test_database_level_offer_throughput"
    ): (
        "tests/get_database_throughput/sync/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_database_level_offer_throughput_rust"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled_async.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_database_level_offer_throughput_async"
    ): (
        "tests/get_database_throughput/aio/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_database_level_offer_throughput_async_rust"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled"
        ".test_offer_read_and_query"
    ): (
        "tests/get_container_throughput/sync/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_offer_read_and_query_rust"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled"
        ".test_offer_replace"
    ): (
        "tests/get_container_throughput/sync/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_offer_replace_rust"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled_async.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_read_and_query_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_read_and_query_async_rust"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled_async.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_replace_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_replace_async_rust"
    ),
}

RETIRED_SESSION_TOKEN_SOURCES = {
    "tests/test_session_token_helpers.py::TestSessionTokenHelpers.test_get_session_token_update": (
        "tests/get_latest_session_token/sync/legacy/test_session_token_helpers_owned.py"
        "::TestSessionTokenHelpers.test_get_session_token_update_rust"
    ),
    "tests/test_session_token_helpers.py::TestSessionTokenHelpers.test_many_session_tokens_update_same_range": (
        "tests/get_latest_session_token/sync/legacy/test_session_token_helpers_owned.py"
        "::TestSessionTokenHelpers.test_many_session_tokens_update_same_range_rust"
    ),
    "tests/test_session_token_helpers.py::TestSessionTokenHelpers.test_many_session_tokens_update": (
        "tests/get_latest_session_token/sync/legacy/test_session_token_helpers_owned.py"
        "::TestSessionTokenHelpers.test_many_session_tokens_update_rust"
    ),
    "tests/test_session_token_helpers.py::TestSessionTokenHelpers.test_simulated_splits_merges": (
        "tests/get_latest_session_token/sync/legacy/test_session_token_helpers_owned.py"
        "::TestSessionTokenHelpers.test_simulated_splits_merges_rust"
    ),
    "tests/test_session_token_helpers.py::TestSessionTokenHelpers.test_invalid_feed_range": (
        "tests/get_latest_session_token/sync/legacy/test_session_token_helpers_owned.py"
        "::TestSessionTokenHelpers.test_invalid_feed_range_rust"
    ),
    "tests/test_partition_split_scenarios.py::TestPartitionSplitScenarios.test_latest_session_token_hpk": (
        "tests/get_latest_session_token/sync/legacy/test_latest_session_token.py"
        "::TestLatestSessionToken.test_latest_session_token_hpk_rust"
    ),
    "tests/test_partition_split_scenarios.py::TestPartitionSplitScenarios.test_latest_session_token_logical_hpk": (
        "tests/get_latest_session_token/sync/legacy/test_latest_session_token.py"
        "::TestLatestSessionToken.test_latest_session_token_logical_hpk_rust"
    ),
    "tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync.test_latest_session_token_hpk": (
        "tests/get_latest_session_token/aio/legacy/test_latest_session_token_async.py"
        "::TestLatestSessionTokenAsync.test_latest_session_token_hpk_rust"
    ),
    "tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync.test_latest_session_token_logical_hpk": (
        "tests/get_latest_session_token/aio/legacy/test_latest_session_token_async.py"
        "::TestLatestSessionTokenAsync.test_latest_session_token_logical_hpk_rust"
    ),
}

# Data provenance is separate: this is not a tenth retired test method.
RETIRED_SESSION_TOKEN_SUPPORT_SOURCES = {
    "tests/test_session_token_helpers.py::create_split_ranges": (
        "tests/get_latest_session_token/_fixtures.py::create_split_ranges"
    ),
}

RETIRED_QUERY_SOURCES = {
    f"tests/{filename}::{class_name}.{method}": (
        f"tests/query_items/{surface}/legacy/{filename}::{class_name}.{method}_rust"
    )
    for surface, filename, class_name, methods in (
        ("sync", "test_query.py", "TestQuery", (
            "test_query_items_with_parameters_none",
            "test_query_pagination_with_max_item_count",
            "test_offset_limit",
            "test_distinct",
            "test_partition_scoped_count_is_index_only",
            "test_value_max_query_results",
            "test_populate_query_metrics",
            "test_populate_index_metrics",
            "test_populate_query_advice",
            "test_paging_with_continuation_token",
            "test_cross_partition_query_with_continuation_token",
            "test_continuation_token_size_limit_query",
        )),
        ("aio", "test_query_async.py", "TestQueryAsync", (
            "test_offset_limit_async",
            "test_distinct_async",
            "test_partition_scoped_count_is_index_only_async",
            "test_value_max_query_results_async",
            "test_populate_query_metrics_async",
            "test_populate_index_metrics_async",
            "test_populate_query_advice_async",
            "test_paging_with_continuation_token_async",
            "test_cross_partition_query_with_continuation_token_async",
            "test_continuation_token_size_limit_query_async",
        )),
        ("sync", "test_none_options.py", "TestNoneOptions", (
            "test_container_query_items_none_options_partition",
        )),
        ("aio", "test_none_options_async.py", "TestNoneOptionsAsync", (
            "test_container_query_items_none_options_partition_async",
        )),
        ("sync", "test_orderby.py", "TestCrossPartitionTopOrderBy", (
            "test_orderby_top_query",
        )),
        ("sync", "test_query_feed_range.py", "TestQueryFeedRange", (
            "test_query_value_sum_across_full_feed_range_still_sums",
            "test_query_value_min_across_full_feed_range_returns_scalar",
            "test_query_with_avg_aggregate_single_partition_feed_range_succeeds",
        )),
        ("aio", "test_query_feed_range_async.py", "TestQueryFeedRangeAsync", (
            "test_query_value_sum_across_full_feed_range_still_sums_async",
            "test_query_value_min_across_full_feed_range_returns_scalar_async",
            "test_query_with_avg_aggregate_single_partition_feed_range_succeeds_async",
        )),
        ("sync", "test_query_feed_range_multipartition.py", "TestFeedRangeMultiPartition", (
            "test_prefix_partition_key_query_pagination_resume",
        )),
        ("aio", "test_query_feed_range_multipartition_async.py", "TestFeedRangeMultiPartitionAsync", (
            "test_prefix_partition_key_query_pagination_resume_async",
        )),
    )
    for method in methods
}

RETIRED_TEST_SOURCES = {
    **RETIRED_THROUGHPUT_SOURCES,
    **RETIRED_SESSION_TOKEN_SOURCES,
    **RETIRED_QUERY_SOURCES,
}
