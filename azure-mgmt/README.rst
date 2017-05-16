Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure Resource Management bundle.

Azure Resource Manager (ARM) is the next generation of management APIs that
replace the old Azure Service Management (ASM).

This package does not contain any code in itself. It installs a set
of packages that provide management APIs for the various Azure services.

All packages in this bundle have been tested with Python 2.7, 3.3, 3.4, 3.5 and 3.6.

This package uses PEP440 syntax, and then requires pip >= 6.0 and/or setuptools >= 8.0
to be installed.

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
Note that versions are fixed at the patch version number level.

-  `azure-mgmt-authorization v0.30.x <https://pypi.python.org/pypi/azure-mgmt-authorization/0.30.0>`__
-  `azure-mgmt-batch v4.0.x <https://pypi.python.org/pypi/azure-mgmt-batch/4.0.0>`__
-  `azure-mgmt-cdn v0.30.x <https://pypi.python.org/pypi/azure-mgmt-cdn/0.30.3>`__
-  `azure-mgmt-cognitiveservices v1.0.x <https://pypi.python.org/pypi/azure-mgmt-cognitiveservices/1.0.0>`__
-  `azure-mgmt-compute v1.0.x <https://pypi.python.org/pypi/azure-mgmt-compute/1.0.0>`__
-  `azure-mgmt-containerregistry v0.2.x <https://pypi.python.org/pypi/azure-mgmt-containerregistry/0.2.1>`__
-  `azure-mgmt-datalake-analytics v0.1.x <https://pypi.python.org/pypi/azure-mgmt-datalake-analytics/0.1.4>`__
-  `azure-mgmt-datalake-store v0.1.x <https://pypi.python.org/pypi/azure-mgmt-datalake-store/0.1.4>`__
-  `azure-mgmt-devtestlabs v2.0.x <https://pypi.python.org/pypi/azure-mgmt-devtestlabs/2.0.0>`__
-  `azure-mgmt-dns v1.0.x <https://pypi.python.org/pypi/azure-mgmt-dns/1.0.1>`__
-  `azure-mgmt-documentdb v0.1.x <https://pypi.python.org/pypi/azure-mgmt-documentdb/0.1.3>`__
-  `azure-mgmt-iothub v0.2.x <https://pypi.python.org/pypi/azure-mgmt-iothub/0.2.2>`__
-  `azure-mgmt-keyvault v0.31.x <https://pypi.python.org/pypi/azure-mgmt-keyvault/0.31.0>`__
-  `azure-mgmt-logic v2.1.x <https://pypi.python.org/pypi/azure-mgmt-logic/2.1.0>`__
-  `azure-mgmt-network v1.0.x <https://pypi.python.org/pypi/azure-mgmt-network/1.0.0>`__
-  `azure-mgmt-rdbms v0.1.x <https://pypi.python.org/pypi/azure-mgmt-rdbms/0.1.0>`__
-  `azure-mgmt-redis v4.1.x <https://pypi.python.org/pypi/azure-mgmt-redis/4.1.0>`__
-  `azure-mgmt-resource v1.1.x <https://pypi.python.org/pypi/azure-mgmt-resource/1.1.0>`__
-  `azure-mgmt-scheduler v1.1.x <https://pypi.python.org/pypi/azure-mgmt-scheduler/1.1.2>`__
-  `azure-mgmt-sql v0.5.x <https://pypi.python.org/pypi/azure-mgmt-sql/0.5.1>`__
-  `azure-mgmt-storage v1.0.x <https://pypi.python.org/pypi/azure-mgmt-storage/1.0.0>`__
-  `azure-mgmt-trafficmanager v0.30.x <https://pypi.python.org/pypi/azure-mgmt-trafficmanager/0.30.0>`__
-  `azure-mgmt-web v0.32.x <https://pypi.python.org/pypi/azure-mgmt-web/0.32.0>`__

Note that if you don't need all of these packages, you can install/uninstall them individually.


Installation
============

To install the Azure Resource Management bundle, type:

.. code:: shell

    pip install azure-mgmt

