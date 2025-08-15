# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Class for defining internal constants in the Azure Cosmos database service.
"""


from typing import Dict
from typing_extensions import Literal


class _Constants:
    """Constants used in the azure-cosmos package"""

    UserConsistencyPolicy: Literal["userConsistencyPolicy"] = "userConsistencyPolicy"
    DefaultConsistencyLevel: Literal["defaultConsistencyLevel"] = "defaultConsistencyLevel"

    # GlobalDB related constants
    WritableLocations: Literal["writableLocations"] = "writableLocations"
    ReadableLocations: Literal["readableLocations"] = "readableLocations"
    Name: Literal["name"] = "name"
    DatabaseAccountEndpoint: Literal["databaseAccountEndpoint"] = "databaseAccountEndpoint"
    DefaultEndpointsRefreshTime: int = 5 * 60 * 1000 # milliseconds
    UnavailableEndpointDBATimeouts: int = 1 # seconds

    # ServiceDocument Resource
    EnableMultipleWritableLocations: Literal[
        "enableMultipleWriteLocations"
    ] = "enableMultipleWriteLocations"

    # Environment variables
    NON_STREAMING_ORDER_BY_DISABLED_CONFIG: str = "AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY"
    NON_STREAMING_ORDER_BY_DISABLED_CONFIG_DEFAULT: str = "False"
    HS_MAX_ITEMS_CONFIG: str = "AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS"
    HS_MAX_ITEMS_CONFIG_DEFAULT: int = 1000
    MAX_ITEM_BUFFER_VS_CONFIG: str = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
    MAX_ITEM_BUFFER_VS_CONFIG_DEFAULT: int = 50000
    CIRCUIT_BREAKER_ENABLED_CONFIG: str =  "AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"
    CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT: str = "False"
    AAD_SCOPE_OVERRIDE: str = "AZURE_COSMOS_AAD_SCOPE_OVERRIDE"
    # Only applicable when circuit breaker is enabled -------------------------
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ: str = (
        "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ"
    )
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ_DEFAULT: int = 10
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE: str = (
        "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE"
    )
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE_DEFAULT: int = 5
    FAILURE_PERCENTAGE_TOLERATED = "AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"
    FAILURE_PERCENTAGE_TOLERATED_DEFAULT: int = 90
    # -------------------------------------------------------------------------

    # Error code translations
    ERROR_TRANSLATIONS: Dict[int, str] = {
        400: "BAD_REQUEST - Request being sent is invalid.",
        401: "UNAUTHORIZED - The input authorization token can't serve the request.",
        403: "FORBIDDEN",
        404: "NOT_FOUND - Entity with the specified id does not exist in the system.",
        405: "METHOD_NOT_ALLOWED",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT - Entity with the specified id already exists in the system.",
        410: "GONE",
        412: (
            "PRECONDITION_FAILED - Operation cannot be performed because one of the "
            "specified precondition is not met"
        ),
        413: "REQUEST_ENTITY_TOO_LARGE - Document size exceeds limit.",
        424: "FAILED_DEPENDENCY - There is a failure in the transactional batch.",
        429: "TOO_MANY_REQUESTS",
        449: (
            "RETRY_WITH - Conflicting request to resource has been attempted. "
            "Retry to avoid conflicts."
        )
    }

    class InternalOptions:
        """Internal option names used in request processing
        
        These constants represent the internal option keys used in the azure-cosmos package
        for request processing and headers. They are used internally by the SDK and should
        not be used directly in public APIs.
        """

        # Internal option keys used in build_options and GetHeaders functions
        ACCESS_CONDITION: Literal["accessCondition"] = "accessCondition"
        """Access condition option for conditional operations (IfMatch, IfNoneMatch)."""

        AUTO_UPGRADE_POLICY: Literal["autoUpgradePolicy"] = "autoUpgradePolicy"
        """Auto-upgrade policy for autoscale settings."""

        CONSISTENCY_LEVEL: Literal["consistencyLevel"] = "consistencyLevel"
        """Consistency level override for the request."""

        CONTAINER_RID: Literal["containerRID"] = "containerRID"
        """Container resource ID for request routing."""

        CONTENT_TYPE: Literal["contentType"] = "contentType"
        """Content type for the request."""

        CONTINUATION: Literal["continuation"] = "continuation"
        """Continuation token for paginated queries."""

        CORRELATED_ACTIVITY_ID: Literal["correlatedActivityId"] = "correlatedActivityId"
        """Correlated activity ID for tracing and diagnostics."""

        DISABLE_RU_PER_MINUTE_USAGE: Literal[
            "disableRUPerMinuteUsage"
        ] = "disableRUPerMinuteUsage"
        """Whether to disable RU per minute usage."""

        ENABLE_CROSS_PARTITION_QUERY: Literal[
            "enableCrossPartitionQuery"
        ] = "enableCrossPartitionQuery"
        """Whether to enable cross-partition queries."""

        ENABLE_SCAN_IN_QUERY: Literal["enableScanInQuery"] = "enableScanInQuery"
        """Whether to enable scan in query operations."""

        ENABLE_SCRIPT_LOGGING: Literal["enableScriptLogging"] = "enableScriptLogging"
        """Whether to enable script logging for stored procedures."""

        EXCLUDED_LOCATIONS: Literal["excludedLocations"] = "excludedLocations"
        """List of locations to exclude for this request."""

        INDEXING_DIRECTIVE: Literal["indexingDirective"] = "indexingDirective"
        """Indexing directive for the operation."""

        INITIAL_HEADERS: Literal["initialHeaders"] = "initialHeaders"
        """Initial headers to include in the request."""

        IS_QUERY_PLAN_REQUEST: Literal["isQueryPlanRequest"] = "isQueryPlanRequest"
        """Whether this is a query plan request."""

        MAX_INTEGRATED_CACHE_STALENESS: Literal[
            "maxIntegratedCacheStaleness"
        ] = "maxIntegratedCacheStaleness"
        """Maximum integrated cache staleness in milliseconds."""

        MAX_ITEM_COUNT: Literal["maxItemCount"] = "maxItemCount"
        """Maximum number of items to return in the response."""

        OFFER_ENABLE_RU_PER_MINUTE_THROUGHPUT: Literal[
            "offerEnableRUPerMinuteThroughput"
        ] = "offerEnableRUPerMinuteThroughput"
        """Whether to enable RU per minute throughput for the offer."""

        OFFER_THROUGHPUT: Literal["offerThroughput"] = "offerThroughput"
        """Throughput value for the offer."""

        OFFER_TYPE: Literal["offerType"] = "offerType"
        """Type of the offer (S1, S2, S3, etc.)."""

        PARTITION_KEY: Literal["partitionKey"] = "partitionKey"
        """Partition key value for the request."""

        POPULATE_INDEX_METRICS: Literal["populateIndexMetrics"] = "populateIndexMetrics"
        """Whether to populate index metrics in the response."""

        POPULATE_PARTITION_KEY_RANGE_STATISTICS: Literal[
            "populatePartitionKeyRangeStatistics"
        ] = "populatePartitionKeyRangeStatistics"
        """Whether to populate partition key range statistics."""

        POPULATE_QUERY_METRICS: Literal["populateQueryMetrics"] = "populateQueryMetrics"
        """Whether to populate query metrics in the response."""

        POPULATE_QUOTA_INFO: Literal["populateQuotaInfo"] = "populateQuotaInfo"
        """Whether to populate quota information in the response."""

        POST_TRIGGER_INCLUDE: Literal["postTriggerInclude"] = "postTriggerInclude"
        """Post-trigger scripts to include in the operation."""

        PRE_TRIGGER_INCLUDE: Literal["preTriggerInclude"] = "preTriggerInclude"
        """Pre-trigger scripts to include in the operation."""

        PRIORITY_LEVEL: Literal["priorityLevel"] = "priorityLevel"
        """Priority level for the request (High, Low)."""

        QUERY_VERSION: Literal["queryVersion"] = "queryVersion"
        """Query version for the request."""

        RESOURCE_TOKEN_EXPIRY_SECONDS: Literal[
            "resourceTokenExpirySeconds"
        ] = "resourceTokenExpirySeconds"
        """Resource token expiry time in seconds."""

        RESPONSE_CONTINUATION_TOKEN_LIMIT_IN_KB: Literal[
            "responseContinuationTokenLimitInKb"
        ] = "responseContinuationTokenLimitInKb"
        """Continuation token size limit in KB."""

        RESPONSE_PAYLOAD_ON_WRITE_DISABLED: Literal[
            "responsePayloadOnWriteDisabled"
        ] = "responsePayloadOnWriteDisabled"
        """Whether to disable response payload on write operations."""

        RETRY_WRITE: Literal["retry_write"] = "retry_write"
        """Whether to retry write operations if they fail. Used either at client level or request level."""

        SESSION_TOKEN: Literal["sessionToken"] = "sessionToken"
        """Session token for session consistency."""

        SUPPORTED_QUERY_FEATURES: Literal["supportedQueryFeatures"] = "supportedQueryFeatures"
        """Supported query features for the request."""

        THROUGHPUT_BUCKET: Literal["throughputBucket"] = "throughputBucket"
        """Throughput bucket for the request."""

        # Additional internal options
        ENABLE_DIAGNOSTICS_LOGGING: Literal["enableDiagnosticsLogging"] = "enableDiagnosticsLogging"
        """Whether to enable diagnostics logging."""

        LOGGER: Literal["logger"] = "logger"
        """Logger instance for diagnostics."""

        PROXIES: Literal["proxies"] = "proxies"
        """Proxy configuration for requests."""

        USER_AGENT_SUFFIX: Literal["userAgentSuffix"] = "userAgentSuffix"
        """Additional user agent suffix for requests."""

        TRANSPORT: Literal["transport"] = "transport"
        """Custom transport for requests."""

        RESPONSE_HOOK: Literal["responseHook"] = "responseHook"
        """Response hook callback function."""

        RAW_RESPONSE_HOOK: Literal["rawResponseHook"] = "rawResponseHook"
        """Raw response hook callback function."""

        FEED_RANGE: Literal["feedRange"] = "feedRange"
        """Feed range for query operations."""

        PREFIX_PARTITION_KEY_OBJECT: Literal["prefixPartitionKeyObject"] = "prefixPartitionKeyObject"
        """Prefix partition key object for queries."""

        PREFIX_PARTITION_KEY_VALUE: Literal["prefixPartitionKeyValue"] = "prefixPartitionKeyValue"
        """Prefix partition key value for queries."""

    class Kwargs:
        """Public-facing keyword argument names used in the azure-cosmos package

        These constants should be used instead of hardcoded strings for kwargs in public APIs
        to improve maintainability, reduce errors, and provide better IDE support.

        Best practices:
        - Always use these constants instead of hardcoded strings in public APIs
        - Follow the naming convention: UPPER_SNAKE_CASE for constant names
        - Use Literal types for type safety
        - Document the purpose of each constant
        """

        # Public kwarg names used in public APIs
        ACCESS_CONDITION: Literal["access_condition"] = "access_condition"
        """Access condition kwarg for conditional operations (IfMatch, IfNoneMatch)."""

        AUTO_UPGRADE_POLICY: Literal["auto_upgrade_policy"] = "auto_upgrade_policy"
        """Auto-upgrade policy kwarg for autoscale settings."""

        CONSISTENCY_LEVEL: Literal["consistency_level"] = "consistency_level"
        """Consistency level override kwarg for the request."""

        CONTAINER_RID: Literal["container_rid"] = "container_rid"
        """Container resource ID kwarg for request routing."""

        CONTENT_TYPE: Literal["content_type"] = "content_type"
        """Content type kwarg for the request."""

        CONTINUATION: Literal["continuation"] = "continuation"
        """Continuation token kwarg for paginated queries."""

        CORRELATED_ACTIVITY_ID: Literal["correlated_activity_id"] = "correlated_activity_id"
        """Correlated activity ID kwarg for tracing and diagnostics."""

        DISABLE_RU_PER_MINUTE_USAGE: Literal[
            "disable_ru_per_minute_usage"
        ] = "disable_ru_per_minute_usage"
        """Whether to disable RU per minute usage kwarg."""

        ENABLE_CROSS_PARTITION_QUERY: Literal[
            "enable_cross_partition_query"
        ] = "enable_cross_partition_query"
        """Whether to enable cross-partition queries kwarg."""

        ENABLE_SCAN_IN_QUERY: Literal["enable_scan_in_query"] = "enable_scan_in_query"
        """Whether to enable scan in query operations kwarg."""

        ENABLE_SCRIPT_LOGGING: Literal["enable_script_logging"] = "enable_script_logging"
        """Whether to enable script logging for stored procedures kwarg."""

        EXCLUDED_LOCATIONS: Literal["excluded_locations"] = "excluded_locations"
        """List of locations to exclude for this request kwarg."""

        INDEXING_DIRECTIVE: Literal["indexing_directive"] = "indexing_directive"
        """Indexing directive kwarg for the operation."""

        INITIAL_HEADERS: Literal["initial_headers"] = "initial_headers"
        """Initial headers kwarg to include in the request."""

        IS_QUERY_PLAN_REQUEST: Literal["is_query_plan_request"] = "is_query_plan_request"
        """Whether this is a query plan request kwarg."""

        MAX_INTEGRATED_CACHE_STALENESS: Literal[
            "max_integrated_cache_staleness"
        ] = "max_integrated_cache_staleness"
        """Maximum integrated cache staleness kwarg in milliseconds."""

        MAX_ITEM_COUNT: Literal["max_item_count"] = "max_item_count"
        """Maximum number of items to return in the response kwarg."""

        OFFER_ENABLE_RU_PER_MINUTE_THROUGHPUT: Literal[
            "offer_enable_ru_per_minute_throughput"
        ] = "offer_enable_ru_per_minute_throughput"
        """Whether to enable RU per minute throughput for the offer kwarg."""

        OFFER_THROUGHPUT: Literal["offer_throughput"] = "offer_throughput"
        """Throughput value kwarg for the offer."""

        OFFER_TYPE: Literal["offer_type"] = "offer_type"
        """Type of the offer kwarg (S1, S2, S3, etc.)."""

        PARTITION_KEY: Literal["partition_key"] = "partition_key"
        """Partition key value kwarg for the request."""

        POPULATE_INDEX_METRICS: Literal["populate_index_metrics"] = "populate_index_metrics"
        """Whether to populate index metrics in the response kwarg."""

        POPULATE_PARTITION_KEY_RANGE_STATISTICS: Literal[
            "populate_partition_key_range_statistics"
        ] = "populate_partition_key_range_statistics"
        """Whether to populate partition key range statistics kwarg."""

        POPULATE_QUERY_METRICS: Literal["populate_query_metrics"] = "populate_query_metrics"
        """Whether to populate query metrics in the response kwarg."""

        POPULATE_QUOTA_INFO: Literal["populate_quota_info"] = "populate_quota_info"
        """Whether to populate quota information in the response kwarg."""

        POST_TRIGGER_INCLUDE: Literal["post_trigger_include"] = "post_trigger_include"
        """Post-trigger scripts kwarg to include in the operation."""

        PRE_TRIGGER_INCLUDE: Literal["pre_trigger_include"] = "pre_trigger_include"
        """Pre-trigger scripts kwarg to include in the operation."""

        PRIORITY: Literal["priority"] = "priority"
        """Priority level kwarg for the request (High, Low)."""

        QUERY_VERSION: Literal["query_version"] = "query_version"
        """Query version kwarg for the request."""

        RESOURCE_TOKEN_EXPIRY_SECONDS: Literal[
            "resource_token_expiry_seconds"
        ] = "resource_token_expiry_seconds"
        """Resource token expiry time kwarg in seconds."""

        RESPONSE_CONTINUATION_TOKEN_LIMIT_IN_KB: Literal[
            "response_continuation_token_limit_in_kb"
        ] = "response_continuation_token_limit_in_kb"
        """Continuation token size limit kwarg in KB."""

        NO_RESPONSE: Literal["no_response"] = "no_response"
        """Whether to disable response payload on write operations kwarg."""

        RETRY_WRITE: Literal["retry_write"] = "retry_write"
        """Whether to retry write operations if they fail kwarg. Used either at client level or request level."""

        SESSION_TOKEN: Literal["session_token"] = "session_token"
        """Session token kwarg for session consistency."""

        SUPPORTED_QUERY_FEATURES: Literal["supported_query_features"] = "supported_query_features"
        """Supported query features kwarg for the request."""

        THROUGHPUT_BUCKET: Literal["throughput_bucket"] = "throughput_bucket"
        """Throughput bucket kwarg for the request."""

        # Additional public kwargs
        ENABLE_DIAGNOSTICS_LOGGING: Literal["enable_diagnostics_logging"] = "enable_diagnostics_logging"
        """Whether to enable diagnostics logging kwarg."""

        LOGGER: Literal["logger"] = "logger"
        """Logger instance kwarg for diagnostics."""

        PROXIES: Literal["proxies"] = "proxies"
        """Proxy configuration kwarg for requests."""

        USER_AGENT_SUFFIX: Literal["user_agent_suffix"] = "user_agent_suffix"
        """Additional user agent suffix kwarg for requests."""

        TRANSPORT: Literal["transport"] = "transport"
        """Custom transport kwarg for requests."""

        RESPONSE_HOOK: Literal["response_hook"] = "response_hook"
        """Response hook callback function kwarg."""

        RAW_RESPONSE_HOOK: Literal["raw_response_hook"] = "raw_response_hook"
        """Raw response hook callback function kwarg."""

        FEED_RANGE: Literal["feed_range"] = "feed_range"
        """Feed range kwarg for query operations."""

        PREFIX_PARTITION_KEY_OBJECT: Literal["prefix_partition_key_object"] = "prefix_partition_key_object"
        """Prefix partition key object kwarg for queries."""

        PREFIX_PARTITION_KEY_VALUE: Literal["prefix_partition_key_value"] = "prefix_partition_key_value"
        """Prefix partition key value kwarg for queries."""
