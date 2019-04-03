Azure Event Hubs client library for Python
==========================================

Azure Event Hubs is a big data streaming platform and event ingestion service. It can receive and process millions of events per second.

Use the Event Hubs client library for Python to:

- Publish events to the Event Hubs service through a sender.
- Read events from the Event Hubs service through a receiver.

On Python 3.5 and above, it also includes:

- An async sender and receiver that supports async/await methods.
- An Event Processor Host module that manages the distribution of partition readers.

`Source code <https://github.com/Azure/azure-sdk-for-python/tree/master/azure-eventhubs>`__ | `Package (PyPi) <https://pypi.org/project/azure-eventhub/>`__ | `API reference documentation <https://docs.microsoft.com/python/api/azure-eventhub>`__ | `Product documentation <https://docs.microsoft.com/en-ca/azure/event-hubs/>`__

Getting started
===============

Install the package
-------------------

Install the Azure Event Hubs client library for Python with pip:

.. code:: shell

    $ pip install azure-eventhub

Prerequisites
+++++++++++++

- An Azure subscription.
- Python 3.4 or later.
- An existing Event Hubs namespace and event hub. You can create these entities by following the instructions in `this article <https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-create>`__.

Authenticate the client
-----------------------

Interaction with Event Hubs starts with an instance of the EventHubClient class. You need the host name, sas policy name, sas key and event hub name to instantiate the client object.

Get credentials
+++++++++++++++

You can find credential information in `Azure Portal <https://portal.azure.com/>`__.

Create client
+++++++++++++

There are several ways to instantiate the EventHubClient object and the following code snippets demonstrate one way:

.. code:: python

    import os
    from azure.eventhub import EventHubClient

    connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        os.environ['EVENT_HUB_HOSTNAME'],
        os.environ['EVENT_HUB_SAS_POLICY'],
        os.environ['EVENT_HUB_SAS_KEY'],
        os.environ['EVENT_HUB_NAME'])
    client = EventHubClient.from_connection_string(connection_str)

Key Concepts
============

- **Namespace:** An Event Hubs namespace provides a unique scoping container, referenced by its fully qualified domain name, in which you create one or more event hubs or Kafka topics.

- **Event publishers**: Any entity that sends data to an event hub is an event producer, or event publisher. Event publishers can publish events using HTTPS or AMQP 1.0 or Kafka 1.0 and later. Event publishers use a Shared Access Signature (SAS) token to identify themselves to an event hub, and can have a unique identity, or use a common SAS token.

- **Event consumers**: Any entity that reads event data from an event hub is an event consumer. All Event Hubs consumers connect via the AMQP 1.0 session and events are delivered through the session as they become available. The client does not need to poll for data availability.

- **SAS tokens**: Event Hubs uses Shared Access Signatures, which are available at the namespace and event hub level. A SAS token is generated from a SAS key and is an SHA hash of a URL, encoded in a specific format. Using the name of the key (policy) and the token, Event Hubs can regenerate the hash and thus authenticate the sender.

For more information about these concepts, see `Features and terminology in Azure Event Hubs <https://docs.microsoft.com/en-ca/azure/event-hubs/event-hubs-features>`__.

Examples
========

The following sections provide several code snippets covering some of the most common Event Hubs tasks, including:

- `Send event data`_
- `Receive event data`_
- `Async send event data`_
- `Async receive event data`_

.. _`Send event data`:

Send event data
---------------

Sends an event data and blocks until acknowledgement is received or operation times out.

.. code:: python

    client = EventHubClient.from_connection_string(connection_str)
    sender = client.add_sender(partition="0")
     try:
        client.run()
        event_data = EventData(b"A single event")
        sender.send(event_data)
    except:
        raise
    finally:
        client.stop()

.. _`Receive event data`:

Receive event data
------------------

Receive events from the EventHub.

.. code:: python

    client = EventHubClient.from_connection_string(connection_str)
    receiver = client.add_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
     try:
        client.run()
        logger = logging.getLogger("azure.eventhub")
        received = receiver.receive(timeout=5, max_batch_size=100)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
    except:
        raise
    finally:
        client.stop()

.. _`Async send event data`:

Async send event data
---------------------

Sends an event data and asynchronously waits until acknowledgement is received or operation times out.

.. code:: python

    client = EventHubClientAsync.from_connection_string(connection_str)
    sender = client.add_async_sender(partition="0")
    try:
        await client.run_async()
        event_data = EventData(b"A single event")
        await sender.send(event_data)
    except:
        raise
    finally:
        await client.stop_async()

.. _`Async receive event data`:

Async receive event data
------------------------

Receive events asynchronously from the EventHub.

.. code:: python

    client = EventHubClientAsync.from_connection_string(connection_str)
    receiver = client.add_async_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    try:
        await client.run_async()
        logger = logging.getLogger("azure.eventhub")
        received = await receiver.receive(timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
    except:
        raise
    finally:
        await client.stop_async()

Troubleshooting
===============

General
-------

The Event Hubs APIs generate exceptions that can fall into the following categories, along with the associated action you can take to try to fix them.

- **User coding error:** System.ArgumentException, System.InvalidOperationException, System.OperationCanceledException, System.Runtime.Serialization.SerializationException. General action: try to fix the code before proceeding.
- **Setup/configuration error:** Microsoft.ServiceBus.Messaging.MessagingEntityNotFoundException, Microsoft.Azure.EventHubs.MessagingEntityNotFoundException, System.UnauthorizedAccessException. General action: review your configuration and change if necessary.
- **Transient exceptions:** Microsoft.ServiceBus.Messaging.MessagingException, Microsoft.ServiceBus.Messaging.ServerBusyException, Microsoft.Azure.EventHubs.ServerBusyException, Microsoft.ServiceBus.Messaging.MessagingCommunicationException. General action: retry the operation or notify users.
- **Other exceptions:** System.Transactions.TransactionException, System.TimeoutException, Microsoft.ServiceBus.Messaging.MessageLockLostException, Microsoft.ServiceBus.Messaging.SessionLockLostException. General action: specific to the exception type; refer to the table in `Event Hubs messaging exceptions <https://docs.microsoft.com/en-ca/azure/event-hubs/event-hubs-messaging-exceptions>`__.

For more detailed infromation about excpetions and how to deal with them , see `Event Hubs messaging exceptions <https://docs.microsoft.com/en-ca/azure/event-hubs/event-hubs-messaging-exceptions>`__.

Next steps
==========

Examples
--------

- ./examples/send.py - use sender to publish events
- ./examples/recv.py - use receiver to read events
- ./examples/send_async.py - async/await support of a sender
- ./examples/recv_async.py - async/await support of a receiver
- ./examples/eph.py - event processor host

Documentation
-------------
Reference documentation is available at `docs.microsoft.com/python/api/azure-eventhub <https://docs.microsoft.com/python/api/azure-eventhub>`__.

Logging
-------

- enable 'azure.eventhub' logger to collect traces from the library
- enable 'uamqp' logger to collect traces from the underlying uAMQP library
- enable AMQP frame level trace by setting `debug=True` when creating the Client

Provide Feedback
----------------

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