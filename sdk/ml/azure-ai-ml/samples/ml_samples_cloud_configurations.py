# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_cloud_configurations.py
DESCRIPTION:
    These samples demonstrate different ways to configure clouds for the MLClient.
USAGE:
    python ml_samples_cloud_configurations.py

"""

import os
from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import ArmConstants
from azure.ai.ml.constants._common import AZUREML_CLOUD_ENV_NAME
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential


class CloudConfigurationOptions(object):
    def ml_cloud_config_from_environment_arm(self):
        subscription_id = "AZURE_SUBSCRIPTION_ID"
        resource_group = "RESOURCE_GROUP_NAME"
        credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_PUBLIC_CLOUD)

        # This environment variable should be set when running python.  If it is set, and the configured cloud is not
        # one of the default ones in _azure_environments.py, it will follow the url to find the cloud config.  If it
        # does not find it anywhere, it will throw an "Unknown cloud environment" error.
        os.environ[ArmConstants.METADATA_URL_ENV_NAME] = (
            "https://management.azure.com/metadata/endpoints?api-version=2019-05-01"
        )
        kwargs = {"cloud": "AzureCloud"}

        ml_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name="test-ws1",
            **kwargs,
        )
        # The client will use the cloud that we passed in
        print("Client is using cloud:", ml_client._cloud)
        # In specifying this cloud, we've also set the environment variable to match it
        print("Cloud name environment variable:", os.environ[AZUREML_CLOUD_ENV_NAME])

    def ml_cloud_config_from_keyword_args(self):
        subscription_id = "AZURE_SUBSCRIPTION_ID"
        resource_group = "RESOURCE_GROUP_NAME"
        credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_PUBLIC_CLOUD)

        # All of these configurations are needed in the kwargs, otherwise the SDK will not recognize the configuration
        # and will throw an "Unknown cloud environment" error.
        kwargs = {
            "cloud": "TestCloud",
            "cloud_metadata": {
                "azure_portal": "https://test.portal.azure.com/",
                "resource_manager": "https://test.management.azure.com/",
                "active_directory": "https://test.login.microsoftonline.com/",
                "aml_resource_id": "https://test.ml.azure.com/",
                "storage_endpoint": "test.core.windows.net",
                "registry_discovery_endpoint": "https://test.eastus.api.azureml.ms/",
            },
        }
        ml_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name="test-ws1",
            **kwargs,
        )
        # The client will use the cloud that we passed in
        print("Client is using cloud:", ml_client._cloud)
        # In configuring this cloud, we've also set the environment variable to match it
        print("Cloud name environment variable:", os.environ[AZUREML_CLOUD_ENV_NAME])


if __name__ == "__main__":
    sample = CloudConfigurationOptions()
    sample.ml_cloud_config_from_environment_arm()
    sample.ml_cloud_config_from_keyword_args()
