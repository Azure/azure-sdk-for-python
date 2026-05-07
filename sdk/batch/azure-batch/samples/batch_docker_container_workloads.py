"""Snippets extracted from articles/batch/batch-docker-container-workloads.md (Python only).

Migrated from azure-batch 14.x to 15.1.0 (azure.batch.BatchClient).
"""

from azure.batch import models


def make_pool_no_prefetch(pool_id: str):
    # [START docker_pool_no_prefetch_python]
    image_ref_to_use = models.BatchVmImageReference(
        publisher='microsoft-dsvm',
        offer='ubuntu-hpc',
        sku='2204',
        version='latest')

    """
    Specify container configuration. This is required even though there are no prefetched images.
    """

    container_conf = models.BatchContainerConfiguration(type='dockerCompatible')

    new_pool = models.BatchPoolCreateOptions(
        id=pool_id,
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=image_ref_to_use,
            container_configuration=container_conf,
            node_agent_sku_id='batch.node.ubuntu 22.04'),
        vm_size='STANDARD_D2S_V3',
        target_dedicated_nodes=1)
    # [END docker_pool_no_prefetch_python]
    return new_pool


def make_pool_dockerhub_prefetch(pool_id: str):
    # [START docker_pool_dockerhub_prefetch_python]
    image_ref_to_use = models.BatchVmImageReference(
        publisher='microsoft-dsvm',
        offer='ubuntu-hpc',
        sku='2204',
        version='latest')

    """
    Specify container configuration, fetching the official Ubuntu container image from Docker Hub.
    """

    container_conf = models.BatchContainerConfiguration(
        type='dockerCompatible',
        container_image_names=['ubuntu'])

    new_pool = models.BatchPoolCreateOptions(
        id=pool_id,
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=image_ref_to_use,
            container_configuration=container_conf,
            node_agent_sku_id='batch.node.ubuntu 22.04'),
        vm_size='STANDARD_D2S_V3',
        target_dedicated_nodes=1)
    # [END docker_pool_dockerhub_prefetch_python]
    return new_pool


def make_pool_acr_prefetch():
    # [START docker_pool_acr_prefetch_python]
    image_ref_to_use = models.BatchVmImageReference(
        publisher='microsoft-dsvm',
        offer='ubuntu-hpc',
        sku='2204',
        version='latest')

    # Specify a container registry
    subscription_id = "yyyy-yyy-yyy-yyy-yyy"
    resource_group_name = "TestRG"
    user_assigned_identity_name = "testUMI"
    resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{user_assigned_identity_name}"
    )

    container_registry = models.ContainerRegistryReference(
        registry_server="myRegistry.azurecr.io",
        identity_reference=models.BatchNodeIdentityReference(resource_id=resource_id))

    # Create container configuration, prefetching Docker images from the container registry
    container_conf = models.BatchContainerConfiguration(
        type='dockerCompatible',
        container_image_names=["myRegistry.azurecr.io/samples/myImage"],
        container_registries=[container_registry])

    new_pool = models.BatchPoolCreateOptions(
        id="myPool",
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=image_ref_to_use,
            container_configuration=container_conf,
            node_agent_sku_id='batch.node.ubuntu 22.04'),
        vm_size='STANDARD_D2S_V3',
        target_dedicated_nodes=1)
    # [END docker_pool_acr_prefetch_python]
    return new_pool


def make_container_task():
    # [START docker_container_task_python]
    task_id = 'sampletask'
    task_container_settings = models.BatchTaskContainerSettings(
        image_name='myimage',
        container_run_options='--rm --workdir /')
    task = models.BatchTaskCreateOptions(
        id=task_id,
        command_line='/bin/sh -c "echo \'hello world\' > $AZ_BATCH_TASK_WORKING_DIR/output.txt"',
        container_settings=task_container_settings
    )
    # [END docker_container_task_python]
    return task
