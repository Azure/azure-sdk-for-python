# pylint: disable=line-too-long,useless-suppression
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


from collections.abc import MutableMapping
from typing import Any, TYPE_CHECKING, Union, Optional
import urllib.parse

from azure.core.credentials import AzureKeyCredential
from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from .._operations._operations import (
    build_web_pub_sub_service_list_connections_request,
)

from .._patch import _parse_connection_string, WebPubSubServiceClientBase
from ._client import WebPubSubServiceClient as WebPubSubServiceClientGenerated
from ..models import GroupMember

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class WebPubSubServiceClient(WebPubSubServiceClientBase, WebPubSubServiceClientGenerated):
    """WebPubSubServiceClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param hub: Target hub name, which should start with alphabetic characters and only contain
     alpha-numeric characters or underscore.
    :type hub: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, hub: str, credential: Union["AsyncTokenCredential", AzureKeyCredential], **kwargs: Any
    ) -> None:
        super().__init__(endpoint=endpoint, hub=hub, credential=credential, **kwargs)

    @distributed_trace
    def list_connections(
        self,
        *,
        group: str,
        top: Optional[int] = None,
        continuation_token_parameter: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[GroupMember]:
        """List connections in a group.

        List connections in a group.

        :keyword group: Target group name, whose length should be greater than 0 and less than 1025.
         Required.
        :paramtype group: str
        :keyword top: The maximum number of connections to return. If the value is not set, then all
         the connections in a group are returned. Default value is None.
        :paramtype top: int
        :keyword continuation_token_parameter: A token that allows the client to retrieve the next page
         of results. This parameter is provided by the service in the response of a previous request
         when there are additional results to be fetched. Clients should include the continuationToken
         in the next request to receive the subsequent page of data. If this parameter is omitted, the
         server will return the first page of results. Default value is None.
        :paramtype continuation_token_parameter: str
        :return: An iterator like instance of GroupMember object
        :rtype: ~azure.core.async_paging.AsyncItemPaged[GroupMember]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                connections = client.list_connections(
                    group="group_name",
                    top=100
                )

                async for member in connections:
                    assert member.connection_id is not None


        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        maxpagesize = kwargs.pop("maxpagesize", None)
        cls = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(next_link=None):
            if not next_link:

                _request = build_web_pub_sub_service_list_connections_request(
                    group=group,
                    hub=self._config.hub,
                    maxpagesize=maxpagesize,
                    top=top,
                    continuation_token_parameter=continuation_token_parameter,
                    api_version=self._config.api_version,
                    headers=_headers,
                    params=_params,
                )
                path_format_arguments = {
                    "endpoint": self._serialize.url(
                        "self._config.endpoint", self._config.endpoint, "str", skip_quote=True
                    ),
                }
                _request.url = self._client.format_url(_request.url, **path_format_arguments)

            else:
                # make call to next link with the client's api-version
                _parsed_next_link = urllib.parse.urlparse(next_link)
                _next_request_params = case_insensitive_dict(
                    {
                        key: [urllib.parse.quote(v) for v in value]
                        for key, value in urllib.parse.parse_qs(_parsed_next_link.query).items()
                    }
                )
                _next_request_params["api-version"] = self._config.api_version
                _request = HttpRequest(
                    "GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params
                )
                path_format_arguments = {
                    "endpoint": self._serialize.url(
                        "self._config.endpoint", self._config.endpoint, "str", skip_quote=True
                    ),
                }
                _request.url = self._client.format_url(_request.url, **path_format_arguments)

            return _request

        async def extract_data(pipeline_response):
            deserialized = pipeline_response.http_response.json()
            list_of_elem = deserialized.get("value", [])

            # Convert each dictionary item to a GroupMember object
            list_of_elem = [
                GroupMember(connection_id=item.get("connectionId"), user_id=item.get("userId")) for item in list_of_elem
            ]

            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return deserialized.get("nextLink") or None, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            _request = prepare_request(next_link)

            _stream = False
            pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
                _request, stream=_stream, **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return AsyncItemPaged(get_next, extract_data)

    @classmethod
    def from_connection_string(cls, connection_string: str, hub: str, **kwargs: Any) -> "WebPubSubServiceClient":
        """Create a new WebPubSubServiceClient from a connection string.

        :param connection_string: Connection string
        :type connection_string: ~str
        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :rtype: WebPubSubServiceClient
        """
        kwargs = _parse_connection_string(connection_string, **kwargs)

        credential = AzureKeyCredential(kwargs.pop("accesskey"))
        return cls(hub=hub, credential=credential, **kwargs)


__all__ = ["WebPubSubServiceClient", "GroupMember"]


def patch_sdk():
    pass
