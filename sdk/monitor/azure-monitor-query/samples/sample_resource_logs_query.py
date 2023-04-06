# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_resource_logs_query.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying the logs
    of a specific resource. Update the `query` variable with a query that corresponds to
    your resource.
USAGE:
    python sample_resource_logs_query.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_RESOURCE_ID - The resource ID. Example: `/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{resourceType}/{resourceName}`

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.

**Note** - Although this example uses pandas to print the response, it's optional and
isn't a required package for querying. Alternatively, native Python can be used as well.
"""
# [START resource_logs_query]
import os
import pandas as pd
from datetime import timedelta
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus


credential  = DefaultAzureCredential()
client = LogsQueryClient(credential)

query = """AzureActivity | take 5"""

try:
    response = client.query_resource(os.environ['LOGS_RESOURCE_ID'], query, timespan=timedelta(days=1))
    if response.status == LogsQueryStatus.PARTIAL:
        error = response.partial_error
        data = response.partial_data
        print(error)
    elif response.status == LogsQueryStatus.SUCCESS:
        data = response.tables
    for table in data:
        df = pd.DataFrame(data=table.rows, columns=table.columns)
        print(df)
except HttpResponseError as err:
    print("something fatal happened")
    print(err)

# [END resource_logs_query]
