# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from types import SimpleNamespace
import unittest.mock

from azure.cosmos._global_partition_endpoint_manager_per_partition_automatic_failover import (
    PartitionLevelFailoverInfo,
)
from azure.cosmos._request_object import RequestObject
from azure.cosmos._session_retry_policy import _SessionRetryPolicy
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import ResourceType


def _request_object():
    return RequestObject(ResourceType.Document, _OperationType.Create, {})


def _context(endpoint: str):
    context = unittest.mock.Mock()
    context.primary_endpoint = endpoint
    return context


def test_ppaf_try_move_to_next_location_skips_excluded_region_when_other_region_exists():
    failover_info = PartitionLevelFailoverInfo()
    failover_info.current_region = "West US 3"
    failover_info.unavailable_regional_endpoints["West US 3"] = "https://westus3.documents.azure.com"

    available_regions = {
        "West US 3": _context("https://westus3.documents.azure.com"),
        "East US 2": _context("https://eastus2.documents.azure.com"),
        "Central US": _context("https://centralus.documents.azure.com"),
    }

    request = _request_object()
    moved = failover_info.try_move_to_next_location(
        available_regions,
        "West US 3",
        request,
        excluded_locations=["East US 2"],
    )

    assert moved is True
    assert failover_info.current_region == "Central US"
    assert request.location_endpoint_to_route == "https://centralus.documents.azure.com"


def test_ppaf_try_move_to_next_location_falls_back_to_excluded_region_when_only_option():
    failover_info = PartitionLevelFailoverInfo()
    failover_info.current_region = "West US 3"
    failover_info.unavailable_regional_endpoints["West US 3"] = "https://westus3.documents.azure.com"

    available_regions = {
        "West US 3": _context("https://westus3.documents.azure.com"),
        "East US 2": _context("https://eastus2.documents.azure.com"),
    }

    request = _request_object()
    moved = failover_info.try_move_to_next_location(
        available_regions,
        "West US 3",
        request,
        excluded_locations=["East US 2"],
    )

    assert moved is True
    assert failover_info.current_region == "East US 2"
    assert request.location_endpoint_to_route == "https://eastus2.documents.azure.com"


def test_ppaf_try_move_to_next_location_reuses_excluded_current_region_as_last_resort():
    failover_info = PartitionLevelFailoverInfo()
    failover_info.current_region = "East US 2"
    failover_info.unavailable_regional_endpoints["West US 3"] = "https://westus3.documents.azure.com"

    available_regions = {
        "West US 3": _context("https://westus3.documents.azure.com"),
        "East US 2": _context("https://eastus2.documents.azure.com"),
    }

    request = _request_object()
    moved = failover_info.try_move_to_next_location(
        available_regions,
        "West US 3",
        request,
        excluded_locations=["East US 2"],
    )

    assert moved is True
    assert failover_info.current_region == "East US 2"
    assert request.location_endpoint_to_route == "https://eastus2.documents.azure.com"


def test_session_retry_policy_ppaf_path_does_not_pin_excluded_current_region():
    request = _request_object()

    location_cache = unittest.mock.Mock()
    location_cache.get_location_from_endpoint.side_effect = lambda endpoint: {
        "None": "West US 3",
        "https://eastus2.documents.azure.com": "East US 2",
    }.get(endpoint)
    location_cache._get_configured_excluded_locations.return_value = ["East US 2"]
    location_cache.account_read_regional_routing_contexts_by_location = {
        "East US 2": _context("https://eastus2.documents.azure.com"),
    }

    pk_failover_info = SimpleNamespace(
        unavailable_regional_endpoints={"West US 3": "https://westus3.documents.azure.com"},
        current_region="East US 2",
    )

    global_endpoint_manager = unittest.mock.Mock()
    global_endpoint_manager.can_use_multiple_write_locations.return_value = False
    global_endpoint_manager.is_per_partition_automatic_failover_enabled.return_value = True
    global_endpoint_manager.partition_range_to_failover_info = {"pk": pk_failover_info}
    global_endpoint_manager.location_cache = location_cache
    global_endpoint_manager.resolve_service_endpoint_for_partition.side_effect = [
        "https://westus3.documents.azure.com",
        "https://eastus2.documents.azure.com",
    ]

    retry_policy = _SessionRetryPolicy(True, global_endpoint_manager, "pk", request)
    should_retry = retry_policy.ShouldRetry(Exception("retry"))

    assert should_retry is True
    assert request.location_endpoint_to_route == "https://eastus2.documents.azure.com"

