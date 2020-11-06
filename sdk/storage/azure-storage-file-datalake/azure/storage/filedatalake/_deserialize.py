# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from typing import (  # pylint: disable=unused-import
    TYPE_CHECKING
)

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.exceptions import HttpResponseError, DecodeError, ResourceModifiedError, ClientAuthenticationError, \
    ResourceNotFoundError, ResourceExistsError
from ._models import FileProperties, DirectoryProperties, LeaseProperties
from ._shared.models import StorageErrorCode

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)


def deserialize_dir_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    dir_properties = DirectoryProperties(
        metadata=metadata,
        **headers
    )
    return dir_properties


def deserialize_file_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    file_properties = FileProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-blob-content-md5' in headers:
            file_properties.content_settings.content_md5 = headers['x-ms-blob-content-md5']
        else:
            file_properties.content_settings.content_md5 = None
    return file_properties


def from_blob_properties(blob_properties):
    file_props = FileProperties()
    file_props.name = blob_properties.name
    file_props.etag = blob_properties.etag
    file_props.deleted = blob_properties.deleted
    file_props.metadata = blob_properties.metadata
    file_props.lease = blob_properties.lease
    file_props.lease.__class__ = LeaseProperties
    file_props.last_modified = blob_properties.last_modified
    file_props.creation_time = blob_properties.creation_time
    file_props.size = blob_properties.size
    file_props.deleted_time = blob_properties.deleted_time
    file_props.remaining_retention_days = blob_properties.remaining_retention_days
    file_props.content_settings = blob_properties.content_settings
    return file_props

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


def return_headers_and_deserialized_path_list(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return deserialized.paths if deserialized.paths else {}, normalize_headers(response_headers)


def process_storage_error(storage_error):
    raise_error = HttpResponseError
    error_code = storage_error.response.headers.get('x-ms-error-code')
    error_message = storage_error.message
    additional_data = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(storage_error.response)
        if error_body:
            for info in error_body:
                if info == 'code':
                    error_code = error_body[info]
                elif info == 'message':
                    error_message = error_body[info]
                else:
                    additional_data[info] = error_body[info]
    except DecodeError:
        pass

    try:
        if error_code:
            error_code = StorageErrorCode(error_code)
            if error_code in [StorageErrorCode.condition_not_met]:
                raise_error = ResourceModifiedError
            if error_code in [StorageErrorCode.invalid_authentication_info,
                              StorageErrorCode.authentication_failed]:
                raise_error = ClientAuthenticationError
            if error_code in [StorageErrorCode.resource_not_found,
                              StorageErrorCode.invalid_property_name,
                              StorageErrorCode.invalid_source_uri,
                              StorageErrorCode.source_path_not_found,
                              StorageErrorCode.lease_name_mismatch,
                              StorageErrorCode.file_system_not_found,
                              StorageErrorCode.path_not_found,
                              StorageErrorCode.parent_not_found,
                              StorageErrorCode.invalid_destination_path,
                              StorageErrorCode.invalid_rename_source_path,
                              StorageErrorCode.lease_is_already_broken,
                              StorageErrorCode.invalid_source_or_destination_resource_type,
                              StorageErrorCode.rename_destination_parent_path_not_found]:
                raise_error = ResourceNotFoundError
            if error_code in [StorageErrorCode.account_already_exists,
                              StorageErrorCode.account_being_created,
                              StorageErrorCode.resource_already_exists,
                              StorageErrorCode.resource_type_mismatch,
                              StorageErrorCode.source_path_is_being_deleted,
                              StorageErrorCode.path_already_exists,
                              StorageErrorCode.destination_path_is_being_deleted,
                              StorageErrorCode.file_system_already_exists,
                              StorageErrorCode.file_system_being_deleted,
                              StorageErrorCode.path_conflict]:
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

    error = raise_error(message=error_message, response=storage_error.response,
                        continuation_token=storage_error.continuation_token)
    error.error_code = error_code
    error.additional_info = additional_data
    raise error
