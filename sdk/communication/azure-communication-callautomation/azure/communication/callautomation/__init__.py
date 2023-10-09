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
    CallParticipant,
    RecordingProperties,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult,
    MediaStreamingConfiguration,
    ChannelAffinity,
    MuteParticipantsResult,
    CancelAddParticipantResult,
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
    "CancelAddParticipantResult",

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


def __getattr__(name):
    if name == 'CallInvite':
        warnings.warn(
            "CallInvite is deprecated and should not be used. Please pass in keyword arguments directly.",
            DeprecationWarning
        )
        from ._models import CallInvite
        return CallInvite
    if name == 'GroupCallLocator':
        warnings.warn(
            "GroupCallLocator is deprecated and should not be used. Please pass in 'group_call_id' directly.",
            DeprecationWarning
        )
        from ._models import GroupCallLocator
        return GroupCallLocator
    if name == 'ServerCallLocator':
        warnings.warn(
            "ServerCallLocator is deprecated and should not be used. Please pass in 'server_call_id' directly.",
            DeprecationWarning
        )
        from ._models import ServerCallLocator
        return ServerCallLocator

    raise AttributeError(f"module 'azure.communication.callautomation' has no attribute {name}")
