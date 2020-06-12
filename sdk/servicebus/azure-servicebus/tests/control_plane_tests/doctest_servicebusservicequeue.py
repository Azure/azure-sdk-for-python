#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

"""
How To: Create a Queue
----------------------
>>> from azure.servicebus._control_client import *
>>> bus_service = ServiceBusService(shared_access_key_name=key_name, shared_access_key_value=key_value, 'owner')
>>> bus_service.create_queue('taskqueue')
True

>>> queue_options = Queue()
>>> queue_options.max_size_in_megabytes = '5120'
>>> queue_options.default_message_time_to_live = 'PT1M'
>>> bus_service.create_queue('taskqueue2', queue_options)
True

How to Send Messages to a Queue
-------------------------------
>>> msg = Message('Test Message')
>>> bus_service.send_queue_message('taskqueue', msg)

How to Receive Messages from a Queue
------------------------------------
>>> msg = bus_service.receive_queue_message('taskqueue')
>>> print(msg.body)
Test Message

>>> msg = Message('Test Message')
>>> bus_service.send_queue_message('taskqueue', msg)

>>> msg = bus_service.receive_queue_message('taskqueue', peek_lock=True)
>>> print(msg.body)
Test Message
>>> msg.delete()


>>> bus_service.delete_queue('taskqueue')
True

>>> bus_service.delete_queue('taskqueue2')
True

"""
import servicebus_settings_real as settings  # pylint: disable=import-error

key_name = settings.SERVICEBUS_SAS_KEY_NAME
key_value = settings.SERVICEBUS_SAS_KEY_VALUE

if __name__ == "__main__":
    import doctest
    doctest.testmod()
