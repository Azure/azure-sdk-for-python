# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_queries.py

DESCRIPTION:
    This sample demonstrates how to query
    - metric enriched series data
    - dimension values
    - metric dimension values
    - metrics series data
    - metric series definitions
    - metric enrichment status

USAGE:
    python sample_queries.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_DETECTION_CONFIGURATION_ID - the ID of an existing detection configuration
    5) METRICS_ADVISOR_METRIC_ID - the ID of an metric from an existing data feed
"""

import os

def sample_list_metric_enriched_series_data():
    # [START list_metric_enriched_series_data]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    series_identity = {"city": "Los Angeles"}

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_metric_enriched_series_data(
        detection_configuration_id=detection_configuration_id,
        start_time=datetime.datetime(2020, 9, 1),
        end_time=datetime.datetime(2020, 11, 1),
        series=[series_identity]
    )
    for result in results:
        print(str(result))

    # [END list_metric_enriched_series_data]

def sample_list_dimension_values():
    # [START list_dimension_values]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    dimension_name = "city"

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_dimension_values(
        detection_configuration_id=detection_configuration_id,
        dimension_name=dimension_name,
        start_time=datetime.datetime(2020, 1, 1),
        end_time=datetime.datetime(2020, 10, 21),
    )
    for result in results:
        print(str(result))

    # [END list_dimension_values]

def sample_list_metric_dimension_values():
    # [START list_metric_dimension_values]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")
    dimension_name = "city"

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_metric_dimension_values(
        metric_id=metric_id,
        dimension_name=dimension_name,
    )
    for result in results:
        print(str(result))

    # [END list_metric_dimension_values]

def sample_list_metrics_series_data():
    # [START list_metrics_series_data]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_metrics_series_data(
            metric_id=metric_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
            series_to_filter=[
                {"city": "Los Angeles", "category": "Homemade"}
            ]
        )
    for result in results:
        print(str(result))

    # [END list_metrics_series_data]

def sample_list_metric_series_definitions():
    # [START list_metric_series_definitions]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_metric_series_definitions(
            metric_id=metric_id,
            active_since=datetime.datetime(2020, 1, 1),
        )
    for result in results:
        print(str(result))

    # [END list_metric_series_definitions]

def sample_list_metric_enrichment_status():
    # [START list_metric_enrichment_status]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_metric_enrichment_status(
            metric_id=metric_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
        )
    for result in results:
        print(str(result))

    # [END list_metric_enrichment_status]

if __name__ == '__main__':
    print("---List metric enriched series data...")
    sample_list_metric_enriched_series_data()
    print("---List dimension values...")
    sample_list_dimension_values()
    print("---List metric dimension values...")
    sample_list_metric_dimension_values()
    print("---List metric series data...")
    sample_list_metrics_series_data()
    print("---List metric series definitions...")
    sample_list_metric_series_definitions()
    print("---List metric enrichment status...")
    sample_list_metric_enrichment_status()
