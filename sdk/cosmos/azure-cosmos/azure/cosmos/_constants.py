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

from enum import IntEnum
from typing_extensions import Literal
# cspell:ignore PPAF

class TimeoutScope:
    """Defines the scope of timeout application"""
    OPERATION: Literal["operation"] = "operation"  # Apply timeout to entire logical operation
    PAGE: Literal["page"] = "page"  # Apply timeout to individual page requests

# cspell:ignore reranker

class _Constants:
    """Constants used in the azure-cosmos package"""

    UserConsistencyPolicy: Literal["userConsistencyPolicy"] = "userConsistencyPolicy"
    DefaultConsistencyLevel: Literal["defaultConsistencyLevel"] = "defaultConsistencyLevel"
    OperationStartTime: Literal["operationStartTime"] = "operationStartTime"
    # whether to apply timeout to the whole logical operation or just a page request
    TimeoutScope: Literal["timeoutScope"] = "timeoutScope"

    # GlobalDB related constants
    WritableLocations: Literal["writableLocations"] = "writableLocations"
    ReadableLocations: Literal["readableLocations"] = "readableLocations"
    Name: Literal["name"] = "name"
    DatabaseAccountEndpoint: Literal["databaseAccountEndpoint"] = "databaseAccountEndpoint"
    DefaultEndpointsRefreshTime: int = 5 * 60 * 1000 # milliseconds
    EnablePerPartitionFailoverBehavior: Literal["enablePerPartitionFailoverBehavior"] = "enablePerPartitionFailoverBehavior" #pylint: disable=line-too-long

    # ServiceDocument Resource
    EnableMultipleWritableLocations: Literal["enableMultipleWriteLocations"] = "enableMultipleWriteLocations"

    # Environment variables
    NON_STREAMING_ORDER_BY_DISABLED_CONFIG: str = "AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY"
    NON_STREAMING_ORDER_BY_DISABLED_CONFIG_DEFAULT: str = "False"
    HS_MAX_ITEMS_CONFIG: str = "AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS"
    HS_MAX_ITEMS_CONFIG_DEFAULT: int = 1000
    MAX_ITEM_BUFFER_VS_CONFIG: str = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
    MAX_ITEM_BUFFER_VS_CONFIG_DEFAULT: int = 50000
    SESSION_TOKEN_FALSE_PROGRESS_MERGE_CONFIG: str = "AZURE_COSMOS_SESSION_TOKEN_FALSE_PROGRESS_MERGE"
    SESSION_TOKEN_FALSE_PROGRESS_MERGE_CONFIG_DEFAULT: str = "True"
    CIRCUIT_BREAKER_ENABLED_CONFIG: str = "AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"
    CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT: str = "False"
    AAD_SCOPE_OVERRIDE: str = "AZURE_COSMOS_AAD_SCOPE_OVERRIDE"
    AAD_DEFAULT_SCOPE: str = "https://cosmos.azure.com/.default"
    INFERENCE_SERVICE_DEFAULT_SCOPE = "https://dbinference.azure.com/.default"
    SEMANTIC_RERANKER_INFERENCE_ENDPOINT: str = "AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT"

    # Health Check Retry Policy constants
    AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES: str = "AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES"
    AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES_DEFAULT: int = 3
    AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS: str = "AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS"
    AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS_DEFAULT: int = 500

    # Only applicable when circuit breaker is enabled -------------------------
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ: str = "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ"
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ_DEFAULT: int = 10
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE: str = "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE"
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE_DEFAULT: int = 5
    FAILURE_PERCENTAGE_TOLERATED = "AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"
    FAILURE_PERCENTAGE_TOLERATED_DEFAULT: int = 90
    # -------------------------------------------------------------------------
    # Only applicable when per partition automatic failover is enabled --------
    TIMEOUT_ERROR_THRESHOLD_PPAF = "AZURE_COSMOS_TIMEOUT_ERROR_THRESHOLD_FOR_PPAF"
    TIMEOUT_ERROR_THRESHOLD_PPAF_DEFAULT: int = 10
    # -------------------------------------------------------------------------

    # Error code translations
    ERROR_TRANSLATIONS: dict[int, str] = {
        400: "BAD_REQUEST - Request being sent is invalid.",
        401: "UNAUTHORIZED - The input authorization token can't serve the request.",
        403: "FORBIDDEN",
        404: "NOT_FOUND - Entity with the specified id does not exist in the system.",
        405: "METHOD_NOT_ALLOWED",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT - Entity with the specified id already exists in the system.",
        410: "GONE",
        412: "PRECONDITION_FAILED - Operation cannot be performed because one of the specified precondition is not met",
        413: "REQUEST_ENTITY_TOO_LARGE - Document size exceeds limit.",
        424: "FAILED_DEPENDENCY - There is a failure in the transactional batch.",
        429: "TOO_MANY_REQUESTS",
        449: "RETRY_WITH - Conflicting request to resource has been attempted. Retry to avoid conflicts."
    }

    class Kwargs:
        """Keyword arguments used in the azure-cosmos package"""

        RETRY_WRITE: Literal["retry_write"] = "retry_write"
        """Whether to retry write operations if they fail. Used either at client level or request level."""
        EXCLUDED_LOCATIONS: Literal["excludedLocations"] = "excludedLocations"
        AVAILABILITY_STRATEGY_CONFIG: Literal["availabilityStrategyConfig"] = "availabilityStrategyConfig"
        """Availability strategy config. Used either at client level or request level"""

    class UserAgentFeatureFlags(IntEnum):
        """
        User agent feature flags.
        Each flag represents a bit in a number to encode what features are enabled. Therefore, the first feature flag
        will be 1, the second 2, the third 4, etc. When constructing the user agent suffix, the feature flags will be
        used to encode a unique number representing the features enabled. This number will be converted into a hex
        string following the prefix "F" to save space in the user agent as it is limited and appended to the user agent
        suffix. This number will then be used to determine what features are enabled by decoding the hex string back
        to a number and checking what bits are set.

        Features being developed should align with the .NET SDK as a source of truth for feature flag assignments:
        https://github.com/Azure/azure-cosmos-dotnet-v3/blob/master/Microsoft.Azure.Cosmos/src/Diagnostics/UserAgentFeatureFlags.cs

        Example:
            If the user agent suffix has "F3", this means that flags 1 and 2.
        """
        PER_PARTITION_AUTOMATIC_FAILOVER = 1
        PER_PARTITION_CIRCUIT_BREAKER = 2
