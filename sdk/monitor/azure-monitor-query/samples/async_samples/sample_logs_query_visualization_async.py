# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore xtitle, ytitle, ymax
"""
FILE: sample_logs_query_visualization_async.py
DESCRIPTION:
    This sample demonstrates how a user might visualize the results of a query using the "plotly" library.
    Kusto queries can be visualized using the "render" operator.
    See https://learn.microsoft.com/azure/data-explorer/kusto/query/renderoperator.

    When executing a render operation in a query using the LogsQueryClient, visualization data can be returned in
    the response by setting the "include_visualization" keyword argument to True. The data returned conveys
    information about how the visualization should be rendered, but the interpretation of the data is generally
    up to the user.
USAGE:
    python sample_logs_query_visualization_async.py

    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.

    The "plotly" library can also be installed with `pip install plotly`.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import asyncio
from datetime import timedelta
import os

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query import LogsQueryStatus
from azure.monitor.query.aio import LogsQueryClient
import plotly.express as px


async def query_visualization():
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)

    query = (
        "AzureActivity "
        "| where Level == 'Error' | summarize operation_count=count() by OperationName "
        "| where operation_count > 10 | project OperationName, operation_count "
        "| sort by operation_count desc "
        "| render columnchart with (title='Operations with errors', xtitle='Operation', ytitle='Count', ymax=100)"
    )

    try:
        async with client:
            response = await client.query_workspace(
                os.environ["LOGS_WORKSPACE_ID"], query, timespan=timedelta(days=1), include_visualization=True
            )
            if response.status == LogsQueryStatus.SUCCESS:
                viz = response.visualization

                if not viz:
                    print("No visualization data returned.")
                    exit()

                # Examine the structure of the visualization data to see what information is provided.
                # Generally, it reflects properties set using the "render" operator in the query.
                print(viz)

                tables = response.tables
                for table in tables:
                    # For each entry, index 0 (OperationName) corresponds to the x-axis and index 1 (operation_count)
                    # corresponds to the y-axis. Some information from the "visualization" dict are used to help
                    # construct a bar chart.
                    fig = px.bar(
                        table.rows,
                        x=0,
                        y=1,
                        title=viz["title"],
                        labels={"0": viz["xTitle"], "1": viz["yTitle"]},
                        range_y=[0, viz["yMax"]],
                    )
                    # Output visualization to a file.
                    fig.write_html("query-visualization.html")
                    # To open in a browser, use:
                    # fig.show()
            else:
                error = response.partial_error
                data = response.partial_data
                print(error)
                print(data)

    except HttpResponseError as err:
        print("something fatal happened")
        print(err)
    await credential.close()


if __name__ == "__main__":
    asyncio.run(query_visualization())
