====================
Azure SDK for Python
====================

The Azure SDK for Python is a set of libraries which allow you to work on Azure for your management, runtime or data needs.

For a more general view of Azure and Python, you can go on the `Python Developer Center for Azure <https://azure.microsoft.com/en-us/develop/python/>`_

Example Usage
-------------

This example shows:

* Authentication on Azure using an AD in your subscription,
* Creation of a Resource Group and a Storage account,
* Upload a simple "Hello world" HTML page and gives you the URL to get it.

.. code:: python

    from azure.common.credentials import UserPassCredentials
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.storage import CloudStorageAccount
    from azure.storage.blob.models import ContentSettings, PublicAccess

    credentials = UserPassCredentials('user@domain.com', 'my_smart_password')
    subscription_id = '33333333-3333-3333-3333-333333333333'

    resource_client = ResourceManagementClient(credentials, subscription_id)
    storage_client = StorageManagementClient(credentials, subscription_id)

    resource_group_name = 'my_resource_group'
    storage_account_name = 'myuniquestorageaccount'

    resource_client.resource_groups.create_or_update(
        resource_group_name,
        {
            'location':'westus'
        }
    )

    async_create = storage_client.storage_accounts.create(
        resource_group_name,
        storage_account_name,
        {
            'location':'westus',
            'kind':'storage',
            'sku': {
                'name':'standard_ragrs'
            }
        }
    )
    async_create.wait()

    storage_keys = storage_client.storage_accounts.list_keys(resource_group_name, storage_account_name)
    storage_keys = {v.key_name: v.value for v in storage_keys.keys}

    storage_client = CloudStorageAccount(storage_account_name, storage_keys['key1'])
    blob_service = storage_client.create_block_blob_service()

    blob_service.create_container(
        'mycontainername',
        public_access=PublicAccess.Blob
    )

    blob_service.create_blob_from_bytes(
        'mycontainername',
        'myblobname',
        b'<center><h1>Hello World!</h1></center>',
        content_settings=ContentSettings('text/html')
    )

    print(blob_service.make_blob_url('mycontainername', 'myblobname'))


Installation
------------

Overview
^^^^^^^^

You can install individually each library for each Azure service:

.. code-block:: console

   $ pip install azure-batch          # Install the latest Batch runtime library
   $ pip install azure-mgmt-scheduler # Install the latest Storage management library

Preview packages can be installed using the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure-mgmt-compute # will install only the latest Compute Management library

More details and information about the available libraries and their status can be found 
in the :doc:`Installation Page<installation>`

The ``azure`` meta-package
^^^^^^^^^^^^^^^^^^^^^^^^^^
   
You can also install a set of Azure libraries in a single line using the ``azure`` meta-package. Since not all packages in this meta-package are
published as stable yet, the ``azure`` meta-package is still in preview. 
However, the core packages, from code quality/completeness perspectives can at this time be considered "stable" 
- it will be officially labeled as such in sync with other languages as soon as possible. 
We are not planning on any further major changes until then.

Since it's a preview release, you need to use the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure
   
or directly

.. code-block:: console

   $ pip install azure==2.0.0rc6

.. important:: The azure meta-package 1.0.3 is deprecated and is not working anymore.
   
Features
--------

Azure Resource Management
^^^^^^^^^^^^^^^^^^^^^^^^^

All documentation of management libraries for Azure are on this website. This includes:

* :doc:`Authorization <sample_azure-mgmt-authorization>` : Permissions, roles and more
* :doc:`Batch<resourcemanagementbatch>` : Manage Batch accounts and applications
* :doc:`Content Delivery Network<resourcemanagementcdn>` : Profiles, endpoints creation and more
* :doc:`Cognitive Services<sample_azure-mgmt-cognitiveservices>` : Create CS accounts and more
* :doc:`Commerce - Billing API<resourcemanagementcommerce>` : RateCard and Usage Billing API
* :doc:`Compute<resourcemanagementcomputenetwork>` : Create virtual machines and more
* :doc:`Data Lake Analytics<sample_azure-mgmt-datalake-analytics>` : Manage account, job, catalog and more
* :doc:`Data Lake Store<sample_azure-mgmt-datalake-store>` : Manage account and more
* :doc:`DevTestLabs<sample_azure-mgmt-devtestlabs>` : Create labs and more
* :doc:`DNS<sample_azure-mgmt-dns>` : Create DNS zone, record set and more
* :doc:`IoTHub<sample_azure-mgmt-iothub>` : Create IoTHub account and more
* :doc:`KeyVault<sample_azure-mgmt-keyvault>` : Create vaults and more
* :doc:`App Service<resourcemanagementapps>` : Create App plan, Web Apps, Logic Apps and more
* :doc:`Media Services<sample_azure-mgmt-media>` : Create account and more
* :doc:`Network<resourcemanagementcomputenetwork>` : Create virtual networks, network interfaces, public IPs and more
* :doc:`Notification Hubs<resourcemanagementnotificationhubs>` : Namespaces, hub creation/deletion and more
* :doc:`PowerBI Embedded<sample_azure-mgmt-powerbiembedded>` : Create account and more
* :doc:`Redis Cache<resourcemanagementredis>` : Create cache and more
* :doc:`Resource Management<resourcemanagement>`:

  * resources :  create resource groups, register providers and more
  * features : manage features of provider and more
  * locks : manage resource group lock and more
  * subscriptions : manage subscriptions and more
  
* :doc:`Scheduler<resourcemanagementscheduler>` : Create job collections, create job and more
* :doc:`Server Manager<sample_azure-mgmt-servermanager>` : Create gateways, nodes and more
* :doc:`SQL Database<sample_azure-mgmt-sql>` : Create servers, databases nodes and more
* :doc:`Storage<resourcemanagementstorage>` : Create storage accounts, list keys, and more
* :doc:`Traffic Manager<sample_azure-mgmt-trafficmanager>` : Create endpoints, profiles and more

Azure Runtime
^^^^^^^^^^^^^

Some documentation of data libraries are on this website. This includes:

* :doc:`Batch<batch>`
* :doc:`Key Vault<sample_azure-keyvault>`
* :doc:`Azure Monitor<sample_azure-monitor>`
* :doc:`Azure Active Directory Graph RBAC<graphrbac>`
* :doc:`Service Bus<servicebus>` using HTTP.

  .. note:: For critical performance issue, the Service Bus team currently recommends `AMQP <https://azure.microsoft.com/en-us/documentation/articles/service-bus-amqp-python/>`_.

These Azure services have Python data libraries which are directly hosted by the service team or are extensively documented on the Azure documentation website:

* `Storage <http://azure-storage.readthedocs.io>`_
* `Azure Data Lake Store Filesystem <http://azure-datalake-store.readthedocs.io/>`_
* `Azure IoT Hub service and device SDKs for Python <https://github.com/Azure/azure-iot-sdk-python>`_
* `SQL Azure <https://azure.microsoft.com/en-us/documentation/articles/sql-database-develop-python-simple/>`_
* `DocumentDB <https://azure.microsoft.com/en-us/documentation/articles/documentdb-sdk-python/>`_
* `Application Insight <https://github.com/Microsoft/ApplicationInsights-Python>`_
* `Redis Cache <https://azure.microsoft.com/en-us/documentation/articles/cache-python-get-started/>`_
* `Write an Azure WebApp in Python <https://azure.microsoft.com/en-us/documentation/articles/web-sites-python-create-deploy-django-app/>`_


Azure Service Management
^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: The Service Management SDK is deprecated and no more features will be added.

This page describes the :doc:`usage and detailed features of Azure Service Management SDK<servicemanagement>`. At a glance:

   -  storage accounts: create, update, delete, list, regenerate keys
   -  affinity groups: create, update, delete, list, get properties
   -  locations: list
   -  hosted services: create, update, delete, list, get properties
   -  deployment: create, get, delete, swap, change configuration,
      update status, upgrade, rollback
   -  role instance: reboot, reimage
   -  discover addresses and ports for the endpoints of other role
      instances in your service
   -  get configuration settings and access local resources
   -  get role instance information for current role and other role
      instances
   -  query and set the status of the current role

System Requirements:
--------------------

The supported Python versions are 2.7.x, 3.3.x, 3.4.x, 3.5.x and 3.6.x
To download Python, please visit
https://www.python.org/download/


We recommend Python Tools for Visual Studio as a development environment for developing your applications.  Please visit http://aka.ms/python for more information.


Need Help?:
-----------

Be sure to check out the Microsoft Azure `Developer Forums on Stack
Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__ if you have
trouble with the provided code.

Contribute Code or Provide Feedback:
------------------------------------

If you would like to become an active contributor to this project please
follow the instructions provided in `Microsoft Azure Projects
Contribution
Guidelines <http://windowsazure.github.com/guidelines.html>`__.

If you encounter any bugs with the library please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :glob:
  :caption: User Documentation

  installation
  quickstart_authentication
  multicloud
  exceptions
  
.. toctree::
  :glob:
  :caption: Management Documentation

  resourcemanagement*
  sample_azure-mgmt-*
  Service Management (Legacy) <servicemanagement>
  
.. toctree::
  :glob:
  :caption: Runtime Documentation

  batch
  sample_azure-monitor
  sample_azure-keyvault
  graphrbac
  servicebus
  
.. include:: autorest_generated_packages.rst
