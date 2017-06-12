Authorization Management
========================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.authorization import AuthorizationManagementClient
	from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
	
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
		'user@domain.com',	# Your user
		'my_password',		# Your password
	)

    authorization_client = AuthorizationManagementClient(
        credentials,
        subscription_id
    )

Registration
------------

Some operations in the ARM APIs require a one-time registration of the
provider with your subscription.

Use the following code to do the registration. You can use the same
credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource.resources import ResourceManagementClient

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )
    resource_client.providers.register('Microsoft.Authorization')

Check permissions for a resource group
--------------------------------------

The following code checks permissions in a given resource group.
To create or manage resource groups, see :doc:`Resource Management<resourcemanagement>`.

.. code:: python

    from azure.mgmt.redis.models import Sku, RedisCreateOrUpdateParameters

    group_name = 'myresourcegroup'
    permissions = self.authorization_client.permissions.list_for_resource_group(
        group_name
    )
    # permissions is a iterable of Permissions instances
