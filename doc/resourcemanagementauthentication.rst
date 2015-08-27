Resource Management Authentication
==================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create Service Principal
------------------------

First we need to create a service principal in Azure Active Directory.

Although creating an application can be done with the Azure Portal,
it is currently not possible to assign a role to the application using
the Azure Portal.

The following instructions use the Azure-CLI to create the application
and assign a role. You can also use Azure PowerShell.

Go to the following links to

1. `Install the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-install/>`__.
2. `Connect to the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-connect#use-the-publish-settings-file-method>`__.
3. `Authenticate to your Service Principal using the Azure-CLI <https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/#authenticate-service-principal-with-password---azure-cli>`__.

The instructions above give the application 'Reader' permissions.
You can use the 'Owner' permission for more access.

If you have access to more than one Azure subscription, make sure to activate
the correct subscription when using Azure-CLI. See the ``azure account list``
and ``azure account set`` commands.


Get token
---------

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

In the code below:

* Set ``endpoint`` to the value of "OAuth 2.0 Token Endpoint".
  Click on VIEW ENDPOINTS on the bottom toolbar in Azure portal,
  Active Directory, in APPLICATIONS page.

* Set ``client_id`` to the value of ``ApplicationId`` when the application
  was created using CLI.

* Set ``client_secret`` to the password used when the application was created
  using CLI.

.. code:: python

    auth_token = get_token_from_client_credentials(
        endpoint='https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/token',
        client_id='11111111-1111-1111-1111-111111111111',
        client_secret='2222222222222222222222222222222222222222222=',
    )
