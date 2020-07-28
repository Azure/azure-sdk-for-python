#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

"""
How to Create a Topic
---------------------
>>> from azure.servicebus._control_client import *
>>> bus_service = ServiceBusService(shared_access_key_name=key_name, shared_access_key_value=key_value, 'owner')
>>> bus_service.create_topic('mytopic')
True

>>> topic_options = Topic()
>>> topic_options.max_size_in_megabytes = '5120'
>>> topic_options.default_message_time_to_live = 'PT1M'
>>> bus_service.create_topic('mytopic2', topic_options)
True

How to Create Subscriptions
---------------------------
>>> bus_service.create_subscription('mytopic', 'AllMessages')
True

>>> bus_service.create_subscription('mytopic', 'HighMessages')
True

>>> rule = Rule()
>>> rule.filter_type = 'SqlFilter'
>>> rule.filter_expression = 'messagenumber > 3'
>>> bus_service.create_rule('mytopic', 'HighMessages', 'HighMessageFilter', rule)
True

>>> bus_service.delete_rule('mytopic', 'HighMessages', DEFAULT_RULE_NAME)
True

>>> bus_service.create_subscription('mytopic', 'LowMessages')
True

>>> rule = Rule()
>>> rule.filter_type = 'SqlFilter'
>>> rule.filter_expression = 'messagenumber <= 3'
>>> bus_service.create_rule('mytopic', 'LowMessages', 'LowMessageFilter', rule)
True

>>> bus_service.delete_rule('mytopic', 'LowMessages', DEFAULT_RULE_NAME)
True

How to Send Messages to a Topic
-------------------------------
>>> for i in range(5):
...     msg = Message('Msg ' + str(i), custom_properties={'messagenumber':i})
...     bus_service.send_topic_message('mytopic', msg)

How to Receive Messages from a Subscription
-------------------------------------------
>>> msg = bus_service.receive_subscription_message('mytopic', 'LowMessages')
>>> print(msg.body)
Msg 0

>>> msg = bus_service.receive_subscription_message('mytopic', 'LowMessages', peek_lock=True)
>>> print(msg.body)
Msg 1
>>> msg.delete()

How to Delete Topics and Subscriptions
--------------------------------------
>>> bus_service.delete_subscription('mytopic', 'HighMessages')
True

>>> bus_service.delete_queue('mytopic')
True

>>> bus_service.delete_queue('mytopic2')
True

"""
import servicebus_settings_real as settings  # pylint: disable=import-error

key_name = settings.SERVICEBUS_SAS_KEY_NAME
key_value = settings.SERVICEBUS_SAS_KEY_VALUE

if __name__ == "__main__":
    import doctest
    doctest.testmod()
