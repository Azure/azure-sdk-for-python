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
    Choice,
    CallParticipant,
    RecordingProperties,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult,
    ChannelAffinity,
    MuteParticipantResult,
    SendDtmfResult
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
    RecognizeInputType,
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
    "Choice",
    "ChannelAffinity",

    # models for output
    "CallConnectionProperties",
    "CallParticipant",
    "RecordingProperties",
    "AddParticipantResult",
    "RemoveParticipantResult",
    "TransferCallResult",
    "MuteParticipantResult",
    "SendDtmfResult",

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
    "RecognizeInputType",
    "DtmfTone",
    "CallConnectionState",
    "RecordingState",
    "Gender"
]
__version__ = VERSION
