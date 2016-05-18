Content Delivery Network Management
===================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on getting a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.cdn import CdnManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    # TODO: See above how to get a Credentials instance
    credentials = ...

    cdn_client = CdnManagementClient(
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
    resource_client.providers.register('Microsoft.Cdn')

Check name availability
-----------------------

The following code check the name availability of a end-point.

.. code:: python

    from azure.mgmt.cdn.models import CheckNameAvailabilityInput

    output = self.cdn_client.name_availability.check_name_availability(
        name='myendpoint',
        type='Microsoft.Cdn/profiles/endpoints'
    )
    # output is a CheckNameAvailabilityOutput instance
    print(output.name_available)
