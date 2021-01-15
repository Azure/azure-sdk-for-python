# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from sys import version_info
from re import match

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.table._shared.parser import _str

from ._constants import (
    _ENCRYPTION_PROTOCOL_V1,
)

def _to_str(value):
    return _str(value) if value is not None else None


_ERROR_ATTRIBUTE_MISSING = '\'{0}\' object has no attribute \'{1}\''
_ERROR_BATCH_COMMIT_FAIL = 'Batch Commit Fail'
_ERROR_CANNOT_FIND_PARTITION_KEY = 'Cannot find partition key in request.'
_ERROR_CANNOT_FIND_ROW_KEY = 'Cannot find row key in request.'
_ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY = \
    'Cannot serialize the specified value ({0}) to an entity.  Please use ' + \
    'an EntityProperty (which can specify custom types), int, str, bool, ' + \
    'or datetime.'
_ERROR_CANNOT_DESERIALIZE_VALUE_TO_ENTITY = \
    'Cannot deserialize the specified value ({0}).'
_ERROR_DUPLICATE_ROW_KEY_IN_BATCH = \
    'Row Keys should not be the same in a batch operations'
_ERROR_INCORRECT_PARTITION_KEY_IN_BATCH = \
    'Partition Key should be the same in a batch operations'
_ERROR_INVALID_ENTITY_TYPE = 'The entity must be either in dict format or an entity object.'
_ERROR_INVALID_PROPERTY_RESOLVER = \
    'The specified property resolver returned an invalid type. Name: {0}, Value: {1}, ' + \
    'EdmType: {2}'
_ERROR_PROPERTY_NAME_TOO_LONG = 'The property name exceeds the maximum allowed length.'
_ERROR_TOO_MANY_ENTITIES_IN_BATCH = \
    'Batches may only contain 100 operations'
_ERROR_TOO_MANY_PROPERTIES = 'The entity contains more properties than allowed.'
_ERROR_TYPE_NOT_SUPPORTED = 'Type not supported when sending data to the service: {0}.'
_ERROR_VALUE_TOO_LARGE = '{0} is too large to be cast to type {1}.'
_ERROR_UNSUPPORTED_TYPE_FOR_ENCRYPTION = 'Encryption is only supported for not None strings.'
_ERROR_ENTITY_NOT_ENCRYPTED = 'Entity was not encrypted.'
_ERROR_ATTRIBUTE_MISSING = '\'{0}\' object has no attribute \'{1}\''
_ERROR_CONFLICT = 'Conflict ({0})'
_ERROR_NOT_FOUND = 'Not found ({0})'
_ERROR_UNKNOWN = 'Unknown error ({0})'
_ERROR_STORAGE_MISSING_INFO = \
    'You need to provide an account name and either an account_key or sas_token when creating a storage service.'
_ERROR_EMULATOR_DOES_NOT_SUPPORT_FILES = \
    'The emulator does not support the file service.'
_ERROR_ACCESS_POLICY = \
    'share_access_policy must be either SignedIdentifier or AccessPolicy ' + \
    'instance'
_ERROR_PARALLEL_NOT_SEEKABLE = 'Parallel operations require a seekable stream.'
_ERROR_VALUE_SHOULD_BE_BYTES = '{0} should be of type bytes.'
_ERROR_VALUE_SHOULD_BE_BYTES_OR_STREAM = '{0} should be of type bytes or a readable file-like/io.IOBase stream object.'
_ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM = '{0} should be a seekable file-like/io.IOBase type stream object.'
_ERROR_VALUE_SHOULD_BE_STREAM = '{0} should be a file-like/io.IOBase type stream object with a read method.'
_ERROR_VALUE_NONE = '{0} should not be None.'
_ERROR_VALUE_NONE_OR_EMPTY = '{0} should not be None or empty.'
_ERROR_VALUE_NEGATIVE = '{0} should not be negative.'
_ERROR_START_END_NEEDED_FOR_MD5 = \
    'Both end_range and start_range need to be specified ' + \
    'for getting content MD5.'
_ERROR_RANGE_TOO_LARGE_FOR_MD5 = \
    'Getting content MD5 for a range greater than 4MB ' + \
    'is not supported.'
_ERROR_MD5_MISMATCH = \
    'MD5 mismatch. Expected value is \'{0}\', computed value is \'{1}\'.'
_ERROR_TOO_MANY_ACCESS_POLICIES = \
    'Too many access policies provided. ' \
    'The server does not support setting more than 5 access policies on a single resource.'
_ERROR_OBJECT_INVALID = \
    '{0} does not define a complete interface. Value of {1} is either missing or invalid.'
_ERROR_UNSUPPORTED_ENCRYPTION_VERSION = \
    'Encryption version is not supported.'
_ERROR_DECRYPTION_FAILURE = \
    'Decryption failed'
_ERROR_ENCRYPTION_REQUIRED = \
    'Encryption required but no key was provided.'
_ERROR_DECRYPTION_REQUIRED = \
    'Decryption required but neither key nor resolver was provided.' + \
    ' If you do not want to decypt, please do not set the require encryption flag.'
_ERROR_INVALID_KID = \
    'Provided or resolved key-encryption-key does not match the id of key used to encrypt.'
_ERROR_UNSUPPORTED_ENCRYPTION_ALGORITHM = \
    'Specified encryption algorithm is not supported.'
_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION = 'The require_encryption flag is set, but encryption is not supported' + \
                                           ' for this method.'
_ERROR_UNKNOWN_KEY_WRAP_ALGORITHM = 'Unknown key wrap algorithm.'
_ERROR_DATA_NOT_ENCRYPTED = 'Encryption required, but received data does not contain appropriate metatadata.' + \
                            'Data was either not encrypted or metadata has been lost.'


def _dont_fail_on_exist(error):
    """ don't throw exception if the resource exists.
    This is called by create_* APIs with fail_on_exist=False"""
    if isinstance(error, ResourceExistsError):  # pylint: disable=R1705
        return False
    else:
        raise error


def _dont_fail_not_exist(error):
    """ don't throw exception if the resource doesn't exist.
    This is called by create_* APIs with fail_on_exist=False"""
    if isinstance(error, ResourceNotFoundError):  # pylint: disable=R1705
        return False
    else:
        raise error


def _http_error_handler(http_error):
    """ Simple error handler for azure."""
    message = str(http_error)
    error_code = None

    if 'x-ms-error-code' in http_error.respheader:
        error_code = http_error.respheader['x-ms-error-code']
        message += ' ErrorCode: ' + error_code

    if http_error.respbody is not None:
        message += '\n' + http_error.respbody.decode('utf-8-sig')

    ex = HttpResponseError(message, http_error.status)
    ex.error_code = error_code

    raise ex


def _validate_type_bytes(param_name, param):
    if not isinstance(param, bytes):
        raise TypeError(_ERROR_VALUE_SHOULD_BE_BYTES.format(param_name))


def _validate_type_bytes_or_stream(param_name, param):
    if not (isinstance(param, bytes) or hasattr(param, 'read')):
        raise TypeError(_ERROR_VALUE_SHOULD_BE_BYTES_OR_STREAM.format(param_name))


def _validate_not_none(param_name, param):
    if param is None:
        raise ValueError(_ERROR_VALUE_NONE.format(param_name))


def _validate_content_match(server_md5, computed_md5):
    if server_md5 != computed_md5:
        raise Exception(_ERROR_MD5_MISMATCH.format(server_md5, computed_md5))


def _validate_access_policies(identifiers):
    if identifiers and len(identifiers) > 5:
        raise Exception(_ERROR_TOO_MANY_ACCESS_POLICIES)


def _validate_key_encryption_key_wrap(kek):
    # Note that None is not callable and so will fail the second clause of each check.
    if not hasattr(kek, 'wrap_key') or not callable(kek.wrap_key):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'wrap_key'))
    if not hasattr(kek, 'get_kid') or not callable(kek.get_kid):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'get_kid'))
    if not hasattr(kek, 'get_key_wrap_algorithm') or not callable(kek.get_key_wrap_algorithm):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'get_key_wrap_algorithm'))


def _validate_key_encryption_key_unwrap(kek):
    if not hasattr(kek, 'get_kid') or not callable(kek.get_kid):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'get_kid'))
    if not hasattr(kek, 'unwrap_key') or not callable(kek.unwrap_key):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'unwrap_key'))


def _validate_encryption_required(require_encryption, kek):
    if require_encryption and (kek is None):
        raise ValueError(_ERROR_ENCRYPTION_REQUIRED)


def _validate_decryption_required(require_encryption, kek, resolver):
    if (require_encryption and (kek is None) and
            (resolver is None)):
        raise ValueError(_ERROR_DECRYPTION_REQUIRED)


def _validate_encryption_protocol_version(encryption_protocol):
    if not _ENCRYPTION_PROTOCOL_V1 == encryption_protocol:
        raise ValueError(_ERROR_UNSUPPORTED_ENCRYPTION_VERSION)


def _validate_kek_id(kid, resolved_id):
    if not kid == resolved_id:
        raise ValueError(_ERROR_INVALID_KID)


def _validate_encryption_unsupported(require_encryption, key_encryption_key):
    if require_encryption or (key_encryption_key is not None):
        raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)


# wraps a given exception with the desired exception type
def _wrap_exception(ex, desired_type):
    msg = ""
    if len(ex.args) > 0:  # pylint: disable=C1801
        msg = ex.args[0]
    if version_info >= (3,):  # pylint: disable=R1705
        # Automatic chaining in Python 3 means we keep the trace
        return desired_type(msg)
    else:
        # There isn't a good solution in 2 for keeping the stack trace
        # in general, or that will not result in an error in 3
        # However, we can keep the previous error type and message
        # TODO: In the future we will log the trace
        return desired_type('{}: {}'.format(ex.__class__.__name__, msg))


def _validate_table_name(table_name):
    if match("^[a-zA-Z]{1}[a-zA-Z0-9]{2,62}$", table_name) is None:
        raise ValueError(
            "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long."
        )


class AzureSigningError(Exception):
    """
    Represents a fatal error when attempting to sign a request.
    In general, the cause of this exception is user error. For example, the given account key is not valid.
    Please visit https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account for more info.
    """
