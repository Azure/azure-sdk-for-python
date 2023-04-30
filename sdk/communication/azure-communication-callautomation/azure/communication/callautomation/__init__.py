# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._version import VERSION
from ._call_automation_client import CallAutomationClient
from ._call_connection_client import CallConnectionClient
from ._call_automation_event_parser import CallAutomationEventParser
from ._models import (
    CallConnectionProperties,
    ResultInformation,
    CallInvite,
    ServerCallLocator,
    GroupCallLocator,
    FileSource,
    CallParticipant,
    RecordingStateResult,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult,
    ChoiceResult,
    CollectTonesResult,
    ToneInfo
)
from ._shared.models import (
    CommunicationIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier,
    CommunicationUserIdentifier
)
from ._generated.models._enums import (
    CallRejectReason,
    RecordingContent,
    RecordingChannel,
    RecordingFormat,
    RecordingStorage,
    RecognizeInputType,
    MediaStreamingAudioChannelType,
    MediaStreamingContentType,
    MediaStreamingTransportType,
    DtmfTone,
    CallConnectionState
)
from ._events import (
    AddParticipantSucceededEventData,
    AddParticipantFailedEventData,
    CallConnectedEventData,
    CallDisconnectedEventData,
    CallTransferAcceptedEventData,
    CallTransferFailedEventData,
    ParticipantsUpdatedEventData,
    RecordingStateChangedEventData,
    PlayCompletedEventData,
    PlayFailedEventData,
    PlayCanceledEventData,
    RecognizeCompletedEventData,
    RecognizeCanceledEventData,
    RecognizeFailedEventData,
    RemoveParticipantSucceededEventData,
    RemoveParticipantFailedEventData,
    ContinuousDtmfRecognitionToneReceivedEventData,
    ContinuousDtmfRecognitionToneFailedEventData,
    ContinuousDtmfRecognitionStoppedEventData,
    SendDtmfCompletedEventData,
    SendDtmfFailedEventData
)
__all__ = [
    # clients and parser
    "CallAutomationClient",
    "CallConnectionClient",
    "CallAutomationEventParser",

    # models for input
    "CallInvite",
    "ServerCallLocator",
    "GroupCallLocator",
    "FileSource",

    # models for output
    "CallConnectionProperties",
    "ResultInformation",
    "CallParticipant",
    "RecordingStateResult",
    "AddParticipantResult",
    "RemoveParticipantResult",
    "TransferCallResult",
    "ChoiceResult",
    "CollectTonesResult",
    "ToneInfo",

    # common ACS communication identifier
    "CommunicationIdentifier",
    "PhoneNumberIdentifier",
    "MicrosoftTeamsUserIdentifier",
    "CommunicationUserIdentifier",

    # enums
    "CallRejectReason",
    "RecordingContent",
    "RecordingChannel",
    "RecordingFormat",
    "RecordingStorage",
    "RecognizeInputType",
    "MediaStreamingAudioChannelType",
    "MediaStreamingContentType",
    "MediaStreamingTransportType",
    "DtmfTone",
    "CallConnectionState",

    # callback events model
    "AddParticipantSucceededEventData",
    "AddParticipantFailedEventData",
    "CallConnectedEventData",
    "CallDisconnectedEventData",
    "CallTransferAcceptedEventData",
    "CallTransferFailedEventData",
    "ParticipantsUpdatedEventData",
    "RecordingStateChangedEventData",
    "PlayCompletedEventData",
    "PlayFailedEventData",
    "PlayCanceledEventData",
    "RecognizeCompletedEventData",
    "RecognizeCanceledEventData",
    "RecognizeFailedEventData",
    "RemoveParticipantSucceededEventData",
    "RemoveParticipantFailedEventData",
    "ContinuousDtmfRecognitionToneReceivedEventData",
    "ContinuousDtmfRecognitionToneFailedEventData",
    "ContinuousDtmfRecognitionStoppedEventData",
    "SendDtmfCompletedEventData",
    "SendDtmfFailedEventData"
]
__version__ = VERSION
