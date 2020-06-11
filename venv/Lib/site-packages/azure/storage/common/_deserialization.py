# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from dateutil import parser

from ._common_conversion import _to_str

try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree

from .models import (
    ServiceProperties,
    Logging,
    Metrics,
    CorsRule,
    AccessPolicy,
    _dict,
    GeoReplication,
    ServiceStats,
    DeleteRetentionPolicy,
    StaticWebsite,
)


def _to_int(value):
    return value if value is None else int(value)


def _bool(value):
    return value.lower() == 'true'


def _to_upper_str(value):
    return _to_str(value).upper() if value is not None else None


def _get_download_size(start_range, end_range, resource_size):
    if start_range is not None:
        end_range = end_range if end_range else (resource_size if resource_size else None)
        if end_range is not None:
            return end_range - start_range
        else:
            return None
    else:
        return resource_size


GET_PROPERTIES_ATTRIBUTE_MAP = {
    'last-modified': (None, 'last_modified', parser.parse),
    'etag': (None, 'etag', _to_str),
    'x-ms-blob-type': (None, 'blob_type', _to_str),
    'content-length': (None, 'content_length', _to_int),
    'content-range': (None, 'content_range', _to_str),
    'x-ms-blob-sequence-number': (None, 'page_blob_sequence_number', _to_int),
    'x-ms-blob-committed-block-count': (None, 'append_blob_committed_block_count', _to_int),
    'x-ms-blob-public-access': (None, 'public_access', _to_str),
    'x-ms-access-tier': (None, 'blob_tier', _to_str),
    'x-ms-access-tier-change-time': (None, 'blob_tier_change_time', parser.parse),
    'x-ms-access-tier-inferred': (None, 'blob_tier_inferred', _bool),
    'x-ms-archive-status': (None, 'rehydration_status', _to_str),
    'x-ms-share-quota': (None, 'quota', _to_int),
    'x-ms-server-encrypted': (None, 'server_encrypted', _bool),
    'x-ms-creation-time': (None, 'creation_time', parser.parse),
    'content-type': ('content_settings', 'content_type', _to_str),
    'cache-control': ('content_settings', 'cache_control', _to_str),
    'content-encoding': ('content_settings', 'content_encoding', _to_str),
    'content-disposition': ('content_settings', 'content_disposition', _to_str),
    'content-language': ('content_settings', 'content_language', _to_str),
    'content-md5': ('content_settings', 'content_md5', _to_str),
    'x-ms-lease-status': ('lease', 'status', _to_str),
    'x-ms-lease-state': ('lease', 'state', _to_str),
    'x-ms-lease-duration': ('lease', 'duration', _to_str),
    'x-ms-copy-id': ('copy', 'id', _to_str),
    'x-ms-copy-source': ('copy', 'source', _to_str),
    'x-ms-copy-status': ('copy', 'status', _to_str),
    'x-ms-copy-progress': ('copy', 'progress', _to_str),
    'x-ms-copy-completion-time': ('copy', 'completion_time', parser.parse),
    'x-ms-copy-destination-snapshot': ('copy', 'destination_snapshot_time', _to_str),
    'x-ms-copy-status-description': ('copy', 'status_description', _to_str),
    'x-ms-has-immutability-policy': (None, 'has_immutability_policy', _bool),
    'x-ms-has-legal-hold': (None, 'has_legal_hold', _bool),
}


def _parse_metadata(response):
    '''
    Extracts out resource metadata information.
    '''

    if response is None or response.headers is None:
        return None

    metadata = _dict()
    for key, value in response.headers.items():
        if key.lower().startswith('x-ms-meta-'):
            metadata[key[10:]] = _to_str(value)

    return metadata


def _parse_properties(response, result_class):
    '''
    Extracts out resource properties and metadata information.
    Ignores the standard http headers.
    '''

    if response is None or response.headers is None:
        return None

    props = result_class()
    for key, value in response.headers.items():
        info = GET_PROPERTIES_ATTRIBUTE_MAP.get(key)
        if info:
            if info[0] is None:
                setattr(props, info[1], info[2](value))
            else:
                attr = getattr(props, info[0])
                setattr(attr, info[1], info[2](value))

    if hasattr(props, 'blob_type') and props.blob_type == 'PageBlob' and hasattr(props, 'blob_tier') and props.blob_tier is not None:
        props.blob_tier = _to_upper_str(props.blob_tier)
    return props


def _parse_length_from_content_range(content_range):
    '''
    Parses the blob length from the content range header: bytes 1-3/65537
    '''
    if content_range is None:
        return None

    # First, split in space and take the second half: '1-3/65537'
    # Next, split on slash and take the second half: '65537'
    # Finally, convert to an int: 65537
    return int(content_range.split(' ', 1)[1].split('/', 1)[1])


def _convert_xml_to_signed_identifiers(response):
    '''
    <?xml version="1.0" encoding="utf-8"?>
    <SignedIdentifiers>
      <SignedIdentifier>
        <Id>unique-value</Id>
        <AccessPolicy>
          <Start>start-time</Start>
          <Expiry>expiry-time</Expiry>
          <Permission>abbreviated-permission-list</Permission>
        </AccessPolicy>
      </SignedIdentifier>
    </SignedIdentifiers>
    '''
    if response is None or response.body is None:
        return None

    list_element = ETree.fromstring(response.body)
    signed_identifiers = _dict()

    for signed_identifier_element in list_element.findall('SignedIdentifier'):
        # Id element
        id = signed_identifier_element.find('Id').text

        # Access policy element
        access_policy = AccessPolicy()
        access_policy_element = signed_identifier_element.find('AccessPolicy')
        if access_policy_element is not None:
            start_element = access_policy_element.find('Start')
            if start_element is not None:
                access_policy.start = parser.parse(start_element.text)

            expiry_element = access_policy_element.find('Expiry')
            if expiry_element is not None:
                access_policy.expiry = parser.parse(expiry_element.text)

            access_policy.permission = access_policy_element.findtext('Permission')

        signed_identifiers[id] = access_policy

    return signed_identifiers


def _convert_xml_to_service_stats(response):
    '''
    <?xml version="1.0" encoding="utf-8"?>
    <StorageServiceStats>
      <GeoReplication>      
          <Status>live|bootstrap|unavailable</Status>
          <LastSyncTime>sync-time|<empty></LastSyncTime>
      </GeoReplication>
    </StorageServiceStats>
    '''
    if response is None or response.body is None:
        return None

    service_stats_element = ETree.fromstring(response.body)

    geo_replication_element = service_stats_element.find('GeoReplication')

    geo_replication = GeoReplication()
    geo_replication.status = geo_replication_element.find('Status').text
    last_sync_time = geo_replication_element.find('LastSyncTime').text
    geo_replication.last_sync_time = parser.parse(last_sync_time) if last_sync_time else None

    service_stats = ServiceStats()
    service_stats.geo_replication = geo_replication
    return service_stats


def _convert_xml_to_service_properties(response):
    '''
    <?xml version="1.0" encoding="utf-8"?>
    <StorageServiceProperties>
        <Logging>
            <Version>version-number</Version>
            <Delete>true|false</Delete>
            <Read>true|false</Read>
            <Write>true|false</Write>
            <RetentionPolicy>
                <Enabled>true|false</Enabled>
                <Days>number-of-days</Days>
            </RetentionPolicy>
        </Logging>
        <HourMetrics>
            <Version>version-number</Version>
            <Enabled>true|false</Enabled>
            <IncludeAPIs>true|false</IncludeAPIs>
            <RetentionPolicy>
                <Enabled>true|false</Enabled>
                <Days>number-of-days</Days>
            </RetentionPolicy>
        </HourMetrics>
        <MinuteMetrics>
            <Version>version-number</Version>
            <Enabled>true|false</Enabled>
            <IncludeAPIs>true|false</IncludeAPIs>
            <RetentionPolicy>
                <Enabled>true|false</Enabled>
                <Days>number-of-days</Days>
            </RetentionPolicy>
        </MinuteMetrics>
        <Cors>
            <CorsRule>
                <AllowedOrigins>comma-separated-list-of-allowed-origins</AllowedOrigins>
                <AllowedMethods>comma-separated-list-of-HTTP-verb</AllowedMethods>
                <MaxAgeInSeconds>max-caching-age-in-seconds</MaxAgeInSeconds>
                <ExposedHeaders>comma-seperated-list-of-response-headers</ExposedHeaders>
                <AllowedHeaders>comma-seperated-list-of-request-headers</AllowedHeaders>
            </CorsRule>
        </Cors>
        <DeleteRetentionPolicy>
             <Enabled>true|false</Enabled>
             <Days>number-of-days</Days>
        </DeleteRetentionPolicy>
        <StaticWebsite>
            <Enabled>true|false</Enabled>
            <IndexDocument></IndexDocument>
            <ErrorDocument404Path></ErrorDocument404Path>
        </StaticWebsite>
    </StorageServiceProperties>
    '''
    if response is None or response.body is None:
        return None

    service_properties_element = ETree.fromstring(response.body)
    service_properties = ServiceProperties()

    # Logging
    logging = service_properties_element.find('Logging')
    if logging is not None:
        service_properties.logging = Logging()
        service_properties.logging.version = logging.find('Version').text
        service_properties.logging.delete = _bool(logging.find('Delete').text)
        service_properties.logging.read = _bool(logging.find('Read').text)
        service_properties.logging.write = _bool(logging.find('Write').text)

        _convert_xml_to_retention_policy(logging.find('RetentionPolicy'),
                                         service_properties.logging.retention_policy)
    # HourMetrics
    hour_metrics_element = service_properties_element.find('HourMetrics')
    if hour_metrics_element is not None:
        service_properties.hour_metrics = Metrics()
        _convert_xml_to_metrics(hour_metrics_element, service_properties.hour_metrics)

    # MinuteMetrics
    minute_metrics_element = service_properties_element.find('MinuteMetrics')
    if minute_metrics_element is not None:
        service_properties.minute_metrics = Metrics()
        _convert_xml_to_metrics(minute_metrics_element, service_properties.minute_metrics)

    # CORS
    cors = service_properties_element.find('Cors')
    if cors is not None:
        service_properties.cors = list()
        for rule in cors.findall('CorsRule'):
            allowed_origins = rule.find('AllowedOrigins').text.split(',')

            allowed_methods = rule.find('AllowedMethods').text.split(',')

            max_age_in_seconds = int(rule.find('MaxAgeInSeconds').text)

            cors_rule = CorsRule(allowed_origins, allowed_methods, max_age_in_seconds)

            exposed_headers = rule.find('ExposedHeaders').text
            if exposed_headers is not None:
                cors_rule.exposed_headers = exposed_headers.split(',')

            allowed_headers = rule.find('AllowedHeaders').text
            if allowed_headers is not None:
                cors_rule.allowed_headers = allowed_headers.split(',')

            service_properties.cors.append(cors_rule)

    # Target version
    target_version = service_properties_element.find('DefaultServiceVersion')
    if target_version is not None:
        service_properties.target_version = target_version.text

    # DeleteRetentionPolicy
    delete_retention_policy_element = service_properties_element.find('DeleteRetentionPolicy')
    if delete_retention_policy_element is not None:
        service_properties.delete_retention_policy = DeleteRetentionPolicy()
        policy_enabled = _bool(delete_retention_policy_element.find('Enabled').text)
        service_properties.delete_retention_policy.enabled = policy_enabled

        if policy_enabled:
            service_properties.delete_retention_policy.days = int(delete_retention_policy_element.find('Days').text)

    # StaticWebsite
    static_website_element = service_properties_element.find('StaticWebsite')
    if static_website_element is not None:
        service_properties.static_website = StaticWebsite()
        service_properties.static_website.enabled = _bool(static_website_element.find('Enabled').text)

        index_document_element = static_website_element.find('IndexDocument')
        if index_document_element is not None:
            service_properties.static_website.index_document = index_document_element.text

        error_document_element = static_website_element.find('ErrorDocument404Path')
        if error_document_element is not None:
            service_properties.static_website.error_document_404_path = error_document_element.text

    return service_properties


def _convert_xml_to_metrics(xml, metrics):
    '''
    <Version>version-number</Version>
    <Enabled>true|false</Enabled>
    <IncludeAPIs>true|false</IncludeAPIs>
    <RetentionPolicy>
        <Enabled>true|false</Enabled>
        <Days>number-of-days</Days>
    </RetentionPolicy>
    '''
    # Version
    metrics.version = xml.find('Version').text

    # Enabled
    metrics.enabled = _bool(xml.find('Enabled').text)

    # IncludeAPIs
    include_apis_element = xml.find('IncludeAPIs')
    if include_apis_element is not None:
        metrics.include_apis = _bool(include_apis_element.text)

    # RetentionPolicy
    _convert_xml_to_retention_policy(xml.find('RetentionPolicy'), metrics.retention_policy)


def _convert_xml_to_retention_policy(xml, retention_policy):
    '''
    <Enabled>true|false</Enabled>
    <Days>number-of-days</Days>
    '''
    # Enabled
    retention_policy.enabled = _bool(xml.find('Enabled').text)

    # Days
    days_element = xml.find('Days')
    if days_element is not None:
        retention_policy.days = int(days_element.text)
