"""Snippets extracted from articles/batch/batch-sig-images.md.

Migrated from azure-batch 14.x to 15.1.0 (azure.batch.BatchClient).
"""

# [START sig_create_pool_python]
from azure.batch import BatchClient, models
from azure.identity import DefaultAzureCredential

# Specify Batch account credentials
account_endpoint = "https://{batch-account-name}.{region}.batch.azure.com"

# Pool settings
pool_id = "LinuxNodesSamplePoolPython"
vm_size = "STANDARD_D2_V3"
node_count = 1

# Initialize the Batch client with Microsoft Entra ID authentication
client = BatchClient(endpoint=account_endpoint, credential=DefaultAzureCredential())

# Configure the start task for the pool
start_task = models.BatchStartTask(
    command_line="printenv AZ_BATCH_NODE_STARTUP_DIR",
    user_identity=models.UserIdentity(
        auto_user=models.AutoUserSpecification(
            elevation_level=models.ElevationLevel.ADMIN,
            scope=models.AutoUserScope.POOL,
        )
    ),
)

# Create an image reference that points to an Azure Compute Gallery image.
ir = models.BatchVmImageReference(
    virtual_machine_image_id=(
        "/subscriptions/{sub id}/resourceGroups/{resource group name}"
        "/providers/Microsoft.Compute/galleries/{gallery name}"
        "/images/{image definition name}/versions/{version id}"
    )
)

# Create the VirtualMachineConfiguration
vmc = models.VirtualMachineConfiguration(
    image_reference=ir,
    node_agent_sku_id="batch.node.ubuntu 22.04",
)

# Create the unbound pool
new_pool = models.BatchPoolCreateOptions(
    id=pool_id,
    vm_size=vm_size,
    target_dedicated_nodes=node_count,
    virtual_machine_configuration=vmc,
    start_task=start_task,
)

# Create pool in the Batch service
client.create_pool(pool=new_pool)
# [END sig_create_pool_python]
