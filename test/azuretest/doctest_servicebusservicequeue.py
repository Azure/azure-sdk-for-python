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
How To: Create a Queue
----------------------
>>> from azure.servicebus import *
>>> bus_service = ServiceBusService(ns, key, 'owner')
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
from azuretest.util import *

ns = credentials.getServiceBusNamespace()
key = credentials.getServiceBusKey()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
