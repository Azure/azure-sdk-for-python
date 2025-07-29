#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Delete an experiment metric
"""

import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError


def delete_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    try:
        # Delete a metric by ID - removes it from the workspace
        client.delete_metric("test_metric_id")
        print(f"Metric 'test_metric_id' successfully deleted")
    except ResourceNotFoundError:
        print("The specified metric was not found in the workspace.")
    except HttpResponseError as error:
        print(f"Failed to delete metric: {error}")


if __name__ == "__main__":
    delete_metric()
