# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from typing import (
    Any, cast, Collection, Dict, List, Tuple,
    TYPE_CHECKING
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
from ._shared.response_handlers import deserialize_metadata

if TYPE_CHECKING:
    from azure.core.rest import RestRequestsTransportResponse  # type: ignore [attr-defined]
    from azure.storage.blob import BlobProperties
    from ._generated.models import (
        BlobItemInternal,
        Path,
        PathList
    )
    from ._models import ContentSettings

_LOGGER = logging.getLogger(__name__)


def deserialize_dir_properties(
    response: "RestRequestsTransportResponse",
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
    response: "RestRequestsTransportResponse",
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
