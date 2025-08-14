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

    class Kwargs:
        """Keyword arguments used in the azure-cosmos package

        These constants should be used instead of hardcoded strings for request options
        to improve maintainability, reduce errors, and provide better IDE support.

        Best practices:
        - Always use these constants instead of hardcoded strings
        - Follow the naming convention: UPPER_SNAKE_CASE for constant names
        - Use Literal types for type safety
        - Document the purpose of each constant
        """

        # Request option keys used in build_options and GetHeaders functions
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
