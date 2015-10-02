Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure Resource Management bundle.

Azure Resource Manager (ARM) is the next generation of management APIs that
replace the old Azure Service Management (ASM).

This package does not contain any code in itself. It installs a set
of packages that provide management APIs for the various Azure services.

All packages in this bundle have been tested with Python 2.7, 3.3 and 3.4.

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


This is a preview release
=========================

The ARM libraries are being released as a preview, to solicit feedback.

**Future releases are subject to breaking changes**.

The Python code generator used to create this version of the ARM
libraries is being replaced, and may not generate code that is compatible
with this version of the ARM libraries.

Although future revisions will likely have breaking changes, the ARM concepts
along with the REST APIs that the library is wrapping should remain the same.

Please try the libraries and give us feedback, which we can incorporate into
future versions.

If you prefer to use the older Azure Service Management (ASM) APIs, see the
`azure-servicemanagement-legacy <https://pypi.python.org/pypi/azure-servicemanagement-legacy>`__ library.


Features
========

This version of the Azure Management package bundle consists of the
following packages. Follow the links for more information on each package.

-  `azure-mgmt-compute v0.20.0 <https://pypi.python.org/pypi/azure-mgmt-compute/0.20.0>`__
-  `azure-mgmt-network v0.20.1 <https://pypi.python.org/pypi/azure-mgmt-network/0.20.1>`__
-  `azure-mgmt-resource v0.20.1 <https://pypi.python.org/pypi/azure-mgmt-resource/0.20.1>`__
-  `azure-mgmt-storage v0.20.0 <https://pypi.python.org/pypi/azure-mgmt-storage/0.20.0>`__

Note that if you don't need all of these packages, you can install/uninstall them individually.


Installation
============

To install the Azure Resource Management bundle, type:

.. code:: shell

    pip install azure-mgmt

