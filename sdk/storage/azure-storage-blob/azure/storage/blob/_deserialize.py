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
from ._models import BlobProperties, ContainerProperties, BlobAnalyticsLogging, Metrics, CorsRule, RetentionPolicy, \
    StaticWebsite

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


def service_stats_deserialize(generated):
    """Deserialize a ServiceStats objects into a dict.
    """
    return {
        'geo_replication': {
            'status': generated.geo_replication.status,
            'last_sync_time': generated.geo_replication.last_sync_time,
        }
    }


def service_properties_deserialize(generated):
    """Deserialize a ServiceProperties objects into a dict.
    """
    return {
        'analytics_logging': BlobAnalyticsLogging._from_generated(generated.logging),  # pylint: disable=protected-access
        'hour_metrics': Metrics._from_generated(generated.hour_metrics),  # pylint: disable=protected-access
        'minute_metrics': Metrics._from_generated(generated.minute_metrics),  # pylint: disable=protected-access
        'cors': [CorsRule._from_generated(cors) for cors in generated.cors],  # pylint: disable=protected-access
        'target_version': generated.default_service_version,  # pylint: disable=protected-access
        'delete_retention_policy': RetentionPolicy._from_generated(generated.delete_retention_policy),  # pylint: disable=protected-access
        'static_website': StaticWebsite._from_generated(generated.static_website),  # pylint: disable=protected-access
    }
