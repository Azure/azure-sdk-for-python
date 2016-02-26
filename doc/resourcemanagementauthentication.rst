Resource Management Authentication
==================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

To be able to use use the ARM library, you need to obtain one of these instances:

* azure.common.credentials.UserPassCredentials
* azure.common.credentials.ServicePrincipalCredentials
 
And use it as credentials in your management configuration client. These two instances correspond to:

* OAuth authentication using Azure Active Directory user/password
* OAuth authentication using Active Directory application and service principal

Using Service Principal
------------------------

There is now a detailled official tutorial to describe this:
https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/

At this point, you must have:

* Your client id. Found in the "client id" box in the "Configure" page of your application in the Azure portal
* Your secret key. Generated when you have created the application. You cannot show the key after creation.
  If you've lost the current key, you must create a new one in the "Configure" page of your application.
* You AD tenant id. It's an UUID (e.g. ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL) which point to the AD containing your application.
  You will found it in the URL when you are in the Azure portal in your AD, or in the "view endpoints" in any of the given url.

Then, you can create your credentials instance:

.. code:: python

    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id = 'ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL',
        secret = 'XXXXXXXXXXXXXXXXXXXXXXXX',
        tenant = 'ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL'
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

    from azure.common.credentials import UserPassCredentials

    credentials = UserPassCredentials(
        'user@domain.com',    # Your new user
        'my_smart_password',  # Your password    
    )
