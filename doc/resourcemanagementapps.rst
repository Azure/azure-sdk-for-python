Apps Management (Web Apps, Logic Apps)
======================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.logic import LogicManagementClient
    from azure.mgmt.web import WebSiteManagementClient
	from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
	
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
		'user@domain.com',	# Your user
		'my_password',		# Your password
	)

    logic_client = LogicManagementClient(
        credentials,
        subscription_id
    )
    web_client = WebSiteManagementClient(
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

    from azure.mgmt.resource import ResourceManagementClient

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )
    resource_client.providers.register('Microsoft.Web')
    resource_client.providers.register('Microsoft.Logic')

Usage sample for Web App Management
-----------------------------------

https://github.com/Azure-Samples/app-service-web-python-manage

    
Create a Logic App Workflow
---------------------------

The following code creates a logic app workflow.

.. code:: python

    from azure.mgmt.logic.models import Workflow

    group_name = 'myresourcegroup'
    workflow_name = '12HourHeartBeat'
    logic_client.workflows.create_or_update(
        group_name,
        workflow_name,
        Workflow(
            location = 'West US',
            definition={ 
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {},
                "triggers": {},
                "actions": {},
                "outputs": {}
            }
        )
    )
