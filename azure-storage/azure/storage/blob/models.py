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
