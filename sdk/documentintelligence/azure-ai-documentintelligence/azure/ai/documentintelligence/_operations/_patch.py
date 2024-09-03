# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
import re
from typing import Any, Callable, Dict, IO, List, Optional, TypeVar, Union, cast, overload

from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.polling.base_polling import LROBasePolling
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ._operations import (
    DocumentIntelligenceClientOperationsMixin as GeneratedDIClientOps,
    DocumentIntelligenceAdministrationClientOperationsMixin as GeneratedDIAdminClientOps,
)
from .. import models as _models
from .._model_base import _deserialize

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]
PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)
_FINISHED = frozenset(["succeeded", "canceled", "failed", "completed"])


def _parse_operation_id(operation_location_header):
    regex = "[^:]+://[^/]+/documentintelligence/.+/([^?/]+)"
    return re.match(regex, operation_location_header).group(1)


class AnalyzeDocumentLROPollingMethod(LROBasePolling):
    @property
    def operation_id(self) -> str:
        return _parse_operation_id(self._initial_response.http_response.headers["Operation-Location"])


class AnalyzeDocumentLROPoller(LROPoller[PollingReturnType_co]):
    def polling_method(self) -> AnalyzeDocumentLROPollingMethod:
        """Return the polling method associated to this poller.

        :return: AnalyzeDocumentLROPollingMethod
        :rtype: ~azure.ai.documentintelligence._operations._patch.AnalyzeDocumentLROPollingMethod
        """
        return self._polling_method  # type: ignore

    @property
    def operation_id(self) -> str:
        return self.polling_method().operation_id


class AnalyzeBatchDocumentsLROPollingMethod(LROBasePolling):
    def finished(self) -> bool:
        """Is this polling finished?

        :return: Whether polling is finished or not.
        :rtype: bool
        """
        return AnalyzeBatchDocumentsLROPollingMethod._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED


class DocumentIntelligenceAdministrationClientOperationsMixin(
    GeneratedDIAdminClientOps
):  # pylint: disable=name-too-long
    @distributed_trace
    def begin_build_classifier(
        self, build_request: Union[_models.BuildDocumentClassifierRequest, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[_models.DocumentClassifierDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentClassifierDetails] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._build_classifier_initial(  # type: ignore
                build_request=build_request,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs,
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
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
            polling_method: PollingMethod = cast(
                PollingMethod, LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller[_models.DocumentClassifierDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller[_models.DocumentClassifierDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_build_document_model(
        self, build_request: Union[_models.BuildDocumentModelRequest, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[_models.DocumentModelDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentModelDetails] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._build_document_model_initial(  # type: ignore
                build_request=build_request,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs,
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
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
            polling_method: PollingMethod = cast(
                PollingMethod, LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller[_models.DocumentModelDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller[_models.DocumentModelDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_compose_model(
        self, compose_request: Union[_models.ComposeDocumentModelRequest, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[_models.DocumentModelDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentModelDetails] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._compose_model_initial(  # type: ignore
                compose_request=compose_request,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs,
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
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
            polling_method: PollingMethod = cast(
                PollingMethod, LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller[_models.DocumentModelDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller[_models.DocumentModelDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_copy_model_to(
        self, model_id: str, copy_to_request: Union[_models.CopyAuthorization, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[_models.DocumentModelDetails]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.DocumentModelDetails] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._copy_model_to_initial(  # type: ignore
                model_id=model_id,
                copy_to_request=copy_to_request,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs,
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
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
            polling_method: PollingMethod = cast(
                PollingMethod, LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller[_models.DocumentModelDetails].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller[_models.DocumentModelDetails](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )


class DocumentIntelligenceClientOperationsMixin(GeneratedDIClientOps):  # pylint: disable=name-too-long
    @overload
    def begin_analyze_document(
        self,
        model_id: str,
        analyze_request: Optional[_models.AnalyzeDocumentRequest] = None,
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.ContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param analyze_request: Analyze request parameters. Default value is None.
        :type analyze_request: ~azure.ai.documentintelligence.models.AnalyzeDocumentRequest
        :keyword pages: Range of 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is
         None.
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
        :paramtype output_content_format: str or ~azure.ai.documentintelligence.models.ContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.ai.documentintelligence.AnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_document(
        self,
        model_id: str,
        analyze_request: Optional[JSON] = None,
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.ContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param analyze_request: Analyze request parameters. Default value is None.
        :type analyze_request: JSON
        :keyword pages: Range of 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is
         None.
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
        :paramtype output_content_format: str or ~azure.ai.documentintelligence.models.ContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.ai.documentintelligence.AnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_document(
        self,
        model_id: str,
        analyze_request: Optional[IO[bytes]] = None,
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.ContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param analyze_request: Analyze request parameters. Default value is None.
        :type analyze_request: IO[bytes]
        :keyword pages: Range of 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is
         None.
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
        :paramtype output_content_format: str or ~azure.ai.documentintelligence.models.ContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.ai.documentintelligence.AnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_analyze_document(
        self,
        model_id: str,
        analyze_request: Optional[Union[_models.AnalyzeDocumentRequest, JSON, IO[bytes]]] = None,
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.ContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        **kwargs: Any,
    ) -> AnalyzeDocumentLROPoller[_models.AnalyzeResult]:
        """Analyzes document with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param analyze_request: Analyze request parameters. Is one of the following types:
         AnalyzeDocumentRequest, JSON, IO[bytes] Default value is None.
        :type analyze_request: ~azure.ai.documentintelligence.models.AnalyzeDocumentRequest or JSON or
         IO[bytes]
        :keyword pages: Range of 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is
         None.
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
        :paramtype output_content_format: str or ~azure.ai.documentintelligence.models.ContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :return: An instance of AnalyzeDocumentLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.ai.documentintelligence.AnalyzeDocumentLROPoller[~azure.ai.documentintelligence.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("content-type", None))
        cls: ClsType[_models.AnalyzeResult] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result, response_headers = self._analyze_document_initial(
                model_id=model_id,
                analyze_request=analyze_request,
                pages=pages,
                locale=locale,
                string_index_type=string_index_type,
                features=features,
                query_fields=query_fields,
                output_content_format=output_content_format,
                output=output,
                content_type=content_type,
                cls=lambda x, y, z: (x, z),
                headers=_headers,
                params=_params,
                **kwargs,
            )
            raw_result.http_response.read()  # type: ignore
            # operation_id = _parse_operation_id(response_headers["Operation-Location"])
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
            polling_method: PollingMethod = cast(
                PollingMethod,
                AnalyzeDocumentLROPollingMethod(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AnalyzeDocumentLROPoller[_models.AnalyzeResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AnalyzeDocumentLROPoller[_models.AnalyzeResult](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_analyze_batch_documents(
        self,
        model_id: str,
        analyze_batch_request: Optional[Union[_models.AnalyzeBatchDocumentsRequest, JSON, IO[bytes]]] = None,
        *,
        pages: Optional[str] = None,
        locale: Optional[str] = None,
        string_index_type: Optional[Union[str, _models.StringIndexType]] = None,
        features: Optional[List[Union[str, _models.DocumentAnalysisFeature]]] = None,
        query_fields: Optional[List[str]] = None,
        output_content_format: Optional[Union[str, _models.ContentFormat]] = None,
        output: Optional[List[Union[str, _models.AnalyzeOutputOption]]] = None,
        **kwargs: Any,
    ) -> LROPoller[_models.AnalyzeBatchResult]:
        """Analyzes batch documents with document model.

        :param model_id: Unique document model name. Required.
        :type model_id: str
        :param analyze_batch_request: Analyze batch request parameters. Is one of the following types:
         AnalyzeBatchDocumentsRequest, JSON, IO[bytes] Default value is None.
        :type analyze_batch_request: ~azure.ai.documentintelligence.models.AnalyzeBatchDocumentsRequest
         or JSON or IO[bytes]
        :keyword pages: Range of 1-based page numbers to analyze.  Ex. "1-3,5,7-9". Default value is
         None.
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
        :paramtype output_content_format: str or ~azure.ai.documentintelligence.models.ContentFormat
        :keyword output: Additional outputs to generate during analysis. Default value is None.
        :paramtype output: list[str or ~azure.ai.documentintelligence.models.AnalyzeOutputOption]
        :return: An instance of LROPoller that returns AnalyzeBatchResult. The AnalyzeBatchResult is
         compatible with MutableMapping
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.documentintelligence.models.AnalyzeBatchResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("content-type", None))
        cls: ClsType[_models.AnalyzeBatchResult] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._analyze_batch_documents_initial(
                model_id=model_id,
                analyze_batch_request=analyze_batch_request,
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
                **kwargs,
            )
            raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.AnalyzeBatchResult, response.json().get("result"))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod,
                AnalyzeBatchDocumentsLROPollingMethod(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller[_models.AnalyzeBatchResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller[_models.AnalyzeBatchResult](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
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
