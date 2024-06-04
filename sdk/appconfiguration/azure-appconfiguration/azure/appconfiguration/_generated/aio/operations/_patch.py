# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import urllib.parse
from typing import Any, AsyncIterable, List, Optional, Union
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict
from ._azure_app_configuration_operations import (
    AzureAppConfigurationOperationsMixin as AzureAppConfigOpGenerated,
    ClsType,
    build_get_key_values_request,
)
from ... import models as _models
from ..._vendor import _convert_request


class AzureAppConfigurationOperationsMixin(AzureAppConfigOpGenerated):
    @distributed_trace_async
    async def get_key_values_in_one_page(
        self,
        key: Optional[str] = None,
        label: Optional[str] = None,
        after: Optional[str] = None,
        accept_datetime: Optional[str] = None,
        select: Optional[List[Union[str, _models.KeyValueFields]]] = None,
        if_match: Optional[str] = None,
        if_none_match: Optional[str] = None,
        continuation_token: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterable["_models.KeyValue"]:
        """Gets a list of key-values in one page.

        Gets a list of key-values in one page.

        :param key: A filter used to match keys. Default value is None.
        :type key: str
        :param label: A filter used to match labels. Default value is None.
        :type label: str
        :param after: Instructs the server to return elements that appear after the element referred to
         by the specified token. Default value is None.
        :type after: str
        :param accept_datetime: Requests the server to respond with the state of the resource at the
         specified time. Default value is None.
        :type accept_datetime: str
        :param select: Used to select what fields are present in the returned resource(s). Default
         value is None.
        :type select: list[str or ~azure.appconfiguration.models.KeyValueFields]
        :param if_match: Used to perform an operation only if the targeted resource's etag matches the
         value provided. Default value is None.
        :type if_match: str
        :param if_none_match: Used to perform an operation only if the targeted resource's etag does
         not match the value provided. Default value is None.
        :type if_none_match: str
        :param str continuation_token: An opaque continuation token.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either KeyValue or the result of cls(response)
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.appconfiguration.models.KeyValue]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

        api_version: str = kwargs.pop("api_version", _params.pop("api-version", self._config.api_version))
        cls: ClsType[_models.KeyValueListResult] = kwargs.pop("cls", None)

        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(next_link=None):
            if not next_link:

                _request = build_get_key_values_request(
                    key=key,
                    label=label,
                    after=after,
                    accept_datetime=accept_datetime,
                    select=select,
                    if_match=if_match,
                    if_none_match=if_none_match,
                    sync_token=self._config.sync_token,
                    api_version=api_version,
                    headers=_headers,
                    params=_params,
                )
                _request = _convert_request(_request)
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
                _request = _convert_request(_request)
                path_format_arguments = {
                    "endpoint": self._serialize.url(
                        "self._config.endpoint", self._config.endpoint, "str", skip_quote=True
                    ),
                }
                _request.url = self._client.format_url(_request.url, **path_format_arguments)
                _request.method = "GET"
            return _request

        _request = prepare_request(continuation_token)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.Error, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        response_headers = response.headers
        deserialized = self._deserialize("KeyValueListResult", pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, response_headers)

        return deserialized


__all__: List[str] = [
    "AzureAppConfigurationOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
