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


from typing import Dict, Final


class _Constants:
    """Constants used in the azure-cosmos package"""

    UserConsistencyPolicy: Final[str] = "userConsistencyPolicy"
    DefaultConsistencyLevel: Final[str] = "defaultConsistencyLevel"

    # GlobalDB related constants
    WritableLocations: Final[str] = "writableLocations"
    ReadableLocations: Final[str] = "readableLocations"
    Name: Final[str] = "name"
    DatabaseAccountEndpoint: Final[str] = "databaseAccountEndpoint"
    DefaultEndpointsRefreshTime: int = 5 * 60 * 1000 # milliseconds
    UnavailableEndpointDBATimeouts: int = 1 # seconds

    # ServiceDocument Resource
    EnableMultipleWritableLocations: Final[str] = "enableMultipleWriteLocations"

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
        ACCESS_CONDITION: Final[str] = "accessCondition"
        """Access condition option for conditional operations (IfMatch, IfNoneMatch)."""

        AUTO_UPGRADE_POLICY: Final[str] = "autoUpgradePolicy"
        """Auto-upgrade policy for autoscale settings."""

        CONSISTENCY_LEVEL: Final[str] = "consistencyLevel"
        """Consistency level override for the request."""

        CONTAINER_RID: Final[str] = "containerRID"
        """Container resource ID for request routing."""

        CONTENT_TYPE: Final[str] = "contentType"
        """Content type for the request."""

        CONTINUATION: Final[str] = "continuation"
        """Continuation token for paginated queries."""

        CORRELATED_ACTIVITY_ID: Final[str] = "correlatedActivityId"
        """Correlated activity ID for tracing and diagnostics."""

        DISABLE_RU_PER_MINUTE_USAGE: Final[str] = "disableRUPerMinuteUsage"
        """Whether to disable RU per minute usage."""

        ENABLE_CROSS_PARTITION_QUERY: Final[str] = "enableCrossPartitionQuery"
        """Whether to enable cross-partition queries."""

        ENABLE_SCAN_IN_QUERY: Final[str] = "enableScanInQuery"
        """Whether to enable scan in query operations."""

        ENABLE_SCRIPT_LOGGING: Final[str] = "enableScriptLogging"
        """Whether to enable script logging for stored procedures."""

        EXCLUDED_LOCATIONS: Final[str] = "excludedLocations"
        """List of locations to exclude for this request."""

        INDEXING_DIRECTIVE: Final[str] = "indexingDirective"
        """Indexing directive for the operation."""

        INITIAL_HEADERS: Final[str] = "initialHeaders"
        """Initial headers to include in the request."""

        IS_QUERY_PLAN_REQUEST: Final[str] = "isQueryPlanRequest"
        """Whether this is a query plan request."""

        MAX_INTEGRATED_CACHE_STALENESS: Final[str] = "maxIntegratedCacheStaleness"
        """Maximum integrated cache staleness in milliseconds."""

        MAX_ITEM_COUNT: Final[str] = "maxItemCount"
        """Maximum number of items to return in the response."""

        OFFER_ENABLE_RU_PER_MINUTE_THROUGHPUT: Final[str] = "offerEnableRUPerMinuteThroughput"
        """Whether to enable RU per minute throughput for the offer."""

        OFFER_THROUGHPUT: Final[str] = "offerThroughput"
        """Throughput value for the offer."""

        OFFER_TYPE: Final[str] = "offerType"
        """Type of the offer (S1, S2, S3, etc.)."""

        PARTITION_KEY: Final[str] = "partitionKey"
        """Partition key value for the request."""

        POPULATE_INDEX_METRICS: Final[str] = "populateIndexMetrics"
        """Whether to populate index metrics in the response."""

        POPULATE_PARTITION_KEY_RANGE_STATISTICS: Final[str] = "populatePartitionKeyRangeStatistics"
        """Whether to populate partition key range statistics."""

        POPULATE_QUERY_METRICS: Final[str] = "populateQueryMetrics"
        """Whether to populate query metrics in the response."""

        POPULATE_QUOTA_INFO: Final[str] = "populateQuotaInfo"
        """Whether to populate quota information in the response."""

        POST_TRIGGER_INCLUDE: Final[str] = "postTriggerInclude"
        """Post-trigger scripts to include in the operation."""

        PRE_TRIGGER_INCLUDE: Final[str] = "preTriggerInclude"
        """Pre-trigger scripts to include in the operation."""

        PRIORITY_LEVEL: Final[str] = "priorityLevel"
        """Priority level for the request (High, Low)."""

        QUERY_VERSION: Final[str] = "queryVersion"
        """Query version for the request."""

        RESOURCE_TOKEN_EXPIRY_SECONDS: Final[str] = "resourceTokenExpirySeconds"
        """Resource token expiry time in seconds."""

        RESPONSE_CONTINUATION_TOKEN_LIMIT_IN_KB: Final[str] = "responseContinuationTokenLimitInKb"
        """Continuation token size limit in KB."""

        RESPONSE_PAYLOAD_ON_WRITE_DISABLED: Final[str] = "responsePayloadOnWriteDisabled"
        """Whether to disable response payload on write operations."""

        RETRY_WRITE: Final[str] = "retry_write"
        """Whether to retry write operations if they fail.
        Used either at client level or request level."""

        SESSION_TOKEN: Final[str] = "sessionToken"
        """Session token for session consistency."""

        SUPPORTED_QUERY_FEATURES: Final[str] = "supportedQueryFeatures"
        """Supported query features for the request."""

        THROUGHPUT_BUCKET: Final[str] = "throughputBucket"
        """Throughput bucket for the request."""

        # Additional internal options
        ENABLE_DIAGNOSTICS_LOGGING: Final[str] = "enableDiagnosticsLogging"
        """Whether to enable diagnostics logging."""

        LOGGER: Final[str] = "logger"
        """Logger instance for diagnostics."""

        PROXIES: Final[str] = "proxies"
        """Proxy configuration for requests."""

        USER_AGENT_SUFFIX: Final[str] = "userAgentSuffix"
        """Additional user agent suffix for requests."""

        TRANSPORT: Final[str] = "transport"
        """Custom transport for requests."""

        RESPONSE_HOOK: Final[str] = "responseHook"
        """Response hook callback function."""

        RAW_RESPONSE_HOOK: Final[str] = "rawResponseHook"
        """Raw response hook callback function."""

        FEED_RANGE: Final[str] = "feedRange"
        """Feed range for query operations."""

        PREFIX_PARTITION_KEY_OBJECT: Final[str] = "prefixPartitionKeyObject"
        """Prefix partition key object for queries."""

        PREFIX_PARTITION_KEY_VALUE: Final[str] = "prefixPartitionKeyValue"
        """Prefix partition key value for queries."""

        DISABLE_AUTOMATIC_ID_GENERATION: Final[str] = "disableAutomaticIdGeneration"
        """Whether to disable automatic ID generation for documents."""

        FILTER_PREDICATE: Final[str] = "filterPredicate"
        """Filter predicate for query operations."""

        CHANGE_FEED_STATE_CONTEXT: Final[str] = "changeFeedStateContext"
        """Change feed state context for change feed operations."""

        CONTAINER_PROPERTIES: Final[str] = "containerProperties"
        """Container properties for requests."""

        ETAG: Final[str] = "etag"
        """Entity tag for conditional operations."""

        MATCH_CONDITION: Final[str] = "matchCondition"
        """Match condition for conditional operations."""

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
        ACCESS_CONDITION: Final[str] = "access_condition"
        """Access condition kwarg for conditional operations (IfMatch, IfNoneMatch)."""

        AUTO_UPGRADE_POLICY: Final[str] = "auto_upgrade_policy"
        """Auto-upgrade policy kwarg for autoscale settings."""

        CONSISTENCY_LEVEL: Final[str] = "consistency_level"
        """Consistency level override kwarg for the request."""

        CONTAINER_RID: Final[str] = "container_rid"
        """Container resource ID kwarg for request routing."""

        CONTENT_TYPE: Final[str] = "content_type"
        """Content type kwarg for the request."""

        CONTINUATION: Final[str] = "continuation"
        """Continuation token kwarg for paginated queries."""

        CORRELATED_ACTIVITY_ID: Final[str] = "correlated_activity_id"
        """Correlated activity ID kwarg for tracing and diagnostics."""

        DISABLE_RU_PER_MINUTE_USAGE: Final[str] = "disable_ru_per_minute_usage"
        """Whether to disable RU per minute usage kwarg."""

        ENABLE_CROSS_PARTITION_QUERY: Final[str] = "enable_cross_partition_query"
        """Whether to enable cross-partition queries kwarg."""

        ENABLE_SCAN_IN_QUERY: Final[str] = "enable_scan_in_query"
        """Whether to enable scan in query operations kwarg."""

        ENABLE_SCRIPT_LOGGING: Final[str] = "enable_script_logging"
        """Whether to enable script logging for stored procedures kwarg."""

        EXCLUDED_LOCATIONS: Final[str] = "excluded_locations"
        """List of locations to exclude for this request kwarg."""

        INDEXING_DIRECTIVE: Final[str] = "indexing_directive"
        """Indexing directive kwarg for the operation."""

        INITIAL_HEADERS: Final[str] = "initial_headers"
        """Initial headers kwarg to include in the request."""

        IS_QUERY_PLAN_REQUEST: Final[str] = "is_query_plan_request"
        """Whether this is a query plan request kwarg."""

        MAX_INTEGRATED_CACHE_STALENESS: Final[str] = "max_integrated_cache_staleness"
        """Maximum integrated cache staleness kwarg in milliseconds."""

        MAX_ITEM_COUNT: Final[str] = "max_item_count"
        """Maximum number of items to return in the response kwarg."""

        OFFER_ENABLE_RU_PER_MINUTE_THROUGHPUT: Final[str] = "offer_enable_ru_per_minute_throughput"
        """Whether to enable RU per minute throughput for the offer kwarg."""

        OFFER_THROUGHPUT: Final[str] = "offer_throughput"
        """Throughput value kwarg for the offer."""

        OFFER_TYPE: Final[str] = "offer_type"
        """Type of the offer kwarg (S1, S2, S3, etc.)."""

        PARTITION_KEY: Final[str] = "partition_key"
        """Partition key value kwarg for the request."""

        POPULATE_INDEX_METRICS: Final[str] = "populate_index_metrics"
        """Whether to populate index metrics in the response kwarg."""

        POPULATE_PARTITION_KEY_RANGE_STATISTICS: Final[str] = "populate_partition_key_range_statistics"
        """Whether to populate partition key range statistics kwarg."""

        POPULATE_QUERY_METRICS: Final[str] = "populate_query_metrics"
        """Whether to populate query metrics in the response kwarg."""

        POPULATE_QUOTA_INFO: Final[str] = "populate_quota_info"
        """Whether to populate quota information in the response kwarg."""

        POST_TRIGGER_INCLUDE: Final[str] = "post_trigger_include"
        """Post-trigger scripts kwarg to include in the operation."""

        PRE_TRIGGER_INCLUDE: Final[str] = "pre_trigger_include"
        """Pre-trigger scripts kwarg to include in the operation."""

        PRIORITY: Final[str] = "priority"
        """Priority level kwarg for the request (High, Low)."""

        QUERY_VERSION: Final[str] = "query_version"
        """Query version kwarg for the request."""

        RESOURCE_TOKEN_EXPIRY_SECONDS: Final[str] = "resource_token_expiry_seconds"
        """Resource token expiry time kwarg in seconds."""

        RESPONSE_CONTINUATION_TOKEN_LIMIT_IN_KB: Final[str] = "response_continuation_token_limit_in_kb"
        """Continuation token size limit kwarg in KB."""

        NO_RESPONSE: Final[str] = "no_response"
        """Whether to disable response payload on write operations kwarg."""

        RETRY_WRITE: Final[str] = "retry_write"
        """Whether to retry write operations if they fail kwarg.
        Used either at client level or request level."""

        SESSION_TOKEN: Final[str] = "session_token"
        """Session token kwarg for session consistency."""

        SUPPORTED_QUERY_FEATURES: Final[str] = "supported_query_features"
        """Supported query features kwarg for the request."""

        THROUGHPUT_BUCKET: Final[str] = "throughput_bucket"
        """Throughput bucket kwarg for the request."""

        # Additional public kwargs
        ENABLE_DIAGNOSTICS_LOGGING: Final[str] = "enable_diagnostics_logging"
        """Whether to enable diagnostics logging kwarg."""

        LOGGER: Final[str] = "logger"
        """Logger instance kwarg for diagnostics."""

        PROXIES: Final[str] = "proxies"
        """Proxy configuration kwarg for requests."""

        USER_AGENT_SUFFIX: Final[str] = "user_agent_suffix"
        """Additional user agent suffix kwarg for requests."""

        TRANSPORT: Final[str] = "transport"
        """Custom transport kwarg for requests."""

        RESPONSE_HOOK: Final[str] = "response_hook"
        """Response hook callback function kwarg."""

        RAW_RESPONSE_HOOK: Final[str] = "raw_response_hook"
        """Raw response hook callback function kwarg."""

        FEED_RANGE: Final[str] = "feed_range"
        """Feed range kwarg for query operations."""

        PREFIX_PARTITION_KEY_OBJECT: Final[str] = "prefix_partition_key_object"
        """Prefix partition key object kwarg for queries."""

        PREFIX_PARTITION_KEY_VALUE: Final[str] = "prefix_partition_key_value"
        """Prefix partition key value kwarg for queries."""

        ETAG: Final[str] = "etag"
        """Entity tag kwarg for conditional operations."""

        MATCH_CONDITION: Final[str] = "match_condition"
        """Match condition kwarg for conditional operations."""
