# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from typing import (
    Any, cast, Collection, Dict, List, NoReturn, Tuple,
    TYPE_CHECKING
)
from xml.etree.ElementTree import Element

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.exceptions import (
    HttpResponseError,
    DecodeError,
    ResourceModifiedError,
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError
)
from ._models import (
    AnalyticsLogging,
    DeletedPathProperties,
    DirectoryProperties,
    FileProperties,
    LeaseProperties,
    Metrics,
    PathProperties,
    RetentionPolicy,
    StaticWebsite
)
from ._shared.models import StorageErrorCode
from ._shared.response_handlers import deserialize_metadata

if TYPE_CHECKING:
    from azure.core.rest import HttpResponse
    from azure.storage.blob import BlobProperties
    from ._generated.models import (
        BlobItemInternal,
        Path,
        PathList
    )
    from ._models import ContentSettings

_LOGGER = logging.getLogger(__name__)


def deserialize_dir_properties(
    response: "HttpResponse",
    obj: Any,
    headers: Dict[str, Any]
) -> DirectoryProperties:
    metadata = deserialize_metadata(response, obj, headers)
    dir_properties = DirectoryProperties(
        metadata=metadata,
        owner=response.headers.get('x-ms-owner'),
        group=response.headers.get('x-ms-group'),
        permissions=response.headers.get('x-ms-permissions'),
        acl=response.headers.get('x-ms-acl'),
        **headers
    )
    return dir_properties


def deserialize_file_properties(
    response: "HttpResponse",
    obj: Any,
    headers: Dict[str, Any]
) -> FileProperties:
    metadata = deserialize_metadata(response, obj, headers)
    # DataLake specific headers that are not deserialized in blob are pulled directly from the raw response header
    file_properties = FileProperties(
        metadata=metadata,
        encryption_context=response.headers.get('x-ms-encryption-context'),
        owner=response.headers.get('x-ms-owner'),
        group=response.headers.get('x-ms-group'),
        permissions=response.headers.get('x-ms-permissions'),
        acl=response.headers.get('x-ms-acl'),
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-blob-content-md5' in headers:
            file_properties.content_settings.content_md5 = headers['x-ms-blob-content-md5']
        else:
            file_properties.content_settings.content_md5 = None
    return file_properties


def deserialize_path_properties(path_list: List["Path"]) -> List[PathProperties]:
    return [PathProperties._from_generated(path) for path in path_list]  # pylint: disable=protected-access


def return_headers_and_deserialized_path_list(  # pylint: disable=name-too-long, unused-argument
    _,
    deserialized: "PathList",
    response_headers: Dict[str, Any]
) -> Tuple[Collection["Path"], Dict[str, Any]]:
    return deserialized.paths if deserialized.paths else {}, normalize_headers(response_headers)


def get_deleted_path_properties_from_generated_code(generated: "BlobItemInternal") -> DeletedPathProperties:  # pylint: disable=name-too-long
    deleted_path = DeletedPathProperties()
    deleted_path.name = generated.name
    deleted_path.deleted_time = generated.properties.deleted_time
    deleted_path.remaining_retention_days = generated.properties.remaining_retention_days
    deleted_path.deletion_id = generated.deletion_id
    return deleted_path


def is_file_path(_, __, headers: Dict[str, Any]) -> bool:
    return headers['x-ms-resource-type'] == "file"


def get_datalake_service_properties(datalake_properties: Dict[str, Any]) -> Dict[str, Any]:
    datalake_properties["analytics_logging"] = AnalyticsLogging._from_generated(  # pylint: disable=protected-access
        datalake_properties["analytics_logging"])
    datalake_properties["hour_metrics"] = Metrics._from_generated(datalake_properties["hour_metrics"])  # pylint: disable=protected-access
    datalake_properties["minute_metrics"] = Metrics._from_generated(  # pylint: disable=protected-access
        datalake_properties["minute_metrics"])
    datalake_properties["delete_retention_policy"] = RetentionPolicy._from_generated(  # pylint: disable=protected-access
        datalake_properties["delete_retention_policy"])
    datalake_properties["static_website"] = StaticWebsite._from_generated(  # pylint: disable=protected-access
        datalake_properties["static_website"])
    return datalake_properties


def from_blob_properties(blob_properties: "BlobProperties", **additional_args: Any) -> FileProperties:
    file_props = FileProperties()
    file_props.name = blob_properties.name
    file_props.etag = blob_properties.etag
    file_props.deleted = blob_properties.deleted
    file_props.metadata = blob_properties.metadata
    file_props.lease = cast(LeaseProperties, blob_properties.lease)
    file_props.lease.__class__ = LeaseProperties
    file_props.last_modified = blob_properties.last_modified
    file_props.creation_time = blob_properties.creation_time
    file_props.size = blob_properties.size
    file_props.deleted_time = blob_properties.deleted_time
    file_props.remaining_retention_days = blob_properties.remaining_retention_days
    file_props.content_settings = cast("ContentSettings", blob_properties.content_settings)

    # Parse additional Datalake-only properties
    file_props.encryption_context = additional_args.pop('encryption_context', None)
    file_props.owner = additional_args.pop('owner', None)
    file_props.group = additional_args.pop('group', None)
    file_props.permissions = additional_args.pop('permissions', None)
    file_props.acl = additional_args.pop('acl', None)

    return file_props


def normalize_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {}
    for key, value in headers.items():
        if key.startswith('x-ms-'):
            key = key[5:]
        normalized[key.lower().replace('-', '_')] = value
    return normalized


def process_storage_error(storage_error) -> NoReturn:  # type: ignore [misc] # pylint:disable=too-many-statements
    raise_error = HttpResponseError
    serialized = False
    if not storage_error.response:
        raise storage_error
    # If it is one of those three then it has been serialized prior by the generated layer.
    if isinstance(storage_error, (ResourceNotFoundError, ClientAuthenticationError, ResourceExistsError)):
        serialized = True
    error_code = storage_error.response.headers.get('x-ms-error-code')
    error_message = storage_error.message
    additional_data = {}
    error_dict = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(storage_error.response)
        # If it is an XML response
        if isinstance(error_body, Element):
            error_dict = {
                child.tag.lower(): child.text
                for child in error_body
            }
        # If it is a JSON response
        elif isinstance(error_body, dict):
            error_dict = error_body.get('error', {})
        elif not error_code:
            _LOGGER.warning(
                'Unexpected return type %s from ContentDecodePolicy.deserialize_from_http_generics.', type(error_body))
            error_dict = {'message': str(error_body)}

        # If we extracted from a Json or XML response
        if error_dict:
            error_code = error_dict.get('code')
            error_message = error_dict.get('message')
            additional_data = {k: v for k, v in error_dict.items() if k not in {'code', 'message'}}

    except DecodeError:
        pass

    try:
        # This check would be unnecessary if we have already serialized the error.
        if error_code and not serialized:
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

    # Error message should include all the error properties
    try:
        error_message += f"\nErrorCode:{error_code.value}"
    except AttributeError:
        error_message += f"\nErrorCode:{error_code}"
    for name, info in additional_data.items():
        error_message += f"\n{name}:{info}"

    # No need to create an instance if it has already been serialized by the generated layer
    if serialized:
        storage_error.message = error_message
        error = storage_error
    else:
        error = raise_error(message=error_message, response=storage_error.response)
    # Ensure these properties are stored in the error instance as well (not just the error message)
    error.error_code = error_code
    error.additional_info = additional_data
    # error.args is what's surfaced on the traceback - show error message in all cases
    error.args = (error.message,)

    try:
        # `from None` prevents us from double printing the exception (suppresses generated layer error context)
        exec("raise error from None")   # pylint: disable=exec-used # nosec
    except SyntaxError as exc:
        raise error from exc
