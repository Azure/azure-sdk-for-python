#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Demonstrates how to create, update, and delete experiment metrics
using the Azure Online Experimentation service client library for Python.
"""

# [START experiment_metrics_management]
import os
import random
import json
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.onlineexperimentation.models import (
    ExperimentMetric,
    LifecycleStage,
    DesiredDirection,
    UserRateMetricDefinition,
    ObservedEvent,
)
from azure.core.exceptions import HttpResponseError

# [Step 1] Initialize the SDK client
# The endpoint URL from the Microsoft.OnlineExperimentation/workspaces resource
endpoint = os.environ.get("AZURE_ONLINEEXPERIMENTATION_ENDPOINT", "<endpoint-not-set>")
credential = DefaultAzureCredential()

print(f"AZURE_ONLINEEXPERIMENTATION_ENDPOINT is {endpoint}")

client = OnlineExperimentationClient(endpoint=endpoint, credential=credential)

# [Step 2] Define the experiment metric
example_metric = ExperimentMetric(
    lifecycle=LifecycleStage.ACTIVE,
    display_name="% users with LLM interaction who made a high-value purchase",
    description="Percentage of users who received a response from the LLM and then made a purchase of $100 or more",
    categories=["Business"],
    desired_direction=DesiredDirection.INCREASE,
    definition=UserRateMetricDefinition(
        start_event=ObservedEvent(event_name="ResponseReceived"),
        end_event=ObservedEvent(event_name="Purchase", filter="Revenue > 100"),
    )
)

# [Optional][Step 2a] Validate the metric - checks for input errors without persisting anything
print("Checking if the experiment metric definition is valid...")
print(json.dumps(example_metric.as_dict(), indent=2))

try:
    validation_result = client.validate_metric(example_metric)
    
    print(f"Experiment metric definition valid: {validation_result.is_valid}.")
    for detail in validation_result.diagnostics or []:
        # Inspect details of why the metric definition was rejected as Invalid
        print(f"- {detail.code}: {detail.message}")
        
    # [Step 3] Create the experiment metric
    example_metric_id = f"sample_metric_id_{random.randint(10000, 20000)}"
    
    print(f"Creating the experiment metric {example_metric_id}...")
    # Using upsert to create the metric with If-None-Match header
    create_response = client.create_or_update_metric(
        experiment_metric_id=example_metric_id, 
        resource=example_metric,
        match_condition=None,  # This ensures If-None-Match: * header is sent
        etag=None
    )
    
    print(f"Experiment metric {create_response.id} created, etag: {create_response.e_tag}.")
    
    # [Step 4] Deactivate the experiment metric and update the description
    updated_metric = {
        "lifecycle": LifecycleStage.INACTIVE,  # pauses computation of this metric
        "description": "No longer need to compute this."
    }
    
    update_response = client.create_or_update_metric(
        experiment_metric_id=example_metric_id,
        resource=updated_metric,
        etag=create_response.e_tag,  # Ensures If-Match header is sent
        match_condition=None  # Not specifying match_condition as we're using etag
    )
    
    print(f"Updated metric: {update_response.id}, etag: {update_response.e_tag}.")
    
    # [Step 5] Delete the experiment metric
    client.delete_metric(
        experiment_metric_id=example_metric_id,
        etag=update_response.e_tag  # Ensures If-Match header is sent
    )
    
    print(f"Deleted metric: {example_metric_id}.")
    
except HttpResponseError as error:
    print(f"The operation failed with error: {error}")
# [END experiment_metrics_management]
