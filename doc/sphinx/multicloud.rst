Multi-cloud - use Azure on all regions
======================================

You can use the Azure SDK for Python to connect to all regions where Azure is available
(`list of Azure regions is available here <https://azure.microsoft.com/regions/services>`_).

By default, the Azure SDK for Python is configured to connect to public Azure.

Using predeclared cloud definition
----------------------------------

.. important:: The `msrestazure` package must be superior or equals to 0.4.11 for this section.

You can use the `azure_cloud` module of `msrestazure`

.. code:: python

  from msrestazure.azure_cloud import AZURE_CHINA_CLOUD
  from msrestazure.azure_active_directory import UserPassCredentials
  from azure.mgmt.resource import ResourceManagementClient

  credentials = UserPassCredentials(
      login,
      password,
      cloud_environment=AZURE_CHINA_CLOUD
  )
  client = ResourceManagementClient(
      credentials,
      subscription_id,
      base_url=AZURE_CHINA_CLOUD.endpoints.resource_manager
  )
  
Available cloud definition are
  - AZURE_PUBLIC_CLOUD
  - AZURE_CHINA_CLOUD
  - AZURE_US_GOV_CLOUD
  - AZURE_GERMAN_CLOUD

Using your own cloud definition (e.g. Azure Stack)
--------------------------------------------------

ARM has a metadata endpoint to help you:

.. code:: python

  from msrestazure.azure_cloud import get_cloud_from_metadata_endpoint
  from msrestazure.azure_active_directory import UserPassCredentials
  from azure.mgmt.resource import ResourceManagementClient

  mystack_cloud = get_cloud_from_metadata_endpoint("https://myazurestack-arm-endpoint.com")
  credentials = UserPassCredentials(
      login,
      password,
      cloud_environment=mystack_cloud
  )
  client = ResourceManagementClient(
      credentials,
      subscription_id,
      base_url=mystack_cloud.endpoints.resource_manager
  )

Using ADAL
----------

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
~~~~~~~~~~~~~~~~

.. code:: python

    import adal
    from msrestazure.azure_active_directory import AdalAuthentication
    from azure.mgmt.resource import ResourceManagementClient

    # Service Principal
    tenant = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    client_id = 'ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL'
    password = 'password

    # Government
    authentication_endpoint = 'https://login.microsoftonline.us/'
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
~~~~~~~~~~~~~

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
~~~~~~~~~~~

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
