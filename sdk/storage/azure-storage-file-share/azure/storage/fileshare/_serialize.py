# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

from azure.core import MatchConditions

from ._generated.models import SourceModifiedAccessConditions


def _get_match_headers(kwargs, match_param, etag_param):
    # type: (str) -> Tuple(Dict[str, Any], Optional[str], Optional[str])
    # TODO: extract this method to shared folder also add some comments, so that share, datalake and blob can use it.
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


def get_source_conditions(kwargs):
    # type: (Dict[str, Any]) -> SourceModifiedAccessConditions
    if_match, if_none_match = _get_match_headers(kwargs, 'source_match_condition', 'source_etag')
    return SourceModifiedAccessConditions(
        source_if_modified_since=kwargs.pop('source_if_modified_since', None),
        source_if_unmodified_since=kwargs.pop('source_if_unmodified_since', None),
        source_if_match=if_match or kwargs.pop('source_if_match', None),
        source_if_none_match=if_none_match or kwargs.pop('source_if_none_match', None)
    )


def validate_copy_mode(copy_mode, permission, permission_key):
    if copy_mode == "source":
        if permission or permission_key:
            raise ValueError("Copy mode should be 'override' if permission/permission_key is specified")
    elif copy_mode == "override":
        if not (permission or permission_key):
            raise ValueError("permission/permission_key should be specified with 'override' mode")
    elif not copy_mode:
        if permission_key or permission_key:
            raise ValueError("permission/permission_key shouldn't be specified without copy mode")
    else:
        raise ValueError("Invalid copy mode")
