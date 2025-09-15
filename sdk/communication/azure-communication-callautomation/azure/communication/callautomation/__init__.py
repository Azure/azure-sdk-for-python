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
    TranscriptionOptions,
    ChannelAffinity,
    MuteParticipantResult,
    SendDtmfTonesResult,
    CancelAddParticipantOperationResult,
    AzureBlobContainerRecordingStorage,
    AzureCommunicationsRecordingStorage,
    MediaStreamingSubscription,
    TranscriptionSubscription,
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
    TeamsExtensionUserProperties,
    TeamsExtensionUserIdentifier,
)
from ._generated.models._enums import (
    CallRejectReason,
    RecordingContent,
    RecordingChannel,
    RecordingFormat,
    RecordingKind,
    RecordingStorageKind,
    RecognizeInputType,
    MediaStreamingAudioChannelType,
    MediaStreamingContentType,
    MediaStreamingSubscriptionState,
    TranscriptionResultType,
    TranscriptionSubscriptionState,
    StreamingTransportType,
    DtmfTone,
    CallConnectionState,
    RecordingState,
    VoiceKind,
    AudioFormat,
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
    "TranscriptionOptions",
    "AzureBlobContainerRecordingStorage",
    "AzureCommunicationsRecordingStorage",
    # models for output
    "CallConnectionProperties",
    "MediaStreamingSubscription",
    "TranscriptionSubscription",
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
    "TeamsExtensionUserProperties",
    "TeamsExtensionUserIdentifier",
    # enums
    "CallRejectReason",
    "RecordingContent",
    "RecordingChannel",
    "RecordingFormat",
    "RecordingKind",
    "RecordingStorageKind",
    "RecognizeInputType",
    "MediaStreamingAudioChannelType",
    "MediaStreamingContentType",
    "MediaStreamingSubscriptionState",
    "TranscriptionResultType",
    "TranscriptionSubscriptionState",
    "StreamingTransportType",
    "DtmfTone",
    "CallConnectionState",
    "RecordingState",
    "VoiceKind",
    "AudioFormat",
]
__version__ = VERSION


def __getattr__(name):
    if name == "CallInvite":
        warnings.warn(
            "CallInvite is deprecated and should not be used. Please pass in keyword arguments directly.",
            DeprecationWarning,
        )
        from ._models import CallInvite

        return CallInvite
    if name == "GroupCallLocator":
        warnings.warn(
            "GroupCallLocator is deprecated and should not be used. Please pass in 'group_call_id' directly.",
            DeprecationWarning,
        )
        from ._models import GroupCallLocator

        return GroupCallLocator
    if name == "ServerCallLocator":
        warnings.warn(
            "ServerCallLocator is deprecated and should not be used. Please pass in 'server_call_id' directly.",
            DeprecationWarning,
        )
        from ._models import ServerCallLocator

        return ServerCallLocator
    if name == "RoomCallLocator":
        warnings.warn(
            "RoomCallLocator is deprecated and should not be used. Please pass in 'room_id' directly.",
            DeprecationWarning,
        )
        from ._models import RoomCallLocator

        return RoomCallLocator
    if name == "MicrosoftBotIdentifier":
        warnings.warn(
            f"{name} is deprecated and should not be used. Please use 'MicrosoftTeamsAppIdentifier' instead.",
            DeprecationWarning,
        )
        from ._shared.models import _MicrosoftBotIdentifier

        return _MicrosoftBotIdentifier
    raise AttributeError(f"module 'azure.communication.callautomation' has no attribute {name}")
