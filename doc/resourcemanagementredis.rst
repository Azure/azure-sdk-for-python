Redis Cache Management
======================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.redis import RedisManagementClient
	from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
	
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
		'user@domain.com',	# Your user
		'my_password',		# Your password
	)

    redis_client = RedisManagementClient(
        credentials,
        subscription_id
    )

Create Redis Cache
------------------

The following code creates a new redis cache under an existing resource group.
To create or manage resource groups, see :doc:`Resource Management<resourcemanagement>`.

.. code:: python

    from azure.mgmt.redis.models import Sku, RedisCreateOrUpdateParameters

    group_name = 'myresourcegroup'
    cache_name = 'mycachename'
    redis_cache = redis_client.redis.create_or_update(
        group_name, 
        cache_name,
        RedisCreateOrUpdateParameters( 
            sku = Sku(name = 'Basic', family = 'C', capacity = '1'),
            location = "West US"
        )
    ) 
    # redis_cache is a RedisResourceWithAccessKey instance
