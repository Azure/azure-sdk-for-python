Resource Management
===================


Resource Management libraries
-----------------------------

The azure-mgmt-resource package is split into several sub-libraries:

* resources : manage resource groups, templates, etc (`Introduction to ARM <https://azure.microsoft.com/en-us/documentation/articles/resource-group-overview/>`__)
* features : manage features of provider (`RestAPI reference <https://msdn.microsoft.com/en-us/library/azure/mt592690.aspx>`__)
* locks : manage resource group lock (`RestAPI reference <https://msdn.microsoft.com/en-us/library/azure/mt204563.aspx>`__)
* subscriptions : manage subscriptions (`RestAPI reference <https://msdn.microsoft.com/en-us/library/azure/dn790566.aspx>`__)
* policy : manage and control access to resources (`RestAPI reference <https://msdn.microsoft.com/en-us/library/azure/mt588471.aspx>`__)

See the examples below for managing resource groups.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.resource.resources import ResourceManagementClient
	from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
	
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
		'user@domain.com',	# Your user
		'my_password',		# Your password
	)

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )
    

Usage sample for Resource Groups and Resources management
---------------------------------------------------------

https://github.com/Azure-Samples/resource-manager-python-resources-and-groups

Usage sample for Template deployment
------------------------------------

https://github.com/Azure-Samples/resource-manager-python-template-deployment
