# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_incidents_async.py

DESCRIPTION:
    This sample demonstrates how to list incidents and root causes.

USAGE:
    python sample_incidents_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_DETECTION_CONFIGURATION_ID - the ID of an anomaly detection configuration
    5) METRICS_ADVISOR_ALERT_CONFIGURATION_ID - the ID of an alert configuration
    6) METRICS_ADVISOR_INCIDENT_ID - the ID of an incident
    7) METRICS_ADVISOR_ALERT_ID - the ID of an alert
"""

import os
import asyncio


async def sample_list_incidents_for_detection_configuration_async():
    # [START list_incidents_for_detection_configuration_async]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    async with client:
        results = client.list_incidents(
            detection_configuration_id=detection_configuration_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 9, 9),
        )
        async for result in results:
            print("Metric id: {}".format(result.metric_id))
            print("Incident ID: {}".format(result.id))
            print("Severity: {}".format(result.severity))
            print("Status: {}".format(result.status))

    # [END list_incidents_for_detection_configuration_async]

async def sample_list_incident_root_cause_async():
    # [START list_incident_root_cause_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    incident_id = os.getenv("METRICS_ADVISOR_INCIDENT_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    async with client:
        results = client.list_incident_root_causes(
            detection_configuration_id=detection_configuration_id,
            incident_id=incident_id,
        )
        async for result in results:
            print("Score: {}".format(result.score))
            print("Description: {}".format(result.description))

    # [END list_incident_root_cause_async]

async def sample_list_incidents_for_alert_async():
    # [START list_incidents_for_alert_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    alert_configuration_id = os.getenv("METRICS_ADVISOR_ALERT_CONFIGURATION_ID")
    alert_id = os.getenv("METRICS_ADVISOR_ALERT_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    async with client:
        results = client.list_incidents(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
        )
        async for result in results:
            print("Metric id: {}".format(result.metric_id))
            print("Incident ID: {}".format(result.id))
            print("Severity: {}".format(result.severity))
            print("Status: {}".format(result.status))

    # [END list_incidents_for_alert_async]


async def main():
    print("---List incidents for detection configuration...")
    await sample_list_incidents_for_detection_configuration_async()
    print("---List root causes...")
    await sample_list_incident_root_cause_async()
    print("---List incidents for alert configuration...")
    await sample_list_incidents_for_alert_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

