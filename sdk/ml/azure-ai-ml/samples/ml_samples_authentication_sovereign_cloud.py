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
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]

        # [START create_ml_client_default_credential]
        from azure.identity import AzureAuthorityHosts, DefaultAzureCredential

        from azure.ai.ml import MLClient

        ml_client = MLClient(subscription_id, resource_group, credential=DefaultAzureCredential())
        # [END create_ml_client_default_credential]

        # [START create_ml_client_sovereign_cloud]
        from azure.identity import AzureAuthorityHosts, DefaultAzureCredential

        from azure.ai.ml import MLClient

        kwargs = {"cloud": "AzureChinaCloud"}
        ml_client = MLClient(
            subscription_id,
            resource_group,
            credential=DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_CHINA),
            **kwargs
        )
        # [END create_ml_client_sovereign_cloud]

        # [START create_ml_client_from_config_default]
        from azure.ai.ml import MLClient

        client = MLClient.from_config(credential=DefaultAzureCredential(), path="src")
        # [END create_ml_client_from_config_default]

        # [START create_ml_client_from_config_custom_filename]
        from azure.ai.ml import MLClient

        client = MLClient.from_config(
            credential=DefaultAzureCredential(), file_name="team_workspace_configuration.json"
        )
        # [END create_ml_client_from_config_custom_filename]

        from azure.ai.ml.entities import Workspace

        # Get a list of workspaces in a resource group
        for ws in ml_client.workspaces.list():
            print(ws.name, ":", ws.location, ":", ws.description)


if __name__ == "__main__":
    sample = MLClientSamples()
    sample.ml_auth_azure_default_credential()
