Resource Management
===================


Resource Management libraries
-----------------------------

The ARM libraries are separated into several packages:

* azure-mgmt-authorization
* azure-mgmt-cdn
* azure-mgmt-compute
* azure-mgmt-logic
* azure-mgmt-network
* azure-mgmt-notificationhubs
* azure-mgmt-redis
* azure-mgmt-resource
* azure-mgmt-scheduler
* azure-mgmt-storage
* azure-mgmt-web

The azure-mgmt-resource itself is splitted into several sub-librairies:

* resources : manage resources groups, template, etc
* features : manage features of provider
* authorization : manage resource group lock
* subscriptions : manage subscriptions

See the examples below for managing resource groups.

Authentication
--------------

All authentication with ARM is done via tokens.

For this preview release, we support authentication with a service principal.

In future releases, we will support additional scenarios using an ADAL library.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>`
for details on getting an authentication token.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>` for details on getting a ``Credential`` instance.

.. code:: python

    from azure.mgmt.resource.resources import ResourceManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    # TODO: See above how to get a Credentials instance
    credentials = ...

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )
    

Create resource group
---------------------

.. code:: python

    from azure.mgmt.resource.resources.models import ResourceGroup

    group_name = 'mynewresourcegroup'
    result = resource_client.resource_groups.create_or_update(
        group_name,
        ResourceGroup(
            location='westus',
            tags={
                'tag1': 'value1',
            },
        )
    )

List resource groups
--------------------

.. code:: python

    resource_groups = resource_client.resource_groups.list()
    for group in resource_groups:
        print(group.name)

Create resource
---------------

This creates an availability set using the generic resource API.

.. code:: python

    from azure.mgmt.resource.resources.models import GenericResource

    resource_name = 'MyAvailabilitySet'

    result = resource_client.resources.create_or_update(
        group_name,
        resource_provider_namespace="Microsoft.Compute",
        parent_resource_path="",
        resource_type="availabilitySets",
        resource_name=resource_name,
        api_version="2015-05-01-preview",
        parameters=GenericResource(
            location='West US',
            properties={},
        ),
    )

Create deployment from linked template
--------------------------------------

This creates resources specified in a linked JSON template.

.. code:: python

    from azure.mgmt.resource.resources.models import Deployment
    from azure.mgmt.resource.resources.models import DeploymentProperties
    from azure.mgmt.resource.resources.models import DeploymentMode
    from azure.mgmt.resource.resources.models import ParametersLink
    from azure.mgmt.resource.resources.models import TemplateLink

    deployment_name = 'MyDeployment'

    template = TemplateLink(
        uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-create-availability-set/azuredeploy.json',
    )

    parameters = ParametersLink(
        uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-create-availability-set/azuredeploy.parameters.json',
    )

    result = resource_client.deployments.create_or_update(
        group_name,
        deployment_name,
        properties=DeploymentProperties(
            mode=DeploymentMode.incremental,
            template_link=template,
            parameters_link=parameters,
        )
    )

Create deployment from template
-------------------------------

This creates resources specified in a JSON template.

.. code:: python

    from azure.mgmt.resource.resources.models import Deployment
    from azure.mgmt.resource.resources.models import DeploymentProperties
    from azure.mgmt.resource.resources.models import DeploymentMode

    deployment_name = 'MyDeployment'

    template = {
      "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "location": {
          "type": "string",
          "allowedValues": [
            "East US",
            "West US",
            "West Europe",
            "East Asia",
            "South East Asia"
          ],
          "metadata": {
            "description": "Location to deploy to"
          }
        }
      },
      "resources": [
        {
          "type": "Microsoft.Compute/availabilitySets",
          "name": "availabilitySet1",
          "apiVersion": "2015-05-01-preview",
          "location": "[parameters('location')]",
          "properties": {}
        }
      ]
    }

    # Note: when specifying values for parameters, omit the outer elements $schema, contentVersion, parameters
    parameters = {"location": { "value": "West US"}}

    result = resource_client.deployments.create_or_update(
        group_name,
        deployment_name,
        properties=DeploymentProperties(
            mode=DeploymentMode.incremental,
            template=template,
            parameters=parameters,
        )
    )


More examples
-------------

-  `Azure Resource Viewer Web Application Sample <https://github.com/Azure/azure-sdk-for-python/tree/master/examples/AzureResourceViewer>`__
-  `Azure Resource Manager Unit tests <https://github.com/Azure/azure-sdk-for-python/tree/master/azure-mgmt/tests>`__

Note that the ADAL library used by the Azure Resource Viewer sample hasn't been
officially released yet.  The application has a pre-release of ADAL in its
wheelhouse folder.
