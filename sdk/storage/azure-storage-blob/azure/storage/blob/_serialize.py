# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

from azure.core import MatchConditions

from ._models import ContainerEncryptionScope
from ._generated.models import (
    ModifiedAccessConditions,
    SourceModifiedAccessConditions,
    CpkScopeInfo,
    ContainerCpkScopeInfo
)


_SUPPORTED_API_VERSIONS = [
    '2019-02-02',
    '2019-07-07'
]


def _get_match_headers(kwargs, match_param, etag_param):
    # type: (str) -> Tuple(Dict[str, Any], Optional[str], Optional[str])
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
        if etag_param in kwargs:
            raise ValueError("'{}' specified without '{}'.".format(etag_param, match_param))
    else:
        raise TypeError("Invalid match condition: {}".format(match_condition))
    return if_match, if_none_match


def get_modify_conditions(kwargs):
    # type: (Dict[str, Any]) -> ModifiedAccessConditions
    if_match, if_none_match = _get_match_headers(kwargs, 'match_condition', 'etag')
    return ModifiedAccessConditions(
        if_modified_since=kwargs.pop('if_modified_since', None),
        if_unmodified_since=kwargs.pop('if_unmodified_since', None),
        if_match=if_match or kwargs.pop('if_match', None),
        if_none_match=if_none_match or kwargs.pop('if_none_match', None)
    )


def get_source_conditions(kwargs):
    # type: (Dict[str, Any]) -> SourceModifiedAccessConditions
    if_match, if_none_match = _get_match_headers(kwargs, 'source_match_condition', 'source_etag')
    return SourceModifiedAccessConditions(
        source_if_modified_since=kwargs.pop('source_if_modified_since', None),
        source_if_unmodified_since=kwargs.pop('source_if_unmodified_since', None),
        source_if_match=if_match or kwargs.pop('source_if_match', None),
        source_if_none_match=if_none_match or kwargs.pop('source_if_none_match', None)
    )


def get_cpk_scope_info(kwargs):
    # type: (Dict[str, Any]) -> CpkScopeInfo
    if 'encryption_scope' in kwargs:
        return CpkScopeInfo(encryption_scope=kwargs.pop('encryption_scope'))
    return None


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
    return None


def get_api_version(kwargs, default):
    # type: (Dict[str, Any]) -> str
    api_version = kwargs.pop('api_version', None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = '\n'.join(_SUPPORTED_API_VERSIONS)
        raise ValueError("Unsupported API version '{}'. Please select from:\n{}".format(api_version, versions))
    return api_version or default
