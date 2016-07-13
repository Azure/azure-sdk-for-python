Azure SDK for Python
====================

Installation:
-------------

**The latest recommended release is currently a release candidate, tell this to pip to install it!**

- Use the ``--pre`` flag: ``pip install --pre azure``

- Specify the version:  ``pip install azure==2.0.0rc5``

If you want to install ``azure`` from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install

DISCLAIMER
----------

This is a release candidate. It could have minor breaking changes until the stable release.

Some of the new generated libraries have not yet been tested extensively, and some have known issues (such as azure-mgmt-web).

Our goal is to release a stable version by July 2016.  Please send us your feedback!

Documentation:
--------------
* Azure Resource Management
   * :doc:`Authorization Resource Management<resourcemanagementauthorization>` -- (:doc:`API <ref/azure.mgmt.authorization>`)
   * :doc:`Batch Management<resourcemanagementbatch>` -- (:doc:`API <ref/azure.mgmt.batch>`)
   * :doc:`CDN Resource Management<resourcemanagementcdn>` -- (:doc:`API <ref/azure.mgmt.cdn>`)
   * :doc:`Commerce - Billing API<resourcemanagementcommerce>` -- (:doc:`API <ref/azure.mgmt.commerce>`)
   * :doc:`Cognitive Services Management<resourcemanagementcognitiveservices>` -- (:doc:`API <ref/azure.mgmt.cognitiveservices>`)
   * :doc:`Compute Resource Management<resourcemanagementcomputenetwork>` -- (:doc:`API <ref/azure.mgmt.compute>`)
   * Apps
      * :doc:`Logic Apps Resource Management<resourcemanagementapps>` -- (:doc:`API <ref/azure.mgmt.logic>`)
      * :doc:`Web Apps Management<resourcemanagementapps>` -- (:doc:`API <ref/azure.mgmt.web>`)
   * :doc:`KeyVault Management<resourcemanagementkeyvault>` -- (:doc:`API <ref/azure.mgmt.keyvault>`)
   * :doc:`Network Resource Management<resourcemanagementcomputenetwork>` -- (:doc:`API <ref/azure.mgmt.network>`)
   * :doc:`Notification Hubs Resource Management<resourcemanagementnotificationhubs>` -- (:doc:`API <ref/azure.mgmt.notificationhubs>`)
   * :doc:`PowerBI Embedded Management<resourcemanagementpowerbiembedded>` -- (:doc:`API <ref/azure.mgmt.powerbiembedded>`)
   * :doc:`Redis Cache Resource Management<resourcemanagementredis>` -- (:doc:`API <ref/azure.mgmt.redis>`)
   * :doc:`Resource Management<resourcemanagement>` -- (:doc:`API <ref/azure.mgmt.resource>`)   
   * :doc:`Scheduler Management<resourcemanagementscheduler>` -- (:doc:`API <ref/azure.mgmt.scheduler>`)
   * :doc:`Storage Resource Management<resourcemanagementstorage>` -- (:doc:`API <ref/azure.mgmt.storage>`)
* :doc:`Batch<batch>` -- (:doc:`API <ref/azure.batch>`)
* :doc:`Azure Active Directory Graph RBAC<graphrbac>` -- (:doc:`API <ref/azure.graphrbac>`)
* :doc:`Service Management<servicemanagement>` -- (:doc:`API <ref/azure.servicemanagement>`)
* :doc:`Service Bus<servicebus>` -- (:doc:`API <ref/azure.servicebus>`)
* `Storage <http://azure-storage.readthedocs.org>`__
* :ref:`All Documentation <modindex>`


Features:
---------

-  Storage Blob, File, Table, Queue

   -  see the Azure storage `Git repository <https://github.com/Azure/azure-storage-python>`__
      or `readthedocs <http://azure-storage.readthedocs.org>`__ for a
      complete list of supported features.

-  Service Bus

   -  Queues: create, list and delete queues; create, list, and delete
      subscriptions; send, receive, unlock and delete messages
   -  Topics: create, list, and delete topics; create, list, and delete
      rules

- Batch Runtime

   - Manage Batch pools, jobs, task and job schedules

- Azure Active Directory Graph RBAC API
  
   - Users
   - Applications
   - and more
      
-  Resource Management

   -  Authorization: permissions, subscriptions, roles and more
   -  Batch: manage Batch accounts and applications
   -  CDN: profiles, endpoints creation and more
   -  Commerce: RateCard and Usage Billing API
   -  Cognitive Services: Manage your accounts
   -  Compute: create virtual machines and more
   -  Apps:

      - Logic Apps: Workflow and job management
      - Web Apps: App Service Plan, web sites, certificate, domains and more

   -  Network: create virtual networks, network interfaces, public ips and more
   -  Notification Hubs: Namespaces, hub creation/deletion and more
   -  PowerBI Embedded: Manage your workspaces
   -  Redis: create cache and more
   -  Resource:
   
        - resources :  create resource groups, register providers and more
        - features : manage features of provider and more
        - locks : manage resource group lock and more
        - subscriptions : manage subscriptions and more

   -  Scheduler: create job collections, create job and more
   -  Storage: create storage accounts, list keys, and more

-  Service Management

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

The supported Python versions are 2.7.x, 3.3.x, 3.4.x, and 3.5.x
To download Python, please visit
https://www.python.org/download/


We recommend Python Tools for Visual Studio as a development environment for developing your applications.  Please visit http://aka.ms/python for more information.


Need Help?:
-----------

Be sure to check out the Microsoft Azure `Developer Forums on Stack
Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__ if you have
trouble with the provided code.

Contributing:
-------------
Contribute Code or Provide Feedback:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you would like to become an active contributor to this project please
follow the instructions provided in `Microsoft Azure Projects
Contribution
Guidelines <http://windowsazure.github.com/guidelines.html>`__.

If you encounter any bugs with the library please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.

Learn More
==========

`Microsoft Azure Python Developer
Center <http://azure.microsoft.com/en-us/develop/python/>`__


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :hidden:

.. toctree::
  :hidden:
  :glob:

  servicebus
  graphrbac
  resourcemanagement
  resourcemanagementauthentication
  resourcemanagamentauthorization
  resourcemanagementcommerce
  resourcemanagementcdn
  resourcemanagementapps
  resourcemanagementstorage
  resourcemanagementcomputenetwork
  resourcemanagementscheduler
  resourcemanagementredis
  resourcemanagementnotificationhubs
  servicemanagement
  ref/*  
