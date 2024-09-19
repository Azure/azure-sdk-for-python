# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import warnings

from ._version import VERSION
from ._call_automation_client import CallAutomationClient
from ._call_connection_client import CallConnectionClient
from ._models import (
    CallConnectionProperties,
    FileSource,
    TextSource,
    SsmlSource,
    RecognitionChoice,
    CallParticipant,
    RecordingProperties,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult,
    MediaStreamingOptions,
    MediaStreamingSubscription,
    TranscriptionOptions,
    TranscriptionSubscription,
    ChannelAffinity,
    MuteParticipantResult,
    SendDtmfTonesResult,
    CancelAddParticipantOperationResult,
    CallInvite,
    ServerCallLocator,
    GroupCallLocator,
    RoomCallLocator,
    AzureBlobContainerRecordingStorage,
    AzureCommunicationsRecordingStorage
)
from ._shared.models import (
    CommunicationIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsAppIdentifier,
    MicrosoftTeamsUserIdentifier,
    CommunicationUserIdentifier,
    CommunicationIdentifierKind,
    CommunicationCloudEnvironment,
    UnknownIdentifier,
)
from ._generated.models._enums import (
    CallRejectReason,
    RecordingContent,
    RecordingChannel,
    RecordingFormat,
    RecordingStorageKind,
    RecordingKind,
    RecognizeInputType,
    MediaStreamingAudioChannelType,
    MediaStreamingSubscriptionState,
    TranscriptionSubscriptionState,
    MediaStreamingContentType,
    MediaStreamingTransportType,
    TranscriptionTransportType,
    TranscriptionResultState,
    DtmfTone,
    CallConnectionState,
    RecordingState,
    VoiceKind
)

__all__ = [
    # clients
    "CallAutomationClient",
    "CallConnectionClient",

    # models for input
    "FileSource",
    "TextSource",
    "SsmlSource",
    "RecognitionChoice",
    "ChannelAffinity",
    "MediaStreamingOptions",
    "MediaStreamingSubscription",
    "TranscriptionOptions",
    "TranscriptionSubscription",
    "AzureBlobContainerRecordingStorage",
    "AzureCommunicationsRecordingStorage",

    # models for output
    "CallConnectionProperties",
    "CallParticipant",
    "RecordingProperties",
    "AddParticipantResult",
    "RemoveParticipantResult",
    "TransferCallResult",
    "MuteParticipantResult",
    "SendDtmfTonesResult",
    "CancelAddParticipantOperationResult",

    # common ACS communication identifier
    "CommunicationIdentifier",
    "PhoneNumberIdentifier",
    "MicrosoftTeamsAppIdentifier",
    "MicrosoftTeamsUserIdentifier",
    "CommunicationUserIdentifier",
    "CommunicationIdentifierKind",
    "CommunicationCloudEnvironment",
    "UnknownIdentifier",

    # enums
    "CallRejectReason",
    "RecordingContent",
    "RecordingChannel",
    "RecordingFormat",
    "RecordingStorageKind",
    "RecordingKind",
    "RecognizeInputType",
    "MediaStreamingAudioChannelType",
    "MediaStreamingSubscriptionState",
    "MediaStreamingContentType",
    "MediaStreamingTransportType",
    "TranscriptionResultState",
    "TranscriptionSubscriptionState",
    "TranscriptionTransportType",
    "DtmfTone",
    "CallConnectionState",
    "RecordingState",
    "VoiceKind",

    # deprecated models
    "CallInvite",
    "ServerCallLocator",
    "GroupCallLocator",
    "RoomCallLocator",
]
__version__ = VERSION


def __getattr__(name):
    if name == 'MicrosoftBotIdentifier':
        warnings.warn(f"{name} is deprecated and should not be used. Please use 'MicrosoftTeamsAppIdentifier' instead.",
                       DeprecationWarning)
        from ._shared.models import _MicrosoftBotIdentifier
        return _MicrosoftBotIdentifier
    raise AttributeError(f"module 'azure.communication.callautomation' has no attribute {name}")
