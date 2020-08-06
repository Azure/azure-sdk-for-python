# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from sys import version_info
from re import match
from enum import Enum

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceExistsError,
    ClientAuthenticationError,
    DecodeError)
from azure.core.pipeline.policies import ContentDecodePolicy

if version_info < (3,):
    def _str(value):
        if isinstance(value, unicode):  # pylint: disable=undefined-variable
            return value.encode('utf-8')

        return str(value)
else:
    _str = str


def _to_utc_datetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


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


def _validate_not_none(param_name, param):
    if param is None:
        raise ValueError(_ERROR_VALUE_NONE.format(param_name))


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


def _process_table_error(storage_error):
    raise_error = HttpResponseError
    error_code = storage_error.response.headers.get('x-ms-error-code')
    error_message = storage_error.message
    additional_data = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(storage_error.response)
        if isinstance(error_body, dict):
            for info in error_body['odata.error']:
                if info == 'code':
                    error_code = error_body['odata.error'][info]
                elif info == 'message':
                    error_message = error_body['odata.error'][info]['value']
                else:
                    additional_data[info.tag] = info.text
        else:
            if error_body:
                for info in error_body.iter():
                    if info.tag.lower().find('code') != -1:
                        error_code = info.text
                    elif info.tag.lower().find('message') != -1:
                        error_message = info.text
                    else:
                        additional_data[info.tag] = info.text
    except DecodeError:
        pass

    try:
        if error_code:
            error_code = TableErrorCode(error_code)
            if error_code in [TableErrorCode.condition_not_met]:
                raise_error = ResourceModifiedError
            if error_code in [TableErrorCode.invalid_authentication_info,
                              TableErrorCode.authentication_failed]:
                raise_error = ClientAuthenticationError
            if error_code in [TableErrorCode.resource_not_found,
                              TableErrorCode.table_not_found,
                              TableErrorCode.entity_not_found,
                              ResourceNotFoundError]:
                raise_error = ResourceNotFoundError
            if error_code in [TableErrorCode.resource_already_exists,
                              TableErrorCode.table_already_exists,
                              TableErrorCode.account_already_exists,
                              TableErrorCode.entity_already_exists,
                              ResourceExistsError]:
                raise_error = ResourceExistsError
    except ValueError:
        # Got an unknown error code
        pass

    try:
        error_message += "\nErrorCode:{}".format(error_code.value)
    except AttributeError:
        error_message += "\nErrorCode:{}".format(error_code)
    for name, info in additional_data.items():
        error_message += "\n{}:{}".format(name, info)

    error = raise_error(message=error_message, response=storage_error.response)
    error.error_code = error_code
    error.additional_info = additional_data
    raise error


class TableErrorCode(str, Enum):
    # Generic storage values
    account_already_exists = "AccountAlreadyExists"
    account_being_created = "AccountBeingCreated"
    account_is_disabled = "AccountIsDisabled"
    authentication_failed = "AuthenticationFailed"
    authorization_failure = "AuthorizationFailure"
    no_authentication_information = "NoAuthenticationInformation"
    condition_headers_not_supported = "ConditionHeadersNotSupported"
    condition_not_met = "ConditionNotMet"
    empty_metadata_key = "EmptyMetadataKey"
    insufficient_account_permissions = "InsufficientAccountPermissions"
    internal_error = "InternalError"
    invalid_authentication_info = "InvalidAuthenticationInfo"
    invalid_header_value = "InvalidHeaderValue"
    invalid_http_verb = "InvalidHttpVerb"
    invalid_input = "InvalidInput"
    invalid_md5 = "InvalidMd5"
    invalid_metadata = "InvalidMetadata"
    invalid_query_parameter_value = "InvalidQueryParameterValue"
    invalid_range = "InvalidRange"
    invalid_resource_name = "InvalidResourceName"
    invalid_uri = "InvalidUri"
    invalid_xml_document = "InvalidXmlDocument"
    invalid_xml_node_value = "InvalidXmlNodeValue"
    md5_mismatch = "Md5Mismatch"
    metadata_too_large = "MetadataTooLarge"
    missing_content_length_header = "MissingContentLengthHeader"
    missing_required_query_parameter = "MissingRequiredQueryParameter"
    missing_required_header = "MissingRequiredHeader"
    missing_required_xml_node = "MissingRequiredXmlNode"
    multiple_condition_headers_not_supported = "MultipleConditionHeadersNotSupported"
    operation_timed_out = "OperationTimedOut"
    out_of_range_input = "OutOfRangeInput"
    out_of_range_query_parameter_value = "OutOfRangeQueryParameterValue"
    request_body_too_large = "RequestBodyTooLarge"
    resource_type_mismatch = "ResourceTypeMismatch"
    request_url_failed_to_parse = "RequestUrlFailedToParse"
    resource_already_exists = "ResourceAlreadyExists"
    resource_not_found = "ResourceNotFound"
    server_busy = "ServerBusy"
    unsupported_header = "UnsupportedHeader"
    unsupported_xml_node = "UnsupportedXmlNode"
    unsupported_query_parameter = "UnsupportedQueryParameter"
    unsupported_http_verb = "UnsupportedHttpVerb"

    # table error codes
    duplicate_properties_specified = "DuplicatePropertiesSpecified"
    entity_not_found = "EntityNotFound"
    entity_already_exists = "EntityAlreadyExists"
    entity_too_large = "EntityTooLarge"
    host_information_not_present = "HostInformationNotPresent"
    invalid_duplicate_row = "InvalidDuplicateRow"
    invalid_value_type = "InvalidValueType"
    json_format_not_supported = "JsonFormatNotSupported"
    method_not_allowed = "MethodNotAllowed"
    not_implemented = "NotImplemented"
    properties_need_value = "PropertiesNeedValue"
    property_name_invalid = "PropertyNameInvalid"
    property_name_too_long = "PropertyNameTooLong"
    property_value_too_large = "PropertyValueTooLarge"
    table_already_exists = "TableAlreadyExists"
    table_being_deleted = "TableBeingDeleted"
    table_not_found = "TableNotFound"
    too_many_properties = "TooManyProperties"
    update_condition_not_satisfied = "UpdateConditionNotSatisfied"
    x_method_incorrect_count = "XMethodIncorrectCount"
    x_method_incorrect_value = "XMethodIncorrectValue"
    x_method_not_using_post = "XMethodNotUsingPost"
