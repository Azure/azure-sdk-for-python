Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure ServiceBus Client Library.

This package has been tested with Python 2.7, 3.4, 3.5, 3.6 and 3.7.

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


Usage
=====

For reference documentation and code snippets see `ServiceBus
<https://docs.microsoft.com/python/api/overview/azure/servicebus>`__
on docs.microsoft.com.


Migration from 0.21.1 to 0.50.0
===============================

Major breaking changes were introduced in version 0.50.0. However the original API from version 0.21.1 is still available
under a new namespace:

.. code:: python

    from azure.servicebus.control_client import ServiceBusService

    key_name = 'RootManageSharedAccessKey' # SharedAccessKeyName from Azure portal
    key_value = '' # SharedAccessKey from Azure portal
    sbs = ServiceBusService(service_namespace,
                            shared_access_key_name=key_name,
                            shared_access_key_value=key_value)


For more information on how to port your code to the new API, please see `ServiceBus
<https://docs.microsoft.com/python/api/overview/azure/servicebus>`__
on docs.microsoft.com.


Provide Feedback
================

If you encounter any bugs or have suggestions, please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.
