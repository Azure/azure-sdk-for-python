# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping
from typing import Any, Optional
from azure.core.tracing.decorator_async import distributed_trace_async

from ... import models as _models
from ._operations import (
    _TranscriptionClientOperationsMixin as _TranscriptionClientOperationsMixinGenerated,
)

JSON = MutableMapping[str, Any]


class _TranscriptionClientOperationsMixin(_TranscriptionClientOperationsMixinGenerated):
    """Custom async operations mixin for TranscriptionClient."""

    @distributed_trace_async
    async def transcribe_from_url(
        self, audio_url: str, *, options: Optional[_models.TranscriptionOptions] = None, **kwargs: Any
    ) -> _models.TranscriptionResult:
        """Transcribes audio from a URL.

        Use this method when the audio is hosted at a URL that the service can access.
        For transcribing local audio files or byte streams, use :meth:`transcribe` instead.

        :param audio_url: The URL of the audio file to transcribe. The audio must be shorter than 2
         hours in duration and smaller than 250 MB in size. Required.
        :type audio_url: str
        :keyword options: Optional transcription configuration. If provided, the audio_url parameter
         will override the audio_url field in the options object.
        :paramtype options: ~azure.ai.transcription.models.TranscriptionOptions
        :return: TranscriptionResult with the transcription text and phrases.
        :rtype: ~azure.ai.transcription.models.TranscriptionResult
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_transcribe_from_url_async.py
                :start-after: [START transcribe_from_url_async]
                :end-before: [END transcribe_from_url_async]
                :language: python
                :dedent: 4
                :caption: Transcribe audio from a URL asynchronously.
        """
        # Create or update options with the audio URL
        if options is None:
            options = _models.TranscriptionOptions(audio_url=audio_url)
        else:
            options.audio_url = audio_url

        # Create request content without audio file (service will fetch from URL)
        body = _models.TranscriptionContent(definition=options, audio=b"\x00\x00")

        # Call the underlying protocol method
        return await super().transcribe(body, **kwargs)


__all__: list[str] = [
    "_TranscriptionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
