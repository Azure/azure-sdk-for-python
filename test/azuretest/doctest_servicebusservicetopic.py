#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

"""
How to Create a Topic
---------------------
>>> from azure.servicebus import *
>>> bus_service = ServiceBusService(ns, key, 'owner')
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
from azuretest.util import *

ns = credentials.getServiceBusNamespace()
key = credentials.getServiceBusKey()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
