# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_datasource_credentials_async.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, update, and delete datasource credentials
    under your Metrics Advisor account. DatasourceSqlConnectionString is used as an example in this sample.

USAGE:
    python sample_datasource_credentials_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) SQL_SERVER_CONNECTION_STRING - SQL service connection string
"""

import os
import asyncio


async def sample_create_datasource_credential_async():
    # [START create_datasource_credential_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import DatasourceSqlConnectionString

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    connection_string = os.getenv("SQL_SERVER_CONNECTION_STRING")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    datasource_credential = await client.create_datasource_credential(
        datasource_credential=DatasourceSqlConnectionString(
            name="sql datasource credential",
            connection_string=connection_string,
            description="my datasource credential",
        )
    )

    return datasource_credential
    # [END create_datasource_credential_async]


async def sample_get_datasource_credential_async(credential_id):
    # [START get_datasource_credential_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credential = await client.get_datasource_credential(credential_id)

    print("Credential type: {}".format(credential.credential_type))
    print("Credential name: {}".format(credential.name))
    print("Description: {}".format(credential.description))

    # [END get_datasource_credential_async]


async def sample_list_datasource_credentials_async():
    # [START list_datasource_credentials_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credentials = client.list_datasource_credentials()
    async for credential in credentials:
        print("Credential type: {}".format(credential.credential_type))
        print("Credential name: {}".format(credential.name))
        print("Description: {}\n".format(credential.description))

    # [END list_datasource_credentials_async]


async def sample_update_datasource_credential_async(datasource_credential):
    # [START update_datasource_credential_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    datasource_credential.description = "updated description"

    updated = await client.update_datasource_credential(datasource_credential)
    print("Credential type: {}".format(updated.credential_type))
    print("Credential name: {}".format(updated.name))
    print("Description: {}\n".format(updated.description))
    # [END update_datasource_credential_async]


async def sample_delete_datasource_credential_async(credential_id):
    # [START delete_datasource_credential_async]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    await client.delete_datasource_credential(credential_id)
    # [END delete_datasource_credential_async]


async def main():
    print("---Creating datasource credential...")
    credential = await sample_create_datasource_credential_async()
    print("Datasource credential successfully created...")
    print("\n---Get a datasource credential...")
    await sample_get_datasource_credential_async(credential.id)
    print("\n---List datasource credentials...")
    await sample_list_datasource_credentials_async()
    print("\n---Update a datasource credential...")
    await sample_update_datasource_credential_async(credential)
    print("\n---Delete a datasource credential...")
    await sample_delete_datasource_credential_async(credential.id)

if __name__ == '__main__':
    asyncio.run(main())
