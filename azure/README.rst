Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure bundle.

This package does not contain any code in itself. It installs a set
of packages that provide Microsoft Azure functionality.

All packages in this bundle have been tested with Python 2.7, 3.4, 3.5, 3.6 and 3.7

This package uses PEP440 syntax, and thus requires pip >= 6.0 and/or setuptools >= 8.0
to be installed.


Documentation
=============

All documentation related to these packages can be found at http://docs.microsoft.com/python/azure/


Features
========

This version of the Azure package bundle consists of the following
packages. Follow the links for more information on each package.
Note that versions are fixed at the minor version number level
(i.e. no breaking changes can be introduced, but features are allowed)

-  `azure-mgmt v4.x <https://pypi.python.org/pypi/azure-mgmt>`__
-  `azure-applicationinsights v0.1.x <https://pypi.python.org/pypi/azure-applicationinsights>`__
-  `azure-batch v4.x <https://pypi.python.org/pypi/azure-batch>`__
-  `azure-cosmosb-table v1.x <https://pypi.python.org/pypi/azure-cosmosdb-table>`__
-  `azure-datalake-store v0.0.x <https://pypi.python.org/pypi/azure-datalake-store>`__
-  `azure-eventgrid v1.x <https://pypi.python.org/pypi/azure-eventgrid>`__
-  `azure-graphrbac v0.40.x <https://pypi.python.org/pypi/azure-graphrbac>`__
-  `azure-keyvault v1.x <https://pypi.python.org/pypi/azure-keyvault>`__
-  `azure-loganalytics v0.1.x <https://pypi.python.org/pypi/azure-loganalytics>`__
-  `azure-servicebus v0.21.x <https://pypi.python.org/pypi/azure-servicebus>`__
-  `azure-servicefabric v6.3.0.0 <https://pypi.python.org/pypi/azure-servicefabric>`__
-  `azure-servicemanagement-legacy v0.20.x <https://pypi.python.org/pypi/azure-servicemanagement-legacy>`__
-  `azure-storage-blob v1.x <https://pypi.python.org/pypi/azure-storage-blob>`__
-  `azure-storage-queue v1.x <https://pypi.python.org/pypi/azure-storage-queue>`__
-  `azure-storage-file v1.x <https://pypi.python.org/pypi/azure-storage-file>`__

Note that if you don't need all of these packages, you can install/uninstall them individually.


Installation
============

To install the Azure package bundle, type:

.. code:: shell

    pip install azure


Upgrade
=======

This package is not compatible with `azure-storage`.
If you installed `azure-storage`, or if you installed `azure` 1.x/2.x and didn't
uninstall `azure-storage`, you must uninstall `azure-storage` first:

.. code:: shell

    pip uninstall azure-storage


Upgrading from azure<1.0 is not supported. You must uninstall the old version first.

.. code:: shell

    pip uninstall azure
    pip install azure


Compatibility
=============

For details on the breaking changes, see the PyPI page of each individual package.
