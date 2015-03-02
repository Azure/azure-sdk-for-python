Microsoft Azure SDK for Python
==============================

This project provides a set of Python packages that make it easy to
access the Microsoft Azure storage and queue services. For documentation
on how to host Python applications on Microsoft Azure, please see the
`Microsoft Azure <http://azure.microsoft.com/en-us/develop/python/>`__
Python Developer Center.

The SDK supports Python 2.7, 3.3, 3.4.

Features
========

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

Getting Started
===============

Download Source Code
--------------------

To get the source code of the SDK via **git** just type:

.. code:: shell

    git clone https://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python

Download Package
----------------

Alternatively, to get the source code via the Python Package Index
(PyPI), type

.. code:: shell

    %SystemDrive%\Python27\Scripts\pip.exe install azure

You can use these packages against the cloud Microsoft Azure Services,
or against the local Storage Emulator (with the exception of Service Bus
features).

1. To use the cloud services, you need to first create an account with
   Microsoft Azure. To use the storage services, you need to set the
   AZURE\_STORAGE\_ACCOUNT and the AZURE\_STORAGE\_ACCESS\_KEY
   environment variables to the storage account name and primary access
   key you obtain from the Azure Portal. To use Service Bus, you need to
   set the AZURE\_SERVICEBUS\_NAMESPACE and the
   AZURE\_SERVICEBUS\_ACCESS\_KEY environment variables to the service
   bus namespace and the default key you obtain from the Azure Portal.
2. To use the Storage Emulator, make sure the latest version of the
   Microsoft Azure SDK is installed on the machine, and set the EMULATED
   environment variable to any value ("true", "1", etc.)

Usage
=====
For detailed usage information please view our documentation at `azure-sdk-for-python.ReadTheDocs.org <http://azure-sdk-for-python.readthedocs.org>`__

\*\* For more examples please see the `Microsoft Azure Python Developer
Center <http://azure.microsoft.com/en-us/develop/python/>`__ \*\*

Need Help?
==========

Be sure to check out the Microsoft Azure `Developer Forums on Stack
Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__ if you have
trouble with the provided code.

Contribute Code or Provide Feedback
===================================

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
