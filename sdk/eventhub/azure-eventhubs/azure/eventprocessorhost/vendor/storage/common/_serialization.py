# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import uuid
from datetime import date
from io import (BytesIO, IOBase, SEEK_SET, SEEK_END, UnsupportedOperation)
from os import fstat
from time import time
from wsgiref.handlers import format_date_time

from dateutil.tz import tzutc

if sys.version_info >= (3,):
    from urllib.parse import quote as url_quote
else:
    from urllib2 import quote as url_quote

try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree

from ._error import (
    _ERROR_VALUE_SHOULD_BE_BYTES,
    _ERROR_VALUE_SHOULD_BE_BYTES_OR_STREAM,
    _ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM
)
from .models import (
    _unicode_type,
)
from ._common_conversion import (
    _str,
)


def _to_utc_datetime(value):
    # Azure expects the date value passed in to be UTC.
    # Azure will always return values as UTC.
    # If a date is passed in without timezone info, it is assumed to be UTC.
    if value.tzinfo:
        value = value.astimezone(tzutc())
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def _update_request(request, x_ms_version, user_agent_string):
    # Verify body
    if request.body:
        request.body = _get_data_bytes_or_stream_only('request.body', request.body)
        length = _len_plus(request.body)

        # only scenario where this case is plausible is if the stream object is not seekable.
        if length is None:
            raise ValueError(_ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM)

        # if it is PUT, POST, MERGE, DELETE, need to add content-length to header.
        if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
            request.headers['Content-Length'] = str(length)

    # append addtional headers based on the service
    request.headers['x-ms-version'] = x_ms_version
    request.headers['User-Agent'] = user_agent_string
    request.headers['x-ms-client-request-id'] = str(uuid.uuid1())

    # If the host has a path component (ex local storage), move it
    path = request.host.split('/', 1)
    if len(path) == 2:
        request.host = path[0]
        request.path = '/{}{}'.format(path[1], request.path)

    # Encode and optionally add local storage prefix to path
    request.path = url_quote(request.path, '/()$=\',~')


def _add_metadata_headers(metadata, request):
    if metadata:
        if not request.headers:
            request.headers = {}
        for name, value in metadata.items():
            request.headers['x-ms-meta-' + name] = value


def _add_date_header(request):
    current_time = format_date_time(time())
    request.headers['x-ms-date'] = current_time


def _get_data_bytes_only(param_name, param_value):
    '''Validates the request body passed in and converts it to bytes
    if our policy allows it.'''
    if param_value is None:
        return b''

    if isinstance(param_value, bytes):
        return param_value

    raise TypeError(_ERROR_VALUE_SHOULD_BE_BYTES.format(param_name))


def _get_data_bytes_or_stream_only(param_name, param_value):
    '''Validates the request body passed in is a stream/file-like or bytes
    object.'''
    if param_value is None:
        return b''

    if isinstance(param_value, bytes) or hasattr(param_value, 'read'):
        return param_value

    raise TypeError(_ERROR_VALUE_SHOULD_BE_BYTES_OR_STREAM.format(param_name))


def _get_request_body(request_body):
    '''Converts an object into a request body.  If it's None
    we'll return an empty string, if it's one of our objects it'll
    convert it to XML and return it.  Otherwise we just use the object
    directly'''
    if request_body is None:
        return b''

    if isinstance(request_body, bytes) or isinstance(request_body, IOBase):
        return request_body

    if isinstance(request_body, _unicode_type):
        return request_body.encode('utf-8')

    request_body = str(request_body)
    if isinstance(request_body, _unicode_type):
        return request_body.encode('utf-8')

    return request_body


def _convert_signed_identifiers_to_xml(signed_identifiers):
    if signed_identifiers is None:
        return ''

    sis = ETree.Element('SignedIdentifiers')
    for id, access_policy in signed_identifiers.items():
        # Root signed identifers element
        si = ETree.SubElement(sis, 'SignedIdentifier')

        # Id element
        ETree.SubElement(si, 'Id').text = id

        # Access policy element
        policy = ETree.SubElement(si, 'AccessPolicy')

        if access_policy.start:
            start = access_policy.start
            if isinstance(access_policy.start, date):
                start = _to_utc_datetime(start)
            ETree.SubElement(policy, 'Start').text = start

        if access_policy.expiry:
            expiry = access_policy.expiry
            if isinstance(access_policy.expiry, date):
                expiry = _to_utc_datetime(expiry)
            ETree.SubElement(policy, 'Expiry').text = expiry

        if access_policy.permission:
            ETree.SubElement(policy, 'Permission').text = _str(access_policy.permission)

    # Add xml declaration and serialize
    try:
        stream = BytesIO()
        ETree.ElementTree(sis).write(stream, xml_declaration=True, encoding='utf-8', method='xml')
    except:
        raise
    finally:
        output = stream.getvalue()
        stream.close()

    return output


def _convert_service_properties_to_xml(logging, hour_metrics, minute_metrics,
                                       cors, target_version=None, delete_retention_policy=None, static_website=None):
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
    service_properties_element = ETree.Element('StorageServiceProperties')

    # Logging
    if logging:
        logging_element = ETree.SubElement(service_properties_element, 'Logging')
        ETree.SubElement(logging_element, 'Version').text = logging.version
        ETree.SubElement(logging_element, 'Delete').text = str(logging.delete)
        ETree.SubElement(logging_element, 'Read').text = str(logging.read)
        ETree.SubElement(logging_element, 'Write').text = str(logging.write)

        retention_element = ETree.SubElement(logging_element, 'RetentionPolicy')
        _convert_retention_policy_to_xml(logging.retention_policy, retention_element)

    # HourMetrics
    if hour_metrics:
        hour_metrics_element = ETree.SubElement(service_properties_element, 'HourMetrics')
        _convert_metrics_to_xml(hour_metrics, hour_metrics_element)

    # MinuteMetrics
    if minute_metrics:
        minute_metrics_element = ETree.SubElement(service_properties_element, 'MinuteMetrics')
        _convert_metrics_to_xml(minute_metrics, minute_metrics_element)

    # CORS
    # Make sure to still serialize empty list
    if cors is not None:
        cors_element = ETree.SubElement(service_properties_element, 'Cors')
        for rule in cors:
            cors_rule = ETree.SubElement(cors_element, 'CorsRule')
            ETree.SubElement(cors_rule, 'AllowedOrigins').text = ",".join(rule.allowed_origins)
            ETree.SubElement(cors_rule, 'AllowedMethods').text = ",".join(rule.allowed_methods)
            ETree.SubElement(cors_rule, 'MaxAgeInSeconds').text = str(rule.max_age_in_seconds)
            ETree.SubElement(cors_rule, 'ExposedHeaders').text = ",".join(rule.exposed_headers)
            ETree.SubElement(cors_rule, 'AllowedHeaders').text = ",".join(rule.allowed_headers)

    # Target version
    if target_version:
        ETree.SubElement(service_properties_element, 'DefaultServiceVersion').text = target_version

    # DeleteRetentionPolicy
    if delete_retention_policy:
        policy_element = ETree.SubElement(service_properties_element, 'DeleteRetentionPolicy')
        ETree.SubElement(policy_element, 'Enabled').text = str(delete_retention_policy.enabled)

        if delete_retention_policy.enabled:
            ETree.SubElement(policy_element, 'Days').text = str(delete_retention_policy.days)

    # StaticWebsite
    if static_website:
        static_website_element = ETree.SubElement(service_properties_element, 'StaticWebsite')
        ETree.SubElement(static_website_element, 'Enabled').text = str(static_website.enabled)

        if static_website.enabled:

            if static_website.index_document is not None:
                ETree.SubElement(static_website_element, 'IndexDocument').text = str(static_website.index_document)

            if static_website.error_document_404_path is not None:
                ETree.SubElement(static_website_element, 'ErrorDocument404Path').text = \
                    str(static_website.error_document_404_path)

    # Add xml declaration and serialize
    try:
        stream = BytesIO()
        ETree.ElementTree(service_properties_element).write(stream, xml_declaration=True, encoding='utf-8',
                                                            method='xml')
    except:
        raise
    finally:
        output = stream.getvalue()
        stream.close()

    return output


def _convert_metrics_to_xml(metrics, root):
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
    ETree.SubElement(root, 'Version').text = metrics.version

    # Enabled
    ETree.SubElement(root, 'Enabled').text = str(metrics.enabled)

    # IncludeAPIs
    if metrics.enabled and metrics.include_apis is not None:
        ETree.SubElement(root, 'IncludeAPIs').text = str(metrics.include_apis)

    # RetentionPolicy
    retention_element = ETree.SubElement(root, 'RetentionPolicy')
    _convert_retention_policy_to_xml(metrics.retention_policy, retention_element)


def _convert_retention_policy_to_xml(retention_policy, root):
    '''
    <Enabled>true|false</Enabled>
    <Days>number-of-days</Days>
    '''
    # Enabled
    ETree.SubElement(root, 'Enabled').text = str(retention_policy.enabled)

    # Days
    if retention_policy.enabled and retention_policy.days:
        ETree.SubElement(root, 'Days').text = str(retention_policy.days)


def _len_plus(data):
    length = None
    # Check if object implements the __len__ method, covers most input cases such as bytearray.
    try:
        length = len(data)
    except:
        pass

    if not length:
        # Check if the stream is a file-like stream object.
        # If so, calculate the size using the file descriptor.
        try:
            fileno = data.fileno()
        except (AttributeError, UnsupportedOperation):
            pass
        else:
            return fstat(fileno).st_size

        # If the stream is seekable and tell() is implemented, calculate the stream size.
        try:
            current_position = data.tell()
            data.seek(0, SEEK_END)
            length = data.tell() - current_position
            data.seek(current_position, SEEK_SET)
        except (AttributeError, UnsupportedOperation):
            pass

    return length
