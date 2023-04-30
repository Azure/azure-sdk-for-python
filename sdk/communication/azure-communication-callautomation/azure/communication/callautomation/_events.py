# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines
from typing import List, Optional, TYPE_CHECKING
from ._models import (
    ResultInformation,
    CallParticipant,
    ChoiceResult,
    CollectTonesResult,
    ToneInfo
)
from ._utils import deserialize_identifier
if TYPE_CHECKING:
    from datetime import datetime
    from ._shared.models import (
        CommunicationIdentifier
    )
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
        SendDtmfFailed as SendDtmfFailedRest
    )
    from ._generated.models._enums import (
        RecordingState,
        RecognitionType
    )

class AddParticipantSucceededEventData(object):
    """Call Automation callback event sent when the participant was successfully added to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar participant: participant that was added to the call.
    :vartype participant: ~azure.communication.callautomation._shared.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        participant: Optional['CommunicationIdentifier'] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.participant = participant
        self.kind = "AddParticipantSucceededEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'AddParticipantSucceededRest'
    ) -> 'AddParticipantSucceededEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information),
            participant=CallParticipant._from_generated(# pylint:disable=protected-access
            generated_model.participant))


class AddParticipantFailedEventData(object):
    """Event sent when the participant was not added successfully to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar participant: participant that was added to the call.
    :vartype participant: ~azure.communication.callautomation.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        participant: Optional['CommunicationIdentifier'] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.participant = participant
        self.kind = "AddParticipantFailedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'AddParticipantFailedRest'
    ) -> 'AddParticipantFailedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information),
            participant=CallParticipant._from_generated(# pylint:disable=protected-access
            generated_model.participant))


class CallConnectedEventData(object):
    """Event sent when the call is established.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.kind = "CallConnectedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'CallConnectedRest'
    ) -> 'CallConnectedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context)


class CallDisconnectedEventData(object):
    """Event sent when the call is terminated.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.kind = "CallDisconnectedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'CallDisconnectedRest'
    ) -> 'CallDisconnectedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context)


class CallTransferAcceptedEventData(object):
    """Event sent when transfer of the call was successful.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "CallTransferAcceptedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'CallTransferAcceptedRest'
    ) -> 'CallTransferAcceptedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))

class CallTransferFailedEventData(object):
    """Event sent when transfer of the call was not successful.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "CallTransferFailedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'CallTransferFailedRest'
    ) -> 'CallTransferFailedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))


class ParticipantsUpdatedEventData(object):
    """Event sent when a participant joins, leaves, muted or unmuted.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar sequence_number: Sequence of this participant updated event in this call.
    :vartype sequence_number: int
    :ivar participants: List of participants in the call.
    :vartype participants: list[~azure.communication.callautomation.CallParticipant]
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        sequence_number: Optional[int] = None,
        participants: Optional[List['CommunicationIdentifier']] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.sequence_number = sequence_number
        self.participants = participants
        self.kind = "ParticipantsUpdatedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'ParticipantsUpdatedRest'
    ) -> 'ParticipantsUpdatedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            sequence_number=generated_model.sequence_number,
            participants=[CallParticipant(identifier=deserialize_identifier(
            participant.identifier), is_muted=participant.is_muted)
            for participant in generated_model.participants])


class RecordingStateChangedEventData(object):
    """Event sent when recording state changes.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar state: state of the call recording.
    :vartype state: RecordingState
    :ivar start_date_time: time the call recording started.
    :vartype start_date_time: startDateTime
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        recording_id: Optional[str] = None,
        state: Optional['RecordingState'] = None,
        start_date_time: Optional['datetime'] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.recording_id = recording_id
        self.state = state
        self.start_date_time = start_date_time
        self.kind = "RecordingStateChangedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'RecordingStateChangedRest'
    ) -> 'RecordingStateChangedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            recording_id=generated_model.recording_id,
            state=generated_model.state,
            start_date_time=generated_model.start_date_time)

class PlayCompletedEventData(object):
    """Event sent when media play is completed successfully.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Result information of the event. Contains detail information of the outcome.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "PlayCompletedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model:'PlayCompletedRest'
    ) -> 'PlayCompletedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))

class PlayFailedEventData(object):
    """Event sent when media play failed.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "PlayFailedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'PlayFailedRest'
    ) -> 'PlayFailedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))

class PlayCanceledEventData(object):
    """Event sent when media play is cancelled.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.kind = "PlayCanceledEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'PlayCanceledRest'
    ) -> 'PlayCanceledEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context)

class RecognizeCompletedEventData(object):
    """Event sent when recognize is completed successfully.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar recognition_type: Determines the sub-type of the recognize operation.
     In case of cancel operation the this field is not set and is returned empty.
    :vartype recognition_type: str or ~azure.communication.callautomation.RecognitionType
    :ivar collect_tones_result: Defines the result for RecognitionType = Dtmf.
    :vartype collect_tones_result: ~azure.communication.callautomation.CollectTonesResult
    :ivar choice_result: Defines the result for RecognitionType = Choices.
    :vartype choice_result: ~azure.communication.callautomation.ChoiceResult
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        recognition_type: Optional['RecognitionType'] = None,
        collect_tones_result: Optional[CollectTonesResult] = None,
        choice_result:Optional[ChoiceResult] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.recognition_type = recognition_type
        self.collect_tones_result = collect_tones_result
        self.choice_result = choice_result
        self.kind = "RecognizeCompletedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'RecognizeCompletedRest'
    ) -> 'RecognizeCompletedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information),
            recognition_type=generated_model.recognition_type,
            collect_tones_result=CollectTonesResult._from_generated(# pylint:disable=protected-access
            generated_model.collect_tones_result),
            choice_result=ChoiceResult._from_generated(# pylint:disable=protected-access
            generated_model.choice_result))

class RecognizeFailedEventData(object):
    """Event sent when recognize action failed.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "RecognizeFailedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'RecognizeFailedRest'
    ) -> 'RecognizeFailedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context)

class RecognizeCanceledEventData(object):
    """Event sent when recognize is cancelled.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.kind = "RecognizeCanceledEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'RecognizeCanceledRest'
    ) -> 'RecognizeCanceledEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context)

class RemoveParticipantSucceededEventData(object):
    """Event sent when the participant was successfully removed to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar participant: participant that was removed to the call.
    :vartype participant: ~azure.communication.callautomation.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        participant: Optional['CommunicationIdentifier'] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.participant = participant
        self.kind = "RemoveParticipantSucceededEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'RemoveParticipantSucceededRest'
    ) -> 'RemoveParticipantSucceededEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information),
            participant=CallParticipant._from_generated(# pylint:disable=protected-access
            generated_model.participant))

class RemoveParticipantFailedEventData(object):
    """Event sent when the participant was not removed successfully to the call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar participant: participant that was removed to the call.
    :vartype participant: ~azure.communication.callautomation.CommunicationIdentifier
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        participant: Optional['CommunicationIdentifier'] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.participant = participant
        self.kind = "RemoveParticipantFailedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'RemoveParticipantFailedRest'
    ) -> 'RemoveParticipantFailedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information),
            participant=CallParticipant._from_generated(# pylint:disable=protected-access
            generated_model.participant))

class ContinuousDtmfRecognitionToneReceivedEventData(object):
    """Event sent when Dtmf tone received from targeted participant in call.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    :ivar tone_info: Information about Tone.
    :vartype tone_info: ~azure.communication.callautomation.ToneInfo
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        tone_info: Optional[ToneInfo] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.result_information = result_information
        self.tone_info = tone_info
        self.kind = "ContinuousDtmfRecognitionToneReceivedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'ContinuousDtmfRecognitionToneReceivedRest'
    ) -> 'ContinuousDtmfRecognitionToneReceivedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information),
            tone_info=generated_model.tone_info)

class ContinuousDtmfRecognitionToneFailedEventData(object):
    """Event sent when failed to start continuous Dtmf recognition.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.result_information = result_information
        self.kind = "ContinuousDtmfRecognitionToneFailedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'ContinuousDtmfRecognitionToneFailedRest'
    ) -> 'ContinuousDtmfRecognitionToneFailedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))

class ContinuousDtmfRecognitionStoppedEventData(object):
    """Event sent when start continuous Dtmf recognition stopped.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "ContinuousDtmfRecognitionStoppedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'ContinuousDtmfRecognitionStoppedRest'
    ) -> 'ContinuousDtmfRecognitionStoppedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))

class SendDtmfCompletedEventData(object):
    """Event sent when Dtmf tones send completed successfully.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "SendDtmfCompletedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'SendDtmfCompletedRest'
    ) -> 'SendDtmfCompletedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))

class SendDtmfFailedEventData(object):
    """Event sent when Dtmf tones send failed.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Id that can be used to correlate with the call. Also Called Skype-Chain-Id.
    :vartype correlation_id: str
    :ivar operation_context: Context that can be used to corelate with the request,
	 if the request provided the context.
    :vartype operation_context: str
    :ivar result_information: Detail Result information of the event.
	 Contains detail information of the outcome if there is any issue.
    :vartype result_information: ~azure.communication.callautomation.ResultInformation
    :ivar kind: This event kind.
    :vartype kind: str
    """
    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        result_information: Optional[ResultInformation] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.correlation_id = correlation_id
        self.operation_context = operation_context
        self.result_information = result_information
        self.kind = "SendDtmfFailedEventData"

    @classmethod
    def _from_generated(
        cls,
        generated_model: 'SendDtmfFailedRest'
    ) -> 'SendDtmfFailedEventData':
        """Internal constructor to build the event from generated event"""

        return cls(
            call_connection_id=generated_model.call_connection_id,
            server_call_id=generated_model.server_call_id,
            correlation_id=generated_model.correlation_id,
            operation_context=generated_model.operation_context,
            result_information=ResultInformation._from_generated(# pylint:disable=protected-access
            generated_model.result_information))
