# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_ingestion.py

DESCRIPTION:
    This sample demonstrates how to monitor data feed ingestion by listing the ingestion statuses,
    refreshing ingestion for a time period, and getting the ingestion progress.

USAGE:
    python sample_ingestion.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_DATA_FEED_ID - The ID to an existing data feed under your account
"""

import os


def sample_list_data_feed_ingestion_status():
    # [START list_data_feed_ingestion_status]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    data_feed_id = os.getenv("METRICS_ADVISOR_DATA_FEED_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    ingestion_status = client.list_data_feed_ingestion_status(
        data_feed_id,
        datetime.datetime(2020, 9, 20),
        datetime.datetime(2020, 9, 25)
    )
    for status in ingestion_status:
        print("Timestamp: {}".format(status.timestamp))
        print("Status: {}".format(status.status))
        print("Message: {}\n".format(status.message))

    # [END list_data_feed_ingestion_status]


def sample_refresh_data_feed_ingestion():
    # [START refresh_data_feed_ingestion]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    data_feed_id = os.getenv("METRICS_ADVISOR_DATA_FEED_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    client.refresh_data_feed_ingestion(
        data_feed_id,
        datetime.datetime(2020, 9, 20),
        datetime.datetime(2020, 9, 25)
    )

    # [END refresh_data_feed_ingestion]


def sample_get_data_feed_ingestion_progress():
    # [START get_data_feed_ingestion_progress]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    data_feed_id = os.getenv("METRICS_ADVISOR_DATA_FEED_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    progress = client.get_data_feed_ingestion_progress(data_feed_id)

    print("Lastest active timestamp: {}".format(progress.latest_active_timestamp))
    print("Latest successful timestamp: {}".format(progress.latest_success_timestamp))

    # [END get_data_feed_ingestion_progress]


if __name__ == '__main__':
    print("---Listing data feed ingestion status...")
    sample_list_data_feed_ingestion_status()
    print("---Refreshing data feed ingestion...")
    sample_refresh_data_feed_ingestion()
    print("---Getting data feed ingestion progress...")
    sample_get_data_feed_ingestion_progress()
