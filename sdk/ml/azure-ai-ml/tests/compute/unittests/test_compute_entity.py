from typing import List, Union

import pytest
import yaml
from msrest import Serializer
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_compute
from azure.ai.ml._restclient.v2022_10_01_preview.models import ComputeResource
from azure.ai.ml.entities import (
    AmlCompute,
    Compute,
    ComputeInstance,
    KubernetesCompute,
    SynapseSparkCompute,
    VirtualMachineCompute,
    ManagedIdentityConfiguration,
)


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestComputeEntity:
    def test_compute_from_rest(self):
        with open("tests/test_configs/compute/compute-kubernetes.yaml", "r") as f:
            data = yaml.safe_load(f)
        resource_id = "/subscriptions/dummy/resourceGroups/dummy/providers/Microsoft.Kubernetes/connectedClusters/dummy"
        uai_resource_id = "/subscriptions/dummy/resourceGroups/dummy/providers/Microsoft.ManagedIdentity/userAssignedIdentities/dummy"
        context = {
            "base_path": "./",
            "params_override": [
                {
                    "resource_id": resource_id,
                    "name": "dummy",
                    "namespace": "default",
                    "identity": {
                        "type": "user_assigned",
                        "user_assigned_identities": [{"resource_id": uai_resource_id}],
                    },
                }
            ],
        }
        compute = KubernetesCompute._load_from_dict(data, context)
        compute._to_rest_object()
        assert compute.type == "kubernetes"
        assert compute.identity.type == "user_assigned"
        assert (
            compute.identity.user_assigned_identities[0].resource_id == uai_resource_id
        )

    def _test_loaded_compute(self, compute: AmlCompute):
        assert compute.name == "banchaml"
        assert compute.ssh_settings.admin_username == "azureuser"
        assert compute.identity.type == "user_assigned"

    def test_compute_from_yaml(self):
        compute: AmlCompute = verify_entity_load_and_dump(
            load_compute,
            self._test_loaded_compute,
            "tests/test_configs/compute/compute-aml.yaml",
        )[0]

        rest_intermediate = compute._to_rest_object()
        assert rest_intermediate.properties.compute_type == "AmlCompute"
        assert (
            rest_intermediate.properties.properties.user_account_credentials.admin_user_name
            == "azureuser"
        )
        assert rest_intermediate.properties.properties.enable_node_public_ip

        serializer = Serializer({"ComputeResource": ComputeResource})
        body = serializer.body(rest_intermediate, "ComputeResource")
        assert body["identity"]["type"] == "UserAssigned"
        assert body["identity"]["userAssignedIdentities"] == self._uai_list_to_dict(
            compute.identity.user_assigned_identities
        )

    def test_compute_vm_from_yaml(self):
        resource_id = "/subscriptions/13e50845-67bc-4ac5-94db-48d493a6d9e8/resourceGroups/myrg/providers/Microsoft.Compute/virtualMachines/myvm"
        fake_key = "myfakekey"
        compute: VirtualMachineCompute = load_compute(
            "tests/test_configs/compute/compute-vm.yaml"
        )
        assert compute.name == "banchcivm"
        assert compute.ssh_settings.admin_username == "azureuser"
        assert compute.ssh_settings.admin_password == "azureuserpassword"
        assert compute.ssh_settings.ssh_port == 8888
        assert compute.resource_id == resource_id
        assert (
            compute.ssh_settings.ssh_private_key_file
            == "tests/test_configs/compute/ssh_fake_key.txt"
        )

        rest_intermediate = compute._to_rest_object()
        assert rest_intermediate.properties.resource_id == resource_id
        assert rest_intermediate.properties.properties.ssh_port == 8888
        assert (
            rest_intermediate.properties.properties.administrator_account.password
            == "azureuserpassword"
        )
        assert (
            rest_intermediate.properties.properties.administrator_account.username
            == "azureuser"
        )
        assert (
            rest_intermediate.properties.properties.administrator_account.private_key_data
            == fake_key
        )

        serializer = Serializer({"ComputeResource": ComputeResource})
        body = serializer.body(rest_intermediate, "ComputeResource")
        assert body["properties"]["resourceId"] == resource_id
        assert body["properties"]["properties"]["sshPort"] == 8888
        assert (
            body["properties"]["properties"]["administratorAccount"]["username"]
            == "azureuser"
        )
        assert (
            body["properties"]["properties"]["administratorAccount"]["password"]
            == "azureuserpassword"
        )
        assert (
            body["properties"]["properties"]["administratorAccount"]["privateKeyData"]
            == fake_key
        )

    def test_compute_from_constructor(self):
        compute = ComputeInstance(name="comp", type="computeinstance")
        assert compute.type == "computeinstance"

        compute = KubernetesCompute(name="mykube", namespace="default", properties={})
        compute._to_dict()
        assert compute.type == "kubernetes"

    def _uai_list_to_dict(
        self, value: List[ManagedIdentityConfiguration]
    ) -> Union[str, ManagedIdentityConfiguration]:
        uai_dict = {}

        for item in value:
            resource_id = item.resource_id
            uai_dict[resource_id] = {}
        return uai_dict

    def test_compute_instance_load_from_rest(self):
        compute_instance: ComputeInstance = load_compute(
            "tests/test_configs/compute/compute-ci-unit.yaml"
        )
        compute_instance._set_full_subnet_name("subscription_id", "resource_group_name")
        compute_resource = compute_instance._to_rest_object()
        compute_instance2: ComputeInstance = ComputeInstance._load_from_rest(
            compute_resource
        )
        assert compute_instance.last_operation == compute_instance2.last_operation
        assert compute_instance.services == compute_instance2.services

    def test_compute_instance_schedules_from_yaml(self):
        compute_instance: ComputeInstance = load_compute(
            "tests/test_configs/compute/compute-ci-schedules.yaml"
        )
        assert len(compute_instance.schedules.compute_start_stop) == 2

        compute_resource = compute_instance._to_rest_object()
        compute_instance2: ComputeInstance = ComputeInstance._load_from_rest(
            compute_resource
        )
        assert len(compute_instance2.schedules.compute_start_stop) == 2
        assert compute_instance2.schedules.compute_start_stop[0].action == "stop"
        assert compute_instance2.schedules.compute_start_stop[0].trigger.type == "Cron"
        assert (
            compute_instance2.schedules.compute_start_stop[0].trigger.start_time
            == "2021-03-10T21:21:07"
        )
        assert (
            compute_instance2.schedules.compute_start_stop[0].trigger.time_zone
            == "Pacific Standard Time"
        )
        assert (
            compute_instance2.schedules.compute_start_stop[0].trigger.expression
            == "0 18 * * *"
        )
        assert compute_instance2.schedules.compute_start_stop[1].action == "start"
        assert (
            compute_instance2.schedules.compute_start_stop[1].trigger.type
            == "Recurrence"
        )
        assert (
            compute_instance2.schedules.compute_start_stop[1].trigger.start_time
            == "2021-03-10T21:21:07"
        )
        assert (
            compute_instance2.schedules.compute_start_stop[1].trigger.time_zone
            == "Pacific Standard Time"
        )
        assert (
            compute_instance2.schedules.compute_start_stop[1].trigger.frequency
            == "week"
        )
        assert compute_instance2.schedules.compute_start_stop[1].trigger.interval == 1
        assert (
            compute_instance2.schedules.compute_start_stop[1].trigger.schedule
            is not None
        )

    def test_compute_instance_idle_shutdown_from_yaml(self):
        compute_instance: ComputeInstance = load_compute(
            "tests/test_configs/compute/compute-ci-idle-shutdown.yaml"
        )
        assert compute_instance.idle_time_before_shutdown == "PT20M"
        assert compute_instance.idle_time_before_shutdown_minutes == 15

        compute_resource = compute_instance._to_rest_object()
        assert (
            compute_resource.properties.properties.idle_time_before_shutdown
            == f"PT{compute_instance.idle_time_before_shutdown_minutes}M"
        )

        compute_instance2: ComputeInstance = ComputeInstance._load_from_rest(
            compute_resource
        )
        assert (
            compute_instance2.idle_time_before_shutdown
            == f"PT{compute_instance.idle_time_before_shutdown_minutes}M"
        )
        assert (
            compute_instance2.idle_time_before_shutdown_minutes
            == compute_instance.idle_time_before_shutdown_minutes
        )

    def test_compute_instance_setup_scripts_from_yaml(self):
        loaded_instance: ComputeInstance = load_compute(
            "tests/test_configs/compute/compute-ci-setup-scripts.yaml"
        )
        compute_resource: ComputeResource = loaded_instance._to_rest_object()
        compute_instance: ComputeInstance = ComputeInstance._load_from_rest(
            compute_resource
        )

        assert compute_instance.setup_scripts is not None
        assert compute_instance.setup_scripts.creation_script is not None
        assert (
            compute_instance.setup_scripts.creation_script.path
            == "Users/test/creation-script.sh"
        )
        assert compute_instance.setup_scripts.creation_script.timeout_minutes == "20"
        assert compute_instance.setup_scripts.startup_script is not None
        assert (
            compute_instance.setup_scripts.startup_script.path
            == "Users/test/startup-script.sh"
        )
        assert compute_instance.setup_scripts.startup_script.command == "ls"
        assert compute_instance.setup_scripts.startup_script.timeout_minutes == "15"

    def test_compute_instance_uai_from_yaml(self):
        compute: ComputeInstance = load_compute(
            "tests/test_configs/compute/compute-ci-uai.yaml"
        )
        assert compute.name == "banchci"
        assert compute.type == "computeinstance"
        assert compute.identity.type == "user_assigned"
        assert compute.identity.user_assigned_identities
        assert len(compute.identity.user_assigned_identities) == 1
        assert (
            compute.identity.user_assigned_identities[0].resource_id
            == "/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/test-rg-centraluseuap-v2-t-2021W35"
            "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/x"
        )

        compute_resource = compute._to_rest_object()
        assert compute_resource.identity.type == "UserAssigned"
        assert len(compute_resource.identity.user_assigned_identities) == 1
        for k in compute_resource.identity.user_assigned_identities.keys():
            assert (
                k
                == "/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/test-rg"
                "-centraluseuap-v2-t-2021W35/providers/Microsoft.ManagedIdentity"
                "/userAssignedIdentities/x"
            )

        compute_from_rest = Compute._from_rest_object(compute_resource)
        assert compute_from_rest.type == "computeinstance"
        assert compute_from_rest.identity.type == "user_assigned"
        assert compute_from_rest.identity.user_assigned_identities
        assert len(compute_from_rest.identity.user_assigned_identities) == 1
        assert (
            compute_from_rest.identity.user_assigned_identities[0].resource_id
            == "/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/test-rg-centraluseuap-v2-t-2021W35"
            "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/x"
        )

    def test_compute_instance_sai_from_yaml(self):
        compute: ComputeInstance = load_compute(
            "tests/test_configs/compute/compute-ci.yaml"
        )
        assert compute.name == "banchci"
        assert compute.type == "computeinstance"
        assert compute.identity.type == "system_assigned"

        compute_resource = compute._to_rest_object()
        assert compute_resource.identity.type == "SystemAssigned"

        compute_from_rest = Compute._from_rest_object(compute_resource)
        assert compute_from_rest.type == "computeinstance"
        assert compute_from_rest.identity.type == "system_assigned"

    def test_synapse_compute_from_rest(self):
        with open("tests/test_configs/compute/compute-synapsespark.yaml", "r") as f:
            data = yaml.safe_load(f)
        resource_id = "/subscriptions/dummy/resourceGroups/dummy/providers/Microsoft.Synapse/workspaces/dummy/bigDataPools/dummypool"
        context = {
            "base_path": "./",
            "params_override": [{"resource_id": resource_id, "name": "dummy"}],
        }
        compute = SynapseSparkCompute._load_from_dict(data, context)
        compute._to_rest_object()
        assert compute.type == "synapsespark"

    def test_synapsespark_compute_from_yaml(self):
        compute: SynapseSparkCompute = load_compute(
            "tests/test_configs/compute/compute-synapsespark-identity.yaml"
        )
        assert compute.name == "testidentity"
        assert compute.identity.type == "user_assigned"

        rest_intermediate = compute._to_rest_object()
        assert rest_intermediate.properties.compute_type == "SynapseSpark"
        serializer = Serializer({"ComputeResource": ComputeResource})
        body = serializer.body(rest_intermediate, "ComputeResource")
        assert body["identity"]["type"] == "UserAssigned"
        assert body["identity"]["userAssignedIdentities"] == self._uai_list_to_dict(
            compute.identity.user_assigned_identities
        )
