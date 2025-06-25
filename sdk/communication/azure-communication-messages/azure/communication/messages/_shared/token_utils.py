# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import json
from datetime import datetime, timezone
from typing import Tuple, Any, List, Optional
from dateutil import parser as dateutil_parser  # type: ignore
from azure.core.exceptions import HttpResponseError

TEAMS_EXTENSION_SCOPE_PREFIX = "https://auth.msft.communication.azure.com/"
COMMUNICATION_CLIENTS_SCOPE_PREFIX = "https://communication.azure.com/clients/"
TEAMS_EXTENSION_ENDPOINT = "/access/teamsExtension/:exchangeAccessToken"
TEAMS_EXTENSION_API_VERSION = "2025-06-30"
COMMUNICATION_CLIENTS_ENDPOINT = "/access/entra/:exchangeAccessToken"
COMMUNICATION_CLIENTS_API_VERSION = "2025-03-02-preview"


def create_request_message(resource_endpoint: str, scopes: Optional[List[str]]) -> Any:
    from azure.core.pipeline.transport import HttpRequest
    request_uri = create_request_uri(resource_endpoint, scopes)
    request = HttpRequest("POST", request_uri)
    request.headers["Accept"] = "application/json"
    request.headers["Content-Type"] = "application/json"
    request.set_json_body({})
    return request


def create_request_uri(resource_endpoint: str, scopes: Optional[List[str]]) -> str:
    endpoint, api_version = determine_endpoint_and_api_version(scopes)
    base = resource_endpoint.rstrip("/")
    return f"{base}{endpoint}?api-version={api_version}"


def determine_endpoint_and_api_version(scopes: Optional[List[str]]) -> Tuple[str, str]:
    if not scopes or not isinstance(scopes, list):
        raise ValueError(
            "Scopes validation failed. Ensure all scopes start with either "
            f"{TEAMS_EXTENSION_SCOPE_PREFIX} or {COMMUNICATION_CLIENTS_SCOPE_PREFIX}."
        )
    if all(scope.startswith(TEAMS_EXTENSION_SCOPE_PREFIX) for scope in scopes):
        return TEAMS_EXTENSION_ENDPOINT, TEAMS_EXTENSION_API_VERSION
    if all(scope.startswith(COMMUNICATION_CLIENTS_SCOPE_PREFIX) for scope in scopes):
        return COMMUNICATION_CLIENTS_ENDPOINT, COMMUNICATION_CLIENTS_API_VERSION
    raise ValueError(
        "Scopes validation failed. Ensure all scopes start with either"
        f"{TEAMS_EXTENSION_SCOPE_PREFIX} or {COMMUNICATION_CLIENTS_SCOPE_PREFIX}."
    )


def parse_expires_on(expires_on, response):
    if isinstance(expires_on, str):
        try:
            expires_on_dt = dateutil_parser.parse(expires_on)
            expires_on_epoch = int(expires_on_dt.timestamp())
            return expires_on_epoch
        except Exception as exc:
            raise HttpResponseError(
                message="Unknown format for expires_on field in access token response",
                response=response.http_response) from exc
    else:
        raise HttpResponseError(
            message="Missing expires_on field in access token response",
            response=response.http_response)


def is_entra_token_cache_valid(entra_token_cache, request):
    current_entra_token = request.http_request.headers.get("Authorization", "")
    cache_valid = (
        entra_token_cache is not None and
        current_entra_token == entra_token_cache
    )
    return cache_valid, current_entra_token


def is_acs_token_cache_valid(response_cache):
    if (response_cache is None or response_cache.http_response is None or
            response_cache.http_response.status_code != 200):
        return False
    try:
        content = response_cache.http_response.text()
        data = json.loads(content)
        expires_on = data["accessToken"]["expiresOn"]
        expires_on_dt = dateutil_parser.parse(expires_on)
        return datetime.now(timezone.utc) < expires_on_dt
    except (KeyError, ValueError, json.JSONDecodeError):
        raise ValueError(  # pylint: disable=W0707
                "Invalid token response")
