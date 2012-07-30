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
>>> from azure.storage import *
>>> queue_service = QueueService(name, key)
>>> queue_service.create_queue('taskqueue')
True

How To: Insert a Message into a Queue
-------------------------------------
>>> queue_service.put_message('taskqueue', 'Hello World')

How To: Peek at the Next Message
--------------------------------
>>> messages = queue_service.peek_messages('taskqueue')
>>> for message in messages:
...     print(message.message_text)
... 
Hello World

How To: Dequeue the Next Message
--------------------------------
>>> messages = queue_service.get_messages('taskqueue')
>>> for message in messages:
...     print(message.message_text)
...     queue_service.delete_message('taskqueue', message.message_id, message.pop_receipt)
Hello World

How To: Change the Contents of a Queued Message
-----------------------------------------------
>>> queue_service.put_message('taskqueue', 'Hello World')
>>> messages = queue_service.get_messages('taskqueue')
>>> for message in messages:
...     res = queue_service.update_message('taskqueue', message.message_id, 'Hello World Again', message.pop_receipt, 0)

How To: Additional Options for Dequeuing Messages
-------------------------------------------------
>>> queue_service.put_message('taskqueue', 'Hello World')
>>> messages = queue_service.get_messages('taskqueue', numofmessages=16, visibilitytimeout=5*60)
>>> for message in messages:
...     print(message.message_text)
...     queue_service.delete_message('taskqueue', message.message_id, message.pop_receipt)
Hello World Again
Hello World

How To: Get the Queue Length
----------------------------
>>> queue_metadata = queue_service.get_queue_metadata('taskqueue')
>>> count = queue_metadata['x-ms-approximate-messages-count']
>>> count
u'0'

How To: Delete a Queue
----------------------
>>> queue_service.delete_queue('taskqueue')
True

"""
from azuretest.util import *

name = credentials.getStorageServicesName()
key = credentials.getStorageServicesKey()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
