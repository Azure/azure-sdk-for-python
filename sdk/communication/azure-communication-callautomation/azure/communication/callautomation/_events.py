# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models import (
    AddParticipantsSucceeded as AddParticipantsSucceededRest,
    AddParticipantsFailed as AddParticipantsFailedRest,
    CallConnected as CallConnectedRest,
    CallDisconnected as CallDisconnectedRest,
    CallTransferAccepted as CallTransferAcceptedRest,
    CallTransferFailed as CallTransferFailedRest,
    ParticipantsUpdated as ParticipantsUpdatedRest,
    RecordingStateChanged as RecordingStateChangedRest,
    PlayCompleted as PlayCompletedRest,
    PlayFailed as PlayFailedRest,
    PlayCanceled as PlayCanceledRest,
    RecognizeCompleted as RecognizeCompletedRest,
    RecognizeCanceled as RecognizeCanceledRest,
    RecognizeFailed as RecognizeFailedRest
)

from ._communication_identifier_serializer import (
    CommunicationIdentifier,
    deserialize_identifier_from_dict
)

from typing import (
    Dict,
    Any,
    cast,
    Optional,
    Union,
    AnyStr,
    IO,
    Mapping,
    Callable,
    TypeVar,
    MutableMapping,
    Type,
    List,
    Mapping,
)

class AddParticipantsSucceeded(AddParticipantsSucceededRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "AddParticipantsSucceeded"

class AddParticipantsFailed(AddParticipantsFailedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "AddParticipantsFailed"

class CallConnected(CallConnectedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "CallConnected"

class CallDisconnected(CallDisconnectedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "CallDisconnected"

class CallTransferAccepted(CallTransferAcceptedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "CallTransferAccepted"

class CallTransferFailed(CallTransferFailedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "CallTransferFailed"

class ParticipantsUpdated(ParticipantsUpdatedRest):
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        participants: Optional[List["CommunicationIdentifier"]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.participants = participants
        self.kind = "ParticipantsUpdated"

    _attribute_map = {
        "call_connection_id": {"key": "callConnectionId", "type": "str"},
        "server_call_id": {"key": "serverCallId", "type": "str"},
        "correlation_id": {"key": "correlationId", "type": "str"},
        "participants": {"key": "participants", "type": "object"},
    }

    @classmethod
    def deserialize(cls: "ParticipantsUpdated", data: Any, content_type: Optional[str] = None) -> "ParticipantsUpdated":
        """Parse a str using the RestAPI syntax and return a model.

        :param str data: A str using RestAPI structure. JSON by default.
        :param str content_type: JSON by default, set application/xml if XML.
        :returns: An instance of this model
        :raises: DeserializationError if something went wrong
        """
        event_with_obj = super(ParticipantsUpdatedRest, cls).deserialize(data, content_type)
        event_with_obj.participants = [deserialize_identifier_from_dict(participant) for participant in event_with_obj.participants]

        return event_with_obj

class RecordingStateChanged(RecordingStateChangedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "RecordingStateChanged"

class PlayCompleted(PlayCompletedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "PlayCompleted"

class PlayFailed(PlayFailedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "PlayFailed"

class PlayCanceled(PlayCanceledRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "PlayCanceled"

class RecognizeCompleted(RecognizeCompletedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "RecognizeCompleted"

class RecognizeCanceled(RecognizeCanceledRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "RecognizeCanceled"

class RecognizeFailed(RecognizeFailedRest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = "RecognizeFailed"