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

from typing import TYPE_CHECKING
import importlib

from azure.core import AsyncPipelineClient
from msrest import Deserializer

from .._version import VERSION
from .._patch import JwtCredentialPolicy, ApiManagementProxy, _parse_connection_string
from ._web_pub_sub_service_client import WebPubSubServiceClient as GeneratedWebPubSubServiceClient
from ..operations._operations import build_send_to_all_request, build_send_to_connection_request, build_send_to_group_request


from azure.core.configuration import Configuration
from azure.core.pipeline import policies
from azure.core.credentials import AzureKeyCredential
from msrest import Serializer
from typing import Any, Callable, Dict, IO, List, Optional, TypeVar, Union

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async


T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Dict, TypeVar, Type
    ClientType = TypeVar("ClientType", bound="WebPubSubServiceClient")

    from azure.core.credentials_async import AsyncTokenCredential


class WebPubSubServiceClientConfiguration(Configuration):
    """Configuration for WebPubSubServiceClient.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: Union[~azure.core.credentials_async.AsyncTokenCredential, ~azure.core.credentials.AzureKeyCredential]
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union["AsyncTokenCredential", "AzureKeyCredential"],
        **kwargs: Any
    ) -> None:
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
        **kwargs: Any
    ) -> None:
        self.user_agent_policy = kwargs.get('user_agent_policy') or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get('headers_policy') or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get('proxy_policy') or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get('logging_policy') or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.http_logging_policy = kwargs.get('http_logging_policy') or policies.HttpLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get('retry_policy') or policies.AsyncRetryPolicy(**kwargs)
        self.custom_hook_policy = kwargs.get('custom_hook_policy') or ApiManagementProxy(**kwargs)
        self.redirect_policy = kwargs.get('redirect_policy') or policies.AsyncRedirectPolicy(**kwargs)
        self.authentication_policy = kwargs.get('authentication_policy')
        if self.credential and not self.authentication_policy:
            if isinstance(self.credential, AzureKeyCredential):
                self.authentication_policy = JwtCredentialPolicy(self.credential, kwargs.get('user'))
            else:
                self.authentication_policy = policies.AsyncBearerTokenCredentialPolicy(self.credential, *self.credential_scopes, **kwargs)


class WebPubSubServiceClient(GeneratedWebPubSubServiceClient):
    """WebPubSubServiceClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union["AsyncTokenCredential", "AzureKeyCredential"],
        **kwargs: Any
    ) -> None:
        kwargs['origin_endpoint'] = endpoint
        _endpoint = '{Endpoint}'
        self._config = WebPubSubServiceClientConfiguration(endpoint, credential, **kwargs)
        self._client = AsyncPipelineClient(base_url=_endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

    @classmethod
    def from_connection_string(cls, connection_string, **kwargs):
        # type: (Type[ClientType], str, Any) -> ClientType
        """Create a new WebPubSubServiceClient from a connection string.
        :param connection_string: Connection string
        :type connection_string: ~str
        :rtype: WebPubSubServiceClient
        """
        kwargs = _parse_connection_string(connection_string, **kwargs)

        credential = AzureKeyCredential(kwargs.pop("accesskey"))
        return cls(credential=credential, **kwargs)


    # could be removed after https://github.com/Azure/autorest.python/issues/1073 is fixed
    @distributed_trace_async
    async def send_to_all(
        self,
        hub: str,
        message: Union[IO, str],
        *,
        excluded: Optional[List[str]] = None,
        **kwargs: Any
    ) -> None:
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

        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})

    send_to_all.metadata = {'url': '/api/hubs/{hub}/:send'}  # type: ignore


    # could be removed after https://github.com/Azure/autorest.python/issues/1073 is fixed
    @distributed_trace_async
    async def send_to_connection(
        self,
        hub: str,
        connection_id: str,
        message: Union[IO, str],
        **kwargs: Any
    ) -> None:
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

        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})

    send_to_connection.metadata = {'url': '/api/hubs/{hub}/connections/{connectionId}/:send'}  # type: ignore


    # could be removed after https://github.com/Azure/autorest.python/issues/1073 is fixed
    @distributed_trace_async
    async def send_to_group(
        self,
        hub: str,
        group: str,
        message: Union[IO, str],
        *,
        excluded: Optional[List[str]] = None,
        **kwargs: Any
    ) -> None:
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

        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})

    send_to_group.metadata = {'url': '/api/hubs/{hub}/groups/{group}/:send'}  # type: ignore


def patch_sdk():
    curr_package = importlib.import_module("azure.messaging.webpubsubservice.aio")
    curr_package.WebPubSubServiceClient = WebPubSubServiceClient
    del curr_package.operations.WebPubSubServiceClientOperationsMixin.generate_client_token