# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py

DESCRIPTION:
    This sample demonstrates how to authenticate with the Azure Metrics Advisor
    service with Subscription key and API key.

USAGE:
    python sample_authentication_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
"""

import os
import asyncio


async def authentication_client_with_metrics_advisor_credential_async():
    # [START authentication_client_with_metrics_advisor_credential_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    # [END authentication_client_with_metrics_advisor_credential_async]


async def authentication_administration_client_with_metrics_advisor_credential_async():
    # [START administration_client_with_metrics_advisor_credential_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    # [END administration_client_with_metrics_advisor_credential_async]


async def authentication_client_with_aad_async():
    # [START authentication_client_with_aad_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    credential = DefaultAzureCredential()
    client = MetricsAdvisorClient(service_endpoint, credential)
    # [END authentication_client_with_aad_async]


async def authentication_administration_client_with_aad_async():
    # [START authentication_administration_client_with_aad_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    credential = DefaultAzureCredential()
    client = MetricsAdvisorAdministrationClient(service_endpoint, credential)
    # [END authentication_administration_client_with_aad_async]


async def main():
    await authentication_client_with_metrics_advisor_credential_async()
    await authentication_administration_client_with_metrics_advisor_credential_async()
    await authentication_client_with_aad_async()
    await authentication_administration_client_with_aad_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
