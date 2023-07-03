# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_authentication.py

DESCRIPTION:
    These samples demonstrate authenticating a client for multiple clouds.
    
USAGE:
    python ml_samples_authentication.py

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

        # [START ml_client_create_or_update]
        from azure.ai.ml.entities import AmlTokenConfiguration, command

        command_job = command(
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs=inputs,
            code="./tests/test_configs/training/",
            command="echo ${{inputs.uri}} ${{inputs.data_asset}} ${{inputs.local_data}}",
            display_name="builder_command_job",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
            identity=AmlTokenConfiguration(),
        )
        created_job = client.create_or_update(command_job)
        # [END ml_client_create_or_update]

        # [START ml_client_begin_create_or_update]
        from azure.ai.ml.entities import ManagedOnlineEndpoint

        endpoint = ManagedOnlineEndpoint(
            name="online_endpoint_name",
            description="this is a sample online endpoint",
            auth_mode="key",
        )
        created_job = client.begin_create_or_update(endpoint)
        # [END ml_client_begin_create_or_update]

        # [START user_identity_configuration]
        from azure.ai.ml import Input, command
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.entities import UserIdentityConfiguration

        job = command(
            code="./src",
            command="python read_data.py --input_data ${{inputs.input_data}}",
            inputs={"input_data": Input(type=AssetTypes.MLTABLE, path="./sample_data")},
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:1",
            compute="cpu-cluster",
            identity=UserIdentityConfiguration(),
        )
        # [END user_identity_configuration]

        # [START aml_token_configuration]
        from azure.ai.ml import Input, command
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.entities import AmlTokenConfiguration

        node = command(
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            code="./tests/test_configs/training/",
            command="python read_data.py --input_data ${{inputs.input_data}}",
            inputs={"input_data": Input(type=AssetTypes.MLTABLE, path="./sample_data")},
            display_name="builder_command_job",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
            identity=AmlTokenConfiguration(),
        )
        # [END aml_token_configuration]

        # Get a list of workspaces in a resource group
        for ws in ml_client.workspaces.list():
            print(ws.name, ":", ws.location, ":", ws.description)


if __name__ == "__main__":
    sample = MLClientSamples()
    sample.ml_auth_azure_default_credential()
