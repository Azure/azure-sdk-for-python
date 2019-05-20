Azure Data Lake Management Analytics
====================================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.datalake.analytics import (
		DataLakeAnalyticsAccountManagementClient,
		DataLakeAnalyticsCatalogManagementClient,
		DataLakeAnalyticsJobManagementClient
	)
    from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
        'user@domain.com',  # Your user
        'my_password',      # Your password
    )

    account_client = DataLakeAnalyticsAccountManagementClient(
        credentials,
        subscription_id
    )
    catalog_client = DataLakeAnalyticsCatalogManagementClient(
        credentials,
        subscription_id
    )
    job_client = DataLakeAnalyticsJobManagementClient(
        credentials,
        subscription_id
    )

Samples
-------

Samples writing in progress! In the meantime, you should look at the unit tests of this package:

https://github.com/Azure/azure-sdk-for-python/blob/master/azure-mgmt/tests/test_mgmt_datalake_analytics.py

