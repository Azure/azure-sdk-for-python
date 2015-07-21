#-------------------------------------------------------------------------
# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
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
    _list_of
)
from ..models import (
    EnumResultsBase
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

    ''' File Share class. '''

    def __init__(self):
        self.name = u''
        self.url = u''
        self.properties = Properties()
        self.metadata = {}


class Properties(WindowsAzureData):

    ''' File Share's properties class. '''

    def __init__(self):
        self.last_modified = u''
        self.etag = u''
