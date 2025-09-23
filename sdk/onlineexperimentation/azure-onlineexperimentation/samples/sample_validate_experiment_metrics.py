#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Validate experiment metrics before creation
"""

import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.onlineexperimentation.models import (
    ExperimentMetric,
    LifecycleStage,
    DesiredDirection,
    EventCountMetricDefinition,
    ObservedEvent,
)
from azure.core.exceptions import HttpResponseError


def validate_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define a metric to validate
    metric_to_validate = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="Test metric for validation",
        description="This metric definition will be validated before creation",
        categories=["Test"],
        desired_direction=DesiredDirection.INCREASE,
        definition=EventCountMetricDefinition(event=ObservedEvent(event_name="TestEvent")),
    )

    try:
        # Validate the metric - checks for errors in the definition
        validation_result = client.validate_metric(metric_to_validate)

        # Check if the metric definition is valid
        if validation_result.is_valid:
            print("Metric definition is valid")

            # Now create the validated metric
            created_metric = client.create_or_update_metric("test_metric_id", metric_to_validate)
            print(f"Created metric: {created_metric.id}")
        else:
            # Handle validation errors
            print("Metric definition has errors:")
            for detail in validation_result.diagnostics:
                print(f"- [{detail.code}] {detail.message}")
    except HttpResponseError as error:
        print(f"Operation failed: {error}")


if __name__ == "__main__":
    validate_metric()
