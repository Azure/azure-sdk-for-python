# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models import (
    AddParticipantSucceeded as AddParticipantSucceededRest,
    AddParticipantFailed as AddParticipantFailedRest,
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
    RecognizeFailed as RecognizeFailedRest,
    CallParticipant
)

from ._models import deserialize_identifier


class AddParticipantSucceeded(AddParticipantSucceededRest):
    def __init__(self, parent: AddParticipantSucceededRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.participant = deserialize_identifier(parent.participant)
        self.kind = "AddParticipantSucceeded"


class AddParticipantFailed(AddParticipantFailedRest):
    def __init__(self, parent: AddParticipantFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.participant = deserialize_identifier(parent.participant)
        self.kind = "AddParticipantFailed"


class CallConnected(CallConnectedRest):
    def __init__(self, parent: CallConnectedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "CallConnected"


class CallDisconnected(CallDisconnectedRest):
    def __init__(self, parent: CallDisconnectedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "CallDisconnected"


class CallTransferAccepted(CallTransferAcceptedRest):
    def __init__(self, parent: CallTransferAcceptedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "CallTransferAccepted"


class CallTransferFailed(CallTransferFailedRest):
    def __init__(self, parent: CallTransferFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "CallTransferFailed"


class ParticipantsUpdated(ParticipantsUpdatedRest):
    def __init__(self, parent: ParticipantsUpdatedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.participants = [CallParticipant(identifier=deserialize_identifier(
            participant.identifier), is_muted=participant.is_muted) for participant in parent.participants]
        self.kind = "ParticipantsUpdated"


class RecordingStateChanged(RecordingStateChangedRest):
    def __init__(self, parent: RecordingStateChangedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.recording_id = parent.recording_id
        self.state = parent.state
        self.start_date_time = parent.start_date_time
        self.kind = "RecordingStateChanged"


class PlayCompleted(PlayCompletedRest):
    def __init__(self, parent: PlayCompletedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "PlayCompleted"


class PlayFailed(PlayFailedRest):
    def __init__(self, parent: PlayFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "PlayFailed"


class PlayCanceled(PlayCanceledRest):
    def __init__(self, parent: PlayCanceledRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "PlayCanceled"


class RecognizeCompleted(RecognizeCompletedRest):
    def __init__(self, parent: RecognizeCompletedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.recognition_type = parent.recognition_type
        self.collect_tones_result = parent.collect_tones_result
        self.choice_result = parent.choice_result
        self.kind = "RecognizeCompleted"


class RecognizeFailed(RecognizeFailedRest):
    def __init__(self, parent: RecognizeFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "RecognizeFailed"


class RecognizeCanceled(RecognizeCanceledRest):
    def __init__(self, parent: RecognizeCanceledRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "RecognizeCanceled"
