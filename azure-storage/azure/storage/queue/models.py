#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
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
from .._common_models import (
    WindowsAzureData,
    _list_of,
)
from ..models import (
    EnumResultsBase,
)


class QueueEnumResults(EnumResultsBase):

    ''' Queue list'''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.queues = _list_of(Queue)

    def __iter__(self):
        return iter(self.queues)

    def __len__(self):
        return len(self.queues)

    def __getitem__(self, index):
        return self.queues[index]


class Queue(WindowsAzureData):

    ''' Queue class '''

    def __init__(self):
        self.name = u''
        self.url = u''
        self.metadata = {}


class QueueMessagesList(WindowsAzureData):

    ''' Queue message list. '''

    def __init__(self):
        self.queue_messages = _list_of(QueueMessage)

    def __iter__(self):
        return iter(self.queue_messages)

    def __len__(self):
        return len(self.queue_messages)

    def __getitem__(self, index):
        return self.queue_messages[index]


class QueueMessage(WindowsAzureData):

    ''' Queue message class. '''

    def __init__(self):
        self.message_id = u''
        self.insertion_time = u''
        self.expiration_time = u''
        self.pop_receipt = u''
        self.time_next_visible = u''
        self.dequeue_count = u''
        self.message_text = u''


class QueueSharedAccessPermissions(object):
    '''Permissions for a queue.'''

    '''
    Read metadata and properties, including message count.
    Peek at messages.
    '''
    READ = 'r'

    '''Add messages to the queue.'''
    ADD = 'a'

    '''Update messages in the queue.'''
    UPDATE = 'u'

    '''Get and delete messages from the queue.'''
    PROCESS = 'p'
