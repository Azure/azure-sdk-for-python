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

    import adal
    from msrestazure.azure_active_directory import AdalAuthentication
    from azure.mgmt.resource import ResourceManagementClient

    # Service Principal
    tenant = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    client_id = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    password = 'password

    # Public Azure - default values
    authentication_endpoint = 'https://login.microsoftonline.com/'
    azure_endpoint = 'https://management.azure.com/'
        
    context = adal.AuthenticationContext(authentication_endpoint+tenant)
    credentials = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        azure_endpoint,
        client_id,
        password
    )
    subscription_id = '33333333-3333-3333-3333-333333333333'

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id,
        base_url=azure_endpoint
    )


Azure Government
----------------

.. code:: python

    import adal
    from msrestazure.azure_active_directory import AdalAuthentication
    from azure.mgmt.resource import ResourceManagementClient

    # Service Principal
    tenant = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    client_id = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    password = 'password

    # Government
    authentication_endpoint = 'https://login-us.microsoftonline.com/'
    azure_endpoint = 'https://management.usgovcloudapi.net/'
        
    context = adal.AuthenticationContext(authentication_endpoint+tenant)
    credentials = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        azure_endpoint,
        client_id,
        password
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

    import adal
    from msrestazure.azure_active_directory import AdalAuthentication
    from azure.mgmt.resource import ResourceManagementClient

    # Service Principal
    tenant = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    client_id = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    password = 'password

    # Azure Germany
    authentication_endpoint = 'https://login.microsoftonline.de/'
    azure_endpoint = 'https://management.microsoftazure.de/'
        
    context = adal.AuthenticationContext(authentication_endpoint+tenant)
    credentials = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        azure_endpoint,
        client_id,
        password
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

    import adal
    from msrestazure.azure_active_directory import AdalAuthentication
    from azure.mgmt.resource import ResourceManagementClient

    # Service Principal
    tenant = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    client_id = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    password = 'password

    # Azure China
    authentication_endpoint = 'https://login.chinacloudapi.cn/'
    azure_endpoint = 'https://management.chinacloudapi.cn/'
        
    context = adal.AuthenticationContext(authentication_endpoint+tenant)
    credentials = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        azure_endpoint,
        client_id,
        password
    )
    subscription_id = '33333333-3333-3333-3333-333333333333'

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id,
        base_url=azure_endpoint
    )
