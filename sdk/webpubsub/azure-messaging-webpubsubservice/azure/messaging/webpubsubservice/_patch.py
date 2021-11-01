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
from .operations._operations import build_send_to_all_request, build_send_to_connection_request, build_send_to_group_request, build_generate_client_token_request

from msrest import Deserializer, Serializer
from azure.core.pipeline import policies
from azure.core import PipelineClient
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import SansIOHTTPPolicy, CustomHookPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from msrest import Serializer


if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, IO, List, Optional, TypeVar, Union

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

    def _get_token_by_key(self, endpoint, hub, **kwargs):
        # type: (str, str, Any) -> str
        """build token with access key.

        :param endpoint:  HTTPS endpoint for the WebPubSub service instance.
        :type endpoint: str
        :param hub: The hub to give access to.
        :type hub: str
        :returns: token
        :rtype: str
        """
        audience = "{}/client/hubs/{}".format(endpoint, hub)
        user = kwargs.pop("user_id", None)
        key = self._config.credential.key
        ttl = timedelta(minutes=kwargs.pop("minutes_to_expire", 60))
        role = kwargs.pop("role", [])

        payload = {
            "aud": audience,
            "iat": datetime.now(tz=_UTC_TZ()),
            "exp": datetime.now(tz=_UTC_TZ()) + ttl,
        }
        if user:
            payload["sub"] = user
        if role:
            payload["role"] = role

        return six.ensure_str(jwt.encode(payload, key, algorithm="HS256"))

    def get_client_access_token(self, hub, **kwargs):
        # type: (str, Any) -> Dict[Any]
        """Build an authentication token.

        :keyword hub: The hub to give access to.
        :type hub: str
        :keyword user_id: User Id.
        :paramtype user_id: str
        :keyword role: Roles that the connection with the generated token will have.
        :paramtype role: list[str]
        :keyword minutes_to_expire: The expire time of the generated token.
        :paramtype minutes_to_expire: int
        :returns: ~dict containing the web socket endpoint, the token and a url with the generated access token.
        :rtype: ~dict

        Example:
        >>> get_client_access_token(hub='theHub')
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
        client_url = "{}/client/hubs/{}".format(client_endpoint, hub)
        if isinstance(self._config.credential, AzureKeyCredential):
            token = self._get_token_by_key(endpoint, hub, **kwargs)
        else:
            token = self._generate_client_token(hub, **kwargs).get('token')

        return {
            "baseUrl": client_url,
            "token": token,
            "url": "{}?access_token={}".format(client_url, token),
        }

    # could be removed after https://github.com/Azure/autorest.python/issues/1073 is fixed
    @distributed_trace
    def send_to_all(
        self,
        hub,  # type: str
        message,  # type: Union[IO, str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Broadcast content inside request body to all the connected client connections.

        Broadcast content inside request body to all the connected client connections.

        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :param message: The payload body.
        :type message: IO or str
        :keyword excluded: Excluded connection Ids.
        :paramtype excluded: list[str]
        :keyword str content_type: Media type of the body sent to the API. Default value is
         "application/json". Allowed values are: "application/json", "application/octet-stream",
         "text/plain."
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        content_type = kwargs.pop('content_type', "text/plain")  # type: Optional[str]
        excluded = kwargs.pop('excluded', None)  # type: Optional[List[str]]

        json = None
        content = None
        if content_type.split(";")[0] in ['text/plain', 'application/octet-stream']:
            content = message
        elif content_type.split(";")[0] in ['application/json']:
            json = message
        else:
            raise ValueError(
                "The content_type '{}' is not one of the allowed values: "
                "['application/json', 'application/octet-stream', 'text/plain']".format(content_type)
            )

        request = build_send_to_all_request(
            hub=hub,
            content_type=content_type,
            json=json,
            content=content,
            excluded=excluded,
            template_url=self.send_to_all.metadata['url'],
        )
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})

    send_to_all.metadata = {'url': '/api/hubs/{hub}/:send'}  # type: ignore

    # could be removed after https://github.com/Azure/autorest.python/issues/1073 is fixed
    @distributed_trace
    def send_to_connection(
        self,
        hub,  # type: str
        connection_id,  # type: str
        message,  # type: Union[IO, str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Send content inside request body to the specific connection.

        Send content inside request body to the specific connection.

        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :param connection_id: The connection Id.
        :type connection_id: str
        :param message: The payload body.
        :type message: IO or str
        :keyword str content_type: Media type of the body sent to the API. Default value is
         "application/json". Allowed values are: "application/json", "application/octet-stream",
         "text/plain."
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        content_type = kwargs.pop('content_type', "text/plain")  # type: Optional[str]

        json = None
        content = None
        if content_type.split(";")[0] in ['text/plain', 'application/octet-stream']:
            content = message
        elif content_type.split(";")[0] in ['application/json']:
            json = message
        else:
            raise ValueError(
                "The content_type '{}' is not one of the allowed values: "
                "['application/json', 'application/octet-stream', 'text/plain']".format(content_type)
            )

        request = build_send_to_connection_request(
            hub=hub,
            connection_id=connection_id,
            content_type=content_type,
            json=json,
            content=content,
            template_url=self.send_to_connection.metadata['url'],
        )
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})

    send_to_connection.metadata = {'url': '/api/hubs/{hub}/connections/{connectionId}/:send'}  # type: ignore


    # could be removed after https://github.com/Azure/autorest.python/issues/1073 is fixed
    @distributed_trace
    def send_to_group(
        self,
        hub,  # type: str
        group,  # type: str
        message,  # type: Union[IO, str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Send content inside request body to a group of connections.

        Send content inside request body to a group of connections.

        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :param group: Target group name, which length should be greater than 0 and less than 1025.
        :type group: str
        :param message: The payload body.
        :type message: IO or str
        :keyword excluded: Excluded connection Ids.
        :paramtype excluded: list[str]
        :keyword str content_type: Media type of the body sent to the API. Default value is
         "application/json". Allowed values are: "application/json", "application/octet-stream",
         "text/plain."
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        content_type = kwargs.pop('content_type', "text/plain")  # type: Optional[str]
        excluded = kwargs.pop('excluded', None)  # type: Optional[List[str]]

        json = None
        content = None
        if content_type.split(";")[0] in ['text/plain', 'application/octet-stream']:
            content = message
        elif content_type.split(";")[0] in ['application/json']:
            json = message
        else:
            raise ValueError(
                "The content_type '{}' is not one of the allowed values: "
                "['application/json', 'application/octet-stream', 'text/plain']".format(content_type)
            )

        request = build_send_to_group_request(
            hub=hub,
            group=group,
            content_type=content_type,
            json=json,
            content=content,
            excluded=excluded,
            template_url=self.send_to_group.metadata['url'],
        )
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})

    send_to_group.metadata = {'url': '/api/hubs/{hub}/groups/{group}/:send'}  # type: ignore

    @distributed_trace
    def _generate_client_token(
            self,
            hub,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> Any
        """Generate token for the client to connect Azure Web PubSub service.

        Generate token for the client to connect Azure Web PubSub service.

        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :keyword user_id: User Id.
        :paramtype user_id: str
        :keyword role: Roles that the connection with the generated token will have.
        :paramtype role: list[str]
        :keyword minutes_to_expire: The expire time of the generated token.
        :paramtype minutes_to_expire: int
        :return: JSON object
        :rtype: Any
        :raises: ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response.json() == {
                    "token": "str"  # Optional. The token value for the WebSocket client to connect to the service.
                }
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[Any]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        user_id = kwargs.pop('user_id', None)  # type: Optional[str]
        role = kwargs.pop('role', None)  # type: Optional[List[str]]
        minutes_to_expire = kwargs.pop('minutes_to_expire', 60)  # type: Optional[int]

        request = build_generate_client_token_request(
            hub=hub,
            user_id=user_id,
            role=role,
            minutes_to_expire=minutes_to_expire,
            template_url=self._generate_client_token.metadata['url'],
        )
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    _generate_client_token.metadata = {'url': '/api/hubs/{hub}/:generateToken'}  # type: ignore


def patch_sdk():
    curr_package = importlib.import_module("azure.messaging.webpubsubservice")
    curr_package.WebPubSubServiceClient = WebPubSubServiceClient
    del curr_package.operations.WebPubSubServiceClientOperationsMixin.generate_client_token
