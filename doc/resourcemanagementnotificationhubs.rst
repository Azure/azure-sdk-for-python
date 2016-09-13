Notification Hubs Management
============================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.notificationhubs import NotificationHubsManagementClient
	from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
	
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
		'user@domain.com',	# Your user
		'my_password',		# Your password
	)

    redis_client = NotificationHubsManagementClient(
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
    resource_client.providers.register('Microsoft.NotificationHubs')

Check namespace availability
----------------------------

The following code check namespace availability of a notification hub.

.. code:: python

    from azure.mgmt.notificationhubs.models import CheckAvailabilityParameters

    account_name = 'mynotificationhub'
    output = notificationhubs_client.namespaces.check_availability(
        azure.mgmt.notificationhubs.models.CheckAvailabilityParameters(
            name = account_name
        )
    )
    # output is a CheckAvailibilityResource instance
    print(output.is_availiable) # Yes, it's 'availiable', it's a typo in the REST API
    
