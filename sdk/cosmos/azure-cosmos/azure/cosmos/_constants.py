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
    CIRCUIT_BREAKER_ENABLED_CONFIG: str =  "AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"
    CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT: str = "False"
    AAD_SCOPE_OVERRIDE: str = "AZURE_COSMOS_AAD_SCOPE_OVERRIDE"
    AAD_DEFAULT_SCOPE: str = "https://cosmos.azure.com/.default"

    # Database Account Retry Policy constants
    AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES: str = "AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES"
    AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES_DEFAULT: int = 3
    AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS: str = "AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS"
    AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS_DEFAULT: int = 100

    # Only applicable when circuit breaker is enabled -------------------------
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ: str = "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ"
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ_DEFAULT: int = 10
    CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE: str = "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE"
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


class _CosmosTracingConstants:
    # Required attributes
    DB_SYSTEM_NAME: Literal["db.system.name"] = "db.system.name"
    DB_SYSTEM_VALUE: Literal["azure.cosmosdb"] = "azure.cosmosdb"
    DB_OPERATION_NAME: Literal["db.operation.name"] = "db.operation.name"

    # Conditionally required attributes
    AZURE_COSMOS_CONNECTION_MODE: Literal["azure.cosmosdb.connection.mode"] = "azure.cosmosdb.connection.mode"
    AZURE_COSMOS_CONSISTENCY_LEVEL: Literal["azure.cosmosdb.consistency.level"] = "azure.cosmosdb.consistency.level"
    AZURE_COSMOS_OPERATION_CONTACTED_REGIONS: Literal[
        "azure.cosmosdb.operation.contacted_regions"] = "azure.cosmosdb.operation.contacted_regions"
    AZURE_COSMOS_OPERATION_REQUEST_CHARGE: Literal[
        "azure.cosmosdb.operation.request_charge"] = "azure.cosmosdb.operation.request_charge"
    AZURE_COSMOS_RESPONSE_SUB_STATUS_CODE: Literal[
        "azure.cosmosdb.response.sub_status_code"] = "azure.cosmosdb.response.sub_status_code"
    DB_COLLECTION_NAME: Literal["db.collection.name"] = "db.collection.name"
    DB_NAMESPACE: Literal["db.namespace"] = "db.namespace"
    DB_RESPONSE_RETURNED_ROWS: Literal["db.response.returned_rows"] = "db.response.returned_rows"
    DB_RESPONSE_STATUS_CODE: Literal["db.response.status_code"] = "db.response.status_code"
    ERROR_TYPE: Literal["error.type"] = "error.type"
    SERVER_PORT: Literal["server.port"] = "server.port"

    # Recommended attributes
    AZURE_CLIENT_ID: Literal["azure.client.id"] = "azure.client.id"
    AZURE_COSMOS_REQUEST_BODY_SIZE: Literal["azure.cosmosdb.request.body.size"] = "azure.cosmosdb.request.body.size"
    AZURE_RESOURCE_PROVIDER_NAMESPACE: Literal[
        "azure.resource_provider.namespace"] = "azure.resource_provider.namespace"
    DB_OPERATION_BATCH_SIZE: Literal["db.operation.batch.size"] = "db.operation.batch.size"
    DB_QUERY_TEXT: Literal["db.query.text"] = "db.query.text"
    DB_STORED_PROCEDURE_NAME: Literal["db.stored_procedure.name"] = "db.stored_procedure.name"
    SERVER_ADDRESS: Literal["server.address"] = "server.address"
    USER_AGENT_ORIGINAL: Literal["user_agent.original"] = "user_agent.original"

    # Opt-in / variable-key attributes
    DB_QUERY_PARAMETER_KEY: Literal["db.query.parameter.<key>"] = "db.query.parameter"

    # Additional common tracing keys seen in code (non-HTTP/header)
    ACTIVITY_ID: Literal["activity_id"] = "activity_id"
    DURATION_MS: Literal["duration"] = "duration"
    VERB: Literal["verb"] = "verb"
    URL: Literal["url"] = "url"
    OPERATION_TYPE: Literal["operation_type"] = "operation_type"
    RESOURCE_TYPE: Literal["resource_type"] = "resource_type"
    DATABASE_NAME: Literal["database_name"] = "database_name"
    COLLECTION_NAME: Literal["collection_name"] = "collection_name"
    STATUS_CODE: Literal["status_code"] = "status_code"
    SUB_STATUS_CODE: Literal["sub_status_code"] = "sub_status_code"
    EXCEPTION_TYPE: Literal["exception_type"] = "exception_type"
    IS_REQUEST: Literal["is_request"] = "is_request"
