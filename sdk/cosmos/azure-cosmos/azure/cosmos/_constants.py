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

    # Request options key for the container resource ID (used to set the
    # x-ms-cosmos-intended-collection-rid header for container-recreate detection).
    ContainerRID: Literal["containerRID"] = "containerRID"

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
    HS_MAX_ITEMS_CONFIG: str = "AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS"
    HS_MAX_ITEMS_CONFIG_DEFAULT: int = 1000
    MAX_ITEM_BUFFER_VS_CONFIG: str = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
    MAX_ITEM_BUFFER_VS_CONFIG_DEFAULT: int = 50000
    SESSION_TOKEN_FALSE_PROGRESS_MERGE_CONFIG: str = "AZURE_COSMOS_SESSION_TOKEN_FALSE_PROGRESS_MERGE"
    SESSION_TOKEN_FALSE_PROGRESS_MERGE_CONFIG_DEFAULT: str = "True"
    CIRCUIT_BREAKER_ENABLED_CONFIG: str = "AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"
    CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT: str = "False"
    AAD_SCOPE_OVERRIDE: str = "AZURE_COSMOS_AAD_SCOPE_OVERRIDE"
    OTEL_ENABLE_QUERY_TEXT: str = "AZURE_COSMOS_ENABLE_DB_QUERY_TEXT"
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
        AVAILABILITY_STRATEGY: Literal["availabilityStrategy"] = "availabilityStrategy"
        """Availability strategy config. Used either at client level or request level"""
        READ_TIMEOUT: Literal["read_timeout"] = "read_timeout"
        """Socket read timeout in seconds. Used either at client level or request level."""
        TIMEOUT: Literal["timeout"] = "timeout"
        """Absolute timeout in seconds for the combined HTTP request and response processing."""

    class OpenTelemetryAttributes:
        """OpenTelemetry Semantic Convention attributes for Cosmos DB.

        Based on the official OpenTelemetry Cosmos DB semantic conventions.

        Reference:
        https://opentelemetry.io/docs/specs/semconv/db/cosmosdb/
        """

        # Core database attributes
        DB_SYSTEM_NAME: Literal["db.system.name"] = "db.system.name"
        DB_NAMESPACE: Literal["db.namespace"] = "db.namespace"  # Database name
        DB_OPERATION_NAME: Literal["db.operation.name"] = "db.operation.name"
        DB_COLLECTION_NAME: Literal["db.collection.name"] = "db.collection.name"
        DB_RESPONSE_STATUS_CODE: Literal["db.response.status_code"] = "db.response.status_code"
        DB_RESPONSE_RETURNED_ROWS: Literal["db.response.returned_rows"] = "db.response.returned_rows"
        DB_OPERATION_BATCH_SIZE: Literal["db.operation.batch.size"] = "db.operation.batch.size"
        DB_STORED_PROCEDURE_NAME: Literal["db.stored_procedure.name"] = "db.stored_procedure.name"
        ERROR_TYPE: Literal["error.type"] = "error.type"
        SERVER_ADDRESS: Literal["server.address"] = "server.address"
        SERVER_PORT: Literal["server.port"] = "server.port"
        USER_AGENT_ORIGINAL: Literal["user_agent.original"] = "user_agent.original"

        # Query attributes
        DB_QUERY_TEXT: Literal["db.query.text"] = "db.query.text"

        # Cosmos DB specific attributes
        AZURE_CLIENT_ID: Literal["azure.client.id"] = "azure.client.id"
        AZURE_COSMOSDB_CONNECTION_MODE: Literal["azure.cosmosdb.connection.mode"] = (
            "azure.cosmosdb.connection.mode"
        )
        AZURE_COSMOSDB_CONSISTENCY_LEVEL: Literal["azure.cosmosdb.consistency.level"] = (
            "azure.cosmosdb.consistency.level"
        )
        AZURE_COSMOSDB_OPERATION_CONTACTED_REGIONS: Literal[
            "azure.cosmosdb.operation.contacted_regions"
        ] = "azure.cosmosdb.operation.contacted_regions"
        AZURE_COSMOSDB_OPERATION_REQUEST_CHARGE: Literal[
            "azure.cosmosdb.operation.request_charge"
        ] = "azure.cosmosdb.operation.request_charge"
        AZURE_COSMOSDB_REQUEST_BODY_SIZE: Literal[
            "azure.cosmosdb.request.body.size"
        ] = "azure.cosmosdb.request.body.size"
        AZURE_COSMOSDB_RESPONSE_SUB_STATUS_CODE: Literal[
            "azure.cosmosdb.response.sub_status_code"
        ] = "azure.cosmosdb.response.sub_status_code"
        AZURE_RESOURCE_PROVIDER_NAMESPACE: Literal[
            "azure.resource_provider.namespace"
        ] = "azure.resource_provider.namespace"

    class OpenTelemetryValues:
        """Shared OpenTelemetry values used by Cosmos telemetry helpers."""

        DB_SYSTEM_NAME_VALUE: Literal["azure.cosmosdb"] = "azure.cosmosdb"
        AZURE_RESOURCE_PROVIDER_NAMESPACE_VALUE: Literal["Microsoft.DocumentDB"] = "Microsoft.DocumentDB"
        CONNECTION_MODE_DIRECT: Literal["direct"] = "direct"
        CONNECTION_MODE_GATEWAY: Literal["gateway"] = "gateway"

    class OpenTelemetryOperationNames:
        """Official Cosmos DB OpenTelemetry db.operation.name values used by this SDK."""

        EXECUTE_BATCH: Literal["execute_batch"] = "execute_batch"

        QUERY_CHANGE_FEED: Literal["query_change_feed"] = "query_change_feed"

        DELETE_CONFLICT: Literal["delete_conflict"] = "delete_conflict"
        QUERY_CONFLICTS: Literal["query_conflicts"] = "query_conflicts"
        READ_ALL_CONFLICTS: Literal["read_all_conflicts"] = "read_all_conflicts"
        READ_CONFLICT: Literal["read_conflict"] = "read_conflict"

        CREATE_CONTAINER: Literal["create_container"] = "create_container"
        CREATE_CONTAINER_IF_NOT_EXISTS: Literal["create_container_if_not_exists"] = "create_container_if_not_exists"
        DELETE_CONTAINER: Literal["delete_container"] = "delete_container"
        QUERY_CONTAINERS: Literal["query_containers"] = "query_containers"
        READ_ALL_CONTAINERS: Literal["read_all_containers"] = "read_all_containers"
        READ_CONTAINER: Literal["read_container"] = "read_container"
        READ_CONTAINER_THROUGHPUT: Literal["read_container_throughput"] = "read_container_throughput"
        REPLACE_CONTAINER: Literal["replace_container"] = "replace_container"
        REPLACE_CONTAINER_THROUGHPUT: Literal["replace_container_throughput"] = "replace_container_throughput"

        CREATE_DATABASE: Literal["create_database"] = "create_database"
        CREATE_DATABASE_IF_NOT_EXISTS: Literal["create_database_if_not_exists"] = "create_database_if_not_exists"
        DELETE_DATABASE: Literal["delete_database"] = "delete_database"
        QUERY_DATABASES: Literal["query_databases"] = "query_databases"
        READ_ALL_DATABASES: Literal["read_all_databases"] = "read_all_databases"
        READ_DATABASE: Literal["read_database"] = "read_database"
        READ_DATABASE_THROUGHPUT: Literal["read_database_throughput"] = "read_database_throughput"
        REPLACE_DATABASE_THROUGHPUT: Literal["replace_database_throughput"] = "replace_database_throughput"

        CREATE_ITEM: Literal["create_item"] = "create_item"
        DELETE_ALL_ITEMS_BY_PARTITION_KEY: Literal[
            "delete_all_items_by_partition_key"
        ] = "delete_all_items_by_partition_key"
        DELETE_ITEM: Literal["delete_item"] = "delete_item"
        PATCH_ITEM: Literal["patch_item"] = "patch_item"
        QUERY_ITEMS: Literal["query_items"] = "query_items"
        READ_ALL_ITEMS: Literal["read_all_items"] = "read_all_items"
        READ_MANY_ITEMS: Literal["read_many_items"] = "read_many_items"
        READ_ITEM: Literal["read_item"] = "read_item"
        REPLACE_ITEM: Literal["replace_item"] = "replace_item"
        UPSERT_ITEM: Literal["upsert_item"] = "upsert_item"

        CREATE_PERMISSION: Literal["create_permission"] = "create_permission"
        DELETE_PERMISSION: Literal["delete_permission"] = "delete_permission"
        QUERY_PERMISSIONS: Literal["query_permissions"] = "query_permissions"
        READ_ALL_PERMISSIONS: Literal["read_all_permissions"] = "read_all_permissions"
        READ_PERMISSION: Literal["read_permission"] = "read_permission"
        REPLACE_PERMISSION: Literal["replace_permission"] = "replace_permission"
        UPSERT_PERMISSION: Literal["upsert_permission"] = "upsert_permission"

        CREATE_USER: Literal["create_user"] = "create_user"
        DELETE_USER: Literal["delete_user"] = "delete_user"
        QUERY_USERS: Literal["query_users"] = "query_users"
        READ_ALL_USERS: Literal["read_all_users"] = "read_all_users"
        READ_USER: Literal["read_user"] = "read_user"
        REPLACE_USER: Literal["replace_user"] = "replace_user"
        UPSERT_USER: Literal["upsert_user"] = "upsert_user"

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
