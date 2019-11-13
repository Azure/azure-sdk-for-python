# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

from typing import (  # pylint: disable=unused-import
    Tuple, Dict, List,
    TYPE_CHECKING
)

from ._shared.response_handlers import deserialize_metadata
from ._models import BlobProperties, ContainerProperties

if TYPE_CHECKING:
    from azure.storage.blob._generated.models import PageList


def deserialize_blob_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    blob_properties = BlobProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-blob-content-md5' in headers:
            blob_properties.content_settings.content_md5 = headers['x-ms-blob-content-md5']
        else:
            blob_properties.content_settings.content_md5 = None
    return blob_properties


def deserialize_blob_stream(response, obj, headers):
    blob_properties = deserialize_blob_properties(response, obj, headers)
    obj.properties = blob_properties
    return response.location_mode, obj


def deserialize_container_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    container_properties = ContainerProperties(
        metadata=metadata,
        **headers
    )
    return container_properties


def get_page_ranges_result(ranges):
    # type: (PageList) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]
    page_range = [] # type: ignore
    clear_range = [] # type: List
    if ranges.page_range:
        page_range = [{'start': b.start, 'end': b.end} for b in ranges.page_range] # type: ignore
    if ranges.clear_range:
        clear_range = [{'start': b.start, 'end': b.end} for b in ranges.clear_range]
    return page_range, clear_range  # type: ignore
