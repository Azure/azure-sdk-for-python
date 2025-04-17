# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
import io
from typing import Any, Callable, Dict, IO, List, Optional, TypeVar, Union, Mapping, cast, overload

from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ._operations import (
    DocumentIntelligenceClientOperationsMixin as GeneratedDIClientOps,
    DocumentIntelligenceAdministrationClientOperationsMixin as GeneratedDIAdminClientOps,
)
from ... import models as _models
from ..._model_base import _deserialize
from ..._operations._patch import PollingReturnType_co, _parse_operation_id

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]


class AsyncAnalyzeDocumentLROPoller(AsyncLROPoller[PollingReturnType_co]):
    @property
    def details(self) -> Mapping[str, Any]:
        """Returns metadata associated with the long-running operation.

        :return: Returns metadata associated with the long-running operation.
        :rtype: Mapping[str, Any]
        """
        return {
            "operation_id": _parse_operation_id(
                self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore # pylint: disable=protected-access
            ),
        }

    @classmethod
    def from_continuation_token(
        cls, polling_method: AsyncPollingMethod[PollingReturnType_co], continuation_token: str, **kwargs: Any
    ) -> "AsyncAnalyzeDocumentLROPoller":
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class DocumentIntelligenceAdministrationClientOperationsMixin(
    GeneratedDIAdminClientOps
):  # pylint: disable=name-too-long
    @distributed_trace_async
    async def begin_build_classifier(  # type: ignore[override]
        self, body: Union[_models.BuildDocumentClassifierRequest, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[_models.DocumentClassifierDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentClassifierDetails] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._build_classifier_initial(
                body=body, content_type=content_type, cls=lambda x, y, z: x, headers=_headers, params=_params, **kwargs
            )
            await raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.DocumentClassifierDetails, response.json())
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncLROPoller[_models.DocumentClassifierDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncLROPoller[_models.DocumentClassifierDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace_async
    async def begin_build_document_model(  # type: ignore[override]
        self, body: Union[_models.BuildDocumentModelRequest, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[_models.DocumentModelDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentModelDetails] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._build_document_model_initial(
                body=body, content_type=content_type, cls=lambda x, y, z: x, headers=_headers, params=_params, **kwargs
            )
            await raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.DocumentModelDetails, response.json())
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncLROPoller[_models.DocumentModelDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncLROPoller[_models.DocumentModelDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace_async
    async def begin_compose_model(  # type: ignore[override]
        self, body: Union[_models.ComposeDocumentModelRequest, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[_models.DocumentModelDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentModelDetails] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._compose_model_initial(
                body=body, content_type=content_type, cls=lambda x, y, z: x, headers=_headers, params=_params, **kwargs
            )
            await raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.DocumentModelDetails, response.json())
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncLROPoller[_models.DocumentModelDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncLROPoller[_models.DocumentModelDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace_async
    async def begin_copy_model_to(  # type: ignore[override]
        self, model_id: str, body: Union[_models.ModelCopyAuthorization, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[_models.DocumentModelDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentModelDetails] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._copy_model_to_initial(
                model_id=model_id,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
            await raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.DocumentModelDetails, response.json().get("result"))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    lro_options={"final-state-via": "operation-location"},
                    **kwargs
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncLROPoller[_models.DocumentModelDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncLROPoller[_models.DocumentModelDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace_async
    async def begin_copy_classifier_to(  # type: ignore[override]
        self, classifier_id: str, body: Union[_models.ClassifierCopyAuthorization, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[_models.DocumentClassifierDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentClassifierDetails] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._copy_classifier_to_initial(
                classifier_id=classifier_id,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
            await raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.DocumentClassifierDetails, response.json().get("result"))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, lro_options={"final-state-via": "operation-location"}, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncLROPoller[_models.DocumentClassifierDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncLROPoller[_models.DocumentClassifierDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )


class DocumentIntelligenceClientOperationsMixin(GeneratedDIClientOps):  # pylint: disable=name-too-long
    @overload
    async def begin_analyze_document(
        self,
        model_id: str,
        body: _models.AnalyzeDocumentRequest,
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.DocumentContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncAnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param body: Analyze request parameters. Required.
        :type body: ~azure.ai.documentintelligence.models.AnalyzeDocumentRequest
        :keyword pages: 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is None.
        :paramtype pages: str
        :keyword locale: Locale hint for text recognition and document analysis.  Value may contain
         only
         the language code (ex. "en", "fr") or BCP 47 language tag (ex. "en-US"). Default value is
         None.
        :paramtype locale: str
        :keyword string_index_type: Method used to compute string offset and length. Known values are:
         "textElements", "unicodeCodePoint", and "utf16CodeUnit". Default value is None.
        :paramtype string_index_type: str or ~azure.ai.documentintelligence.models.StringIndexType
        :keyword features: List of optional analysis features. Default value is None.
        :paramtype features: list[str or ~azure.ai.documentintelligence.models.DocumentAnalysisFeature]
        :keyword query_fields: List of additional fields to extract.  Ex. "NumberOfGuests,StoreNumber".
         Default value is None.
        :paramtype query_fields: list[str]
        :keyword output_content_format: Format of the analyze result top-level content. Known values
         are: "text" and "markdown". Default value is None.
        :paramtype output_content_format: str or
         ~azure.ai.documentintelligence.models.DocumentContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncAnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping
        :rtype: AsyncAnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_document(
        self,
        model_id: str,
        body: JSON,
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.DocumentContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncAnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param body: Analyze request parameters. Required.
        :type body: JSON
        :keyword pages: 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is None.
        :paramtype pages: str
        :keyword locale: Locale hint for text recognition and document analysis.  Value may contain
         only
         the language code (ex. "en", "fr") or BCP 47 language tag (ex. "en-US"). Default value is
         None.
        :paramtype locale: str
        :keyword string_index_type: Method used to compute string offset and length. Known values are:
         "textElements", "unicodeCodePoint", and "utf16CodeUnit". Default value is None.
        :paramtype string_index_type: str or ~azure.ai.documentintelligence.models.StringIndexType
        :keyword features: List of optional analysis features. Default value is None.
        :paramtype features: list[str or ~azure.ai.documentintelligence.models.DocumentAnalysisFeature]
        :keyword query_fields: List of additional fields to extract.  Ex. "NumberOfGuests,StoreNumber".
         Default value is None.
        :paramtype query_fields: list[str]
        :keyword output_content_format: Format of the analyze result top-level content. Known values
         are: "text" and "markdown". Default value is None.
        :paramtype output_content_format: str or
         ~azure.ai.documentintelligence.models.DocumentContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncAnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping
        :rtype: AsyncAnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_document(
        self,
        model_id: str,
        body: IO[bytes],
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.DocumentContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncAnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param body: Analyze request parameters. Required.
        :type body: IO[bytes]
        :keyword pages: 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is None.
        :paramtype pages: str
        :keyword locale: Locale hint for text recognition and document analysis.  Value may contain
         only
         the language code (ex. "en", "fr") or BCP 47 language tag (ex. "en-US"). Default value is
         None.
        :paramtype locale: str
        :keyword string_index_type: Method used to compute string offset and length. Known values are:
         "textElements", "unicodeCodePoint", and "utf16CodeUnit". Default value is None.
        :paramtype string_index_type: str or ~azure.ai.documentintelligence.models.StringIndexType
        :keyword features: List of optional analysis features. Default value is None.
        :paramtype features: list[str or ~azure.ai.documentintelligence.models.DocumentAnalysisFeature]
        :keyword query_fields: List of additional fields to extract.  Ex. "NumberOfGuests,StoreNumber".
         Default value is None.
        :paramtype query_fields: list[str]
        :keyword output_content_format: Format of the analyze result top-level content. Known values
         are: "text" and "markdown". Default value is None.
        :paramtype output_content_format: str or
         ~azure.ai.documentintelligence.models.DocumentContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncAnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping
        :rtype: AsyncAnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_analyze_document(  # type: ignore[override]
        self,
        model_id: str,
        body: Union[_models.AnalyzeDocumentRequest, JSON, IO[bytes]],
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.DocumentContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        **kwargs: Any
    ) -> AsyncAnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param body: Analyze request parameters. Is one of the following types:
         AnalyzeDocumentRequest, JSON, IO[bytes]. Required.
        :type body: ~azure.ai.documentintelligence.models.AnalyzeDocumentRequest or JSON or
         IO[bytes]
        :keyword pages: 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is None.
        :paramtype pages: str
        :keyword locale: Locale hint for text recognition and document analysis.  Value may contain
         only
         the language code (ex. "en", "fr") or BCP 47 language tag (ex. "en-US"). Default value is
         None.
        :paramtype locale: str
        :keyword string_index_type: Method used to compute string offset and length. Known values are:
         "textElements", "unicodeCodePoint", and "utf16CodeUnit". Default value is None.
        :paramtype string_index_type: str or ~azure.ai.documentintelligence.models.StringIndexType
        :keyword features: List of optional analysis features. Default value is None.
        :paramtype features: list[str or ~azure.ai.documentintelligence.models.DocumentAnalysisFeature]
        :keyword query_fields: List of additional fields to extract.  Ex. "NumberOfGuests,StoreNumber".
         Default value is None.
        :paramtype query_fields: list[str]
        :keyword output_content_format: Format of the analyze result top-level content. Known values
         are: "text" and "markdown". Default value is None.
        :paramtype output_content_format: str or
         ~azure.ai.documentintelligence.models.DocumentContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :return: An instance of AsyncAnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping
        :rtype: AsyncAnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("content-type", None))
        cls: ClsType[_models.AnalyzeResult] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            if isinstance(body, (bytes, io.BytesIO, io.BufferedReader)):
                content_type = "application/octet-stream"
            raw_result = await self._analyze_document_initial(
                model_id=model_id,
                body=body,
                pages=pages,
                locale=locale,
                string_index_type=string_index_type,
                features=features,
                query_fields=query_fields,
                output_content_format=output_content_format,
                output=output,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
            await raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.AnalyzeResult, response.json().get("analyzeResult"))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncAnalyzeDocumentLROPoller[_models.AnalyzeResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncAnalyzeDocumentLROPoller[_models.AnalyzeResult](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace_async
    async def begin_classify_document(  # type: ignore[override]
        self,
        classifier_id: str,
        body: Union[_models.ClassifyDocumentRequest, JSON, IO[bytes]],
        *,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        split: Optional[Union[str, _models.SplitMode]] = None,
        pages: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.AnalyzeResult]:
        """Classifies document with document classifier.

        :param classifier_id: Unique document classifier name. Required.
        :type classifier_id: str
        :param body: Classify request parameters. Is one of the following types:
         ClassifyDocumentRequest, JSON, IO[bytes] Required.
        :type body: ~azure.ai.documentintelligence.models.ClassifyDocumentRequest or JSON
         or IO[bytes]
        :keyword string_index_type: Method used to compute string offset and length. Known values are:
         "textElements", "unicodeCodePoint", and "utf16CodeUnit". Default value is None.
        :paramtype string_index_type: str or ~azure.ai.documentintelligence.models.StringIndexType
        :keyword split: Document splitting mode. Known values are: "auto", "none", and "perPage".
         Default value is None.
        :paramtype split: str or ~azure.ai.documentintelligence.models.SplitMode
        :keyword pages: 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is None.
        :paramtype pages: str
        :return: An instance of AsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("content-type", None))
        if isinstance(body, (bytes, io.BytesIO, io.BufferedReader)):
            content_type = "application/octet-stream"
        return await super().begin_classify_document(  # type: ignore[arg-type, misc]
            classifier_id=classifier_id,
            body=body,  # type: ignore[arg-type]
            content_type=content_type,  # type: ignore[arg-type]
            string_index_type=string_index_type,
            split=split,
            pages=pages,
            **kwargs
        )

    @distributed_trace_async
    async def get_analyze_batch_result(  # type: ignore[override] # pylint: disable=arguments-differ
        self, continuation_token: str
    ) -> AsyncLROPoller[_models.AnalyzeBatchResult]:
        """Gets the result of batch document analysis.

        :param str continuation_token: An opaque continuation token. Required.
        :return: An instance of AsyncLROPoller that returns AnalyzeBatchResult. The AnalyzeBatchResult
         is compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.ai.documentintelligence.models.AnalyzeBatchResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self.begin_analyze_batch_documents(  # type: ignore[call-overload]
            None, None, continuation_token=continuation_token
        )


__all__: List[str] = [
    "DocumentIntelligenceClientOperationsMixin",
    "DocumentIntelligenceAdministrationClientOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
