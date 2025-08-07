# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, List, Optional, Type, Union
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
from ._enums import ServerEventType, ClientEventType

__all__ = [
    "ClientEvent",
    "ServerEvent",
]  # Add all objects you want publicly available to users at this package level

log = logging.getLogger(__name__)


class ClientEvent(ClientEventGenerated):
    """Extended ClientEvent with serialization."""

    @classmethod
    def to_dict(cls, event: "ClientEvent") -> Dict[str, Any]:
        """Recursively convert the event to a JSON-serializable dictionary."""
        result = {"type": event.type}

        if hasattr(event, "event_id") and event.event_id is not None:
            result["event_id"] = event.event_id

        # Include all other public attributes that are not methods or base fields
        for attr in dir(event):
            if attr.startswith("_") or attr in ("type", "event_id") or callable(getattr(event, attr)):
                continue

            value = getattr(event, attr)
            result[attr] = cls._to_jsonable(value)

        return result

    @staticmethod
    def _to_jsonable(obj: Any) -> Any:
        """Convert objects to a JSON-serializable format."""
        if hasattr(obj, "serialize_data"):
            return obj.serialize_data()
        elif isinstance(obj, (list, tuple)):
            return [ClientEvent._to_jsonable(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: ClientEvent._to_jsonable(v) for k, v in obj.items()}
        elif hasattr(obj, "__dict__"):
            return {k: ClientEvent._to_jsonable(v) for k, v in vars(obj).items() if not k.startswith("_")}
        else:
            return obj

    @classmethod
    def serialize(cls, event: "ClientEvent") -> str:
        """Serialize the event to a JSON string."""
        return json.dumps(cls.to_dict(event))


class ServerEvent(ServerEventGenerated):
    """Extended ServerEvent with deserialization."""

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

        # Parse JSON
        data_dict = json.loads(data)

        # Determine the event type
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
        # Determine the event type
        event_type = data.get("type")

        # Map event type to appropriate class
        event_class_map = {
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

        # Get the appropriate class or default to base class
        event_class = event_class_map.get(event_type, cls)

        # Special handling for certain event types
        if event_type in [ServerEventType.SESSION_CREATED, ServerEventType.SESSION_UPDATED]:
            # Extract session data for special handling
            session_data = data.get("session", {})

            # Convert session data to ResponseSession object if not already
            if isinstance(session_data, dict):
                session = ResponseSession(**session_data)
                data["session"] = session

        # Create and return the event instance
        try:
            # Make a copy of the data and remove 'type' to avoid duplicate parameter
            event_data = data.copy()
            if event_type in event_class_map:
                # Remove 'type' for subclasses that already set it via discriminator
                event_data.pop("type", None)

            return event_class(**event_data)
        except TypeError as e:
            log.warning(f"Could not create {event_class.__name__} from data: {e}. Falling back to base class.")
            # Fallback to base class with minimal fields
            return cls(type=event_type, event_id=data.get("event_id"))


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """