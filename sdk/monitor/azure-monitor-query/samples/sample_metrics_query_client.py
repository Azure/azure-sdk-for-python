# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from azure.monitor.query import MetricsClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = MetricsClient(credential)
names = [os.environ['STORAGE_METRIC_NAME']]
response = client.query(os.environ['APPINSIGHTS_STORAGE_RESOURCE_URI'], metricnames=names)
