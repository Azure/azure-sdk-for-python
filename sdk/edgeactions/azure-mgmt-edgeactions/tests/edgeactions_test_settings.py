# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
RESOURCE_GROUP_OPTIONS = {
    "name_prefix": "pythonsdk-edgeaction-test-",
    "random_name_length": 40,
    "location": "eastus",
}

# Only replace query values; polling paths and API versions must remain distinct.
POLLING_QUERY_SECRET_REGEX = r'(?i)(?<=[?&][tcsh]=)[^&\s"\\#]+'
TRACE_HEADERS = (
    "x-ms-correlation-request-id",
    "x-ms-routing-request-id",
    "x-ms-operation-identifier",
    "x-ms-original-request-ids",
    "X-MSEdge-Ref",
)
