# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Iterable, List, Optional, Union
import urllib.parse

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ._azure_app_configuration_operations import (
    AzureAppConfigurationOperationsMixin as GeneratedAzureAppConfigOps,
    build_get_key_values_request,
    ClsType,
    _SERIALIZER,
)
from .. import models as _models
from .._vendor import _convert_request


class AzureAppConfigurationOperationsMixin(GeneratedAzureAppConfigOps):  # pylint: disable=too-many-public-methods
    @distributed_trace
    def get_key_values(
        self,
        key: Optional[str] = None,
        label: Optional[str] = None,
        after: Optional[str] = None,
        accept_datetime: Optional[str] = None,
        select: Optional[List[Union[str, _models.KeyValueFields]]] = None,
        snapshot: Optional[str] = None,
        if_match: Optional[str] = None,
        if_none_match: Optional[str] = None,
        **kwargs: Any
    ) -> Iterable["_models.KeyValue"]:
        """Gets a list of key-values.

        Gets a list of key-values.

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
        :param snapshot: A filter used get key-values for a snapshot. The value should be the name of
         the snapshot. Not valid when used with 'key' and 'label' filters. Default value is None.
        :type snapshot: str
        :param if_match: Used to perform an operation only if the targeted resource's etag matches the
         value provided. Default value is None.
        :type if_match: str
        :param if_none_match: Used to perform an operation only if the targeted resource's etag does
         not match the value provided. Default value is None.
        :type if_none_match: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either KeyValue or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.appconfiguration.models.KeyValue]
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
                    snapshot=snapshot,
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
                
                # Construct headers
                if if_match is not None:
                    _headers["If-Match"] = _SERIALIZER.header("if_match", if_match, "str")
                if if_none_match is not None:
                    _headers["If-None-Match"] = _SERIALIZER.header("if_none_match", if_none_match, "str")
                _request = HttpRequest(
                    "GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params, headers=_headers
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

        def extract_data(pipeline_response):
            deserialized = self._deserialize("KeyValueListResult", pipeline_response)
            list_of_elem = deserialized.items
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return deserialized.next_link or None, iter(list_of_elem)

        def get_next(next_link=None):
            _request = prepare_request(next_link)

            _stream = False
            pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
                _request, stream=_stream, **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.Error, pipeline_response)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

__all__: List[str] = [
    "AzureAppConfigurationOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
