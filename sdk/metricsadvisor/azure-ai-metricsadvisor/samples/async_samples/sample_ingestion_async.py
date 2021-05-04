# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_ingestion_async.py

DESCRIPTION:
    This sample demonstrates how to monitor data feed ingestion by listing the ingestion statuses,
    refreshing ingestion for a time period, and getting the ingestion progress.

USAGE:
    python sample_ingestion_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_DATA_FEED_ID - The ID to an existing data feed under your account
"""

import os
import asyncio


async def sample_list_data_feed_ingestion_status_async():
    # [START list_data_feed_ingestion_status_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    data_feed_id = os.getenv("METRICS_ADVISOR_DATA_FEED_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        ingestion_status = client.list_data_feed_ingestion_status(
            data_feed_id,
            datetime.datetime(2020, 9, 20),
            datetime.datetime(2020, 9, 25)
        )
        async for status in ingestion_status:
            print("Timestamp: {}".format(status.timestamp))
            print("Status: {}".format(status.status))
            print("Message: {}\n".format(status.message))

    # [END list_data_feed_ingestion_status_async]


async def sample_refresh_data_feed_ingestion_async():
    # [START refresh_data_feed_ingestion_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    data_feed_id = os.getenv("METRICS_ADVISOR_DATA_FEED_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        await client.refresh_data_feed_ingestion(
            data_feed_id,
            datetime.datetime(2020, 9, 20),
            datetime.datetime(2020, 9, 25)
        )

    # [END refresh_data_feed_ingestion_async]


async def sample_get_data_feed_ingestion_progress_async():
    # [START get_data_feed_ingestion_progress_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    data_feed_id = os.getenv("METRICS_ADVISOR_DATA_FEED_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        progress = await client.get_data_feed_ingestion_progress(data_feed_id)

        print("Lastest active timestamp: {}".format(progress.latest_active_timestamp))
        print("Latest successful timestamp: {}".format(progress.latest_success_timestamp))

    # [END get_data_feed_ingestion_progress_async]


async def main():
    print("---Listing data feed ingestion status...")
    await sample_list_data_feed_ingestion_status_async()
    print("---Refreshing data feed ingestion...")
    await sample_refresh_data_feed_ingestion_async()
    print("---Getting data feed ingestion progress...")
    await sample_get_data_feed_ingestion_progress_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
