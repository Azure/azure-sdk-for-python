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
    RemoveParticipantSucceeded as RemoveParticipantSucceededRest,
    RemoveParticipantFailed as RemoveParticipantFailedRest,
    ContinuousDtmfRecognitionToneReceived as ContinuousDtmfRecognitionToneReceivedRest,
    ContinuousDtmfRecognitionToneFailed as ContinuousDtmfRecognitionToneFailedRest,
    ContinuousDtmfRecognitionStopped as ContinuousDtmfRecognitionStoppedRest,
    SendDtmfCompleted as SendDtmfCompletedRest,
    SendDtmfFailed as SendDtmfFailedRest,
    CallParticipant
)

from ._communication_identifier_serializer import deserialize_identifier

class AddParticipantSucceeded(AddParticipantSucceededRest):
    """Event sent when the participant was successfully added to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar participant: participant that was added to the call.
    :vartype participant: ~azure.communication.callautomation.models.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
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
    """Event sent when the participant was not added successfully to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar participant: participant that was added to the call.
    :vartype participant: ~azure.communication.callautomation.models.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
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
    """Event sent when the call is established.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: CallConnectedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "CallConnected"


class CallDisconnected(CallDisconnectedRest):
    """Event sent when the call is terminated.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: CallDisconnectedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "CallDisconnected"


class CallTransferAccepted(CallTransferAcceptedRest):
    """Event sent when transfer of the call was successful.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: CallTransferAcceptedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "CallTransferAccepted"


class CallTransferFailed(CallTransferFailedRest):
    """Event sent when transfer of the call was not successful.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: CallTransferFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "CallTransferFailed"


class ParticipantsUpdated(ParticipantsUpdatedRest):
    """Event sent when a participant joins, leaves, muted or unmuted.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :vartype operation_context: str
    :ivar participants: List of participants in the call.
    :vartype participants: [~azure.communication.callautomation.models.CallParticipant]
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: ParticipantsUpdatedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.participants = [CallParticipant(identifier=deserialize_identifier(
            participant.identifier), is_muted=participant.is_muted) for participant in parent.participants]
        self.kind = "ParticipantsUpdated"


class RecordingStateChanged(RecordingStateChangedRest):
    """Event sent when recording state changes.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar recording_id: recording id to be used for recording actions.
    :vartype recording_id: str
    :ivar state: state of the call recording.
    :vartype state: RecordingState
    :ivar start_date_time: time the call recording started.
    :vartype start_date_time: startDateTime
    :ivar kind: This event kind.
    :vartype kind: str
    """
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
    """Event sent when media play is completed successfully.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: PlayCompletedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "PlayCompleted"


class PlayFailed(PlayFailedRest):
    """Event sent when media play failed.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: PlayFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "PlayFailed"


class PlayCanceled(PlayCanceledRest):
    """Event sent when media play is cancelled.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: PlayCanceledRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "PlayCanceled"


class RecognizeCompleted(RecognizeCompletedRest):
    """Event sent when recognize is completed successfully.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
     skype chain ID.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
     request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar recognition_type: Determines the sub-type of the recognize operation.
     In case of cancel operation the this field is not set and is returned empty. Known values are:
     "dtmf" and "choices".
    :vartype recognition_type: str or ~azure.communication.callautomation.models.RecognitionType
    :ivar collect_tones_result: Defines the result for RecognitionType = Dtmf.
    :vartype collect_tones_result: ~azure.communication.callautomation.models.CollectTonesResult
    :ivar choice_result: Defines the result for RecognitionType = Choices.
    :vartype choice_result: ~azure.communication.callautomation.models.ChoiceResult
    :ivar kind: This event kind.
    :vartype kind: str
    """
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
    """Event sent when recognize action failed.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: RecognizeFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "RecognizeFailed"


class RecognizeCanceled(RecognizeCanceledRest):
    """Event sent when recognize is cancelled.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: RecognizeCanceledRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.kind = "RecognizeCanceled"


class RemoveParticipantSucceeded(RemoveParticipantSucceededRest):
    """Event sent when the participant was successfully removed to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar participant: participant that was removed to the call.
    :vartype participant: ~azure.communication.callautomation.models.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: RemoveParticipantSucceededRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.participant = deserialize_identifier(parent.participant)
        self.kind = "RemovedParticipantSucceeded"


class RemoveParticipantFailed(RemoveParticipantFailedRest):
    """Event sent when the participant was not removed successfully to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar participant: participant that was removed to the call.
    :vartype participant: ~azure.communication.callautomation.models.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: RemoveParticipantFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.participant = deserialize_identifier(parent.participant)
        self.kind = "RemovedParticipantFailed"


class ContinuousDtmfRecognitionToneReceived(ContinuousDtmfRecognitionToneReceivedRest):
    """Event sent when Dtmf tone received from targeted participant in call.

    :ivar tone_info: Information about Tone.
    :vartype tone_info: ~azure.communication.callautomation.models.ToneInfo
    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId or
     skype chain ID.
    :vartype correlation_id: str
    :ivar result_information: Contains the resulting SIP code/sub-code and message from NGC
     services.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: ContinuousDtmfRecognitionToneReceivedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tone_info = parent.tone_info
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.result_information = parent.result_information
        self.kind = "ContinuousDtmfRecognitionToneReceived"


class ContinuousDtmfRecognitionToneFailed(ContinuousDtmfRecognitionToneFailedRest):
    """Event sent when failed to start continuous Dtmf recognition.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
     skype chain ID.
    :vartype correlation_id: str
    :ivar result_information: Contains the resulting SIP code/sub-code and message from NGC
     services.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: ContinuousDtmfRecognitionToneFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.result_information = parent.result_information
        self.kind = "ContinuousDtmfRecognitionToneFailed"


class ContinuousDtmfRecognitionStopped(ContinuousDtmfRecognitionStoppedRest):
    """Event sent when start continuous Dtmf recognition stopped.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
     skype chain ID.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
     request to the response event.
    :vartype operation_context: str
    :ivar result_information: Contains the resulting SIP code/sub-code and message from NGC
     services.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: ContinuousDtmfRecognitionStoppedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "ContinuousDtmfRecognitionStopped"


class SendDtmfCompleted(SendDtmfCompletedRest):
    """Event sent when Dtmf tones send completed successfully.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
     skype chain ID.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
     request to the response event.
    :vartype operation_context: str
    :ivar result_information: Contains the resulting SIP code/sub-code and message from NGC
     services.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: SendDtmfCompletedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "SendDtmfCompleted"


class SendDtmfFailed(SendDtmfFailedRest):
    """Event sent when Dtmf tones send failed.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
     skype chain ID.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
     request to the response event.
    :vartype operation_context: str
    :ivar result_information: Contains the resulting SIP code/sub-code and message from NGC
     services.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(self, parent: SendDtmfFailedRest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_connection_id = parent.call_connection_id
        self.server_call_id = parent.server_call_id
        self.correlation_id = parent.correlation_id
        self.operation_context = parent.operation_context
        self.result_information = parent.result_information
        self.kind = "SendDtmfFailed"
