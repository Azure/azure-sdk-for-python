"""Snippets extracted from articles/batch/batch-user-accounts.md (Python only).

Migrated from azure-batch 14.x to 15.1.0 (azure.batch.BatchClient).
"""

from azure.batch import BatchClient, models


def add_admin_autouser_task(batch_client: BatchClient, jobid: str) -> None:
    # [START user_accounts_admin_autouser_python]
    user = models.UserIdentity(
        auto_user=models.AutoUserSpecification(
            elevation_level=models.ElevationLevel.ADMIN,
            scope=models.AutoUserScope.TASK))
    task = models.BatchTaskCreateOptions(
        id='task_1',
        command_line='cmd /c "echo hello world"',
        user_identity=user)
    batch_client.create_task(job_id=jobid, task=task)
    # [END user_accounts_admin_autouser_python]


def make_named_user_pool(pool_id: str, image_ref_to_use, sku_to_use, vm_size: str, vm_count: int):
    # [START user_accounts_pool_python]
    users = [
        models.UserAccount(
            name='pool-admin',
            password='A1bC2d',
            elevation_level=models.ElevationLevel.ADMIN),
        models.UserAccount(
            name='pool-nonadmin',
            password='A1bC2d',
            elevation_level=models.ElevationLevel.NON_ADMIN),
    ]
    pool = models.BatchPoolCreateOptions(
        id=pool_id,
        user_accounts=users,
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=image_ref_to_use,
            node_agent_sku_id=sku_to_use),
        vm_size=vm_size,
        target_dedicated_nodes=vm_count)
    # [END user_accounts_pool_python]
    return pool
