#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show connection-string based authentication of the ServiceBusClient.

Note: To get credentials, one can either obtain the connection string from the Azure Portal,
or use the Azure CLI snippet below to populate an environment variable with the service bus connection string. The following is in bash:

```bash
RES_GROUP=<resource-group-name>
NAMESPACE_NAME=<servicebus-namespace-name>

export SERVICE_BUS_CONN_STR=$(az servicebus namespace authorization-rule keys list --resource-group $RES_GROUP --namespace-name $NAMESPACE_NAME --name RootManageSharedAccessKey --query primaryConnectionString --output tsv)
```
"""

from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']

with ServiceBusClient.from_connection_string(connstr) as client:
    pass # Client is now initialized and can be used.

