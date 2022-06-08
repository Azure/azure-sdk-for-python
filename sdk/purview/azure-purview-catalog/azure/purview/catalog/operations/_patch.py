# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level



def build_entity_import_business_metadata_request(
    uploadedInputStream: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> HttpRequest:
    content_type = kwargs.pop('content_type', None)  # type: Optional[str]

    accept = "application/json"
    # Construct URL
    _url = "/atlas/v2/entity/businessmetadata/import"

    # Construct headers
    _header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    if content_type is not None:
        _header_parameters['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_query_parameters,
        headers=_header_parameters,
        uploadedInputStream=uploadedInputStream,
        content=content,
        **kwargs
    )


def build_glossary_import_glossary_terms_via_csv_request_initial(
    glossary_guid: str,
    *,
    files: Optional[Dict[str, Any]] = None,
    content: Any = None,
    include_term_hierarchy: Optional[bool] = False,
    **kwargs: Any
) -> HttpRequest:
    api_version = kwargs.pop('api_version', "2022-03-01-preview")  # type: str
    content_type = kwargs.pop('content_type', None)  # type: Optional[str]

    accept = "application/json"
    # Construct URL
    _url = "/glossary/{glossaryGuid}/terms/import"
    path_format_arguments = {
        "glossaryGuid": _SERIALIZER.url("glossary_guid", glossary_guid, 'str', max_length=4096, min_length=1),
    }

    _url = _format_url_section(_url, **path_format_arguments)

    # Construct parameters
    _query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    if include_term_hierarchy is not None:
        _query_parameters['includeTermHierarchy'] = _SERIALIZER.query("include_term_hierarchy", include_term_hierarchy, 'bool')
    _query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    _header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    if content_type is not None:
        _header_parameters['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_query_parameters,
        headers=_header_parameters,
        files=files,
        content=content,
        **kwargs
    )


def build_glossary_import_glossary_terms_via_csv_by_glossary_name_request_initial(
        glossary_name: str,
    *,
    files: Optional[Dict[str, Any]] = None,
    content: Any = None,
    include_term_hierarchy: Optional[bool] = False,
    **kwargs: Any
) -> HttpRequest:
    api_version = kwargs.pop('api_version', "2022-03-01-preview")  # type: str
    content_type = kwargs.pop('content_type', None)  # type: Optional[str]

    accept = "application/json"
    # Construct URL
    _url = "/glossary/name/{glossaryName}/terms/import"
    path_format_arguments = {
        "glossaryName": _SERIALIZER.url("glossary_name", glossary_name, 'str', max_length=4096, min_length=1),
    }

    _url = _format_url_section(_url, **path_format_arguments)

    # Construct parameters
    _query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    if include_term_hierarchy is not None:
        _query_parameters['includeTermHierarchy'] = _SERIALIZER.query("include_term_hierarchy", include_term_hierarchy, 'bool')
    _query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    _header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    if content_type is not None:
        _header_parameters['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_query_parameters,
        headers=_header_parameters,
        files=files,
        content=content,
        **kwargs
    )


def import_business_metadata(
    self,
    *args,
    **kwargs
    ) -> JSON:
    _headers = kwargs.pop("headers", {}) or {}
    _params = kwargs.pop("params", {}) or {}

    request = build_entity_import_business_metadata_reques(
        headers=_headers,
        params=_params,
    )
    path_format_arguments = {
        "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
    }
    request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

    pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
        request,
        stream=True,
        **kwargs
    )
    response = pipeline_response.http_response

    if response.status_code not in [200]:
        map_error(status_code=response.status_code, response=response, error_map=error_map)
        raise HttpResponseError(response=response)

    deserialized = response
    return deserialized


def begin_import_glossary_terms_via_csv(
    self,
    glossary_guid: str,
    files: Dict[str, Any],
    *,
    include_term_hierarchy: Optional[bool] = False,
    **kwargs: Any
    ) -> LROPoller[JSON]:
    api_version = kwargs.pop('api_version', "2022-03-01-preview")  #type: str
    content_type = kwargs.pop('content_type', None)  #type: Optional[str]
    polling = kwargs.pop('polling', True)  #type: Union[bool, PollingMethod]
    cls = kwargs.pop('cls', None)# type: ClsType[JSONType]
    lro_delay = kwargs.pop(
        'polling_interval',
        self._config.polling_interval
    )
    cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]
    if cont_token is None:
        raw_result = self._import_glossary_terms_via_csv_initial(
            glossary_guid=glossary_guid,
            files=files,
            include_term_hierarchy=include_term_hierarchy,
            api_version=api_version,
            content_type=content_type,
            cls=lambda x,y,z: x,
            **kwargs
        )
    kwargs.pop('error_map', None)

    def get_long_running_output(pipeline_response):
        response = pipeline_response.http_response
        if response.content:
            deserialized = response.json()
        else:
            deserialized = None
        if cls:
            return cls(pipeline_response, deserialized, {})
        return deserialized


    path_format_arguments = {
        "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
    }

    if polling is True: polling_method = LROBasePolling(lro_delay, lro_options={'final-state-via': 'azure-async-operation'}, path_format_arguments=path_format_arguments, **kwargs)
    elif polling is False: polling_method = NoPolling()
    else: polling_method = polling
    if cont_token:
        return LROPoller.from_continuation_token(
            polling_method=polling_method,
            continuation_token=cont_token,
            client=self._client,
            deserialization_callback=get_long_running_output
         )
    return LROPoller(self._client, raw_result, get_long_running_output, polling_method)


def begin_import_glossary_terms_via_csv_by_glossary_name(
    self,
    glossary_name: str,
    files: Dict[str, Any],
    *,
    include_term_hierarchy: Optional[bool] = False,
    **kwargs: Any
    ) -> LROPoller[JSON]:
    api_version = kwargs.pop('api_version', "2022-03-01-preview")  # type: str
    content_type = kwargs.pop('content_type', None)  # type: Optional[str]
    polling = kwargs.pop('polling', True)  # type: Union[bool, PollingMethod]
    cls = kwargs.pop('cls', None)  # type: ClsType[JSONType]
    lro_delay = kwargs.pop(
        'polling_interval',
        self._config.polling_interval
    )
    cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]
    if cont_token is None:
        raw_result = self._import_glossary_terms_via_csv_by_glossary_name_initial(
            glossary_name=glossary_name,
            files=files,
            include_term_hierarchy=include_term_hierarchy,
            api_version=api_version,
            content_type=content_type,
            cls=lambda x,y,z: x,
            **kwargs
            )
    kwargs.pop('error_map', None)

    def get_long_running_output(pipeline_response):
        response = pipeline_response.http_response
        if response.content:
            deserialized = response.json()
        else:
            deserialized = None
        if cls:
            return cls(pipeline_response, deserialized, {})
        return deserialized


    path_format_arguments = {
        "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
    }

    if polling is True: polling_method = LROBasePolling(lro_delay, lro_options={'final-state-via': 'azure-async-operation'}, path_format_arguments=path_format_arguments, **kwargs)
    elif polling is False: polling_method = NoPolling()
    else: polling_method = polling
    if cont_token:
        return LROPoller.from_continuation_token(
            polling_method=polling_method,
            continuation_token=cont_token,
            client=self._client,
            deserialization_callback=get_long_running_output
        )
    return LROPoller(self._client, raw_result, get_long_running_output, polling_method)

