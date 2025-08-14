# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, Optional, Type, Union, cast
import json
import logging

# Import the generated classes
from ._models import (
    ClientEvent as ClientEventGenerated,
    ServerEvent as ServerEventGenerated,
    ServerEventSessionCreated,
    ServerEventSessionUpdated,
    ServerEventError,
    ServerEventResponseTextDelta,
    ServerEventResponseAudioDelta,
    ServerEventConversationItemCreated,
    ServerEventConversationItemDeleted,
    ServerEventConversationItemRetrieved,
    ServerEventConversationItemTruncated,
    ServerEventConversationItemInputAudioTranscriptionCompleted,
    ServerEventConversationItemInputAudioTranscriptionDelta,
    ServerEventConversationItemInputAudioTranscriptionFailed,
    ServerEventInputAudioBufferCommitted,
    ServerEventInputAudioBufferCleared,
    ServerEventInputAudioBufferSpeechStarted,
    ServerEventInputAudioBufferSpeechStopped,
    ServerEventResponseCreated,
    ServerEventResponseDone,
    ServerEventResponseOutputItemAdded,
    ServerEventResponseOutputItemDone,
    ServerEventResponseContentPartAdded,
    ServerEventResponseContentPartDone,
    ServerEventResponseTextDone,
    ServerEventResponseAudioTranscriptDelta,
    ServerEventResponseAudioTranscriptDone,
    ServerEventResponseAudioDone,
    ResponseSession,
)
from ._enums import ServerEventType

__all__ = [
    "ClientEvent",
    "ServerEvent",
]  # Add all objects you want publicly available to users at this package level

log = logging.getLogger(__name__)


class ClientEvent(ClientEventGenerated):
    """Extended ClientEvent with serialization."""

    @classmethod
    def to_dict(cls, event: "ClientEvent") -> Dict[str, Any]:
        """Recursively convert the event to a JSON-serializable dictionary.

        :param event: The ClientEvent instance to convert.
        :type event: ~azure.ai.voicelive.models.ClientEvent
        :return: A dictionary representation of the event.
        :rtype: Dict[str, Any]
        """
        result = {"type": event.type}

        if hasattr(event, "event_id") and event.event_id is not None:
            result["event_id"] = event.event_id

        for attr in dir(event):
            if attr.startswith("_") or attr in ("type", "event_id") or callable(getattr(event, attr)):
                continue
            value = getattr(event, attr)
            result[attr] = cls._to_jsonable(value)

        return result

    @staticmethod
    def _to_jsonable(obj: Any) -> Any:
        """Convert an object to a JSON-serializable format.

        :param obj: The object to convert.
        :type obj: Any
        :return: A JSON-serializable representation of the object.
        :rtype: Any
        """
        if hasattr(obj, "serialize_data"):
            return obj.serialize_data()
        if isinstance(obj, (list, tuple)):
            return [ClientEvent._to_jsonable(v) for v in obj]
        if isinstance(obj, dict):
            return {k: ClientEvent._to_jsonable(v) for k, v in obj.items()}
        if hasattr(obj, "__dict__"):
            return {k: ClientEvent._to_jsonable(v) for k, v in vars(obj).items() if not k.startswith("_")}
        return obj

    @classmethod
    def serialize(cls, event: "ClientEvent") -> str:
        """Serialize the event to a JSON string.

        :param event: The ClientEvent instance to serialize.
        :type event: ~azure.ai.voicelive.models.ClientEvent
        :return: A JSON string representation of the event.
        :rtype: str
        """
        return json.dumps(cls.to_dict(event))


class ServerEvent(ServerEventGenerated):
    """Extended ServerEvent with deserialization."""

    @staticmethod
    def _normalize_event_type(raw: Any) -> Optional[ServerEventType]:
        """Convert an incoming 'type' value to ServerEventType or None.

        :param raw: The raw type value (string, enum, or other) to normalize.
        :type raw: Any
        :return: A ServerEventType if recognized, otherwise None.
        :rtype: Optional[~azure.ai.voicelive.models.ServerEventType]
        """
        if isinstance(raw, ServerEventType):
            return raw
        if isinstance(raw, str):
            try:
                return ServerEventType(raw)
            except ValueError:
                return None
        return None

    @classmethod
    def deserialize(cls, data: Union[str, bytes]) -> "ServerEvent":
        """Deserialize a JSON string or bytes to a ServerEvent.

        :param data: JSON string or bytes to deserialize.
        :type data: Union[str, bytes]
        :return: A ServerEvent instance.
        :rtype: ~azure.ai.voicelive.models.ServerEvent
        :raises ValueError: If the data is not valid JSON or the event type is not recognized.
        """
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        data_dict = json.loads(data)

        event_type = data_dict.get("type")
        if not event_type:
            raise ValueError("Event data is missing 'type' field")

        return cls.from_dict(data_dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerEvent":
        """Create an event instance from a dictionary.

        :param data: Dictionary containing event data.
        :type data: Dict[str, Any]
        :return: A ServerEvent instance.
        :rtype: ~azure.ai.voicelive.models.ServerEvent
        """
        raw_type: Any = data.get("type")
        event_type = cls._normalize_event_type(raw_type)

        event_class_map: Dict[ServerEventType, Type[Any]] = {
            ServerEventType.SESSION_CREATED: ServerEventSessionCreated,
            ServerEventType.SESSION_UPDATED: ServerEventSessionUpdated,
            ServerEventType.ERROR: ServerEventError,
            ServerEventType.RESPONSE_TEXT_DELTA: ServerEventResponseTextDelta,
            ServerEventType.RESPONSE_AUDIO_DELTA: ServerEventResponseAudioDelta,
            ServerEventType.CONVERSATION_ITEM_CREATED: ServerEventConversationItemCreated,
            ServerEventType.CONVERSATION_ITEM_DELETED: ServerEventConversationItemDeleted,
            ServerEventType.CONVERSATION_ITEM_RETRIEVED: ServerEventConversationItemRetrieved,
            ServerEventType.CONVERSATION_ITEM_TRUNCATED: ServerEventConversationItemTruncated,
            ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED: ServerEventConversationItemInputAudioTranscriptionCompleted,
            ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA: ServerEventConversationItemInputAudioTranscriptionDelta,
            ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED: ServerEventConversationItemInputAudioTranscriptionFailed,
            ServerEventType.INPUT_AUDIO_BUFFER_COMMITTED: ServerEventInputAudioBufferCommitted,
            ServerEventType.INPUT_AUDIO_BUFFER_CLEARED: ServerEventInputAudioBufferCleared,
            ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED: ServerEventInputAudioBufferSpeechStarted,
            ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED: ServerEventInputAudioBufferSpeechStopped,
            ServerEventType.RESPONSE_CREATED: ServerEventResponseCreated,
            ServerEventType.RESPONSE_DONE: ServerEventResponseDone,
            ServerEventType.RESPONSE_OUTPUT_ITEM_ADDED: ServerEventResponseOutputItemAdded,
            ServerEventType.RESPONSE_OUTPUT_ITEM_DONE: ServerEventResponseOutputItemDone,
            ServerEventType.RESPONSE_CONTENT_PART_ADDED: ServerEventResponseContentPartAdded,
            ServerEventType.RESPONSE_CONTENT_PART_DONE: ServerEventResponseContentPartDone,
            ServerEventType.RESPONSE_TEXT_DONE: ServerEventResponseTextDone,
            ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA: ServerEventResponseAudioTranscriptDelta,
            ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE: ServerEventResponseAudioTranscriptDone,
            ServerEventType.RESPONSE_AUDIO_DONE: ServerEventResponseAudioDone,
        }

        if event_type is None:
            event_class: Type[Any] = cls
        else:
            event_class = cast(Type[Any], event_class_map.get(event_type, cls))

        if event_type is not None and event_type in (ServerEventType.SESSION_CREATED, ServerEventType.SESSION_UPDATED):
            session_data = data.get("session", {})
            if isinstance(session_data, dict):
                data["session"] = ResponseSession(**session_data)

        try:
            event_data = data.copy()
            if event_type is not None and event_type in event_class_map:
                event_data.pop("type", None)
            return event_class(**event_data)
        except TypeError as e:
            log.warning(
                "Could not create %s from data: %s. Falling back to base class.",
                event_class.__name__,
                e,
            )
            type_str: str = (
                raw_type if isinstance(raw_type, str)
                else (raw_type.value if isinstance(raw_type, ServerEventType) else "")
            )
            return cls(type=type_str, event_id=data.get("event_id"))


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
