Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure ServiceBus Client Library.

This package has been tested with Python 2.7, 3.4, 3.5, 3.6 and 3.7.

For a more complete set of Azure libraries, see the `azure <https://pypi.python.org/pypi/azure>`__ bundle package.


Migration from 0.21.1 to 0.50.0
===============================

Major breaking changes were introduced in version 0.50.0.
The original HTTP-based API is still available in v0.50.0 - however it now exists under a new namesapce: `azure.servicebus.control_client`.
The new package introduces a new AMQP-based API for sending and receiving messages.


Should I upgrade?
-----------------

The new package (v0.50.0) offers no improvements in HTTP-based operations over v0.21.1. The HTTP-based API is identical except
that it now exists under a new namespace. For this reason if you only wish to use HTTP-based operations (`create_queue`, `delete_queue` etc) - there will be
no benefit in upgrading at this time.


What's in the new package?
---------------------------

The new package offers a new AMQP-based API for improved message passing reliability and performance.


How do I migrate my code to the new version?
--------------------------------------------

Code written against v0.21.0 can be ported to version 0.50.0 by simple changing the import namespace:

.. code:: python

    from azure.servicebus.control_client import ServiceBusService

    key_name = 'RootManageSharedAccessKey' # SharedAccessKeyName from Azure portal
    key_value = '' # SharedAccessKey from Azure portal
    sbs = ServiceBusService(service_namespace,
                            shared_access_key_name=key_name,
                            shared_access_key_value=key_value)


Usage
=====

For reference documentation and code snippets see `ServiceBus
<https://docs.microsoft.com/python/api/overview/azure/servicebus>`__
on docs.microsoft.com.


Provide Feedback
================

If you encounter any bugs or have suggestions, please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.
