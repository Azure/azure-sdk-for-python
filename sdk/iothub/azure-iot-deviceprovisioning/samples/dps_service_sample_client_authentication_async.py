# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: dps_service_sample_client_authentication_async.py
DESCRIPTION:
    These samples demonstrate authenticating a client via a connection string,
    shared access key, or by generating a sas token with which the returned signature
    can be used with the credential parameter of any DeviceProvisioningClient
USAGE:
    python dps_service_sample_client_authentication_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_DPS_CONNECTION_STRING - the connection string to your storage account
    2) ACTIVE_DIRECTORY_APPLICATION_ID - Azure Active Directory application ID
    3) ACTIVE_DIRECTORY_APPLICATION_SECRET - Azure Active Directory application secret
    4) ACTIVE_DIRECTORY_TENANT_ID - Azure Active Directory tenant ID
"""

import asyncio
from os import environ

from azure.core.utils import parse_connection_string


class ClientAuthSamples(object):
    connection_string = environ["AZURE_DPS_CONNECTION_STRING"]
    conn_str_parts = parse_connection_string(connection_string)
    endpoint = conn_str_parts["hostname"]

    active_directory_application_id = environ["ACTIVE_DIRECTORY_APPLICATION_ID"]
    active_directory_application_secret = environ["ACTIVE_DIRECTORY_APPLICATION_SECRET"]
    active_directory_tenant_id = environ["ACTIVE_DIRECTORY_TENANT_ID"]

    async def auth_connection_string_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

    async def auth_named_key_async(self):
        # Instantiate a DPS Service Client using a named key credential
        from azure.core.credentials import AzureNamedKeyCredential
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        # Parse policy components from connection string parts
        policy_name = self.conn_str_parts["sharedaccesskeyname"]
        policy = self.conn_str_parts["sharedaccesskey"]

        # Create AzureNamedKeyCredential object
        credential = AzureNamedKeyCredential(name=policy_name, key=policy)

        dps_service_client = DeviceProvisioningClient(
            endpoint=self.endpoint, credential=credential
        )

    async def auth_active_directory_async(self):
        # Instantiate a DPS Service Client using a named key credential
        from azure.identity.aio import ClientSecretCredential
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        # Get a token credential for authentication
        credential = ClientSecretCredential(
            self.active_directory_tenant_id,
            self.active_directory_application_id,
            self.active_directory_application_secret,
        )

        dps_service_client = DeviceProvisioningClient(
            endpoint=self.endpoint, credential=credential  # type: ignore
        )

    async def auth_sas_token_async(self):
        # Instantiate a DPS Service Client using a generated SAS token
        from azure.core.credentials import AzureSasCredential
        from azure.iot.deviceprovisioning import generate_sas_token
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        # Parse policy components from connection string
        policy_name = self.conn_str_parts["sharedaccesskeyname"]
        policy = self.conn_str_parts["sharedaccesskey"]

        # Generate SAS token (default TTL is 3600 ms, or 1 hour)
        sas_token = generate_sas_token(self.endpoint, policy_name, policy)

        # Create AzureSasCredential object
        credential = AzureSasCredential(signature=sas_token)

        dps_service_client = DeviceProvisioningClient(
            endpoint=self.endpoint, credential=credential
        )

    async def auth_default_azure_credential_async(self):
        # Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
        # For example, the user to be logged in can be specified by the environment variable AZURE_USERNAME
        # Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
        # The docs above specify all mechanisms which the defaultCredential internally support.
        from azure.identity.aio import DefaultAzureCredential
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        # Instantiate a DefaultAzureCredential
        credential = DefaultAzureCredential()

        dps_service_client = DeviceProvisioningClient(
            endpoint=self.endpoint, credential=credential  # type: ignore
        )


async def main():
    sample = ClientAuthSamples()
    await sample.auth_connection_string_async()
    await sample.auth_named_key_async()
    await sample.auth_active_directory_async()
    await sample.auth_sas_token_async()
    await sample.auth_default_azure_credential_async()


if __name__ == "__main__":
    asyncio.run(main())
