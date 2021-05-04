# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_queries_async.py

DESCRIPTION:
    This sample demonstrates how to query
    - metric enriched series data
    - dimension values
    - metric dimension values
    - metrics series data
    - metric series definitions
    - metric enrichment status

USAGE:
    python sample_queries_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_DETECTION_CONFIGURATION_ID - the ID of an existing detection configuration
    5) METRICS_ADVISOR_METRIC_ID - the ID of an metric from an existing data feed
"""

import os
import asyncio

async def sample_list_metric_enriched_series_data_async():
    # [START list_metric_enriched_series_data_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    series_identity = {"city": "Los Angeles"}

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        results = client.list_metric_enriched_series_data(
            detection_configuration_id=detection_configuration_id,
            start_time=datetime.datetime(2020, 9, 1),
            end_time=datetime.datetime(2020, 11, 1),
            series=[series_identity]
        )
        async for result in results:
            print(str(result))

    # [END list_metric_enriched_series_data_async]

async def sample_list_anomaly_dimension_values_async():
    # [START list_anomaly_dimension_values_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    dimension_name = "city"

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        results = client.list_anomaly_dimension_values(
            detection_configuration_id=detection_configuration_id,
            dimension_name=dimension_name,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
        )
        async for result in results:
            print(str(result))

    # [END list_anomaly_dimension_values_async]

async def sample_list_metric_dimension_values_async():
    # [START list_metric_dimension_values_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")
    dimension_name = "city"

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        results = client.list_metric_dimension_values(
            metric_id=metric_id,
            dimension_name=dimension_name,
        )
        async for result in results:
            print(str(result))

    # [END list_metric_dimension_values_async]

async def sample_list_metrics_series_data_async():
    # [START list_metrics_series_data_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        results = client.list_metrics_series_data(
                metric_id=metric_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
                series_to_filter=[
                    {"city": "Los Angeles", "category": "Homemade"}
                ]
            )
        async for result in results:
            print(str(result))

    # [END list_metrics_series_data_async]

async def sample_list_metric_series_definitions_async():
    # [START list_metric_series_definitions_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        results = client.list_metric_series_definitions(
                metric_id=metric_id,
                active_since=datetime.datetime(2020, 1, 1),
            )
        async for result in results:
            print(str(result))

    # [END list_metric_series_definitions_async]

async def sample_list_metric_enrichment_status_async():
    # [START list_metric_enrichment_status_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        results = client.list_metric_enrichment_status(
                metric_id=metric_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
            )
        async for result in results:
            print(str(result))

    # [END list_metric_enrichment_status_async]

async def main():
    print("---List metric enriched series data...")
    await sample_list_metric_enriched_series_data_async()
    print("---List dimension values...")
    await sample_list_anomaly_dimension_values_async()
    print("---List metric dimension values...")
    await sample_list_metric_dimension_values_async()
    print("---List metric series data...")
    await sample_list_metrics_series_data_async()
    print("---List metric series definitions...")
    await sample_list_metric_series_definitions_async()
    print("---List metric enrichment status...")
    await sample_list_metric_enrichment_status_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
