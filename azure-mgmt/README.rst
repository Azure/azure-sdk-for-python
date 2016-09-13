Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure Resource Management bundle.

Azure Resource Manager (ARM) is the next generation of management APIs that
replace the old Azure Service Management (ASM).

This package does not contain any code in itself. It installs a set
of packages that provide management APIs for the various Azure services.

All packages in this bundle have been tested with Python 2.7, 3.3, 3.4 and 3.5.

For a more complete set of Azure libraries, see the `azure <https://pypi.python.org/pypi/azure>`__ bundle package.


Compatibility
=============

**IMPORTANT**: If you have an earlier version of the azure package
(version < 1.0), you should uninstall it before installing this package.

You can check the version using pip:

.. code:: shell

    pip freeze

If you see azure==0.11.0 (or any version below 1.0), uninstall it first:

.. code:: shell

    pip uninstall azure


Features
========

This version of the Azure Management package bundle consists of the
following packages. Follow the links for more information on each package.

-  `azure-mgmt-batch v1.0.0 <https://pypi.python.org/pypi/azure-mgmt-batch/1.0.0>`__
-  `azure-mgmt-logic v1.0.0 <https://pypi.python.org/pypi/azure-mgmt-logic/1.0.0>`__
-  `azure-mgmt-redis v1.0.0 <https://pypi.python.org/pypi/azure-mgmt-redis/1.0.0>`__
-  `azure-mgmt-scheduler v1.0.0 <https://pypi.python.org/pypi/azure-mgmt-scheduler/1.0.0>`__
-  `azure-mgmt-compute v0.30.0rc6 <https://pypi.python.org/pypi/azure-mgmt-compute/0.30.0rc6>`__
-  `azure-mgmt-keyvault v0.30.0rc6 <https://pypi.python.org/pypi/azure-mgmt-keyvault/0.30.0rc6>`__
-  `azure-mgmt-network v0.30.0rc6 <https://pypi.python.org/pypi/azure-mgmt-network/0.30.0rc6>`__
-  `azure-mgmt-resource v0.30.0rc6 <https://pypi.python.org/pypi/azure-mgmt-resource/0.30.0rc6>`__
-  `azure-mgmt-storage v0.30.0rc6 <https://pypi.python.org/pypi/azure-mgmt-storage/0.30.0rc6>`__

Note that if you don't need all of these packages, you can install/uninstall them individually.


Installation
============

To install the Azure Resource Management bundle, type:

.. code:: shell

    pip install azure-mgmt

