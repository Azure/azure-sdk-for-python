"""Snippets extracted from articles/batch/batch-linux-nodes.md (Python only).

Migrated from azure-batch 14.x to 15.1.0 (azure.batch.BatchClient).
"""

import datetime
import getpass

from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential


def create_pool_explicit_image():
    # [START linux_nodes_pool_create_python]
    # Specify Batch account credentials
    account = "<batch-account-name>"
    key = "<batch-account-key>"
    account_endpoint = "<batch-account-url>"

    # Pool settings
    pool_id = "LinuxNodesSamplePoolPython"
    vm_size = "STANDARD_D2_V3"
    node_count = 1

    # Initialize the Batch client
    creds = AzureNamedKeyCredential(account, key)
    client = BatchClient(endpoint=account_endpoint, credential=creds)

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

    # Create an ImageReference which specifies the Marketplace
    # virtual machine image to install on the nodes
    ir = models.BatchVmImageReference(
        publisher="canonical",
        offer="0001-com-ubuntu-server-focal",
        sku="20_04-lts",
        version="latest")

    # Create the VirtualMachineConfiguration, specifying
    # the VM image reference and the Batch node agent
    # to install on the node
    vmc = models.VirtualMachineConfiguration(
        image_reference=ir,
        node_agent_sku_id="batch.node.ubuntu 20.04")

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
    # [END linux_nodes_pool_create_python]
    return client


def vm_config_from_supported_images(client: BatchClient):
    # [START linux_nodes_image_reference_python]
    # Get the list of supported images from the Batch service
    images = list(client.list_supported_images())

    # Obtain the desired image reference
    image = None
    for img in images:
        if (img.image_reference.publisher.lower() == "canonical" and
                img.image_reference.offer.lower() == "0001-com-ubuntu-server-focal" and
                img.image_reference.sku.lower() == "20_04-lts"):
            image = img
            break

    if image is None:
        raise RuntimeError('invalid image reference for desired configuration')

    # Create the VirtualMachineConfiguration, specifying the VM image
    # reference and the Batch node agent to be installed on the node
    vmc = models.VirtualMachineConfiguration(
        image_reference=image.image_reference,
        node_agent_sku_id=image.node_agent_sku_id)
    # [END linux_nodes_image_reference_python]
    return vmc


def ssh_create_user_demo_inputs():
    # [START linux_nodes_ssh_user_python]
    # Specify your own account credentials
    batch_account_name = ''
    batch_account_key = ''
    batch_account_url = ''

    # Specify the ID of an existing pool containing Linux nodes
    # currently in the 'idle' state
    pool_id = ''

    # Specify the username and prompt for a password
    username = 'linuxuser'
    password = getpass.getpass()

    # Create a BatchClient
    creds = AzureNamedKeyCredential(batch_account_name, batch_account_key)
    batch_client = BatchClient(endpoint=batch_account_url, credential=creds)

    # Create the user that will be added to each node in the pool
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    user = models.BatchNodeUserCreateOptions(
        name=username,
        password=password,
        is_admin=True,
        expiry_time=expiry,
    )

    # Get the list of nodes in the pool and add the user to each
    nodes = batch_client.list_nodes(pool_id=pool_id)
    for node in nodes:
        batch_client.create_node_user(pool_id=pool_id, node_id=node.id, user=user)
        login_settings = batch_client.get_node_remote_login_settings(pool_id=pool_id, node_id=node.id)
        print(f"{node.id}: ssh {username}@{login_settings.remote_login_ip_address} -p {login_settings.remote_login_port}")
    # [END linux_nodes_ssh_user_python]
