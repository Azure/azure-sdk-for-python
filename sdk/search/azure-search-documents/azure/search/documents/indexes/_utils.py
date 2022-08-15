# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import TYPE_CHECKING
import six
from azure.core import MatchConditions
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceNotModifiedError,
)

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Optional


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


def get_access_conditions(model, match_condition=MatchConditions.Unconditionally):
    # type: (Any, MatchConditions) -> Tuple[Dict[int, Any], Dict[str, bool]]
    error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError}

    if isinstance(model, six.string_types):
        if match_condition is not MatchConditions.Unconditionally:
            raise ValueError("A model must be passed to use access conditions")
        return (error_map, {})

    try:
        if_match = prep_if_match(model.e_tag, match_condition)
        if_none_match = prep_if_none_match(model.e_tag, match_condition)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[304] = ResourceNotModifiedError
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        return (error_map, dict(if_match=if_match, if_none_match=if_none_match))
    except AttributeError:
        raise ValueError("Unable to get e_tag from the model")


def normalize_endpoint(endpoint):
    try:
        if not endpoint.lower().startswith("http"):
            endpoint = "https://" + endpoint
        elif not endpoint.lower().startswith("https"):
            raise ValueError(
                "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
            )
        return endpoint
    except AttributeError:
        raise ValueError("Endpoint must be a string.")
