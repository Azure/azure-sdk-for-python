Resource Management Authentication
==================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

To be able to use use the ARM library, you need to obtain one of these instances:

* azure.common.credentials.ServicePrincipalCredentials
* azure.common.credentials.UserPassCredentials
* msrestazure.azure_active_directory.AdalAuthentication
 
And use it as credentials in your management configuration client. These three instances correspond to:

* OAuth authentication using Active Directory application and service principal
* OAuth authentication using Azure Active Directory user/password
* A wrapper on top of `ADAL for Python <https://github.com/AzureAD/azure-activedirectory-library-for-python>`

Using Service Principal
------------------------

There is now a detailed official tutorial to describe this:
https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/

At this point, you must have:

* Your client id. Found in the "client id" box in the "Settings" page of your application in the Azure portal.
* Your secret key. Generated when you have created the application. You cannot show the key after creation.
  If you've lost the current key, you must create a new one in the "Settings" page of your application.
* Your AD tenant id. It's an UUID (e.g. ABCDEFAB-1234-ABCD-1234-ABCDEFABCDEF) which points to the AD containing your application.
  You will find it in the URL when you are in the Azure portal in your AD, or in the "view endpoints" in any of the given url.

Then, you can create your credentials instance:

.. code:: python

    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id = 'ABCDEFAB-1234-ABCD-1234-ABCDEFABCDEF',
        secret = 'XXXXXXXXXXXXXXXXXXXXXXXX',
        tenant = 'ABCDEFAB-1234-ABCD-1234-ABCDEFABCDEF'
    )



Using AD User/Password
----------------------

1. Connect to the Azure Classic Portal with your admin account
2. `Create a user in your default AAD <https://azure.microsoft.com/en-us/documentation/articles/active-directory-create-users/>`__. **You must NOT activate Multi-Factor Authentication!**

3. Go to Settings - Administrators
4. Click on Add and enter the email of the new user. Check the checkbox of the subscription you want to test with this user.
5. Login to Azure Portal with this new user to change the temporary password to a new one. You will not be able to use the temporary password for OAuth login.

You are now able to log in Python using OAuth.

.. code:: python

    from azure.common.credentials import UserPassCredentials

    credentials = UserPassCredentials(
        'user@domain.com',    # Your new user
        'my_smart_password',  # Your password    
    )

Using ADAL
----------

`ADAL for Python <https://github.com/AzureAD/azure-activedirectory-library-for-python>`__ is a library 
from the Azure Active Directory team, that proposes the more complex scenarios not covered by the
two previous instances (like 2FA). Please refer to the ADAL website for all the available scenarios
list and samples.

For example, this code from the ADAL tutorial:

.. code:: python

    context = adal.AuthenticationContext('https://login.microsoftonline.com/ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL')
    RESOURCE = '00000002-0000-0000-c000-000000000000' #AAD graph resource
    token = context.acquire_token_with_client_credentials(
        RESOURCE,
        "http://PythonSDK",
        "Key-Configured-In-Portal")

can be written here:

.. code:: python

    from msrestazure.azure_active_directory import AdalAuthentication

    context = adal.AuthenticationContext('https://login.microsoftonline.com/ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL')
    RESOURCE = '00000002-0000-0000-c000-000000000000' #AAD graph resource
    credentials = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        RESOURCE,
        "http://PythonSDK",
        "Key-Configured-In-Portal")

or using a lambda if you prefer:

.. code:: python

    from msrestazure.azure_active_directory import AdalAuthentication

    context = adal.AuthenticationContext('https://login.microsoftonline.com/ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL')
    RESOURCE = '00000002-0000-0000-c000-000000000000' #AAD graph resource
    credentials = AdalAuthentication(
        lambda: context.acquire_token_with_client_credentials(
            RESOURCE,
            "http://PythonSDK",
            "Key-Configured-In-Portal"
        )
    )

Note that the UserPassCredentials and ServicePrincipalCredentials scenarios are also covered by the ADAL library. 
In the near future their implementation will be rewritten using ADAL.
