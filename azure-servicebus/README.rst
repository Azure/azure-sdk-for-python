Microsoft Azure SDK for Python
==============================

This is the Microsoft Azure Service Bus Runtime Client Library.

This package has been tested with Python 2.7, 3.3, 3.4 and 3.5.

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

-  Queues: create, list and delete queues; create, list, and delete subscriptions; send, receive, unlock and delete messages
-  Topics: create, list, and delete topics; create, list, and delete rules
-  Event Hubs: create and delete event hubs; send events


Installation
============

Download Package
----------------

To install via the Python Package Index (PyPI), type:

.. code:: shell

    pip install azure-servicebus


Download Source Code
--------------------

To get the source code of the SDK via **git** type:

.. code:: shell

    git clone https://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    cd azure-servicebus
    python setup.py install


Usage
=====

ServiceBus Queues
-----------------

ServiceBus Queues are an alternative to Storage Queues that might be
useful in scenarios where more advanced messaging features are needed
(larger message sizes, message ordering, single-operation destructive
reads, scheduled delivery) using push-style delivery (using long
polling).

The service can use Shared Access Signature authentication, or ACS
authentication.

Service bus namespaces created using the Azure portal after August 2014
no longer support ACS authentication. You can create ACS compatible
namespaces with the Azure SDK.

Shared Access Signature Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use Shared Access Signature authentication, create the service bus
service with:

.. code:: python

    from azure.servicebus import ServiceBusService

    key_name = 'RootManageSharedAccessKey' # SharedAccessKeyName from Azure portal
    key_value = '' # SharedAccessKey from Azure portal
    sbs = ServiceBusService(service_namespace,
                            shared_access_key_name=key_name,
                            shared_access_key_value=key_value)

ACS Authentication
~~~~~~~~~~~~~~~~~~

To use ACS authentication, create the service bus service with:

.. code:: python

    from azure.servicebus import ServiceBusService

    account_key = '' # DEFAULT KEY from Azure portal
    issuer = 'owner' # DEFAULT ISSUER from Azure portal
    sbs = ServiceBusService(service_namespace,
                            account_key=account_key,
                            issuer=issuer)

Sending and Receiving Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **create\_queue** method can be used to ensure a queue exists:

.. code:: python

    sbs.create_queue('taskqueue')

The **send\_queue\_message** method can then be called to insert the
message into the queue:

.. code:: python

    from azure.servicebus import Message

    msg = Message('Hello World!')
    sbs.send_queue_message('taskqueue', msg)

It is then possible to call the **receive\_queue\_message** method to
dequeue the message.

.. code:: python

    msg = sbs.receive_queue_message('taskqueue')

ServiceBus Topics
-----------------

ServiceBus topics are an abstraction on top of ServiceBus Queues that
make pub/sub scenarios easy to implement.

The **create\_topic** method can be used to create a server-side topic:

.. code:: python

    sbs.create_topic('taskdiscussion')

The **send\_topic\_message** method can be used to send a message to a
topic:

.. code:: python

    from azure.servicebus import Message

    msg = Message('Hello World!')
    sbs.send_topic_message('taskdiscussion', msg)

A client can then create a subscription and start consuming messages by
calling the **create\_subscription** method followed by the
**receive\_subscription\_message** method. Please note that any messages
sent before the subscription is created will not be received.

.. code:: python

    from azure.servicebus import Message

    sbs.create_subscription('taskdiscussion', 'client1')
    msg = Message('Hello World!')
    sbs.send_topic_message('taskdiscussion', msg)
    msg = sbs.receive_subscription_message('taskdiscussion', 'client1')

Event Hub
---------

Event Hubs enable the collection of event streams at high throughput, from
a diverse set of devices and services.

The **create\_event\_hub** method can be used to create an event hub:

.. code:: python

    sbs.create_event_hub('myhub')

To send an event:

.. code:: python

    sbs.send_event('myhub', '{ "DeviceId":"dev-01", "Temperature":"37.0" }')

The event content is the event message or JSON-encoded string that contains multiple messages.


Need Help?
==========

Be sure to check out the Microsoft Azure `Developer Forums on Stack
Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__ if you have
trouble with the provided code.


Contribute Code or Provide Feedback
===================================

If you would like to become an active contributor to this project please
follow the instructions provided in `Microsoft Azure Projects
Contribution
Guidelines <http://azure.github.io/guidelines.html>`__.

If you encounter any bugs with the library please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.


Learn More
==========

`Microsoft Azure Python Developer
Center <http://azure.microsoft.com/en-us/develop/python/>`__
