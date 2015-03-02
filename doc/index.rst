.. pydocumentdb documentation master file, created by
   sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Azure SDK for Python.
========================================

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
* :doc:`ServiceManagement<servicemanagement>` -- (:doc:`API <ref/azure.servicemanagement>`)
* :doc:`ServiceBus<servicebus>` -- (:doc:`API <ref/azure.servicebus>`)
* :doc:`Storage<storage>` -- (:doc:`API <ref/azure.storage>`)
* :ref:`All Documentation <modindex>`


Features:
---------

-  Tables

   -  create and delete tables
   -  create, query, insert, update, merge, and delete entities

-  Blobs

   -  create, list, and delete containers, work with container metadata
      and permissions, list blobs in container
   -  create block and page blobs (from a stream, a file, or a string),
      work with blob blocks and pages, delete blobs
   -  work with blob properties, metadata, leases, snapshot a blob

-  Storage Queues

   -  create, list, and delete queues, and work with queue metadata
   -  create, get, peek, update, delete messages

-  Service Bus

   -  Queues: create, list and delete queues; create, list, and delete
      subscriptions; send, receive, unlock and delete messages
   -  Topics: create, list, and delete topics; create, list, and delete
      rules

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

To run tests:
~~~~~~~~~~~~~
To run the tests for the Azure SDK for Python::

    TODO.

To generate documentation:
~~~~~~~~~~~~~~~~~~~~~~~~~~~
To generate the documentation run::

    cd doc
    BuildDocs.bat

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
  servicemanagement
  storage
  ref/*  
