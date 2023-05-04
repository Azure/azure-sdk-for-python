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
    CallParticipant,
    RecordingProperties,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult,
    MediaStreamingConfiguration
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
    RecordingState
)
__all__ = [
    # clients and parser
    "CallAutomationClient",
    "CallConnectionClient",

    # models for input
    "CallInvite",
    "ServerCallLocator",
    "GroupCallLocator",
    "FileSource",

    # models for output
    "CallConnectionProperties",
    "CallParticipant",
    "RecordingProperties",
    "AddParticipantResult",
    "RemoveParticipantResult",
    "TransferCallResult",
    "MediaStreamingConfiguration",

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
    "RecordingState"
]
__version__ = VERSION
