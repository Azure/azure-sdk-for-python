    
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys

_ERROR_MESSAGE_SHOULD_BE_UNICODE = 'message should be of type unicode.'
_ERROR_MESSAGE_SHOULD_BE_STR = 'message should be of type str.'
_ERROR_MESSAGE_NOT_BASE64 = 'message is not a valid base64 value.'
_ERROR_MESSAGE_NOT_ENCRYPTED = 'Message was not encrypted.'
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
    'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'
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

def _validate_message_type_text(param):
    if sys.version_info < (3,):
        if not isinstance(param, unicode):
            raise TypeError(_ERROR_MESSAGE_SHOULD_BE_UNICODE)
    else:
        if not isinstance(param, str):
            raise TypeError(_ERROR_MESSAGE_SHOULD_BE_STR)
