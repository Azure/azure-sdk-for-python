Compute and Network Resource Management
=======================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>`
for details on getting a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.network import NetworkManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    # TODO: See above how to get a Credentials instance
    credentials = ...

    compute_client = ComputeManagementClient(
        credentials,
        subscription_id
    )

    network_client = NetworkManagementClient(
        credentials,
        subscription_id
    )


Registration
------------

Some operations in the compute/network ARM APIs require a one-time
registration of the storage provider with your subscription.

Use the following code to do the registration. You can use the same
credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource.resources import ResourceManagementClient

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )
    resource_client.providers.register('Microsoft.Compute')
    resource_client.providers.register('Microsoft.Network')

List images
-----------

Use the following code to print all of the available images to use for
creating virtual machines, including all skus and versions.

.. code:: python

    region = 'eastus2'

    result_list_pub = compute_client.virtual_machine_images.list_publishers(
        region,
    )

    for publisher in result_list_pub:
        result_list_offers = compute_client.virtual_machine_images.list_offers(
            region,
            publisher.name,
        )

        for offer in result_list_offers:
            result_list_skus = compute_client.virtual_machine_images.list_skus(
                region,
                publisher.name,
                offer.name,
            )

            for sku in result_list_skus:
                result_list = compute_client.virtual_machine_images.list(
                    region,
                    publisher.name,
                    offer.name,
                    sku.name,
                )

                for version in result_list:
                    result_get = compute_client.virtual_machine_images.get(
                        region,
                        publisher.name,
                        offer.name,
                        sku.name,
                        version.name,
                    )

                    print('PUBLISHER: {0}, OFFER: {1}, SKU: {2}, VERSION: {3}'.format(
                        publisher.name,
                        offer.name,
                        sku.name,
                        version.name,
                    ))

Create virtual machine
----------------------

The following code creates a new virtual machine. Creating a virtual
machine involves creating a resource group, storage accounts, virtual
network resources, and finally the virtual machine.

To create or manage resource groups, see :doc:`Resource Management<resourcemanagement>`.

To create or manage storage accounts, see :doc:`Storage Resource Management<resourcemanagementstorage>`.

.. code:: python

    import azure.mgmt.compute
    import azure.mgmt.network
    import azure.mgmt.resource
    import azure.mgmt.storage

    resource_client = azure.mgmt.resource.ResourceManagementClient(res_config)
    storage_client = azure.mgmt.storage.StorageManagementClient(storage_config)
    compute_client = azure.mgmt.compute.ComputeManagementClient(compute_config)
    network_client = azure.mgmt.network.NetworkManagementClient(network_config)

    BASE_NAME = 'pythonexample'

    GROUP_NAME = BASE_NAME
    STORAGE_NAME = BASE_NAME
    VIRTUAL_NETWORK_NAME = BASE_NAME
    SUBNET_NAME = BASE_NAME
    NETWORK_INTERFACE_NAME = BASE_NAME
    VM_NAME = BASE_NAME
    OS_DISK_NAME = BASE_NAME
    PUBLIC_IP_NAME = BASE_NAME
    COMPUTER_NAME = BASE_NAME
    ADMIN_USERNAME='azureadminuser'
    ADMIN_PASSWORD='<censored>'
    REGION = 'eastus2'
    IMAGE_PUBLISHER = 'Canonical'
    IMAGE_OFFER = 'UbuntuServer'
    IMAGE_SKU = '15.04'
    IMAGE_VERSION = '15.04.201508180'

    # 1. Create a resource group
    result = resource_client.resource_groups.create_or_update(
        GROUP_NAME,
        azure.mgmt.resource.models.ResourceGroup(
            location=REGION,
        ),
    )

    # 2. Create a storage account
    result = storage_client.storage_accounts.create(
        GROUP_NAME,
        STORAGE_NAME,
        azure.mgmt.storage.models.StorageAccountCreateParameters(
            location=REGION,
            account_type=azure.mgmt.storage.models.AccountType.standard_lrs,
        ),
    )
    result.wait() # async operation

    # 3. Create the network interface using a helper function (defined below)
    nic_id = create_network_interface(
        network_client,
        REGION,
        GROUP_NAME,
        NETWORK_INTERFACE_NAME,
        VIRTUAL_NETWORK_NAME,
        SUBNET_NAME,
        PUBLIC_IP_NAME,
    )

    # 4. Create the virtual machine
    result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME,
        azure.mgmt.compute.models.VirtualMachine(
            location=REGION,
            os_profile=azure.mgmt.compute.models.OSProfile(
                admin_username=ADMIN_USERNAME,
                admin_password=ADMIN_PASSWORD,
                computer_name=COMPUTER_NAME,
            ),
            hardware_profile=azure.mgmt.compute.models.HardwareProfile(
                virtual_machine_size=azure.mgmt.compute.models.VirtualMachineSizeTypes.standard_a0
            ),
            network_profile=azure.mgmt.compute.models.NetworkProfile(
                network_interfaces=[
                    azure.mgmt.compute.models.NetworkInterfaceReference(
                        reference_uri=nic_id,
                    ),
                ],
            ),
            storage_profile=azure.mgmt.compute.models.StorageProfile(
                os_disk=azure.mgmt.compute.models.OSDisk(
                    caching=azure.mgmt.compute.models.CachingTypes.none,
                    create_option=azure.mgmt.compute.models.DiskCreateOptionTypes.from_image,
                    name=OS_DISK_NAME,
                    vhd=azure.mgmt.compute.models.VirtualHardDisk(
                        uri='https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
                            STORAGE_NAME,
                            OS_DISK_NAME,
                        ),
                    ),
                ),
                image_reference = azure.mgmt.compute.models.ImageReference(
                    publisher=IMAGE_PUBLISHER,
                    offer=IMAGE_OFFER,
                    sku=IMAGE_SKU,
                    version=IMAGE_VERSION,
                ),
            ),
        ),
    )

    # Display the public ip address
    # You can now connect to the machine using SSH
    public_ip_address = network_client.public_ip_addresses.get(GROUP_NAME, PUBLIC_IP_NAME)
    print('VM available at {}'.format(public_ip_address.ip_address))


This is the helper function that creates the network resources, such as
virtual network, public ip and network interface.

.. code:: python

    def create_network_interface(network_client, region, group_name, interface_name,
                                 network_name, subnet_name, ip_name):

        result = network_client.virtual_networks.create_or_update(
            group_name,
            network_name,
            azure.mgmt.network.models.VirtualNetwork(
                location=region,
                address_space=azure.mgmt.network.models.AddressSpace(
                    address_prefixes=[
                        '10.1.0.0/16',
                    ],
                ),
                subnets=[
                    azure.mgmt.network.models.Subnet(
                        name=subnet_name,
                        address_prefix='10.1.0.0/24',
                    ),
                ],
            ),
        )

        subnet = network_client.subnets.get(group_name, network_name, subnet_name)

        result = network_client.public_ip_addresses.create_or_update(
            group_name,
            ip_name,
            azure.mgmt.network.models.PublicIPAddress(
                location=region,
                public_ip_allocation_method=azure.mgmt.network.models.IPAllocationMethod.dynamic,
                idle_timeout_in_minutes=4,
            ),
        )

        public_ip_address = network_client.public_ip_addresses.get(group_name, ip_name)
        public_ip_id = public_ip_address.id

        result = network_client.network_interfaces.create_or_update(
            group_name,
            interface_name,
            azure.mgmt.network.models.NetworkInterface(
                location=region,
                ip_configurations=[
                    azure.mgmt.network.models.NetworkInterfaceIPConfiguration(
                        name='default',
                        private_ip_allocation_method=azure.mgmt.network.models.IPAllocationMethod.dynamic,
                        subnet=subnet,
                        public_ip_address=azure.mgmt.network.models.PublicIPAddress(
                            id=public_ip_id,
                        ),
                    ),
                ],
            ),
        )

        network_interface = network_client.network_interfaces.get(
            group_name,
            interface_name,
        )

        return network_interface.id
