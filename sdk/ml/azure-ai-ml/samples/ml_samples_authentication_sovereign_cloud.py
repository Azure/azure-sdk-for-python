# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_authentication_sovereign_cloud.py

DESCRIPTION:
    These samples demonstrate authenticating a client for multiple clouds.
    
USAGE:
    python ml_samples_authentication_sovereign_cloud.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SUBSCRIPTION_ID - The subscription id.
    2) RESOURCE_GROUP_NAME - Resource group name.

"""

import os


class MLClientSamples(object):
    def ml_auth_azure_default_credential(self):
        # [START create_ml_client_default_credential]
        # Get a credential for authentication
        # Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
        # Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
        # The docs above specify all mechanisms which the defaultCredential internally support.
        # Enter details of your subscription
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]

        # Instantiate a MLClient
        from azure.identity import AzureAuthorityHosts, DefaultAzureCredential

        from azure.ai.ml import MLClient

        # When using sovereign domains (that is, any cloud other than AZURE_PUBLIC_CLOUD),
        # you must use an authority with DefaultAzureCredential.
        # Default authority value : AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
        # Expected values for authority for sovereign clouds:
        # AzureAuthorityHosts.AZURE_CHINA or AzureAuthorityHosts.AZURE_GOVERNMENT
        # credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_CHINA)
        credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_PUBLIC_CLOUD)

        # When using sovereign domains (that is, any cloud other than AZURE_PUBLIC_CLOUD),
        # you must pass in the cloud name in kwargs. Default cloud is AzureCloud
        kwargs = {"cloud": "AzureCloud"}
        # get a handle to the subscription
        ml_client = MLClient(credential, subscription_id, resource_group, **kwargs)
        # [END create_ml_client_default_credential]

        from azure.ai.ml.entities import Workspace

        # Get a list of workspaces in a resource group
        for ws in ml_client.workspaces.list():
            print(ws.name, ":", ws.location, ":", ws.description)


if __name__ == "__main__":
    sample = MLClientSamples()
    sample.ml_auth_azure_default_credential()
