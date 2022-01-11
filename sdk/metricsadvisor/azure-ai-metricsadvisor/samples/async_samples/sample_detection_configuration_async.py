# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_detection_configuration_async.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, update, and delete anomaly detection configurations
    under your Metrics Advisor account.

USAGE:
    python sample_detection_configuration_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_METRIC_ID - the ID of an metric from an existing data feed
"""

import os
import asyncio


async def sample_create_detection_config_async():
    # [START create_detection_config_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import (
        ChangeThresholdCondition,
        HardThresholdCondition,
        SmartDetectionCondition,
        SuppressCondition,
        MetricDetectionCondition,
    )

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    change_threshold_condition = ChangeThresholdCondition(
        anomaly_detector_direction="Both",
        change_percentage=20,
        shift_point=10,
        within_range=True,
        suppress_condition=SuppressCondition(
            min_number=5,
            min_ratio=2
        )
    )
    hard_threshold_condition = HardThresholdCondition(
        anomaly_detector_direction="Up",
        upper_bound=100,
        suppress_condition=SuppressCondition(
            min_number=2,
            min_ratio=2
        )
    )
    smart_detection_condition = SmartDetectionCondition(
        anomaly_detector_direction="Up",
        sensitivity=10,
        suppress_condition=SuppressCondition(
            min_number=2,
            min_ratio=2
        )
    )

    async with client:
        detection_config = await client.create_detection_configuration(
            name="my_detection_config",
            metric_id=metric_id,
            description="anomaly detection config for metric",
            whole_series_detection_condition=MetricDetectionCondition(
                condition_operator="OR",
                change_threshold_condition=change_threshold_condition,
                hard_threshold_condition=hard_threshold_condition,
                smart_detection_condition=smart_detection_condition
            )
        )

        return detection_config
    # [END create_detection_config_async]


async def sample_get_detection_config_async(detection_config_id):
    # [START get_detection_config_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        config = await client.get_detection_configuration(detection_config_id)

        print("Detection config name: {}".format(config.name))
        print("Description: {}".format(config.description))
        print("Metric ID: {}".format(config.metric_id))

        print("\nDetection conditions specified for configuration...")
        print("\nWhole Series Detection Conditions:\n")
        conditions = config.whole_series_detection_condition

        print("Use {} operator for multiple detection conditions".format(conditions.condition_operator))

        print("Smart Detection Condition:")
        print("- Sensitivity: {}".format(conditions.smart_detection_condition.sensitivity))
        print("- Detection direction: {}".format(conditions.smart_detection_condition.anomaly_detector_direction))
        print("- Suppress conditions: minimum number: {}; minimum ratio: {}".format(
            conditions.smart_detection_condition.suppress_condition.min_number,
            conditions.smart_detection_condition.suppress_condition.min_ratio
        ))

        print("Hard Threshold Condition:")
        print("- Lower bound: {}".format(conditions.hard_threshold_condition.lower_bound))
        print("- Upper bound: {}".format(conditions.hard_threshold_condition.upper_bound))
        print("- Detection direction: {}".format(conditions.smart_detection_condition.anomaly_detector_direction))
        print("- Suppress conditions: minimum number: {}; minimum ratio: {}".format(
            conditions.smart_detection_condition.suppress_condition.min_number,
            conditions.smart_detection_condition.suppress_condition.min_ratio
        ))

        print("Change Threshold Condition:")
        print("- Change percentage: {}".format(conditions.change_threshold_condition.change_percentage))
        print("- Shift point: {}".format(conditions.change_threshold_condition.shift_point))
        print("- Detect anomaly if within range: {}".format(conditions.change_threshold_condition.within_range))
        print("- Detection direction: {}".format(conditions.smart_detection_condition.anomaly_detector_direction))
        print("- Suppress conditions: minimum number: {}; minimum ratio: {}".format(
            conditions.smart_detection_condition.suppress_condition.min_number,
            conditions.smart_detection_condition.suppress_condition.min_ratio
        ))

    # [END get_detection_config_async]


async def sample_list_detection_configs_async():
    # [START list_detection_configs_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        configs = client.list_detection_configurations(metric_id=metric_id)
        async for config in configs:
            print("Detection config name: {}".format(config.name))
            print("Description: {}".format(config.description))
            print("Metric ID: {}\n".format(config.metric_id))

    # [END list_detection_configs_async]


async def sample_update_detection_config_async(detection_config):
    # [START update_detection_config_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import (
        MetricSeriesGroupDetectionCondition,
        MetricSingleSeriesDetectionCondition,
        SmartDetectionCondition,
        SuppressCondition
    )

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    detection_config.name = "updated config name"
    detection_config.description = "updated with more detection conditions"
    smart_detection_condition = SmartDetectionCondition(
        anomaly_detector_direction="Up",
        sensitivity=10,
        suppress_condition=SuppressCondition(
            min_number=2,
            min_ratio=2
        )
    )

    async with client:
        updated = await client.update_detection_configuration(
            detection_config,
            series_group_detection_conditions=[
                MetricSeriesGroupDetectionCondition(
                    series_group_key={"region": "Seoul"},
                    smart_detection_condition=smart_detection_condition
                )
            ],
            series_detection_conditions=[
                MetricSingleSeriesDetectionCondition(
                    series_key={"region": "Osaka", "category": "Cell Phones"},
                    smart_detection_condition=smart_detection_condition
                )
            ]
        )
        print("Updated detection name: {}".format(updated.name))
        print("Updated detection description: {}".format(updated.description))
        print("Updated detection condition for series group: {}".format(
            updated.series_group_detection_conditions[0].series_group_key
        ))
        print("Updated detection condition for series: {}".format(
            updated.series_detection_conditions[0].series_key
        ))

    # [END update_detection_config_async]


async def sample_delete_detection_config_async(detection_config_id):
    # [START delete_detection_config_async]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        await client.delete_detection_configuration(detection_config_id)

        try:
            await client.get_detection_configuration(detection_config_id)
        except ResourceNotFoundError:
            print("Detection configuration successfully deleted.")
    # [END delete_detection_config_async]


async def main():
    print("---Creating anomaly detection configuration...")
    detection_config = await sample_create_detection_config_async()
    print("Anomaly detection configuration successfully created...")
    print("\n---Get an anomaly detection configuration...")
    await sample_get_detection_config_async(detection_config.id)
    print("\n---List anomaly detection configurations...")
    await sample_list_detection_configs_async()
    print("\n---Update an anomaly detection configuration...")
    await sample_update_detection_config_async(detection_config)
    print("\n---Delete an anomaly detection configuration...")
    await sample_delete_detection_config_async(detection_config.id)


if __name__ == '__main__':
    asyncio.run(main())
