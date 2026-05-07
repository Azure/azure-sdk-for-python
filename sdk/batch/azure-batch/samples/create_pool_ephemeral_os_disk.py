"""Snippets extracted from articles/batch/create-pool-ephemeral-os-disk.md.

Migrated from azure-batch 14.x to 15.1.0 (azure.batch.BatchClient).
"""

from azure.batch import models


def make_vm_configuration(image_ref_to_use, node_sku_id):
    # [START ephemeral_os_disk_vm_config]
    virtual_machine_configuration = models.VirtualMachineConfiguration(
        image_reference=image_ref_to_use,
        node_agent_sku_id=node_sku_id,
        os_disk=models.BatchOsDisk(
            ephemeral_os_disk_settings=models.BatchDiffDiskSettings(
                placement=models.DiffDiskPlacement.CACHE_DISK
            )
        )
    )
    # [END ephemeral_os_disk_vm_config]
    return virtual_machine_configuration
