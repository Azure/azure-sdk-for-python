Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure bundle.

This package does not contain any code in itself. It installs a set
of packages that provide Microsoft Azure functionality.

All packages in this bundle have been tested with Python 2.7, 3.3, 3.4 and 3.5.


Features
========

This version of the Azure package bundle consists of the following
packages. Follow the links for more information on each package.

-  `azure-mgmt v0.30.0rc6 <https://pypi.python.org/pypi/azure-mgmt/0.30.0rc6>`__
-  `azure-batch v1.0.0 <https://pypi.python.org/pypi/azure-batch/1.0.0>`__
-  `azure-servicebus v0.20.3 <https://pypi.python.org/pypi/azure-servicebus/0.20.3>`__
-  `azure-servicemanagement-legacy v0.20.4 <https://pypi.python.org/pypi/azure-servicemanagement-legacy/0.20.4>`__
-  `azure-storage v0.33.0 <https://pypi.python.org/pypi/azure-storage/0.33.0>`__

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


Uninstall
=========

Installing the azure bundle package installs several packages.

Use the following script to uninstall all of them.

.. code:: shell

    pip uninstall azure
    pip uninstall azure-mgmt
    pip uninstall azure-mgmt-batch
    pip uninstall azure-mgmt-compute
    pip uninstall azure-mgmt-keyvault
    pip uninstall azure-mgmt-network
    pip uninstall azure-mgmt-resource
    pip uninstall azure-mgmt-storage
    pip uninstall azure-mgmt-nspkg
    pip uninstall azure-batch
    pip uninstall azure-servicebus
    pip uninstall azure-storage
    pip uninstall azure-common
    pip uninstall azure-nspkg
