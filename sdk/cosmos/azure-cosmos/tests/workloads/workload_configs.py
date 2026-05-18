# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# All configuration is driven by environment variables with sensible defaults.
import logging
import os
from perf_config import _safe_int

from azure.identity import DefaultAzureCredential


def _parse_region_list(env_var_name):
    value = os.environ.get(env_var_name, "")
    return (
        [region.strip() for region in value.split(",") if region.strip()]
        if value
        else []
    )


PREFERRED_LOCATIONS = _parse_region_list("COSMOS_PREFERRED_LOCATIONS")
CLIENT_EXCLUDED_LOCATIONS = _parse_region_list("COSMOS_CLIENT_EXCLUDED_LOCATIONS")
REQUEST_EXCLUDED_LOCATIONS = _parse_region_list("COSMOS_REQUEST_EXCLUDED_LOCATIONS")
COSMOS_PROXY_URI = os.environ.get("COSMOS_PROXY_URI", "0.0.0.0")
COSMOS_URI = os.environ.get("COSMOS_URI", "")
COSMOS_KEY = os.environ.get("COSMOS_KEY", "")
COSMOS_CREDENTIAL = COSMOS_KEY if COSMOS_KEY else DefaultAzureCredential()
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER", "scale_cont")
COSMOS_DATABASE = os.environ.get("COSMOS_DATABASE", "scale_db")
USER_AGENT_PREFIX = os.environ.get("COSMOS_USER_AGENT_PREFIX", "")
LOG_LEVEL = getattr(logging, os.environ.get("COSMOS_LOG_LEVEL", "DEBUG"), logging.DEBUG)
APP_INSIGHTS_CONNECTION_STRING = os.environ.get("APP_INSIGHTS_CONNECTION_STRING", "")
CIRCUIT_BREAKER_ENABLED = (
    os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "false").lower() == "true"
)
USE_MULTIPLE_WRITABLE_LOCATIONS = (
    os.environ.get("COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS", "false").lower() == "true"
)
CONCURRENT_REQUESTS = _safe_int(os.environ.get("COSMOS_CONCURRENT_REQUESTS", "100"), 100)
CONCURRENT_QUERIES = _safe_int(os.environ.get("COSMOS_CONCURRENT_QUERIES", "2"), 2)
WORKLOAD_NUM_CLIENTS = _safe_int(os.environ.get("WORKLOAD_NUM_CLIENTS", "1"), 1)
PARTITION_KEY = os.environ.get("COSMOS_PARTITION_KEY", "id")
NUMBER_OF_LOGICAL_PARTITIONS = int(
    os.environ.get("COSMOS_NUMBER_OF_LOGICAL_PARTITIONS", "10000")
)
THROUGHPUT = _safe_int(os.environ.get("COSMOS_THROUGHPUT", "100000"), 100000)  # For DR drills, set COSMOS_THROUGHPUT=1000000

# Workload behavior
_VALID_OPERATIONS = {"read", "write", "query"}
WORKLOAD_OPERATIONS = frozenset(
    op.strip().lower()
    for op in os.environ.get("WORKLOAD_OPERATIONS", "read,write,query").split(",")
    if op.strip()
)
_unknown_ops = WORKLOAD_OPERATIONS - _VALID_OPERATIONS
if _unknown_ops:
    raise ValueError(
        f"Unknown WORKLOAD_OPERATIONS: {_unknown_ops}. Valid: {_VALID_OPERATIONS}"
    )
WORKLOAD_USE_PROXY = os.environ.get("WORKLOAD_USE_PROXY", "false").lower() == "true"
WORKLOAD_USE_SYNC = os.environ.get("WORKLOAD_USE_SYNC", "false").lower() == "true"

# When true, the client is created without a context manager (no automatic close).
# Simulates applications that don't properly close the Cosmos client.
WORKLOAD_SKIP_CLOSE = os.environ.get("WORKLOAD_SKIP_CLOSE", "false").lower() == "true"
