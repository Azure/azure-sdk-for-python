# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotModifiedError)


def prep_if_match(etag, match_condition):
    # type: (str, MatchConditions) -> Optional[str]
    error_map = {}
    if match_condition == MatchConditions.IfNotModified:
        if not etag:
            raise ValueError("The 'IfNotModified' match condition must be paired with an etag.")
        error_map[412] = ResourceModifiedError
        return etag, error_map
    if match_condition == MatchConditions.IfPresent:
        if etag:
            raise ValueError("An etag value cannot be paired with the 'IfPresent' match condition.")
        return "*", error_map
    if match_condition != MatchConditions.Unconditionally:
        raise ValueError("Unsupported match condition: {}".format(match_condition))
    return None, error_map

def prep_if_none_match(etag, match_condition):
    # type: (str, MatchConditions) -> Optional[str]
    error_map = {}
    if match_condition == MatchConditions.IfModified:
        error_map[412] = ResourceNotModifiedError
        if not etag:
            raise ValueError("The 'IfModified' match condition must be paired with an etag.")
        return etag, error_map
    if match_condition == MatchConditions.IfMissing:
        error_map[412] = ResourceExistsError
        if etag:
            raise ValueError("An etag value cannot be paired with the 'IfMissing' match condition.")
        return "*", error_map
    if match_condition != MatchConditions.Unconditionally:
        raise ValueError("Unsupported match condition: {}".format(match_condition))
    return None, error_map
