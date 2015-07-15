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

class ShareEnumResults(EnumResultsBase):

    ''' File Share list. '''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.shares = _list_of(Share)

    def __iter__(self):
        return iter(self.shares)

    def __len__(self):
        return len(self.shares)

    def __getitem__(self, index):
        return self.shares[index]


class Share(WindowsAzureData):

    ''' File share class. '''

    def __init__(self):
        self.name = u''
        self.url = u''
        self.properties = Properties()
        self.metadata = {}


class Properties(WindowsAzureData):

    ''' File share's properties class. '''

    def __init__(self):
        self.last_modified = u''
        self.etag = u''


class FileAndDirectoryEnumResults(EnumResultsBase):

    ''' 
    Enum result class holding a list of files
    and a list of directories. 
    '''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.files = _list_of(File)
        self.directories = _list_of(Directory)


class FileResult(bytes):

    def __new__(cls, file, properties):
        return bytes.__new__(cls, file if file else b'')

    def __init__(self, file, properties):
        self.properties = properties


class File(WindowsAzureData):

    ''' File class. '''

    def __init__(self):
        self.name = u''
        self.url = u''
        self.properties = FileProperties()
        self.metadata = {}


class FileProperties(WindowsAzureData):

    ''' File Properties '''

    def __init__(self):
        self.last_modified = u''
        self.etag = u''
        self.content_length = 0
        self.content_type = u''
        self.content_encoding = u''
        self.content_language = u''
        self.content_md5 = u''
        self.content_disposition = u''
        self.cache_control = u''


class Directory(WindowsAzureData):

    ''' Directory class. '''

    def __init__(self):
        self.name = ''


class Range(WindowsAzureData):

    ''' File Range. '''

    def __init__(self):
        self.start = 0
        self.end = 0


class RangeList(object):

    ''' Range list for range file. '''

    def __init__(self):
        self.file_ranges = _list_of(Range)

    def __iter__(self):
        return iter(self.file_ranges)

    def __len__(self):
        return len(self.file_ranges)

    def __getitem__(self, index):
        return self.file_ranges[index]
