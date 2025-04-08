# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import urllib.parse
from typing import Any, AsyncIterable, List, Optional, Union, MutableMapping, Type
from azure.core import MatchConditions
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    ResourceModifiedError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict
from ._operations import (
    AzureAppConfigurationClientOperationsMixin as AzureAppConfigClientOpGenerated,
    ClsType,
    build_azure_app_configuration_get_key_values_request,
)
from ... import models as _models
from ..._model_base import _deserialize


class AzureAppConfigurationClientOperationsMixin(AzureAppConfigClientOpGenerated):
    @distributed_trace_async
    async def get_key_values_in_one_page(
        self,
        *,
        key: Optional[str] = None,
        label: Optional[str] = None,
        sync_token: Optional[str] = None,
        after: Optional[str] = None,
        accept_datetime: Optional[str] = None,
        select: Optional[List[Union[str, _models.ConfigurationSettingFields]]] = None,
        snapshot: Optional[str] = None,
        tags: Optional[List[str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        continuation_token: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterable["_models.KeyValue"]:
        """Gets a list of key-values in one page.

        Gets a list of key-values in one page.

        :keyword key: A filter used to match keys. Syntax reference:
         https://aka.ms/azconfig/docs/keyvaluefiltering. Default value is None.
        :paramtype key: str
        :keyword label: A filter used to match labels. Syntax reference:
         https://aka.ms/azconfig/docs/keyvaluefiltering. Default value is None.
        :paramtype label: str
        :keyword sync_token: Used to guarantee real-time consistency between requests. Default value is
         None.
        :paramtype sync_token: str
        :keyword after: Instructs the server to return elements that appear after the element referred
         to by the specified token. Default value is None.
        :paramtype after: str
        :keyword accept_datetime: Requests the server to respond with the state of the resource at the
         specified
         time. Default value is None.
        :paramtype accept_datetime: str
        :keyword select: Used to select what fields are present in the returned resource(s). Default
         value is None.
        :paramtype select: list[str or ~azure.appconfiguration.models.KeyValueFields]
        :keyword snapshot: A filter used get key-values for a snapshot. The value should be the name of
         the snapshot. Not valid when used with 'key' and 'label' filters. Default value is None.
        :paramtype snapshot: str
        :keyword tags: A filter used to query by tags. Syntax reference:
         https://aka.ms/azconfig/docs/keyvaluefiltering. Default value is None.
        :paramtype tags: list[str]
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :param str continuation_token: An opaque continuation token.
        :return: An iterator like instance of KeyValue
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.appconfiguration.models.KeyValue]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[List[_models.KeyValue]] = kwargs.pop("cls", None)

        error_map: MutableMapping[int, Type[HttpResponseError]] = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        elif match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        elif match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(next_link=None):
            if not next_link:

                _request = build_azure_app_configuration_get_key_values_request(
                    key=key,
                    label=label,
                    sync_token=sync_token,
                    after=after,
                    accept_datetime=accept_datetime,
                    select=select,
                    snapshot=snapshot,
                    tags=tags,
                    etag=etag,
                    match_condition=match_condition,
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

        _request = prepare_request(continuation_token)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = _deserialize(_models.Error, response.json())
            raise HttpResponseError(response=response, model=error)

        response_headers = response.headers
        deserialized = pipeline_response.http_response.json()

        if cls:
            return cls(pipeline_response, deserialized, response_headers)

        return deserialized


__all__: List[str] = [
    "AzureAppConfigurationClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
