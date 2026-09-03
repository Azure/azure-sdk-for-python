# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Iterator
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from ._operations import AgentEndpointConversationsOperations as GeneratedAgentEndpointConversationsOperations
from .. import models as _models
from ..models._enums import _AgentDefinitionOptInKeys
from ..models._patch import (
    _FOUNDRY_FEATURES_HEADER_NAME,
    _has_header_case_insensitive,
    _PREVIEW_FEATURE_REQUIRED_CODE,
    _PREVIEW_FEATURE_ADDED_ERROR_MESSAGE,
)


class AgentEndpointConversationsOperations(GeneratedAgentEndpointConversationsOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`agent_endpoint_conversations` attribute.
    """

    @distributed_trace
    def get_agent_conversation_item_generated_audio(  # pylint: disable=name-too-long # type: ignore[override]
        self, agent_name: str, conversation_id: str, item_id: str, **kwargs: Any
    ) -> _models.VoiceGeneratedItemAudioResponse:
        """Get a voice agent conversation item's generated audio metadata.

        Returns metadata for a conversation item's generated audio. This subordinate artifact is
        separate from the canonical heard-audio segment and exists only when playback was interrupted
        and the service rendered more audio than the listener heard, including when the response ends
        as cancelled. Returns ``404`` when the conversation or item was not persisted, or when no
        generated audio exists beyond the heard segment. When the client is constructed with
        ``allow_preview=True``, the required preview opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation that contains the item. Required.
        :type conversation_id: str
        :param item_id: The id of the conversation item whose generated audio metadata is retrieved.
         Required.
        :type item_id: str
        :return: VoiceGeneratedItemAudioResponse. The VoiceGeneratedItemAudioResponse is compatible
         with MutableMapping
        :rtype: ~azure.ai.projects.models.VoiceGeneratedItemAudioResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            # Add Foundry-Features header if not already present
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {
                    _FOUNDRY_FEATURES_HEADER_NAME: _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value
                }
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_item_generated_audio(agent_name, conversation_id, item_id, **kwargs)
        except HttpResponseError as exc:
            if exc.status_code == 403 and not self._config.allow_preview and exc.model is not None:
                api_error_response = exc.model
                if hasattr(api_error_response, "error") and api_error_response.error is not None:
                    if api_error_response.error.code == _PREVIEW_FEATURE_REQUIRED_CODE:
                        new_exc = HttpResponseError(
                            message=f"{exc.message} {_PREVIEW_FEATURE_ADDED_ERROR_MESSAGE}",
                        )
                        new_exc.status_code = exc.status_code
                        new_exc.reason = exc.reason
                        new_exc.response = exc.response
                        new_exc.model = exc.model
                        raise new_exc from exc
            raise

    @distributed_trace
    def get_agent_conversation_item_generated_audio_content(  # pylint: disable=name-too-long # type: ignore[override]
        self, agent_name: str, conversation_id: str, item_id: str, **kwargs: Any
    ) -> Iterator[bytes]:
        """Stream a voice agent conversation item's generated audio.

        Streams a conversation item's generated audio as a WAV (``audio/wav``) byte stream through the
        service. This subordinate artifact exists only when playback was interrupted and the service
        rendered more audio than the listener heard, including when the response ends as cancelled.
        This route serves Foundry-managed storage only. For bring-your-own-storage (BYOS) recordings
        the bytes are not proxied, so this route returns ``409 Conflict``. Returns ``404`` when the
        conversation or item was not persisted, or when no generated audio exists beyond the heard
        segment. When the client is constructed with ``allow_preview=True``, the required preview
        opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation that contains the item. Required.
        :type conversation_id: str
        :param item_id: The id of the conversation item whose generated audio is streamed. Required.
        :type item_id: str
        :return: Iterator[bytes]
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {
                    _FOUNDRY_FEATURES_HEADER_NAME: _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value
                }
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_item_generated_audio_content(
                agent_name, conversation_id, item_id, **kwargs
            )
        except HttpResponseError as exc:
            if exc.status_code == 403 and not self._config.allow_preview and exc.model is not None:
                api_error_response = exc.model
                if hasattr(api_error_response, "error") and api_error_response.error is not None:
                    if api_error_response.error.code == _PREVIEW_FEATURE_REQUIRED_CODE:
                        new_exc = HttpResponseError(
                            message=f"{exc.message} {_PREVIEW_FEATURE_ADDED_ERROR_MESSAGE}",
                        )
                        new_exc.status_code = exc.status_code
                        new_exc.reason = exc.reason
                        new_exc.response = exc.response
                        new_exc.model = exc.model
                        raise new_exc from exc
            raise
