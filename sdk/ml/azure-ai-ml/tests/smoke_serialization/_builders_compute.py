# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for compute entities (smoke serialization suite).

Compute types span the still-to-migrate API versions (v2022-10, v2022-12, v2023-08), so their
request-wire serialization is exactly what the upcoming migrations must preserve. Each builder is
fully deterministic (fixed names, no random/timestamp) so the wire is byte-stable across runs.
"""
from azure.ai.ml.entities import (
    AmlCompute,
    ComputeInstance,
    IdentityConfiguration,
    KubernetesCompute,
    SynapseSparkCompute,
    VirtualMachineCompute,
)
from azure.ai.ml.entities._compute.aml_compute import AmlComputeSshSettings
from azure.ai.ml.entities._compute.compute import NetworkSettings
from azure.ai.ml.entities._compute.compute_instance import ComputeInstanceSshSettings
from azure.ai.ml.entities._compute.synapsespark_compute import AutoPauseSettings, AutoScaleSettings
from azure.ai.ml.entities._compute._setup_scripts import ScriptReference, SetupScripts
from azure.ai.ml.entities._compute.virtual_machine_compute import VirtualMachineSshSettings

_FAKE_VM_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/smoke-rg"
    "/providers/Microsoft.Compute/virtualMachines/smoke-vm"
)


def build_aml_compute_full():
    """AmlCompute with ssh, network, identity, tier and scale settings."""
    return AmlCompute(
        name="smoke-aml-compute",
        description="smoke aml compute",
        size="STANDARD_DS3_V2",
        tags={"tag1": "value1"},
        min_instances=0,
        max_instances=4,
        idle_time_before_scale_down=120,
        tier="dedicated",
        ssh_public_access_enabled=True,
        ssh_settings=AmlComputeSshSettings(admin_username="azureuser", ssh_key_value="ssh-rsa AAAAB3Nz smoke"),
        network_settings=NetworkSettings(vnet_name="smoke-vnet", subnet="smoke-subnet"),
        identity=IdentityConfiguration(type="system_assigned"),
        enable_node_public_ip=True,
    )


def build_aml_compute_minimal():
    """AmlCompute with only required fields."""
    return AmlCompute(name="smoke-aml-minimal", size="STANDARD_DS3_V2")


def build_compute_instance_full():
    """ComputeInstance with ssh, setup scripts and identity."""
    return ComputeInstance(
        name="smoke-compute-instance",
        description="smoke compute instance",
        size="STANDARD_DS3_V2",
        tags={"tag1": "value1"},
        ssh_public_access_enabled=True,
        ssh_settings=ComputeInstanceSshSettings(ssh_key_value="ssh-rsa AAAAB3Nz smoke"),
        setup_scripts=SetupScripts(
            startup_script=ScriptReference(path="setup.sh", command="bash setup.sh", timeout_minutes=10)
        ),
        identity=IdentityConfiguration(type="system_assigned"),
        idle_time_before_shutdown_minutes=30,
        enable_node_public_ip=True,
        enable_sso=True,
        enable_root_access=True,
    )


def build_compute_instance_minimal():
    """ComputeInstance with only required fields."""
    return ComputeInstance(name="smoke-ci-minimal", size="STANDARD_DS3_V2")


def build_kubernetes_compute_full():
    """KubernetesCompute with namespace, properties and identity."""
    return KubernetesCompute(
        name="smoke-k8s-compute",
        description="smoke kubernetes compute",
        namespace="smoke-namespace",
        properties={"defaultInstanceType": "defaultInstanceType", "vcName": "smoke-vc"},
        identity=IdentityConfiguration(type="system_assigned"),
    )


def build_synapse_spark_compute_full():
    """SynapseSparkCompute with node config, scale and auto-pause settings."""
    return SynapseSparkCompute(
        name="smoke-synapse-spark",
        description="smoke synapse spark compute",
        tags={"tag1": "value1"},
        node_count=3,
        node_family="MemoryOptimized",
        node_size="Medium",
        spark_version="3.4",
        identity=IdentityConfiguration(type="system_assigned"),
        scale_settings=AutoScaleSettings(min_node_count=1, max_node_count=5, enabled=True),
        auto_pause_settings=AutoPauseSettings(delay_in_minutes=15, enabled=True),
    )


def build_virtual_machine_compute_full():
    """VirtualMachineCompute with resource id and ssh settings."""
    return VirtualMachineCompute(
        name="smoke-vm-compute",
        description="smoke vm compute",
        resource_id=_FAKE_VM_ID,
        tags={"tag1": "value1"},
        ssh_settings=VirtualMachineSshSettings(
            admin_username="azureuser",
            admin_password="smoke-password",
            ssh_port=22,
        ),
    )


COMPUTE_BUILDERS = {
    "aml_compute_full": build_aml_compute_full,
    "aml_compute_minimal": build_aml_compute_minimal,
    "compute_instance_full": build_compute_instance_full,
    "compute_instance_minimal": build_compute_instance_minimal,
    "kubernetes_compute_full": build_kubernetes_compute_full,
    "synapse_spark_compute_full": build_synapse_spark_compute_full,
    "virtual_machine_compute_full": build_virtual_machine_compute_full,
}
