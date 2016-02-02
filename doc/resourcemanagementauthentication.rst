Resource Management Authentication
==================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

To be able to use use the ARM library, you need to obtain one of these instances:

* msrestazure.azure_active_directory.UserPassCredentials
* msrestazure.azure_active_directory.ServicePrincipalCredentials
 
And use it as credentials in your management configuration client. These two instances correspond to:

* OAuth authentication using Azure Active Directory user/password
* OAuth authentication using Active Directory application and service principal

Using Service Principal
------------------------

There is now a detailled official tutorial to describe this:
https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/

Then, you can create your credentials instance:

.. code:: python

    from msrestazure.azure_active_directory import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        'https://login.microsoftonline.com/ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL/', # Your OAuth 2.0 Token Endpoint for this app
        'ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL',                                    # Your client id
        'generatedkey',                                                            # Your authentication key
    )



Using AD User/Password
----------------------

1. Connect to the Azure Classic Portal with your admin account
2. `Create a user in your default AAD <https://azure.microsoft.com/en-us/documentation/articles/active-directory-create-users/>`__

**You must NOT activate Multi-Factor Authentication**

3. Go to Settings - Administrators
4. Click on Add and enter the email of the new user. Check the checkbox of the subscription you want to test with this user.
5. Login to Azure Portal with this new user to change the temporary password to a new one. You will not be able to use the temporary password for OAuth login.

You are now able to log in Python using OAuth.

.. code:: python

    from msrestazure.azure_active_directory import UserPassCredentials

    credentials = UserPassCredentials(
        'user@domain.com',    # Your new user
        'my_smart_password',  # Your password    
    )
