# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------_
from typing import (
    Any, cast, Dict, List, Optional, Tuple,
    TYPE_CHECKING
)

from ._generated.models import ShareFileRangeList
from ._models import DirectoryProperties, FileProperties, ShareProperties
from ._shared.response_handlers import deserialize_metadata

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse
    from ._shared.models import LocationMode


def deserialize_share_properties(response: "PipelineResponse", obj: Any, headers: Dict[str, Any]) -> ShareProperties:
    metadata = deserialize_metadata(response, obj, headers)
    share_properties = ShareProperties(
        metadata=metadata,
        **headers
    )
    return share_properties


def deserialize_directory_properties(
    response: "PipelineResponse",
    obj: Any,
    headers: Dict[str, Any]
) -> DirectoryProperties:
    metadata = deserialize_metadata(response, obj, headers)
    directory_properties = DirectoryProperties(
        metadata=metadata,
        **headers
    )
    return directory_properties


def deserialize_file_properties(response: "PipelineResponse", obj: Any, headers: Dict[str, Any]) -> FileProperties:
    metadata = deserialize_metadata(response, obj, headers)
    file_properties = FileProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-content-md5' in headers:
            file_properties.content_settings.content_md5 = headers['x-ms-content-md5']
        else:
            file_properties.content_settings.content_md5 = None
    return file_properties


def deserialize_file_stream(
    response: "PipelineResponse",
    obj: Any,
    headers: Dict[str, Any]
) -> Tuple["LocationMode", Any]:
    file_properties = deserialize_file_properties(response, obj, headers)
    obj.properties = file_properties
    return response.http_response.location_mode, obj


# Extracts out file permission
def deserialize_permission(response: "PipelineResponse", obj: Any, headers: Dict[str, Any]) -> Optional[str]:  # pylint: disable=unused-argument
    return cast(Optional[str], obj.permission)


# Extracts out file permission key
def deserialize_permission_key(response: "PipelineResponse", obj: Any, headers: Dict[str, Any]) -> Optional[str]:  # pylint: disable=unused-argument
    if response is None or headers is None:
        return None
    return cast(Optional[str], headers.get('x-ms-file-permission-key', None))


def get_file_ranges_result(ranges: ShareFileRangeList) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]:
    file_ranges = []
    clear_ranges = []
    if ranges.ranges:
        file_ranges = [{'start': file_range.start, 'end': file_range.end} for file_range in ranges.ranges]
    if ranges.clear_ranges:
        clear_ranges = [{'start': clear_range.start, 'end': clear_range.end} for clear_range in ranges.clear_ranges]
    return file_ranges, clear_ranges
