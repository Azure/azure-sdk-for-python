# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Callable, Union, overload, MutableMapping
from azure.core.tracing.decorator_async import distributed_trace_async
from ._operations import _TranscriptionClientOperationsMixin as _TranscriptionClientOperationsMixinGenerated
from ... import models as _models

JSON = MutableMapping[str, Any]


class _TranscriptionClientOperationsMixin(_TranscriptionClientOperationsMixinGenerated):
    """Custom operations mixin to add documentation examples."""

    @overload
    async def transcribe(self, body: _models.TranscribeRequestContent, **kwargs: Any) -> _models.TranscriptionResult:
        """Transcribes the provided audio stream.

        :param body: The body of the multipart request. Required.
        :type body: ~azure.ai.speech.transcription.models.TranscribeRequestContent
        :return: TranscriptionResult. The TranscriptionResult is compatible with MutableMapping
        :rtype: ~azure.ai.speech.transcription.models.TranscriptionResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def transcribe(self, body: JSON, **kwargs: Any) -> _models.TranscriptionResult:
        """Transcribes the provided audio stream.

        :param body: The body of the multipart request. Required.
        :type body: JSON
        :return: TranscriptionResult. The TranscriptionResult is compatible with MutableMapping
        :rtype: ~azure.ai.speech.transcription.models.TranscriptionResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def transcribe(
        self, body: Union[_models.TranscribeRequestContent, JSON], **kwargs: Any
    ) -> _models.TranscriptionResult:
        """Transcribes the provided audio stream.

        :param body: The body of the multipart request. Is either a TranscribeRequestContent type or a
         JSON type. Required.
        :type body: ~azure.ai.speech.transcription.models.TranscribeRequestContent or JSON
        :return: TranscriptionResult. The TranscriptionResult is compatible with MutableMapping
        :rtype: ~azure.ai.speech.transcription.models.TranscriptionResult
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_transcribe_audio_file_async.py
                :start-after: [START transcribe_audio_file_async]
                :end-before: [END transcribe_audio_file_async]
                :language: python
                :dedent: 4
                :caption: Transcribe an audio file asynchronously
        """
        original_url: Callable[[str, str, str], str] = self._serialize.url

        def _passthrough_endpoint(name: str, value: str, data_type: str) -> str:
            if name == "self._config.endpoint":
                return value.rstrip("/")
            return original_url(name, value, data_type)

        self._serialize.url = _passthrough_endpoint  # type: ignore[assignment]
        try:
            return await super().transcribe(body, **kwargs)
        finally:
            self._serialize.url = original_url  # type: ignore[assignment]


__all__: list[str] = [
    "_TranscriptionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
