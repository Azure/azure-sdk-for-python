Batch Management
================

For more information on the Azure Batch service, check out the `Batch Documentation <https://azure.microsoft.com/en-us/documentation/services/batch/>`__.
For working samples, see the `Batch samples repo <https://github.com/Azure/azure-batch-samples/tree/master/Python>`__.

The API documentation: :doc:`API <ref/azure.mgmt.batch>`

Create the Batch Management client
----------------------------------

The following code creates an instance of the management client.
You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.batch import BatchManagementClient
	from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
	
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
		'user@domain.com',	# Your user
		'my_password',		# Your password
	)

    batch_client = BatchManagementClient(
        credentials,
        subscription_id
    )


Create a Batch Account
----------------------

A Batch Account will need to be created in a specified location and resource group.
The default Batch Account quota is 1 per location per subscription, but can be increased to a maximum of 50.
Please contact support if you require a quota increase.
For more information on resource groups and resource management, see :doc:`Resource Management<resourcemanagement>`.

In order to make use of Application Packages, a storage account will need to be linked to the Batch Account. A linked storage account is known as 'auto-storage'.
A storage account can be created with the :doc:`Storage Resource Management Client <resourcemanagementstorage>`.

.. code:: python

	# Create a Resource Group (or use an existing one)
	import azure.mgmt.resource

	RESOURCE_GROUP = 'python_sdk'
	LOCATION = 'westus'

	resource_client = = azure.mgmt.storage.ResourceManagementClient(
		azure.mgmt.resources.ResourceManagementClientConfiguration(
			credentials, # See section above
			subscription_id
		)
	)
	group = azure.mgmt.resource.resources.models.ResourceGroup(
		name=RESOURCE_GROUP,
		location=LOCATION
	)
	resource_client.resource_groups.create_or_update(
		RESOURCE_GROUP,
		group,
	)


	# Create a storage account for 'auto-storage' (or use an existing one)
	import azure.mgmt.storage
	storage_client = azure.mgmt.storage.StorageManagementClient(
		azure.mgmt.storage.StorageManagementClientConfiguration(
			credentials, # See section above
			subscription_id
		)
	)
	storage_params = azure.mgmt.storage.models.StorageAccountCreateParameters(
		location=LOCATION,
		account_type=azure.mgmt.storage.models.AccountType.standard_lrs
	)
	creating = storage_client.storage_accounts.create(
		RESOURCE_GROUP,
		'pythonstorageaccount',
		storage_params
	)
	creating.wait()

	# Create a Batch Account, specifying the storage account we want to link
	storage_resource = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}'.format(
		subscription_id,
		RESOURCE_GROUP,
		'pythonstorageaccount'
	)
	batch_account = azure.mgmt.batch.models.BatchAccountCreateParameters(
		location=LOCATION,
		auto_storage=azure.mgmt.batch.models.AutoStorageBaseProperties(storage_resource)
	)
	creating = batch_client.account.create('MyBatchAccount', LOCATION, batch_account)
	creating.wait()



Account keys (used for authenticating the :doc:`Batch Client <batch>`) can be retrieved or regenerated.

.. code:: python

	batch_client.account.regenerate_key(
		RESOURCE_GROUP,
		'MyBatchAccount',
		'Primary'
	)
	accounts_keys = batch_client.account.list_keys(RESOURCE_GROUP, 'MyBatchAccount')
	print('Updated primary key: {}'.format(accounts_keys.primary))



Application Packages
--------------------

Application packages can be configured to be used by the the :doc:`Batch Client <batch>` for running tasks.
An Application can have multiple versioned packages (zipped directories containing the application to be executed on the Compute Node) associated with it.
You can find an overview of this feature in this article on `application deployment with Azure Batch Applications <https://azure.microsoft.com/en-us/documentation/articles/batch-application-packages/>`__.

.. code:: python

	# Create Application reference
	batch_client.application.add(
		RESOURCE_GROUP,
		'MyBatchAccount',
		'MyApplicationId'
		allow_updates=True,
		display_name='Test App v1'
	)

	# Add a new package to the application
	package_ref = batch_client.application.add_application_package(
		RESOURCE_GROUP,
		'MyBatchAccount',
		'MyApplicationId',
		'v1.0'
	)

	# Upload a zip directory for the created package reference
	import requests
	with open('my_application.zip', 'rb') as app_data:
		headers = {'x-ms-blob-type': 'BlockBlob'}
		requests.put(package_ref.storage_url, headers=headers, data=app_data.read())
		
	# In order to use the application in a job, the package must be activated
	batch_client.application.activate_application_package(
		RESOURCE_GROUP,
		'MyBatchAccount',
		'MyApplicationId',
		'v1.0',
		'zip'
	)

