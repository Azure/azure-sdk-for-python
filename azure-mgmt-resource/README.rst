Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure Resource Management Client Library.

Azure Resource Manager (ARM) is the next generation of management APIs that
replace the old Azure Service Management (ASM).

This package has been tested with Python 2.7, 3.3 and 3.4.

For the older Azure Service Management (ASM) libraries, see
`azure-servicemanagement-legacy <https://pypi.python.org/pypi/azure-servicemanagement-legacy>`__ library.

For a more complete set of Azure libraries, see the `azure <https://pypi.python.org/pypi/azure>`__ bundle package.


Compatibility
=============

**IMPORTANT**: If you have an earlier version of the azure package
(version < 1.0), you should uninstall it before installing this package.

You can check the version using pip:

.. code:: shell

    pip freeze

If you see azure==0.11.0 (or any version below 1.0), uninstall it first:

.. code:: shell

    pip uninstall azure


This is a preview release
=========================

The ARM libraries are being released as a preview, to solicit feedback.

**Future releases are subject to breaking changes**.

The Python code generator used to create this version of the ARM
libraries is being replaced, and may not generate code that is compatible
with this version of the ARM libraries.

Although future revisions will likely have breaking changes, the ARM concepts
along with the REST APIs that the library is wrapping should remain the same.

Please try the libraries and give us feedback, which we can incorporate into
future versions.


Usage
=====

Authentication
--------------

Authentication with Azure Resource Manager is done via tokens.

First we need create a service principal.  Go the following links to

1. `Install the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-install/>`__.
2. `Connect to the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-connect#use-the-publish-settings-file-method>`__.
3. `Authenticate to your Service Principal using the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/#authenticate-service-principal-with-password---azure-cli>`__.

Then, use the following code to obtain an authentication token.

.. code:: python

    import requests

    def get_token_from_client_credentials(endpoint, client_id, client_secret):
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': 'https://management.core.windows.net/',
        }
        response = requests.post(endpoint, data=payload).json()
        return response['access_token']

    # TODO: Replace endpoint, client id and secret for your application
    # In Azure portal, in your application configure page:
    # - Click on View Endpoints, use the OAuth 2.0 Token Endpoint
    # - The client id is already generated for you
    # - The client secret is only displayed when the key is created the first time
    auth_token = get_token_from_client_credentials(
        endpoint='https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/token',
        client_id='11111111-1111-1111-1111-111111111111',
        client_secret='2222222222222222222222222222222222222222222=',
    )

Create the management client
----------------------------

The following code uses the authentication token obtained in the previous
section and create an instance of the management client. You will need to provide your ``subscription_id`` which can be retrieved from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.



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


Provide Feedback
================

If you encounter any bugs or have suggestions, please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.
