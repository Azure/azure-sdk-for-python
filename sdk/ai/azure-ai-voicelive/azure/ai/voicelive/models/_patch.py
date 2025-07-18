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
    VoiceLiveClientEvent as VoiceLiveClientEventGenerated,
    VoiceLiveServerEvent as VoiceLiveServerEventGenerated,
    VoiceLiveServerEventSessionCreated,
    VoiceLiveServerEventSessionUpdated,
    VoiceLiveServerEventError,
    VoiceLiveServerEventResponseTextDelta,
    VoiceLiveServerEventResponseAudioDelta,
    VoiceLiveServerEventConversationItemCreated,
    VoiceLiveServerEventConversationItemDeleted,
    VoiceLiveServerEventConversationItemRetrieved,
    VoiceLiveServerEventConversationItemTruncated,
    VoiceLiveServerEventConversationItemInputAudioTranscriptionCompleted,
    VoiceLiveServerEventConversationItemInputAudioTranscriptionDelta,
    VoiceLiveServerEventConversationItemInputAudioTranscriptionFailed,
    VoiceLiveServerEventInputAudioBufferCommitted,
    VoiceLiveServerEventInputAudioBufferCleared,
    VoiceLiveServerEventInputAudioBufferSpeechStarted,
    VoiceLiveServerEventInputAudioBufferSpeechStopped,
    VoiceLiveServerEventResponseCreated,
    VoiceLiveServerEventResponseDone,
    VoiceLiveServerEventResponseOutputItemAdded,
    VoiceLiveServerEventResponseOutputItemDone,
    VoiceLiveServerEventResponseContentPartAdded,
    VoiceLiveServerEventResponseContentPartDone,
    VoiceLiveServerEventResponseTextDone,
    VoiceLiveServerEventResponseAudioTranscriptDelta,
    VoiceLiveServerEventResponseAudioTranscriptDone,
    VoiceLiveServerEventResponseAudioDone,
    VoiceLiveResponseSession,
)
from ._enums import VoiceLiveServerEventType, VoiceLiveClientEventType

__all__: List[str] = [
    "VoiceLiveClientEvent",
    "VoiceLiveServerEvent",
]  # Add all objects you want publicly available to users at this package level

log = logging.getLogger(__name__)


class VoiceLiveClientEvent(VoiceLiveClientEventGenerated):
    """Extended VoiceLiveClientEvent with serialization."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary.

        :return: Dictionary representation of the event.
        :rtype: Dict[str, Any]
        """
        result = {"type": self.type}

        # Add event_id if present
        if hasattr(self, "event_id") and self.event_id is not None:
            result["event_id"] = self.event_id

        # Add specific fields based on event type
        if self.type == VoiceLiveClientEventType.SESSION_UPDATE:
            result["session"] = {}
            if hasattr(self, "session") and self.session is not None:
                # Use Model's serialize_data if available, otherwise convert to dict manually
                if hasattr(self.session, "serialize_data"):
                    result["session"] = self.session.serialize_data()
                else:
                    # Include all public properties
                    for attr in dir(self.session):
                        if not attr.startswith("_") and not callable(getattr(self.session, attr)):
                            value = getattr(self.session, attr)
                            if value is not None:
                                result["session"][attr] = value

        return result

    def serialize(self) -> str:
        """Serialize the event to JSON.

        :return: JSON string representation of the event.
        :rtype: str
        """
        return json.dumps(self.to_dict())


class VoiceLiveServerEvent(VoiceLiveServerEventGenerated):
    """Extended VoiceLiveServerEvent with deserialization."""

    @classmethod
    def deserialize(cls, data: Union[str, bytes]) -> "VoiceLiveServerEvent":
        """Deserialize a JSON string or bytes to a VoiceLiveServerEvent.

        :param data: JSON string or bytes to deserialize.
        :type data: Union[str, bytes]
        :return: A VoiceLiveServerEvent instance.
        :rtype: ~azure.ai.voicelive.models.VoiceLiveServerEvent
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
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceLiveServerEvent":
        """Create an event instance from a dictionary.

        :param data: Dictionary containing event data.
        :type data: Dict[str, Any]
        :return: A VoiceLiveServerEvent instance.
        :rtype: ~azure.ai.voicelive.models.VoiceLiveServerEvent
        """
        # Determine the event type
        event_type = data.get("type")

        # Map event type to appropriate class
        event_class_map = {
            VoiceLiveServerEventType.SESSION_CREATED: VoiceLiveServerEventSessionCreated,
            VoiceLiveServerEventType.SESSION_UPDATED: VoiceLiveServerEventSessionUpdated,
            VoiceLiveServerEventType.ERROR: VoiceLiveServerEventError,
            VoiceLiveServerEventType.RESPONSE_TEXT_DELTA: VoiceLiveServerEventResponseTextDelta,
            VoiceLiveServerEventType.RESPONSE_AUDIO_DELTA: VoiceLiveServerEventResponseAudioDelta,
            VoiceLiveServerEventType.CONVERSATION_ITEM_CREATED: VoiceLiveServerEventConversationItemCreated,
            VoiceLiveServerEventType.CONVERSATION_ITEM_DELETED: VoiceLiveServerEventConversationItemDeleted,
            VoiceLiveServerEventType.CONVERSATION_ITEM_RETRIEVED: VoiceLiveServerEventConversationItemRetrieved,
            VoiceLiveServerEventType.CONVERSATION_ITEM_TRUNCATED: VoiceLiveServerEventConversationItemTruncated,
            VoiceLiveServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED: VoiceLiveServerEventConversationItemInputAudioTranscriptionCompleted,
            VoiceLiveServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA: VoiceLiveServerEventConversationItemInputAudioTranscriptionDelta,
            VoiceLiveServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED: VoiceLiveServerEventConversationItemInputAudioTranscriptionFailed,
            VoiceLiveServerEventType.INPUT_AUDIO_BUFFER_COMMITTED: VoiceLiveServerEventInputAudioBufferCommitted,
            VoiceLiveServerEventType.INPUT_AUDIO_BUFFER_CLEARED: VoiceLiveServerEventInputAudioBufferCleared,
            VoiceLiveServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED: VoiceLiveServerEventInputAudioBufferSpeechStarted,
            VoiceLiveServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED: VoiceLiveServerEventInputAudioBufferSpeechStopped,
            VoiceLiveServerEventType.RESPONSE_CREATED: VoiceLiveServerEventResponseCreated,
            VoiceLiveServerEventType.RESPONSE_DONE: VoiceLiveServerEventResponseDone,
            VoiceLiveServerEventType.RESPONSE_OUTPUT_ITEM_ADDED: VoiceLiveServerEventResponseOutputItemAdded,
            VoiceLiveServerEventType.RESPONSE_OUTPUT_ITEM_DONE: VoiceLiveServerEventResponseOutputItemDone,
            VoiceLiveServerEventType.RESPONSE_CONTENT_PART_ADDED: VoiceLiveServerEventResponseContentPartAdded,
            VoiceLiveServerEventType.RESPONSE_CONTENT_PART_DONE: VoiceLiveServerEventResponseContentPartDone,
            VoiceLiveServerEventType.RESPONSE_TEXT_DONE: VoiceLiveServerEventResponseTextDone,
            VoiceLiveServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA: VoiceLiveServerEventResponseAudioTranscriptDelta,
            VoiceLiveServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE: VoiceLiveServerEventResponseAudioTranscriptDone,
            VoiceLiveServerEventType.RESPONSE_AUDIO_DONE: VoiceLiveServerEventResponseAudioDone,
        }

        # Get the appropriate class or default to base class
        event_class = event_class_map.get(event_type, cls)

        # Special handling for certain event types
        if event_type in [VoiceLiveServerEventType.SESSION_CREATED, VoiceLiveServerEventType.SESSION_UPDATED]:
            # Extract session data for special handling
            session_data = data.get("session", {})

            # Convert session data to VoiceLiveResponseSession object if not already
            if isinstance(session_data, dict):
                session = VoiceLiveResponseSession(**session_data)
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
