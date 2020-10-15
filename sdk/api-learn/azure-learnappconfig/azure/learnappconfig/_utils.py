# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceNotModifiedError,
)

def get_match_headers(etag, match_condition):
    if_match = None  # Default to empty headers
    if_none_match = None
    errors = {}

    if match_condition == MatchConditions.IfNotModified:
        errors = {412: ResourceModifiedError}
        if_match = etag
    elif match_condition == MatchConditions.IfPresent:
        errors = {412: ResourceNotFoundError}
        if_match = "*"
    elif match_condition == MatchConditions.IfModified:
        errors = {304: ResourceNotModifiedError}
        if_none_match = etag
    elif match_condition == MatchConditions.IfMissing:
        errors = {412: ResourceExistsError}
        if_none_match = "*"
    return if_match, if_none_match, errors