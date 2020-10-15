# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from azure.core import MatchConditions


def get_match_headers(etag, match_condition):
    if_match = None  # Default to empty headers
    if_none_match = None

    if match_condition == MatchConditions.IfNotModified:
        if_match = etag
    elif match_condition == MatchConditions.IfPresent:
        if_match = "*"
    elif match_condition == MatchConditions.IfModified:
        if_none_match = etag
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = "*"
    return if_match, if_none_match
