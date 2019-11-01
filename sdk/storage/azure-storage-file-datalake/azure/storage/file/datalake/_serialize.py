# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.storage.blob._shared import encode_base64
from azure.storage.file.datalake._generated.models import ModifiedAccessConditions, PathHTTPHeaders, \
    SourceModifiedAccessConditions


def convert_dfs_url_to_blob_url(dfs_account_url):
    return dfs_account_url.replace('dfs.core.windows.net', 'blob.core.windows.net', 1)


def add_metadata_headers(metadata=None):
    # type: (Optional[Dict[str, str]]) -> str
    headers = list()
    if metadata:
        for key, value in metadata.items():
            headers.append(key + '=')
            headers.append(encode_base64(value))
            headers.append(',')

    if len(headers) is not 0:
        del headers[-1]

    return ''.join(headers)


def get_mod_conditions(kwargs):
    mod_conditions = ModifiedAccessConditions(
        if_modified_since=kwargs.pop('if_modified_since', None),
        if_unmodified_since=kwargs.pop('if_unmodified_since', None),
        if_match=kwargs.pop('if_match', None),
        if_none_match=kwargs.pop('if_none_match', None))
    return mod_conditions


def get_source_mod_conditions(kwargs):
    mod_conditions = SourceModifiedAccessConditions(
        source_if_modified_since=kwargs.pop('source_if_modified_since', None),
        source_if_unmodified_since=kwargs.pop('source_if_unmodified_since', None),
        source_if_match=kwargs.pop('source_if_match', None),
        source_if_none_match=kwargs.pop('source_if_none_match', None))
    return mod_conditions


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


def get_lease_id(lease):
    if not lease:
        return ""
    try:
        lease_id = lease.id
    except AttributeError:
        lease_id = lease
    return lease_id
