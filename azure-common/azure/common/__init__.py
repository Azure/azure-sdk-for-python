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

__author__ = 'Microsoft Corp. <ptvshelp@microsoft.com>'
__version__ = '0.20.0'


# TODO: Rename and merge with the new exception classes used by ARM

class WindowsAzureError(Exception):

    ''' WindowsAzure Exception base class. '''

    def __init__(self, message):
        super(WindowsAzureError, self).__init__(message)


class WindowsAzureConflictError(WindowsAzureError):

    '''Indicates that the resource could not be created because it already
    exists'''

    def __init__(self, message):
        super(WindowsAzureConflictError, self).__init__(message)


class WindowsAzureMissingResourceError(WindowsAzureError):

    '''Indicates that a request for a request for a resource (queue, table,
    container, etc...) failed because the specified resource does not exist'''

    def __init__(self, message):
        super(WindowsAzureMissingResourceError, self).__init__(message)


class WindowsAzureBatchOperationError(WindowsAzureError):

    '''Indicates that a batch operation failed'''

    def __init__(self, message, code):
        super(WindowsAzureBatchOperationError, self).__init__(message)
        self.code = code


class WindowsAzureAsyncOperationError(WindowsAzureError):

    '''Indicates that an async operation failed'''

    def __init__(self, message, result):
        super(WindowsAzureAsyncOperationError, self).__init__(message)
        self.result = result
