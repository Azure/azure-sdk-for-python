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
        workspace_name = "test-ws1"

        # [START create_ml_client_default_credential]
        from azure.ai.ml import MLClient
        from azure.identity import AzureAuthorityHosts, DefaultAzureCredential

        ml_client = MLClient(
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            credential=DefaultAzureCredential(),
        )
        # [END create_ml_client_default_credential]

        # [START create_ml_client_from_config_default]
        from azure.ai.ml import MLClient

        client = MLClient.from_config(credential=DefaultAzureCredential(), path="./sdk/ml/azure-ai-ml/samples/src")
        # [END create_ml_client_from_config_default]

        # [START create_ml_client_from_config_custom_filename]
        from azure.ai.ml import MLClient

        client = MLClient.from_config(
            credential=DefaultAzureCredential(),
            file_name="./sdk/ml/azure-ai-ml/samples/team_workspace_configuration.json",
        )
        # [END create_ml_client_from_config_custom_filename]

        # [START ml_client_create_or_update]
        from azure.ai.ml import Input, command
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.entities import ManagedOnlineEndpoint, UserIdentityConfiguration

        client = MLClient(
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            credential=DefaultAzureCredential(),
        )
        job = command(
            code="./sdk/ml/azure-ai-ml/samples/src",
            command="echo hello world",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:1",
            compute="cpu-cluster",
            identity=UserIdentityConfiguration(),
        )

        client.create_or_update(job)
        # [END ml_client_create_or_update]

        # [START ml_client_begin_create_or_update]
        from random import randint

        from azure.ai.ml.entities import ManagedOnlineEndpoint

        client = MLClient(
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            credential=DefaultAzureCredential(),
        )
        endpoint = ManagedOnlineEndpoint(
            name=f"online-endpoint-name-{randint(1, 1000)}",
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
            code="./sdk/ml/azure-ai-ml/samples/src",
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
        from azure.ai.ml.entities._credentials import AmlTokenConfiguration

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

        # [START create_ml_client_sovereign_cloud]
        from azure.ai.ml import MLClient
        from azure.identity import AzureAuthorityHosts, DefaultAzureCredential

        kwargs = {"cloud": "AzureChinaCloud"}
        ml_client = MLClient(
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            credential=DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_CHINA),
            **kwargs,
        )
        # [END create_ml_client_sovereign_cloud]


if __name__ == "__main__":
    sample = MLClientSamples()
    sample.ml_auth_azure_default_credential()
