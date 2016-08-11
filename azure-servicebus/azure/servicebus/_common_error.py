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
    AzureHttpError,
    AzureConflictHttpError,
    AzureMissingResourceHttpError,
)


_ERROR_CONFLICT = 'Conflict ({0})'
_ERROR_NOT_FOUND = 'Not found ({0})'
_ERROR_UNKNOWN = 'Unknown error ({0})'
_ERROR_VALUE_NONE = '{0} should not be None.'
_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_DELETE = \
    'Message is not peek locked and cannot be deleted.'
_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_UNLOCK = \
    'Message is not peek locked and cannot be unlocked.'
_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_RENEW_LOCK = \
    'Message is not peek locked and lock cannot be renewed.'
_ERROR_EVENT_HUB_NOT_FOUND = 'Event hub was not found'
_ERROR_QUEUE_NOT_FOUND = 'Queue was not found'
_ERROR_TOPIC_NOT_FOUND = 'Topic was not found'
_ERROR_SERVICEBUS_MISSING_INFO = \
    'You need to provide servicebus namespace, access key and Issuer'
_WARNING_VALUE_SHOULD_BE_BYTES = \
    'Warning: {0} must be bytes data type. It will be converted ' + \
    'automatically, with utf-8 text encoding.'
_ERROR_VALUE_SHOULD_BE_BYTES = '{0} should be of type bytes.'
_ERROR_VALUE_NEGATIVE = '{0} should not be negative.'


def _general_error_handler(http_error):
    ''' Simple error handler for azure.'''
    message = str(http_error)
    if http_error.respbody is not None:
        message += '\n' + http_error.respbody.decode('utf-8-sig')
    raise AzureHttpError(message, http_error.status)


def _dont_fail_on_exist(error):
    ''' don't throw exception if the resource exists.
    This is called by create_* APIs with fail_on_exist=False'''
    if isinstance(error, AzureConflictHttpError):
        return False
    else:
        raise error


def _dont_fail_not_exist(error):
    ''' don't throw exception if the resource doesn't exist.
    This is called by create_* APIs with fail_on_exist=False'''
    if isinstance(error, AzureMissingResourceHttpError):
        return False
    else:
        raise error


def _validate_type_bytes(param_name, param):
    if not isinstance(param, bytes):
        raise TypeError(_ERROR_VALUE_SHOULD_BE_BYTES.format(param_name))


def _validate_not_none(param_name, param):
    if param is None:
        raise ValueError(_ERROR_VALUE_NONE.format(param_name))
