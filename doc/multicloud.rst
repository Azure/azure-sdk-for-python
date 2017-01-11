Multi-cloud - use Azure on all regions
======================================

You can use the Azure SDK for Python to connect to all regions where Azure is available
(`list of Azure regions is available here <https://azure.microsoft.com/regions/services>`_).

Use the SDK on a different region than US Azure
-----------------------------------------------

By default, the Azure SDK for Python is configured to connect to public Azure.
To connect to another region, a few things have to be considered:

- What is the endpoint where to ask for a token (authentication)?
- What is the endpoint where I will use this token (usage)?

This is a generic example:

.. code:: python

    from azure.common.credentials import UserPassCredentials
    from azure.mgmt.resource import ResourceManagementClient

    # Public Azure - default values
    authentication_endpoint = 'https://login.microsoftonline.com/'
    azure_endpoint = 'https://management.azure.com/'
    
    credentials = UserPassCredentials(
        'user@domain.com',
        'my_smart_password',
        auth_uri=authentication_endpoint,
        resource=azure_endpoint
    )
    subscription_id = '33333333-3333-3333-3333-333333333333'

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id,
        base_url=azure_endpoint
    )


Azure Government
----------------

Azure Government is currently using the same authentication endpoint that public azure.
This means that we can use the default `authentication_endpoint`.

.. code:: python

    from azure.common.credentials import UserPassCredentials
    from azure.mgmt.resource import ResourceManagementClient

    azure_endpoint = 'https://management.usgovcloudapi.net/'

    credentials = UserPassCredentials(
        'user@domain.com',
        'my_smart_password',
        resource=azure_endpoint
    )
    subscription_id = '33333333-3333-3333-3333-333333333333'

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id,
        base_url=azure_endpoint
    )

Azure Germany
-------------

.. code:: python

    from azure.common.credentials import UserPassCredentials
    from azure.mgmt.resource import ResourceManagementClient

    authentication_endpoint = 'https://login.microsoftonline.de/'
    azure_endpoint = 'https://management.microsoftazure.de/'

    credentials = UserPassCredentials(
        'user@domain.com',
        'my_smart_password',
        auth_uri=authentication_endpoint,		
        resource=azure_endpoint
    )
    subscription_id = '33333333-3333-3333-3333-333333333333'

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id,
        base_url=azure_endpoint
    )

Azure China
-------------

.. code:: python

    from azure.common.credentials import UserPassCredentials
    from azure.mgmt.resource import ResourceManagementClient

    authentication_endpoint = 'https://login.chinacloudapi.cn/'
    azure_endpoint = 'https://management.chinacloudapi.cn/'

    credentials = UserPassCredentials(
        'user@domain.com',
        'my_smart_password',
        auth_uri=authentication_endpoint,		
        resource=azure_endpoint
    )
    subscription_id = '33333333-3333-3333-3333-333333333333'

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id,
        base_url=azure_endpoint
    )