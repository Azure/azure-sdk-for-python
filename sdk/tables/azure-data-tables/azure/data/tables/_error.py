# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
from enum import Enum
from typing import Any

from azure.core import CaseInsensitiveEnumMeta
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceExistsError,
    ClientAuthenticationError,
    DecodeError,
)
from azure.core.pipeline.policies import ContentDecodePolicy


_ERROR_TYPE_NOT_SUPPORTED = "Type not supported when sending data to the service: {0}."
_ERROR_VALUE_TOO_LARGE = "{0} is too large to be cast to type {1}."
_ERROR_UNKNOWN = "Unknown error ({0})"
_ERROR_VALUE_NONE = "{0} should not be None."

# Storage table validation regex breakdown:
# ^ Match start of string.
# [a-zA-Z]{1} Match any letter for exactly 1 character.
# [a-zA-Z0-9]{2,62} Match any alphanumeric character for between 2 and 62 characters.
# $ End of string
_STORAGE_VALID_TABLE = re.compile(r"^[a-zA-Z]{1}[a-zA-Z0-9]{2,62}$")

# Cosmos table validation regex breakdown:
# ^ Match start of string.
# [^/\#?]{0,254} Match any character that is not /\#? for between 0-253 characters.
# [^ /\#?]{1} Match any character that is not /\#? or a space for exactly 1 character.
# $ End of string
_COSMOS_VALID_TABLE = re.compile(r"^[^/\\#?]{0,253}[^ /\\#?]{1}$")


def _validate_not_none(param_name, param):
    if param is None:
        raise ValueError(_ERROR_VALUE_NONE.format(param_name))


def _wrap_exception(ex, desired_type):
    msg = ""
    if len(ex.args) > 0:
        msg = ex.args[0]
    return desired_type(msg)
    # TODO: In the future we will log the trace


def _validate_storage_tablename(table_name):
    if _STORAGE_VALID_TABLE.match(table_name) is None:
        raise ValueError(
            "Storage table names must be alphanumeric, cannot begin with a number, \
                and must be between 3-63 characters long."
        )


def _validate_cosmos_tablename(table_name):
    if _COSMOS_VALID_TABLE.match(table_name) is None:
        raise ValueError(
            "Cosmos table names must contain from 1-255 characters, \
                and they cannot contain /, \\, #, ?, or a trailing space."
        )


def _validate_tablename_error(decoded_error, table_name):
    if (
        decoded_error.error_code == "InvalidResourceName"
        and "The specified resource name contains invalid characters" in decoded_error.message
    ):
        # This error is raised by Storage for any table/entity operations where the table name contains
        # forbidden characters.
        _validate_storage_tablename(table_name)
    elif (
        decoded_error.error_code == "InvalidResourceName"
        and "The specifed resource name contains invalid characters" in decoded_error.message
    ):
        # This error is raised by Storage for any table/entity operations where the table name contains
        # forbidden characters.
        _validate_storage_tablename(table_name)
    elif (
        decoded_error.error_code == "OutOfRangeInput"
        and "The specified resource name length is not within the permissible limits" in decoded_error.message
    ):
        # This error is raised by Storage for any table/entity operations where the table name is < 3 or > 63
        # characters long
        _validate_storage_tablename(table_name)
    elif decoded_error.error_code == "InternalServerError" and (
        "The resource name presented contains invalid character" in decoded_error.message
        or "The resource name can't end with space" in decoded_error.message
    ):
        # This error is raised by Cosmos during create_table if the table name contains forbidden
        # characters or ends in a space.
        _validate_cosmos_tablename(table_name)
    elif decoded_error.error_code == "BadRequest" and "The input name is invalid." in decoded_error.message:
        # This error is raised by Cosmos specifically during create_table if the table name is 255 or more
        # characters. Entity operations on a too-long-table name simply result in a ResourceNotFoundError.
        _validate_cosmos_tablename(table_name)
    elif decoded_error.error_code == "InvalidInput" and (
        "Request url is invalid." in decoded_error.message
        or "One of the input values is invalid." in decoded_error.message
        or "The table name contains an invalid character" in decoded_error.message
        or "Table name cannot end with a space." in decoded_error.message
    ):
        # This error is raised by Cosmos for any entity operations or delete_table if the table name contains
        # forbidden characters (except in the case of trailing space and backslash).
        _validate_cosmos_tablename(table_name)
    elif decoded_error.error_code == "Unauthorized" and (
        "The input authorization token can't serve the request." in decoded_error.message
        or "The MAC signature found in the HTTP request" in decoded_error.message
    ):
        # This error is raised by Cosmos specifically on entity operations where the table name contains
        # some forbidden characters, and seems to be a bug in the service authentication.
        _validate_cosmos_tablename(table_name)


def _validate_key_values(decoded_error, partition_key, row_key):
    if decoded_error.error_code == "PropertiesNeedValue":
        if partition_key is None:
            raise ValueError("PartitionKey must be present in an entity") from decoded_error
        if row_key is None:
            raise ValueError("RowKey must be present in an entity") from decoded_error


def _decode_error(response, error_message=None, error_type=None, **kwargs):  # pylint: disable=too-many-branches
    error_code = response.headers.get("x-ms-error-code")
    additional_data = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(response)
        if isinstance(error_body, dict):
            for info in error_body.get("odata.error", {}):
                if info == "code":
                    error_code = error_body["odata.error"][info]
                elif info == "message":
                    error_message = error_body["odata.error"][info]["value"]
                else:
                    additional_data[info.tag] = info.text
        else:
            if error_body:
                # Attempt to parse from XML element
                for info in error_body.iter():
                    if info.tag.lower().find("code") != -1:
                        error_code = info.text
                    elif info.tag.lower().find("message") != -1:
                        error_message = info.text
                    else:
                        additional_data[info.tag] = info.text
    except AttributeError:
        # Response body wasn't XML, give up trying to parse
        error_message = str(error_body)
    except DecodeError:
        pass

    try:
        if not error_type:
            error_code = TableErrorCode(error_code)
            if error_code in [TableErrorCode.condition_not_met, TableErrorCode.update_condition_not_satisfied]:
                error_type = ResourceModifiedError
            elif error_code in [
                TableErrorCode.invalid_authentication_info,
                TableErrorCode.authentication_failed,
            ]:
                error_type = ClientAuthenticationError
            elif error_code in [
                TableErrorCode.resource_not_found,
                TableErrorCode.table_not_found,
                TableErrorCode.entity_not_found,
                ResourceNotFoundError,
            ]:
                error_type = ResourceNotFoundError
            elif error_code in [
                TableErrorCode.resource_already_exists,
                TableErrorCode.table_already_exists,
                TableErrorCode.account_already_exists,
                TableErrorCode.entity_already_exists,
                ResourceExistsError,
            ]:
                error_type = ResourceExistsError
            else:
                error_type = HttpResponseError
    except ValueError:
        # Got an unknown error code
        error_type = HttpResponseError

    try:
        error_message = f"{error_message}\nErrorCode:{error_code.value}"
    except AttributeError:
        error_message = f"{error_message}\nErrorCode:{error_code}"
    for name, info in additional_data.items():
        error_message += f"\n{name}:{info}"

    error = error_type(message=error_message, response=response, **kwargs)
    error.error_code = error_code
    error.additional_info = additional_data
    return error


def _process_table_error(storage_error, table_name=None):
    try:
        decoded_error = _decode_error(storage_error.response, storage_error.message)
    except AttributeError as exc:
        raise storage_error from exc
    if table_name:
        _validate_tablename_error(decoded_error, table_name)
    raise decoded_error from storage_error


def _reprocess_error(decoded_error, identifiers=None):
    try:
        error_code = decoded_error.error_code
        message = decoded_error.message
        authentication_failed = "Server failed to authenticate the request"
        invalid_input = (
            "The number of keys specified in the URI does not match number of key properties for the resource"
        )
        invalid_query_parameter_value = "Value for one of the query parameters specified in the request URI is invalid"
        invalid_url = "Request url is invalid"
        properties_need_value = "The values are not specified for all properties in the entity"
        table_does_not_exist = "The table specified does not exist"
        if (  # pylint: disable=too-many-boolean-expressions
            (error_code == "AuthenticationFailed" and authentication_failed in message)
            or (error_code == "InvalidInput" and invalid_input in message)
            or (error_code == "InvalidInput" and invalid_url in message)
            or (error_code == "InvalidQueryParameterValue" and invalid_query_parameter_value in message)
            or (error_code == "PropertiesNeedValue" and properties_need_value in message)
            or (error_code == "TableNotFound" and table_does_not_exist in message)
        ):
            args_list = list(decoded_error.args)
            args_list[0] += (
                "\nA possible cause of this error could be that the account URL used to"
                "create the Client includes an invalid path, for example the table name. Please check your account URL."
            )
            decoded_error.args = tuple(args_list)

        if identifiers is not None and error_code == "InvalidXmlDocument" and len(identifiers) > 5:
            raise ValueError(
                "Too many access policies provided. The server does not support setting more than 5 access policies"
                "on a single resource."
            )
    except AttributeError as exc:
        raise decoded_error from exc


class TableTransactionError(HttpResponseError):
    """There is a failure in the transaction operations.

    :ivar int index: If available, the index of the operation in the transaction that caused the error.
     Defaults to 0 in the case where an index was not provided, or the error applies across operations.
    :ivar ~azure.data.tables.TableErrorCode error_code: The error code.
    :ivar str message: The error message.
    :ivar additional_info: Any additional data for the error.
    :vartype additional_info: Mapping[str, Any]
    """

    def __init__(self, **kwargs: Any) -> None:
        super(TableTransactionError, self).__init__(**kwargs)
        self.index = kwargs.get("index", self._extract_index())

    def _extract_index(self) -> int:
        try:
            message_sections = self.message.split(":", 1)
            return int(message_sections[0])
        except Exception:  # pylint:disable=broad-except
            return 0


class RequestTooLargeError(TableTransactionError):
    """An error response with status code 413 - Request Entity Too Large"""


class TableErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    # Generic storage values
    ACCOUNT_ALREADY_EXISTS = "AccountAlreadyExists"
    ACCOUNT_BEING_CREATED = "AccountBeingCreated"
    ACCOUNT_IS_DISABLED = "AccountIsDisabled"
    AUTHENTICATION_FAILED = "AuthenticationFailed"
    AUTHORIZATION_FAILURE = "AuthorizationFailure"
    NO_AUTHENTICATION_INFORMATION = "NoAuthenticationInformation"
    CONDITION_HEADERS_NOT_SUPPORTED = "ConditionHeadersNotSupported"
    CONDITION_NOT_MET = "ConditionNotMet"
    EMPTY_METADATA_KEY = "EmptyMetadataKey"
    INSUFFICIENT_ACCOUNT_PERMISSIONS = "InsufficientAccountPermissions"
    INTERNAL_ERROR = "InternalError"
    INVALID_AUTHENTICATION_INFO = "InvalidAuthenticationInfo"
    INVALID_HEADER_VALUE = "InvalidHeaderValue"
    INVALID_HTTP_VERB = "InvalidHttpVerb"
    INVALID_INPUT = "InvalidInput"
    INVALID_MD5 = "InvalidMd5"
    INVALID_METADATA = "InvalidMetadata"
    INVALID_QUERY_PARAMETER_VALUE = "InvalidQueryParameterValue"
    INVALID_RANGE = "InvalidRange"
    INVALID_RESOURCE_NAME = "InvalidResourceName"
    INVALID_URI = "InvalidUri"
    INVALID_XML_DOCUMENT = "InvalidXmlDocument"
    INVALID_XML_NODE_VALUE = "InvalidXmlNodeValue"
    MD5_MISMATCH = "Md5Mismatch"
    METADATA_TOO_LARGE = "MetadataTooLarge"
    MISSING_CONTENT_LENGTH_HEADER = "MissingContentLengthHeader"
    MISSING_REQUIRED_QUERY_PARAMETER = "MissingRequiredQueryParameter"
    MISSING_REQUIRED_HEADER = "MissingRequiredHeader"
    MISSING_REQUIRED_XML_NODE = "MissingRequiredXmlNode"
    MULTIPLE_CONDITION_HEADERS_NOT_SUPPORTED = "MultipleConditionHeadersNotSupported"
    OPERATION_TIMED_OUT = "OperationTimedOut"
    OUT_OF_RANGE_INPUT = "OutOfRangeInput"
    OUT_OF_RANGE_QUERY_PARAMETER_VALUE = "OutOfRangeQueryParameterValue"
    REQUEST_BODY_TOO_LARGE = "RequestBodyTooLarge"
    RESOURCE_TYPE_MISMATCH = "ResourceTypeMismatch"
    REQUEST_URL_FAILED_TO_PARSE = "RequestUrlFailedToParse"
    RESOURCE_ALREADY_EXISTS = "ResourceAlreadyExists"
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    SERVER_BUSY = "ServerBusy"
    UNSUPPORTED_HEADER = "UnsupportedHeader"
    UNSUPPORTED_XML_NODE = "UnsupportedXmlNode"
    UNSUPPORTED_QUERY_PARAMETER = "UnsupportedQueryParameter"
    UNSUPPORTED_HTTP_VERB = "UnsupportedHttpVerb"

    # table error codes
    DUPLICATE_PROPERTIES_SPECIFIED = "DuplicatePropertiesSpecified"
    ENTITY_NOT_FOUND = "EntityNotFound"
    ENTITY_ALREADY_EXISTS = "EntityAlreadyExists"
    ENTITY_TOO_LARGE = "EntityTooLarge"
    HOST_INFORMATION_NOT_PRESENT = "HostInformationNotPresent"
    INVALID_DUPLICATE_ROW = "InvalidDuplicateRow"
    INVALID_VALUE_TYPE = "InvalidValueType"
    JSON_FORMAT_NOT_SUPPORTED = "JsonFormatNotSupported"
    METHOD_NOT_ALLOWED = "MethodNotAllowed"
    NOT_IMPLEMENTED = "NotImplemented"
    PROPERTIES_NEED_VALUE = "PropertiesNeedValue"
    PROPERTY_NAME_INVALID = "PropertyNameInvalid"
    PROPERTY_NAME_TOO_LONG = "PropertyNameTooLong"
    PROPERTY_VALUE_TOO_LARGE = "PropertyValueTooLarge"
    TABLE_ALREADY_EXISTS = "TableAlreadyExists"
    TABLE_BEING_DELETED = "TableBeingDeleted"
    TABLE_NOT_FOUND = "TableNotFound"
    TOO_MANY_PROPERTIES = "TooManyProperties"
    UPDATE_CONDITION_NOT_SATISFIED = "UpdateConditionNotSatisfied"
    X_METHOD_INCORRECT_COUNT = "XMethodIncorrectCount"
    X_METHOD_INCORRECT_VALUE = "XMethodIncorrectValue"
    X_METHOD_NOT_USING_POST = "XMethodNotUsingPost"
