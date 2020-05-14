Quickstart Tutorial - Resource Management (Preview Libraries)
===============================================================

We are excited to announce that a new set of management libraries are now in Public Preview.
Those packages share a number of new features such as Azure Identity support,
HTTP pipeline, error-handling.,etc, and they also follow the new Azure SDK guidelines which
create easy-to-use APIs that are idiomatic, compatible, and dependable.

You can find the details of those new libraries `here <https://azure.github.io/azure-sdk/releases/latest/#python>`__

In this basic quickstart guide, we will walk you through how to
authenticate to Azure using the preview libraries and start interacting with
Azure resources. There are several possible approaches to
authentication. This document illustrates the most common scenario

Prerequisites
-------------

| You will need the following values to authenticate to Azure
 
- **Subscription ID**
- **Client ID** 
- **Client Secret** 
- **Tenant ID** 

These values can be obtained from the portal, here's the instructions:

Get Subscription ID
^^^^^^^^^^^^^^^^^^^

1. Login into your Azure account
2. Select Subscriptions in the left sidebar
3. Select whichever subscription is needed
4. Click on Overview
5. Copy the Subscription ID

Get Client ID / Client Secret / Tenant ID 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For information on how to get Client ID, Client Secret, and Tenant ID, please refer to `this document <https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal>`__

Setting Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After you obtained the values, you need to set the following values as
your environment variables

-  ``AZURE_CLIENT_ID``
-  ``AZURE_CLIENT_SECRET``
-  ``AZURE_TENANT_ID``
-  ``AZURE_SUBSCRIPTION_ID``

To set the following environment variables on your development system:

Windows (Note: Administrator access is required)

1. Open the Control Panel
2. Click System Security, then System
3. Click Advanced system settings on the left
4. Inside the System Properties window, click the Environment Variables… button.
5. Click on the property you would like to change, then click the Edit… button. If the property name is not listed, then click the New… button.

Linux-based OS
::

    export AZURE_CLIENT_ID="__CLIENT_ID__"
    export AZURE_CLIENT_SECRET="__CLIENT_SECRET__"
    export AZURE_TENANT_ID="__TENANT_ID__"
    export AZURE_SUBSCRIPTION_ID="__SUBSCRIPTION_ID__"

Authentication and Creating Resource Management Client
------------------------------------------------------

Now that the environment is setup, all you need to do is to create an
authenticated client. Our default option is to use
**DefaultAzureCredential** and in this guide we have picked
**Resources** as our target service, but you can set it up similarly for any other service that you are using.

To authenticate to Azure and create
a management client, simply do the following:

::

    import azure.mgmt.resource
    import azure.mgmt.network
    import azure.mgmt.compute
    from azure.identity import DefaultAzureCredential;
    ...
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    credentials = DefaultAzureCredential()
    resource_client = azure.mgmt.resource.ResourceManagementClient(credential=credentials, subscription_id=subscription_id)

More information and different authentication approaches using Azure Identity can be found in
`this document <https://docs.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python>`__

Managing Resources
------------------

Now that we are authenticated, we can use our management client to make API
calls. Let's create a resource group and demonstrate management client's usage

**Create a resource group**

::

    location = "mylocation"
    group_name = "my_resource_group_name"
    group = resource_client.resource_groups.create_or_update(
        group_name,
        {'location': location}
    )

**Update a resource group**

::

    group_name = "my_resource_group_name"
    group.tags = {
        "environment":"test",
        "department":"tech"
    }
    updated_group = resource_client.resource_groups.create_or_update(group_name, group)

**List all resource groups**

::

    # 
    group_list = self.resource_client.resource_groups.list()
    for g in group_list:
        print_resource_group(g)

**Delete a resource group**

::

    delete_async_op = resource_client.resource_groups.begin_delete(group_name)
    delete_async_op.wd 
