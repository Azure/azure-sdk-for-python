# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_credential_entities_async.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, update, and delete credential entities
    under your Metrics Advisor account. SqlConnectionStringCredentialEntity is used as an example in this sample.

USAGE:
    python sample_credential_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) SQL_SERVER_CONNECTION_STRING - SQL service connection string
"""

import os
import asyncio


async def sample_create_credential_entity_async():
    # [START create_credential_entity_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import SqlConnectionStringCredentialEntity

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    connection_string = os.getenv("SQL_SERVER_CONNECTION_STRING")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credential_entity = await client.create_credential_entity(
        credential_entity=SqlConnectionStringCredentialEntity(
            name="sql credential entity",
            connection_string=connection_string,
            description="my credential entity",
        )
    )

    return credential_entity
    # [END create_credential_entity_async]


async def sample_get_credential_entity_async(credential_entity_id):
    # [START get_credential_entity_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credential_entity = await client.get_credential_entity(credential_entity_id)

    print("Credential entity type: {}".format(credential_entity.type))
    print("Credential entity name: {}".format(credential_entity.name))
    print("Description: {}".format(credential_entity.description))

    # [END get_credential_entity_async]


async def sample_list_credential_entities_async():
    # [START list_credential_entities_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credential_entities = client.list_credential_entities()
    async for credential_entity in credential_entities:
        print("Credential entity type: {}".format(credential_entity.type))
        print("Credential entity name: {}".format(credential_entity.name))
        print("Description: {}\n".format(credential_entity.description))

    # [END list_credential_entities_async]


async def sample_update_credential_entity_async(credential_entity):
    # [START update_credential_entity_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credential_entity.description = "updated description"

    updated = await client.update_credential_entity(credential_entity)
    print("Credential entity type: {}".format(updated.type))
    print("Credential entity name: {}".format(updated.name))
    print("Description: {}\n".format(updated.description))
    # [END update_credential_entity_async]


async def sample_delete_credential_entity_async(credential_entity_id):
    # [START delete_credential_entity_async]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    await client.delete_credential_entity(credential_entity_id)

    try:
        await client.get_credential_entity(credential_entity_id)
    except ResourceNotFoundError:
        print("Credential entity successfully deleted.")
    # [END delete_credential_entity_async]


async def main():
    print("---Creating credential entity...")
    credential_entity = await sample_create_credential_entity_async()
    print("Credential_entity successfully created...")
    print("\n---Get a credential entity...")
    await sample_get_credential_entity_async(credential_entity.id)
    print("\n---List credential entities...")
    await sample_list_credential_entities_async()
    print("\n---Update a credential entity...")
    await sample_update_credential_entity_async(credential_entity)
    print("\n---Delete a credential entity...")
    await sample_delete_credential_entity_async(credential_entity.id)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())