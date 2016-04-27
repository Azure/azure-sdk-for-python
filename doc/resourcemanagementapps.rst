Apps Management (Web Apps, Logic Apps)
======================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>`
for details on getting a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.logic import LogicManagementClient, LogicManagementClientConfiguration
    from azure.mgmt.web import WebSiteManagementClient, WebSiteManagementClientConfiguration

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    # TODO: See above how to get a Credentials instance
    credentials = ...

    logic_client = LogicManagementClient(
        LogicManagementClientConfiguration(
            credentials,
            subscription_id
        )
    )
    web_client = WebSiteManagementClient(
        WebSiteManagementClientConfiguration(
            credentials,
            subscription_id
        )
    )

Registration
------------

Some operations in the ARM APIs require a one-time registration of the
provider with your subscription.

Use the following code to do the registration. You can use the same
credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource.resources import ResourceManagementClient, ResourceManagementClientConfiguration

    resource_client = ResourceManagementClient(
        ResourceManagementClientConfiguration(
            credentials,
            subscription_id
        )
    )
    resource_client.providers.register('Microsoft.Web')
    resource_client.providers.register('Microsoft.Logic')

Create an App Service Plan
--------------------------

The following code creates an App Service Plan under an existing resource group.
To create or manage resource groups, see :doc:`Resource Management<resourcemanagement>`.

.. code:: python

    from azure.mgmt.web.models import ServerFarmWithRichSku, SkuDescription

    group_name = 'myresourcegroup'
    app_service_plan_name = 'myserviceplan'
    app_service_plan = web_client.server_farms.create_or_update_server_farm(
        group_name,
        app_service_plan_name,
        ServerFarmWithRichSku(
            location='West US',
            sku = SkuDescription(
                name='F1',
                tier='Free'
            )
        )
    )
    # app_service_plan is a msrestazure.azure_operation.AzureOperationPoller instance
    # wait insure polling the underlying async operation until it's done.
    # result() will return a ServerFarmWithRichSku instance
    app_service_plan = app_service_plan.result()


    
Create a Logic App Workflow
---------------------------

The following code creates a logic app workflow under an existing app service plan.

.. code:: python

    from azure.mgmt.logic.models import Workflow, Sku, ResourceReference

    group_name = 'myresourcegroup'
    workflow_name = '12HourHeartBeat'
    logic_client.workflows.create_or_update(
        group_name,
        workflow_name,
        Workflow(
            location = 'West US',
            sku = Sku(
                name = 'Free',
                plan = ResourceReference(
                    id = app_service_plan.id
                )
            ),
            definition={ 
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2015-08-01-preview/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {},
                "triggers": {},
                "actions": {},
                "outputs": {}
            }
        )
    )
