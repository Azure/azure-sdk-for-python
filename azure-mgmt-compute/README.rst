Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure Compute Resource Management Client Library.

Azure Resource Manager (ARM) is the next generation of management APIs that
replace the old Azure Service Management (ASM).

This package has been tested with Python 2.7, 3.3 and 3.4.

For the older Azure Service Management (ASM) libraries, see
`azure-servicemanagement-legacy <https://pypi.python.org/pypi/azure-servicemanagement-legacy>`__ library.

For a more complete set of Azure libraries, see the `azure <https://pypi.python.org/pypi/azure>`__ bundle package.


Compatibility
=============

**IMPORTANT**: If you have an earlier version of the azure package
(version < 1.0), you should uninstall it before installing this package.

You can check the version using pip:

.. code:: shell

    pip freeze

If you see azure==0.11.0 (or any version below 1.0), uninstall it first:

.. code:: shell

    pip uninstall azure


This is a preview release
=========================

The ARM libraries are being released as a preview, to solicit feedback.

**Future releases are subject to breaking changes**.

The Python code generator used to create this version of the ARM
libraries is being replaced, and may not generate code that is compatible
with this version of the ARM libraries.

Although future revisions will likely have breaking changes, the ARM concepts
along with the REST APIs that the library is wrapping should remain the same.

Please try the libraries and give us feedback, which we can incorporate into
future versions.


Usage
=====

Authentication
--------------

Authentication with Azure Resource Manager is done via tokens.

First we need create a service principal go the following links to

1. `Install the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-install/>`__.
2. `Connect to the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-connect#use-the-publish-settings-file-method>`__.
3. `Authenticate to your Service Principal using the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/#authenticate-service-principal-with-password---azure-cli>`__.

Then, use the following code to obtain an authentication token.

.. code:: python

    import requests

    def get_token_from_client_credentials(endpoint, client_id, client_secret):
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': 'https://management.core.windows.net/',
        }
        response = requests.post(endpoint, data=payload).json()
        return response['access_token']

    # TODO: Replace endpoint, client id and secret for your application
    # In Azure portal, in your application configure page:
    # - Click on View Endpoints, use the OAuth 2.0 Token Endpoint
    # - The client id is already generated for you
    # - The client secret is only displayed when the key is created the first time
    auth_token = get_token_from_client_credentials(
        endpoint='https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/token',
        client_id='11111111-1111-1111-1111-111111111111',
        client_secret='2222222222222222222222222222222222222222222=',
    )

Create the management client
----------------------------

The following code uses the authentication token obtained in the previous
section and create an instance of the management client. You will need to
provide your ``subscription_id`` which can be retrieved from
`your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

.. code:: python

    from azure.mgmt.common import SubscriptionCloudCredentials
    from azure.mgmt.compute import ComputeManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    creds = SubscriptionCloudCredentials(subscription_id, auth_token)

    compute_client = ComputeManagementClient(creds)

Registration
------------

Some operations in the compute ARM APIs require a one-time registration of the
storage provider with your subscription.

Use the following code with the `azure-mgmt-resource <https://pypi.python.org/pypi/azure-mgmt-resource>`__ package to do the registration.
You can use the same credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource import ResourceManagementClient

    resource_client = ResourceManagementClient(creds)
    resource_client.providers.register('Microsoft.Compute')

List images
-----------

Use the following code to print all of the available images to use for
creating virtual machines, including all skus and versions.

.. code:: python

    region = 'eastus2'

    result_list_pub = compute_client.virtual_machine_images.list_publishers(
        azure.mgmt.compute.VirtualMachineImageListPublishersParameters(
            location=region,
        ),
    )

    for publisher in result_list_pub.resources:
        result_list_offers = compute_client.virtual_machine_images.list_offers(
            azure.mgmt.compute.VirtualMachineImageListOffersParameters(
                location=region,
                publisher_name=publisher.name,
            ),
        )

        for offer in result_list_offers.resources:
            result_list_skus = compute_client.virtual_machine_images.list_skus(
                azure.mgmt.compute.VirtualMachineImageListSkusParameters(
                    location=region,
                    publisher_name=publisher.name,
                    offer=offer.name,
                ),
            )

            for sku in result_list_skus.resources:
                result_list = compute_client.virtual_machine_images.list(
                    azure.mgmt.compute.VirtualMachineImageListParameters(
                        location=region,
                        publisher_name=publisher.name,
                        offer=offer.name,
                        skus=sku.name,
                    ),
                )

                for version in result_list.resources:
                    result_get = compute_client.virtual_machine_images.get(
                        azure.mgmt.compute.VirtualMachineImageGetParameters(
                            location=region,
                            publisher_name=publisher.name,
                            offer=offer.name,
                            skus=sku.name,
                            version=version.name,
                        ),
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

To create or manage resource groups, see the `azure-mgmt-resource <https://pypi.python.org/pypi/azure-mgmt-resource>`__ package.
To create or manage storage accounts, see the `azure-mgmt-storage <https://pypi.python.org/pypi/azure-mgmt-storage>`__ package.
To create or manage virtual networks, see the `azure-mgmt-network <https://pypi.python.org/pypi/azure-mgmt-network>`__ package.

.. code:: python

    import azure.mgmt.compute
    import azure.mgmt.network
    import azure.mgmt.resource
    import azure.mgmt.storage

    resource_client = azure.mgmt.resource.ResourceManagementClient(creds)
    storage_client = azure.mgmt.storage.StorageManagementClient(creds)
    compute_client = azure.mgmt.compute.ComputeManagementClient(creds)
    network_client = azure.mgmt.network.NetworkResourceProviderClient(creds)

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
        azure.mgmt.resource.ResourceGroup(
            location=REGION,
        ),
    )

    # 2. Create a storage account
    result = storage_client.storage_accounts.create(
        GROUP_NAME,
        STORAGE_NAME,
        azure.mgmt.storage.StorageAccountCreateParameters(
            location=REGION,
            account_type=azure.mgmt.storage.AccountType.standard_lrs,
        ),
    )

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
        azure.mgmt.compute.VirtualMachine(
            location=REGION,
            name=VM_NAME,
            os_profile=azure.mgmt.compute.OSProfile(
                admin_username=ADMIN_USERNAME,
                admin_password=ADMIN_PASSWORD,
                computer_name=COMPUTER_NAME,
            ),
            hardware_profile=azure.mgmt.compute.HardwareProfile(
                virtual_machine_size=azure.mgmt.compute.VirtualMachineSizeTypes.standard_a0
            ),
            network_profile=azure.mgmt.compute.NetworkProfile(
                network_interfaces=[
                    azure.mgmt.compute.NetworkInterfaceReference(
                        reference_uri=nic_id,
                    ),
                ],
            ),
            storage_profile=azure.mgmt.compute.StorageProfile(
                os_disk=azure.mgmt.compute.OSDisk(
                    caching=azure.mgmt.compute.CachingTypes.none,
                    create_option=azure.mgmt.compute.DiskCreateOptionTypes.from_image,
                    name=OS_DISK_NAME,
                    virtual_hard_disk=azure.mgmt.compute.VirtualHardDisk(
                        uri='https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
                            STORAGE_NAME,
                            OS_DISK_NAME,
                        ),
                    ),
                ),
                image_reference = azure.mgmt.compute.ImageReference(
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
    result = network_client.public_ip_addresses.get(GROUP_NAME, PUBLIC_IP_NAME)
    print('VM available at {}'.format(result.public_ip_address.ip_address))


This is the helper function that creates the network resources, such as
virtual network, public ip and network interface.

.. code:: python

    def create_network_interface(network_client, region, group_name, interface_name,
                                 network_name, subnet_name, ip_name):

        result = network_client.virtual_networks.create_or_update(
            group_name,
            network_name,
            azure.mgmt.network.VirtualNetwork(
                location=region,
                address_space=azure.mgmt.network.AddressSpace(
                    address_prefixes=[
                        '10.1.0.0/16',
                    ],
                ),
                subnets=[
                    azure.mgmt.network.Subnet(
                        name=subnet_name,
                        address_prefix='10.1.0.0/24',
                    ),
                ],
            ),
        )

        result = network_client.subnets.get(group_name, network_name, subnet_name)
        subnet = result.subnet

        result = network_client.public_ip_addresses.create_or_update(
            group_name,
            ip_name,
            azure.mgmt.network.PublicIpAddress(
                location=region,
                public_ip_allocation_method='Dynamic',
                idle_timeout_in_minutes=4,
            ),
        )

        result = network_client.public_ip_addresses.get(group_name, ip_name)
        public_ip_id = result.public_ip_address.id

        result = network_client.network_interfaces.create_or_update(
            group_name,
            interface_name,
            azure.mgmt.network.NetworkInterface(
                name=interface_name,
                location=region,
                ip_configurations=[
                    azure.mgmt.network.NetworkInterfaceIpConfiguration(
                        name='default',
                        private_ip_allocation_method=azure.mgmt.network.IpAllocationMethod.dynamic,
                        subnet=subnet,
                        public_ip_address=azure.mgmt.network.ResourceId(
                            id=public_ip_id,
                        ),
                    ),
                ],
            ),
        )

        result = network_client.network_interfaces.get(
            group_name,
            interface_name,
        )

        return result.network_interface.id

More examples
-------------

-  `Azure Resource Viewer Web Application Sample <https://github.com/Azure/azure-sdk-for-python/tree/master/examples/AzureResourceViewer>`__
-  `Azure Resource Manager Unit tests <https://github.com/Azure/azure-sdk-for-python/tree/master/azure-mgmt/tests>`__

Note that the ADAL library used by the Azure Resource Viewer sample hasn't been
officially released yet.  The application has a pre-release of ADAL in its
wheelhouse folder.


Provide Feedback
================

If you encounter any bugs or have suggestions, please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.
