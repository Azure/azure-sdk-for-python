Azure SDK for Python
====================

Installation:
-------------
 
You can use ``pip`` to install the latest released version of ``azure``::

    pip install azure

If you want to install ``azure`` from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install


Documentation:
--------------
* :doc:`Resource Management<resourcemanagement>` -- (:doc:`API <ref/azure.mgmt.resource>`)
   * :doc:`Compute Resource Management<resourcemanagementcomputenetwork>` -- (:doc:`API <ref/azure.mgmt.compute>`)
   * :doc:`Network Resource Management<resourcemanagementcomputenetwork>` -- (:doc:`API <ref/azure.mgmt.network>`)
   * :doc:`Storage Resource Management<resourcemanagementstorage>` -- (:doc:`API <ref/azure.mgmt.storage>`)
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

-  Resource Management (Preview)

   -  Compute: create virtual machines and more
   -  Network: create virtual networks, network interfaces, public ips and more
   -  Resource: create resource groups, register providers and more
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

The supported Python versions are 2.7.x, 3.3.x, and 3.4.x
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
  resourcemanagement
  resourcemanagementauthentication
  resourcemanagementstorage
  resourcemanagementcomputenetwork
  servicemanagement
  ref/*  
