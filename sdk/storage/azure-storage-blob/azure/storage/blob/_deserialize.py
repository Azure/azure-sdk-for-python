# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from urllib.parse import unquote
from xml.etree.ElementTree import Element

from ._models import (
    BlobAnalyticsLogging,
    BlobProperties,
    BlobType,
    ContainerProperties,
    ContentSettings,
    CopyProperties,
    CorsRule,
    ImmutabilityPolicy,
    LeaseProperties,
    Metrics,
    ObjectReplicationPolicy,
    ObjectReplicationRule,
    RetentionPolicy,
    StaticWebsite,
)
from ._shared.models import get_enum_value
from ._shared.response_handlers import deserialize_metadata

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse
    from ._generated.models import (
        BlobItemInternal,
        BlobTags,
        PageList,
        StorageServiceProperties,
        StorageServiceStats,
    )
    from ._shared.models import LocationMode


def deserialize_pipeline_response_into_cls(cls_method, response: "PipelineResponse", obj: Any, headers: Dict[str, Any]):
    try:
        deserialized_response = response.http_response
    except AttributeError:
        deserialized_response = response
    return cls_method(deserialized_response, obj, headers)


def deserialize_blob_properties(response: "PipelineResponse", obj: Any, headers: Dict[str, Any]) -> BlobProperties:
    blob_properties = BlobProperties(
        metadata=deserialize_metadata(response, obj, headers),
        object_replication_source_properties=deserialize_ors_policies(response.http_response.headers),
        **headers
    )
    if "Content-Range" in headers:
        if "x-ms-blob-content-md5" in headers:
            blob_properties.content_settings.content_md5 = headers["x-ms-blob-content-md5"]
        else:
            blob_properties.content_settings.content_md5 = None
    return blob_properties


def deserialize_ors_policies(policy_dictionary: Optional[Dict[str, str]]) -> Optional[List[ObjectReplicationPolicy]]:

    if policy_dictionary is None:
        return None
    # For source blobs (blobs that have policy ids and rule ids applied to them),
    # the header will be formatted as "x-ms-or-<policy_id>_<rule_id>: {Complete, Failed}".
    # The value of this header is the status of the replication.
    or_policy_status_headers = {
        key: val for key, val in policy_dictionary.items() if "or-" in key and key != "x-ms-or-policy-id"
    }

    parsed_result: Dict[str, List[ObjectReplicationRule]] = {}

    for key, val in or_policy_status_headers.items():
        # list blobs gives or-policy_rule and get blob properties gives x-ms-or-policy_rule
        policy_and_rule_ids = key.split("or-")[1].split("_")
        policy_id = policy_and_rule_ids[0]
        rule_id = policy_and_rule_ids[1]

        # If we are seeing this policy for the first time, create a new list to store rule_id -> result
        parsed_result[policy_id] = parsed_result.get(policy_id) or []
        parsed_result[policy_id].append(ObjectReplicationRule(rule_id=rule_id, status=val))

    result_list = [ObjectReplicationPolicy(policy_id=k, rules=v) for k, v in parsed_result.items()]

    return result_list


# iter_bytes and iter_raw return generators
class _DownloadResponse:
    """Wrapper for download response that holds the stream, properties, and content length.

    The generated download operation returns ``response.iter_bytes()`` (a generator)
    as the deserialized body. ``StorageStreamDownloader`` expects to access
    ``.properties``, ``.content_length``, and iteration on the response object, so
    this wrapper bundles them together.
    """

    def __init__(
        self,
        stream: Any,
        properties: BlobProperties,
        response: "PipelineResponse",
    ) -> None:
        self._stream = stream
        self.properties = properties
        self.response = response.http_response
        self.content_length = int(response.http_response.headers.get("Content-Length", 0))

    def __iter__(self):
        return iter(self._stream)

    def __aiter__(self):
        return self._stream.__aiter__()


def deserialize_blob_stream(
    response: "PipelineResponse",
    obj: Any,
    headers: Dict[str, Any],
) -> Tuple["LocationMode", "_DownloadResponse"]:
    blob_properties = deserialize_blob_properties(response, obj, headers)
    download_response = _DownloadResponse(obj, blob_properties, response)
    return response.http_response.location_mode, download_response


def deserialize_container_properties(
    response: "PipelineResponse", obj: Any, headers: Dict[str, Any]
) -> ContainerProperties:
    metadata = deserialize_metadata(response, obj, headers)
    container_properties = ContainerProperties(metadata=metadata, **headers)
    return container_properties


def get_page_ranges_result(ranges: "PageList") -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]:
    page_range = []
    clear_range = []
    if ranges.page_range:
        page_range = [{"start": b.start, "end": b.end} for b in ranges.page_range]
    if ranges.clear_range:
        clear_range = [{"start": b.start, "end": b.end} for b in ranges.clear_range]
    return page_range, clear_range


def service_stats_deserialize(generated: "StorageServiceStats") -> Dict[str, Any]:
    status = None
    last_sync_time = None
    if generated.geo_replication is not None:
        status = generated.geo_replication.status
        last_sync_time = generated.geo_replication.last_sync_time
    return {"geo_replication": {"status": status, "last_sync_time": last_sync_time}}


def service_properties_deserialize(generated: "StorageServiceProperties") -> Dict[str, Any]:
    cors_list = None
    if generated.cors is not None:
        cors_list = [CorsRule._from_generated(cors) for cors in generated.cors]  # pylint: disable=protected-access
    return {
        "analytics_logging": BlobAnalyticsLogging._from_generated(  # pylint: disable=protected-access
            generated.logging
        ),
        "hour_metrics": Metrics._from_generated(generated.hour_metrics),  # pylint: disable=protected-access
        "minute_metrics": Metrics._from_generated(generated.minute_metrics),  # pylint: disable=protected-access
        "cors": cors_list,
        "target_version": generated.default_service_version,
        "delete_retention_policy": RetentionPolicy._from_generated(  # pylint: disable=protected-access
            generated.delete_retention_policy
        ),
        "static_website": StaticWebsite._from_generated(generated.static_website),  # pylint: disable=protected-access
    }


def get_blob_properties_from_generated_code(generated: "BlobItemInternal") -> BlobProperties:
    # Hot path for list_blobs: bypass _RestField descriptors and read straight from the
    # underlying ``_data`` dicts populated by ``_init_from_xml``. With eager deserialization,
    # scalar values in _data are already typed (int, bool, datetime, etc.).
    blob = BlobProperties()
    gen_d = generated._data  # pylint: disable=protected-access

    name_obj = gen_d.get("name")
    if name_obj is not None:
        name_d = name_obj._data  # pylint: disable=protected-access
        content = name_d.get("content")
        if name_d.get("encoded") and content is not None:
            blob.name = unquote(content)
        else:
            blob.name = content  # type: ignore [assignment]

    props = gen_d.get("properties")
    props_d: Dict[str, Any] = props._data if props is not None else {}  # pylint: disable=protected-access

    blob_type = get_enum_value(props_d.get("blobType"))
    blob.blob_type = BlobType(blob_type) if blob_type and blob_type != "None" else blob_type  # type: ignore
    blob.etag = props_d.get("etag")
    blob.deleted = gen_d.get("deleted")
    blob.snapshot = gen_d.get("snapshot")
    blob.is_append_blob_sealed = props_d.get("isSealed")

    metadata_obj = gen_d.get("metadata")
    if metadata_obj is not None:
        meta_d = metadata_obj._data  # pylint: disable=protected-access
        blob.metadata = {k: v for k, v in meta_d.items() if k != "Encrypted"}  # type: ignore [assignment]
        blob.encrypted_metadata = meta_d.get("encrypted")
    else:
        blob.metadata = {}  # type: ignore [assignment]
        blob.encrypted_metadata = None

    # Inline LeaseProperties._from_generated
    lease = LeaseProperties()
    lease.status = get_enum_value(props_d.get("leaseStatus"))
    lease.state = get_enum_value(props_d.get("leaseState"))
    lease.duration = get_enum_value(props_d.get("leaseDuration"))
    blob.lease = lease

    # Inline CopyProperties._from_generated
    copy = CopyProperties()
    copy.id = props_d.get("copyId") or None
    copy.status = get_enum_value(props_d.get("copyStatus")) or None
    copy.source = props_d.get("copySource") or None
    copy.progress = props_d.get("copyProgress") or None
    copy.completion_time = props_d.get("copyCompletionTime") or None
    copy.status_description = props_d.get("copyStatusDescription") or None
    copy.incremental_copy = props_d.get("incrementalCopy") or None
    copy.destination_snapshot = props_d.get("destinationSnapshot") or None
    blob.copy = copy

    blob.last_modified = props_d.get("lastModified")
    blob.creation_time = props_d.get("creationTime")  # type: ignore [assignment]

    # Inline ContentSettings._from_generated
    settings = ContentSettings()
    settings.content_type = props_d.get("contentType") or None
    settings.content_encoding = props_d.get("contentEncoding") or None
    settings.content_language = props_d.get("contentLanguage") or None
    settings.content_md5 = props_d.get("contentMd5") or None
    settings.content_disposition = props_d.get("contentDisposition") or None
    settings.cache_control = props_d.get("cacheControl") or None
    blob.content_settings = settings

    blob.size = props_d.get("contentLength")  # type: ignore [assignment]
    blob.page_blob_sequence_number = props_d.get("blobSequenceNumber")
    blob.server_encrypted = props_d.get("serverEncrypted")  # type: ignore [assignment]
    blob.encryption_scope = props_d.get("encryptionScope")
    blob.deleted_time = props_d.get("deletedTime")
    blob.remaining_retention_days = props_d.get("remainingRetentionDays")
    blob.blob_tier = props_d.get("accessTier")  # type: ignore [assignment]
    blob.smart_access_tier = props_d.get("smartAccessTier")
    blob.rehydrate_priority = props_d.get("rehydratePriority")
    blob.blob_tier_inferred = props_d.get("accessTierInferred")
    blob.archive_status = props_d.get("archiveStatus")
    blob.blob_tier_change_time = props_d.get("accessTierChangeTime")
    blob.version_id = gen_d.get("versionId")
    blob.is_current_version = gen_d.get("isCurrentVersion")
    blob.tag_count = props_d.get("tagCount")
    blob.tags = parse_tags(gen_d.get("blobTags"))

    or_metadata = gen_d.get("objectReplicationMetadata")
    blob.object_replication_source_properties = deserialize_ors_policies(
        or_metadata._data if or_metadata is not None else None  # pylint: disable=protected-access
    )
    blob.last_accessed_on = props_d.get("lastAccessedOn")

    # Inline ImmutabilityPolicy._from_generated
    immutability = ImmutabilityPolicy()
    immutability.expiry_time = props_d.get("immutabilityPolicyExpiresOn")
    immutability.policy_mode = props_d.get("immutabilityPolicyMode")
    blob.immutability_policy = immutability

    blob.has_legal_hold = props_d.get("legalHold")
    blob.has_versions_only = gen_d.get("hasVersionsOnly")
    return blob


def parse_tags(generated_tags: Optional["BlobTags"]) -> Optional[Dict[str, str]]:
    """Deserialize a list of BlobTag objects into a dict.

    :param Optional[BlobTags] generated_tags:
        A list containing the BlobTag objects from generated code.
    :return: A dictionary of the BlobTag objects.
    :rtype: Optional[Dict[str, str]]
    """
    if generated_tags:
        # Read straight from _data to avoid descriptor overhead. blob_tag_set's
        # rest_name is "blobTagSet"; each BlobTag stores key/value under their
        # rest_names (defaults to attribute names "key"/"value").
        tag_set = generated_tags._data.get("blobTagSet") or []  # pylint: disable=protected-access
        return {t._data.get("key"): t._data.get("value") for t in tag_set}  # pylint: disable=protected-access
    return None


def load_single_xml_node(element: Element, name: str) -> Optional[Element]:
    return element.find(name)


def load_many_xml_nodes(element: Element, name: str, wrapper: Optional[str] = None) -> List[Optional[Element]]:
    found_element: Optional[Element] = element
    if wrapper:
        found_element = load_single_xml_node(element, wrapper)
    if found_element is None:
        return []
    return list(found_element.findall(name))


def load_xml_string(element: Element, name: str) -> Optional[str]:
    node = element.find(name)
    if node is None or not node.text:
        return None
    return node.text


def load_xml_int(element: Element, name: str) -> Optional[int]:
    node = element.find(name)
    if node is None or not node.text:
        return None
    return int(node.text)