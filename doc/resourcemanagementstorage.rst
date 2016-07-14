Storage Resource Management
===========================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>`
for details on getting a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.storage import StorageManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    # TODO: See above how to get a Credentials instance
    credentials = ...

    storage_client = StorageManagementClient(
        credentials,
        subscription_id
    )

Registration
------------

Some operations in the storage ARM APIs require a one-time registration of the
storage provider with your subscription.

Use the following code to do the registration. You can use the same
credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource.resources import ResourceManagementClient

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )
    resource_client.providers.register('Microsoft.Storage')

Create storage account
----------------------

The following code creates a new storage account under an existing resource group.
To create or manage resource groups, see :doc:`Resource Management<resourcemanagement>`.

.. code:: python

    from azure.mgmt.storage.models import StorageAccountCreateParameters, AccountType

    group_name = 'myresourcegroup'
    account_name = 'mystorageaccountname'
    result = storage_client.storage_accounts.create(
        group_name,
        account_name,
        StorageAccountCreateParameters(
            location='westus',
            account_type=AccountType.standard_lrs,
        ),
    )
    # result is a msrestazure.azure_operation.AzureOperationPoller instance
    # wait insure polling the underlying async operation until it's done.
    result.wait()

List storage accounts
---------------------

.. code:: python

    group_name = 'myresourcegroup'
    storage_accounts = storage_client.storage_accounts.list_by_resource_group(group_name)
    for storage_account in storage_accounts:
        print(storage_account.name)
        print(storage_account.account_type)
        print(storage_account.location)
        print(storage_account.provisioning_state)
        print('')

Get storage account keys
------------------------

.. code:: python

    group_name = 'myresourcegroup'
    account_name = 'mystorageaccountname'
    storage_account_keys = storage_client.storage_accounts.list_keys(group_name, account_name)
    print(storage_account_keys['key1'])
    print(storage_account_keys['key2'])
