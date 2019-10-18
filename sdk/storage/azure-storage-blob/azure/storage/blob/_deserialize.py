# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

from azure.core import MatchConditions

from ._shared.response_handlers import deserialize_metadata
from ._generated.models import ModifiedAccessConditions, SourceModifiedAccessConditions
from .models import BlobProperties, ContainerProperties


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
    # type: (PageList) -> Tuple(List[Dict[str, int]], List[Dict[str, int]])
    page_range = [] # type: ignore
    clear_range = [] # type: List
    if ranges.page_range:
        page_range = [{'start': b.start, 'end': b.end} for b in ranges.page_range] # type: ignore
    if ranges.clear_range:
        clear_range = [{'start': b.start, 'end': b.end} for b in ranges.clear_range]
    return page_range, clear_range  # type: ignore


def get_modify_conditions(kwargs):
    # type: (Dict[str, Any]) -> ModifiedAccessConditions
    if_match = None
    if_none_match = None
    match_condition = kwargs.pop('match_condition', None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop('etag', None)
    elif match_condition == MatchConditions.IfPresent:
        if_match = '*'
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop('etag', None)
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = '*'

    return ModifiedAccessConditions(
        if_modified_since=kwargs.pop('if_modified_since', None),
        if_unmodified_since=kwargs.pop('if_unmodified_since', None),
        if_match=if_match or kwargs.pop('if_match', None),
        if_none_match=if_none_match or kwargs.pop('if_none_match', None)
    )


def get_source_conditions(kwargs):
    # type: (Dict[str, Any]) -> SourceModifiedAccessConditions
    if_match = None
    if_none_match = None
    match_condition = kwargs.pop('source_match_condition', None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop('source_etag', None)
    elif match_condition == MatchConditions.IfPresent:
        if_match = '*'
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop('source_etag', None)
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = '*'

    return SourceModifiedAccessConditions(
        source_if_modified_since=kwargs.pop('source_if_modified_since', None),
        source_if_unmodified_since=kwargs.pop('source_if_unmodified_since', None),
        source_if_match=if_match or kwargs.pop('source_if_match', None),
        source_if_none_match=if_none_match or kwargs.pop('source_if_none_match', None)
    )
