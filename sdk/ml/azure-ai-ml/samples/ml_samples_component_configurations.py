# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_component_configurations.py
DESCRIPTION:
    These samples configures some operations of the component
USAGE:
    python ml_samples_component_configurations.py

"""

import os


class ComponentConfigurationOptions(object):
    def ml_component_config(self):
        from azure.ai.ml import MLClient
        from azure.ai.ml.entities import Environment
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        workspace_name = "test-ws1"
        credential = DefaultAzureCredential()
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name=workspace_name)
        cpu_cluster = ml_client.compute.get("cpu-cluster")
        job_env = Environment(
            name="my-env",
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
        )
        job_env = ml_client.environments.create_or_update(job_env)

        # [START configure_load_component]
        from azure.ai.ml import load_component

        component = load_component(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/components/helloworld_component.yml",
            params_override=[{"version": "1.0.2"}],
        )
        registered_component = ml_client.components.create_or_update(component)
        # [END configure_load_component]


if __name__ == "__main__":
    sample = ComponentConfigurationOptions()
    sample.ml_component_config()
