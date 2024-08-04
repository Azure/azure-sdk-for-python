# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import AsyncIterator, Callable, Dict, Type, TypeVar, overload, Any, IO, List, Optional, Union, cast
from azure.core.polling import AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.utils import case_insensitive_dict

from ..._vendor import prepare_multipart_form_data
from ...models import _models
from ... import _model_base

from ..._model_base import _deserialize
from ._operations import (
    DocumentTranslationClientOperationsMixin as GeneratedDocumentTranslationClientOperationsMixin,
    SingleDocumentTranslationClientOperationsMixin as GeneratedSingleDocumentTranslationClientOperationsMixin,
    build_single_document_translation_document_translate_request,
    JSON,
    ClsType,
)
from ...aio._patch import AsyncDocumentTranslationLROPoller

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # type: ignore[misc] # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[  # type: ignore[misc]
    Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]
]


class DocumentTranslationClientOperationsMixin(GeneratedDocumentTranslationClientOperationsMixin):

    @distributed_trace
    async def begin_start_translation(  # type: ignore[override]
        self, body: Union[_models.StartTranslationDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[_models.TranslationStatus]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.TranslationStatus] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._start_translation_initial(  # type: ignore[func-returns-value]
                body=body, content_type=content_type, cls=lambda x, y, z: x, headers=_headers, params=_params, **kwargs
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.TranslationStatus, response.json())
            if cls:
                return cls(pipeline_response, deserialized, response_headers)
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
            return AsyncDocumentTranslationLROPoller[_models.TranslationStatus].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncDocumentTranslationLROPoller[_models.TranslationStatus](
            self._client, raw_result, get_long_running_output, polling_method
        )


class SingleDocumentTranslationClientOperationsMixin(
    GeneratedSingleDocumentTranslationClientOperationsMixin
):  # pylint: disable=name-too-long

    @overload
    async def document_translate(
        self,
        body: _models.DocumentTranslateContent,
        *,
        target_language: str,
        source_language: Optional[str] = None,
        category: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Submit a single document translation request to the Document Translation service.

        Use this API to submit a single translation request to the Document Translation Service.

        :param body: Required.
        :type body: ~azure.ai.translation.document.models.DocumentTranslateContent
        :keyword target_language: Specifies the language of the output document.
         The target language must be one of the supported languages included in the translation scope.
         For example if you want to translate the document in German language, then use
         targetLanguage=de. Required.
        :paramtype target_language: str
        :keyword source_language: Specifies source language of the input document.
         If this parameter isn't specified, automatic language detection is applied to determine the
         source language.
         For example if the source document is written in English, then use sourceLanguage=en. Default
         value is None.
        :paramtype source_language: str
        :keyword category: A string specifying the category (domain) of the translation. This parameter
         is used to get translations
         from a customized system built with Custom Translator. Add the Category ID from your Custom
         Translator
         project details to this parameter to use your deployed customized system. Default value is:
         general. Default value is None.
        :paramtype category: str
        :keyword allow_fallback: Specifies that the service is allowed to fall back to a general system
         when a custom system doesn't exist.
         Possible values are: true (default) or false. Default value is None.
        :paramtype allow_fallback: bool
        :return: AsyncIterator[bytes]
        :rtype: AsyncIterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "document": filetype,
                    "glossary": [filetype]
                }
        """

    @overload
    async def document_translate(
        self,
        body: JSON,
        *,
        target_language: str,
        source_language: Optional[str] = None,
        category: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Submit a single document translation request to the Document Translation service.

        Use this API to submit a single translation request to the Document Translation Service.

        :param body: Required.
        :type body: JSON
        :keyword target_language: Specifies the language of the output document.
         The target language must be one of the supported languages included in the translation scope.
         For example if you want to translate the document in German language, then use
         targetLanguage=de. Required.
        :paramtype target_language: str
        :keyword source_language: Specifies source language of the input document.
         If this parameter isn't specified, automatic language detection is applied to determine the
         source language.
         For example if the source document is written in English, then use sourceLanguage=en. Default
         value is None.
        :paramtype source_language: str
        :keyword category: A string specifying the category (domain) of the translation. This parameter
         is used to get translations
         from a customized system built with Custom Translator. Add the Category ID from your Custom
         Translator
         project details to this parameter to use your deployed customized system. Default value is:
         general. Default value is None.
        :paramtype category: str
        :keyword allow_fallback: Specifies that the service is allowed to fall back to a general system
         when a custom system doesn't exist.
         Possible values are: true (default) or false. Default value is None.
        :paramtype allow_fallback: bool
        :return: AsyncIterator[bytes]
        :rtype: AsyncIterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def document_translate(
        self,
        body: Union[_models.DocumentTranslateContent, JSON],
        *,
        target_language: str,
        source_language: Optional[str] = None,
        category: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Submit a single document translation request to the Document Translation service.

        Use this API to submit a single translation request to the Document Translation Service.

        :param body: Is either a DocumentTranslateContent type or a JSON type. Required.
        :type body: ~azure.ai.translation.document.models.DocumentTranslateContent or JSON
        :keyword target_language: Specifies the language of the output document.
         The target language must be one of the supported languages included in the translation scope.
         For example if you want to translate the document in German language, then use
         targetLanguage=de. Required.
        :paramtype target_language: str
        :keyword source_language: Specifies source language of the input document.
         If this parameter isn't specified, automatic language detection is applied to determine the
         source language.
         For example if the source document is written in English, then use sourceLanguage=en. Default
         value is None.
        :paramtype source_language: str
        :keyword category: A string specifying the category (domain) of the translation. This parameter
         is used to get translations
         from a customized system built with Custom Translator. Add the Category ID from your Custom
         Translator
         project details to this parameter to use your deployed customized system. Default value is:
         general. Default value is None.
        :paramtype category: str
        :keyword allow_fallback: Specifies that the service is allowed to fall back to a general system
         when a custom system doesn't exist.
         Possible values are: true (default) or false. Default value is None.
        :paramtype allow_fallback: bool
        :return: AsyncIterator[bytes]
        :rtype: AsyncIterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "document": filetype,
                    "glossary": [filetype]
                }
        """
        error_map: MutableMapping[int, Type[HttpResponseError]] = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[AsyncIterator[bytes]] = kwargs.pop("cls", None)

        _body = body.as_dict() if isinstance(body, _model_base.Model) else body
        _file_fields: List[str] = ["document", "glossary"]
        _data_fields: List[str] = []
        _files, _data = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_single_document_translation_document_translate_request(
            target_language=target_language,
            source_language=source_language,
            category=category,
            allow_fallback=allow_fallback,
            api_version=self._config.api_version,
            files=_files,
            data=_data,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = kwargs.pop("stream", True)
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        response_headers = {}
        response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))

        # deserialized = response.iter_bytes()

        if cls:
            # return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return cls(pipeline_response, response.read(), response_headers)  # type: ignore

        return await response.read()


__all__: List[str] = [
    "DocumentTranslationClientOperationsMixin",
    "SingleDocumentTranslationClientOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
