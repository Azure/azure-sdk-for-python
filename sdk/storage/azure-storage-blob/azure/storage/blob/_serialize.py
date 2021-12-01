# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use
from typing import Dict, Any, Optional, Union, Tuple

from . import BlobLeaseClient

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote  # type: ignore

from azure.core import MatchConditions

from ._models import (
    ContainerEncryptionScope,
    DelimitedJsonDialect)
from ._generated.models import (
    ModifiedAccessConditions,
    SourceModifiedAccessConditions,
    CpkScopeInfo,
    ContainerCpkScopeInfo,
    QueryFormat,
    QuerySerialization,
    DelimitedTextConfiguration,
    JsonTextConfiguration,
    ArrowConfiguration,
    QueryFormatType,
    BlobTag,
    BlobTags, LeaseAccessConditions
)


_SUPPORTED_API_VERSIONS = [
    '2019-02-02',
    '2019-07-07',
    '2019-10-10',
    '2019-12-12',
    '2020-02-10',
    '2020-04-08',
    '2020-06-12',
    '2020-08-04',
    '2020-10-02',
    '2020-12-06'
]


def _get_match_headers(kwargs, match_param, etag_param):
    # type: (Dict[str, Any], str, str) -> Tuple[Union[Optional[str], Any], Union[Optional[str], Any]]
    if_match = None
    if_none_match = None
    match_condition = kwargs.pop(match_param, None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop(etag_param, None)
        if not if_match:
            raise ValueError("'{}' specified without '{}'.".format(match_param, etag_param))
    elif match_condition == MatchConditions.IfPresent:
        if_match = '*'
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop(etag_param, None)
        if not if_none_match:
            raise ValueError("'{}' specified without '{}'.".format(match_param, etag_param))
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = '*'
    elif match_condition is None:
        if kwargs.get(etag_param):
            raise ValueError("'{}' specified without '{}'.".format(etag_param, match_param))
    else:
        raise TypeError("Invalid match condition: {}".format(match_condition))
    return if_match, if_none_match


def get_access_conditions(lease):
    # type: (Optional[Union[BlobLeaseClient, str]]) -> Union[LeaseAccessConditions, None]
    try:
        lease_id = lease.id # type: ignore
    except AttributeError:
        lease_id = lease # type: ignore
    return LeaseAccessConditions(lease_id=lease_id) if lease_id else None


def get_modify_conditions(kwargs):
    # type: (Dict[str, Any]) -> ModifiedAccessConditions
    if_match, if_none_match = _get_match_headers(kwargs, 'match_condition', 'etag')
    return ModifiedAccessConditions(
        if_modified_since=kwargs.pop('if_modified_since', None),
        if_unmodified_since=kwargs.pop('if_unmodified_since', None),
        if_match=if_match or kwargs.pop('if_match', None),
        if_none_match=if_none_match or kwargs.pop('if_none_match', None),
        if_tags=kwargs.pop('if_tags_match_condition', None)
    )


def get_source_conditions(kwargs):
    # type: (Dict[str, Any]) -> SourceModifiedAccessConditions
    if_match, if_none_match = _get_match_headers(kwargs, 'source_match_condition', 'source_etag')
    return SourceModifiedAccessConditions(
        source_if_modified_since=kwargs.pop('source_if_modified_since', None),
        source_if_unmodified_since=kwargs.pop('source_if_unmodified_since', None),
        source_if_match=if_match or kwargs.pop('source_if_match', None),
        source_if_none_match=if_none_match or kwargs.pop('source_if_none_match', None),
        source_if_tags=kwargs.pop('source_if_tags_match_condition', None)
    )


def get_cpk_scope_info(kwargs):
    # type: (Dict[str, Any]) -> CpkScopeInfo
    if 'encryption_scope' in kwargs:
        return CpkScopeInfo(encryption_scope=kwargs.pop('encryption_scope'))


def get_container_cpk_scope_info(kwargs):
    # type: (Dict[str, Any]) -> ContainerCpkScopeInfo
    encryption_scope = kwargs.pop('container_encryption_scope', None)
    if encryption_scope:
        if isinstance(encryption_scope, ContainerEncryptionScope):
            return ContainerCpkScopeInfo(
                default_encryption_scope=encryption_scope.default_encryption_scope,
                prevent_encryption_scope_override=encryption_scope.prevent_encryption_scope_override
            )
        if isinstance(encryption_scope, dict):
            return ContainerCpkScopeInfo(
                default_encryption_scope=encryption_scope['default_encryption_scope'],
                prevent_encryption_scope_override=encryption_scope.get('prevent_encryption_scope_override')
            )
        raise TypeError("Container encryption scope must be dict or type ContainerEncryptionScope.")


def get_api_version(kwargs):
    # type: (Dict[str, Any]) -> str
    api_version = kwargs.get('api_version', None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = '\n'.join(_SUPPORTED_API_VERSIONS)
        raise ValueError("Unsupported API version '{}'. Please select from:\n{}".format(api_version, versions))
    return api_version or _SUPPORTED_API_VERSIONS[-1]


def serialize_blob_tags_header(tags=None):
    # type: (Optional[Dict[str, str]]) -> str
    if tags is None:
        return None

    components = list()
    if tags:
        for key, value in tags.items():
            components.append(quote(key, safe='.-'))
            components.append('=')
            components.append(quote(value, safe='.-'))
            components.append('&')

    if components:
        del components[-1]

    return ''.join(components)


def serialize_blob_tags(tags=None):
    # type: (Optional[Dict[str, str]]) -> Union[BlobTags, None]
    tag_list = list()
    if tags:
        tag_list = [BlobTag(key=k, value=v) for k, v in tags.items()]
    return BlobTags(blob_tag_set=tag_list)


def serialize_query_format(formatter):
    if formatter == "ParquetDialect":
        qq_format = QueryFormat(
            type=QueryFormatType.PARQUET,
            parquet_text_configuration=' '
        )
    elif isinstance(formatter, DelimitedJsonDialect):
        serialization_settings = JsonTextConfiguration(
            record_separator=formatter.delimiter
        )
        qq_format = QueryFormat(
            type=QueryFormatType.json,
            json_text_configuration=serialization_settings)
    elif hasattr(formatter, 'quotechar'):  # This supports a csv.Dialect as well
        try:
            headers = formatter.has_header
        except AttributeError:
            headers = False
        serialization_settings = DelimitedTextConfiguration(
            column_separator=formatter.delimiter,
            field_quote=formatter.quotechar,
            record_separator=formatter.lineterminator,
            escape_char=formatter.escapechar,
            headers_present=headers
        )
        qq_format = QueryFormat(
            type=QueryFormatType.delimited,
            delimited_text_configuration=serialization_settings
        )
    elif isinstance(formatter, list):
        serialization_settings = ArrowConfiguration(
            schema=formatter
        )
        qq_format = QueryFormat(
            type=QueryFormatType.arrow,
            arrow_configuration=serialization_settings)
    elif not formatter:
        return None
    else:
        raise TypeError("Format must be DelimitedTextDialect or DelimitedJsonDialect or ParquetDialect.")
    return QuerySerialization(format=qq_format)
