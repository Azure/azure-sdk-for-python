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
import importlib

from ._version import VERSION
from ._web_pub_sub_service_client import WebPubSubServiceClient as GeneratedWebPubSubServiceClient

from msrest import Deserializer, Serializer
from azure.core.pipeline import policies
from azure.core import PipelineClient
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import SansIOHTTPPolicy, ProxyPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from msrest import Serializer


if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Optional, TypeVar, Union
    from ._operations._operations import JSONType

    T = TypeVar('T')
    ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

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


def _get_token_by_key(endpoint, hub, key, **kwargs):
    # type: (str, str, str, Any) -> str
    """build token with access key.

    :param endpoint:  HTTPS endpoint for the WebPubSub service instance.
    :type endpoint: str
    :param hub: The hub to give access to.
    :type hub: str
    :param key: The access key
    :type hub: str
    :keyword dict[str, any] jwt_headers: Any headers you want to pass to jwt encoding.
    :returns: token
    :rtype: str
    """
    audience = "{}/client/hubs/{}".format(endpoint, hub)
    user = kwargs.pop("user_id", None)
    ttl = timedelta(minutes=kwargs.pop("minutes_to_expire", 60))
    roles = kwargs.pop("roles", [])

    payload = {
        "aud": audience,
        "iat": datetime.now(tz=_UTC_TZ()),
        "exp": datetime.now(tz=_UTC_TZ()) + ttl,
    }
    if user:
        payload["sub"] = user
    if roles:
        payload["role"] = roles

    return six.ensure_str(jwt.encode(payload, key, algorithm="HS256", headers=kwargs.pop("jwt_headers", {})))


def _parse_connection_string(connection_string, **kwargs):
    # type: (str, Any) -> JSONType
    for segment in connection_string.split(";"):
        if "=" in segment:
            key, value = segment.split("=", 1)
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


class ApiManagementProxy(ProxyPolicy):

    def __init__(self, **kwargs):
        # type: (Any) -> None
        """Create a new instance of the policy.

        :param endpoint: endpoint to be replaced
        :type endpoint: str
        :param proxy_endpoint: proxy endpoint
        :type proxy_endpoint: str
        """
        super(ApiManagementProxy, self).__init__(**kwargs)
        self._endpoint = kwargs.pop('origin_endpoint', None)
        self._reverse_proxy_endpoint = kwargs.pop('reverse_proxy_endpoint', None)


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

    :param hub: Target hub name, which should start with alphabetic characters and only contain alpha-numeric characters or underscore.
    :type hub: str
    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: Union[~azure.core.credentials.TokenCredential, ~azure.core.credentials.AzureKeyCredential]
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this default value may result in unsupported behavior.
    """

    def __init__(
        self,
        hub,  # type: str
        endpoint,  # type: str
        credential,  # type: Union[TokenCredential, AzureKeyCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        super(WebPubSubServiceClientConfiguration, self).__init__(**kwargs)
        api_version = kwargs.pop('api_version', "2021-10-01")  # type: str

        if hub is None:
            raise ValueError("Parameter 'hub' must not be None.")
        if endpoint is None:
            raise ValueError("Parameter 'endpoint' must not be None.")
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")

        self.hub = hub
        self.endpoint = endpoint
        self.credential = credential
        self.api_version = api_version
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
        self.proxy_policy = kwargs.get('proxy_policy') or ApiManagementProxy(**kwargs)
        self.logging_policy = kwargs.get('logging_policy') or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.http_logging_policy = kwargs.get('http_logging_policy') or policies.HttpLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get('retry_policy') or policies.RetryPolicy(**kwargs)
        self.custom_hook_policy = kwargs.get('custom_hook_policy') or policies.CustomHookPolicy(**kwargs)
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
    :param hub: Target hub name, which should start with alphabetic characters and only contain
     alpha-numeric characters or underscore.
    :type hub: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint,  # type: str
        hub,  # type: str
        credential,  # type: Union[TokenCredential, AzureKeyCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        if kwargs.get("port") and endpoint:
            endpoint = endpoint.rstrip("/") + ":{}".format(kwargs.pop('port'))
        kwargs['origin_endpoint'] = endpoint
        _endpoint = '{Endpoint}'
        self._config = WebPubSubServiceClientConfiguration(hub=hub, endpoint=endpoint, credential=credential, **kwargs)
        self._client = PipelineClient(base_url=_endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

    @classmethod
    def from_connection_string(cls, connection_string, hub, **kwargs):
        # type: (Type[ClientType], str, str, Any) -> ClientType
        """Create a new WebPubSubServiceClient from a connection string.

        :param connection_string: Connection string
        :type connection_string: str
        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :rtype: WebPubSubServiceClient
        """
        kwargs = _parse_connection_string(connection_string, **kwargs)

        credential = AzureKeyCredential(kwargs.pop("accesskey"))
        return cls(hub=hub, credential=credential, **kwargs)

    @distributed_trace
    def get_client_access_token(self, **kwargs):
        # type: (Any) -> JSONType
        """Build an authentication token.

        :keyword user_id: User Id.
        :paramtype user_id: str
        :keyword roles: Roles that the connection with the generated token will have.
        :paramtype roles: list[str]
        :keyword minutes_to_expire: The expire time of the generated token.
        :paramtype minutes_to_expire: int
        :keyword dict[str, any] jwt_headers: Any headers you want to pass to jwt encoding.
        :returns: JSON response containing the web socket endpoint, the token and a url with the generated access token.
        :rtype: JSONType

        Example:
        >>> get_client_access_token()
        {
            'baseUrl': 'wss://contoso.com/api/webpubsub/client/hubs/theHub',
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ...',
            'url': 'wss://contoso.com/api/webpubsub/client/hubs/theHub?access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ...'
        }
        """
        endpoint = self._config.endpoint.lower()
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
        hub = self._config.hub
        client_url = "{}/client/hubs/{}".format(client_endpoint, hub)
        jwt_headers = kwargs.pop("jwt_headers", {})
        if isinstance(self._config.credential, AzureKeyCredential):
            token = _get_token_by_key(endpoint, hub, self._config.credential.key, jwt_headers=jwt_headers, **kwargs)
        else:
            token = super(WebPubSubServiceClient, self).get_client_access_token(**kwargs).get('token')

        return {
            "baseUrl": client_url,
            "token": token,
            "url": "{}?access_token={}".format(client_url, token),
        }
    get_client_access_token.metadata = {'url': '/api/hubs/{hub}/:generateToken'}  # type: ignore


def patch_sdk():
    curr_package = importlib.import_module("azure.messaging.webpubsubservice")
    curr_package.WebPubSubServiceClient = WebPubSubServiceClient
