# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_logs_query_key_value_form.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying a single query
    and printing the response in a key value form.
USAGE:
    python sample_logs_query_key_value_form.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.

**Note** - Although this example uses pandas to print the response, it's optional and
isn't a required package for querying. Alternatively, native Python can be used as well.
"""
from datetime import timedelta
import os
from pprint import pprint

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
import pandas as pd


credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

query = "AppRequests | take 5"

try:
    response = client.query_workspace(os.environ["LOGS_WORKSPACE_ID"], query, timespan=timedelta(days=1))
    if response.status == LogsQueryStatus.SUCCESS:
        data = response.tables
    else:
        # LogsQueryPartialResult - handle error here
        error = response.partial_error
        data = response.partial_data
        print(error)

    for table in data:
        df = pd.DataFrame(data=table.rows, columns=table.columns)
        key_value = df.to_dict(orient="records")
        pprint(key_value)
except HttpResponseError as err:
    print("something fatal happened")
    print(err)
