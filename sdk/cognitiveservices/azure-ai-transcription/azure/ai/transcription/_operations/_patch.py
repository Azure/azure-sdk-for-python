# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping
from typing import Any, Optional, Union
from azure.core.tracing.decorator import distributed_trace

from .. import models as _models
from ._operations import _TranscriptionClientOperationsMixin as _TranscriptionClientOperationsMixinGenerated

JSON = MutableMapping[str, Any]


class _TranscriptionClientOperationsMixin(_TranscriptionClientOperationsMixinGenerated):
    """Custom operations mixin for TranscriptionClient."""

    @distributed_trace
    def transcribe_from_url(
        self,
        audio_url: str,
        *,
        locales: Optional[list[str]] = None,
        models: Optional[dict[str, str]] = None,
        profanity_filter_mode: Optional[Union[str, _models.ProfanityFilterMode]] = None,
        diarization_options: Optional[_models.TranscriptionDiarizationOptions] = None,
        active_channels: Optional[list[int]] = None,
        enhanced_mode: Optional[_models.EnhancedModeProperties] = None,
        phrase_list: Optional[_models.PhraseListProperties] = None,
        **kwargs: Any
    ) -> _models.TranscriptionResult:
        """Transcribes audio from a URL.

        Use this method when the audio is hosted at a URL that the service can access.
        For transcribing local audio files or byte streams, use :meth:`transcribe` instead.

        :param audio_url: The URL of the audio file to transcribe. The audio must be shorter than 2
         hours in duration and smaller than 250 MB in size. Required.
        :type audio_url: str
        :keyword locales: A list of possible locales for the transcription. If not specified, the
         locale is detected automatically.
        :paramtype locales: list[str]
        :keyword models: Maps candidate locales to a model URI to be used for transcription.
        :paramtype models: dict[str, str]
        :keyword profanity_filter_mode: Mode of profanity filtering. Known values are: "None",
         "Removed", "Tags", and "Masked".
        :paramtype profanity_filter_mode: str or ~azure.ai.transcription.models.ProfanityFilterMode
        :keyword diarization_options: Speaker diarization settings.
        :paramtype diarization_options: ~azure.ai.transcription.models.TranscriptionDiarizationOptions
        :keyword active_channels: The 0-based indices of channels to transcribe separately.
        :paramtype active_channels: list[int]
        :keyword enhanced_mode: Enhanced mode properties.
        :paramtype enhanced_mode: ~azure.ai.transcription.models.EnhancedModeProperties
        :keyword phrase_list: Phrase list properties.
        :paramtype phrase_list: ~azure.ai.transcription.models.PhraseListProperties
        :return: TranscriptionResult with the transcription text and phrases.
        :rtype: ~azure.ai.transcription.models.TranscriptionResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Create options with the audio URL
        options = _models.TranscriptionOptions(
            audio_url=audio_url,
            locales=locales,
            models=models,
            profanity_filter_mode=profanity_filter_mode,
            diarization_options=diarization_options,
            active_channels=active_channels,
            enhanced_mode=enhanced_mode,
            phrase_list=phrase_list,
        )

        # Create request content without audio file (service will fetch from URL)
        body = _models.TranscribeRequestContent(options=options, audio=None)

        # Call the underlying protocol method
        return super().transcribe(body, **kwargs)


__all__: list[str] = [
    "_TranscriptionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
