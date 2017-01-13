Service Bus
===========

ServiceBus Queues
-----------------

ServiceBus Queues are an alternative to Storage Queues that might be
useful in scenarios where more advanced messaging features are needed
(larger message sizes, message ordering, single-operaiton destructive
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

The **send\_queue\_message_batch** method can then be called to 
send several messages at once:

.. code:: python

    from azure.servicebus import Message

    msg1 = Message('Hello World!')
    msg2 = Message('Hello World again!')
    sbs.send_queue_message_batch('taskqueue', [msg1, msg2])

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

    msg = Message(b'Hello World!')
    sbs.send_topic_message('taskdiscussion', msg)

The **send\_topic\_message_batch** method can be used to send 
several messages at once:

.. code:: python

    from azure.servicebus import Message

    msg1 = Message(b'Hello World!')
    msg2 = Message(b'Hello World again!')
    sbs.send_topic_message_batch('taskdiscussion', [msg1, msg2])


Please consider that in Python 3 a str message will be utf-8 encoded
and you should have to manage your encoding yourself in Python 2.

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

Advanced features
-----------------

Broker Properties and User Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section describes how to use Broker and User properties defined here:
https://docs.microsoft.com/rest/api/servicebus/message-headers-and-properties

.. code:: python

    sent_msg = Message(b'This is the third message',
                       broker_properties={'Label': 'M3'},
                       custom_properties={'Priority': 'Medium',
                                          'Customer': 'ABC'}
               )

You can use datetime, int, float or boolean

.. code:: python

    props = {'hello': 'world',
             'number': 42,
             'active': True,
             'deceased': False,
             'large': 8555111000,
             'floating': 3.14,
             'dob': datetime(2011, 12, 14),
             'double_quote_message': 'This "should" work fine',
             'quote_message': "This 'should' work fine"}
    sent_msg = Message(b'message with properties', custom_properties=props)

For compatibility reason with old version of this library, 
`broker_properties` could also be defined as a JSON string.
If this situation, you're responsible to write a valid JSON string, no check
will be made by Python before sending to the RestAPI.

.. code:: python

    broker_properties = '{"ForcePersistence": false, "Label": "My label"}'
    sent_msg = Message(b'receive message',
                       broker_properties = broker_properties
    )


