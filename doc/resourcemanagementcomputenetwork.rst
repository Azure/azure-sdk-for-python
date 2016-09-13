Compute and Network Management
==============================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.network import NetworkManagementClient
	from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
	
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
		'user@domain.com',	# Your user
		'my_password',		# Your password
	)

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

Virtual Machine sample
----------------------

You can get a fully functionnal Virtual Machine sample from the AzureSample Github repository:
https://github.com/Azure-Samples/virtual-machines-python-manage
	
Load Balancer sample
--------------------

You can get a fully functionnal Load Balancer sample from the AzureSample Github repository:
https://github.com/Azure-Samples/network-python-manage-loadbalancer
	
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