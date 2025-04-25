# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_capability_host.py
DESCRIPTION:
    These samples configures some operations of the capability host
USAGE:
    python ml_samples_capability_host.py

"""

import os


class CapabilityHostConfigurationOptions(object):
    def ml_capability_host_config(self):

        # [START load_capability_host]
        from azure.ai.ml import load_capability_host

        capability_host = load_capability_host(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/workspace/ai_workspaces/test_capability_host_hub.yml"
        )
        # [END load_capability_host]

        # [START capability_host_object_create]
        from azure.ai.ml.entities._workspace._ai_workspaces.capability_host import (
            CapabilityHost,
        )
        from azure.ai.ml.constants._workspace import CapabilityHostKind

        # CapabilityHost in Hub workspace. For Hub workspace, only name and description are required.
        capability_host = CapabilityHost(
            name="test-capability-host",
            description="some description",
            capability_host_kind=CapabilityHostKind.AGENTS,
        )

        # CapabilityHost in Project workspace
        capability_host = CapabilityHost(
            name="test-capability-host",
            description="some description",
            capability_host_kind=CapabilityHostKind.AGENTS,
            ai_services_connections=["connection1"],
            storage_connections=["projectname/workspaceblobstore"],
            vector_store_connections=["connection1"],
        )
        # [END capability_host_object_create]

        # [START capability_host_begin_create_or_update_operation]
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential
        from azure.ai.ml.entities._workspace._ai_workspaces.capability_host import (
            CapabilityHost,
        )
        from azure.ai.ml.constants._workspace import CapabilityHostKind

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        hub_name = "test-hub"
        project_name = "test-project"

        # Create a CapabilityHost in Hub
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=hub_name,
        )
        capability_host = CapabilityHost(
            name="test-capability-host",
            description="some description",
            capability_host_kind=CapabilityHostKind.AGENTS,
        )
        result = ml_client.capability_hosts.begin_create_or_update(capability_host).result()

        # Create a CapabilityHost in Project
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=project_name,
        )
        capability_host = CapabilityHost(
            name="test-capability-host",
            description="some description",
            capability_host_kind=CapabilityHostKind.AGENTS,
            ai_services_connections=["connection1"],
            storage_connections=["projectname/workspaceblobstore"],
            vector_store_connections=["connection1"],
        )
        result = ml_client.capability_hosts.begin_create_or_update(capability_host).result()
        # [END capability_host_begin_create_or_update_operation]

        # [START capability_host_get_operation]
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        hub_name = "test-hub"
        project_name = "test-project"

        # Get CapabilityHost created in Hub
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=hub_name,
        )
        capability_host = ml_client.capability_hosts.get(name="test-capability-host")

        # Get CapabilityHost created in Project
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=project_name,
        )
        capability_host = ml_client.capability_hosts.get(name="test-capability-host")
        # [END capability_host_get_operation]

        # [START capability_host_delete_operation]
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        hub_name = "test-hub"
        project_name = "test-project"

        # Delete CapabilityHost created in Hub
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=hub_name,
        )
        capability_host = ml_client.capability_hosts.begin_delete(name="test-capability-host")

        # Delete CapabilityHost created in Project
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=project_name,
        )
        capability_host = ml_client.capability_hosts.begin_delete(name="test-capability-host")
        # [END capability_host_delete_operation]

        # [START capability_host_list_operation]
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        hub_name = "test-hub"
        project_name = "test-project"

        # List CapabilityHosts created in Hub
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=hub_name,
        )
        capability_hosts = ml_client.capability_hosts.list()  # type:ignore

        # List CapabilityHosts created in Project
        ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name=project_name,
        )
        capability_hosts = ml_client.capability_hosts.list()  # type:ignore
        # [END capability_host_list_operation]


if __name__ == "__main__":
    sample = CapabilityHostConfigurationOptions()
    sample.ml_capability_host_config()
