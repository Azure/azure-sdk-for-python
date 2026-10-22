#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Update an existing experiment metric
"""

import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError


def update_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    try:
        # First, get the existing metric
        existing_metric = client.get_metric("avg_revenue_per_purchase")

        # Modify the metric properties
        existing_metric.display_name = "Average revenue per purchase [USD]"
        existing_metric.description = (
            "The average revenue per purchase transaction in USD. Refund transactions are excluded."
        )

        # Update the metric - the create_or_update_metric method is used for both creating and updating
        response = client.create_or_update_metric(existing_metric.id, existing_metric)

        print(f"Updated metric: {response.id}")
        print(f"New display name: {response.display_name}")
        print(f"New description: {response.description}")
    except HttpResponseError as error:
        print(f"Failed to update metric: {error}")


if __name__ == "__main__":
    update_metric()
