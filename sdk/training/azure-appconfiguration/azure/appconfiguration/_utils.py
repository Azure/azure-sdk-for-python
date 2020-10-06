from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceNotModifiedError
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

def parse_connection_string(connection_string):
    segments = connection_string.split(";")
    if len(segments) != 3:
        raise ValueError("Invalid connection string.")

    endpoint = ""
    id_ = ""
    secret = ""
    for segment in segments:
        segment = segment.strip()
        if segment.startswith("Endpoint"):
            endpoint = str(segment[17:])
        elif segment.startswith("Id"):
            id_ = str(segment[3:])
        elif segment.startswith("Secret"):
            secret = str(segment[7:])
        else:
            raise ValueError("Invalid connection string.")

    if not endpoint or not id_ or not secret:
        raise ValueError("Invalid connection string.")

    return endpoint, id_, secret