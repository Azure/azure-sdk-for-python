# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_incidents.py

DESCRIPTION:
    This sample demonstrates how to list incidents and root causes.

USAGE:
    python sample_incidents.py

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


def sample_list_incidents_for_detection_configuration():
    # [START list_incidents_for_detection_configuration]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    # detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    detection_configuration_id = "efaee305-f049-43ec-9f9b-76026d55c14a"

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    results = client.list_incidents(
        detection_configuration_id=detection_configuration_id,
        start_time=datetime.datetime(2021, 1, 1),
        end_time=datetime.datetime(2021, 9, 9),
    )
    for result in results:
        print("Metric id: {}".format(result.metric_id))
        print("Incident ID: {}".format(result.id))
        print("Severity: {}".format(result.severity))
        print("Status: {}".format(result.status))

    # [END list_incidents_for_detection_configuration]

def sample_list_incident_root_cause():
    # [START list_incident_root_cause]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    incident_id = os.getenv("METRICS_ADVISOR_INCIDENT_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    results = client.list_incident_root_causes(
        detection_configuration_id=detection_configuration_id,
        incident_id=incident_id,
    )
    for result in results:
        print("Score: {}".format(result.score))
        print("Description: {}".format(result.description))

    # [END list_incident_root_cause]

def sample_list_incidents_for_alert():
    # [START list_incidents_for_alert]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    alert_configuration_id = os.getenv("METRICS_ADVISOR_ALERT_CONFIGURATION_ID")
    alert_id = os.getenv("METRICS_ADVISOR_ALERT_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    results = client.list_incidents(
        alert_configuration_id=alert_configuration_id,
        alert_id=alert_id,
    )
    for result in results:
        print("Metric id: {}".format(result.metric_id))
        print("Incident ID: {}".format(result.id))
        print("Severity: {}".format(result.severity))
        print("Status: {}".format(result.status))

    # [END list_incidents_for_alert]

if __name__ == '__main__':
    print("---List incidents for detection configuration...")
    sample_list_incidents_for_detection_configuration()
    print("---List root causes...")
    sample_list_incident_root_cause()
    print("---List incidents for alert configuration...")
    sample_list_incidents_for_alert()

