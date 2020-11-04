# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.core import MatchConditions

def quote_etag(etag):
    if not etag or etag == "*":
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'

def prep_if_match(etag, match_condition):
    # type: (str, MatchConditions) -> Optional[str]
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None

def prep_if_none_match(etag, match_condition):
    # type: (str, MatchConditions) -> Optional[str]
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None
