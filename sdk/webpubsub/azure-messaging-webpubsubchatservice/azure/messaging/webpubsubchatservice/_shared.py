# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
import re
from typing import Any, Awaitable, Optional, Union
from urllib.parse import urlsplit

import jwt
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy, ProxyPolicy
from azure.core.credentials import AzureKeyCredential


_DOT_PATH_SEGMENT = re.compile(r"/(?:\.|%(?:25)*2e){1,2}(?:/|$)", re.IGNORECASE)
_DOT_SEGMENT_VALUE = re.compile(r"(?:\.|%(?:25)*2e){1,2}", re.IGNORECASE)


def validate_path_segment_value(name: str, value: Any) -> None:
    for segment in str(value).split("/"):
        if _DOT_SEGMENT_VALUE.fullmatch(segment):
            raise ValueError(f"URL path parameter '{name}' must not be '.' or '..'.")


def validate_path_segments(url: str) -> None:
    path = urlsplit(url).path
    if path and _DOT_PATH_SEGMENT.search(path):
        raise ValueError("URL path segments must not be '.' or '..'.")


def wrap_serializer_url(serializer: Any) -> None:
    if getattr(serializer, "_validates_dot_path_segments", False):
        return
    original_url = serializer.url

    def _validating_url(name: str, data: Any, data_type: str, **kwargs: Any) -> str:
        output = original_url(name, data, data_type, **kwargs)
        if kwargs.get("skip_quote") is not True and data is not None:
            validate_path_segment_value(name, data)
        return output

    serializer.url = _validating_url
    serializer._validates_dot_path_segments = True  # pylint: disable=protected-access


def add_path_validation_policy(kwargs: Any) -> None:
    existing = kwargs.get("per_call_policies")
    policy = PathSegmentValidationPolicy()
    if existing is None:
        kwargs["per_call_policies"] = [policy]
    elif isinstance(existing, (list, tuple, set)):
        kwargs["per_call_policies"] = [policy, *existing]
    else:
        kwargs["per_call_policies"] = [policy, existing]




class PathSegmentValidationPolicy(SansIOHTTPPolicy):
    """Pipeline policy that rejects '.' and '..' URL path segments before sending a request."""

    def on_request(self, request: PipelineRequest) -> Union[None, Awaitable[None]]:
        validate_path_segments(request.http_request.url)
        return super(PathSegmentValidationPolicy, self).on_request(request)



def _parse_connection_string(connection_string: str, **kwargs: Any) -> Any:
    for segment in connection_string.split(";"):
        if "=" in segment:
            key, value = segment.split("=", 1)
            key = key.lower()
            if key not in ("version",):
                kwargs.setdefault(key, value)
        elif segment:
            raise ValueError("Malformed connection string - expected 'key=value'")
    if "endpoint" not in kwargs:
        raise ValueError("connection_string missing 'endpoint' field")
    if "accesskey" not in kwargs:
        raise ValueError("connection_string missing 'accesskey' field")
    return kwargs


class JwtCredentialPolicy(SansIOHTTPPolicy):
    def __init__(
        self,
        credential: AzureKeyCredential,
        *,
        origin_endpoint: Optional[str] = None,
        reverse_proxy_endpoint: Optional[str] = None,
    ) -> None:
        """Create a new instance of the policy associated with the given credential.

        :param credential: The azure.core.credentials.AzureKeyCredential instance to use
        :type credential: ~azure.core.credentials.AzureKeyCredential
        """
        self._credential = credential
        self._original_url = origin_endpoint
        self._reverse_proxy_endpoint = reverse_proxy_endpoint

    def on_request(self, request: PipelineRequest) -> Union[None, Awaitable[None]]:
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: An awaitable or None.
        :rtype: ~typing.Awaitable[None] or None
        """
        url = request.http_request.url
        if self._reverse_proxy_endpoint:
            url = url.replace(self._reverse_proxy_endpoint, self._original_url, 1)
        request.http_request.headers["Authorization"] = "Bearer " + self._encode(url)
        return super(JwtCredentialPolicy, self).on_request(request)

    def _encode(self, url: str) -> str:
        data = {
            "aud": url,
            "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=60),
        }
        encoded = jwt.encode(
            payload=data,
            key=self._credential.key,
            algorithm="HS256",
        )
        return encoded


class ApiManagementProxy(ProxyPolicy):
    def __init__(self, **kwargs: Any) -> None:
        """Create a new instance of the policy.

        :param endpoint: endpoint to be replaced
        :type endpoint: str
        :param proxy_endpoint: proxy endpoint
        :type proxy_endpoint: str
        """
        super(ApiManagementProxy, self).__init__(**kwargs)
        self._endpoint = kwargs.pop("origin_endpoint", None)
        self._reverse_proxy_endpoint = kwargs.pop("reverse_proxy_endpoint", None)

    def on_request(self, request: PipelineRequest) -> None:
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        super(ApiManagementProxy, self).on_request(request)
        if self._endpoint and self._reverse_proxy_endpoint:
            request.http_request.url = request.http_request.url.replace(self._endpoint, self._reverse_proxy_endpoint)


def get_token_by_key(
    endpoint: str,
    path: str,
    hub: str,
    key: str,
    *,
    user_id: Optional[str] = None,
    minutes_to_expire: int = 60,
    roles: Optional[list[str]] = None,
    groups: Optional[list[str]] = None,
) -> str:
    """Build token with access key.

    :param endpoint: HTTPS endpoint for the WebPubSub service instance.
    :type endpoint: str
    :param path: HTTPS path for the WebPubSub service instance.
    :type path: str
    :param hub: The hub to give access to.
    :type hub: str
    :param key: The access key
    :type key: str
    :keyword user_id: User ID for the client connection.
    :paramtype user_id: str
    :keyword minutes_to_expire: Token lifetime in minutes. Defaults to 60.
    :paramtype minutes_to_expire: int
    :keyword roles: Roles granted to the client connection.
    :paramtype roles: list[str]
    :keyword groups: Groups the client connection will join.
    :paramtype groups: list[str]
    :returns: token
    :rtype: str
    """
    if minutes_to_expire < 1:
        raise ValueError("minutes_to_expire must be at least 1")

    audience = endpoint + path + hub
    ttl = timedelta(minutes=minutes_to_expire)

    payload = {
        "aud": audience,
        "iat": datetime.now(tz=timezone.utc),
        "exp": datetime.now(tz=timezone.utc) + ttl,
    }
    if user_id:
        payload["sub"] = user_id
    if roles:
        payload["role"] = roles
    if groups:
        payload["webpubsub.group"] = groups
    encoded = jwt.encode(payload, key, algorithm="HS256")
    return encoded
