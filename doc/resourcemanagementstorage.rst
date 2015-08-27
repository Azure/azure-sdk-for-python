Storage Resource Management
===========================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>`
for details on getting an authentication token.

.. code:: python

    from azure.mgmt.common import SubscriptionCloudCredentials
    from azure.mgmt.storage import StorageManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    creds = SubscriptionCloudCredentials(subscription_id, auth_token)

    storage_client = StorageManagementClient(creds)

Registration
------------

Some operations in the storage ARM APIs require a one-time registration of the
storage provider with your subscription.

Use the following code to do the registration. You can use the same
credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource import ResourceManagementClient

    resource_client = ResourceManagementClient(creds)
    resource_client.providers.register('Microsoft.Storage')

Create storage account
----------------------

The following code creates a new storage account under an existing resource group.
To create or manage resource groups, see :doc:`Resource Management<resourcemanagement>`.

.. code:: python

    from azure.mgmt.storage import StorageAccountCreateParameters, AccountType

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

List storage accounts
---------------------

.. code:: python

    group_name = 'myresourcegroup'
    result = storage_client.storage_accounts.list_by_resource_group(group_name)
    for storage_account in result.storage_accounts:
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
    result = storage_client.storage_accounts.list_keys(group_name, account_name)
    print(result.storage_account_keys.key1)
    print(result.storage_account_keys.key2)
