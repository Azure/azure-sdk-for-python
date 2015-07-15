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


_ERROR_CANNOT_FIND_PARTITION_KEY = 'Cannot find partition key in request.'
_ERROR_CANNOT_FIND_ROW_KEY = 'Cannot find row key in request.'
_ERROR_INCORRECT_TABLE_IN_BATCH = \
    'Table should be the same in a batch operations'
_ERROR_INCORRECT_PARTITION_KEY_IN_BATCH = \
    'Partition Key should be the same in a batch operations'
_ERROR_DUPLICATE_ROW_KEY_IN_BATCH = \
    'Row Keys should not be the same in a batch operations'
_ERROR_BATCH_COMMIT_FAIL = 'Batch Commit Fail'
_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_DELETE = \
    'Message is not peek locked and cannot be deleted.'
_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_UNLOCK = \
    'Message is not peek locked and cannot be unlocked.'
_ERROR_CONFLICT = 'Conflict ({0})'
_ERROR_NOT_FOUND = 'Not found ({0})'
_ERROR_UNKNOWN = 'Unknown error ({0})'
_ERROR_STORAGE_MISSING_INFO = \
    'You need to provide an account name'
_ERROR_ACCESS_POLICY = \
    'share_access_policy must be either SignedIdentifier or AccessPolicy ' + \
    'instance'
_WARNING_VALUE_SHOULD_BE_BYTES = \
    'Warning: {0} must be bytes data type. It will be converted ' + \
    'automatically, with utf-8 text encoding.'
_ERROR_VALUE_SHOULD_BE_BYTES = '{0} should be of type bytes.'
_ERROR_VALUE_NONE = '{0} should not be None.'
_ERROR_VALUE_NEGATIVE = '{0} should not be negative.'
_ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY = \
    'Cannot serialize the specified value ({0}) to an entity.  Please use ' + \
    'an EntityProperty (which can specify custom types), int, str, bool, ' + \
    'or datetime.'
_ERROR_PAGE_BLOB_SIZE_ALIGNMENT = \
    'Invalid page blob size: {0}. ' + \
    'The size must be aligned to a 512-byte boundary.'


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


def _general_error_handler(http_error):
    ''' Simple error handler for azure.'''
    message = str(http_error)
    if http_error.respbody is not None:
        message += '\n' + http_error.respbody.decode('utf-8-sig')
    raise AzureHttpError(message, http_error.status)


def _validate_type_bytes(param_name, param):
    if not isinstance(param, bytes):
        raise TypeError(_ERROR_VALUE_SHOULD_BE_BYTES.format(param_name))


def _validate_not_none(param_name, param):
    if param is None:
        raise ValueError(_ERROR_VALUE_NONE.format(param_name))
