# pylint: disable=line-too-long,useless-suppression
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
import json
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import map_error, HttpResponseError, ClientAuthenticationError, ResourceNotFoundError, ResourceExistsError, ResourceNotModifiedError

from ... import models as _models
from ..._utils.model_base import _deserialize, SdkJSONEncoder
from ..._operations._operations import build_transcription_transcribe_request
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

        # Send as multipart request with only definition (no audio file)
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        _headers["Accept"] = "application/json"

        # Serialize definition as JSON string for multipart
        definition_json = json.dumps(options.as_dict(), cls=SdkJSONEncoder, exclude_readonly=True)

        # Build multipart request - pass definition through files to ensure multipart encoding
        # The definition needs to be in files list with explicit content-type to trigger multipart/form-data
        _request = build_transcription_transcribe_request(
            api_version=self._config.api_version,
            files=[("definition", (None, definition_json, "application/json"))],
            headers=_headers,
        )

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        pipeline_response = await self._client._pipeline.run(_request, stream=False, **kwargs)  # pylint: disable=protected-access
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = _deserialize(_models.TranscriptionResult, response.json())
        return deserialized


__all__: list[str] = [
    "_TranscriptionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
