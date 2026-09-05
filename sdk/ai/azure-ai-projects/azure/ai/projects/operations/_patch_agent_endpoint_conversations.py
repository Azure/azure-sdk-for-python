# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Iterator, Optional, Union
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
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

# All methods on this class always require the VoiceAgents=V1Preview opt-in (voice-agent
# conversation reads), regardless of `allow_preview` -- this class used to live entirely as a
# nested `.beta.agent_endpoint_conversations` sub-client (whose methods were unconditionally
# wrapped with this same header by `_OperationMethodHeaderProxy` in `operations/_patch.py`, since
# merely accessing `.beta` was itself the opt-in signal). Upstream has since merged it entirely
# into this top-level, stable client attribute, but the *service* still requires the same opt-in
# header for every one of these methods -- confirmed empirically: an unauthenticated (no header)
# call to `list_agent_conversations` returns 403 with error.code="preview_feature_required" even
# though the generated SDK surface no longer marks this class as beta. So every method here still
# needs the same `allow_preview`-gated header injection (and, for non-paged methods, the same
# friendlier error message on 403) as every other "optional preview feature on an otherwise-stable
# operation" elsewhere in this SDK (see e.g. `AgentsOperations.generate_agent`).
_VOICE_AGENTS_HEADER_VALUE = _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value


class AgentEndpointConversationsOperations(GeneratedAgentEndpointConversationsOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`agent_endpoint_conversations` attribute.
    """

    @distributed_trace
    def list_agent_conversations(  # type: ignore[override]
        self,
        agent_name: str,
        *,
        limit: Optional[int] = None,
        order: Optional[Union[str, _models.PageOrder]] = None,
        before: Optional[str] = None,
        **kwargs: Any,
    ) -> ItemPaged["_models.VoiceConversation"]:
        """List voice agent conversations.

        Returns the conversations persisted for the specified voice agent endpoint. Conversations are
        present when the session's effective ``store`` setting is ``true``, whether inherited from the
        agent definition or enabled by the WebSocket session override. When the client is constructed
        with ``allow_preview=True``, the required preview opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :keyword limit: A limit on the number of objects to be returned. Limit can range between 1 and
         100, and the
         default is 20. Default value is None.
        :paramtype limit: int
        :keyword order: Sort order by the ``created_at`` timestamp of the objects. ``asc`` for
         ascending order and``desc``
         for descending order. Known values are: "asc" and "desc". Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.PageOrder
        :keyword before: A cursor for use in pagination. ``before`` is an object ID that defines your
         place in the list.
         For instance, if you make a list request and receive 100 objects, ending with obj_foo, your
         subsequent call can include before=obj_foo in order to fetch the previous page of the list.
         Default value is None.
        :paramtype before: str
        :return: An iterator like instance of VoiceConversation
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.VoiceConversation]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        return super().list_agent_conversations(agent_name, limit=limit, order=order, before=before, **kwargs)

    @distributed_trace
    def get_agent_conversation(  # type: ignore[override]
        self, agent_name: str, conversation_id: str, **kwargs: Any
    ) -> _models.VoiceConversation:
        """Get a voice agent conversation.

        Retrieves a single conversation recorded for the specified voice agent endpoint by its id.
        Returns ``404`` when the conversation was not persisted (``store = false``) or does not exist.
        When the client is constructed with ``allow_preview=True``, the required preview opt-in header
        is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation to retrieve. Required.
        :type conversation_id: str
        :return: VoiceConversation. The VoiceConversation is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VoiceConversation
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation(agent_name, conversation_id, **kwargs)
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
    def delete_agent_conversation(  # pylint: disable=inconsistent-return-statements # type: ignore[override]
        self, agent_name: str, conversation_id: str, **kwargs: Any
    ) -> None:
        """Delete a voice agent conversation.

        Deletes a conversation and all of its stored data — responses, items, and any audio (cascade).
        This is the customer's explicit data-deletion control for voice conversations. When the client
        is constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation to delete. Required.
        :type conversation_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().delete_agent_conversation(agent_name, conversation_id, **kwargs)
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
    def list_agent_conversation_responses(  # type: ignore[override]
        self,
        agent_name: str,
        conversation_id: str,
        *,
        limit: Optional[int] = None,
        order: Optional[Union[str, _models.PageOrder]] = None,
        before: Optional[str] = None,
        **kwargs: Any,
    ) -> ItemPaged["_models.VoiceResponse"]:
        """List responses in a voice agent conversation.

        Returns a paged collection of the responses (model inference turns) recorded for the specified
        conversation. The per-response ``output`` projection may be omitted here; use the
        response-items route for the canonical paged output. Returns ``404`` when the conversation was
        not persisted (``store = false``). When the client is constructed with ``allow_preview=True``,
        the required preview opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation whose responses are listed. Required.
        :type conversation_id: str
        :keyword limit: A limit on the number of objects to be returned. Limit can range between 1 and
         100, and the
         default is 20. Default value is None.
        :paramtype limit: int
        :keyword order: Sort order by the ``created_at`` timestamp of the objects. ``asc`` for
         ascending order and``desc``
         for descending order. Known values are: "asc" and "desc". Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.PageOrder
        :keyword before: A cursor for use in pagination. ``before`` is an object ID that defines your
         place in the list.
         For instance, if you make a list request and receive 100 objects, ending with obj_foo, your
         subsequent call can include before=obj_foo in order to fetch the previous page of the list.
         Default value is None.
        :paramtype before: str
        :return: An iterator like instance of VoiceResponse
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.VoiceResponse]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        return super().list_agent_conversation_responses(
            agent_name, conversation_id, limit=limit, order=order, before=before, **kwargs
        )

    @distributed_trace
    def get_agent_conversation_response(  # type: ignore[override]
        self, agent_name: str, conversation_id: str, response_id: str, **kwargs: Any
    ) -> _models.VoiceResponse:
        """Get a voice agent conversation response.

        Retrieves a single response from the specified conversation by its id, including its ``output``
        items, ``usage``, and status. Returns ``404`` when the conversation or response was not
        persisted (``store = false``). When the client is constructed with ``allow_preview=True``, the
        required preview opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation that contains the response. Required.
        :type conversation_id: str
        :param response_id: The id of the response to retrieve. Required.
        :type response_id: str
        :return: VoiceResponse. The VoiceResponse is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VoiceResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_response(agent_name, conversation_id, response_id, **kwargs)
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
    def list_agent_conversation_response_items(  # pylint: disable=name-too-long # type: ignore[override]
        self,
        agent_name: str,
        conversation_id: str,
        response_id: str,
        *,
        limit: Optional[int] = None,
        order: Optional[Union[str, _models.PageOrder]] = None,
        before: Optional[str] = None,
        **kwargs: Any,
    ) -> ItemPaged["_models.RealtimeConversationItem"]:
        """List items produced by a voice agent conversation response.

        Returns a paged collection of the output items produced by a specific response (the response's
        output projection). For the complete ordered conversation history — including user input and
        client-created tool outputs — use the conversation items route instead. Returns ``404`` when
        the conversation or response was not persisted (``store = false``). When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation that contains the response. Required.
        :type conversation_id: str
        :param response_id: The id of the response whose output items are listed. Required.
        :type response_id: str
        :keyword limit: A limit on the number of objects to be returned. Limit can range between 1 and
         100, and the
         default is 20. Default value is None.
        :paramtype limit: int
        :keyword order: Sort order by the ``created_at`` timestamp of the objects. ``asc`` for
         ascending order and``desc``
         for descending order. Known values are: "asc" and "desc". Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.PageOrder
        :keyword before: A cursor for use in pagination. ``before`` is an object ID that defines your
         place in the list.
         For instance, if you make a list request and receive 100 objects, ending with obj_foo, your
         subsequent call can include before=obj_foo in order to fetch the previous page of the list.
         Default value is None.
        :paramtype before: str
        :return: An iterator like instance of RealtimeConversationItem
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.RealtimeConversationItem]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        return super().list_agent_conversation_response_items(
            agent_name, conversation_id, response_id, limit=limit, order=order, before=before, **kwargs
        )

    @distributed_trace
    def list_agent_conversation_items(  # type: ignore[override]
        self,
        agent_name: str,
        conversation_id: str,
        *,
        limit: Optional[int] = None,
        order: Optional[Union[str, _models.PageOrder]] = None,
        before: Optional[str] = None,
        **kwargs: Any,
    ) -> ItemPaged["_models.RealtimeConversationItem"]:
        """List items in a voice agent conversation.

        Returns a paged collection of items — the complete ordered conversation history, including user
        input, assistant output, and client-created tool outputs (transcripts + tool events). Returns
        ``404`` when the conversation was not persisted (``store = false``). When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation whose items are listed. Required.
        :type conversation_id: str
        :keyword limit: A limit on the number of objects to be returned. Limit can range between 1 and
         100, and the
         default is 20. Default value is None.
        :paramtype limit: int
        :keyword order: Sort order by the ``created_at`` timestamp of the objects. ``asc`` for
         ascending order and``desc``
         for descending order. Known values are: "asc" and "desc". Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.PageOrder
        :keyword before: A cursor for use in pagination. ``before`` is an object ID that defines your
         place in the list.
         For instance, if you make a list request and receive 100 objects, ending with obj_foo, your
         subsequent call can include before=obj_foo in order to fetch the previous page of the list.
         Default value is None.
        :paramtype before: str
        :return: An iterator like instance of RealtimeConversationItem
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.RealtimeConversationItem]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        return super().list_agent_conversation_items(
            agent_name, conversation_id, limit=limit, order=order, before=before, **kwargs
        )

    @distributed_trace
    def get_agent_conversation_item(  # type: ignore[override]
        self, agent_name: str, conversation_id: str, item_id: str, **kwargs: Any
    ) -> _models.RealtimeConversationItem:
        """Get a voice agent conversation item.

        Retrieves a single item from the specified conversation by its id, including its transcript. An
        ``input_audio``/``output_audio`` content part indicates that audio is available for the item;
        the canonical per-item audio metadata is the ``/items/{item_id}/audio`` resource, and the bytes
        are streamed by ``/items/{item_id}/audio/content``. Returns ``404`` when the conversation or
        item was not persisted (``store = false``). When the client is constructed with
        ``allow_preview=True``, the required preview opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation that contains the item. Required.
        :type conversation_id: str
        :param item_id: The id of the conversation item to retrieve. Required.
        :type item_id: str
        :return: RealtimeConversationItem. The RealtimeConversationItem is compatible with
         MutableMapping
        :rtype: ~azure.ai.projects.models.RealtimeConversationItem
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_item(agent_name, conversation_id, item_id, **kwargs)
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
    def get_agent_conversation_item_audio(  # pylint: disable=name-too-long # type: ignore[override]
        self, agent_name: str, conversation_id: str, item_id: str, **kwargs: Any
    ) -> _models.VoiceItemAudioResponse:
        """Get a voice agent conversation item's audio metadata.

        Returns metadata for a single conversation item's audio segment, including the common playback
        facts (role, format/codec, sample rate, channels, offset, duration) for both Foundry-managed
        and bring-your-own-storage (BYOS) recordings; for BYOS the response additionally includes
        ``blob_uri``, the URI of the recording in the customer's own storage (no SAS) that the customer
        downloads with their own credentials. Requires the conversation to have persisted audio
        (``store = true``); returns ``404`` when the conversation, item, or its audio was not
        persisted. When the client is constructed with ``allow_preview=True``, the required preview
        opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation that contains the item. Required.
        :type conversation_id: str
        :param item_id: The id of the conversation item whose audio metadata is retrieved. Required.
        :type item_id: str
        :return: VoiceItemAudioResponse. The VoiceItemAudioResponse is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VoiceItemAudioResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_item_audio(agent_name, conversation_id, item_id, **kwargs)
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
    def get_agent_conversation_item_audio_content(  # pylint: disable=name-too-long # type: ignore[override]
        self, agent_name: str, conversation_id: str, item_id: str, **kwargs: Any
    ) -> Iterator[bytes]:
        """Stream a voice agent conversation item's audio.

        Streams a single conversation item's audio as a WAV (``audio/wav``) byte stream through the
        service (no SAS URL). This route serves Foundry-managed storage only. For
        bring-your-own-storage (BYOS) recordings the bytes are not proxied — the caller must download
        directly from customer storage using the ``blob_uri`` returned by the item's ``/audio``
        metadata route — so this route returns ``409 Conflict`` for BYOS recordings. Returns ``404``
        when the conversation, item, or its audio was not persisted (``store = false``). When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation that contains the item. Required.
        :type conversation_id: str
        :param item_id: The id of the conversation item whose audio is streamed. Required.
        :type item_id: str
        :return: Iterator[bytes]
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_item_audio_content(agent_name, conversation_id, item_id, **kwargs)
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

    @distributed_trace
    def get_agent_conversation_audio(  # type: ignore[override]
        self, agent_name: str, conversation_id: str, **kwargs: Any
    ) -> _models.VoiceRecordingResponse:
        """Get a voice agent conversation's merged recording metadata.

        Returns metadata for the whole-call merged stereo recording (user audio on the left channel,
        agent audio on the right). The common metadata (format, sample rate, channels, channel layout,
        duration) is returned for both Foundry-managed and bring-your-own-storage (BYOS) recordings;
        for BYOS the response additionally includes ``blob_uri``, the URI of the recording in the
        customer's own storage (no SAS) that the customer downloads with their own credentials. The
        recording is built once from the per-turn segments after persistence finalization succeeds.
        While the conversation is ``in_progress``, this route returns retriable ``409 Conflict`` with
        ``error.code = recording_not_ready`` and a ``Retry-After`` header when retry guidance is
        available. When the conversation is ``failed``, it returns terminal ``409 Conflict`` with
        ``error.code = recording_unavailable``. For a ``completed`` conversation, metadata is available
        subject to the existing BYOS behavior. Requires the conversation to have persisted audio
        (``store = true``); otherwise returns ``404``. When the client is constructed with
        ``allow_preview=True``, the required preview opt-in header is added automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation whose merged recording metadata is
         retrieved. Required.
        :type conversation_id: str
        :return: VoiceRecordingResponse. The VoiceRecordingResponse is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VoiceRecordingResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_audio(agent_name, conversation_id, **kwargs)
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
    def get_agent_conversation_audio_content(  # type: ignore[override]
        self, agent_name: str, conversation_id: str, **kwargs: Any
    ) -> Iterator[bytes]:
        """Stream a voice agent conversation's merged recording.

        Streams the whole-call merged stereo recording as a WAV (``audio/wav``) byte stream through the
        service (no SAS URL). This route serves Foundry-managed storage only. For
        bring-your-own-storage (BYOS) recordings the bytes are not proxied — the caller must download
        directly from customer storage using the ``blob_uri`` returned by the metadata route — so this
        route returns ``409 Conflict`` for BYOS recordings. While the conversation is ``in_progress``,
        this route returns retriable ``409 Conflict`` with ``error.code = recording_not_ready`` and a
        ``Retry-After`` header when retry guidance is available. When the conversation is ``failed``,
        it returns terminal ``409 Conflict`` with ``error.code = recording_unavailable``. For a
        ``completed`` conversation, content is available subject to the existing BYOS behavior. A
        conversation without persisted audio (``store = false``) returns ``404``. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param conversation_id: The id of the conversation whose merged recording is streamed.
         Required.
        :type conversation_id: str
        :return: Iterator[bytes]
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _VOICE_AGENTS_HEADER_VALUE}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _VOICE_AGENTS_HEADER_VALUE
                kwargs["headers"] = headers

        try:
            return super().get_agent_conversation_audio_content(agent_name, conversation_id, **kwargs)
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
