Batch
=====

Create the batch client
-----------------------

The following code creates an instance of the batch client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>`
for details on getting a Credentials instance.

.. code:: python

    from azure.batch import BatchRestClient, BatchRestClientConfiguration

    # TODO: must be an instance of 
    # - msrestazure.azure_active_directory.UserPassCredentials
    # - msrestazure.azure_active_directory.ServicePrincipalCredentials
    credentials = ...

    batch_client = BatchRestClient(
        BatchRestClientConfiguration(
            credentials,
        )
    )

Registration
------------

Some operations in the ARM APIs require a one-time registration of the
provider with your subscription.

Use the following code to do the registration. You can use the same
credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource import ResourceManagementClient

    resource_client = ResourceManagementClient(creds)
    resource_client.providers.register('Microsoft.Batch')

Do something
------------

Example to come