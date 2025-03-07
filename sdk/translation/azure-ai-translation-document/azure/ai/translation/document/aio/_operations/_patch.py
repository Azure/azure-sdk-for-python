# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=protected-access
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import AsyncIterator, Callable, Dict, Type, TypeVar, overload, Any, IO, List, Optional, Union, cast, Tuple
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
from azure.core.polling import AsyncLROPoller
from azure.core.polling.base_polling import (
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)
from ..._vendor import prepare_multipart_form_data
from ... import _model_base, models as _models

from ..._model_base import _deserialize
from ...models import (
    TranslationStatus,
)
from ._operations import (
    DocumentTranslationClientOperationsMixin as GeneratedDocumentTranslationClientOperationsMixin,
    SingleDocumentTranslationClientOperationsMixin as GeneratedSingleDocumentTranslationClientOperationsMixin,
    build_single_document_translation_translate_request,
    JSON,
    ClsType,
)

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore
JSON = MutableMapping[str, Any]  # type: ignore[misc] # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[  # type: ignore[misc]
    Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]
]

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)
_FINISHED = frozenset(["succeeded", "cancelled", "cancelling", "failed"])
_FAILED = frozenset(["validationfailed"])


class AsyncDocumentTranslationLROPoller(AsyncLROPoller[PollingReturnType_co]):
    """An async custom poller implementation for Document Translation. Call `result()` on the poller to return
    a pageable of :class:`~azure.ai.translation.document.DocumentStatus`."""

    _polling_method: "AsyncDocumentTranslationLROPollingMethod"

    @property
    def id(self) -> str:
        """The ID for the translation operation

        :return: The str ID for the translation operation.
        :rtype: str
        """
        if self._polling_method._current_body:
            return self._polling_method._current_body.id
        return self._polling_method._get_id_from_headers()

    @property
    def details(self) -> TranslationStatus:
        """The details for the translation operation

        :return: The details for the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        """
        if self._polling_method._current_body:
            return TranslationStatus(self._polling_method._current_body)
        return TranslationStatus(id=self._polling_method._get_id_from_headers())  # type: ignore

    @classmethod
    def from_continuation_token(  # pylint: disable=docstring-missing-return,docstring-missing-param,docstring-missing-rtype
        cls, polling_method, continuation_token, **kwargs
    ):
        """
        :meta private:
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class AsyncDocumentTranslationLROPollingMethod(AsyncLROBasePolling):
    """A custom polling method implementation for Document Translation."""

    def __init__(self, *args, **kwargs):
        self._cont_token_response = kwargs.pop("cont_token_response")
        super().__init__(*args, **kwargs)

    @property
    def _current_body(self) -> TranslationStatus:
        try:
            return TranslationStatus(self._pipeline_response.http_response.json())
        except Exception:  # pylint: disable=broad-exception-caught
            return TranslationStatus()  # type: ignore[call-overload]

    def _get_id_from_headers(self) -> str:
        return (
            self._initial_response.http_response.headers["Operation-Location"]
            .split("/batches/")[1]
            .split("?api-version")[0]
        )

    def finished(self) -> bool:
        """Is this polling finished?

        :return: True/False for whether polling is complete.
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        if self._current_body:
            return self._current_body.id
        return self._get_id_from_headers()

    # pylint: disable=arguments-differ
    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:  # type: ignore[override]
        try:
            client = kwargs["client"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token") from exc

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from exc

        return client, self._cont_token_response, deserialization_callback

    async def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """
        if not self.finished():
            await self.update_status()
        while not self.finished():
            await self._delay()
            await self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = await self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)


class DocumentTranslationClientOperationsMixin(GeneratedDocumentTranslationClientOperationsMixin):

    @distributed_trace
    async def _begin_translation(  # type: ignore[override]
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
            raw_result = await self.__begin_translation_initial(  # type: ignore[func-returns-value]
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
            self._client, raw_result, get_long_running_output, polling_method # pylint: disable=possibly-used-before-assignment
        )


class SingleDocumentTranslationClientOperationsMixin(
    GeneratedSingleDocumentTranslationClientOperationsMixin
):  # pylint: disable=name-too-long

    @overload
    async def translate(
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
    async def translate(
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
    async def translate(
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

        _request = build_single_document_translation_translate_request(
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
