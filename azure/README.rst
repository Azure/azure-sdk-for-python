Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure bundle.

This package does not contain any code in itself. It installs a set
of packages that provide Microsoft Azure functionality.

All packages in this bundle have been tested with Python 2.7, 3.3, 3.4, 3.5 and 3.6.

This package uses PEP440 syntax, and thus requires pip >= 6.0 and/or setuptools >= 8.0
to be installed.


Features
========

This version of the Azure package bundle consists of the following
packages. Follow the links for more information on each package.
Note that versions are fixed at the patch version number level.

-  `azure-mgmt v1.0.x <https://pypi.python.org/pypi/azure-mgmt/1.0.0>`__
-  `azure-batch v3.0.0 <https://pypi.python.org/pypi/azure-batch/3.0.0>`__
-  `azure-datalake-store v0.0.x <https://pypi.python.org/pypi/azure-datalake-store/0.0.9>`__
-  `azure-graphrbac v0.30.x <https://pypi.python.org/pypi/azure-graphrbac/0.30.0>`__
-  `azure-keyvault v0.3.x <https://pypi.python.org/pypi/azure-keyvault/0.3.3>`__
-  `azure-servicebus v0.21.x <https://pypi.python.org/pypi/azure-servicebus/0.21.1>`__
-  `azure-servicefabric v5.6.130 <https://pypi.python.org/pypi/azure-servicefabric/5.6.130>`__
-  `azure-servicemanagement-legacy v0.20.x <https://pypi.python.org/pypi/azure-servicemanagement-legacy/0.20.6>`__
-  `azure-storage v0.34.x <https://pypi.python.org/pypi/azure-storage/0.34.2>`__

Note that if you don't need all of these packages, you can install/uninstall them individually.


Installation
============

To install the Azure package bundle, type:

.. code:: shell

    pip install azure


Upgrade
=======

Upgrading from azure<1.0 is not supported. You must uninstall the old version first.

.. code:: shell

    pip uninstall azure
    pip install azure


Compatibility
=============

Some breaking changes were introduced in azure==1.0.

If you are porting your code from an older version (<1.0), be prepared
to change some import statements and rename exception classes.

For details on the breaking changes, see the
`change log <https://github.com/Azure/azure-sdk-for-python/blob/master/ChangeLog.txt>`__.
