# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from typing import (  # pylint: disable=unused-import
    TYPE_CHECKING
)

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)


def normalize_headers(headers):
    normalized = {}
    for key, value in headers.items():
        if key.startswith('x-ms-'):
            key = key[5:]
        normalized[key.lower().replace('-', '_')] = value
    return normalized


def deserialize_metadata(response, obj, headers):  # pylint: disable=unused-argument
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}


def return_response_headers(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return normalize_headers(response_headers)


def return_headers_and_deserialized_path_list(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return deserialized.paths if deserialized.paths else {}, normalize_headers(response_headers)


#
# def process_storage_error(storage_error):
#     raise_error = HttpResponseError
#     error_code = storage_error.response.headers.get('x-ms-error-code')
#     error_message = storage_error.message
#     additional_data = {}
#     try:
#         error_body = ContentDecodePolicy.deserialize_from_http_generics(storage_error.response)
#         if error_body:
#             for info in error_body.iter():
#                 if info.tag.lower() == 'code':
#                     error_code = info.text
#                 elif info.tag.lower() == 'message':
#                     error_message = info.text
#                 else:
#                     additional_data[info.tag] = info.text
#     except DecodeError:
#         pass
#
#     try:
#         if error_code:
#             error_code = StorageErrorCode(error_code)
#             if error_code in [StorageErrorCode.condition_not_met,
#                               StorageErrorCode.blob_overwritten]:
#                 raise_error = ResourceModifiedError
#             if error_code in [StorageErrorCode.invalid_authentication_info,
#                               StorageErrorCode.authentication_failed]:
#                 raise_error = ClientAuthenticationError
#             if error_code in [StorageErrorCode.resource_not_found,
#                               StorageErrorCode.cannot_verify_copy_source,
#                               StorageErrorCode.blob_not_found,
#                               StorageErrorCode.queue_not_found,
#                               StorageErrorCode.container_not_found,
#                               StorageErrorCode.parent_not_found,
#                               StorageErrorCode.share_not_found]:
#                 raise_error = ResourceNotFoundError
#             if error_code in [StorageErrorCode.account_already_exists,
#                               StorageErrorCode.account_being_created,
#                               StorageErrorCode.resource_already_exists,
#                               StorageErrorCode.resource_type_mismatch,
#                               StorageErrorCode.blob_already_exists,
#                               StorageErrorCode.queue_already_exists,
#                               StorageErrorCode.container_already_exists,
#                               StorageErrorCode.container_being_deleted,
#                               StorageErrorCode.queue_being_deleted,
#                               StorageErrorCode.share_already_exists,
#                               StorageErrorCode.share_being_deleted]:
#                 raise_error = ResourceExistsError
#     except ValueError:
#         # Got an unknown error code
#         pass
#
#     try:
#         error_message += "\nErrorCode:{}".format(error_code.value)
#     except AttributeError:
#         error_message += "\nErrorCode:{}".format(error_code)
#     for name, info in additional_data.items():
#         error_message += "\n{}:{}".format(name, info)
#
#     error = raise_error(message=error_message, response=storage_error.response)
#     error.error_code = error_code
#     error.additional_info = additional_data
#     raise error
#
#
