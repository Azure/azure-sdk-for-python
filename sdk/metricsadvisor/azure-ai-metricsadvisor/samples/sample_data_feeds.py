# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_data_feeds.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, update, and delete datafeeds under your Metrics Advisor account.

USAGE:
    python sample_data_feeds.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_SQL_SERVER_CONNECTION_STRING - Used in this sample for demonstration, but you should
       add your own credentials specific to the data source type you're using
    5) METRICS_ADVISOR_SQL_SERVER_QUERY - Used in this sample for demonstration, but you should
       add your own credentials specific to the data source type you're using
"""

import os
import datetime


def sample_create_data_feed():
    # [START create_data_feed]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import (
        SQLServerDataFeed,
        DataFeedSchema,
        DataFeedMetric,
        DataFeedDimension,
        DataFeedOptions,
        DataFeedRollupSettings,
        DataFeedMissingDataPointFillSettings,
    )

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    sql_server_connection_string = os.getenv("METRICS_ADVISOR_SQL_SERVER_CONNECTION_STRING")
    query = os.getenv("METRICS_ADVISOR_SQL_SERVER_QUERY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    data_feed = client.create_data_feed(
        name="My data feed",
        source=SQLServerDataFeed(
            connection_string=sql_server_connection_string,
            query=query,
        ),
        granularity="Daily",
        schema=DataFeedSchema(
            metrics=[
                DataFeedMetric(name="cost", display_name="Cost"),
                DataFeedMetric(name="revenue", display_name="Revenue")
            ],
            dimensions=[
                DataFeedDimension(name="category", display_name="Category"),
                DataFeedDimension(name="city", display_name="City")
            ],
            timestamp_column="Timestamp"
        ),
        ingestion_settings=datetime.datetime(2019, 10, 1),
        options=DataFeedOptions(
            data_feed_description="cost/revenue data feed",
            rollup_settings=DataFeedRollupSettings(
                rollup_type="AutoRollup",
                rollup_method="Sum",
                rollup_identification_value="__CUSTOM_SUM__"
            ),
            missing_data_point_fill_settings=DataFeedMissingDataPointFillSettings(
                fill_type="SmartFilling"
            ),
            access_mode="Private"
        )
    )

    return data_feed

    # [END create_data_feed]


def sample_get_data_feed(data_feed_id):
    # [START get_data_feed]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    data_feed = client.get_data_feed(data_feed_id)

    print("ID: {}".format(data_feed.id))
    print("Data feed name: {}".format(data_feed.name))
    print("Created time: {}".format(data_feed.created_time))
    print("Status: {}".format(data_feed.status))
    print("Source type: {}".format(data_feed.source.data_source_type))
    print("Granularity type: {}".format(data_feed.granularity.granularity_type))
    print("Data feed metrics: {}".format([metric.name for metric in data_feed.schema.metrics]))
    print("Data feed dimensions: {}".format([dimension.name for dimension in data_feed.schema.dimensions]))
    print("Data feed timestamp column: {}".format(data_feed.schema.timestamp_column))
    print("Ingestion data starting on: {}".format(data_feed.ingestion_settings.ingestion_begin_time))
    print("Data feed description: {}".format(data_feed.options.data_feed_description))
    print("Data feed rollup type: {}".format(data_feed.options.rollup_settings.rollup_type))
    print("Data feed rollup method: {}".format(data_feed.options.rollup_settings.rollup_method))
    print("Data feed fill setting: {}".format(data_feed.options.missing_data_point_fill_settings.fill_type))
    print("Data feed access mode: {}".format(data_feed.options.access_mode))
    # [END get_data_feed]


def sample_list_data_feeds():
    # [START list_data_feeds]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    data_feeds = client.list_data_feeds()

    for feed in data_feeds:
        print("Data feed name: {}".format(feed.name))
        print("ID: {}".format(feed.id))
        print("Created time: {}".format(feed.created_time))
        print("Status: {}".format(feed.status))
        print("Source type: {}".format(feed.source.data_source_type))
        print("Granularity type: {}".format(feed.granularity.granularity_type))

        print("\nFeed metrics:")
        for metric in feed.schema.metrics:
            print(metric.name)

        print("\nFeed dimensions:")
        for dimension in feed.schema.dimensions:
            print(dimension.name)

    # [END list_data_feeds]


def sample_update_data_feed(data_feed):
    # [START update_data_feed]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    # update data feed on the data feed itself or by using available keyword arguments
    data_feed.name = "updated name"
    data_feed.options.data_feed_description = "updated description for data feed"

    client.update_data_feed(
        data_feed,
        access_mode="Public",
        fill_type="CustomValue",
        custom_fill_value=1
    )
    updated_data_feed = client.get_data_feed(data_feed.id)

    print("Updated name: {}".format(updated_data_feed.name))
    print("Updated description: {}".format(updated_data_feed.options.data_feed_description))
    print("Updated access mode: {}".format(updated_data_feed.options.access_mode))
    print("Updated fill setting, value: {}, {}".format(
        updated_data_feed.options.missing_data_point_fill_settings.fill_type,
        updated_data_feed.options.missing_data_point_fill_settings.custom_fill_value,
    ))
    # [END update_data_feed]


def sample_delete_data_feed(data_feed_id):
    # [START delete_data_feed]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    client.delete_data_feed(data_feed_id)

    try:
        client.get_data_feed(data_feed_id)
    except ResourceNotFoundError:
        print("Data feed successfully deleted.")

    # [END delete_data_feed]


if __name__ == '__main__':
    print("---Creating data feed...")
    data_feed = sample_create_data_feed()
    print("Data feed successfully created...")
    print("\n---Get a data feed...")
    sample_get_data_feed(data_feed.id)
    print("\n---List data feeds...")
    sample_list_data_feeds()
    print("\n---Update a data feed...")
    sample_update_data_feed(data_feed)
    print("\n---Delete a data feed...")
    sample_delete_data_feed(data_feed.id)
