# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_compute_configurations.py
DESCRIPTION:
    These samples demonstrate different ways to configure Compute.
USAGE:
    python ml_samples_compute_configurations.py

"""

import os
from random import randint

from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential


def handle_resource_exists_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ResourceExistsError, ResourceNotFoundError) as e:
            pass

    return wrapper


subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["RESOURCE_GROUP_NAME"]
workspace_name = "test-ws1"
credential = DefaultAzureCredential()
ml_client = MLClient(credential, subscription_id, resource_group, workspace_name=workspace_name)

compute_name_1 = f"compute-{randint(1, 1000)}-sample"
compute_name_2 = f"compute-{randint(1, 1000)}-sample"
ci_name = f"ci-{randint(1, 1000)}-sample"


class ComputeConfigurationOptions(object):
    @handle_resource_exists_error
    def ml_compute_config_setup_0(self):
        # [START compute_instance]
        from azure.ai.ml.entities import ComputeInstance

        ci = ComputeInstance(
            name=ci_name,
            size="Standard_DS2_v2",
        )
        ml_client.compute.begin_create_or_update(ci)
        # [END compute_instance]

    @handle_resource_exists_error
    def ml_compute_config_setup_1(self):
        # [START compute_operations_get]
        cpu_cluster = ml_client.compute.get("cpu-cluster")
        # [END compute_operations_get]

        # [START load_compute]
        from azure.ai.ml import load_compute

        compute = load_compute(
            "../tests/test_configs/compute/compute-vm.yaml",
            params_override=[{"description": "loaded from compute-vm.yaml"}],
        )
        # [END load_compute]

        # [START compute_operations_list]
        compute_list = ml_client.compute.list(compute_type="AMLK8s")  # cspell:disable-line
        # [END compute_operations_list]

        # [START compute_operations_list_nodes]
        node_list = ml_client.compute.list_nodes(name="cpu-cluster")
        # [END compute_operations_list_nodes]

    @handle_resource_exists_error
    def ml_compute_config_setup_2(self):
        # [START compute_operations_create_update]
        from azure.ai.ml.entities import AmlCompute

        compute_obj = AmlCompute(
            name=compute_name_1,
            tags={"key1": "value1", "key2": "value2"},
            min_instances=0,
            max_instances=10,
            idle_time_before_scale_down=100,
        )
        registered_compute = ml_client.compute.begin_create_or_update(compute_obj)
        # [END compute_operations_create_update]

    @handle_resource_exists_error
    def ml_compute_config_setup_3(self):
        # [START compute_operations_attach]
        from azure.ai.ml.entities import AmlCompute

        compute_obj = AmlCompute(
            name=compute_name_2,
            tags={"key1": "value1", "key2": "value2"},
            min_instances=0,
            max_instances=10,
            idle_time_before_scale_down=100,
        )
        attached_compute = ml_client.compute.begin_attach(compute_obj)
        # [END compute_operations_attach]

        # [START compute_operations_update]
        compute_obj = ml_client.compute.get("cpu-cluster")
        compute_obj.idle_time_before_scale_down = 200
        updated_compute = ml_client.compute.begin_update(compute_obj)
        # [END compute_operations_update]

        # [START compute_operations_list_usage]
        usage_list = ml_client.compute.list_usage()
        # [END compute_operations_list_usage]

        # [START compute_operations_list_sizes]
        size_list = ml_client.compute.list_sizes()
        # [END compute_operations_list_sizes]

        # [START amlcompute]
        from azure.ai.ml.entities import AmlCompute, IdentityConfiguration, ManagedIdentityConfiguration

        aml_compute = AmlCompute(
            name="my-aml-compute",
            min_instances=0,
            max_instances=10,
            idle_time_before_scale_down=100,
            identity=IdentityConfiguration(
                type="UserAssigned",
                user_assigned_identities=[
                    ManagedIdentityConfiguration(
                        resource_id="/subscriptions/1234567-abcd-ef12-1234-12345/resourcegroups/our_rg_eastus/providers/Microsoft.ManagedIdentity/userAssignedIdentities/our-agent-aks"
                    )
                ],
            ),
        )
        # [END amlcompute]

        # [START aml_compute_ssh_settings]
        from azure.ai.ml.entities import AmlComputeSshSettings

        ssh_settings = AmlComputeSshSettings(
            admin_username="azureuser",
            ssh_key_value="ssh-rsa ABCDEFGHIJKLMNOPQRSTUVWXYZ administrator@MININT-2023",
            admin_password="password123",
        )
        # [END aml_compute_ssh_settings]

        # [START compute_instance_ssh_settings]
        from azure.ai.ml.entities import ComputeInstanceSshSettings

        ssh_settings = ComputeInstanceSshSettings(
            ssh_key_value="ssh-rsa ABCDEFGHIJKLMNOPQRSTUVWXYZ administrator@MININT-2023"
        )
        # [END compute_instance_ssh_settings]

        # [START assigned_user_configuration]
        from azure.ai.ml.entities import AssignedUserConfiguration

        on_behalf_of_config = AssignedUserConfiguration(user_tenant_id="12345", user_object_id="abcdef")
        # [END assigned_user_configuration]

        # [START compute_operations_stop]
        ml_client.compute.begin_stop(ci_name)
        # [END compute_operations_stop]

        # [START compute_operations_start]
        ml_client.compute.begin_start(ci_name)
        # [END compute_operations_start]

        # [START vm_ssh_settings]
        from azure.ai.ml.entities import VirtualMachineSshSettings

        ssh_settings = VirtualMachineSshSettings(
            admin_username="azureuser",
            admin_password="azureuserpassword",
            ssh_port=8888,
            ssh_private_key_file="../tests/test_configs/compute/ssh_fake_key.txt",
        )
        # [END vm_ssh_settings]

        # [START vm_compute]
        from azure.ai.ml.entities import VirtualMachineCompute

        vm_compute = VirtualMachineCompute(
            name="vm-compute",
            resource_id="/subscriptions/123456-1234-1234-1234-123456789/resourceGroups/my-rg/providers/Microsoft.Compute/virtualMachines/my-vm",
            ssh_settings=ssh_settings,
        )
        # [END vm_compute]

        # [START network_settings]
        from azure.ai.ml.entities import (
            AmlCompute,
            IdentityConfiguration,
            ManagedIdentityConfiguration,
            NetworkSettings,
        )

        aml_compute = AmlCompute(
            name="my-compute",
            min_instances=0,
            max_instances=10,
            idle_time_before_scale_down=100,
            network_settings=NetworkSettings(vnet_name="my-vnet", subnet="default"),
        )
        # [END network_settings]

        # [START compute_runtime]
        from azure.ai.ml.entities import ComputeRuntime

        compute_runtime = ComputeRuntime(spark_runtime_version="3.3.0")
        # [END compute_runtime]

        # [START compute_start_stop_schedule]
        from azure.ai.ml.constants import TimeZone
        from azure.ai.ml.entities import ComputeSchedules, ComputeStartStopSchedule, CronTrigger

        start_stop = ComputeStartStopSchedule(
            trigger=CronTrigger(
                expression="15 10 * * 1",
                start_time="2022-03-10 10:15:00",
                end_time="2022-06-10 10:15:00",
                time_zone=TimeZone.PACIFIC_STANDARD_TIME,
            )
        )
        compute_schedules = ComputeSchedules(compute_start_stop=[start_stop])

        # [END compute_start_stop_schedule]

        # [START image_metadata]
        from azure.ai.ml.entities import ImageMetadata

        os_image_metadata = ImageMetadata(
            current_image_version="22.08.19",
            latest_image_version="22.08.20",
            is_latest_os_image_version=False,
        )
        # [END image_metadata]

        # [START kubernetes_compute]
        from azure.ai.ml.entities import KubernetesCompute

        k8s_compute = KubernetesCompute(
            identity=IdentityConfiguration(
                type="UserAssigned",
                user_assigned_identities=[
                    ManagedIdentityConfiguration(
                        resource_id="/subscriptions/1234567-abcd-ef12-1234-12345/resourcegroups/our_rg_eastus/providers/Microsoft.ManagedIdentity/userAssignedIdentities/our-agent-aks"
                    )
                ],
            ),
        )
        # [END kubernetes_compute]

        # [START materialization_compute_resource]
        from azure.ai.ml.entities import MaterializationComputeResource

        materialization_compute = MaterializationComputeResource(instance_type="standard_e4s_v3")
        # [END materialization_compute_resource]

        # [START compute_operations_restart]
        ml_client.compute.begin_restart(ci_name)
        # [END compute_operations_restart]

        # [START compute_operations_delete]
        ml_client.compute.begin_delete(compute_name_1, action="Detach")

        ml_client.compute.begin_delete(compute_name_2)
        # [END compute_operations_delete]


if __name__ == "__main__":
    sample = ComputeConfigurationOptions()
    sample.ml_compute_config_setup_0()
    sample.ml_compute_config_setup_1()
    sample.ml_compute_config_setup_2()
    sample.ml_compute_config_setup_3()
