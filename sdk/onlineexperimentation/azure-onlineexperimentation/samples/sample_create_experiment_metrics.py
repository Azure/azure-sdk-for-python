#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Create different types of experiment metrics
"""

import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.onlineexperimentation.models import (
    ExperimentMetric,
    LifecycleStage,
    DesiredDirection,
    EventCountMetricDefinition,
    UserCountMetricDefinition,
    EventRateMetricDefinition,
    UserRateMetricDefinition,
    SumMetricDefinition,
    AverageMetricDefinition,
    PercentileMetricDefinition,
    ObservedEvent,
    AggregatedValue,
)
from azure.core.exceptions import HttpResponseError


def create_event_count_metric():
    # Create a client with your Azure Online Experimentation workspace endpoint and credentials
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define the Event Count metric - counts all occurrences of a specific event type
    prompt_sent_metric = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="Total number of prompts sent",
        description="Counts the total number of prompts sent by users to the chatbot",
        categories=["Usage"],
        desired_direction=DesiredDirection.INCREASE,
        definition=EventCountMetricDefinition(event=ObservedEvent(event_name="PromptSent")),
    )

    try:
        # Create the metric with ID "prompt_sent_count"
        response = client.create_or_update_metric("prompt_sent_count", prompt_sent_metric)

        print(f"Created metric: {response.id}")
        print(f"Display name: {response.display_name}")
    except HttpResponseError as error:
        print(f"Failed to create metric: {error}")


def create_user_count_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define the User Count metric with a filter - counts unique users who performed a specific action
    users_prompt_sent_metric = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="Users with at least one prompt sent on checkout page",
        description="Counts unique users who sent at least one prompt while on the checkout page",
        categories=["Usage"],
        desired_direction=DesiredDirection.INCREASE,
        definition=UserCountMetricDefinition(
            event=ObservedEvent(event_name="PromptSent", filter="Page == 'checkout.html'")
        ),
    )

    try:
        # Create the metric with ID "users_prompt_sent"
        response = client.create_or_update_metric("users_prompt_sent", users_prompt_sent_metric)

        print(f"Created metric: {response.id}")
    except HttpResponseError as error:
        print(f"Failed to create metric: {error}")


def create_event_rate_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define the Event Rate metric - measures a percentage of events meeting a condition
    relevance_metric = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="% evaluated conversations with good relevance",
        description="Percentage of evaluated conversations where the LLM response has good relevance (score >= 4)",
        categories=["Quality"],
        desired_direction=DesiredDirection.INCREASE,
        definition=EventRateMetricDefinition(
            event=ObservedEvent(event_name="EvaluateLLM"), rate_condition="Relevance > 4"
        ),
    )

    try:
        # Create the metric
        response = client.create_or_update_metric("pct_relevance_good", relevance_metric)

        print(f"Created metric: {response.id}")
    except HttpResponseError as error:
        print(f"Failed to create metric: {error}")


def create_user_rate_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define the User Rate metric - measures percentage of users who performed action B after action A
    conversion_metric = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="% users with LLM interaction who made a high-value purchase",
        description="Percentage of users who received a response from the LLM and then made a purchase of $100 or more",
        categories=["Business"],
        desired_direction=DesiredDirection.INCREASE,
        definition=UserRateMetricDefinition(
            start_event=ObservedEvent(event_name="ResponseReceived"),
            end_event=ObservedEvent(event_name="Purchase", filter="Revenue > 100"),
        ),
    )

    try:
        # Create the metric
        response = client.create_or_update_metric("pct_chat_to_high_value_purchase_conversion", conversion_metric)

        print(f"Created metric: {response.id}")
    except HttpResponseError as error:
        print(f"Failed to create metric: {error}")


def create_sum_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define the Sum metric - sums a numeric value across all events of a type
    revenue_metric = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="Total revenue",
        description="Sum of revenue from all purchase transactions",
        categories=["Business"],
        desired_direction=DesiredDirection.INCREASE,
        definition=SumMetricDefinition(
            value=AggregatedValue(event_name="Purchase", event_property="Revenue", filter="Revenue > 0")
        ),
    )

    try:
        # Create the metric
        response = client.create_or_update_metric("total_revenue", revenue_metric)

        print(f"Created metric: {response.id}")
    except HttpResponseError as error:
        print(f"Failed to create metric: {error}")


def create_average_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define the Average metric - calculates the mean of a numeric value across events
    avg_revenue_metric = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="Average revenue per purchase",
        description="The average revenue per purchase transaction in USD",
        categories=["Business"],
        desired_direction=DesiredDirection.INCREASE,
        definition=AverageMetricDefinition(value=AggregatedValue(event_name="Purchase", event_property="Revenue")),
    )

    try:
        # Create the metric
        response = client.create_or_update_metric("avg_revenue_per_purchase", avg_revenue_metric)

        print(f"Created metric: {response.id}")
        print(f"Display name: {response.display_name}")
    except HttpResponseError as error:
        print(f"Failed to create metric: {error}")


def create_percentile_metric():
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())

    # Define the Percentile metric - calculates a specific percentile of a numeric value
    p95_response_time_metric = ExperimentMetric(
        lifecycle=LifecycleStage.ACTIVE,
        display_name="P95 LLM response time [seconds]",
        description="The 95th percentile of response time in seconds for LLM responses",
        categories=["Performance"],
        desired_direction=DesiredDirection.DECREASE,
        definition=PercentileMetricDefinition(
            value=AggregatedValue(event_name="ResponseReceived", event_property="ResponseTimeSeconds"), percentile=95
        ),
    )

    try:
        # Create the metric
        response = client.create_or_update_metric("p95_response_time_seconds", p95_response_time_metric)

        print(f"Created metric: {response.id}")
    except HttpResponseError as error:
        print(f"Failed to create metric: {error}")


if __name__ == "__main__":
    create_event_count_metric()
    create_user_count_metric()
    create_event_rate_metric()
    create_user_rate_metric()
    create_sum_metric()
    create_average_metric()
    create_percentile_metric()
