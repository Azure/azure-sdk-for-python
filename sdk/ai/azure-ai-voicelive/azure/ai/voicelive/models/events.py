# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
Event models for VoiceLive WebSocket connections.
"""

import json
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class EventType(str, Enum):
    """Enum for VoiceLive event types."""
    # Connection events
    CONNECTION_ESTABLISHED = "connection.established"
    CONNECTION_CLOSED = "connection.closed"
    
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    
    # Voice events
    VOICE_INPUT_STARTED = "voice.input.started"
    VOICE_INPUT_ENDED = "voice.input.ended"
    VOICE_OUTPUT_STARTED = "voice.output.started"
    VOICE_OUTPUT_ENDED = "voice.output.ended"
    
    # Recognition events
    RECOGNITION_STARTED = "recognition.started"
    RECOGNITION_RESULT = "recognition.result"
    RECOGNITION_COMPLETED = "recognition.completed"
    
    # Error events
    ERROR = "error"


class BaseEvent:
    """Base class for all VoiceLive events."""
    
    def __init__(self, event_type: EventType, event_id: Optional[str] = None, timestamp: Optional[datetime] = None):
        self.event_type = event_type
        self.event_id = event_id
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the event to a dictionary."""
        return {
            "type": self.event_type,
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_json(self) -> str:
        """Converts the event to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEvent":
        """Creates an event from a dictionary."""
        event_type = data.get("type")
        event_id = data.get("event_id")
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
        
        return cls(event_type=event_type, event_id=event_id, timestamp=timestamp)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseEvent":
        """Creates an event from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class ErrorEvent(BaseEvent):
    """Error event from the VoiceLive service."""
    
    def __init__(
        self, 
        error_code: str, 
        error_message: str, 
        event_id: Optional[str] = None, 
        timestamp: Optional[datetime] = None
    ):
        super().__init__(EventType.ERROR, event_id, timestamp)
        self.error_code = error_code
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the event to a dictionary."""
        data = super().to_dict()
        data.update({
            "error_code": self.error_code,
            "error_message": self.error_message,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorEvent":
        """Creates an error event from a dictionary."""
        error_code = data.get("error_code", "unknown_error")
        error_message = data.get("error_message", "Unknown error occurred")
        event_id = data.get("event_id")
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
        
        return cls(
            error_code=error_code,
            error_message=error_message,
            event_id=event_id,
            timestamp=timestamp
        )


class ConnectionEstablishedEvent(BaseEvent):
    """Event sent when a connection is established."""
    
    def __init__(
        self, 
        session_id: str, 
        event_id: Optional[str] = None, 
        timestamp: Optional[datetime] = None
    ):
        super().__init__(EventType.CONNECTION_ESTABLISHED, event_id, timestamp)
        self.session_id = session_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the event to a dictionary."""
        data = super().to_dict()
        data.update({
            "session_id": self.session_id,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConnectionEstablishedEvent":
        """Creates a connection established event from a dictionary."""
        session_id = data.get("session_id", "")
        event_id = data.get("event_id")
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
        
        return cls(
            session_id=session_id,
            event_id=event_id,
            timestamp=timestamp
        )


class RecognitionResultEvent(BaseEvent):
    """Event sent when a recognition result is available."""
    
    def __init__(
        self,
        text: str,
        is_final: bool,
        confidence: float,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        super().__init__(EventType.RECOGNITION_RESULT, event_id, timestamp)
        self.text = text
        self.is_final = is_final
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the event to a dictionary."""
        data = super().to_dict()
        data.update({
            "text": self.text,
            "is_final": self.is_final,
            "confidence": self.confidence,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecognitionResultEvent":
        """Creates a recognition result event from a dictionary."""
        text = data.get("text", "")
        is_final = data.get("is_final", False)
        confidence = data.get("confidence", 0.0)
        event_id = data.get("event_id")
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
        
        return cls(
            text=text,
            is_final=is_final,
            confidence=confidence,
            event_id=event_id,
            timestamp=timestamp
        )


# Factory function to create events from json data
def create_event_from_json(json_str: str) -> BaseEvent:
    """Creates an appropriate event object based on the event type in the JSON data."""
    data = json.loads(json_str)
    event_type = data.get("type")
    
    if event_type == EventType.ERROR:
        return ErrorEvent.from_dict(data)
    elif event_type == EventType.CONNECTION_ESTABLISHED:
        return ConnectionEstablishedEvent.from_dict(data)
    elif event_type == EventType.RECOGNITION_RESULT:
        return RecognitionResultEvent.from_dict(data)
    else:
        # Default to base event for unspecified event types
        return BaseEvent.from_dict(data)