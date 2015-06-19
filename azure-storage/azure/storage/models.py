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
from ._internal import (
    WindowsAzureData,
)


class EnumResultsBase(object):

    ''' base class for EnumResults. '''

    def __init__(self):
        self.prefix = u''
        self.marker = u''
        self.max_results = 0
        self.next_marker = u''


class ContainerEnumResults(EnumResultsBase):

    ''' Blob Container list. '''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.containers = _list_of(Container)

    def __iter__(self):
        return iter(self.containers)

    def __len__(self):
        return len(self.containers)

    def __getitem__(self, index):
        return self.containers[index]


class Container(WindowsAzureData):

    ''' Blob container class. '''

    def __init__(self):
        self.name = u''
        self.url = u''
        self.properties = Properties()
        self.metadata = {}


class Properties(WindowsAzureData):

    ''' Blob container's properties class. '''

    def __init__(self):
        self.last_modified = u''
        self.etag = u''


class RetentionPolicy(WindowsAzureData):

    ''' RetentionPolicy in service properties. '''

    def __init__(self):
        self.enabled = False
        self.__dict__['days'] = None

    def get_days(self):
        # convert days to int value
        return int(self.__dict__['days'])

    def set_days(self, value):
        ''' set default days if days is set to empty. '''
        self.__dict__['days'] = value

    days = property(fget=get_days, fset=set_days)


class Logging(WindowsAzureData):

    ''' Logging class in service properties. '''

    def __init__(self):
        self.version = u'1.0'
        self.delete = False
        self.read = False
        self.write = False
        self.retention_policy = RetentionPolicy()


class HourMetrics(WindowsAzureData):

    ''' Hour Metrics class in service properties. '''

    def __init__(self):
        self.version = u'1.0'
        self.enabled = False
        self.include_apis = None
        self.retention_policy = RetentionPolicy()


class MinuteMetrics(WindowsAzureData):

    ''' Minute Metrics class in service properties. '''

    def __init__(self):
        self.version = u'1.0'
        self.enabled = False
        self.include_apis = None
        self.retention_policy = RetentionPolicy()


class StorageServiceProperties(WindowsAzureData):

    ''' Storage Service Propeties class. '''

    def __init__(self):
        self.logging = Logging()
        self.hour_metrics = HourMetrics()
        self.minute_metrics = MinuteMetrics()

    @property
    def metrics(self):
        import warnings
        warnings.warn(
            'The metrics attribute has been deprecated. Use hour_metrics and minute_metrics instead.')
        return self.hour_metrics


class AccessPolicy(WindowsAzureData):

    ''' Access Policy class in service properties. '''

    def __init__(self, start=u'', expiry=u'', permission=u'',
                 start_pk=u'', start_rk=u'', end_pk=u'', end_rk=u''):
        self.start = start
        self.expiry = expiry
        self.permission = permission
        self.start_pk = start_pk
        self.start_rk = start_rk
        self.end_pk = end_pk
        self.end_rk = end_rk


class SignedIdentifier(WindowsAzureData):

    ''' Signed Identifier class for service properties. '''

    def __init__(self):
        self.id = u''
        self.access_policy = AccessPolicy()


class SignedIdentifiers(WindowsAzureData):

    ''' SignedIdentifier list. '''

    def __init__(self):
        self.signed_identifiers = _list_of(SignedIdentifier)

    def __iter__(self):
        return iter(self.signed_identifiers)

    def __len__(self):
        return len(self.signed_identifiers)

    def __getitem__(self, index):
        return self.signed_identifiers[index]


class BlobEnumResults(EnumResultsBase):

    ''' Blob list.'''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.blobs = _list_of(Blob)
        self.prefixes = _list_of(BlobPrefix)
        self.delimiter = ''

    def __iter__(self):
        return iter(self.blobs)

    def __len__(self):
        return len(self.blobs)

    def __getitem__(self, index):
        return self.blobs[index]


class BlobResult(bytes):

    def __new__(cls, blob, properties):
        return bytes.__new__(cls, blob if blob else b'')

    def __init__(self, blob, properties):
        self.properties = properties


class Blob(WindowsAzureData):

    ''' Blob class. '''

    def __init__(self):
        self.name = u''
        self.snapshot = u''
        self.url = u''
        self.properties = BlobProperties()
        self.metadata = {}


class BlobProperties(WindowsAzureData):

    ''' Blob Properties '''

    def __init__(self):
        self.last_modified = u''
        self.etag = u''
        self.content_length = 0
        self.content_type = u''
        self.content_encoding = u''
        self.content_language = u''
        self.content_md5 = u''
        self.xms_blob_sequence_number = 0
        self.blob_type = u''
        self.lease_status = u''
        self.lease_state = u''
        self.lease_duration = u''
        self.copy_id = u''
        self.copy_source = u''
        self.copy_status = u''
        self.copy_progress = u''
        self.copy_completion_time = u''
        self.copy_status_description = u''


class BlobPrefix(WindowsAzureData):

    ''' BlobPrefix in Blob. '''

    def __init__(self):
        self.name = ''


class BlobBlock(WindowsAzureData):

    ''' BlobBlock class '''

    def __init__(self, id=None, size=None):
        self.id = id
        self.size = size


class BlobBlockList(WindowsAzureData):

    ''' BlobBlockList class '''

    def __init__(self):
        self.committed_blocks = []
        self.uncommitted_blocks = []


class PageRange(WindowsAzureData):

    ''' Page Range for page blob. '''

    def __init__(self):
        self.start = 0
        self.end = 0


class PageList(object):

    ''' Page list for page blob. '''

    def __init__(self):
        self.page_ranges = _list_of(PageRange)

    def __iter__(self):
        return iter(self.page_ranges)

    def __len__(self):
        return len(self.page_ranges)

    def __getitem__(self, index):
        return self.page_ranges[index]


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


class Entity(WindowsAzureData):

    ''' Entity class. The attributes of entity will be created dynamically. '''
    pass


class EntityProperty(WindowsAzureData):

    ''' Entity property. contains type and value.  '''

    def __init__(self, type=None, value=None):
        self.type = type
        self.value = value


class Table(WindowsAzureData):

    ''' Only for IntelliSense and telling user the return type. '''
    pass


class ContainerSharedAccessPermissions(object):
    '''Permissions for a container.'''

    '''
    Read the content, properties, metadata or block list of any blob in
    the container. Use any blob in the container as the source of a
    copy operation.
    '''
    READ = 'r'

    '''
    For any blob in the container, create or write content, properties,
    metadata, or block list. Snapshot or lease the blob. Resize the blob
    (page blob only). Use the blob as the destination of a copy operation
    within the same account.
    You cannot grant permissions to read or write container properties or
    metadata, nor to lease a container.
    '''
    WRITE = 'w'

    '''Delete any blob in the container.'''
    DELETE = 'd'

    '''List blobs in the container.'''
    LIST = 'l'


class BlobSharedAccessPermissions(object):
    '''Permissions for a blob.'''

    '''
    Read the content, properties, metadata and block list. Use the blob
    as the source of a copy operation.
    '''
    READ = 'r'

    '''
    Create or write content, properties, metadata, or block list.
    Snapshot or lease the blob. Resize the blob (page blob only). Use the
    blob as the destination of a copy operation within the same account.
    '''
    WRITE = 'w'

    '''Delete the blob.'''
    DELETE = 'd'


class TableSharedAccessPermissions(object):
    '''Permissions for a table.'''

    '''Get entities and query entities.'''
    QUERY = 'r'

    '''Add entities.'''
    ADD = 'a'

    '''Update entities.'''
    UPDATE = 'u'

    '''Delete entities.'''
    DELETE = 'd'


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
