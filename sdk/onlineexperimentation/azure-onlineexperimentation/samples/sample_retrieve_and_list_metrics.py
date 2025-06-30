#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Retrieve and list experiment metrics
"""

import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError


def retrieve_single_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    try:
        # Get a specific metric by ID
        metric = client.get_metric("avg_revenue_per_purchase")

        # Access metric properties to view or use the metric definition
        print(f"Metric ID: {metric.id}")
        print(f"Display name: {metric.display_name}")
        print(f"Description: {metric.description}")
        print(f"Lifecycle stage: {metric.lifecycle}")
        print(f"Desired direction: {metric.desired_direction}")
    except ResourceNotFoundError:
        print("The specified metric was not found in the workspace.")
    except HttpResponseError as error:
        print(f"Failed to retrieve metric: {error}")


def list_all_metrics():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    try:
        # List all metrics in the workspace
        print("Listing all metrics:")
        metrics = client.list_metrics()
        for item in metrics:
            print(f"- {item.id}: {item.display_name}")
    except HttpResponseError as error:
        print(f"Failed to list metrics: {error}")


if __name__ == "__main__":
    retrieve_single_metric()
    list_all_metrics()
