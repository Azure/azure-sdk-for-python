# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate with the Azure Metrics Advisor
    service with Subscription key and API key.

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
"""

import os


def authentication_client_with_metrics_advisor_credential():
    # [START authentication_client_with_metrics_advisor_credential]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    # [END authentication_client_with_metrics_advisor_credential]


def authentication_administration_client_with_metrics_advisor_credential():
    # [START administration_client_with_metrics_advisor_credential]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    # [END administration_client_with_metrics_advisor_credential]


if __name__ == '__main__':
    authentication_client_with_metrics_advisor_credential()
    authentication_administration_client_with_metrics_advisor_credential()
