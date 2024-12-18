# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

OFFLINE_STORE_CONNECTION_NAME = "OfflineStoreConnectionName"
OFFLINE_MATERIALIZATION_STORE_TYPE = "azure_data_lake_gen2"
OFFLINE_STORE_CONNECTION_CATEGORY = "ADLSGen2"
ONLINE_STORE_CONNECTION_NAME = "OnlineStoreConnectionName"
ONLINE_MATERIALIZATION_STORE_TYPE = "redis"
ONLINE_STORE_CONNECTION_CATEGORY = "Redis"
DEFAULT_SPARK_RUNTIME_VERSION = "3.3.0"
STORE_REGEX_PATTERN = (
    "^/?subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.Storage"
    "/storageAccounts/([^/]+)/blobServices/default/containers/([^/]+)"
)
