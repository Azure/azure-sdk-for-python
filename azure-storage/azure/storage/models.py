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
from azure.common import (
    AzureException,
    AzureHttpError,
)
from ._common_models import (
    WindowsAzureData,
    _list_of,
)


class AzureBatchValidationError(AzureException):

    '''Indicates that a batch operation cannot proceed due to invalid input'''


class AzureBatchOperationError(AzureHttpError):

    '''Indicates that a batch operation failed'''

    def __init__(self, message, status_code, batch_code):
        super(AzureBatchOperationError, self).__init__(message, status_code)
        self.code = batch_code


class EnumResultsBase(object):

    ''' base class for EnumResults. '''

    def __init__(self):
        self.prefix = u''
        self.marker = u''
        self.max_results = 0
        self.next_marker = u''


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
