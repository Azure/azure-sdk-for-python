# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Optional
from azure.core import MatchConditions


def quote_etag(etag: Optional[str]) -> Optional[str]:
    if not etag or etag == "*":
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'


def prep_if_match(etag: Optional[str], match_condition: MatchConditions) -> Optional[str]:
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None


def prep_if_none_match(etag: str, match_condition: MatchConditions) -> Optional[str]:
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None


def normalize_endpoint(endpoint):
    try:
        if not endpoint.lower().startswith("http"):
            endpoint = "https://" + endpoint
        elif not endpoint.lower().startswith("https"):
            raise ValueError("Bearer token authentication is not permitted for non-TLS protected (non-https) URLs.")
        return endpoint
    except AttributeError as ex:
        raise ValueError("Endpoint must be a string.") from ex
