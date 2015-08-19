Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure Resource Management Client Library.

Azure Resource Manager (ARM) is the next generation of management APIs that
replace the old Azure Service Management (ASM).


This is a preview release
=========================

The ARM libraries are being released as a preview, to gather feedback.

**Future releases of this library are subject to breaking changes**.

We are working on a new Python REST API code generator, which will replace
our existing code generator. The extent of the breaking changes is unknown
at this time.

Although future revisions will likely have breaking changes, the ARM concepts
along with the REST APIs that the library is wrapping should remain the same.

Please try the libraries and give us feedback, which we can incorporate into
future versions.

If you prefer to use the old Azure Service Management APIs, see the
`azure-servicemanagement-legacy <https://pypi.python.org/pypi/azure-servicemanagement-legacy>`__ library.


Usage
=====

Examples
--------

We'll work on adding some documentation here, but for now, see the following
for examples on using the ARM APIs.

-  `Azure Resource Viewer Web Application Sample <https://github.com/Azure/azure-sdk-for-python/tree/master/examples/AzureResourceViewer>`__
-  `Azure Resource Manager Unit tests <https://github.com/Azure/azure-sdk-for-python/tree/master/azure-mgmt/tests>`__

Authentication
--------------

Authentication with ARM is done via tokens (certificates are not supported).

You can use the `ADAL <https://pypi.python.org/pypi/azure>`__ library to
obtain authentication tokens.


Provide Feedback
================

If you encounter any bugs or have suggestions, please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.
