# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Approved original-test retirements and their retained Rust regression cases.

Source comments remain historical provenance. Only these explicit retirements
may resolve to retained tests instead of a live original.
"""

RETIRED_THROUGHPUT_SOURCES = {
    "tests/test_auto_scale.py::TestAutoScale.test_autoscale_create_container": (
        "tests/get_container_throughput/sync/legacy/test_auto_scale.py"
        "::TestAutoScale.test_autoscale_create_container"
    ),
    "tests/test_auto_scale.py::TestAutoScale.test_autoscale_create_database": (
        "tests/get_database_throughput/sync/legacy/test_auto_scale.py"
        "::TestAutoScale.test_autoscale_create_database"
    ),
    "tests/test_auto_scale.py::TestAutoScale.test_autoscale_replace_throughput": (
        "tests/replace_database_throughput/sync/legacy/test_auto_scale.py"
        "::TestAutoScale.test_autoscale_replace_throughput"
    ),
    "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_container_async": (
        "tests/get_container_throughput/aio/legacy/test_auto_scale_async.py"
        "::TestAutoScaleAsync.test_autoscale_create_container_async"
    ),
    "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_database_async": (
        "tests/get_database_throughput/aio/legacy/test_auto_scale.py"
        "::TestAutoScaleAsync.test_autoscale_create_database_async"
    ),
    "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_replace_throughput_async": (
        "tests/replace_database_throughput/aio/legacy/test_auto_scale.py"
        "::TestAutoScaleAsync.test_replace_throughput_async"
    ),
    "tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_offer_methods": (
        "tests/get_container_throughput/sync/legacy/test_backwards_compatibility.py"
        "::TestBackwardsCompatibility.test_offer_methods"
    ),
    (
        "tests/test_container_properties_cache.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate"
    ): (
        "tests/get_container_throughput/sync/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCache.test_offer_throughput_container_recreate"
    ),
    (
        "tests/test_container_properties_cache.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate_sub_partition"
    ): (
        "tests/get_container_throughput/sync/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCache.test_offer_throughput_container_recreate_sub_partition"
    ),
    (
        "tests/test_container_properties_cache_async.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCacheAsync.test_offer_throughput_container_recreate_async"
    ),
    (
        "tests/test_container_properties_cache_async.py::TestContainerPropertiesCache"
        ".test_offer_throughput_container_recreate_sub_partition_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_container_properties_cache.py"
        "::TestContainerPropertiesCacheAsync.test_offer_throughput_container_recreate_sub_partition_async"
    ),
    "tests/test_cosmos_responses.py::TestCosmosResponses.test_container_replace_throughput": (
        "tests/get_database_throughput/sync/legacy/test_cosmos_responses.py"
        "::TestCosmosResponses.test_container_replace_throughput"
    ),
    "tests/test_cosmos_responses.py::TestCosmosResponses.test_database_replace_throughput": (
        "tests/get_database_throughput/sync/legacy/test_cosmos_responses.py"
        "::TestCosmosResponses.test_database_replace_throughput"
    ),
    "tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_container_replace_throughput_async": (
        "tests/get_database_throughput/aio/legacy/test_cosmos_responses.py"
        "::TestCosmosResponsesAsync.test_container_replace_throughput_async"
    ),
    "tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_database_replace_throughput_async": (
        "tests/get_database_throughput/aio/legacy/test_cosmos_responses.py"
        "::TestCosmosResponsesAsync.test_database_replace_throughput_async"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_offer_read_and_query": (
        "tests/get_container_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_offer_read_and_query"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_offer_replace": (
        "tests/get_container_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_offer_replace"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_replace_throughput_offer_with_int": (
        "tests/replace_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_replace_throughput_offer_with_int"
    ),
    "tests/test_crud_container.py::TestCRUDContainerOperations.test_replace_throughput_offer_with_object": (
        "tests/replace_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_replace_throughput_offer_with_object"
    ),
    (
        "tests/test_crud_container.py::TestCRUDContainerOperations"
        ".test_negative_replace_throughput_with_all_configs_set"
    ): (
        "tests/replace_throughput/sync/legacy/test_crud_container.py"
        "::TestCRUDContainerOperations.test_negative_replace_throughput_with_all_configs_set"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_offer_read_and_query_async": (
        "tests/get_container_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_offer_read_and_query_async"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_offer_replace_async": (
        "tests/get_container_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_offer_replace_async"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_int": (
        "tests/replace_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_int"
    ),
    "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_object": (
        "tests/replace_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_object"
    ),
    (
        "tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync"
        ".test_negative_replace_throughput_with_all_configs_set"
    ): (
        "tests/replace_throughput/aio/legacy/test_crud_container_async.py"
        "::TestCRUDContainerOperationsAsync.test_negative_replace_throughput_with_all_configs_set"
    ),
    "tests/test_crud_database.py::TestCRUDDatabaseOperations.test_database_level_offer_throughput": (
        "tests/get_database_throughput/sync/legacy/test_crud_database.py"
        "::TestCRUDDatabaseOperations.test_database_level_offer_throughput"
    ),
    "tests/test_crud_database_async.py::TestCRUDDatabaseOperationsAsync.test_database_level_offer_throughput_async": (
        "tests/get_database_throughput/aio/legacy/test_crud_database.py"
        "::TestCRUDDatabaseOperationsAsync.test_database_level_offer_throughput_async"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled"
        ".test_database_level_offer_throughput"
    ): (
        "tests/get_database_throughput/sync/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_database_level_offer_throughput"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled_async.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_database_level_offer_throughput_async"
    ): (
        "tests/get_database_throughput/aio/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_database_level_offer_throughput_async"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled"
        ".test_offer_read_and_query"
    ): (
        "tests/get_container_throughput/sync/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_offer_read_and_query"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled"
        ".test_offer_replace"
    ): (
        "tests/get_container_throughput/sync/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_offer_replace"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled_async.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_read_and_query_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_read_and_query_async"
    ),
    (
        "tests/test_crud_response_payload_on_write_disabled_async.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_replace_async"
    ): (
        "tests/get_container_throughput/aio/legacy/test_crud_response_payload_on_write_disabled.py"
        "::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_replace_async"
    ),
}
