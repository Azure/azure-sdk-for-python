====================
Azure SDK for Python
====================

.. important:: You can find all of the Python on Azure documentation at https://docs.microsoft.com/python/azure

The Azure SDK for Python is a set of libraries which allow you to work on Azure for your management, runtime or data needs.

For a more general view of Azure and Python, you can go on the `Python Developer Center for Azure <https://azure.microsoft.com/en-us/develop/python/>`_


Installation
------------

You can install individually each library for each Azure service:

.. code-block:: console

   $ pip install azure-batch          # Install the latest Batch runtime library
   $ pip install azure-mgmt-scheduler # Install the latest Storage management library

Preview packages can be installed using the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure-mgmt-compute # will install only the latest Compute Management library

More details and information about the available libraries and their status can be found
in the :doc:`Installation Page<installation>`


System Requirements:
--------------------

The supported Python versions are 2.7.x, 3.4.x, 3.5.x, 3.6.x and 3.7.x
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

.. toctree::
  :glob:
  :caption: User Documentation

  installation
  quickstart_authentication
  mgmt_preview_quickstart
  python_mgmt_migration_guide
  multicloud
  exceptions
  Service Management (Legacy) <servicemanagement>

.. include:: toc_tree.rst
