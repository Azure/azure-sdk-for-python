# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_datasource_credentials.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, update, and delete datasource credentials
    under your Metrics Advisor account. DatasourceSqlConnectionString is used as an example in this sample.

USAGE:
    python sample_datasource_credentials.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) SQL_SERVER_CONNECTION_STRING - SQL service connection string
"""

import os


def sample_create_datasource_credential():
    # [START create_datasource_credential]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import DatasourceSqlConnectionString

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    connection_string = os.getenv("SQL_SERVER_CONNECTION_STRING")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credential = client.create_datasource_credential(
        datasource_credential=DatasourceSqlConnectionString(
            name="sql datasource credential",
            connection_string=connection_string,
            description="my datasource credential",
        )
    )

    return credential
    # [END create_datasource_credential]


def sample_get_datasource_credential(credential_id):
    # [START get_datasource_credential]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credential = client.get_datasource_credential(credential_id)

    print("Credential type: {}".format(credential.credential_type))
    print("Credential name: {}".format(credential.name))
    print("Description: {}".format(credential.description))

    # [END get_datasource_credential]


def sample_list_datasource_credentials():
    # [START list_datasource_credentials]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    credentials = client.list_datasource_credentials()
    for credential in credentials:
        print("Credential type: {}".format(credential.credential_type))
        print("Credential name: {}".format(credential.name))
        print("Description: {}\n".format(credential.description))

    # [END list_datasource_credentials]


def sample_update_datasource_credential(datasource_credential):
    # [START update_datasource_credential]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    datasource_credential.description = "updated description"

    updated = client.update_datasource_credential(datasource_credential)
    print("Credential type: {}".format(updated.credential_type))
    print("Credential name: {}".format(updated.name))
    print("Description: {}\n".format(updated.description))
    # [END update_datasource_credential]


def sample_delete_datasource_credential(credential_id):
    # [START delete_datasource_credential]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    client.delete_datasource_credential(credential_id)
    # [END delete_datasource_credential]


if __name__ == '__main__':
    print("---Creating datasource credential...")
    credential = sample_create_datasource_credential()
    print("Datasource credential successfully created...")
    print("\n---Get a datasource credential...")
    sample_get_datasource_credential(credential.id)
    print("\n---List datasource credentials...")
    sample_list_datasource_credentials()
    print("\n---Update a datasource credential...")
    sample_update_datasource_credential(credential)
    print("\n---Delete a datasource credential...")
    sample_delete_datasource_credential(credential.id)