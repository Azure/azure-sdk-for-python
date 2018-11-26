Microsoft Azure SDK for Event Hubs
==================================

.. image:: https://img.shields.io/pypi/v/azure-eventhub.svg
    :target: https://pypi.python.org/pypi/azure-eventhub/

.. image:: https://img.shields.io/pypi/pyversions/azure-eventhub.svg
    :target: https://pypi.python.org/pypi/azure-eventhub/

.. image:: https://travis-ci.org/Azure/azure-event-hubs-python.svg?branch=master
    :target: https://travis-ci.org/Azure/azure-event-hubs-python


A Python AMQP client for Azure Event Hubs the provides:

- A sender to publish events to the Event Hubs service.
- A receiver to read events from the Event Hubs service.

On Python 3.5 and above, it also includes:

- An async sender and receiver that supports async/await methods.
- An Event Processor Host module that manages the distribution of partition readers.


Installation
============

Wheels are provided for all major operating systems, so you can install directly with pip:

.. code:: shell

    $ pip install azure-eventhub


Documentation
+++++++++++++
Reference documentation is available at `docs.microsoft.com/python/api/azure-eventhub <https://docs.microsoft.com/python/api/azure-eventhub>`__.


Examples
+++++++++

- ./examples/send.py - use sender to publish events
- ./examples/recv.py - use receiver to read events
- ./examples/send_async.py - async/await support of a sender
- ./examples/recv_async.py - async/await support of a receiver
- ./examples/eph.py - event processor host


Logging
++++++++

- enable 'azure.eventhub' logger to collect traces from the library
- enable 'uamqp' logger to collect traces from the underlying uAMQP library
- enable AMQP frame level trace by setting `debug=True` when creating the Client


Provide Feedback
================

If you encounter any bugs or have suggestions, please file an issue in the
`Issues <https://github.com/Azure/azure-uamqp-python/issues>`__
section of the project.


Contributing
============

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit `https://cla.microsoft.com <https://cla.microsoft.com>`__.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the `Microsoft Open Source Code of Conduct <https://opensource.microsoft.com/codeofconduct/>`__.
For more information see the `Code of Conduct FAQ <https://opensource.microsoft.com/codeofconduct/faq/>`__ or
contact `opencode@microsoft.com <mailto:opencode@microsoft.com>`__ with any additional questions or comments.
