# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import typing
import jwt
import six
from datetime import datetime, timedelta, tzinfo
from typing import TYPE_CHECKING

from ._version import VERSION
from ._web_pub_sub_service_client import WebPubSubServiceClient as GeneratedWebPubSubServiceClient

from msrest import Deserializer, Serializer
from azure.core.pipeline import policies
from azure.core import PipelineClient
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import SansIOHTTPPolicy, CustomHookPolicy
from azure.core.credentials import AzureKeyCredential

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Type, TypeVar, Any, Union, Dict

    ClientType = TypeVar("ClientType", bound="WebPubSubServiceClient")

    from azure.core.credentials import TokenCredential
    from azure.core.pipeline import PipelineRequest


class _UTC_TZ(tzinfo):
    """from https://docs.python.org/2/library/datetime.html#tzinfo-objects"""

    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return self.__class__.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.__class__.ZERO


def _parse_connection_string(connection_string, **kwargs):
    # type: (str, Any) -> Dict[Any]
    for segment in connection_string.split(";"):
        if "=" in segment:
            key, value = segment.split("=", maxsplit=1)
            key = key.lower()
            if key not in ("version",):
                kwargs.setdefault(key, value)
        elif segment:
            raise ValueError(
                "Malformed connection string - expected 'key=value', found segment '{}' in '{}'".format(
                    segment, connection_string
                )
            )

    if "endpoint" not in kwargs:
        raise ValueError("connection_string missing 'endpoint' field")

    if "accesskey" not in kwargs:
        raise ValueError("connection_string missing 'accesskey' field")

    return kwargs


def build_authentication_token(endpoint, hub, **kwargs):
    # type: (str, str, Any) -> Dict[Any]
    """Build an authentication token for the given endpoint, hub using the provided key.

    :keyword endpoint: connetion string or HTTP or HTTPS endpoint for the WebPubSub service instance.
    :type endpoint: str
    :keyword hub: The hub to give access to.
    :type hub: str
    :keyword accesskey: Key to sign the token with. Required if endpoint is not a connection string
    :type accesskey: str
    :keyword ttl: Optional ttl timedelta for the token. Default is 1 hour.
    :type ttl: ~datetime.timedelta
    :keyword user: Optional user name (subject) for the token. Default is no user.
    :type user: str
    :keyword roles: Roles for the token.
    :type roles: typing.List[str]. Default is no roles.
    :returns: ~dict containing the web socket endpoint, the token and a url with the generated access token.
    :rtype: ~dict


    Example:
    >>> build_authentication_token(endpoint='https://contoso.com/api/webpubsub', hub='theHub', key='123')
    {
        'baseUrl': 'wss://contoso.com/api/webpubsub/client/hubs/theHub',
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ...',
        'url': 'wss://contoso.com/api/webpubsub/client/hubs/theHub?access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ...'
    }
    """
    if 'accesskey' not in kwargs:
        kwargs = _parse_connection_string(endpoint, **kwargs)
        endpoint = kwargs.pop('endpoint')

    user = kwargs.pop("user", None)
    key = kwargs.pop("accesskey")
    ttl = kwargs.pop("ttl", timedelta(hours=1))
    roles = kwargs.pop("roles", [])
    endpoint = endpoint.lower()
    if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
        raise ValueError(
            "Invalid endpoint: '{}' has unknown scheme - expected 'http://' or 'https://'".format(
                endpoint
            )
        )

    # Ensure endpoint has no trailing slash
    endpoint = endpoint.rstrip("/")

    # Switch from http(s) to ws(s) scheme
    client_endpoint = "ws" + endpoint[4:]
    client_url = "{}/client/hubs/{}".format(client_endpoint, hub)
    audience = "{}/client/hubs/{}".format(endpoint, hub)

    payload = {
        "aud": audience,
        "iat": datetime.now(tz=_UTC_TZ()),
        "exp": datetime.now(tz=_UTC_TZ()) + ttl,
    }
    if user:
        payload["sub"] = user
    if roles:
        payload["role"] = roles

    token = six.ensure_str(jwt.encode(payload, key, algorithm="HS256"))
    return {
        "baseUrl": client_url,
        "token": token,
        "url": "{}?access_token={}".format(client_url, token),
    }


class JwtCredentialPolicy(SansIOHTTPPolicy):

    NAME_CLAIM_TYPE = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"

    def __init__(self, credential, user=None):
        # type: (AzureKeyCredential, typing.Optional[str]) -> None
        """Create a new instance of the policy associated with the given credential.

        :param credential: The azure.core.credentials.AzureKeyCredential instance to use
        :type credential: ~azure.core.credentials.AzureKeyCredential
        :param user: Optional user name associated with the credential.
        :type user: str
        """
        self._credential = credential
        self._user = user

    def on_request(self, request):
        # type: (PipelineRequest) -> typing.Union[None, typing.Awaitable[None]]
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        request.http_request.headers["Authorization"] = "Bearer " + self._encode(
            request.http_request.url
        )
        return super(JwtCredentialPolicy, self).on_request(request)

    def _encode(self, url):
        # type: (AzureKeyCredential) -> str
        data = {
            "aud": url,
            "exp": datetime.now(tz=_UTC_TZ()) + timedelta(seconds=60),
        }
        if self._user:
            data[self.NAME_CLAIM_TYPE] = self._user

        encoded = jwt.encode(
            payload=data,
            key=self._credential.key,
            algorithm="HS256",
        )
        return six.ensure_str(encoded)


class ApiManagementProxy(CustomHookPolicy):

    def __init__(self, **kwargs):
        # type: (typing.Optional[str], typing.Optional[str]) -> None
        """Create a new instance of the policy.

        :param endpoint: endpoint to be replaced
        :type endpoint: str
        :param proxy_endpoint: proxy endpoint
        :type proxy_endpoint: str
        """
        self._endpoint = kwargs.pop('origin_endpoint', None)
        self._reverse_proxy_endpoint = kwargs.pop('reverse_proxy_endpoint', None)
        super(ApiManagementProxy, self).__init__(**kwargs)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        super(ApiManagementProxy, self).on_request(request)
        if self._endpoint and self._reverse_proxy_endpoint:
            request.http_request.url = request.http_request.url.replace(self._endpoint, self._reverse_proxy_endpoint)


class WebPubSubServiceClientConfiguration(Configuration):
    """Configuration for WebPubSubServiceClient.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: Union[~azure.core.credentials.TokenCredential, ~azure.core.credentials.AzureKeyCredential]
    """

    def __init__(
        self,
        endpoint,  # type: str
        credential,  # type: Union[TokenCredential, AzureKeyCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        if endpoint is None:
            raise ValueError("Parameter 'endpoint' must not be None.")
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        super(WebPubSubServiceClientConfiguration, self).__init__(**kwargs)

        self.endpoint = endpoint
        self.credential = credential
        self.credential_scopes = kwargs.pop('credential_scopes', ['https://webpubsub.azure.com/.default'])
        kwargs.setdefault('sdk_moniker', 'messaging-webpubsubservice/{}'.format(VERSION))
        self._configure(**kwargs)

    def _configure(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self.user_agent_policy = kwargs.get('user_agent_policy') or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get('headers_policy') or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get('proxy_policy') or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get('logging_policy') or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.http_logging_policy = kwargs.get('http_logging_policy') or policies.HttpLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get('retry_policy') or policies.RetryPolicy(**kwargs)
        self.custom_hook_policy = kwargs.get('custom_hook_policy') or ApiManagementProxy(**kwargs)
        self.redirect_policy = kwargs.get('redirect_policy') or policies.RedirectPolicy(**kwargs)
        self.authentication_policy = kwargs.get('authentication_policy')
        if self.credential and not self.authentication_policy:
            if isinstance(self.credential, AzureKeyCredential):
                self.authentication_policy = JwtCredentialPolicy(self.credential, kwargs.get('user'))
            else:
                self.authentication_policy = policies.BearerTokenCredentialPolicy(self.credential, *self.credential_scopes, **kwargs)


class WebPubSubServiceClient(GeneratedWebPubSubServiceClient):
    """WebPubSubServiceClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(
        self,
        endpoint,  # type: str
        credential,  # type: Union[TokenCredential, AzureKeyCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs['origin_endpoint'] = endpoint
        _endpoint = '{Endpoint}'
        self._config = WebPubSubServiceClientConfiguration(endpoint, credential, **kwargs)
        self._client = PipelineClient(base_url=_endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

    @classmethod
    def from_connection_string(cls, connection_string, **kwargs):
        # type: (Type[ClientType], str, Any) -> ClientType
        """Create a new WebPubSubServiceClient from a connection string.

        :param connection_string: Connection string
        :type connection_string: str
        :rtype: WebPubSubServiceClient
        """
        kwargs = _parse_connection_string(connection_string, **kwargs)

        credential = AzureKeyCredential(kwargs.pop("accesskey"))
        return cls(credential=credential, **kwargs)


def patch_sdk():
    pass
