# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._version import VERSION
from ._call_automation_client import CallAutomationClient
from ._call_connection_client import CallConnectionClient
from ._models import (
    CallConnectionProperties,
    CallInvite,
    ServerCallLocator,
    GroupCallLocator,
    FileSource,
    TextSource,
    SsmlSource,
    CallParticipant,
    RecordingProperties,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult,
    MediaStreamingConfiguration,
    ChannelAffinity,
    MuteParticipantsResult
)
from ._shared.models import (
    CommunicationIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier,
    CommunicationUserIdentifier,
    CommunicationIdentifierKind,
    CommunicationCloudEnvironment,
    MicrosoftBotIdentifier,
    UnknownIdentifier,
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
    CallConnectionState,
    RecordingState,
    Gender
)
__all__ = [
    # clients
    "CallAutomationClient",
    "CallConnectionClient",

    # models for input
    "CallInvite",
    "ServerCallLocator",
    "GroupCallLocator",
    "FileSource",
    "TextSource",
    "SsmlSource",
    "ChannelAffinity",
    "MediaStreamingConfiguration",

    # models for output
    "CallConnectionProperties",
    "CallParticipant",
    "RecordingProperties",
    "AddParticipantResult",
    "RemoveParticipantResult",
    "TransferCallResult",
    "MuteParticipantsResult",

    # common ACS communication identifier
    "CommunicationIdentifier",
    "PhoneNumberIdentifier",
    "MicrosoftTeamsUserIdentifier",
    "CommunicationUserIdentifier",
    "CommunicationIdentifierKind",
    "CommunicationCloudEnvironment",
    "MicrosoftBotIdentifier",
    "UnknownIdentifier",

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
    "RecordingState",
    "Gender"
]
__version__ = VERSION
