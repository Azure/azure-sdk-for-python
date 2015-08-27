Resource Management
===================

This is a preview release
-------------------------

The ARM libraries are being released as a preview, to solicit feedback.

**Future releases are subject to breaking changes**.

The Python code generator used to create this version of the ARM
libraries is being replaced, and may not generate code that is compatible
with this version of the ARM libraries.

Although future revisions will likely have breaking changes, the ARM concepts
along with the REST APIs that the library is wrapping should remain the same.

Please try the libraries and give us feedback, which we can incorporate into
future versions.

Compute, Network and Storage Resource Management
------------------------------------------------

The ARM libraries are separated into several packages:

* azure-mgmt-resource
* azure-mgmt-compute
* azure-mgmt-network
* azure-mgmt-storage

See :doc:`Storage Resource Management <resourcemanagementstorage>` for examples
of managing storage accounts.

See :doc:`Compute and Network Resource Management <resourcemanagementcomputenetwork>`
for examples of managing virtual machines.

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

See :doc:`Resource Management Authentication <resourcemanagementauthentication>` for details on getting an authentication token.

.. code:: python

    from azure.mgmt.common import SubscriptionCloudCredentials
    from azure.mgmt.resource import ResourceManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    creds = SubscriptionCloudCredentials(subscription_id, auth_token)

    resource_client = ResourceManagementClient(creds)

Create resource group
---------------------

.. code:: python

    from azure.mgmt.resource import ResourceGroup

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

    result = resource_client.resource_groups.list(None)
    for group in result.resource_groups:
        print(group.name)

More examples
-------------

-  `Azure Resource Viewer Web Application Sample <https://github.com/Azure/azure-sdk-for-python/tree/master/examples/AzureResourceViewer>`__
-  `Azure Resource Manager Unit tests <https://github.com/Azure/azure-sdk-for-python/tree/master/azure-mgmt/tests>`__

Note that the ADAL library used by the Azure Resource Viewer sample hasn't been
officially released yet.  The application has a pre-release of ADAL in its
wheelhouse folder.
