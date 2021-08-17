# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from datetime import datetime, timedelta
import urllib3
from azure.monitor.query import MetricsQueryClient, AggregationType
from azure.identity import DefaultAzureCredential

urllib3.disable_warnings()

# [START metrics_client_auth_with_token_cred]
credential  = DefaultAzureCredential()

client = MetricsQueryClient(credential)
# [END metrics_client_auth_with_token_cred]

# [START send_metrics_query]
metrics_uri = "/subscriptions/faa080af-c1d8-40ad-9cce-e1a450ca5b57/resourceGroups/sabhyrav-resourcegroup/providers/Microsoft.EventGrid/topics/rakshith-cloud"
response = client.query(
    metrics_uri,
    metric_names=["MatchedEventCount", "DeliverySuccesssCount"],
    timespan=timedelta(days=1),
    aggregations=[AggregationType.COUNT]
    )

for metric in response.metrics:
    print(metric.name)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            if metric_value.count != 0:
                print(
                    "There are {} matched events at {}".format(
                        metric_value.count,
                        metric_value.time_stamp
                    )
                )
# [END send_metrics_query]
