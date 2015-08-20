Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure bundle.

This package does not contain any code by itself. It installs a set
of packages that provide Microsoft Azure functionality.

All packages have been tested with Python 2.7, 3.3 and 3.4.


Features
========

This version of the Azure package bundle consists of the following
packages. Follow the links for more information on each package.

-  `azure-mgmt v0.20.0 <https://pypi.python.org/pypi/azure-mgmt/0.20.0>`__
-  `azure-servicebus v0.20.0 <https://pypi.python.org/pypi/azure-servicebus/0.20.0>`__
-  `azure-servicemanagement-legacy v0.20.0 <https://pypi.python.org/pypi/azure-servicemanagement-legacy/0.20.0>`__
-  `azure-storage v0.20.0 <https://pypi.python.org/pypi/azure-storage/0.20.0>`__


Installation
============

To install the Azure package bundle, type:

.. code:: shell

    pip install azure

You can also install them individually (see the next section for an important note regarding the upgrade scenario).


Upgrade
=======

**IMPORTANT**: If you have an earlier version of the azure package (version < 1.0), you should either

-  Install the new version of the azure package, which will automatically uninstall your previous version.
-  Uninstall the azure package, then install the individual packages ie. azure-storage, azure-servicebus, etc.  You cannot have the old azure<1.0 package and the new individual packages at the same time.

See the `change log <https://github.com/Azure/azure-sdk-for-python/blob/master/ChangeLog.txt>`__ for information on breaking changes. For version 1.0, we've moved a lot of code around and did some renaming.
