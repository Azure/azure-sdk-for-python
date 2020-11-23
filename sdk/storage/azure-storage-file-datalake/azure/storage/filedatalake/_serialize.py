# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.storage.blob._serialize import _get_match_headers  # pylint: disable=protected-access
from ._shared import encode_base64
from ._generated.models import ModifiedAccessConditions, PathHTTPHeaders, \
    SourceModifiedAccessConditions, LeaseAccessConditions


def convert_dfs_url_to_blob_url(dfs_account_url):
    return dfs_account_url.replace('.dfs.', '.blob.', 1)


def convert_datetime_to_rfc1123(date):
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][date.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, date.day, month,
                                                    date.year, date.hour, date.minute, date.second)


def add_metadata_headers(metadata=None):
    # type: (Optional[Dict[str, str]]) -> str
    headers = list()
    if metadata:
        for key, value in metadata.items():
            headers.append(key + '=')
            headers.append(encode_base64(value))
            headers.append(',')

    if headers:
        del headers[-1]

    return ''.join(headers)


def get_mod_conditions(kwargs):
    # type: (Dict[str, Any]) -> ModifiedAccessConditions
    if_match, if_none_match = _get_match_headers(kwargs, 'match_condition', 'etag')
    return ModifiedAccessConditions(
        if_modified_since=kwargs.pop('if_modified_since', None),
        if_unmodified_since=kwargs.pop('if_unmodified_since', None),
        if_match=if_match or kwargs.pop('if_match', None),
        if_none_match=if_none_match or kwargs.pop('if_none_match', None)
    )


def get_source_mod_conditions(kwargs):
    # type: (Dict[str, Any]) -> SourceModifiedAccessConditions
    if_match, if_none_match = _get_match_headers(kwargs, 'source_match_condition', 'source_etag')
    return SourceModifiedAccessConditions(
        source_if_modified_since=kwargs.pop('source_if_modified_since', None),
        source_if_unmodified_since=kwargs.pop('source_if_unmodified_since', None),
        source_if_match=if_match or kwargs.pop('source_if_match', None),
        source_if_none_match=if_none_match or kwargs.pop('source_if_none_match', None)
    )


def get_path_http_headers(content_settings):
    path_headers = PathHTTPHeaders(
        cache_control=content_settings.cache_control,
        content_type=content_settings.content_type,
        content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
        content_encoding=content_settings.content_encoding,
        content_language=content_settings.content_language,
        content_disposition=content_settings.content_disposition
    )
    return path_headers


def get_access_conditions(lease):
    # type: (Optional[Union[BlobLeaseClient, str]]) -> Union[LeaseAccessConditions, None]
    try:
        lease_id = lease.id # type: ignore
    except AttributeError:
        lease_id = lease  # type: ignore
    return LeaseAccessConditions(lease_id=lease_id) if lease_id else None


def get_lease_id(lease):
    if not lease:
        return ""
    try:
        lease_id = lease.id
    except AttributeError:
        lease_id = lease
    return lease_id
