# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, cast, Dict, Optional, Tuple, Union, TYPE_CHECKING

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote  # type: ignore

from azure.core import MatchConditions

from ._generated.models import (
    ArrowConfiguration,
    BlobTag,
    BlobTags,
    DelimitedTextConfiguration,
    JsonTextConfiguration,
    QueryFormat,
    QueryFormatType,
    QuerySerialization,
)
from ._models import ContainerEncryptionScope, DelimitedJsonDialect

if TYPE_CHECKING:
    from ._lease import BlobLeaseClient


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
    '2020-12-06',
    '2021-02-12',
    '2021-04-10',
    '2021-06-08',
    '2021-08-06',
    '2021-12-02',
    '2022-11-02',
    '2023-01-03',
    '2023-05-03',
    '2023-08-03',
    '2023-11-03',
    '2024-05-04',
    '2024-08-04',
    '2024-11-04',
    '2025-01-05',
    '2025-05-05',
    '2025-07-05',
    '2025-11-05',
    '2026-02-06',
    '2026-04-06',
    '2026-06-06',
]


def _get_match_headers(
    kwargs: Dict[str, Any],
    match_param: str,
    etag_param: str
) -> Tuple[Optional[str], Optional[Any]]:
    if_match = None
    if_none_match = None
    match_condition = kwargs.pop(match_param, None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop(etag_param, None)
        if not if_match:
            raise ValueError(f"'{match_param}' specified without '{etag_param}'.")
    elif match_condition == MatchConditions.IfPresent:
        if_match = '*'
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop(etag_param, None)
        if not if_none_match:
            raise ValueError(f"'{match_param}' specified without '{etag_param}'.")
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = '*'
    elif match_condition is None:
        if kwargs.get(etag_param):
            raise ValueError(f"'{etag_param}' specified without '{match_param}'.")
    else:
        raise TypeError(f"Invalid match condition: {match_condition}")
    return if_match, if_none_match


def get_access_conditions(lease: Optional[Union["BlobLeaseClient", str]]) -> Dict[str, Any]:
    try:
        lease_id = lease.id # type: ignore
    except AttributeError:
        lease_id = lease # type: ignore
    if lease_id:
        return {"lease_id": lease_id}
    return {}


def _pop_etag_match_condition(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Pop etag/match_condition from kwargs, converting legacy if_match/if_none_match.

    Returns a dict with 'etag' and/or 'match_condition' if set.
    Raises ValueError if etag is provided without match_condition.
    """
    result: Dict[str, Any] = {}
    match_condition = kwargs.pop('match_condition', None)
    etag = kwargs.pop('etag', None)
    if_match = kwargs.pop('if_match', None)
    if_none_match = kwargs.pop('if_none_match', None)

    # Convert legacy if_match/if_none_match to etag/match_condition if not already set
    if match_condition is None and etag is None:
        if if_match == '*':
            match_condition = MatchConditions.IfPresent
        elif if_match is not None:
            etag = if_match
            match_condition = MatchConditions.IfNotModified
        elif if_none_match == '*':
            match_condition = MatchConditions.IfMissing
        elif if_none_match is not None:
            etag = if_none_match
            match_condition = MatchConditions.IfModified

    # Validate: etag without match_condition is ambiguous
    if etag is not None and match_condition is None:
        raise ValueError("'etag' specified without 'match_condition'.")
    # Validate: match_condition that requires an etag value
    if match_condition in (MatchConditions.IfNotModified, MatchConditions.IfModified) and etag is None:
        raise ValueError("'match_condition' specified without 'etag'.")

    if etag is not None:
        result['etag'] = etag
    if match_condition is not None:
        result['match_condition'] = match_condition
    return result


def get_modify_conditions(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract modify conditions from kwargs.

    Converts user-facing etag/match_condition (and legacy if_match/if_none_match)
    into the etag/match_condition format expected by the generated operations.
    """
    result = _pop_etag_match_condition(kwargs)
    val = kwargs.pop('if_modified_since', None)
    if val is not None:
        result['if_modified_since'] = val
    val = kwargs.pop('if_unmodified_since', None)
    if val is not None:
        result['if_unmodified_since'] = val
    val = kwargs.pop('if_tags_match_condition', None)
    if val is not None:
        result['if_tags'] = val
    return result


def get_blob_modify_conditions(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract blob modify conditions from kwargs (no if_tags).

    Uses if_match/if_none_match (not etag/match_condition) because the generated
    operations that use BlobModifiedAccessConditions (set_tags, get_tags) accept
    if_match/if_none_match directly.
    """
    if_match, if_none_match = _get_match_headers(kwargs, 'match_condition', 'etag')
    result: Dict[str, Any] = {}
    val = kwargs.pop('if_modified_since', None)
    if val is not None:
        result['if_modified_since'] = val
    val = kwargs.pop('if_unmodified_since', None)
    if val is not None:
        result['if_unmodified_since'] = val
    val = if_match or kwargs.pop('if_match', None)
    if val is not None:
        result['if_match'] = val
    val = if_none_match or kwargs.pop('if_none_match', None)
    if val is not None:
        result['if_none_match'] = val
    return result


def get_source_conditions(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    if_match, if_none_match = _get_match_headers(kwargs, 'source_match_condition', 'source_etag')
    result: Dict[str, Any] = {}
    val = kwargs.pop('source_if_modified_since', None)
    if val is not None:
        result['source_if_modified_since'] = val
    val = kwargs.pop('source_if_unmodified_since', None)
    if val is not None:
        result['source_if_unmodified_since'] = val
    val = if_match or kwargs.pop('source_if_match', None)
    if val is not None:
        result['source_if_match'] = val
    val = if_none_match or kwargs.pop('source_if_none_match', None)
    if val is not None:
        result['source_if_none_match'] = val
    val = kwargs.pop('source_if_tags_match_condition', None)
    if val is not None:
        result['source_if_tags'] = val
    return result


def get_cpk_scope_info(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    if 'encryption_scope' in kwargs:
        return {"encryption_scope": kwargs.pop('encryption_scope')}
    return {}


def get_container_cpk_scope_info(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    encryption_scope = kwargs.pop('container_encryption_scope', None)
    if encryption_scope:
        if isinstance(encryption_scope, ContainerEncryptionScope):
            return {
                "default_encryption_scope": encryption_scope.default_encryption_scope,
                "prevent_encryption_scope_override": encryption_scope.prevent_encryption_scope_override
            }
        if isinstance(encryption_scope, dict):
            result: Dict[str, Any] = {
                "default_encryption_scope": encryption_scope['default_encryption_scope'],
            }
            val = encryption_scope.get('prevent_encryption_scope_override')
            if val is not None:
                result["prevent_encryption_scope_override"] = val
            return result
        raise TypeError("Container encryption scope must be dict or type ContainerEncryptionScope.")
    return {}


def get_api_version(kwargs: Dict[str, Any]) -> str:
    api_version = kwargs.get('api_version', None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = '\n'.join(_SUPPORTED_API_VERSIONS)
        raise ValueError(f"Unsupported API version '{api_version}'. Please select from:\n{versions}")
    return api_version or _SUPPORTED_API_VERSIONS[-1]

def get_version_id(self_vid: Optional[str], kwargs: Dict[str, Any]) -> Optional[str]:
    if 'version_id' in kwargs:
        return cast(str, kwargs.pop('version_id'))
    return self_vid

def serialize_blob_tags_header(tags: Optional[Dict[str, str]] = None) -> Optional[str]:
    if tags is None:
        return None

    components = []
    if tags:
        for key, value in tags.items():
            components.append(quote(key, safe='.-'))
            components.append('=')
            components.append(quote(value, safe='.-'))
            components.append('&')

    if components:
        del components[-1]

    return ''.join(components)


def serialize_blob_tags(tags: Optional[Dict[str, str]] = None) -> BlobTags:
    tag_list = []
    if tags:
        tag_list = [BlobTag(key=k, value=v) for k, v in tags.items()]
    return BlobTags(blob_tag_set=tag_list)


def serialize_query_format(formater: Union[str, DelimitedJsonDialect]) -> Optional[QuerySerialization]:
    if formater == "ParquetDialect":
        qq_format = QueryFormat(
            type=QueryFormatType.PARQUET,
            parquet_text_configuration=' '  # type: ignore[call-overload]
        )
    elif isinstance(formater, DelimitedJsonDialect):
        json_serialization_settings = JsonTextConfiguration(record_separator=formater.delimiter)
        qq_format = QueryFormat(type=QueryFormatType.JSON, json_text_configuration=json_serialization_settings)
    elif hasattr(formater, 'quotechar'):  # This supports a csv.Dialect as well
        try:
            headers = formater.has_header  # type: ignore
        except AttributeError:
            headers = False
        if isinstance(formater, str):
            raise ValueError("Unknown string value provided. Accepted values: ParquetDialect")
        csv_serialization_settings = DelimitedTextConfiguration(
            column_separator=formater.delimiter,
            field_quote=formater.quotechar,
            record_separator=formater.lineterminator,
            escape_char=formater.escapechar,
            headers_present=headers
        )
        qq_format = QueryFormat(
            type=QueryFormatType.DELIMITED,
            delimited_text_configuration=csv_serialization_settings
        )
    elif isinstance(formater, list):
        arrow_serialization_settings = ArrowConfiguration(schema=formater)
        qq_format = QueryFormat(type=QueryFormatType.arrow, arrow_configuration=arrow_serialization_settings)
    elif not formater:
        return None
    else:
        raise TypeError("Format must be DelimitedTextDialect or DelimitedJsonDialect or ParquetDialect.")
    return QuerySerialization(format=qq_format)
