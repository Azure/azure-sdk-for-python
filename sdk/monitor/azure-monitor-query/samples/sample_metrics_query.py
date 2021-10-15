# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_metrics_query.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying a single query
    on multiple workspaces using the additional_workspaces param.
USAGE:
    python sample_metrics_query.py
    Set the environment variables with your own values before running the sample:
    1) METRICS_RESOURCE_URI - The resource uri of the resource for which the metrics are being queried.
    In this example, a storage account resource URI is taken.

    In order to use the DefaultAzureCredential, the following environment variables must be set:
    1) AZURE_CLIENT_ID - The client ID of a user-assigned managed identity.
    2) AZURE_TENANT_ID - Tenant ID to use when authenticating a user.
    3) AZURE_CLIENT_ID - The client secret to be used for authentication.
"""
import os
from datetime import timedelta
import urllib3
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from azure.identity import DefaultAzureCredential

# provide a cert or disable warnings to run this sample
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# [START metrics_client_auth_with_token_cred]
credential  = DefaultAzureCredential()

client = MetricsQueryClient(credential)
# [END metrics_client_auth_with_token_cred]

# [START send_metrics_query]
metrics_uri = os.environ.get('METRICS_RESOURCE_URI')
response = client.query_resource(
    metrics_uri,
    metric_names=["Ingress"],
    timespan=timedelta(hours=2),
    granularity=timedelta(minutes=5),
    aggregations=[MetricAggregationType.AVERAGE],
    )

for metric in response.metrics:
    print(metric.name + ' -- ' + metric.display_description)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            print('The ingress at {} is {}'.format(
                metric_value.timestamp,
                metric_value.average
            ))
# [END send_metrics_query]
